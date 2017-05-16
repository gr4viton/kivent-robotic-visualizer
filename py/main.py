from kivy.app import App
from kivy.logger import Logger
from kivy.uix.widget import Widget
from kivy.clock import Clock
from kivy.core.window import Window
from random import randint, choice
from math import radians, pi, sin, cos
import kivent_core
import kivent_cymunk
from kivent_core.gameworld import GameWorld
from kivent_core.managers.resource_managers import texture_manager

from kivent_core.rendering.svg_loader import SVGModelInfo
from kivent_core.systems.renderers import RotateRenderer
from kivent_core.systems.position_systems import PositionSystem2D
from kivent_core.systems.rotate_systems import RotateSystem2D
from kivent_cymunk.interaction import CymunkTouchSystem
from kivy.properties import StringProperty, NumericProperty
from functools import partial
from os.path import dirname, join, abspath


texture_manager.load_atlas(
        join(dirname(dirname(abspath(__file__))), 'assets', 
        'background_objects.atlas'))


print(join(dirname(dirname(abspath(__file__))), 'assets', 'glsl'))


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
        self.draw_some_stuff()

    def destroy_created_entity(self, ent_id, dt):
        self.gameworld.remove_entity(ent_id)
        self.app.count -= 1


    def draw_some_stuff(self):
        size = Window.size
        w, h = size[0], size[1]
        delete_time = 2.5
        create_asteroid = self.create_asteroid
        destroy_ent = self.destroy_created_entity
        for x in range(100):
            pos = (randint(0, w), randint(0, h))
            ent_id = create_asteroid(pos)
            #Clock.schedule_once(partial(destroy_ent, ent_id), delete_time)
        self.app.count += 100

        self.load_svg('objects.svg', self.gameworld)

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
        return self.gameworld.init_entity(
            create_component_dict, component_order)


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

        ret = SVGModelInfo(info.indices,
                       info.vertices.copy(),
                       custom_data=info.custom_data,
                       description=info.description,
                       element_id=info.element_id,
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


    def load_svg(self, fname, gameworld):
        mm = gameworld.model_manager
        data = mm.get_model_info_for_svg(fname)
        print('fname', fname)
        print('data', data)
        

        for info in data['model_info']:
            
            pos = (randint(0, 200), randint(0, 200))
            info, pos = self.normalize_info(info)

            Logger.debug("adding object with title/element_id=%s/%s and desc=%s",
                         info.title, info.element_id, info.description)
            model_name = mm.load_model_from_model_info(info, data['svg_name'])

            poly_shape = {
                'shape_type': 'poly',
                'elasticity': 0.6,
                'collision_type': 1,
                'friction': 1.0,
                'shape_info': {
                    'mass': 50,
                    'offset': (0, 0),
                    'vertices': info.path_vertices
                }

            }
           
            physics = {
                    'main_shape': 'poly',
                    'velocity': (0, 0),
                    'position': pos,
                    'angle': 0,
                    'angular_velocity': radians(100),
                    'ang_vel_limit': radians(0),
                    'mass': 50, 
                    'col_shapes': [poly_shape]
            }

            create_dict = {
                    'position': pos,
                    'rotate_poly_renderer': {'model_key': model_name},
                    'cymunk_physics': physics, 
                    'rotate': radians(0),
            }

            #ent = gameworld.init_entity(create_dict, ['position', 'rotate', 'poly_renderer', 'cymunk_physics'])

            ent = gameworld.init_entity(create_dict, ['position', 'rotate',
                'rotate_poly_renderer', 'cymunk_physics'])
            self.app.count += 1

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
    count = NumericProperty(0)


if __name__ == '__main__':
    DalekApp().run()
