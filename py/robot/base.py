from cymunk import Vec2d
from random import randint
from math import radians, sin, cos
import svgwrite as svg

from settings import svg_folder_path

import json

from robot.ultrasound_sensor import UltrasoundSensor
from robot.mecanum_control import RobotMecanumControl

from robot.ultrasound_control import RobotMixinUltrasoundControl
from robot.chase_candy_control import RobotMixinChaseCandyControl


svg.profile = "tiny"


class Robot(RobotMixinUltrasoundControl, RobotMixinChaseCandyControl):

    cats = ["ultrasound", "robot"]

    def __init__(
        self, root, drive, robot_name="robot", us_id_offset=0, robot_number=0
    ):
        self.root = root
        self.robot_name = robot_name
        self.us_id_offset = us_id_offset
        self.robot_number = robot_number

        self.baseProfile = "tiny"  # 'full'
        self.__svg_dir__ = "../assets/objects/svg/"
        self.ents = {category: [] for category in Robot.cats}

        self.ultrasounds = {}

        self.cts = root.collision_types
        self.drive = drive
        self.create_robot()

        self.entity = self.root.gameworld.entities[self.ent]
        self.body = self.entity.cymunk_physics.body

        if drive == "mecanum":
            self.control = RobotMecanumControl(self.root, self)

        self.init_chase_candy_control()
        self.init_ultrasound_control()

    def set_random_position(self):
        self.entity.cymunk_physics.body.position = self.candy.get_rand_pos()

    def get_pos(self):
        return self.body.position

    def create_ultrasound(self, name, color, stroke_color, vert_list):
        cat = "ultrasound"
        info_dict = {
            "collision_type": self.cts[cat],
            "object_info": {"name": str(name), "category": cat, "mass": 0},
        }
        info_str = json.dumps(info_dict)
        id_str = self.robot_name + "_" + cat + "_" + str(name)

        #           color = self.dwg.SolidColor('green', 0.2)
        gradient = svg.gradients.LinearGradient(color="#00FF00", opacity=0.2)

        ultra = (
            self.dwg.polygon(vert_list, id=id_str, description=info_str)
            .fill("green", opacity=0.2)
            .stroke("white", width=1)
            .dasharray([20, 10])
        )
        self.dwg.add(ultra)

    def add_entity(self, entity_info):
        category = entity_info["category"]

        print(";;;;;;;;;;;;;;;;;;;;;", category)

        if category in "ultrasound":
            us = UltrasoundSensor(self, **entity_info)
            #            self.ultrasounds.append()
            self.ultrasounds[entity_info["us_id"]] = us
            print(entity_info["us_id"])
        # elif category in 'robot':
        # self.ent = entity_info['ent']

        # self.entities[category].append(ent)

    def create_robot(self):
        #      self.color = '#FF0000'
        #       self.stroke_color = '#000000'
        #        self.path = svg_folder_path + 'robot.svg'

        w, h = self.root.field_size

        pos = (randint(0, w), randint(0, h))
        self.siz = [40, 60]
        self.mass = 100

        self.create_robot_rect(
            self.robot_name,
            self.mass,
            pos,
            self.siz,
            self.us_id_offset,
            self.robot_number,
        )

    def create_robot_rect(
        self, name, mass, pos, siz, us_id_offset, robot_number
    ):
        id_str = self.robot_name
        insert_pos = [pos[i] + siz[i] / 2 for i in range(2)]
        # self.pos = insert_pos
        self.pos = pos
        cat = "robot"
        robot_name = name

        cts = self.root.collision_types
        self.ct = cts["robot"] + robot_number
        # robot_group = 42

        width, height = siz
        w, h = siz
        robot_verts = [
            (-width / 2.0, -height / 2.0),
            (-width / 2.0, height / 2.0),
            (width / 2.0, height / 2.0),
            (width / 2.0, -height / 2.0),
        ]

        robot_shape = {
            "shape_type": "poly",
            "elasticity": 0.6,
            "collision_type": self.ct,
            "friction": 1.0,
            #       'group' : robot_group,
            "shape_info": {
                "mass": mass,
                "offset": (0, 0),
                "vertices": robot_verts,
            },
        }

        col_shapes = [robot_shape]

        physics = {
            "main_shape": "poly",
            "velocity": (0, 0),
            "position": self.pos,
            "angle": 0,
            "angular_velocity": radians(0),
            "ang_vel_limit": radians(0),
            "mass": mass,
            "col_shapes": col_shapes,
        }

        # ultrasounds
        open_angle = radians(45)
        count_ultrasounds = 3
        names = ["left", "middle", "right"]
        ultrasound_range = 60
        ultrasound_ranges = [ultrasound_range, ultrasound_range + 100]
        x0, y0 = self.pos[0] + 0, self.pos[1] + h / 4
        center_x0, center_y0 = 0, h / 2

        us_color = (0, 255, 0)
        self.max_us_range = 250
        self.max_us_opacity = 200
        us_models = []
        sensor_width = 10
        for i in range(count_ultrasounds):
            # to center it
            shift_angle = count_ultrasounds / 2 * open_angle  # + radians(180)
            # cone edges
            edge_angles = (
                i * open_angle - shift_angle,
                (1 + i) * open_angle - shift_angle,
            )

            us_x = (i - (count_ultrasounds - 1) / 2) * sensor_width
            us_y = 1
            x0 = center_x0 + us_x
            y0 = center_y0 + us_y

            edge_points = [
                [
                    ultrasound_range * sin(edge_angle) + x0,
                    ultrasound_range * cos(edge_angle) + y0,
                ]
                for edge_angle in edge_angles
            ]

            vert_list = [(x0, y0), edge_points[0], edge_points[1]]

            mass = 0.1
            us_id = cts["ultrasound"][i] + us_id_offset

            us_shape = {
                "shape_type": "poly",
                "elasticity": 0.0,
                "collision_type": us_id,
                "friction": 0.0,
                "sensor": True,
                #'group': robot_group,
                "shape_info": {
                    "mass": mass,
                    "offset": (0, 0),
                    "vertices": vert_list,
                },
            }
            col_shapes.append(us_shape)

            entity_info = {
                "category": "ultrasound",
                "us_id": us_id,
                "name": names[i],
                "distance_range": ultrasound_range,
                "us_pos": (us_x, us_y),
            }

            us_color = (
                randint(100, 200),
                255 * randint(8, 10) / 10,
                randint(100, 100),
            )
            us_model = self.get_triangle_data(
                vert_list, us_color, ultrasound_ranges
            )
            us_models.append(us_model)

            # self.root.add_entity(entity_info)

            us = UltrasoundSensor(self, **entity_info)
            self.ultrasounds[entity_info["us_id"]] = us
            print(entity_info["us_id"])

        model_name = robot_name
        model_manager = self.root.gameworld.model_manager

        rect_data = self.get_rectangle_data(h, w)
        rect_data2 = self.get_rectangle_data(w, w)

        rects = [rect_data, rect_data2]
        rects.extend(us_models)

        model_data = self.join_vert_models(rects)

        rectangle_model = model_manager.load_model(
            "vertex_format_2f4ub",
            model_data["vertex_count"],
            model_data["index_count"],
            model_name,
            indices=model_data["indices"],
            vertices=model_data["vertices"],
        )

        # self.root.pprint(dir(model_manager))
        robot_model = rectangle_model
        # self.shapes['rectangle_model'] = rectangle_model

        component_dict = {
            "position": pos,
            "rotate_poly_renderer": {"model_key": rectangle_model},
            "cymunk_physics": physics,
            "rotate": radians(0),
        }

        cat = "robot"
        info_dict = {
            "mass": mass,
            "object_info": {"name": name, "category": cat},
        }
        info_str = json.dumps(info_dict)

        object_info = info_dict["object_info"]

        print("robot component creation")
        component_order = [
            "position",
            "rotate",
            "rotate_poly_renderer",
            "cymunk_physics",
        ]
        # self.root.init_entity(component_dict, component_order, object_info=object_info)

        self.ent = self.root.gameworld.init_entity(
            component_dict, component_order
        )
        print(">>>>>>", self.ent)
        self.root.add_entity(self.ent, "robot")

    def join_vert_models(self, model_list):
        # self.root.pprint(model_list)

        vertices = None
        indices = None
        prev_vert_count = 0
        for d in model_list:
            if indices is None:
                indices = list(d["indices"])
                vertices = dict(d["vertices"])
            else:
                this_indices_incremented = [
                    ind + prev_vert_count for ind in d["indices"]
                ]
                indices.extend(this_indices_incremented)
                this_vertices_incremented = {
                    (k + prev_vert_count): v for k, v in d["vertices"].items()
                }

                # did not work
                # vertices.update(this_indices_incremented)
                for k, v in this_vertices_incremented.items():
                    vertices[k] = v

            prev_vert_count += d["vertex_count"]

        joined = {
            "vertex_count": sum([d["vertex_count"] for d in model_list]),
            "index_count": sum([d["index_count"] for d in model_list]),
            "indices": indices,
            "vertices": vertices,
        }
        # self.root.pprint(joined)
        return joined

    @staticmethod
    def get_rectangle_data(height, width):
        def _rnd():
            return randint(0, 255)

        def c_rnd():
            return (_rnd(), _rnd(), _rnd(), 255)

        return {
            "vertices": {
                0: {"pos": (-width / 2.0, -height / 2.0), "v_color": c_rnd()},
                1: {"pos": (-width / 2.0, height / 2.0), "v_color": c_rnd()},
                2: {"pos": (width / 2.0, height / 2.0), "v_color": c_rnd()},
                3: {"pos": (width / 2.0, -height / 2.0), "v_color": c_rnd()},
            },
            "indices": [0, 1, 2, 2, 3, 0],
            "vertex_count": 4,
            "index_count": 6,
        }

    def get_triangle_data(self, vert_list, us_color, us_range_list):

        opacities = [
            self.max_us_opacity * (1 - us_range / self.max_us_range)
            for us_range in us_range_list
        ]
        # print(opacities)
        colors = [list(us_color), list(us_color)]
        [color.append(opacity) for color, opacity in zip(colors, opacities)]
        # print(colors)

        color_inds = [0, 1, 1]
        # print(vert_list)
        # print([(i, v) for i,v in enumerate(vert_list)])
        vertices = {
            i: {"pos": vert_tuple, "v_color": colors[color_inds[i]]}
            for i, vert_tuple in enumerate(vert_list)
        }
        model_info = {
            "vertices": vertices,
            "indices": [0, 1, 2],
            "vertex_count": 3,
            "index_count": 3,
        }
        return model_info
