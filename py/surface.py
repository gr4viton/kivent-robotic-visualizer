

from random import randint, choice, randrange
from math import radians, pi, sin, cos
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
        w0, h0 = self.root.field_size

        sizes = [(w0, t), (t, h0+2*t), (w0,t), (t, h0+2*t)]
        poss = [[0, -t], [w0, -t], [0, h0], [-t, -t]]
        poss = [[pos[0] + x0, pos[1] + y0] for pos in poss]

        for pos, size in zip(poss, sizes):
            self.create_wall(pos, size, txu)


    def create_wall(self, pos_lf, size, txu, name='wall'):
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

        name = cat + str(randint(0,100000))
        object_info = {
            'name': name,
            'category': cat,
        }
        component_order = ['position', 'rotate', 'rotate_renderer', 'cymunk_physics']
        self.wall_id += 1
        return self.root.init_entity(create_component_dict, component_order, object_info=object_info)

    def draw_rect_obstacles(self, count=10):
        fname = self.create_rect_obstacles(count)
        self.root.fl.load_svg(fname, self.root.gameworld)

    def draw_obstacles(self, count=10):
        self.create_obstacles(count)
        #self.draw_rect_obstacles()

    #def draw_stuff(self):
        #self.draw_obstacles()
        #self.draw_rect_obstacles()
     #   pass

    def create_obstacles(self, count):
        self.color = '#42ACDC'
        self.stroke_color = '#000000'

        Fw, Fh = self.root.field_size

        w, h = Fw, Fh
        siz = (str(w), str(h))
        print(siz)

        dens_interval = (900, 1000)
 #       mass_interval = (1000, 5000)
        smaller = h if h<=w else w
        siz_min, siz_max = one_siz_interval = 0.01*smaller, 0.08* smaller
        siz_interval = [one_siz_interval, one_siz_interval]

        model_manager = self.root.gameworld.model_manager
        start = int(time.time())
        for i in range(count):
            group = start - i
            print(group)

            rnd.seed(time.time())
            siz = [randint(*siz_interval[i]) for i in range(2)]

            pos_lf_interval = ((0, w - siz[0]), (0, h - siz[1]))

            pos_of_shape = [randint(*pos_lf_interval[i]) + siz[i]/2 for i in range(2)]
            pos = (0,0)
  #          mass = randint(*mass_interval)
            dens = randint(*dens_interval)
            mass = siz[0] * siz[1] * dens/1000

            cat = 'obstacle'
            name = cat + str(i)
            info_dict = {
                        'mass': mass,
                        'object_info': {
                            'name': name,
                            'category': cat,
                        }
                    }

            color = (0, 128, 255, 255)
            v_count = randint(3, 5) + randint(0, 5)
            model_data = self.get_polyobstacle(pos, siz, v_count, color)
            #self.root.pprint(model_data)

            model_name = 'poly_obstacle' + str(v_count) + 'v' + str(time.time())
            model = model_manager.load_model(
                                            'vertex_format_2f4ub',
                                            model_data['vertex_count'],
                                            model_data['index_count'],
                                            model_name,
                                            indices=model_data['indices'],
                                            vertices=model_data['vertices']
                                            )
            col_shapes = []
            for tri_verts in model_data['tri_list']:

                col_shape = {
                        'shape_type': 'poly',
                        'elasticity': 0.6,
                        'collision_type': self.cts[cat],
                        'friction': 1.0,
                        'group': group,
                        'shape_info': {
                            'mass': mass,
                            'offset': (0, 0),
                            'vertices': tri_verts
                        }
                    }
                col_shapes.append(col_shape)

            physics = {
                'main_shape': 'poly',
                'velocity': (0, 0),
                'position': pos_of_shape,
                'angle': 0,
                'angular_velocity': radians(0),
                'ang_vel_limit': radians(0),
                'mass': mass,
                'col_shapes': col_shapes
            }



            component_dict = {
                    'position': pos_of_shape,
                    'rotate_poly_renderer': {
                        'model_key': model
                        },
                        'cymunk_physics': physics,
                        'rotate': radians(0),
                }


            cat = 'obstacle'
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
            self.root.add_entity(self.ent, cat)
            print('>>>>>>', self.ent)


    # kivy - 12_drawing_shapes
    def create_rect_obstacles(self, count):
        self.color = '#42ACDC'
        self.stroke_color = '#000000'
        self.path = self.__svg_map_dir__ + 'map{}.svg'

        Fw, Fh = self.root.field_size

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

        for i in range(count):

            rnd.seed(time.time())
            #pos = siz = (100,100)
         #   rnd.seed(time.time())
            siz = [randint(*siz_interval[i]) for i in range(2)]

            pos_lf_interval = ((0, w - siz[0]), (0, h - siz[1]))

            pos = [randint(*pos_lf_interval[i]) + siz[i]/2 for i in range(2)]
  #          mass = randint(*mass_interval)
            dens = randrange(*dens_interval)
            mass = siz[0] * siz[1] * dens/1000
            cat = 'obstacle_rect'
            name = cat + str(i)
            info_dict = {
                        'mass': mass,
                        'collision_type': self.cts[cat],
                        'object_info': {
                            'name': name,
                            'category': cat,
                        }
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

    # kivy - 12_drawing_shapes
    def get_layered_regular_polygon(levels, sides, middle_color,
                                    radius_color_dict, pos=(0., 0.)):
        '''
        radius_color_dict = {level#: (r, (r,g,b,a))}
        '''
        x, y = pos
        angle = 2 * pi / sides
        all_verts = {}
        all_verts[0] = {'pos': pos, 'v_color': middle_color}
        r_total = 0
        i = 0
        indices = []
        vert_count = 1
        ind_count = 0
        ind_ext = indices.extend
        for count in range(levels):
            level = i + 1
            r, color = radius_color_dict[level]
            for s in range(sides):
                new_pos = list((x + (r + r_total) * sin(s * angle),
                    y + (r + r_total) * cos(s * angle)))
                all_verts[vert_count] = {'pos': new_pos, 'v_color': color}
                vert_count += 1
            r_total +=  r
            c = 1 #side number we are on in loop
            if level == 1:
                for each in range(sides):
                    if c < sides:
                        ind_ext((c, 0, c+1))
                    else:
                        ind_ext((c, 0, 1))
                    ind_count += 3
                    c += 1
            else:
                for each in range(sides):
                    offset = sides*(i-1)
                    if c < sides:
                        ind_ext((c+sides+offset, c+sides+1+offset, c+offset))
                        ind_ext((c+offset, c+1+offset, c+sides+1+offset))
                    else:
                        ind_ext((c+sides+offset, sides+1+offset, sides+offset))
                        ind_ext((sides+offset, 1+offset, sides+1+offset))
                    ind_count += 6
                    c += 1
            i += 1
        return {'indices': indices, 'vertices': all_verts,
                'vertex_count': vert_count, 'index_count': ind_count}

    @staticmethod
    def get_polyobstacle(pos, siz, v_count, color):

        rnd.seed(time.time())
        vert_count = 0
        ind_count = 0
        angles = [radians(randint(0, 360)) for i in range(v_count)]
        angles = sorted(angles)
        indices = []
        vert_positions = [(0., 0.)]
        rad_range = sorted(siz)
        all_verts = {}

        tri_list = []
        angles = [radians(360*i/v_count) for i in range(v_count)]
        def get_randomized_angle(j, k, k_angle_offset=0):
            a_1 = angles[j]
            a_2 = angles[k] + k_angle_offset
            a_min = a_1
            a_max = a_1 + (a_2 - a_1) * 0.8 # to not make it too convex
            return randint(int(a_min * 100), int(a_max * 100)) / 100

        angles = [get_randomized_angle(i, i+1) for i in range(len(angles)-1)]
        angles.append(get_randomized_angle(len(angles) - 1, 0, radians(360)))
        print(angles)
        for ang in angles:
            radius = randint(*rad_range)
            rand_siz = [randint(int(s*1000/2), int(s*1000))/1000/s for s in siz]
            pos = radius * cos(ang) * rand_siz[0], radius * sin(ang) * rand_siz[1]
            vert_positions.append(pos)

        for i, v_pos in enumerate(vert_positions):
            all_verts.update({i: {'pos': v_pos, 'v_color': color}})
            if i>1:
                inds = (0, i-1, i)
                indices.extend(inds)
                tri_list.append([vert_positions[ind] for ind in inds])
            else:
                inds = (0, v_count, 1)
                indices.extend(inds)
                tri_list.append([vert_positions[ind] for ind in inds])


        vert_count = len(all_verts)
        ind_count = len(indices)
        model= {'indices': indices, 'vertices': all_verts,
                'vertex_count': vert_count, 'index_count': ind_count}
        model['vert_list'] = vert_positions
        model['tri_list'] = tri_list
        return model
