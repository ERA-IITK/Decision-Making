from Utils import *
from thread import *
from math import pi
from math import exp
import time
import sys
import os
import argparse
import socket

start_time = time.time()
# Parse arguments
parser = argparse.ArgumentParser()
parser.add_argument('-p1', '--port1', dest="port1", type=int, default=12121, help='Port for our player')
parser.add_argument('-p2', '--port2', dest="port2", type=int, default=34343, help='Port for opponent player')
parser.add_argument('-rs', '--random-seed', dest="rng", type=int, default=0, help='Random Seed')
parser.add_argument('-n', '--noise', dest="noise", type=int, default=1, help='Turn noise on/off')
parser.add_argument('-num', '--number', dest="num", type=int, default=1, help="Number of rounds to be played between the AI robots")
args = parser.parse_args()
port1 = args.port1
port2 = args.port2
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

def play(space, state_1, action_1, state_2, action_2, score_1, score_2):
    # Printing the state, actions and the scores of both players
    print 'state_1: ' + str(state_1)
    print 'action_1: ' + str(action_1)
    print 'state_2: ' + str(state_2)
    print 'action_2: ' + str(action_2)
    print 'score_1: ' + str(score_1)
    print 'score_2: ' + str(score_2)

    # Getting state of player 1
    prevscore_1 = score_1
    location_self_1 = state_1["location_self"]
    location_op_1 = state_1["location_op"]
    HP_1 = state_1["HP"]
    defense_1 = state_1["defense"]
    defense_triggered_1 = state_1["defense_triggered"]
    barrel_heat_1 = state_1["barrel_heat"]
    projectiles_left_1 = state_1["projectiles_left"]
    armor_modules_1 = state_1["armor_modules"]
    time_since_last_shoot_1 = state_1["time_since_last_shoot"]
    time_since_last_hit_1 = state_1["time_since_last_hit"]
    # Getting state of player 2
    prevscore_2 = score_2
    location_self_2 = state_2["location_self"]
    location_op_2 = state_2["location_op"]
    HP_2 = state_2["HP"]
    defense_2 = state_2["defense"]
    defense_triggered_2 = state_2["defense_triggered"]
    barrel_heat_2 = state_2["barrel_heat"]
    projectiles_left_2 = state_2["projectiles_left"]
    armor_modules_2 = state_2["armor_modules"]
    time_since_last_shoot_2 = state_2["time_since_last_shoot"]
    time_since_last_hit_2 = state_2["time_since_last_hit"]

    # 1 - Shoot action = {action_type, yaw, speed}
    # 2 - Chase action = {action_type, speed, direction, angularvelocity} Cover even rotating in a given position in order to be able to shoot
    # 3 - Refill action = {action_type, speed, direction, angularvelocity} Position of the refill zone and the best orientation of the robot
    # 4 - Defense action = {action_type, speed, direction, angularvelocity} Position of the defense zone and the best orientaton of the robot
    # 5 - Escape action = {action_type, speed, direction, angularvelocity} Position and orientation of the robot in the best escape spot
    # 6 - Roam action = {action_type}
    if action_1[0] == 1 and time_since_last_shoot_1 > 1/float(MAX_SHOOT_FREQUENCY): #Shoot
        ball_body, ball_shape = spawn_ball(player1_body.position, action_1[1], action_1[2])
        space.add(ball_body, ball_shape)
        projectiles.append(ball_shape)
        barrel_heat_1 = barrel_heat_1 + action_1[2]
        projectiles_left_1 = projectiles_left_1 - 1
        time_since_last_shoot_1 = 0
    elif action_1[0] == 2: #Chase
        translate_player(action_1[1], action_1[2], 1)
        rotate_player(action_1[3], 1)
        score_1 = score_1 + ENEMY_CHASE_COEFF
    elif action_1[0] == 3: #Refill
        if location_self_1[0] > 3500*f2 and location_self_1[0] < 4500*f2 and location_self_1[1] > 4000*f2 and location_self_1[1] < 5000*f:
            score_1 = score_1 + REFILL_COEFF*(REFILL_NUMBER_AT_A_TIME - projectiles_left_1)
            projectiles_left_1 = projectiles_left_1 + REFILL_NUMBER_AT_A_TIME
        else:
            translate_player(action_1[1], action_1[2], 1)
            rotate_player(action_1[3], 1)
            score_1 = score_1 - REFILL_TRAVEL_COEFF*projectiles_left_1
    elif action_1[0] == 4: #Defense
        if defense_triggered_1 >= 2:
            score_1 = score_1 - DEFENSE_TRIGGERED_PUNISHMENT
        if defense_1 == -5:
            defense_1 = 30
            defense_triggered_1 = defense_triggered_1 + 1
            if defense_triggered_1 <= 2:
                score_1 = score_1 + DEFENSE_TRIGGERED_COEFF*(defense_triggered_1)
            else:
                score_1 = score_1 - DEFENSE_TRIGGERED_PUNISHMENT
        elif location_self_1[0] > 5800*f and location_self_1[0] < 6800*f and location_self_1[1] > 1250*f and location_self_1[1] < 2250*f:
            defense_1 = defense_1 - (1/TIME_STEP)
            score_1 = score_1 + DEFENSE_CHARGE_COEFF*exp(DEFENSE_CHARGE_TIME_COEFF*defense_1)
        else:
            translate_player(action_1[1], action_1[2], 1)
            rotate_player(action_1[3], 1)
            if defense_triggered_1 < 2 and defense_1 == 0:
                score_1 = score_1 #TODO
    elif action_1[0] == 5: #Escape
        translate_player(action_1[1], action_1[2], 1)
        rotate_player(action_1[3], 1)
        score_1 = score_1 + ENEMY_CHASE_COEFF

    if action_2[0] == 1 and time_since_last_shoot_2 > 1/float(MAX_SHOOT_FREQUENCY): #Shoot
        ball_body, ball_shape = spawn_ball(player2_body.position, action_2[1], action_2[2])
        space.add(ball_body, ball_shape)
        projectiles.append(ball_shape)
        barrel_heat_2 = barrel_heat_2 + action_2[2]
        projectiles_left_2 = projectiles_left_2 - 1
        time_since_last_shoot_2 = 0
    elif action_2[0] == 2: #Chase
        translate_player(action_2[1], action_2[2], 2)
        rotate_player(action_2[3], 2)
    elif action_2[0] == 3: #Refill
        if location_self_2[0] > 3500*f and location_self_2[0] < 4500*f and location_self_2[1] > 0*f and location_self_2[1] < 1000*f:
            score_2 = score_2 + REFILL_COEFF*(REFILL_NUMBER_AT_A_TIME - projectiles_left_1)
            projectiles_left_2 = projectiles_left_2 + REFILL_NUMBER_AT_A_TIME
        else:
            translate_player(action_2[1], action_2[2], 2)
            rotate_player(action_2[3], 2)
            score_2 = score_2 - REFILL_TRAVEL_COEFF*projectiles_left_2
    elif action_2[0] == 4: #Defense
        if defense_triggered_2 >= 2:
            score_2 = score_2 - DEFENSE_TRIGGERED_PUNISHMENT
        if defense_2 == -5:
            defense_2 = 30
            defense_triggered_2 = defense_triggered_2 + 1
            if defense_triggered_2 <= 2:
                score_2 = score_2 + DEFENSE_TRIGGERED_COEFF*(defense_triggered_2)
            else:
                score_2 = score_2 - DEFENSE_TRIGGERED_PUNISHMENT
        elif location_self_2[0] > 1200*f and location_self_2[0] < 2200*f and location_self_2[1] > 2750*f and location_self_2[1] < 3750*f:
            defense_2 = defense_2 - (1/TIME_STEP)
            score_2 = score_2 + DEFENSE_CHARGE_COEFF*exp(DEFENSE_CHARGE_TIME_COEFF*defense_2)
        else:
            translate_player(action_2[1], action_2[2], 2)
            rotate_player(action_2[3], 2)
            if defense_triggered_2 < 2 and defense_2 == 0:
                score_2 = score_2 #TODO
    elif action_2[0] == 5: #Escape
        translate_player(action_2[1], action_2[2], 2)
        rotate_player(action_2[3], 2)
    # Remove projectiles collided with obstacle
    for projectile in projectiles:
        for obstacle in obstacles:
            if dist(projectile.body.position, obstacle.body.position) < 1:
                space.remove(projectile, projectile.body)
                projectiles.remove(projectile)
                break
    # Remove projectiles collided with armor module
    for projectile in projectiles:
        for armor in player1_armors:
            if dist(projectile.body.position, armor.body.position) > 0 and dist(projectile.body.position, armor.body.position) < 1 and time_since_last_hit_1 > 1/float(MAX_HIT_FREQUENCY):
                if defense_1 > 0: #Within 30s of defense zone
                    HP_1 -= 25
                    score_2 += SHOOT_HIT_COEFF*25
                else:
                    HP_1 -= 50
                    score_2 += SHOOT_HIT_COEFF*50
                if projectile in space._shapes:
                    space.remove(projectile, projectile.body)
                    projectiles.remove(projectile)
                time_since_last_hit_1 = 0
        for armor in player2_armors:
            if dist(projectile.body.position, armor.body.position) > 0 and dist(projectile.body.position, armor.body.position) < 1 and time_since_last_hit_2 > 1/float(MAX_HIT_FREQUENCY):
                if defense_2 > 0: #Within 30s of defense zone
                    HP_2 -= 25
                    score_1 += SHOOT_HIT_COEFF*25
                else:
                    HP_2 -= 50
                    score_1 += SHOOT_HIT_COEFF*50
                if projectile in space._shapes:
                    space.remove(projectile, projectile.body)
                    projectiles.remove(projectile)
                time_since_last_hit_2 = 0
    pygame.display.flip()
    clock.tick()
        
    # New state for player 1
    state_new_1 = {"location_self": [], "location_op": [], "HP": 0, "defense": 0, "defense_triggered": 0, "barrel_heat": 0, "projectiles_left": 0, "armor_modules": [], "time_since_last_shoot": 0, "time_since_last_hit": 0}
    state_new_1["location_self"] = player1_body.position
    state_new_1["location_op"] = player2_body.position
    state_new_1["HP"] = HP_1
    state_new_1["defense"] = defense_1
    state_new_1["defense_triggered"] = defense_triggered_1
    state_new_1["barrel_heat"] = barrel_heat_1
    state_new_1["projectiles_left"] = projectiles_left_1
    state_new_1["time_since_last_shoot"] = time_since_last_shoot_1
    state_new_1["time_since_last_hit"] = time_since_last_hit_1
    # New state for player 2
    state_new_2 = {"location_self": [], "location_op": [], "HP": 0, "defense": 0, "defense_triggered": 0, "barrel_heat": 0, "projectiles_left": 0, "armor_modules": [], "time_since_last_shoot": 0, "time_since_last_hit": 0}
    state_new_2["location_self"] = player2_body.position
    state_new_2["location_op"] = player1_body.position
    state_new_2["HP"] = HP_2
    state_new_2["defense"] = defense_2
    state_new_2["defense_triggered"] = defense_triggered_2
    state_new_2["barrel_heat"] = barrel_heat_2
    state_new_2["projectiles_left"] = projectiles_left_2
    state_new_2["time_since_last_shoot"] = time_since_last_shoot_2
    state_new_2["time_since_last_hit"] = time_since_last_hit_2
    return state_new_1, state_new_2, score_1-prevscore_1, score_2-prevscore_2

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


