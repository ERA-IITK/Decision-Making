import argparse
from game_models.ddqn_game_model import DDQNTrainer, DDQNSolver
import random
import math
import numpy as np
import cv2 as cv
import pygame
from pygame.color import THECOLORS
import pymunk
from pymunk.vec2d import Vec2d
from pymunk.pygame_util import DrawOptions as draw

LENGTH_COEFF = 10
f=0.14
y_outer=5000*f
x_outer=8000*f
f2 = 0.125 # factor to multiply by all dimensions given in rules manual
bottom_left = ((x_outer - 8000*f2)/2, (y_outer - 5000*f2)/2)
bottom_right = (bottom_left[0] + 8000*f2, bottom_left[1])
top_left = (bottom_left[0], bottom_left[1] + 5000*f2)
top_right = (bottom_right[0], top_left[1])
# PyGame init
width = 1120
height = 700
pygame.init()
screen = pygame.display.set_mode((width, height))
clock = pygame.time.Clock()

# Turn off alpha since we don't use it.
screen.set_alpha(None)

# Showing sensors and redrawing slows things down.
show_sensors = True
draw_screen = False

FRAMES_IN_OBSERVATION = 4
INPUT_SHAPE = (FRAMES_IN_OBSERVATION, 100, 160)
ACTION_SPACE_N = 3

