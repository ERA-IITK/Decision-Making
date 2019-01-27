import math, sys, random
import os

import pygame
from pygame.locals import *
from pygame.color import *
from math import sqrt, sin, cos, tan    
import pymunk
from pymunk import Vec2d
import pymunk.pygame_util
from collections import namedtuple
f=0.14
y_outer=5000*f
x_outer=8000*f
width = int(round(x_outer))
height = int(round(y_outer))
hp1=100
hp2=100
f2 = 0.125 # factor to multiply by all dimensions given in rules manual
x1 = (x_outer-8000*f2)/2# bottom left
y1 = (y_outer-5000*f2)/2
x2 = x1+8000*f2 #bottom right
y2 = y1
x3 = x1 #top left
y3 = y1+5000*f2
x4 = x2 #top right
y4 = y3
count=0

collision_types = {
    "ball": 1,
    "brick": 2,
#    "bottom": 3,
    "player": 3,
    "player2": 4,
    "armor1": 5,
    "armor2": 6
}


def spawn_ball(space, position, direction):
    ball_body = pymunk.Body(1, pymunk.inf)
    ball_body.position = position
    
    ball_shape = pymunk.Circle(ball_body, 8.5*f2)
    ball_shape.color =  THECOLORS["black"]
    ball_shape.elasticity = 0.0
    ball_shape._set_friction =1.0
    ball_shape.collision_type = collision_types["ball"]
    
    ball_body.apply_impulse_at_local_point(Vec2d(direction))
    
    #Keep ball velocity at a static value
    def constant_velocity(body, gravity, damping, dt):
        body.velocity = body.velocity.normalized() * 400
    ball_body.velocity_func = constant_velocity 
    
    space.add(ball_body, ball_shape)

def setup_level(space, player_body):
    
    
            
    # Spawn a ball for the player to have something to play with
    #spawn_ball(space, player_body.position + (0,40), random.choice([(1,10),(-1,10)]))
    
    
    
    
    #obstacle 1
    o1x =  x3 +1700*f2
    o1y =  y3 - 1125*f2 
    brick_body = pymunk.Body(body_type=pymunk.Body.STATIC)
    brick_body.position = o1x, o1y
    brick_shape = pymunk.Poly.create_box(brick_body, (1000*f2,250*f2))
    brick_shape.elasticity = 0.0
    brick_shape.friction = 10000.0
    brick_shape.color = THECOLORS['blue']
#    brick_shape.group = 1
    brick_shape.collision_type = collision_types["brick"]
    space.add(brick_body, brick_shape)
    #obstacle 2
    o2x= 1525*f2 + x1
    o2y=y1+ 1875*f2
    brick_body = pymunk.Body(body_type=pymunk.Body.STATIC)
    brick_body.position = o2x, o2y
    brick_shape = pymunk.Poly.create_box(brick_body, (250*f2,1000*f2))
    brick_shape.elasticity = 0.0
    brick_shape.friction = 10000.0
    brick_shape.color = THECOLORS['blue']
#    brick_shape.group = 1
    brick_shape.collision_type = collision_types["brick"]
    space.add(brick_body, brick_shape)
    #obstacle 3
    o3x= x1 + 3375*f2
    o3y= 500*f2 + y1
    brick_body = pymunk.Body(body_type=pymunk.Body.STATIC)
    brick_body.position = o3x, o3y
    brick_shape = pymunk.Poly.create_box(brick_body, (250*f2,1000*f2))
    brick_shape.elasticity = 0.0
    brick_shape.friction = 10000.0
    brick_shape.color = THECOLORS['blue']
#    brick_shape.group = 1
    brick_shape.collision_type = collision_types["brick"]
    space.add(brick_body, brick_shape)
    #obstacle 4
    o4x =  x1 +4000*f2
    o4y =  y1 + 2500*f2
    brick_body = pymunk.Body(body_type=pymunk.Body.STATIC)
    brick_body.position = o4x, o4y
    brick_shape = pymunk.Poly.create_box(brick_body, (1000*f2,250*f2))
    brick_shape.elasticity = 0.0
    brick_shape.friction = 10000.0
    brick_shape.color = THECOLORS['blue']
