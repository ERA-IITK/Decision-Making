from utils import *
from thread import *
from math import pi
import time
import sys
import os
import argparse
import socket

start_time = time.time()
# Parse arguments
parser = argparse.ArgumentParser()
parser.add_argument('-v', '--visualization', dest="vis", type=int, default=0, help='visualization on/off')
parser.add_argument('-rr', '--', dest="render_rate", type=int, default=60, help='Render every nth frame')
parser.add_argument('-p1', '--port1', dest="port1", type=int, default=12121, help='Port for our player')
parser.add_argument('-p2', '--port2', dest="port2", type=int, default=34343, help='Port for opponent player')
parser.add_argument('-rs', '--random-seed', dest="rng", type=int, default=0, help='Random Seed')
parser.add_argument('-n', '--noise', dest="noise", type=int, default=1, help='Turn noise on/off')
parser.add_argument('-log', '--log', dest="log", type=str, default="log1", help='Name of logfile')
args = parser.parse_args()
log = args.log
render_rate = args.render_rate
vis = args.vis
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
timeout_period = 0.5
obstacles = None
##########################################################################

def play(state_1, action_1, state_2, action_2, score_1, score_2):
    # Getting state of player 1
    prevscore_1 = score_1
    location_self_1 = state_1["location_self"]
    location_op_1 = state_1["location_op"]
    HP_1 = state_1["HP"]
    defense_1 = state_1["defense"]
    defense_triggered_1 = state_1["defense_triggered"]
    barrel_heat_1 = state_1["barrel_heat"]
    projectiles_left_1 = state_1["projectiles_left"]
    # Getting state of player 2
    location_self_2 = state_2["location_self"]
    location_op_2 = state_2["location_op"]
    HP_2 = state_2["HP"]
    defense_2 = state_2["defense"]
    defense_triggered_2 = state_2["defense_triggered"]
    barrel_heat_2 = state_2["barrel_heat"]
    projectiles_left_2 = state_2["projectiles_left"]

    # 1 - Shoot action = {action_type, yaw, speed}
    # 2 - Chase action = {action_type, velocity, orientation} Cover even rotating in a given position in order to be able to shoot
    # 3 - Refill action = {action_type, velocity, orientation} Position of the refill zone and the best orientation of the robot
    # 4 - Defense action = {action_type, velocity, orientation} Position of the defense zone and the best orientaton of the robot
    # 5 - Escape action = {action_type, velocity, orientation} Position and orientation of the robot in the best escape spot
    # 6 - Roam action = {action_type}
    if action_1[0] == 1: #Shoot
        spawn_ball(space, player1_body.position, action_1[1])
        barrel_heat_1 = barrel_heat_1 + action_1[1]
    elif action_1[0] == 2: #Chase
        translate_player(action_1["velocity"]["linearspeed"], action_1["velocity"]["direction"], 1)
    elif action_1[0] == 3: #Refill
        if location_self_1[0] > 3500*f and location_self_1[0] < 4500*f and location_self_1[1] > 4000*f location_self_1[1] < 5000*f:
            score_1 = score_1 + REFILL_COEFF*(REFILL_NUMBER_AT_A_TIME - projectiles_left_1)
            projectiles_left_1 = projectiles_left_1 + REFILL_NUMBER_AT_A_TIME
        else:
            translate_player(action_1["velocity"]["linearspeed"], action_1["velocity"]["direction"], 1)
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
        elif location_self_1[0] > 5800*f and location_self_1[0] < 6800*f and location_self_1[1] > 1250*f location_self_1[1] < 2250*f:
            defense_1 = defense_1 - (1/TIME_STEP)
            score_1 = score_1 + DEFENSE_CHARGE_COEFF*exp(DEFENSE_CHARGE_TIME_COEFF*defense_1)
        else:
            translate_player(action_1["velocity"]["linearspeed"], action_1["velocity"]["direction"], 1)
            if defense_triggered_1 < 2 and defense_1 == 0:
                score_1 = score_1 #TODO
    elif action_1[0] == 5: #Escape
        translate_player(action_1["velocity"]["linearspeed"], action_1["velocity"]["direction"], 1)
    elif action_1[0] == 6: #Roam
        translate_player(action_1["velocity"]["linearspeed"], action_1["velocity"]["direction"], 1)

    if action_2[0] == 1: #Shoot
        spawn_ball(space, player2_body.position, action[_21])
        barrel_heat_2 = barrel_heat_2 + action_2[1]
    elif action_2[0] == 2: #Chase
        translate_player(action_2["velocity"]["linearspeed"], action_2["velocity"]["direction"], 2)
    elif action_2[0] == 3: #Refill
        if location_self_2[0] > 3500*f and location_self_2[0] < 4500*f and location_self_2[1] > 0*f location_self_2[1] < 1000*f:
            score_2 = score_2 + REFILL_COEFF*(REFILL_NUMBER_AT_A_TIME - projectiles_left_1)
            projectiles_left_2 = projectiles_left_2 + REFILL_NUMBER_AT_A_TIME
        else:
            translate_player(action_2["velocity"]["linearspeed"], action_2["velocity"]["direction"], 2)
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
        elif location_self_2[0] > 1200*f and location_self_2[0] < 2200*f and location_self_2[1] > 2750*f location_self_2[1] < 3750*f:
            defense_2 = defense_2 - (1/TIME_STEP)
            score_2 = score_2 + DEFENSE_CHARGE_COEFF*exp(DEFENSE_CHARGE_TIME_COEFF*defense_2)
        else:
            translate_player(action_2["velocity"]["linearspeed"], action_1["velocity"]["direction"], 2)
            if defense_triggered_2 < 2 and defense_2 == 0:
                score_2 = score_2 #TODO
    elif action_2[0] == 5: #Escape
        translate_player(action_2["velocity"]["linearspeed"], action_2["velocity"]["direction"], 2)
    elif action_2[0] == 6: #Roam
        translate_player(action_2["velocity"]["linearspeed"], action_2["velocity"]["direction"], 2)

    if vis == 1:
        draw_options = pymunk.pygame_util.DrawOptions(screen)

    # Remove projectiles collided with obstacle
    for projectile in projectiles:
        for obstacle in obstacles
        if dist(projectile.body.position, obstacle.body.position) < 1:
            space.remove(projectile, projectile.body)
            break
    # Remove projectiles collided with armor module
    for projectile in projectiles:
        for armor in player1_armors:
            if dist(projectile.body.position, armor.body.position) < 1:
            if defense > 0: #Within 30s of defense zone
                HP_1 -= 25
                score_2 += SHOOT_HIT_COEFF*25
            else:
                HP_1 -= 50
                score_2 += SHOOT_HIT_COEFF*50
            space.remove(projectile, projectile.body)
        for armor in player2_armors:
            if dist(projectile.body.position, armor.body.position) < 1:
            if defense > 0: #Within 30s of defense zone
                HP_2 -= 25
                score_1 += SHOOT_HIT_COEFF*25
            else:
                HP_2 -= 50
                score_1 += SHOOT_HIT_COEFF*50
            space.remove(projectile, projectile.body)

    pygame.display.flip()
    clock.tick()
        
    # Do post processing and return the next State
    if HP1 == 0 or HP2 == 0 or ticks > TICKS_LIMIT:
        state_new = {"location_self": [], "location_op": [], "HP": 0, "defense": 0, "barrel_heat": 0, "projectiles_left": 0}
        state_new["location_self"] = player1_body.body_position
        state_new["location_op"] = player2_body.body_position
        state_new["HP"] = HP
        state_new["defense"] = defense
        if action[0] == 1: #Shoot
            state_new["barrel_heat"] = state_new["barrel_heat"] + action[2]
            
        return state_new, score1-prevscore1, score2-prevscore2

