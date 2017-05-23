
import logging

from logging import info as prinf
from logging import debug as prind
from logging import warning as prinw
from logging import error as prine

import time

import random as rnd
from random import randint, choice, randrange
from math import radians, pi, sin, cos
import svgwrite as svg
import glob

import json

import os

svg.profile = 'tiny'

class UltrasoundSensor:

    def __init__(self, ent, name, open_angle=None, distance_range=None, category='ultrasound'):
        self.ent = ent
        self.name = name
        self.open_angle = open_angle
        self.distance_range = distance_range
        self.detected = False
        prinf('UltrasoundSensor created and entangled: %s %s', ent, name)


class Robot:

    cats = ['ultrasound', 'robot']

    def __init__(self, root, drive, robot_name='robot'):
        self.root = root
        self.robot_name = robot_name

        self.baseProfile = 'tiny' # 'full'
        self.__svg_dir__ = '../assets/objects/svg/'
        self.ents = {category: [] for category in Robot.cats}

        self.ultrasounds = {}

        self.cts = root.collision_types
        self.drive = drive
        self.create_robot()


    def create_robot_rect(self, name, color, stroke_color, mass, pos, siz):
        id_str = self.robot_name
        insert_pos = [pos[i] + siz[i]/2 for i in range(2)]
        self.pos = insert_pos
        cat = 'robot'
        info_dict = {
                    'mass': mass,
                    'object_info': {
                        'name': name,
                        'category': cat,
                    },
                }
        info_str = json.dumps(info_dict)

        rect = self.dwg.rect(id=id_str, insert=pos, size=siz,
                fill=color, stroke=stroke_color,
                description=info_str,
                )
        self.dwg.add(rect)

    def create_ultrasound(self, name, color, stroke_color, vert_list):
        cat = 'ultrasound'
        info_dict = {
                'collision_type': self.cts[cat],
                'object_info': {
                    'name': str(name),
                    'category': cat,
                    },
                }
        info_str = json.dumps(info_dict)
        id_str = self.robot_name + '_' + cat  +'_' + str(name)

 #           color = self.dwg.SolidColor('green', 0.2)
        gradient = svg.gradients.LinearGradient(color='#00FF00', opacity=0.2)

        ultra = self.dwg.polygon(vert_list,
                id=id_str, description=info_str).fill(
                        'green', opacity=0.2).stroke('white', width=1).dasharray([20,10])
        self.dwg.add(ultra)


    def add_entity(self, entity_info):
        category = entity_info['category']

        print(';;;;;;;;;;;;;;;;;;;;;', category)

        if category in 'ultrasound':
            us = UltrasoundSensor(**entity_info)
#            self.ultrasounds.append()
            self.ultrasounds[entity_info['ent']] = us


        #self.entities[category].append(ent)

 #   @property
  #  def ultrasounds(self):

   #    return self.Ultrasounds

    def ultrasound_hit(self, ultrasound_id, object_id):
        return self.ultrasound_detection(ultrasound_id, object_id, True)

    def ultrasound_miss(self, ultrasound_id, object_id):
        return self.ultrasound_detection(ultrasound_id, object_id, False)

    def ultrasound_detection(self, ultrasound_id, object_id, state):
        us = self.ultrasounds[ultrasound_id]
        us.detected = state
        return us.name

    def create_robot(self):
        self.color = '#FF0000'
        self.stroke_color = '#000000'
        self.path = self.__svg_dir__ + 'robot.svg'

 #       group = self.dwg.add(self.dwg.g(id='obstacles', fill=self.color))
#        Fw, Fh = self.field_size
 #       w, h = Fw, Fh
        w,h = 300,300
        siz = (str(w), str(h))
        print(siz)
        self.dwg = None
        fname = self.path
        self.dwg = svg.Drawing(fname, size=siz, debug=False, profile=self.baseProfile)
 #       self.dwg.profile = self.baseProfile

        self.create_robot_rect('dalek', '#FF0000', self.stroke_color, 100, (300, -100), [50,100])

        open_angle = radians(45)
        count_ultrasounds = 3
        names = ['right', 'middle', 'left' ]
        ultrasound_range = 100
        x0, y0 = self.pos[0] + 0, self.pos[1] - h/4
        for i in range(count_ultrasounds):
            # to center it
            shift_angle = count_ultrasounds / 2 * open_angle + radians(180)
            # cone edges
            edge_angles = (i * open_angle - shift_angle,
                     (1 + i) * open_angle - shift_angle)

 #           print(type(edge_angles[0]))

            edge_points = [[
                ultrasound_range * sin(edge_angle) + x0,
                ultrasound_range * cos(edge_angle) + y0
                ] for edge_angle in edge_angles]

            vert_list = [(x0, y0), edge_points[0], edge_points[1]]

            print('$'*42, self.dwg.profile)
            #self.root.pprint(dir(self.dwg))
            self.create_ultrasound(names[i], '#00FF00', self.stroke_color, vert_list)

        #group.add(rect)


        self.root.info('saving: ' + self.dwg.filename)
        self.dwg.save()

        return fname