#    brick_shape.group = 1
    brick_shape.collision_type = collision_types["brick"]
    space.add(brick_body, brick_shape)

    #obstacle 5
    o5x= x4 - 3375*f2
    o5y= y3 - 500*f2
    brick_body = pymunk.Body(body_type=pymunk.Body.STATIC)
    brick_body.position = o5x, o5y
    brick_shape = pymunk.Poly.create_box(brick_body, (250*f2,1000*f2))
    brick_shape.elasticity = 0.0
    brick_shape.friction = 10000.0
    brick_shape.color = THECOLORS['blue']
#    brick_shape.group = 1
    brick_shape.collision_type = collision_types["brick"]
    space.add(brick_body, brick_shape)
    #obstacle 6
    o6x= x4 - 1525*f2
    o6y= y3 - 1900*f2
    brick_body = pymunk.Body(body_type=pymunk.Body.STATIC)
    brick_body.position = o6x, o6y
    brick_shape = pymunk.Poly.create_box(brick_body, (250*f2,1000*f2))
    brick_shape.elasticity = 0.0
    brick_shape.friction = 10000.0
    brick_shape.color = THECOLORS['blue']
#    brick_shape.group = 1
    brick_shape.collision_type = collision_types["brick"]
    space.add(brick_body, brick_shape)
    #obstacle 7
    o7x =  x2 - 1700*f2
    o7y =  y1 + 1125*f2
    brick_body = pymunk.Body(body_type=pymunk.Body.STATIC)
    brick_body.position = o7x, o7y
    brick_shape = pymunk.Poly.create_box(brick_body, (1000*f2,250*f2))
    brick_shape.elasticity = 0.0
    brick_shape.friction = 10000.0
    brick_shape.color = THECOLORS['blue']
#    brick_shape.group = 1
    brick_shape.collision_type = collision_types["brick"]
    space.add(brick_body, brick_shape)


    ### Game area
    
    static_lines = [pymunk.Segment(space.static_body, (x1,y1), (x2,y2), 2)
                ,pymunk.Segment(space.static_body, (x2, y2), (x4, y4), 2)
                ,pymunk.Segment(space.static_body, (x1,y1), (x3, y3), 2),
                pymunk.Segment(space.static_body, (x3, y3), (x4, y4), 2)
                ]  
               
    for line in static_lines:
        line.color = THECOLORS['black']
        line.elasticity = 0.0
        line.friction = 10000.0
        line.collision_type = collision_types["brick"]
    
    space.add(static_lines)
    
    

    refill_lines = [pymunk.Segment(space.static_body,(x1+3500*f2,y1),(x1+4500*f2,y1),2),
    pymunk.Segment(space.static_body,(x1+3500*f2,y1),(x1+3500*f2,y1+1000*f2),2),
    pymunk.Segment(space.static_body,(x1+3500*f2,y1+1000*f2),(x1+4500*f2,y1+1000*f2),2),
    pymunk.Segment(space.static_body,(x1+4500*f2,y1),(x1+4500*f2,y1+1000*f2),2)

    ]

    for line in refill_lines:
        line.color = THECOLORS['black']
        line.sensor = True

    space.add(refill_lines)

    refill_lines2 = [pymunk.Segment(space.static_body,(x1+3500*f2,y3),(x1+4500*f2,y3),2),
    pymunk.Segment(space.static_body,(x1+3500*f2,y3-1000*f2),(x1+3500*f2,y3),2),
    pymunk.Segment(space.static_body,(x1+3500*f2,y3-1000*f2),(x1+4500*f2,y3-1000*f2),2),
    pymunk.Segment(space.static_body,(x1+4500*f2,y3),(x1+4500*f2,y3-1000*f2),2)

    ]

    for line in refill_lines2:
        line.color = THECOLORS['black']
        line.sensor = True

    space.add(refill_lines2)


    bonus_lines1 = [pymunk.Segment(space.static_body,(x1+1200*f2,y3-1250*f2),(x1+2200*f2,y3-1250*f2),2),
    pymunk.Segment(space.static_body,(x1+1200*f2,y3-1250*f2),(x1+1200*f2,y3-2250*f2),2),
    pymunk.Segment(space.static_body,(x1+1200*f2,y3-2250*f2),(x1+2200*f2,y3-2250*f2),2),
    pymunk.Segment(space.static_body,(x1+2200*f2,y3-1250*f2),(x1+2200*f2,y3-2250*f2),2)

    ]

    for line in bonus_lines1:
        line.color = THECOLORS['black']
        line.sensor = True

    space.add(bonus_lines1)

    bonus_lines2 = [pymunk.Segment(space.static_body,(x2-1200*f2,y2+2250*f2),(x2-2200*f2,y2+2250*f2),2),
    pymunk.Segment(space.static_body,(x2-2200*f2,y2+2250*f2),(x2-2200*f2,y2+1250*f2),2),
    pymunk.Segment(space.static_body,(x2-2200*f2,y2+2250*f2),(x2-2200*f2,y2+1250*f2),2),
    pymunk.Segment(space.static_body,(x2-1200*f2,y2+1250*f2),(x2-1200*f2,y2+2250*f2),2)

    ]

    for line in bonus_lines2:
        line.color = THECOLORS['black']
        line.sensor = True

    space.add(bonus_lines2)


    



    
