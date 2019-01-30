# Utility functions for the game server
from pygame.locals import *
from pygame.color import *
from math import sqrt, sin, cos, tan, atan
import numpy as np
from random import randrange, gauss
from collections import OrderedDict
from pymunk import Vec2d
import pygame
import pymunk
import pymunk.pygame_util
import random
import sys
import os
import copy
import array


# Reward Coefficients
TIME_STEP = 60.0  # Step size for pymunk
DURATION_OF_ROUND = 180 # In seconds
REFILL_NUMBER_AT_A_TIME = 50
REFILL_COEFF = 1
REFILL_TRAVEL_COEFF = 1
DEFENSE_TRAVEL_COEFF = 1
DEFENSE_CHARGE_COEFF = 1
DEFENSE_CHARGE_TIME_COEFF = 1
DEFENSE_TRIGGERED_COEFF = 1
DEFENSE_TRIGGERED_PUNISHMENT = 100
SHOOT_HIT_COEFF = 1
ENEMY_CHASE_COEFF = 1
ENEMY_ESCAPE_COEFF = 1
TICKS_LIMIT = 10800
HEALTH_FREQUENCY = 10
ENEMY_SEEN_REWARD = 1
MAX_SHOOT_FREQUENCY = 10
MAX_HIT_FREQUENCY = 10
INITIAL_STATE_1 = {'location_self': None, 'location_op': None, 'HP': 2000, 'defense': 0, 'barrel_heat': 0, 'projectiles_left': 40, 'defense_triggered': 0, 'armor_modules': None, 'time_since_last_shoot': 0, 'time_since_last_hit': 0}
INITIAL_STATE_2 = {'location_self': None, 'location_op': None, 'HP': 2000, 'defense': 0, 'barrel_heat': 0, 'projectiles_left': 40, 'defense_triggered': 0, 'armor_modules': None, 'time_since_last_shoot': 0, 'time_since_last_hit': 0}

# Arena parameters
f=0.14
y_outer=5000*f
x_outer=8000*f
width = int(round(x_outer))
height = int(round(y_outer))
f2 = 0.125 # factor to multiply by all dimensions given in rules manual
x1 = (x_outer-8000*f2)/2# bottom left
y1 = (y_outer-5000*f2)/2
x2 = x1+8000*f2 #bottom right
y2 = y1
x3 = x1 #top left
y3 = y1+5000*f2
x4 = x2 #top right
y4 = y3
collision_types = {
    "ball": 1,
    "brick": 2,
    "player1": 3,
    "player2": 4,
    "armor1": 5,
    "armor2": 6
}
players = dict()

def make_player(number):
    player_armors = []
    player_body = pymunk.Body(500,pymunk.inf)
    player_shape = pymunk.Circle(player_body, (300*f2))
    player_shape.elasticity = 0
    player_shape.friction = 1.0
    player_shape.color = THECOLORS['red']
    player_shape.collision_type = collision_types["player"+str(number)]
    armor = pymunk.Segment(player_body,(-300*f2, -65*f2),(-300*f2, 65*f2), 2)
    armor.color=THECOLORS['black']
    armor.collision_type = collision_types["armor"+str(number)]
    player_armors.append(armor)
    armor = pymunk.Segment(player_body,(-65*f2, -300*f2),(65*f2, -300*f2), 2)
    armor.color=THECOLORS['black']
    armor.collision_type = collision_types["armor"+str(number)]
    player_armors.append(armor)
    armor = pymunk.Segment(player_body,(300*f2, -65*f2),(300*f2, 65*f2), 2)
    armor.color=THECOLORS['black']
    armor.collision_type = collision_types["armor"+str(number)]
    player_armors.append(armor)
    armor = pymunk.Segment(player_body,(-65*f2, 300*f2),(65*f2, 300*f2), 2)
    armor.color=THECOLORS['black']
    armor.collision_type = collision_types["armor"+str(number)]
    player_armors.append(armor)
    shooter_shape = pymunk.Segment(player_body,(0,0),(250*f2,0),3)
    shooter_shape.color = THECOLORS['blue']
    players[str(number)] = player_body
    return player_body, player_shape, shooter_shape, player_armors


def translate_player(linearspeed, direction, number):
    players[str(number)].velocity=(linearspeed*cos(direction), linearspeed*sin(direction))

def rotate_player(angularvelocity, number):
    players[str(number)].angular_velocity = angularvelocity    

def spawn_ball(position, direction, speed): #TODO Make this function accept a speed of launch
    ball_body = pymunk.Body(1, pymunk.inf)
    ball_body.position = position
    
    ball_shape = pymunk.Circle(ball_body, 8.5*f2)
    ball_shape.color =  THECOLORS["black"]
    ball_shape.elasticity = 1.0
    ball_shape.collision_type = collision_types["ball"]
    ball_body.apply_impulse_at_local_point(pymunk.Vec2d(cos(direction), sin(direction)))
    
    #Keep ball velocity at a static value
    def constant_velocity(body, gravity, damping, dt):
        body.velocity = body.velocity.normalized() * speed
    ball_body.velocity_func = constant_velocity
    return ball_body, ball_shape

