from thread import *
from environment import *
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
parser.add_argument('-m', '--manual', dest='m', type=bool, default=False, help="Whether to launch a random or a manual agent")
args = parser.parse_args()

host = '127.0.0.1'
port = args.port
n = args.n
m = args.m
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

def agent_process_state(state):
    flag = 0
    try:
        state, reward = parse_state_message(state)  # Get the state and reward
    except:
        pass
    i = int(random.random()*1000)

    a = ''
    if str(state) != '':
        print "FROM AGENT ---------------------------------------------------"
        print str(state)
        if i % 10 == 0 and 'projectiles_left' in state and state['projectiles_left'] > 38:
            a = '1,' + str(int(random.random()*180) - 90) + ',' + str(random.randrange(1, 25))
        else:
            a = '2,' + str(f2*float(random.randrange(0, 300))) + ',' + str(random.randrange(-10, 10)) + ',' + str(random.randrange(-5, 5))

    return agent_play(a)

def agent_play(action):
    flag = 1
    try:
        s.send(action)
    except Exception as e:
        print "Error in sending:",  action, " : ", e
        print "Closing connection"
        flag = 0
    return flag
    

if not m:
    while 1:
        state = s.recv(1024)  # Receive state from server
        if agent_process_state(state) == 0:
            break
else:
    angle = 0
    while 1:
        for event in pygame.event.get():
            if event.type == KEYDOWN and event.key == K_p:
                pygame.image.save(screen, "breakout.png")    
            elif event.type == KEYDOWN and event.key == K_LEFT:
                a = '2,' + str(600) + ',' + str(180) + ',' + str(0)
                agent_play(a)
            elif event.type == KEYUP and event.key == K_LEFT:
                a = '2,' + str(0) + ',' + str(180) + ',' + str(0)
                agent_play(a)
            elif event.type == KEYDOWN and event.key == K_RIGHT:                
                a = '2,' + str(600) + ',' + str(0) + ',' + str(0)
                agent_play(a)
            elif event.type == KEYUP and event.key == K_RIGHT:
                a = '2,' + str(0) + ',' + str(0) + ',' + str(0)
                agent_play(a)
            elif event.type == KEYDOWN and event.key == K_UP:
                a = '2,' + str(600) + ',' + str(90) + ',' + str(0)
                agent_play(a)
            elif event.type == KEYUP and event.key == K_UP:
                a = '2,' + str(0) + ',' + str(90) + ',' + str(0)
                agent_play(a)
            elif event.type == KEYDOWN and event.key == K_DOWN:
                a = '2,' + str(600) + ',' + str(270) + ',' + str(0)
                agent_play(a)
            elif event.type == KEYUP and event.key == K_DOWN:
                a = '2,' + str(0) + ',' + str(270) + ',' + str(0)
                agent_play(a)
            elif event.type == KEYDOWN and event.key == K_s:
                a = '2,' + str(0) + ',' + str(0) + ',' + str(20)
                agent_play(a)
            elif event.type == KEYUP and event.key == K_s:
                a = '2,' + str(0) + ',' + str(0) + ',' + str(0)
                agent_play(a)
            elif event.type == KEYDOWN and event.key == K_w:
                a = '2,' + str(0) + ',' + str(0) + ',' + str(-20)
                agent_play(a)
            elif event.type == KEYUP and event.key == K_w:
                a = '2,' + str(0) + ',' + str(0) + ',' + str(0)
                agent_play(a)
            elif event.type == KEYDOWN and event.key == K_e:
                angle += 5
            elif event.type == KEYUP and event.key == K_e:
                angle += 0
            elif event.type == KEYDOWN and event.key == K_d:
                angle -= 5
            elif event.type == KEYUP and event.key == K_d:
                angle -= 0
            elif event.type == KEYDOWN and event.key == K_SPACE:
                a = '1,' + str(angle) + ',' + str(2500)
                agent_play(a)
s.close()