class AIChallenge:

    def __init__(self):
        # Global-ish.
        self.crashed = False
        self.drawoptions = draw(screen)
        # Physics stuff.
        self.space = pymunk.Space()
        self.space.gravity = pymunk.Vec2d(0., 0.)
        # Create the car.
        self.create_car(100, 100, 0)
        # Record steps.
        self.time = 0
        self.goal = (int(top_right[0]/2), int(top_left[1]/2 + 700*f2))
        x, y = self.car_body.position
        self.init_heuristic = Vec2d(self.goal[0]-x, self.goal[1]-y).get_length()
        self.current_set_of_frames = np.zeros((FRAMES_IN_OBSERVATION, 100, 160))
        # Create walls.
        static = [
            pymunk.Segment(
                self.space.static_body,
                bottom_left, top_left, 4),
            pymunk.Segment(
                self.space.static_body,
                top_left, top_right, 4),
            pymunk.Segment(
                self.space.static_body,
                top_right, bottom_right, 4),
            pymunk.Segment(
                self.space.static_body,
                bottom_left, bottom_right, 4)
        ]
        for s in static:
            s.friction = 1.
            s.group = 1
            s.collision_type = 1
            s.color = THECOLORS['red']
        self.space.add(static)
        self.obstacles = []

        o1x = top_left[0] + 1700*f2
        o1y = top_left[1] - 1125*f2 
        o2x = 1525*f2 + bottom_left[0]
        o2y = bottom_left[1] + 1875*f2
        o3x = bottom_left[0] + 3375*f2
        o3y = 500*f2 + bottom_left[1]
        o4x = bottom_left[0] + 4000*f2
        o4y = bottom_left[1] + 2500*f2
        o5x = top_right[0] - 3375*f2
        o5y = top_left[1] - 500*f2
        o6x = top_right[0] - 1525*f2
        o6y = top_left[1] - 1900*f2
        o7x = bottom_right[0] - 1700*f2
        o7y = bottom_left[1] + 1000*f2
        self.create_rect_obstacle(o1x, o1y, 1000*f2,250*f2)
        self.create_rect_obstacle(o2x, o2y, 250*f2,1000*f2)
        self.create_rect_obstacle(o3x, o3y, 250*f2,1000*f2)
        self.create_rect_obstacle(o4x, o4y, 1000*f2,250*f2)
        self.create_rect_obstacle(o5x, o5y, 250*f2,1000*f2)
        self.create_rect_obstacle(o6x, o6y, 250*f2,1000*f2)
        self.create_rect_obstacle(o7x, o7y, 1000*f2,250*f2)
        game_mode, total_step_limit, total_run_limit = self._args()
        self._main_loop(self._game_model(game_mode, ACTION_SPACE_N), total_step_limit, total_run_limit)

    def new_handle(self):
        pass

    def create_rect_obstacle(self, x, y, w, h):
        brick_body = pymunk.Body(body_type=pymunk.Body.STATIC)
        brick_body.position = x, y
        brick_shape = pymunk.Poly.create_box(brick_body, (w,h))
        brick_shape.elasticity = 1.0
        brick_shape.color = THECOLORS['blue']
        brick_shape.collision_type = 1
        self.space.add(brick_body, brick_shape)
        return brick_shape

    def create_car(self, x, y, r):
        inertia = pymunk.moment_for_circle(1, 0, 14, (0, 0))
        self.car_body = pymunk.Body(1, inertia)
        self.car_body.position = x, y
        self.car_shape = pymunk.Circle(self.car_body, 25)
        self.car_shape.color = THECOLORS["white"]
        self.car_shape.elasticity = 1.0
        self.car_body.angle = r
        driving_direction = Vec2d(1, 0).rotated(self.car_body.angle)
        self.car_body.apply_impulse_at_world_point(driving_direction)
        self.space.add(self.car_body, self.car_shape)

    def frame_step(self, action):
        if action == 0:
            self.car_body.angle -= 0.204
        elif action == 1:
            self.car_body.angle -= 0.102
        elif action == 2:
            self.car_body.angle += 0

        driving_direction = Vec2d(1, 0).rotated(self.car_body.angle)
        self.car_body.velocity = 20* driving_direction
        screen.fill(THECOLORS["black"])
        self.space.debug_draw(self.drawoptions)
        self.space.step(1./10)
        if draw_screen:
            pygame.display.flip()
        clock.tick()
        x, y = self.car_body.position
        readings = self.get_sonar_readings(x, y, self.car_body.angle)
        pygame.draw.circle(screen, (255, 255, 0), (int(self.goal[0]), int(y_outer-self.goal[1])), 6)
        pygame.display.update()
        joining_line = Vec2d(self.goal[0]-x, self.goal[1]-y)
        pygame.draw.line(screen, (255, 255, 255), (self.goal[0], y_outer-self.goal[1]) , (x, y_outer-y), 4)
        pygame.display.update()
        j_angle = joining_line.angle
        j_angle = j_angle*int(j_angle>=0) + (j_angle+2*math.pi)*int(j_angle<0) 
        dist = math.sqrt((self.goal[0]-x)**2+(self.goal[1]-y)**2)
        terminal = False
        reward = 0
        print("init_heuristic = " + str(self.init_heuristic))
        print("current_heuristic = " + str(dist))
        print("current pos = " + str(x) + ", " + str(y))
        print("goal pos = " + str(self.goal))
        if self.car_is_crashed(readings):
            self.time -= 0.01
            self.crashed = True
            reward = -500 + self.time
            self.recover_from_crash(driving_direction)
            terminal = True
        elif joining_line.get_length() > 250*f2:
            self.time -= 0.01
            reward = (self.init_heuristic-joining_line.get_length())*LENGTH_COEFF
            if(self.time < -70):
                self.time = 0
                self.goal = (int(random.random()*29031)%8000*f2, int(random.random()*10093)%5000*f2)
                while not (self.goal[0] > bottom_left[0]+90 and self.goal[0] < top_right[0]-90 and self.goal[1] > bottom_left[1]+90 and self.goal[1] < top_left[1]-90 and screen.get_at((int(self.goal[0]), int(self.goal[1]))) == THECOLORS['black']):
                    self.goal = (int(random.random()*29031)%8000*f2, int(random.random()*10093)%5000*f2)
        else:
            self.time = 0
            reward = 300
            self.goal = (int(random.random()*29031)%8000*f2, int(random.random()*10093)%5000*f2)
            while not (self.goal[0] > bottom_left[0]+90 and self.goal[0] < top_right[0]-90 and self.goal[1] > bottom_left[1]+90 and self.goal[1] < top_left[1]-90 and screen.get_at((int(self.goal[0]), int(self.goal[1]))) == THECOLORS['black']):
                self.goal = (int(random.random()*29031)%8000*f2, int(random.random()*10093)%5000*f2)
            self.init_heuristic = Vec2d(self.goal[0]-x, self.goal[1]-y).get_length()
        if math.fabs(joining_line.angle-self.car_body.angle) < 0.102:
            reward += 100
        return reward, terminal

    def make_state(self):
        pygame.image.save(screen, "buffer.png")
        image = cv.imread("buffer.png")
        state = cv.resize(image, (160, 100))
        state = cv.cvtColor(state, cv.COLOR_BGR2GRAY)
        cv.imwrite("state.png", state)
        for i in range(0, FRAMES_IN_OBSERVATION-2):
            self.current_set_of_frames[i] = self.current_set_of_frames[i+1]
        self.current_set_of_frames[FRAMES_IN_OBSERVATION-1] = state

    def car_is_crashed(self, readings):
        if readings[0] == 1 or readings[1] == 1 or readings[2] == 1:
            return True
        else:
            return False

    def recover_from_crash(self, driving_direction):
        while self.crashed:
            self.car_body.velocity = -100 * driving_direction
            self.crashed = False
            for i in range(10):
                self.car_body.angle += .2 
                self.space.step(1./10)
                clock.tick()

    def get_sonar_readings(self, x, y, angle):
        readings = []
        arm_left = self.make_sonar_arm(x, y)
        arm_middle = arm_left
        arm_right = arm_left
        readings.append(self.get_arm_distance(arm_left, x, y, angle, 0.75))
        readings.append(self.get_arm_distance(arm_middle, x, y, angle, 0))
        readings.append(self.get_arm_distance(arm_right, x, y, angle, -0.75))
        if show_sensors:
            pygame.display.update()
        return readings

    def get_arm_distance(self, arm, x, y, angle, offset):
        i = 0
        for point in arm:
            i += 1
            rotated_p = self.get_rotated_point(x, y, point[0], point[1], angle + offset)
            if rotated_p[0] <= 0 or rotated_p[1] <= 0 \
                    or rotated_p[0] >= width or rotated_p[1] >= height:
                return i
            else:
                obs = screen.get_at(rotated_p)
                if self.get_track_or_not(obs) != 0:
                    return i
            if show_sensors:
                pygame.draw.circle(screen, (255, 255, 255), (rotated_p), 4)
        return i

    def make_sonar_arm(self, x, y):
        spread = 10
        distance = 20
        arm_points = []
        for i in range(1, 40):
            arm_points.append((distance + x + (spread * i), y))

        return arm_points

    def get_rotated_point(self, x_1, y_1, x_2, y_2, radians):
        x_change = (x_2 - x_1) * math.cos(radians) + \
            (y_2 - y_1) * math.sin(radians)
        y_change = (y_1 - y_2) * math.cos(radians) - \
            (x_1 - x_2) * math.sin(radians)
        new_x = x_change + x_1
        new_y = height - (y_change + y_1)
        return int(new_x), int(new_y)

    def get_track_or_not(self, reading):
        if reading == THECOLORS['black']:
            return 0
        else:
            return 1

    def _main_loop(self, game_model, total_step_limit, total_run_limit):
        run = 0
        total_step = 0
        while True:
            if total_run_limit is not None and run >= total_run_limit:
                print("Reached total run limit of: " + str(total_run_limit))
                exit(0)
            run += 1
            self.make_state()
            step = 0
            score = 0
            while True:
                if total_step >= total_step_limit:
                    print("Reached total step limit of: " + str(total_step_limit))
                    exit(0)
                total_step += 1
                step += 1
                action = game_model.move(self.current_set_of_frames) 
                reward, terminal = self.frame_step(action)
                score += reward
                current_state = self.current_set_of_frames
                self.make_state()
                game_model.remember(current_state, action, reward, self.current_set_of_frames, terminal)
                game_model.step_update(total_step)
                if terminal:
                    game_model.save_run(score, step, run)
                    break

    def _args(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("-m", "--mode", help="Choose from available modes: ddqn_train, ddqn_test. Default is 'ddqn_training'.", default="ddqn_training")
        parser.add_argument("-tsl", "--total_step_limit", help="Choose how many total steps (frames visible by agent) should be performed. Default is '5000000'.", default=5000000, type=int)
        parser.add_argument("-trl", "--total_run_limit", help="Choose after how many runs we should stop. Default is None (no limit).", default=None, type=int)
        args = parser.parse_args()
        game_mode = args.mode
        total_step_limit = args.total_step_limit
        total_run_limit = args.total_run_limit
        print("Selected mode: " + str(game_mode))
        print("Total step limit: " + str(total_step_limit))
        print("Total run limit: " + str(total_run_limit))
        return game_mode, total_step_limit, total_run_limit

    def _game_model(self, game_mode, action_space):
        if game_mode == "ddqn_training":
            return DDQNTrainer(INPUT_SHAPE, action_space)
        elif game_mode == "ddqn_testing":
            return DDQNSolver(INPUT_SHAPE, action_space)
        else:
            print("Unrecognized mode. Use --help")
            exit(1)

if __name__ == "__main__":
    AIChallenge()
