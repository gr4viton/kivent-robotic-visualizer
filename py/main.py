from kivy.app import App
from kivy.logger import Logger
from kivy.uix.widget import Widget
from kivy.clock import Clock
from kivy.config import Config
from kivy.core.window import Window
import kivent_core
import kivent_cymunk
from kivent_core.gameworld import GameWorld
from kivent_core.managers.resource_managers import texture_manager


from kivy.uix.scrollview import ScrollView

#from kivent_maps import map_utils
#from kivent_maps.map_system import MapSystem


from kivent_core.rendering.svg_loader import SVGModelInfo
from kivent_core.systems.renderers import RotateRenderer
from kivent_core.systems.position_systems import PositionSystem2D
from kivent_core.systems.rotate_systems import RotateSystem2D
from kivent_cymunk.interaction import CymunkTouchSystem
from kivy.properties import StringProperty, NumericProperty
from functools import partial
from os.path import dirname, join, abspath

from random import randint, choice
import types

import logging

from logging import info as prinf
from logging import debug as prind
from logging import warning as prinw
from logging import error as prine

#from svgwrite import cm, mm
import inspect

from collections.abc import Mapping
#import shutil

from robot import Robot, Candy

from file_loader import FileLoader
from surface import Map2D
from asteroids import Asteroids

import pprint

def get_asset_path(asset, asset_loc):
    return join(dirname(dirname(abspath(__file__))), asset_loc, asset)

#def _get_args_dict(fn, args, kwargs):
#    args_names = fn.__code__.co_varnames[:fn.__code__.co_argcount]
#    return {**dict(zip(args_names, args)), **kwargs}

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


class ScrollableLabel(ScrollView):
    text = StringProperty('')



class CollisionControl:

    def __init__(self, ultrasound_count):

        self.ultrasound_count = ultrasound_count 

        self.collision_objects = []
        self.add_object_type('wall', 1)
        self.add_object_type('obstacle', 2)
        self.add_object_type('robot', 10)
        self.add_object_type('candy', 42)
      #  self.add_object_type('ultrasound

        self.ultrasound_offset = 100
        us_cts = [self.ultrasound_offset + i for i in range(ultrasound_count)]
        self.add_category('ultrasound_cone', us_cts, False, False)
    
    def get_collision_types(self):
        return {o.name: o.collision_type for o in self.collide_control.collision_objects}

    def add_category(self, object_type, collision_type_list,
            collide=True,
            ultrasound_detectable=True,
            ):
        for ct in collision_type_list:
            self.add_object_type(object_type, ct, collide, ultrasound_detectable)
    
    def add_object_type(self, object_type, collsion_type,
            collide=True,
            ultrasound_detectable=True,
            ):
        col_obj = {
                'object_type': object_type,
                'collision_type': collision_type,
                'collide': collide,
                'ultrasound_detectable': ultrasound_detectable
                }
        self.collision_objects.append(col_obj)

class TestGame(Widget):
    
    def init_collision_types(self):
        self.ultrasound_count = 10

        #self.collide_control = CollideControl(self.ultrasound_count)
        #self.collision_types = self.collide_control.collision_types 
        self.collision_types = {
                'wall': 1,
                'obstacle_rect' : 2,
                'obstacle' : 3,
                'asteroid' : 5,
                'ultrasound_detectable' : 0,
                'ultrasound' : [50 + i for i in range(self.ultrasound_count)],
                'robot' : 10,
                'robot_B' : 11,
                'candy' : 42,
                }

        detected_names = ['wall', 'obstacle', 'obstacle_rect', 'robot_B']
        self.collision_types['ultrasound_detectable'] = list({self.collision_types[name] for name in detected_names}) 
        print('ultrasound_detectable')
        print(self.collision_types['ultrasound_detectable'])
        
        # ignore touch of user
        self.ignore_groups = []
        self.ignore_groups.extend(self.collision_types['ultrasound'])
        #[ self.ignore_groups.append(self.collision_types[key]) for key in ['robot']]
        

    def __init__(self, **kwargs):
        self.init_collision_types()
        super(TestGame, self).__init__(**kwargs)

        self.gameworld.init_gameworld(
            ['cymunk_physics', 'poly_renderer', 'rotate_poly_renderer',
                'rotate_renderer', 
                #'steering_system'
                'rotate', 'position',  'cymunk_touch' ],
            callback=self.init_game)

    def info(self, text):
        self.app.info_text += '\n' + str(text)

    def init_game(self):
        # called automatically? probably
        self.pp = pprint.PrettyPrinter(indent=4)
        self.pprint = self.pp.pprint

        self.field_size = 1000,800

        self.r = None
        self.setup_states()
        self.set_state()
        self.init_loaders()
        print('init_physicals')
        self.init_physicals()
        self.init_space_constraints()

        self.init_properties_updater()

        self.init_control_logic()

    def init_control_logic(self):
        self.init_chase_candy_updater()

    def init_loaders(self):
        self.fl = FileLoader(self)

    def init_physicals(self):