# Generate logs
def logger(log, msg):
    f = open("logs/"+log, "a")
    f.write(msg)
    f.close()


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

    winner = 0
    reward1 = 0
    score1 = 0
    reward2 = 0
    score2 = 0
    state_1 = INITIAL_STATE_1
    next_state_1 = state_1
    state_2 = INITIAL_STATE_2
    next_state_2 = state_2
    it = 0

    pygame.init()
    clock = pygame.time.Clock()
    if vis == 1:
        screen = pygame.display.set_mode((BOARD_SIZE, BOARD_SIZE))
        pygame.display.set_caption("Carrom RL Simulation")
    space = pymunk.Space(threaded=True)
    # Setup arena
    obstacles = setup_level(space)
    # Add player 1 to the arena (already initialized in Utils.py)
    space.add(player1_body, player1_shape)
    # Add player 2 to the arena (already initialized in Utils.py)
    space.add(player2_body, player2_shape)

    while it < 10800:  # Number of ticks in a single episode - 60fps in 180s
        it += 1
        send_state(str(next_state_1) + str(reward_1), conn1)
        send_state(str(next_state_2) + str(reward_2), conn2)
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
            action1 = tuplise(a1.replace(" ", "").split(','))
            action2 = tuplise(a1.replace(" ", "").split(','))

        next_state, queen_flag, reward = play(next_state, 1, validate(action, next_state))
        # Defense cooldown
        if next_state["defense"] > 0:
            next_state["defense"] = next_state["defense"] - (1/TIME_STEP)
        if (1/TIME_STEP) - next_state["defense"] > 0:
            next_state["defense"] = 0            
        space.step(1/TIME_STEP)
        clock.tick(TIME_STEP)

    if it >= 5000:
        print "Player took more than 500 turns, aborting"
        sys.exit()