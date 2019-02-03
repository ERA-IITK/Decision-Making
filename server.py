from environment import *
from thread import *
from math import pi
from math import exp
import time
import sys
import os
import argparse
import socket
from reward import *

start_time = time.time()
# Parse arguments
parser = argparse.ArgumentParser()
parser.add_argument('-p1', '--port1', dest="port1", type=int, default=12121, help='Port for our player')
parser.add_argument('-p2', '--port2', dest="port2", type=int, default=34343, help='Port for opponent player')
parser.add_argument('-rs', '--random-seed', dest="rng", type=int, default=0, help='Random Seed')
parser.add_argument('-n', '--noise', dest="noise", type=int, default=1, help='Turn noise on/off')
parser.add_argument('-num', '--number', dest="num", type=int, default=2, help="Number of rounds to be played between the AI robots")
args = parser.parse_args()
ports = [0]*num_of_players
ports[0] = args.port1
ports[1] = args.port2
random.seed(args.rng)
host = '127.0.0.1'   # Symbolic name meaning all available interfaces
noise = args.noise
if noise == 1:
    noise1 = 0.005
    noise2 = 0.01
    noise3 = 2
else:
    noise1 = 0
    noise2 = 0
    noise3 = 0
timeout_msg = "TIMED OUT"
timeout_period = 5
num = args.num
obstacles = list()
##########################################################################

def play(space, action):
    # Printing the state, actions and the scores of both players
    print 'state_1: ' + str(state[0])
    print 'action_1: ' + str(action[0])
    print 'state_2: ' + str(state[1])
    print 'action_2: ' + str(action[1])
    print 'score_1: ' + str(score[0])
    print 'score_2: ' + str(score[1])
    # 1 - Shoot action = {action_type, yaw, speed}
    # 2 - Chase action = {action_type, speed, direction, angularvelocity} Cover even rotating in a given position in order to be able to shoot
    # 3 - Refill action = {action_type, speed, direction, angularvelocity} Position of the refill zone and the best orientation of the robot
    # 4 - Defense action = {action_type, speed, direction, angularvelocity} Position of the defense zone and the best orientaton of the robot
    # 5 - Escape action = {action_type, speed, direction, angularvelocity} Position and orientation of the robot in the best escape spot
    # 6 - Roam action = {action_type}
    for i in range(0, num_of_players):
        if action[i][0] == 1 and float(pygame.time.get_ticks() - state[i]["last_shoot_time"]) > 1000/float(MAX_SHOOT_FREQUENCY): #Shoot
            ball_body, ball_shape = spawn_ball(state[i]["location_self"], action[i][1], action[i][2])
            space.add(ball_body, ball_shape)
            state[i]["barrel_heat"] = state[i]["barrel_heat"] + action[i][2]
            state[i]["projectiles_left"] = state[i]["projectiles_left"] - 1
            state[i]["last_shoot_time"] = pygame.time.get_ticks()
        elif action[i][0] == 2: #Chase
            translate_player(action[i][1], action[i][2], i)
            rotate_player(action[i][3], i)
        elif action[i][0] == 3: #Refill
            if state[i]["location_self"][0] > 3500*f2 and state[i]["location_self"][0] < 4500*f2 and state[i]["location_self"][1] > 4000*f2 and state[i]["location_self"][1] < 5000*f:
                state[i]["projectiles_left"] = state[i]["projectiles_left"] + REFILL_NUMBER_AT_A_TIME
            else:
                translate_player(action[i][1], action[i][2], i)
                rotate_player(action[i][3], i)
        elif action[i][0] == 4: #Defense
            if state[i]["defense"] <= -5:
                if state[i]["defense_triggered"] < DEFENSE_TRIGGER_LIMIT:                    
                    state[i]["defense"] = 30
                    state[i]["defense_triggered"] = state[i]["defense_triggered"] + 1
                else:
                    state[i]["defense"] = 0
            elif state[i]["location_self"][0] > DEFENSE_ZONES[i][0]*f2 and state[i]["location_self"][0] < DEFENSE_ZONES[i][1]*f2 and state[i]["location_self"][1] > DEFENSE_ZONES[i][2]*f2 and state[i]["location_self"][1] < DEFENSE_ZONES[i][3]*f2:
                state[i]["defense"] = state[i]["defense"] - (1/TIME_STEP)
            else:
                translate_player(action[i][1], action[i][2], i)
                rotate_player(action[i][3], i)
        elif action[i][0] == 5: #Escape
            translate_player(action[i][1], action[i][2], i)
            rotate_player(action[i][3], i)

    pygame.display.flip()
    clock.tick()