#        self._entities = {}
        self.setup_collision_callbacks()

        self.entities = Entities(self.app)

        self.map = Map2D(self)

        self.asteroids = Asteroids(self)
        self.init_robot()


    def init_robot(self):
        self.r = Robot(self, drive='mecanum')
        
        self.candy = Candy(self)
        #self.fl.load_svg(self.r.path, self.gameworld)

    def toggle_robot_control(self, state):
        self.robot_controlled = state
        if state == True:
            self.r.add_state('INIT')

    def init_chase_candy_updater(self):
        self.r.chase_candy(self.candy)
        self.robot_controlled = False
        Clock.schedule_once(self.chase_candy_update)

    def chase_candy_update(self, dt):
        if self.robot_controlled:
            self.r.goto_target()
        Clock.schedule_once(self.chase_candy_update, .05)

    def draw_asteroids(self):
        self.asteroids.draw_asteroids()

    def setup_collision_callbacks(self):
        cts = self.collision_types

        sm = self.gameworld.system_manager
 #       self.pprint(dir(sm))
 #       systems = self.gameworld.systems

        #self.pprint(sm['cymunk_physics'])
        physics_system = sm['cymunk_physics']
        def rfalse(na,nb):
             return False
        #collide_remove_first
        
        self.begin_ultrasound_callback = {}
        #for us_id in range(self.ultrasound_count):
        for us_id in cts['ultrasound']:
            for ignore in range(1024):
            #for ignore in cts.values():
                if type(ignore) is int: # not list
                  #  if ignore not in cts['ultrasound_detectable']:
                    physics_system.add_collision_handler(ignore, us_id, 
                            begin_func=rfalse,
                            separate_func=rfalse,
                            )
    
            for detectable in cts['ultrasound_detectable']:
                print('us_id', us_id)
                physics_system.add_collision_handler(
                    detectable, us_id,
                   # pre_solve_func=self.return_begin_ultrasound_callback(us_id, True),
                    begin_func=self.return_begin_ultrasound_callback(us_id, True),
                    separate_func=self.return_begin_ultrasound_callback(us_id, False))


    def return_begin_ultrasound_callback(self, us_id, state):
        # this adds the segmentation fault on exit - but currently I am not able to simulate ultrasounds any other way than 
        # returning 
        def begin_ultrasound_callback(self, space, arbiter):
            #ent0_id = arbiter.shapes[0].body.data #detectable_object
            #ent1_id = arbiter.shapes[1].body.data #robot
            space.enable_contact_graph = True
            #print(space.bodies)

            ent0 = arbiter.shapes[0]
            e_id = ent0.body.data
            #a = ent0.body
            #print(len(arbiter.shapes))
            con = arbiter.contacts
            #print(a)
            #print(dir(a))
            #print(a.contact)

            if con is not None:
                self.r.ultrasound_detection(us_id, ent0, state)
                ent = self.gameworld.entities[e_id]
                cat = [cat for cat, id_list in self.entities.items() if e_id in id_list]
                print('detect', cat, e_id)
            return False

        ind = 2*us_id + int(state) 
        self.begin_ultrasound_callback[ind] = types.MethodType(begin_ultrasound_callback, self)
        return self.begin_ultrasound_callback[ind]
        #return begin_ultrasound_callback

    def add_entity(self, ent, category):
        # add to entity counter
        print('added entity', category)
        if category not in self.entities.keys():
            self.entities[category] = []
        self.entities.add_item(category, ent)
    


    def set_robot_mid(self):
        rob_ent = self.r.ent
        rob_body = self.gameworld.entities[rob_ent].cymunk_physics.body
        rob_body.position = (100,100)

    def kick_robot(self):
        rob_ent = self.r.ent
        print(rob_ent)
        p = self.gameworld.system_manager['cymunk_physics']
        #self.pprint(dir(p))
        
        rob_body = self.gameworld.entities[rob_ent].cymunk_physics.body
        #rob_body = rob_ent.cymunk_physics.body
        print(dir(rob_body))

        im = (10000, 10000)
        seq = [-1, 1]
        imp = (choice(seq) * randint(*im), choice(seq) * randint(*im))
        rob_body.apply_impulse(imp)
        print('impulse', imp)
        
        #p.querry_segment((x,y),(x,y))
        #if len(hits) > 0:
        #    ent = entities[hits[0][0]]
        #    ent.color.r = 0
        #    self.app.selected_id = ent.entity_id
        #    gameview.entity_to_focus = ent.entity_id
        #    gameview.focus_entity = True
        #else:
        #    self.app.selected = None
        #    gameview.focus_entity = False

    def init_space_constraints(self):
        return 
        p = self.gameworld.system_manager['cymunk_physics']
        #self.pprint(dir(p))
        
        space = p.space
        #self.pprint(dir(space))

        rob_ent = self.r.ent
        rob = self.gameworld.entities[rob_ent]
        rob_body = self.gameworld.entities[rob_ent].cymunk_physics.body
        rob_renderer = rob.rotate_poly_renderer
        #print('rob_body')
        #self.pprint(dir(rob_body))
        #print('rob_renderer')
        #self.pprint(dir(rob_renderer))
        for us_ent in self.r.ultrasounds.keys():
            us = self.gameworld.entities[us_ent]
            usb = us.cymunk_physics.body
            kwargs = {#'rest_length': 10,
			'stiffness': 10,
		        'damping': 0.1}
            b1 = rob_body
            b2 = usb
            joint_type = 'DampedSpring'
            cymunk = kivent_cymunk.physics.cymunk
            print(dir(cymunk))
         #   print(cymunk.DampedSpring.__init__.__code__.co_varnames)

            an1 = (0,0)
            an4 = (10, -10)
            an5 = (10, 10)
            an2 = (100,-100)
            an3 = (100,100)
            
            

            #self.pprint(dir(rob_body))
            h = rob_renderer.height/2
            rob_att = (0, h)



            anchor_pairs = ((an1, an1), (an2, an4), (an2, an5))
            anchor_pairs = ((an1, an1), (an1, an2), (an1, an3))
            
            A = ((100, 0), (10, 100))
            B = ((-100, 0), (-10, 100))
            C = ((0, -100), (0, 100))
            
            anchor_pairs = (A,B,C)

            A = ((-20, 0), (-10, 0))
            B = ((20, 0), (10, 0))
            C = ((0, -20), (0, -10))
            anchor_pairs = (A,B)
            for anchor_pair in anchor_pairs:
                anch1, anch2 = anchor_pair
                con = cymunk.PinJoint(b1, b2, anch1, anch2)
                space.add_constraint(con)
            
            break
            #anchor_pair = 
                #con = cymunk.DampedSpring(b1, b2, anch1, anch2, joint_type, **kwargs)           

