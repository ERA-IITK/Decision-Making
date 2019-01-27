from thread import *
import time
import socket
import sys
import argparse
import random
import ast

# Parse arguments
parser = argparse.ArgumentParser()
parser.add_argument('-p', '--port', dest="port", type=int, default=12121, help='port')
parser.add_argument('-rs', '--random-seed', dest="rng", type=int, default=0, help='Random Seed')
parser.add_argument('-n', '--player-number', dest="n", type=int, default=1, help="Player number (1 or 2)")
args = parser.parse_args()

host = '127.0.0.1'
port = args.port
n = args.n
random.seed(args.rng)  # Important

MAX_FORWARD_SPEED = 3000
MAX_TRANSLATION_SPEED = 2000
MAX_SHOOTING_SPEED = 25000

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.connect((host, port))

# Given a message from the server, parses it and returns state and action
def parse_state_message(msg):
    s = msg.split(";REWARD")
    s[0] = s[0].replace("Vec2d", "")
    try:
        reward = float(s[1])
    except:
        reward = 0
    state = ast.literal_eval(s[0])
    return state, reward

def agent_play(state):
    flag = 0
    try:
        state, reward = parse_state_message(state)  # Get the state and reward
    except:
        pass
    i = random.random()
    if str(state) != '':
        if i > 0 and state['projectiles_left'] > 0:
            a = '1,' + str(random.randrange(-92, 92)) + ',' + str(random.randrange(1, 25))
        elif state['projectiles_left'] <= 0:
            a = '2,' + str(3.5*float(random.randrange(0, 3)/3)) + ',' + str(random.randrange(-180, 180)) + ',' + str(random.randrange(-5, 5))
        else:
            a = '6'

        try:
            s.send(a)
            flag = 1
        except Exception as e:
            print "Error in sending:",  a, " : ", e
            print "Closing connection"
            flag = 0
    return flag

while 1:
    state = s.recv(1024)  # Receive state from server
    if agent_play(state) == 0:
        break

s.close()