# The server receives an action from the agent
def request_action(conn):
    try:
        data = conn.recv(1024)
    except:
        data = timeout_msg
    finally:
        return data

# The server sends it's state to the agent
def send_state(state, conn):
    try:
        conn.send(state)
    except socket.error:
        print "Aborting, player did not respond within timeout"
        sys.exit()
    return True

def ball_armor_collision_handler_generator(player1, player2):
    def ball_armor_collision(arbiter, space, data):
        ball_shape = arbiter.shapes[0]
        armor_shape = arbiter.shapes[1]
        space.remove(ball_shape, ball_shape.body)
        if state[player1]["last_hit_time"] - pygame.time.get_ticks() > 1000/float(MAX_HIT_FREQUENCY):
            if state[player1]["last_hit_time"] > 0: #Within 30s of defense zone
                state[player1]["HP"] -= 25
            else:
                state[player1]["HP"] -= 50
            state[player1]["last_hit_time"] = pygame.time.get_ticks()
            ball_armor_collision(player2, player1)
        return True
    return ball_armor_collision

if __name__ == '__main__':

    # Bind to socket, and wait for the agent to connect
    conn = [None]*num_of_players
    for i in range(0, num_of_players):        
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((host, ports[i]))
        except socket.error as msg:
            print 'Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
            sys.exit()
        s.listen(1)
        connection, addr = s.accept()
        connection.settimeout(timeout_period)
        conn[i] = connection

    pygame.init()
    clock = pygame.time.Clock()
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("AI Challenge Simulation")
    space = pymunk.Space(threaded=True)
    draw_options = pymunk.pygame_util.DrawOptions(screen) 
    screen.fill(THECOLORS["lightgreen"])
    obstacles = setup_level(space)
    armor_sets = [None]*num_of_players
    for i in range(0, num_of_players):
        score[i] = 0
        state[i] = dict(INITIAL_STATE)
    for i in range(0, num_of_players):
        player_body, player_shape, player_shooter, player_armors = make_player(i)
        player_body.position = x1 + INITIAL_LOCATIONS[i][0]*f2, y1 + INITIAL_LOCATIONS[i][1]*f2
        space.add(player_body, player_shape, player_shooter)
        armor_sets[i] = player_armors
        for armor in player_armors:
            space.add(armor)
    
    h = space.add_collision_handler(collision_types["ball"], collision_types["brick"])
    h.begin = ball_brick_collision
    h = space.add_collision_handler(collision_types["ball"], collision_types["armor1"])
    h.begin = ball_armor_collision_handler_generator(1, 0)
    h.separate = player_collision_handler_generator(1)
    h = space.add_collision_handler(collision_types["ball"], collision_types["armor0"])
    h.begin = ball_armor_collision_handler_generator(0, 1)
    h.separate = player_collision_handler_generator(0)
    h = space.add_collision_handler(collision_types["ball"],  collision_types["player1"])
    h.begin = ball_brick_collision
    h.separate = player_collision_handler_generator(1)
    h = space.add_collision_handler(collision_types["ball"],  collision_types["player0"])
    h.begin = ball_brick_collision
    h.separate = player_collision_handler_generator(0)
    h = space.add_collision_handler(collision_types["player0"], collision_types["player1"])
    h.separate = player_player_collision_handler_generator(0, 1)
    h = space.add_collision_handler(collision_types["player0"], collision_types["armor1"])
    h.separate = player_player_collision_handler_generator(0, 1)
    h = space.add_collision_handler(collision_types["player1"], collision_types["armor0"])
    h.separate = player_player_collision_handler_generator(0, 1)
    h = space.add_collision_handler(collision_types["armor0"], collision_types["armor1"])
    h.separate = player_player_collision_handler_generator(0, 1)
    h = space.add_collision_handler(collision_types["player0"], collision_types["brick"])
    h.separate = player_collision_handler_generator(0)
    h = space.add_collision_handler(collision_types["player1"], collision_types["brick"])
    h.separate = player_collision_handler_generator(1)
    h = space.add_collision_handler(collision_types["armor0"], collision_types["brick"])
    h.separate = player_collision_handler_generator(0)
    h = space.add_collision_handler(collision_types["armor1"], collision_types["brick"])
    h.separate = player_collision_handler_generator(1)
    for i in range(0, num):
        reward = [0]*num_of_players
        for i in range(0, num_of_players):
            score[i] = 0
            state[i] = dict(INITIAL_STATE)
        # Setup arena
        for i in range(0, num_of_players):
            players[str(i)].velocity = (0, 0)
            players[str(i)].position = offsets[0] + INITIAL_LOCATIONS[i][0]*f2, offsets[2] + INITIAL_LOCATIONS[i][1]*f2
            state[i]['location_self'] = players[str(i)].position

        space.debug_draw(draw_options)
        it = 0
        while it < TIME_STEP*DURATION_OF_ROUND:  # Number of ticks in a single episode - 60fps in 180s
            print "Tick number: " + str(it+1)
            it += 1
            action = [None]*num_of_players
            for i in range(0, num_of_players):
                send_state(str(state[i]) + ";REWARD" + str(reward[i]), conn[i])
                a = request_action(conn[i])
                if not a:  # response empty player 1
                    print "No response from player " + str(i)
                    sys.exit()
                elif a == timeout_msg:
                    print "Timeout from player " + str(i)
                    sys.exit()
                else:
                    action[i] = tuplise(a.replace(" ", "").split(','))
            play(space, action)
            screen.fill(THECOLORS["lightgreen"])
            space.debug_draw(draw_options)
            game_over = False
            for i in range(0, num_of_players):
                if state[i]["barrel_heat"] < 0:
                    state[i]["barrel_heat"] = 0
                if state[i]["barrel_heat"] >= 720:
                    state[i]["HP"] = state[i]["HP"] - (state[i]["barrel_heat"]-720)*40
                if it%(TIME_STEP/HEALTH_FREQUENCY) == 0:
                    if state[i]["barrel_heat"]<720 and state[i]["barrel_heat"]>360:
                        state[i]["HP"] = state[i]["HP"] - (state[i]["barrel_heat"]-360)*4
                if state[i]["HP"] >= 400 and state[i]["barrel_heat"] > 0:
                    state[i]["barrel_heat"] = state[i]["barrel_heat"] - 12
                elif state[i]["HP"] < 400 and state[i]["HP"] > 0 and state[i]["barrel_heat"] > 0:
                    state[i]["barrel_heat"] = state[i]["barrel_heat"] - 24
                if state[i]["defense"] > 0:
                    state[i]["defense"] = state[i]["defense"] - (1/TIME_STEP)
                if (1/TIME_STEP) - state[i]["defense"] > 0:
                    state[i]["defense"] = 0            
                if state[i]["HP"] <= 0:
                    game_over = True
                    break
                reward[i] = calculate_reward(space, i)
                state[i]['location_self'] = players[str(i)].position
                for j in range(i+1, num_of_players):
                    p1 = state[i]['location_self']
                    p2 = state[j]['location_self']
                    pt1 = state[i]['location_self']
                    pt2 = state[j]['location_self']
                    r0=350*f2
                    theta = atan((p2[1]-p1[1])/(p2[0]-p1[0]))
                    pt1[0] = p1[0]+r0*cos(theta)
                    pt1[1] = p1[1]+r0*sin(theta)
                    pt2[0] = p2[0]+r0*cos(theta)
                    pt2[1] = p2[1]+r0*sin(theta)
                    query = space.segment_query_first(pt1, pt2, 1, pymunk.ShapeFilter())
                    if query.shape == None:
                        state[i]["armor_modules"] = armor_sets[j]
                        state[j]["armor_modules"] = armor_sets[i]
                        state[i]["location_op"] = state[j]["location_self"]
                        state[j]["location_op"] = state[i]["location_self"]
                    else:
                        state[i]["armor_modules"] = None
                        state[j]["armor_modules"] = None
                        state[i]["location_op"] = None
                        state[j]["location_op"] = None
            if game_over:
                break        
            if it/TIME_STEP >= 60:
                for i in range(0, num_of_players):
                    state[i]["defense_triggered"] = 0
            space.step(1/TIME_STEP)
            clock.tick(TIME_STEP)
    sys.exit()