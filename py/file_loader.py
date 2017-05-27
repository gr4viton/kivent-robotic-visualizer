
from kivent_core.gameworld import GameWorld
from kivent_core.managers.resource_managers import texture_manager

from kivent_core.rendering.svg_loader import SVGModelInfo
import svgwrite as svg

import random as rnd
from random import randint, choice, randrange
from math import radians, pi, sin, cos
import json

from random import randint, choice, randrange
import time
import logging

from logging import info as prinf
from logging import debug as prind
from logging import warning as prinw
from logging import error as prine

class FileLoader:

    def __init__(self, root):
        self.root = root
        self.gameworld = root.gameworld
        pass

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


    def load_svg(self, fname, massless=False):
        mm = self.gameworld.model_manager
        data = mm.get_model_info_for_svg(fname)

        print('loading svg:', fname)
        mass = 50
        object_info = {'category': fname}
        category = fname
        collision_type = 0
        name = None

        for info in data['model_info']:
            info, pos = self.normalize_info(info)

            if info.description is not None:
                info_dict = json.loads(info.description)
  #              print(info_dict)

                mass = float(info_dict.get('mass', mass))
                object_info = info_dict.get('object_info', object_info)
                collision_type = int(info_dict.get('collision_type', collision_type))

            #if massless:
            #    mass = float('inf')
            #    mass = float(0)
                #av = float('inf')

 #           prinf('mass=%f', mass)
            #Logger.debug
            prind("adding object with title/element_id=%s/%s and desc=%s",
                         info.title, info.element_id, info.description)


            this_model_name = data['svg_name']
            print('>>'*42)
            self.root.pprint(info)
            model_name = mm.load_model_from_model_info(info, this_model_name)
            

            poly_shape = {
                'shape_type': 'poly',
                'elasticity': 0.6,
                'collision_type': collision_type,
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
            self.root.init_entity(create_dict, component_order, object_info=object_info)

#        mm.unload_models_for_svg(data['svg_name'])


