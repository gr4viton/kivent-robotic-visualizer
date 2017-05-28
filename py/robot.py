
import logging

from logging import info as prinf
from logging import debug as prind
from logging import warning as prinw
from logging import error as prine

import time

from cymunk import Vec2d
#from cymunk import cpBodyLocal2World in body.
#import cymunk
#print(dir(cymunk))

import random as rnd
from random import randint, choice, randrange
from math import radians, pi, sin, cos, sqrt, degrees
import svgwrite as svg
import glob

import json

import os

svg.profile = 'tiny'


class Candy:

    def __init__(self, root):
        self.root = root
        w, h = self.root.field_size
        pos = [float(randint(0, s)) for s in [w, h]]
        print('>>>', pos)
        self.siz = (42., 42.)

        #self.ent = self.create_candy(pos)
        #self.create_asteroid(pos)
        self.create_candy(pos)
        self.body = self.root.gameworld.entities[self.ent].cymunk_physics.body

    def create_candy(self, pos):
        vel = (0., 0.) #randint(-15, 15)
        angle = radians(randint(-360, 360))
        angular_velocity = radians(randint(-1500, -1500))

        cts = self.root.collision_types
        siz = self.siz

        mass = 10.
        shape_dict = {
            'inner_radius': 0, 'outer_radius': 20,
            'mass': mass, 'offset': (0, 0)
            }
        col_shape = {
            'shape_type': 'circle', 'elasticity': 1.0,
            'collision_type': cts['candy'], 'shape_info': shape_dict, 'friction': 1.0
            }

        col_shapes = [col_shape]

        physics_component = {'main_shape': 'circle',
                            'velocity': vel,
                            'position': pos, 'angle': angle,
                            'angular_velocity': angular_velocity,
                            'vel_limit': 250,
                            'ang_vel_limit': radians(11200),
                            'mass': mass, 'col_shapes': col_shapes
                            }

        component_dict = {
            'cymunk_physics': physics_component,
            'rotate_renderer': {
                'texture': 'candy',
                'size': siz,
                'render': True
                },
            'position': pos,
            'rotate': 0, }

        component_order = ['position', 'rotate', 'rotate_renderer',
            'cymunk_physics',]

        cat = 'candy'

        self.ent = self.root.gameworld.init_entity(component_dict, component_order)
        #return self.root.init_entity(create_component_dict, component_order, cat)


class UltrasoundSensor:

    def __init__(self, us_id, name, open_angle=None, distance_range=None, category='ultrasound', mass=None):
        self.name = name
        self.open_angle = open_angle
        self.distance_range = distance_range
        self.detected = False
        prinf('UltrasoundSensor created and entangled: %s %s', us_id, name)