def main():
    ### PyGame init
    pygame.init()
    screen = pygame.display.set_mode((width,height)) 
    clock = pygame.time.Clock()
    running = True
    font = pygame.font.SysFont("Arial", 16)
    ### Physics stuff
    space = pymunk.Space()  
    draw_options = pymunk.pygame_util.DrawOptions(screen) 
    
    
    
    
    
    
    
    

    
    
    ### Player ship
#    STRIKER_MASS = 2.8
#    STRIKER_RADIUS = 20.6
#    STRIKER_ELASTICITY = 0.7
#    STRIKER_COLOR = [65, 125, 212]
    #inertia = pymunk.moment_for_circle(STRIKER_MASS, 0, STRIKER_RADIUS, (0, 0))


    player_body = pymunk.Body(500,pymunk.inf)
    player_body.position = 300, 100
    #player_shape = pymunk.Poly.create_box(player_body, (600*f2,600*f2))
    player_shape = pymunk.Circle(player_body, (300*f2))
    player_shape.elasticity = 0
    player_shape.friction = 1.0
    player_shape.color = THECOLORS['red']
#    player_shape.group = 1
    player_shape.collision_type = collision_types["player"]
    

#    player_shape2=pymunk.Circle(player_body,STRIKER_RADIUS, (0,0))
#    player_shape2.color = THECOLORS["black"]
    

    player_shape3 = pymunk.Segment(player_body,(-300*f2,-65*f2),(-300*f2,65*f2),2)
    player_shape3.color=THECOLORS['black']
    player_shape3.collision_type = collision_types["armor1"]

    player_shape4 = pymunk.Segment(player_body,(-65*f2,-300*f2),(65*f2,-300*f2),2)
    player_shape4.color=THECOLORS['black']
    player_shape4.collision_type = collision_types["armor1"]

    player_shape5 = pymunk.Segment(player_body,(300*f2,-65*f2),(300*f2,65*f2),2)
    player_shape5.color=THECOLORS['black']
    player_shape5.collision_type = collision_types["armor1"]

    player_shape6 = pymunk.Segment(player_body,(-65*f2,300*f2),(65*f2,300*f2),2)
    player_shape6.color=THECOLORS['black']
    player_shape6.collision_type = collision_types["armor1"]
    anglen=player_shape6._get_normal
    

    angle=0
    player_shape7 = pymunk.Segment(player_body,(0,0),(250*f2*cos(angle),250*f2*sin(angle)),3)
    player_shape7.color = THECOLORS['blue']
    


    player2_body = pymunk.Body(500,pymunk.inf)
    player2_body.position = 500, 600
    #player2_shape = pymunk.Poly.create_box(player2_body, (600*f2,600*f2))
    player2_shape = pymunk.Circle(player2_body, (300*f2))
    player2_shape.elasticity = 0
    player2_shape.friction = 1.0
    player2_shape.color = THECOLORS['red']
#    player2_shape.group = 1
    player2_shape.collision_type = collision_types["player2"]
    

