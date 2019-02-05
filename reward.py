import pygame
from environment import *
from math import exp
score = [0]*num_of_players
state = [None]*num_of_players

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
ENEMY_SEEN_REWARD = 1

def ball_armor_collision(playershoot, playerhit):
    if pygame.time.get_ticks() - state[playerhit]["last_hit_time"] > 1000/float(MAX_HIT_FREQUENCY):
        print "HIT!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! by " + str(playershoot)
        if state[playerhit]["defense"] > 0: #Within 30s of defense zone
            score[playershoot] += SHOOT_HIT_COEFF*25
        else:
            score[playershoot] += SHOOT_HIT_COEFF*50

def refill(player):
    if state[player]['location_self'][0] > REFILL_ZONES[player][0]*f2 and state[player]['location_self'][0] < REFILL_ZONES[player][1]*f2 and state[player]['location_self'][1] > REFILL_ZONES[player][2]*f2 and state[player]['location_self'][1] < REFILL_ZONES[player][3]*f:
        print "SCORE INCREASING IN refill"
        score[player] = score[player] + REFILL_COEFF*(REFILL_NUMBER_AT_A_TIME - state[player]["projectiles_left"])

def defense_triggered(player):
    if state[player]["defense_triggered"] > 2:
        score[player] = score[player] - DEFENSE_TRIGGERED_PUNISHMENT
    elif state[player]["defense_triggered"] <= 2 and state[player]["defense_triggered"] <= 2:
        score[player] = score[player] + (DEFENSE_TRIGGERED_COEFF*(state[player]["defense_triggered"]))

def defense_charge(player):
    if state[player]["location_self"][0] > DEFENSE_ZONES[player][0]*f2 and state[player]["location_self"][0] < DEFENSE_ZONES[player][1]*f2 and state[player]["location_self"][1] > DEFENSE_ZONES[player][2]*f2 and state[player]["location_self"][1] < DEFENSE_ZONES[player][3]*f2:
        score[player] = score[player] + DEFENSE_CHARGE_COEFF*exp(DEFENSE_CHARGE_TIME_COEFF*state[player]["defense"])

def line_of_sight(space, player1, player2):
    p1=state[player1]['location_self']
    p2=state[player2]['location_self']
    pt1=state[player1]['location_self']
    pt2=state[player2]['location_self']
    r0=350*f2
    theta = atan((p2[1]-p1[1])/(p2[0]-p1[0]))
    pt1[0] = p1[0]+r0*cos(theta)
    pt1[1] = p1[1]+r0*sin(theta)
    pt2[0] = p2[0]+r0*cos(theta)
    pt2[1] = p2[1]+r0*sin(theta)
    query = space.segment_query_first(pt1, pt2, 1, pymunk.ShapeFilter())
    if query == None or query.shape == None:
        print "SCORE INCREASING IN line_of_sight"
        score[player1] = score[player1] + ENEMY_SEEN_REWARD*10

def calculate_reward(space, player):
    prevscore = score[player]
    refill(player)
    defense_triggered(player)
    defense_charge(player)
    for i in range(0, num_of_players):
        if i != player:
            line_of_sight(space, player, i)
    print "Reward for " + str(player) + " = " + str(score[player]-prevscore)
    return score[player]-prevscore