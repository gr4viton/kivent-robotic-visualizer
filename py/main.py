from kivy.app import App
from kivy.logger import Logger
from kivy.uix.widget import Widget
from kivy.clock import Clock
from kivy.config import Config
from kivy.core.window import Window
import random as rnd
from random import randint, choice, randrange
from math import radians, pi, sin, cos
import kivent_core
import kivent_cymunk
from kivent_core.gameworld import GameWorld
from kivent_core.managers.resource_managers import texture_manager


from kivent_maps import map_utils
from kivent_maps.map_system import MapSystem


from kivent_core.rendering.svg_loader import SVGModelInfo
from kivent_core.systems.renderers import RotateRenderer
from kivent_core.systems.position_systems import PositionSystem2D
from kivent_core.systems.rotate_systems import RotateSystem2D
from kivent_cymunk.interaction import CymunkTouchSystem
from kivy.properties import StringProperty, NumericProperty
from functools import partial
from os.path import dirname, join, abspath

import logging

from logging import info as prinf
from logging import debug as prind
from logging import warning as prinw
from logging import error as prine

import svgwrite as svg
from svgwrite import cm, mm
import json
import inspect

from collections.abc import Mapping
import time
import os
#import shutil
import glob

from robot import Robot

def get_asset_path(asset, asset_loc):
    return join(dirname(dirname(abspath(__file__))), asset_loc, asset)

def _get_args_dict(fn, args, kwargs):
    args_names = fn.__code__.co_varnames[:fn.__code__.co_argcount]
    return {**dict(zip(args_names, args)), **kwargs}

texture_manager.load_atlas(get_asset_path('background_objects.atlas','assets'))
#texture_manager.load_atlas(get_asset_path('dalek_objects.atlas','assets'))
#texture_manager.load_atlas(join(atlas_dir, 'robot_objects.atlas'))

print(join(dirname(dirname(abspath(__file__))), 'assets', 'glsl'))



class Entities(Mapping):
    def __init__(self, app, *args, **kw):
        self._storage = dict(*args, **kw)
     #   self.ent_count = ent_count
        self.app = app
    
    def __getitem__(self, key):
        self.update_count()
        return self._storage[key]

    def __iter__(self):
        self.update_count()
        return iter(self._storage)

    def __len__(self):
        return len(self._storage)

 #   def __delitem__(self, key):
  #      return self._storage.__delitem__(self, key)

    def add_item(self, key, value):
        ret = self._storage[key].append(value)
        self.update_count()
        return ret 

    def __setitem__(self, key, value):
        ret = self._storage.__setitem__(key, value)
        self.update_count()
        return ret

    def update_count(self):
        self.app.ent_count = '\n'.join(['{}={}'.format(key, len(val)) for key, val in self._storage.items()])

    def __str__(self):
        self.update_count()
        return self._storage.__str__()


class TestGame(Widget):
    def __init__(self, **kwargs):
        super(TestGame, self).__init__(**kwargs)

        self.gameworld.init_gameworld(
            ['cymunk_physics', 'poly_renderer', 'rotate_poly_renderer', 
                'rotate_renderer', 
                'rotate', 'position',  'cymunk_touch' ],
            callback=self.init_game)

    def init_game(self):

        self.setup_states()
        self.set_state()
        self.init_physicals()

    def info(self, text):
        self.app.info_text += '\n' + str(text)


    def clear_maps(self):
        prinf('Deleting maps in '+ self.__svg_map_dir__)
 #       shutil.rmtree(self.__svg_map_dir__)
        files = glob.glob(self.__svg_map_dir__ + '*')
        for f in files:
            os.remove(f)

    def init_physicals(self):
#        self._entities = {}
        self.entities = Entities(self.app)

        self.__svg_map_dir__ = '../assets/maps/svg/'
        self.clear_maps()

        self.draw_walls()
        #self.draw_some_stuff()
        self.draw_obstacles()

        self.init_robot()

    def init_robot(self):

#        self.r = Robot(pos, siz, drive='mecanum')

        self.create_robot()

#        fname = self.create_robot()
 #       self.load_svg(fname, self.gameworld)

    def create_robot(self):

        
        pass



    def draw_walls(self):
        Ww, Wh = Wsize = Window.size
        prinw(Wsize)
        self.info(Wsize)
        
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

        
    def add_entity(self, ent, category='default'):

        if category not in self.entities.keys():
            self.entities[category] = []
 #       self.entities[category].append(ent)
        self.entities.add_item(category, ent)
    