#    player2_shape2=pymunk.Circle(player2_body,STRIKER_RADIUS, (0,0))
#    player2_shape2.color = THECOLORS["black"]

    player2_shape3 = pymunk.Segment(player2_body,(-300*f2,-65*f2),(-300*f2,65*f2),2)
    player2_shape3.color=THECOLORS['black']
    player2_shape3.collision_type = collision_types["armor2"]

    player2_shape4 = pymunk.Segment(player2_body,(-65*f2,-300*f2),(65*f2,-300*f2),2)
    player2_shape4.color=THECOLORS['black']
    player2_shape4.collision_type = collision_types["armor2"]

    player2_shape5 = pymunk.Segment(player2_body,(300*f2,-65*f2),(300*f2,65*f2),2)
    player2_shape5.color=THECOLORS['black']
    player2_shape5.collision_type = collision_types["armor2"]

    player2_shape6 = pymunk.Segment(player2_body,(-65*f2,300*f2),(65*f2,300*f2),2)
    player2_shape6.color=THECOLORS['black']
    player2_shape6.collision_type = collision_types["armor2"]
    
    

    angle=0
    player2_shape7 = pymunk.Segment(player2_body,(0,0),(250*f2*cos(angle),250*f2*sin(angle)),3)
    player2_shape7.color = THECOLORS['blue']
    



    

    #player_body.force=-10
    #player_body.apply_force(-20, vec2d(0,10))
    
    '''def pre_solve(arbiter, space, data):
        # We want to update the collision normal to make the bounce direction 
        # dependent of where on the paddle the ball hits. Note that this 
        # calculation isn't perfect, but just a quick example.
        set_ = arbiter.contact_point_set    
        if len(set_.points) > 0:
            player_shape = arbiter.shapes[0]
            width = (player_shape.b - player_shape.a).x
            print(width)
            print(" and delta is ")
            
            delta = (player_shape.body.position - set_.points[0].point_a.x).x
            print(delta)
            normal = Vec2d(0, 1).rotated(delta / width / 2)
            set_.normal = normal
            set_.points[0].distance = 0
        arbiter.contact_point_set = set_        
        return True
    h = space.add_collision_handler(
        collision_types["player"],
        collision_types["ball"])
    h.pre_solve = pre_solve '''
    
    def remove_first(arbiter, space, data):
        ball_shape = arbiter.shapes[0]
        space.remove(ball_shape, ball_shape.body)
        return True
    h = space.add_collision_handler(
        collision_types["ball"], 
        collision_types["brick"])
    h.begin = remove_first

    def hit_armor(arbiter, space, data):
        global hp2
        ball_shape = arbiter.shapes[0]
        armor_shape = arbiter.shapes[1]
        space.remove(ball_shape, ball_shape.body)
        hp2=hp2-10
        print("hooray")
        #print(arbiter.shapes)
        #print( space.shape_query(armor_shape))
        return True
    def hitend_armor(arbiter, space, data):
        player2_body.velocity=(0,0)
        player2_body.angular_velocity = 0
    h = space.add_collision_handler(
        collision_types["ball"], 
        collision_types["armor2"])
    h.begin = hit_armor
    h.separate = hitend_armor
    def hit_player(arbiter, space, data):
        ball_shape = arbiter.shapes[0]
        space.remove(ball_shape, ball_shape.body)
        return True
    def hitend_armor(arbiter, space, data):
        player2_body.velocity=(0,0)
        player2_body.angular_velocity = 0
    h = space.add_collision_handler(
        collision_types["ball"], 
        collision_types["player2"])
    h.begin = hit_player
    h.separate = hitend_armor

    def player_collision(arbiter, space, data):
        player_body.velocity=(0,0)
        player_body.angular_velocity = 0
        player2_body.velocity=(0,0)
        player2_body.angular_velocity = 0
        print("hit it")
    h1 = space.add_collision_handler(
        collision_types["player"], 
        collision_types["player2"])
    h2 = space.add_collision_handler(
        collision_types["player"], 
        collision_types["armor2"])
    h3 = space.add_collision_handler(
        collision_types["player2"], 
        collision_types["armor2"])
    h4 = space.add_collision_handler(
        collision_types["armor1"], 
        collision_types["armor2"])
    h1.begin = player_collision
    h1.separate = player_collision
    h2.begin = player_collision
    h2.separate = player_collision
    h3.begin = player_collision
    h3.separate = player_collision
    h4.begin = player_collision
    h4.separate = player_collision

    def wall1_collision(arbiter, space, data):
        player_body.velocity=(0,0)
        player_body.angular_velocity = 0
        print("hit the wall")
    def wall2_collision(arbiter, space, data):
        player2_body.velocity=(0,0)
        player2_body.angular_velocity = 0
        print("hit the wall")
    h1 = space.add_collision_handler(
        collision_types["player"], 
        collision_types["brick"])
    h2 = space.add_collision_handler(
        collision_types["player2"], 
        collision_types["brick"])
    h3 = space.add_collision_handler(
        collision_types["brick"], 
        collision_types["armor2"])
    h4 = space.add_collision_handler(
        collision_types["armor1"], 
        collision_types["brick"])
    h1.separate = wall1_collision
    h2.separate = wall2_collision
    h3.separate = wall2_collision
    h4.separate = wall1_collision


    def queryinfo():
        p1=player_body.position
        p2=player2_body.position
        pt1=p1
        pt2=p2
        r0=350*f2
        theta=math.atan((p2[1]-p1[1])/(p2[0]-p1[0]))
        pt1[0]=p1[0]+r0*math.cos(theta)
        pt1[1]=p1[1]+r0*math.sin(theta)
        pt2[0]=p2[0]+r0*math.cos(theta)
        pt2[0]=p2[0]+r0*math.sin(theta)
        query = space.segment_query_first(pt1,pt2,1,pymunk.ShapeFilter())
        if query:
            print("hooray")
        #c_p=query.point
        #line=pymunk.Segment(space.static_body,player_body.position,player2_body.position,1)
        #line.sensor=True
        #line.body.position=player_body.position
        #space.add(line)
        
    
    
    #space.add(bot_body, bot_shape)
    space.add(player_body, player_shape,player_shape3,player_shape4,player_shape5,player_shape6,player_shape7)
    space.add(player2_body, player2_shape,player2_shape3,player2_shape4,player2_shape5,player2_shape6,player2_shape7)

    global count
    global state
    # Start game
    setup_level(space, player_body)

    while running:
        #print(pymunk.Vec2d.get_angle_degrees_between(anglen,(1,0)))
        for event in pygame.event.get():
            if event.type == QUIT: 
                running = False
            elif event.type == KEYDOWN and event.key == K_y:
                queryinfo()
            elif event.type == KEYDOWN and (event.key in [K_ESCAPE, K_q]):
                running = False
            elif event.type == KEYDOWN and event.key == K_p:
                pygame.image.save(screen, "breakout.png")
                
            elif event.type == KEYDOWN and event.key == K_LEFT:
                
                #player_body.angular_velocity = -100
                #player_body.space.angular_velocity=300
                
                player_body.velocity = (-600,0)
            elif event.type == KEYUP and event.key == K_LEFT:
                
                #player_body.angular_velocity = 0
                #player_shape7.space.angular_velocity=0
                player_body.velocity = 0,0
                
            elif event.type == KEYDOWN and event.key == K_RIGHT:
                
                #player_body.angular_velocity = 100
                #player_shape7.space.angular_velocity=300
                player_body.velocity = (600,0)
            elif event.type == KEYUP and event.key == K_RIGHT:
                
                #player_body.angular_velocity = 0
                #player_shape7.space.angular_velocity=0
                player_body.velocity = 0,0

            elif event.type == KEYDOWN and event.key == K_UP:
                
                #player_body.angular_velocity = - 100
                #player_shape7.space.angular_velocity=-300
                player_body.velocity = (0,600)
            elif event.type == KEYUP and event.key == K_UP:
                
                #player_body.angular_velocity = 0
                #player_shape7.space.angular_velocity=0
                player_body.velocity = 0,0

            elif event.type == KEYDOWN and event.key == K_DOWN:
                
                #player_body.angular_velocity = 100
                #player_shape7.space.angular_velocity=300
                player_body.velocity = (0,-600)
            elif event.type == KEYUP and event.key == K_DOWN:
                 
                #player_body.angular_velocity = 0  
                #player_shape7.space.angular_velocity=0
                player_body.velocity = 0,0     
            elif event.type == KEYUP and event.key == K_s:
                angle+= 20
            elif event.type == KEYDOWN and event.key == K_s:
                angle+= 0
            elif event.type == KEYUP and event.key == K_w:
                angle-= 20
            elif event.type == KEYDOWN and event.key == K_w:
                angle+= 0
            elif event.type == KEYDOWN and event.key == K_r:
                setup_level(space, player_body)
            elif event.type == KEYDOWN and event.key == K_SPACE:
                if count<50:
                    spawn_ball(space, player_body.position + (340*f2*cos(angle),340*f2*sin(angle)), (cos(angle),sin(angle)) )
                    count=count+1
                elif count==50:
                    if player_body.position[0]<600 and player_body.position[0]>520 and player_body.position[1]>565 and player_body.position[1]<645:
                        count=0
                print(player_body.position)
                print(count)
            elif event.type == KEYDOWN and event.key == K_7:
                player2_body.angular_velocity = 100
            elif event.type == KEYUP and event.key == K_7:
                player2_body.angular_velocity = 0
            elif event.type == KEYDOWN and event.key == K_8:
                player2_body.angular_velocity = -100
            elif event.type == KEYUP and event.key == K_8:
                player2_body.angular_velocity = 0
            elif event.type ==  KEYDOWN and event.key == K_5:
                player2_body.velocity = (0,600) 
            elif event.type == KEYUP and event.key == K_5:
                player2_body.velocity =(0,0)
            elif event.type == KEYDOWN and event.key == K_2:
                player2_body.velocity=(0,-600)
            elif event.type == KEYUP and event.key == K_2:
                player2_body.velocity=(0,0)
            elif event.type ==  KEYDOWN and event.key == K_1:
                player2_body.velocity = (-600,0) 
            elif event.type == KEYUP and event.key == K_1:
                player2_body.velocity =(0,0)
            elif event.type == KEYDOWN and event.key == K_3:
                player2_body.velocity=(600,0)
            elif event.type == KEYUP and event.key == K_3:
                player2_body.velocity=(0,0)

            elif event.type ==  KEYDOWN and event.key == K_i:
                player_body.velocity = (0,600) 
            #elif event.type == KEYUP and event.key == K_i:
            #    player2_body.velocity =(0,0)
            elif event.type == KEYDOWN and event.key == K_k:
                player_body.velocity=(0,-600)
            #elif event.type == KEYUP and event.key == K_k:
            #    player2_body.velocity=(0,0)
            elif event.type ==  KEYDOWN and event.key == K_j:
                player_body.velocity = (-600,0) 
            #elif event.type == KEYUP and event.key == K_j:
            #    player2_body.velocity =(0,0)
            elif event.type == KEYDOWN and event.key == K_l:
                player_body.velocity=(600,0)
            #elif event.type == KEYUP and event.key == K_l:
            #    player2_body.velocity=(0,0)                                  
                   
        ### Clear screen
        screen.fill(THECOLORS["lightgreen"])
        
        
        ### Draw stuff
        space.debug_draw(draw_options)
        
        state = []
        for x in space.shapes:
            s = "%s %s %s" % (x, x.body.position, x.body.velocity)
            state.append(s)
        
        ### Update physics
        fps = 60
        dt = 1./fps
        space.step(dt)
        
        ### Info and flip screen
        screen.blit(font.render("hp2: " + str(hp2), 1, THECOLORS["black"]), (500,0))
        screen.blit(font.render("fps: " + str(clock.get_fps()), 1, THECOLORS["black"]), (0,0))
        screen.blit(font.render("#ERA-IITK", 1, THECOLORS["darkblue"]), (5,height - 35))
        screen.blit(font.render("#Rising of a new era", 1, THECOLORS["darkblue"]), (5,height - 20))
        
        pygame.display.flip()
        clock.tick(fps)
        
if __name__ == '__main__':
    sys.exit(main())
