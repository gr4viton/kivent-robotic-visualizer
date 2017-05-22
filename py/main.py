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

#from svgwrite import cm, mm
import inspect

from collections.abc import Mapping
#import shutil

from robot import Robot

from file_loader import FileLoader
from surface import Map2D
from asteroids import Asteroids

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

    def info(self, text):
        self.app.info_text += '\n' + str(text)

    def init_game(self):

        self.setup_states()
        self.set_state()
        self.init_loaders()
        self.init_physicals()

    def init_loaders(self):
        self.fl = FileLoader(self)

    def init_physicals(self):
#        self._entities = {}
        self.entities = Entities(self.app)
        
        self.map = Map2D(self)

        self.asteroids = Asteroids(self)
        self.init_robot()

    def init_robot(self):

        self.r = Robot(self, drive='mecanum')

        self.fl.load_svg(self.r.path, self.gameworld)

    def draw_asteroids(self):
        self.asteroids.draw_asteroids()

    def create_robot(self):

        
        pass



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

    def draw_some_stuff(self):
     #   self.load_svg('objects.svg', self.gameworld)
        #self.load_svg('map.svg', self.gameworld)
        self.map.draw_stuff() 
 #       self.load_svg('map.svg', self.gameworld)


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
        self.root.map.clear_maps()


if __name__ == '__main__':
    DalekApp().run()