# Initialize space
def setup_level(space):
    #obstacle 1
    obstacles = list()
    o1x =  x3 +1700*f2
    o1y =  y3 - 1125*f2 
    brick_body = pymunk.Body(body_type=pymunk.Body.STATIC)
    brick_body.position = o1x, o1y
    brick_shape = pymunk.Poly.create_box(brick_body, (1000*f2,250*f2))
    brick_shape.elasticity = 0.0
    brick_shape.friction = 10000.0
    brick_shape.color = THECOLORS['brown']
    brick_shape.collision_type = collision_types["brick"]
    space.add(brick_body, brick_shape)
    obstacles.append(brick_shape)
    #obstacle 2
    o2x= 1525*f2 + x1
    o2y=y1+ 1875*f2
    brick_body = pymunk.Body(body_type=pymunk.Body.STATIC)
    brick_body.position = o2x, o2y
    brick_shape = pymunk.Poly.create_box(brick_body, (250*f2,1000*f2))
    brick_shape.elasticity = 0.0
    brick_shape.friction = 10000.0
    brick_shape.color = THECOLORS['brown']
    brick_shape.collision_type = collision_types["brick"]
    space.add(brick_body, brick_shape)
    obstacles.append(brick_shape)
    #obstacle 3
    o3x= x1 + 3375*f2
    o3y= 500*f2 + y1
    brick_body = pymunk.Body(body_type=pymunk.Body.STATIC)
    brick_body.position = o3x, o3y
    brick_shape = pymunk.Poly.create_box(brick_body, (250*f2,1000*f2))
    brick_shape.elasticity = 0.0
    brick_shape.friction = 10000.0
    brick_shape.color = THECOLORS['brown']
    brick_shape.collision_type = collision_types["brick"]
    space.add(brick_body, brick_shape)
    obstacles.append(brick_shape)
    #obstacle 4
    o4x =  x1 +4000*f2
    o4y =  y1 + 2500*f2
    brick_body = pymunk.Body(body_type=pymunk.Body.STATIC)
    brick_body.position = o4x, o4y
    brick_shape = pymunk.Poly.create_box(brick_body, (1000*f2,250*f2))
    brick_shape.elasticity = 0.0
    brick_shape.friction = 10000.0
    brick_shape.color = THECOLORS['brown']
    brick_shape.collision_type = collision_types["brick"]
    space.add(brick_body, brick_shape)
    obstacles.append(brick_shape)
    #obstacle 5
    o5x= x4 - 3375*f2
    o5y= y3 - 500*f2
    brick_body = pymunk.Body(body_type=pymunk.Body.STATIC)
    brick_body.position = o5x, o5y
    brick_shape = pymunk.Poly.create_box(brick_body, (250*f2,1000*f2))
    brick_shape.elasticity = 0.0
    brick_shape.friction = 10000.0
    brick_shape.color = THECOLORS['brown']
    brick_shape.collision_type = collision_types["brick"]
    space.add(brick_body, brick_shape)
    obstacles.append(brick_shape)
    #obstacle 6
    o6x= x4 - 1525*f2
    o6y= y3 - 1900*f2
    brick_body = pymunk.Body(body_type=pymunk.Body.STATIC)
    brick_body.position = o6x, o6y
    brick_shape = pymunk.Poly.create_box(brick_body, (250*f2,1000*f2))
    brick_shape.elasticity = 0.0
    brick_shape.friction = 10000.0
    brick_shape.color = THECOLORS['brown']
    brick_shape.collision_type = collision_types["brick"]
    space.add(brick_body, brick_shape)
    obstacles.append(brick_shape)
    #obstacle 7
    o7x =  x2 - 1700*f2
    o7y =  y1 + 1125*f2
    brick_body = pymunk.Body(body_type=pymunk.Body.STATIC)
    brick_body.position = o7x, o7y
    brick_shape = pymunk.Poly.create_box(brick_body, (1000*f2,250*f2))
    brick_shape.elasticity = 0.0
    brick_shape.friction = 10000.0
    brick_shape.color = THECOLORS['brown']
    brick_shape.collision_type = collision_types["brick"]
    space.add(brick_body, brick_shape)
    obstacles.append(brick_shape)
    ### Game area
    static_lines = [pymunk.Segment(space.static_body, (x1,y1), (x2,y2), 2), pymunk.Segment(space.static_body, (x2, y2), (x4, y4), 2),
                    pymunk.Segment(space.static_body, (x1,y1), (x3, y3), 2), pymunk.Segment(space.static_body, (x3, y3), (x4, y4), 2)]  
    for line in static_lines:
        line.color = THECOLORS['black']
        line.elasticity = 0.0
        line.friction = 10000.0
        line.collision_type = collision_types["brick"]
    space.add(static_lines)
    obstacles.extend(static_lines)           
    refill_lines = [pymunk.Segment(space.static_body,(x1+3500*f2,y1),(x1+4500*f2,y1),2),
    pymunk.Segment(space.static_body,(x1+3500*f2,y1),(x1+3500*f2,y1+1000*f2),2),
    pymunk.Segment(space.static_body,(x1+3500*f2,y1+1000*f2),(x1+4500*f2,y1+1000*f2),2),
    pymunk.Segment(space.static_body,(x1+4500*f2,y1),(x1+4500*f2,y1+1000*f2),2)]
    for line in refill_lines:
        line.color = THECOLORS['black']
        line.sensor = True
    space.add(refill_lines)
    refill_lines2 = [pymunk.Segment(space.static_body,(x1+3500*f2,y3),(x1+4500*f2,y3),2),
    pymunk.Segment(space.static_body,(x1+3500*f2,y3-1000*f2),(x1+3500*f2,y3),2),
    pymunk.Segment(space.static_body,(x1+3500*f2,y3-1000*f2),(x1+4500*f2,y3-1000*f2),2),
    pymunk.Segment(space.static_body,(x1+4500*f2,y3),(x1+4500*f2,y3-1000*f2),2)]
    for line in refill_lines2:
        line.color = THECOLORS['black']
        line.sensor = True
    space.add(refill_lines2)
    bonus_lines1 = [pymunk.Segment(space.static_body,(x1+1200*f2,y3-1250*f2),(x1+2200*f2,y3-1250*f2),2),
    pymunk.Segment(space.static_body,(x1+1200*f2,y3-1250*f2),(x1+1200*f2,y3-2250*f2),2),
    pymunk.Segment(space.static_body,(x1+1200*f2,y3-2250*f2),(x1+2200*f2,y3-2250*f2),2),
    pymunk.Segment(space.static_body,(x1+2200*f2,y3-1250*f2),(x1+2200*f2,y3-2250*f2),2)]
    for line in bonus_lines1:
        line.color = THECOLORS['black']
        line.sensor = True
    space.add(bonus_lines1)
    bonus_lines2 = [pymunk.Segment(space.static_body,(x2-1200*f2,y2+2250*f2),(x2-2200*f2,y2+2250*f2),2),
                    pymunk.Segment(space.static_body,(x2-2200*f2,y2+2250*f2),(x2-2200*f2,y2+1250*f2),2),
                    pymunk.Segment(space.static_body,(x2-2200*f2,y2+2250*f2),(x2-2200*f2,y2+1250*f2),2),
                    pymunk.Segment(space.static_body,(x2-1200*f2,y2+1250*f2),(x2-1200*f2,y2+2250*f2),2)]
    for line in bonus_lines2:
        line.color = THECOLORS['black']
        line.sensor = True
    space.add(bonus_lines2)
    start_lines1 = [pymunk.Segment(space.static_body,(x1,y1),(x1+1000*f2,y1),2),    
    pymunk.Segment(space.static_body,(x1,y1),(x1,y1+1000*f2),2),
    pymunk.Segment(space.static_body,(x1+1000*f2,y1),(x1+1000*f2,y1+1000*f2),2),
    pymunk.Segment(space.static_body,(x1,y1+1000*f2),(x1+1000*f2,y1+1000*f2),2)]
    for line in start_lines1:
        line.color = THECOLORS['blue']
        line.sensor = True
    space.add(start_lines1)
    start_lines2 = [pymunk.Segment(space.static_body,(x4,y4),(x4-1000*f2,y4),2),
    pymunk.Segment(space.static_body,(x4,y4),(x4,y4-1000*f2),2),
    pymunk.Segment(space.static_body,(x4,y4-1000*f2),(x4-1000*f2,y4-1000*f2),2),
    pymunk.Segment(space.static_body,(x4-1000*f2,y4),(x4-1000*f2,y4-1000*f2),2)]
    for line in start_lines2:
        line.color = THECOLORS['red']
        line.sensor = True
    space.add(start_lines2)
    return obstacles

def draw_arrow(screen, position, angle):
    length = 100*f
    endpos_x = (position[0] + cos(angle) * length)
    endpos_y = (position[1] - (length* sin(angle)))
    pygame.draw.line(
        screen, (50, 255, 50), (endpos_x, endpos_y), position, 3)

# Parse the received action
def tuplise(s):
    if(int(s[0]) == 1):
        return (int(s[0]), round(float(s[1]), 4), round(float(s[2]), 4))
    else:
        return (int(s[0]), round(float(s[1]), 4), round(float(s[2]), 4), round(float(s[2]), 4))

def dist(p1, p2):
    return sqrt(pow(p1[0] - p2[0], 2) + pow(p1[1] - p2[1], 2))

class BACKGROUND(pygame.sprite.Sprite):

    def __init__(self, image_file, location):
        pygame.sprite.Sprite.__init__(self)  # call Sprite initializer
        self.image = pygame.image.load(image_file)
        self.rect = self.image.get_rect()
        self.rect.left, self.rect.top = location