
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




class Robot:

    def __init__(self, root, drive, robot_name='robot'):
        self.root = root
        self.robot_name = robot_name
#        self.pos = pos
        self.__svg_dir__ = '../assets/objects/svg/'
#        self.siz = siz

        self.cts = root.collision_types
        self.drive = drive
        self.create_robot()


    def create_robot_rect(self, color, stroke_color, mass, pos, siz):
        id_str = self.robot_name
        insert_pos = [pos[i] + siz[i]/2 for i in range(2)]
        self.pos = insert_pos
        cat = 'robot'
        info_dict = {
                    'mass': mass,
                    'category': cat
                }
        info_str = json.dumps(info_dict)

        rect = self.dwg.rect(id=id_str, insert=pos, size=siz, 
                fill=color, stroke=stroke_color,
                description=info_str,
                )
        self.dwg.add(rect)

    def create_ultrasound(self, i, color, stroke_color, vert_list):
        cat = 'ultrasound'
        info_dict = {
                'category': cat,
                'collision_type': self.cts[cat],
                'id': str(i)
                }
        info_str = json.dumps(info_dict)
        id_str = self.robot_name + '_' + cat  +'_' + str(i)
        ultra = self.dwg.polygon(vert_list,
                id=id_str, fill=color, stroke=stroke_color, description=info_str)
        self.dwg.add(ultra)


#        
    
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
        self.dwg = svg.Drawing(fname, size=siz, baseProfile='full', debug=False,)

        self.create_robot_rect('#FF0000', self.stroke_color, 100, (300, -100), [50,100])

        open_angle = radians(45)
        count_ultrasounds = 3
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

            self.create_ultrasound(id, '#00FF00', self.stroke_color, vert_list)
                    
        #group.add(rect)
    

        self.root.info('saving: ' + self.dwg.filename)
        self.dwg.save()

        return fname
        

    