class RobotMecanumControl:

    def __init__(self, root, robot):
        self.root = root
        self.r = robot
        
        self.ang_vel_max = radians(30)

        self.wheel_vectors = []
        w, h = self.r.siz


        #wheel = [position_of_wheel, vector_when_moving_wheel_in_frontal_direction 
        self.wheels = [
                [Vec2d(-w, +h), Vec2d(+1, +1)], # lf
                [Vec2d(+w, +h), Vec2d(-1, +1)], # rf
                [Vec2d(-w, -h), Vec2d(-1, +1)], # lb
                [Vec2d(+w, -h), Vec2d(+1, +1)], # rb
            ]

    def set_ang_vel(self, ang_vel):
        ang_vel = self.ang_vel_max if ang_vel > self.ang_vel_max else ang_vel

        self.r.body.torque(ang_vel)


    def calc_wheel_speed(self, vel_vec, ang_vel):
        """Simple mecanum wheel control algorithm
        
        http://thinktank.wpi.edu/resources/346/ControllingMecanumDrive.pdf
        """

        vd = vel_vec.length
        th = vel_vec.angle
        dth = ang_vel 
        
        th45 = th + radians(45)
        wheel_speeds = [
                vd * sin(th45) + dth,
                vd * cos(th45) - dth,
                vd * cos(th45) + dth,
                vd * sin(th45) - dth,
            ]

        return wheel_speeds

    def apply_wheel_speed(self, wheel_speeds):
        """wheel_speeds in range 0 - 1
        
        lf, rf, lb, rb
        """
        # rotate ccw
        #wheel_speeds = [+1, +1, +1,+ 1] # go straight
        #wheel_speeds = [+1, +0, +0, +1] # go front left 
        #wheel_speeds = [+0, -1, -1, 0] # go back left 
        #wheel_speeds = [+1, -1, -1, +1] # strafe left
        wheel_speeds = [+1, -1, +1, -1] # rotate CW

        imp_value = 1000 # strength of actuators

        #print(self.wheels)
        b = self.r.body
        ori = b.angle
        for v, wheel_speed in zip(self.wheels, wheel_speeds):
            wheel_pos, wheel_force_dir = v
            imp_vec = wheel_force_dir * imp_value * wheel_speed
            
            loc_wheel_pos = Vec2d(wheel_pos)
            loc_imp_vec = Vec2d(imp_vec)
            [v.rotate(ori) for v in [loc_wheel_pos, loc_imp_vec]]
            print('wheel_pos')
            print(loc_wheel_pos, wheel_pos)
            b.apply_impulse(loc_imp_vec, loc_wheel_pos)
        

    def go(self, vel_vec, ang_vel):
        ori = self.r.body.angle
        
        imp_value = 1000
        imp_vec = vel_vec * imp_value
        imp_vec.rotate(ori + radians(90))

        imp_rot = ang_vel
       # self.r.body.apply_impulse(imp_vec, imp_rot)

        wheel_speeds = self.calc_wheel_speed(vel_vec, ang_vel)
        self.apply_wheel_speed(wheel_speeds)

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

        self.entity = self.root.gameworld.entities[self.ent]
        self.body = self.entity.cymunk_physics.body

        if drive == 'mecanum':
            self.control = RobotMecanumControl(self.root, self)


    def chase_candy(self, candy):
        self.candy = candy
        
        self.t_body = self.candy.body

    def camera_get_target(self):
        """Returns relative position and orientation of target

        possibly with simulated error
        """
       # pos = self.body.position
       # t_pos = self.t_body.position
       # t_dir = [t_xy - xy for xy, t_xy in zip(pos, t_pos)]

        global_vec = self.t_body.position - self.body.position 
        
        ori = self.body.angle
        rel_vec = global_vec
        rel_vec.rotate(-ori - radians(90))
        #print(degrees(rel_vec.angle))
        return rel_vec

    def goto_target(self):
        imp = (100,100)
         
        rel_vec = self.camera_get_target()
        
        #print(dir(self.body))
        #print(dir(self.body.position))
        max_angle_dif = radians(10)

        n_rel_vec = rel_vec.normalized()
        ang_vel = 0
        if abs(rel_vec.angle) > max_angle_dif:
            ang_vel = -rel_vec.angle
            vel_vec = n_rel_vec * 0.8 
        else:
            vel_vec = n_rel_vec

        self.control.go(vel_vec, ang_vel)
            



    def create_ultrasound(self, name, color, stroke_color, vert_list):
        cat = 'ultrasound'
        info_dict = {
                'collision_type': self.cts[cat],
                'object_info': {
                    'name': str(name),
                    'category': cat,
                    'mass': 0,
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
            self.ultrasounds[entity_info['us_id']] = us
            print(entity_info['us_id'])
        #elif category in 'robot':
            #self.ent = entity_info['ent']

        #self.entities[category].append(ent)

 #   @property
  #  def ultrasounds(self):

   #    return self.Ultrasounds

    def ultrasound_hit(self, ultrasound_id, object_ent_id):
        return self.ultrasound_detection(ultrasound_id, object_ent_id, True)

    def ultrasound_miss(self, ultrasound_id, object_id):
        return self.ultrasound_detection(ultrasound_id, object_ent_id, False)

    def ultrasound_detection(self, ultrasound_id, object_ent_id, state):
        us = self.ultrasounds[ultrasound_id]
        us.detected = state
        return us.name
    
    def ultrasound_status(self):
        return '|'.join(['{}={}'.format(us.name, us.detected) for us in self.ultrasounds.values()])

    def create_robot(self):
  #      self.color = '#FF0000'
 #       self.stroke_color = '#000000'
#        self.path = self.__svg_dir__ + 'robot.svg'

        w, h = self.root.field_size
        
        pos = (randint(0, w), randint(0, h))
        self.siz = [40, 60]
        self.mass = 100
        self.create_robot_rect('dalek', self.mass, pos, self.siz)
        
    def create_robot_rect(self, name, mass, pos, siz):
        id_str = self.robot_name
        insert_pos = [pos[i] + siz[i]/2 for i in range(2)]
        #self.pos = insert_pos
        self.pos = pos
        cat = 'robot'
        robot_name = name
        
        cts = self.root.collision_types

        width, height = siz
        w, h = siz
        robot_verts = [
                     (-width/2., -height/2.),
                     (-width/2., height/2.),
                     (width/2., height/2.),
                     (width/2., -height/2.),
                    ]

        robot_shape = {
                'shape_type': 'poly',
                'elasticity': 0.6,
                'collision_type': cts['robot'],
                'friction': 1.0,
                'shape_info': {
                    'mass': mass,
                    'offset': (0, 0),
                    'vertices': robot_verts
                }
            }

        col_shapes = [robot_shape]

        open_angle = radians(45)
        count_ultrasounds = 3
        names = ['right', 'middle', 'left' ]
        ultrasound_range = 100
        ultrasound_ranges = [ultrasound_range, ultrasound_range + 100]
        x0, y0 = self.pos[0] + 0, self.pos[1] + h/4
        x0, y0 = 0, h/2 

        us_color = (0, 255, 0)
        self.max_us_range = 250
        self.max_us_opacity = 200
        us_models = []
        for i in range(count_ultrasounds):
            # to center it
            shift_angle = count_ultrasounds / 2 * open_angle # + radians(180)
            # cone edges
            edge_angles = (i * open_angle - shift_angle,
                     (1 + i) * open_angle - shift_angle)

            edge_points = [[
                ultrasound_range * sin(edge_angle) + x0,
                ultrasound_range * cos(edge_angle) + y0
                ] for edge_angle in edge_angles]

            vert_list = [(x0, y0), edge_points[0], edge_points[1]]
            
            mass = 0
            us_id = cts['ultrasound'][i]

            us_shape = {
                    'shape_type': 'poly',
                    'elasticity': 0.6,
                    'collision_type': us_id,
                    'friction': 1.0,
                    'shape_info': {
                        'mass': mass,
                        'offset': (0, 0),
                        'vertices': vert_list
                    }
                }
            col_shapes.append(us_shape)

            entity_info = {
                'category': 'ultrasound',
                'us_id': us_id,
                'name': names[i]
            }
            
            us_color = (randint(100,200), 255*randint(8,10)/10, randint(100,100))
            us_model = self.get_triangle_data(vert_list, us_color, ultrasound_ranges)
            us_models.append(us_model)

            self.add_entity(entity_info)
        
        mass = 200
        physics = {
                'main_shape': 'poly',
                'velocity': (0, 0),
                'position': self.pos,
                'angle': 0,
                'angular_velocity': radians(0),
                'ang_vel_limit': radians(0),
                'mass': mass,
                'col_shapes': col_shapes
        }


        model_name = robot_name
        model_manager = self.root.gameworld.model_manager

        rect_data = self.get_rectangle_data(h, w)
        rect_data2 = self.get_rectangle_data(w,w)

        
        rects = [rect_data, rect_data2]
        rects.extend(us_models)
        model_data = self.join_vert_models(rects)
        
        
        rectangle_model = model_manager.load_model(
                                            'vertex_format_2f4ub',
                                            model_data['vertex_count'],
                                            model_data['index_count'],
                                            model_name,
                                            indices=model_data['indices'],
                                            vertices=model_data['vertices']
                                            )

        #self.root.pprint(dir(model_manager))
        robot_model = rectangle_model
        #self.shapes['rectangle_model'] = rectangle_model

        component_dict = {
                'position': pos,
                'rotate_poly_renderer': {
                    'model_key': rectangle_model
                    },
                    'cymunk_physics': physics,
                    'rotate': radians(0),
            }

        
        cat = 'robot'
        info_dict = {
                'mass': mass,
                'object_info': {
                    'name': name,
                    'category': cat,
                },
            }
        info_str = json.dumps(info_dict)
        
        object_info = info_dict['object_info']
        
        print('robot component creation')
        component_order = ['position', 'rotate', 'rotate_poly_renderer', 'cymunk_physics']
        #self.root.init_entity(component_dict, component_order, object_info=object_info)
    
        self.ent = self.root.gameworld.init_entity(component_dict, component_order)
        print('>>>>>>', self.ent)
    def join_vert_models(self, model_list):
        #self.root.pprint(model_list)
        
        vertices = None
        indices = None
        prev_vert_count = 0
        for d in model_list:
            if indices is None:
                indices = list(d['indices'])
                vertices = dict(d['vertices'])
            else:
                this_indices_incremented = [ind + prev_vert_count for ind in d['indices']] 
                indices.extend(this_indices_incremented)
                this_vertices_incremented = {(k + prev_vert_count) : v for k, v in d['vertices'].items()}

                # did not work
                # vertices.update(this_indices_incremented)
                for k, v in this_vertices_incremented.items():
                    vertices[k] = v

            prev_vert_count += d['vertex_count']

        joined = { 
                'vertex_count': sum([d['vertex_count'] for d in model_list]),
                'index_count': sum([d['index_count'] for d in model_list]),
                'indices': indices,
                'vertices': vertices
                }
        #self.root.pprint(joined)
        return joined
        
        

    @staticmethod
    def get_rectangle_data(height, width):
        return {
                'vertices': {0: {'pos': (-width/2., -height/2.),
                                 'v_color': (255, 0, 0, 255)},
                             1: {'pos': (-width/2., height/2.),
                                 'v_color': (0, 255, 0, 255)},
                             2: {'pos': (width/2., height/2.),
                                 'v_color': (0, 0, 255, 255)},
                             3: {'pos': (width/2., -height/2.),
                                 'v_color': (255, 0, 255, 255)}
                            },
                'indices': [0, 1, 2, 2, 3, 0],
                'vertex_count': 4,
                'index_count': 6,
            }
    
    def get_triangle_data(self, vert_list, us_color, us_range_list):

        opacities = [self.max_us_opacity * (1 - us_range / self.max_us_range) 
                for us_range in us_range_list]
        #print(opacities)
        colors = [list(us_color), list(us_color)]
        [color.append(opacity) for color, opacity in zip(colors,opacities)]
        #print(colors)
        
        color_inds = [0, 1, 1]
        #print(vert_list)
        #print([(i, v) for i,v in enumerate(vert_list)])
        vertices = {i: {'pos': vert_tuple, 'v_color': colors[color_inds[i]]} for i, vert_tuple
                in enumerate(vert_list)}
        model_info = {
                'vertices': vertices,
                'indices': [0, 1, 2],
                'vertex_count': 3,
                'index_count': 3,
            }
        return model_info

    
