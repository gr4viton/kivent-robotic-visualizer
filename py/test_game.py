import types
from random import randint, choice
import pprint

from logging import info as prinf


from kivy.clock import Clock
from kivy.uix.widget import Widget

from file_loader import FileLoader
from entities import Entities

from robot import Robot
from candy import Candy
from asteroids import Asteroids

from surface import Map2D


class TestGame(Widget):
    def init_collision_ids(self):
        self.ultrasound_count = 10

        # self.collide_control = CollideControl(self.ultrasound_count)
        # self.collision_ids = self.collide_control.collision_ids
        self.collision_ids = {
            "wall": 1,
            "obstacle_rect": 2,
            "obstacle": 3,
            "asteroid": 5,
            "ultrasound_detectable": 0,
            "ultrasound": [50 + i for i in range(self.ultrasound_count)],
            "robot": 100,  # let it be free after robot for num of robot create
            "candy": 42,
        }

        detected_names = ["wall", "obstacle", "obstacle_rect", "robot"]

        self.collision_ids["ultrasound_detectable"] = list(
            {self.collision_ids[name] for name in detected_names}
        )
        print("ultrasound_detectable")
        print(self.collision_ids["ultrasound_detectable"])

        # ignore touch of user
        self.ignore_groups = []
        self.ignore_groups.extend(self.collision_ids["ultrasound"])
        # [ self.ignore_groups.append(self.collision_ids[key]) for key in ['robot']]

    def __init__(self, **kwargs):
        self.init_collision_ids()
        super(TestGame, self).__init__(**kwargs)

        self.gameworld.init_gameworld(
            [
                "cymunk_physics",
                "poly_renderer",
                "rotate_poly_renderer",
                "rotate_renderer",
                #'steering_system'
                "rotate",
                "position",
                "cymunk_touch",
            ],
            callback=self.init_game,
        )

    def info(self, text):
        self.app.info_text += "\n" + str(text)

    def init_game(self):
        # called automatically? probably
        self.pp = pprint.PrettyPrinter(indent=4)
        self.pprint = self.pp.pprint

        self.field_size = 800, 600
        self.to_draw_obstacles = 0

        self.robot = None
        self.robots = None

        self.setup_states()
        self.set_state()
        self.init_loaders()
        print("init_physicals")
        self.init_physicals()
        # self.init_space_constraints()

        self.init_properties_updater()

        self.init_control_logic()

    def init_control_logic(self):
        self.init_chase_candy_updater()

    def init_loaders(self):
        self.fl = FileLoader(self)

    def init_physicals(self):
        #        self._entities = {}
        self.robot_names = ["dalek", "drWho", "k9", "kachna"]
        self.num_of_robots = len(self.robot_names)

        self.setup_collision_callbacks()

        self.entities = Entities(self.app)

        self.map = Map2D(self)

        self.asteroids = Asteroids(self)
        self.init_robots()

    def init_robots(self):
        self.robots = [
            self.get_robot(name, i) for i, name in enumerate(self.robot_names)
        ]

        self.candy = Candy(self)

    def unused_load_robot_svg(self, robot):
        self.fl.load_svg(robot.path, self.gameworld)

    def add_robot(self):
        i = len(self.robots)
        name = f"robot_{i}"
        robot = self.get_robot(name, i)
        self.robots.append(robot)

    def get_robot(self, name, i):
        drive = "mecanum"
        us_count = 3
        return Robot(
            root=self,
            drive=drive,
            robot_name=name,
            us_id_offset=i * us_count,
            robot_number=i,
        )

    def toggle_robot_control(self, state):
        self.robot_controlled = state

        if not state:
            return

        for r in self.robots:
            r.add_state("INIT")
            r.reset_ultrasounds()

    def init_chase_candy_updater(self):
        for r in self.robots:
            r.chase_candy(self.candy)
        self.robot_controlled = False
        Clock.schedule_once(self.chase_candy_update)

    def chase_candy_update(self, dt):
        if self.robot_controlled:
            for r in self.robots:
                r.goto_target()
        Clock.schedule_once(self.chase_candy_update, 0.05)

    def draw_asteroids(self):
        self.asteroids.draw_asteroids()

    def setup_collision_callbacks(self):
        """Setup the correct collisions for the cymunk physics system manager.

        use the physics_system.add_collision_handler
        to define between which collision_ids the collision should happen and between which not

        Following handler functions are passed
        - begin_func - called once on collision begin
        - separate_func - called once on collision end
        """

        physics_system = self.gameworld.system_manager["cymunk_physics"]

        def ignore_collision(na, nb):
            """Returns false to indicate ignoring the collision."""
            return False

        # collide_remove_first

        # add robots
        us_detectable = self.collision_ids["ultrasound_detectable"]
        rob_collision_ids = [
            self.collision_ids["robot"] + ct
            for ct in range(self.num_of_robots)
        ]
        us_detectable.extend(rob_collision_ids)

        self.begin_ultrasound_callback = {}

        # ignore_collision of ultrasound triangle with 0-1024 collision_ids
        # to enable the triangles to clip through other objects
        # ! this should be done on robot / on ultrasound creation
        for us_id in self.collision_ids["ultrasound"]:
            for index_id in range(1024):
                physics_system.add_collision_handler(
                    index_id,
                    us_id,
                    begin_func=ignore_collision,
                    separate_func=ignore_collision,
                )

        # add ultrasound triangles object detection via collision
        # ! this should be done on robot / on ultrasound creation
        for us_id in self.collision_ids["ultrasound"]:
            for detectable in us_detectable:
                print("us_id", us_id)
                physics_system.add_collision_handler(
                    detectable,
                    us_id,
                    begin_func=self.return_begin_ultrasound_callback(
                        us_id, True
                    ),
                    separate_func=self.return_begin_ultrasound_callback(
                        us_id, False
                    ),
                )

        for r_ct in rob_collision_ids:
            from pudb.remote import set_trace

            set_trace(term_size=(238, 54), host="0.0.0.0", port=6900)  # noqa
            physics_system.add_collision_handler(
                self.collision_ids["candy"],
                r_ct,
                begin_func=self.begin_candy_callback,
                separate_func=self.begin_candy_callback,
            )

    def candy_caught(self, robot_ent_id):
        print("candy eaten! by robot:", robot_ent_id)
        self.candy.reset_position()
        self.to_draw_obstacles = 2

    def begin_candy_callback(self, space, arbiter):
        # self.r
        robot_ent_id = arbiter.shapes[1].body.data
        # us[us_id] = rob
        self.candy_caught(robot_ent_id)
        return False

    def get_robot_from_us_id(self, us_id):
        for r in self.robots:
            if r.is_this_us_mine(us_id):
                return r
        return None

    def get_robot_from_ent_id(self, robot_id):
        for r in self.robots:
            if r.ent == robot_id:
                return r
        return None

    def return_begin_ultrasound_callback(self, us_id, state):
        # this adds the segmentation fault on exit - but currently I am not able to simulate ultrasounds any other way than
        # returning
        def begin_ultrasound_callback(self, space, arbiter):
            # ent0_id = arbiter.shapes[0].body.data #detectable_object
            # ent1_id = arbiter.shapes[1].body.data #robot
            space.enable_contact_graph = True
            # print(space.bodies)

            ent0 = arbiter.shapes[0]
            e_id = ent0.body.data
            # a = ent0.body
            # print(len(arbiter.shapes))
            con = arbiter.contacts
            # print(a)
            # print(dir(a))
            # print(a.contact)
            rob_ent = arbiter.shapes[1].body.data

            if con is not None:
                r = self.get_robot_from_ent_id(rob_ent)

                # r = self.get_robot_from_us_id(us_id)
                r.ultrasound_detection(us_id, ent0, state)
                ent = self.gameworld.entities[e_id]
                cat = [
                    cat
                    for cat, id_list in self.entities.items()
                    if e_id in id_list
                ]
                # print('detect', cat, e_id)
            return False

        ind = 2 * us_id + int(state)
        self.begin_ultrasound_callback[ind] = types.MethodType(
            begin_ultrasound_callback, self
        )
        return self.begin_ultrasound_callback[ind]
        # return begin_ultrasound_callback

    def add_entity(self, ent, category):
        # add to entity counter
        print("added entity", category)
        if category not in self.entities.keys():
            self.entities[category] = []
        self.entities.add_item(category, ent)

    def set_robots_rand(self):
        for r in self.robots:
            r.set_random_position()

    def kick_robots(self):
        for r in self.robots:
            self.kick_robot(r)

    def kick_robot(self, r):
        rob_ent = r.ent
        print(rob_ent)

        rob_body = self.gameworld.entities[rob_ent].cymunk_physics.body

        im = (10000, 10000)
        seq = [-1, 1]
        imp = (choice(seq) * randint(*im), choice(seq) * randint(*im))
        rob_body.apply_impulse(imp)
        print("impulse", imp)

    def init_entity(
        self,
        component_dict,
        component_order,
        category="default_category",
        object_info=None,
    ):
        if object_info is not None:
            category = object_info.get("category", category)
        else:
            object_info = {}

        ent = self.gameworld.init_entity(component_dict, component_order)

        # add to counter
        self.add_entity(ent, category)

        object_info.update({"ent": ent})
        entity_info = object_info

        # print('@'*42)
        # self.pprint(entity_info)
        # print(Robot.cats, category in Robot.cats)

        # add to specific subobjects
        # if self.robot is not None:
        #   self.robot.add_entity(entity_info)
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
                prinf("Clearing entities of " + ent_cat)
                for ent in ent_list:
                    self.destroy_created_entity(ent, 0)
                self.entities[ent_cat].clear()
        for r in self.robots:
            r.reset_ultrasounds()

    def destroy_created_entity(self, ent_id, dt):
        self.gameworld.remove_entity(ent_id)

    # def draw_some_stuff(self):
    #   self.load_svg('objects.svg', self.gameworld)
    # self.load_svg('map.svg', self.gameworld)
    #    self.map.draw_stuff()
    #       self.load_svg('map.svg', self.gameworld)

    def draw_obstacles(self):
        self.map.draw_obstacles(5)

    def draw_rect_obstacles(self):
        self.map.draw_rect_obstacles(5)

    def update(self, dt):
        self.gameworld.update(dt)

    def setup_states(self):
        self.gameworld.add_state(
            state_name="main",
            systems_added=["poly_renderer"],
            systems_removed=[],
            systems_paused=[],
            systems_unpaused=["poly_renderer"],
            screenmanager_screen="main",
        )

    def set_state(self):
        self.gameworld.state = "main"

    def init_properties_updater(self):
        Clock.schedule_once(self.update_properties)

    def update_properties(self, dt):
        self.app.ultrasound_status = "\n".join(
            [r.ultrasound_status() for r in self.robots]
        )
        self.app.robot_states = "\n\n".join(
            [str(r.states) for r in self.robots]
        )
        #       self.app.robot_score =
        #   self.r.reset_ultrasounds()
        if self.to_draw_obstacles > 0:
            self.map.draw_obstacles(self.to_draw_obstacles)
            self.to_draw_obstacles = 0
        Clock.schedule_once(self.update_properties, 0.05)