#    @property
 #   def entities(self):
  #      return self._entities

   # @entities.setter
    #def entities(self, value):
     #   self.app.ent_count = '\n'.join(['{}={}'.format(key, len(val)) for key, val in self.entities.items()])
      #  self._entities = value

    def init_entity(self, component_dict, component_order, category):
        ent = self.gameworld.init_entity(component_dict, component_order)
        self.add_entity(ent, category)
        return ent


    def create_wall(self, pos_lf, size, txu): 
        w, h = size

        pos = [pos_lf[i] + size[i]/2 for i in range(2)]
        model_key = 'wall' + str(self.wall_id)
        self.gameworld.model_manager.load_textured_rectangle('vertex_format_4f', w, h, txu, model_key)
        mass = 0

        shape_dict = {'width': w, 'height': h, 'mass': mass, }
        col_shape = {
                'shape_type': 'box', 
                'elasticity': 1.0,
                'collision_type': 0, 
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
        return self.init_entity(create_component_dict, component_order, 'walls')

    def destroy_all_entities(self):
        self.destroy_entities()

    def destroy_entities(self, cat_list=None, skip_cat_list=None):
        for ent_cat, ent_list in self.entities.items():
            delete = False
            if cat_list is None and skip_cat_list is None:
                delete = True
            else:
                if cat_list is None:
                    if ent_cat not in skip_cat_list:
                        delete = True
                else:
                    if ent_cat in cat_list:
                        delete = True
                
            if delete:
                prinf('Clearing entities of ' + ent_cat)
                for ent in ent_list:
                    self.destroy_created_entity(ent, 0)
                self.entities[ent_cat].clear()



    def destroy_created_entity(self, ent_id, dt):
        self.gameworld.remove_entity(ent_id)

    def draw_obstacles(self):
        fname = self.create_obstacles()
        self.load_svg(fname, self.gameworld)


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

            name = 'obstacle' + str(i)
            info_dict = {
                      #  'name': name,
                        'mass': mass,
                        'category': 'obstacle'
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
                print(siz, pos)
            print('>>>>>>>>>>>>>>>>>>>>>>>>>>>ww')
#            print(inspect.getfullargspec())
    #        group.add(rect)
        
            self.dwg.add(rect)

        self.info('saving: ' + self.dwg.filename)

        self.dwg.save()
        return fname
        

    def draw_asteroids(self):
        size = Window.size
        w, h = size[0], size[1]
        delete_time = 2.5
        create_asteroid = self.create_asteroid
        destroy_ent = self.destroy_created_entity
        for x in range(100):
            pos = (randint(0, w), randint(0, h))
            ent_id = create_asteroid(pos)
            Clock.schedule_once(partial(destroy_ent, ent_id), delete_time)
 #       self.app.ent_count += 100

    def draw_some_stuff(self):
       # rnd.seed(time.time())
     #   self.load_svg('objects.svg', self.gameworld)
        #self.load_svg('map.svg', self.gameworld)
        self.draw_obstacles()
 #       self.load_svg('map.svg', self.gameworld)


    def create_asteroid(self, pos):
        x_vel = randint(-15, 15)
        y_vel = randint(-15, 15)
        angle = radians(randint(-360, 360))
        angular_velocity = radians(randint(-1500, -1500))
        shape_dict = {
            'inner_radius': 0, 'outer_radius': 20,
            'mass': 50-40, 'offset': (0, 0)
            }
        col_shape = {
            'shape_type': 'circle', 'elasticity': 1.0,
            'collision_type': 3, 'shape_info': shape_dict, 'friction': 1.0
            }
        col_shapes = [col_shape]
        physics_component = {'main_shape': 'circle',
                            'velocity': (x_vel, y_vel),
                            'position': pos, 'angle': angle,
                            'angular_velocity': angular_velocity,
                            'vel_limit': 250,
                            'ang_vel_limit': radians(11200),
                            'mass': 50-40, 'col_shapes': col_shapes}

        create_component_dict = {
            'cymunk_physics': physics_component,
            'rotate_renderer': {
                'texture': 'asteroid1',
                'size': (45, 45),
                'render': True
                },
            'position': pos,
            'rotate': 0, }

        component_order = ['position', 'rotate', 'rotate_renderer',
            'cymunk_physics',]


        return self.init_entity(create_component_dict, component_order, 'asteroid')


    def normalize_info(self, info):
        def _median(li):
            li = sorted(li)
            lenli = len(li)
            if lenli % 2: 
                return li[lenli//2]
            else:
                return (li[lenli//2 - 1] + li[lenli//2])/2.0

        #first - calculate (very roughly middle of the object), median
        xmid = _median([ x['pos'][0] for x in info.vertices.values()])
        ymid = _median([ x['pos'][1] for x in info.vertices.values()])

        if info.element_id is None:
            element_id = 'added_default_element_id'
        else:
            element_id = info.element_id

        element_id += str(time.time())

        ret = SVGModelInfo(info.indices,
                       info.vertices.copy(),
                       custom_data=info.custom_data,
                       description=info.description,
                       element_id=element_id,
                       title=info.title,
                       path_vertices=info.path_vertices[:]
                       )

        #now substract it from vertices
        for k in ret.vertices:
            v = ret.vertices[k].copy()
            x, y = v['pos']
            v['pos'] = (x - xmid, y - ymid)
            ret.vertices[k] = v

        #and path vertices
        for i, (x, y) in enumerate(ret.path_vertices):
            ret.path_vertices[i] = (x - xmid, y - ymid)
        
        return ret, (xmid, ymid)


    def load_svg(self, fname, gameworld, massless=False):
        mm = gameworld.model_manager
        data = mm.get_model_info_for_svg(fname)

        print('loading svg:', fname)
        mass = 50 
        category = fname

        for info in data['model_info']:
            info, pos = self.normalize_info(info)

            if info.description is not None:
                info_dict = json.loads(info.description)
                #print(info_dict)a
                mass = float(info_dict.get('mass', mass))
                category = info_dict.get('category', category)

            if massless:
                mass = float('inf')
                mass = float(0)
                #av = float('inf')

            Logger.debug("adding object with title/element_id=%s/%s and desc=%s",
                         info.title, info.element_id, info.description)
            

            this_model_name = data['svg_name'] 
            model_name = mm.load_model_from_model_info(info, this_model_name)

            poly_shape = {
                'shape_type': 'poly',
                'elasticity': 0.6,
                'collision_type': 0,
                'friction': 1.0,
                'shape_info': {
                    'mass': mass,
                    'offset': (0, 0),
                    'vertices': info.path_vertices
                }

            }
           
            physics = {
                    'main_shape': 'poly',
                    'velocity': (0, 0),
                    'position': pos,
                    'angle': 0,
                    'angular_velocity': radians(0),
                    'ang_vel_limit': radians(0),
                    'mass': mass, 
                    'col_shapes': [poly_shape]
            }

            create_dict = {
                    'position': pos,
                    'rotate_poly_renderer': {'model_key': model_name},
                    'cymunk_physics': physics, 
                    'rotate': radians(0),
            }

            #ent = gameworld.init_entity(create_dict, ['position', 'rotate', 'poly_renderer', 'cymunk_physics'])
            component_order = ['position', 'rotate', 'rotate_poly_renderer', 'cymunk_physics']
            self.init_entity(create_dict, component_order, category)

#        mm.unload_models_for_svg(data['svg_name'])   

    def update(self, dt):
        self.gameworld.update(dt)

    def setup_states(self):
        self.gameworld.add_state(state_name='main', 
            systems_added=['poly_renderer'],
            systems_removed=[], systems_paused=[],
            systems_unpaused=['poly_renderer'],
            screenmanager_screen='main')

    def set_state(self):
        self.gameworld.state = 'main'


class DebugPanel(Widget):
    fps = StringProperty(None)

    def __init__(self, **kwargs):
        super(DebugPanel, self).__init__(**kwargs)
        Clock.schedule_once(self.update_fps)

    def update_fps(self,dt):
        self.fps = str(int(Clock.get_fps()))
        Clock.schedule_once(self.update_fps, .05)

class DalekApp(App):
    ent_count = StringProperty('...')
    info_text = StringProperty('...')
    damping = NumericProperty(0.5)
    #def __init__(self, **kwargs):
     #   super(App, self).__init__(**kwargs)
      #  return 
    def build(self):
        # root.bind(size=self._update_rect, pos=self._update_rect)
        h = 700
        w = 1300
        #Config.set('kivy', 'show_fps', 1)
        #Config.set('kivy', 'desktop', 1)

        Config.set('graphics', 'window_state', 'maximized')
        Config.set('graphics', 'position', 'custom')
        Config.set('graphics', 'height', h)
        Config.set('graphics', 'width', w)
        Config.set('graphics', 'top', 15)
        Config.set('graphics', 'left', 4)
        #Config.set('graphics',
        #Config.set('graphics', 'multisamples', 0) # to correct bug from kivy 1.9.1 - https://github.com/kivy/kivy/issues/3576

        # Config.set('graphics', 'fullscreen', 'fake')
        # Config.set('graphics', 'fullscreen', 1)
        Window.clearcolor = (1,1,1,1)
        self.root = TestGame()
        return self.root

    def on_stop(self):
        self.root.clear_maps()


if __name__ == '__main__':
    DalekApp().run()
