

from kivy.core.window import Window

import logging

from logging import info as prinf
from logging import debug as prind
from logging import warning as prinw
from logging import error as prine

import time

import random as rnd
from random import randint, choice, randrange
import svgwrite as svg
import glob

import json

import os


class Map2D:

    def __init__(self, root):
        self.root = root

        self.__svg_map_dir__ = '../assets/maps/svg/'
        self.clear_maps()
        self.cts = self.root.collision_types

        self.draw_walls()
        #self.draw_some_stuff()
        self.draw_obstacles()

    def clear_maps(self):
        prinf('Deleting maps in '+ self.__svg_map_dir__)
 #       shutil.rmtree(self.__svg_map_dir__)
        files = glob.glob(self.__svg_map_dir__ + '*')
        for f in files:
            os.remove(f)

    
    def draw_walls(self):
        Ww, Wh = Wsize = Window.size
        prinw(Wsize)
        self.root.info(Wsize)
        
        self.wall_id = 0
        # thickness
        t = 125
        txu = 'warning'

        x0, y0 = 30,30 
        #w0, h0 = Ww-2*x0, Wh-2*y0
        w0, h0 = 1000, 800
        self.field_size = w0, h0
        
        sizes = [(w0, t), (t, h0+2*t), (w0,t), (t, h0+2*t)]
        poss = [[0, -t], [w0, -t], [0, h0], [-t, -t]]
        poss = [[pos[0] + x0, pos[1] + y0] for pos in poss]
        
        for pos, size in zip(poss, sizes):
            self.create_wall(pos, size, txu)

        
    def create_wall(self, pos_lf, size, txu): 
        w, h = size
        cat = 'wall'
        pos = [pos_lf[i] + size[i]/2 for i in range(2)]
        model_key = cat + str(self.wall_id)
        self.root.gameworld.model_manager.load_textured_rectangle('vertex_format_4f', w, h, txu, model_key)
        mass = 0

        shape_dict = {'width': w, 'height': h, 'mass': mass, }
        col_shape = {
                'shape_type': 'box', 
                'elasticity': 1.0,
                'collision_type': self.cts[cat], 
                'shape_info': shape_dict, 'friction': 1.0
            }
        col_shapes = [col_shape]
        physics_component = {
                'main_shape': 'box',
                'velocity': (0, 0),
                'position': pos, 'angle': 0,
                'angular_velocity': 0,
                'vel_limit': 0,
                'ang_vel_limit': 0,
                'mass': mass, 'col_shapes': col_shapes
            }

        create_component_dict = {
                'cymunk_physics': physics_component,
                'rotate_renderer': {
                    'texture': txu,
                    'model_key': model_key,
                    },
                'position': pos,
                'rotate': 0,
            }

        component_order = ['position', 'rotate', 'rotate_renderer', 'cymunk_physics']
        self.wall_id += 1
        return self.root.init_entity(create_component_dict, component_order, cat)

    def draw_obstacles(self):
        fname = self.create_obstacles()
        self.root.fl.load_svg(fname, self.root.gameworld)

    def draw_stuff(self):
        self.draw_obstacles()

    def create_obstacles(self):
        self.color = '#42ACDC'
        self.stroke_color = '#000000'
        self.path = self.__svg_map_dir__ + 'map{}.svg'

        Fw, Fh = self.field_size
        
        w, h = Fw, Fh
        siz = (str(w), str(h))
        print(siz)
        self.dwg = None
        fname = self.path.format(time.time())
        self.dwg = svg.Drawing(fname, size=siz, baseProfile='full', debug=False,)
        
 #       group = self.dwg.add(self.dwg.g(id='obstacles', fill=self.color))

        dens_interval = (900, 1000)
 #       mass_interval = (1000, 5000)
        smaller = h if h<=w else w
        siz_min, siz_max = one_siz_interval = 0.01*smaller, 0.1* smaller
        siz_interval = [one_siz_interval, one_siz_interval]

        for i in range(10):

            rnd.seed(time.time())   
            #pos = siz = (100,100)
         #   rnd.seed(time.time())
            siz = [randint(*siz_interval[i]) for i in range(2)]

            pos_lf_interval = ((0, w - siz[0]), (0, h - siz[1]))

            pos = [randint(*pos_lf_interval[i]) + siz[i]/2 for i in range(2)]
  #          mass = randint(*mass_interval)
            dens = randrange(*dens_interval)
            mass = siz[0] * siz[1] * dens/1000
            cat = 'obstacle'
            name = cat + str(i)
            info_dict = {
                      #  'name': name,
                        'mass': mass,
                        'category': cat,
                        'collision_type': self.cts[cat]
                    }
            # id is necessary attribut for the kivent svg loader!, also I use it for sharing info about the obstacle
            info_str = json.dumps(info_dict)
            desc = name
            id_str = name
            color = self.color
            stroke_color = self.stroke_color
            rect = self.dwg.rect(id=id_str, insert=pos, size=siz, 
                    fill=color, stroke=stroke_color,
                    description=info_str,
                    )
            if i == 0:
                print(siz, pos, mass)
            print('>>>>>>>>>>>>>>>>>>>>>>>>>>>ww')
#            print(inspect.getfullargspec())
    #        group.add(rect)
        
            self.dwg.add(rect)

        self.root.info('saving: ' + self.dwg.filename)

        self.dwg.save()
        return fname
        

    
