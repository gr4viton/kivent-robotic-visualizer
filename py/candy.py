from random import randint
from math import radians


class Candy:
    def __init__(self, root):
        self.root = root
        pos = self.get_rand_pos()
        print(">>>", pos)
        self.siz = (42.0, 42.0)

        self.initial_ang_vel = -1500
        # self.ent = self.create_candy(pos)
        # self.create_asteroid(pos)
        self.create_candy(pos)
        self.body = self.root.gameworld.entities[self.ent].cymunk_physics.body

    def get_rand_pos(self):
        w, h = self.root.field_size
        return [float(randint(0, s)) for s in [w, h]]

    def reset_position(self):
        self.body.position = self.get_rand_pos()
        self.body.angular_velocity = self.initial_ang_vel

    def create_candy(self, pos):
        vel = (0.0, 0.0)  # randint(-15, 15)
        angle = radians(randint(-360, 360))
        # angular_velocity = radians(randint(-1500, -1500))
        angular_velocity = self.initial_ang_vel

        cts = self.root.collision_types
        siz = self.siz

        mass = 10.0
        shape_dict = {
            "inner_radius": 0,
            "outer_radius": 20,
            "mass": mass,
            "offset": (0, 0),
        }
        col_shape = {
            "shape_type": "circle",
            "elasticity": 1.0,
            "collision_type": cts["candy"],
            "shape_info": shape_dict,
            "friction": 1.0,
        }

        col_shapes = [col_shape]

        physics_component = {
            "main_shape": "circle",
            "velocity": vel,
            "position": pos,
            "angle": angle,
            "angular_velocity": angular_velocity,
            "vel_limit": 250,
            "ang_vel_limit": radians(11200),
            "mass": mass,
            "col_shapes": col_shapes,
        }

        component_dict = {
            "cymunk_physics": physics_component,
            "rotate_renderer": {
                "texture": "candy",
                "size": siz,
                "render": True,
            },
            "position": pos,
            "rotate": 0,
        }

        component_order = [
            "position",
            "rotate",
            "rotate_renderer",
            "cymunk_physics",
        ]

        cat = "candy"

        self.ent = self.root.gameworld.init_entity(
            component_dict, component_order
        )
        self.root.add_entity(self.ent, cat)
        # return self.root.init_entity(create_component_dict, component_order, cat)