if __name__ == '__main__':

    # Bind to socket, and wait for the agent to connect
    s1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s1.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s1.bind((host, port1))
    except socket.error as msg:
        print 'Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
        sys.exit()

    s1.listen(1)
    conn1, addr1 = s1.accept()
    conn1.settimeout(timeout_period)

    s2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s2.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s2.bind((host, port2))
    except socket.error as msg:
        print 'Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
        sys.exit()

    s2.listen(1)
    conn2, addr2 = s2.accept()
    conn2.settimeout(timeout_period)

    pygame.init()
    clock = pygame.time.Clock()
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("AI Challenge Simulation")
    space = pymunk.Space(threaded=True)
    draw_options = pymunk.pygame_util.DrawOptions(screen) 
    screen.fill(THECOLORS["lightgreen"])

    winner = 0
    reward_1 = 0
    score_1 = 0
    reward_2 = 0
    score_2 = 0
    next_state_1 = INITIAL_STATE_1
    next_state_2 = INITIAL_STATE_2
    # Setup arena
    obstacles = setup_level(space)
    # Add player 1 to the arena (already initialized in Utils.py)
    space.add(player1_body, player1_shape)
    # Add player 2 to the arena (already initialized in Utils.py)
    space.add(player2_body, player2_shape)
    space.debug_draw(draw_options)
    it = 0
    while it < TIME_STEP*DURATION_OF_ROUND:  # Number of ticks in a single episode - 60fps in 180s
        print "Tick number: " + str(it+1)
        it += 1
        send_state(str(next_state_1) + ";REWARD" + str(reward_1), conn1)
        send_state(str(next_state_2) + ";REWARD" + str(reward_2), conn2)
        a1 = request_action(conn1)
        a2 = request_action(conn2)
        if not a1:  # response empty player 1
            print "No response from player 1, aborting"
            sys.exit()
        elif a1 == timeout_msg:
            print "Player 1 timeout, aborting"
            sys.exit()
        elif not a2: # response empty player 2
            print "No response from player 2, aborting"
            sys.exit()
        elif a2 == timeout_msg:
            print "Player 2 timeout, aborting"
            sys.exit()
        else:
            action_1 = tuplise(a1.replace(" ", "").split(','))
            action_2 = tuplise(a2.replace(" ", "").split(','))

        next_state_1, next_state_2, reward_1, reward_2 = play(space, next_state_1, action_1, next_state_2, action_2, score_1, score_2)
        screen.fill(THECOLORS["lightgreen"])
        space.debug_draw(draw_options)
        if next_state_1["HP"] <= 0:
            winner = 2
            print 'Player 2 wins!'
            break
        if next_state_2["HP"] <= 0:
            winner = 1
            print 'Player 1 wins!'
            break

        if next_state_1["barrel_heat"] < 0:
            next_state_1["barrel_heat"] = 0
        if next_state_2["barrel_heat"] < 0:
            next_state_2["barrel_heat"] = 0
        if next_state_1["barrel_heat"]>=720:
            next_state_1["HP"] = next_state_1["HP"] - (next_state_1["barrel_heat"]-720)*40
        if it%(TIME_STEP/HEALTH_FREQUENCY)==0:
            if next_state_1["barrel_heat"]<720 and next_state_1["barrel_heat"]>360:
                next_state_1["HP"] = next_state_1["HP"] - (next_state_1["barrel_heat"]-360)*4
            if next_state_1["HP"] >= 400 and next_state_1["barrel_heat"] > 0:
                next_state_1["barrel_heat"] = next_state_1["barrel_heat"] - 12
            elif next_state_1["HP"] < 400 and next_state_1["HP"] > 0 and next_state_1["barrel_heat"] > 0:
                next_state_1["barrel_heat"] = next_state_1["barrel_heat"] - 24
        if next_state_2["barrel_heat"]>=720:
            next_state_2["HP"] = next_state_2["HP"] - (next_state_2["barrel_heat"]-720)*40
        if it%(TIME_STEP/HEALTH_FREQUENCY)==0:
            if next_state_2["barrel_heat"]<720 and next_state_2["barrel_heat"]>360:
                next_state_2["HP"] = next_state_2["HP"] - (next_state_2["barrel_heat"]-360)*4
            if next_state_2["HP"] >= 400 and next_state_2["barrel_heat"] > 0:
                next_state_2["barrel_heat"] = next_state_2["barrel_heat"] - 12
            elif next_state_2["HP"] < 400 and next_state_2["HP"] > 0 and next_state_2["barrel_heat"] > 0:
                next_state_2["barrel_heat"] = next_state_2["barrel_heat"] - 24

        p1=player1_body.position
        p2=player2_body.position
        pt1=p1
        pt2=p2
        r0=350*f2
        theta=atan((p2[1]-p1[1])/(p2[0]-p1[0]))
        pt1[0]=p1[0]+r0*cos(theta)
        pt1[1]=p1[1]+r0*sin(theta)
        pt2[0]=p2[0]+r0*cos(theta)
        pt2[1]=p2[1]+r0*sin(theta)
        query = space.segment_query_first(pt1,pt2,1,pymunk.ShapeFilter())
        if query.shape == None:
            score_1 = score_1 + ENEMY_SEEN_REWARD*10
            score_2 = score_2 + ENEMY_SEEN_REWARD*10
            next_state_1["armor_modules"] = player2_armors
            next_state_2["armor_modules"] = player1_armors
        else:
            next_state_1["armor_modules"] = None
            next_state_2["armor_modules"] = None
                
        # Defense cooldown
        if next_state_1["defense"] > 0:
            next_state_1["defense"] = next_state_1["defense"] - (1/TIME_STEP)
        if (1/TIME_STEP) - next_state_1["defense"] > 0:
            next_state_1["defense"] = 0            
        if next_state_2["defense"] > 0:
            next_state_2["defense"] = next_state_2["defense"] - (1/TIME_STEP)
        if (1/TIME_STEP) - next_state_2["defense"] > 0:
            next_state_2["defense"] = 0

        next_state_1["time_since_last_shoot"] = next_state_1["time_since_last_shoot"] + (1/TIME_STEP)
        next_state_2["time_since_last_shoot"] = next_state_2["time_since_last_shoot"] + (1/TIME_STEP)
        next_state_1["time_since_last_hit"] = next_state_1["time_since_last_hit"] + (1/TIME_STEP)
        next_state_2["time_since_last_hit"] = next_state_2["time_since_last_hit"] + (1/TIME_STEP)

        #TODO add reset defense_triggered to 0 every 1 minute 
        space.step(1/TIME_STEP)
        clock.tick(TIME_STEP)
    sys.exit()