#    @property
 #   def entities(self):
  #      return self._entities

   # @entities.setter
    #def entities(self, value):
     #   self.app.ent_count = '\n'.join(['{}={}'.format(key, len(val)) for key, val in self.entities.items()])
      #  self._entities = value

    def init_entity(self, component_dict, component_order, category='default_category', object_info=None):
        if object_info is not None:
            category = object_info.get('category', category)
        else:
            object_info = {}

        ent = self.gameworld.init_entity(component_dict, component_order)
        
        # add to counter
        self.add_entity(ent, category)

        object_info.update({'ent': ent})
        entity_info = object_info

        #print('@'*42)
        #self.pprint(entity_info)
        #print(Robot.cats, category in Robot.cats)

        # add to specific subobjects
        #if self.r is not None:
         #   self.r.add_entity(entity_info)
          #      if category == 'robot':
           #         print('added robot')
            
        return ent


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

   # def draw_some_stuff(self):
     #   self.load_svg('objects.svg', self.gameworld)
        #self.load_svg('map.svg', self.gameworld)
    #    self.map.draw_stuff()
 #       self.load_svg('map.svg', self.gameworld)

    def draw_obstacles(self):
        self.map.draw_obstacles()

    def draw_rect_obstacles(self):
        self.map.draw_rect_obstacles()

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


    def init_properties_updater(self):
        Clock.schedule_once(self.update_properties)

    def update_properties(self, dt):
        self.app.ultrasound_status = self.r.ultrasound_status()
        self.app.robot_states = str(self.r.states)
     #   self.r.reset_ultrasounds()
        Clock.schedule_once(self.update_properties, .05)

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
    ultrasound_status = StringProperty('...')
    robot_states = StringProperty('...')

    info_text = StringProperty('...')
    damping = NumericProperty(0.2)
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
        self.root.map.clear_maps()


if __name__ == '__main__':
    DalekApp().run()
