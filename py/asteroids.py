from kivy.clock import Clock
from kivy.core.window import Window

import logging

from logging import info as prinf
from logging import debug as prind
from logging import warning as prinw
from logging import error as prine

from functools import partial

# import time

import random as rnd
from random import randint, choice, randrange

# import svgwrite as svg
# import glob

# import json

# import os

from math import radians, pi, sin, cos


class Asteroids:
    def __init__(self, root):
        self.root = root
        pass

    def draw_asteroids(self):
        size = Window.size
        w, h = size[0], size[1]
        delete_time = 2.5
        create_asteroid = self.create_asteroid
        destroy_ent = self.root.destroy_created_entity
        for x in range(100):
            pos = (randint(0, w), randint(0, h))
            ent_id = create_asteroid(pos)
            Clock.schedule_once(partial(destroy_ent, ent_id), delete_time)

    #       self.app.ent_count += 100

    def create_asteroid(self, pos):
        x_vel = randint(-15, 15)
        y_vel = randint(-15, 15)
        angle = radians(randint(-360, 360))
        angular_velocity = radians(randint(-1500, -1500))
        shape_dict = {
            "inner_radius": 0,
            "outer_radius": 20,
            "mass": 50 - 40,
            "offset": (0, 0),
        }
        col_shape = {
            "shape_type": "circle",
            "elasticity": 1.0,
            "collision_type": 3,
            "shape_info": shape_dict,
            "friction": 1.0,
        }
        col_shapes = [col_shape]
        physics_component = {
            "main_shape": "circle",
            "velocity": (x_vel, y_vel),
            "position": pos,
            "angle": angle,
            "angular_velocity": angular_velocity,
            "vel_limit": 250,
            "ang_vel_limit": radians(11200),
            "mass": 50 - 40,
            "col_shapes": col_shapes,
        }

        create_component_dict = {
            "cymunk_physics": physics_component,
            "rotate_renderer": {
                "texture": "asteroid1",
                "size": (45, 45),
                "render": True,
            },
            "position": pos,
            "rotate": 0,
        }

        component_order = [
            "position",
            "rotate",
            "rotate_renderer",
            "cymunk_physics",
        ]

        return self.root.init_entity(
            create_component_dict, component_order, "asteroid"
        )
