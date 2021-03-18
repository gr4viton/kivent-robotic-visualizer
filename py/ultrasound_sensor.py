from logging import info as prinf


class UltrasoundSensor:
    def __init__(
        self,
        robot,
        us_id,
        name,
        open_angle=None,
        distance_range=None,
        category="ultrasound",
        mass=None,
        us_pos=None,
    ):
        self.name = name
        self.r = robot
        self.us_id = us_id

        self.open_angle = open_angle
        self.distance_range = distance_range
        self.detected = False
        self.us_pos = us_pos
        prinf("UltrasoundSensor created and entangled: %s %s", us_id, name)

        opa = 242
        self.colors = {True: (255, 0, 0, opa), False: (0, 255, 0, opa)}
        self.v_inds = {"left": 8, "middle": 11, "right": 14}

    def set_detected_state(self, state):
        self.detected = state
        # this for changing a vertex color (do it properly later.)
        ind = self.v_inds[self.name]

        rend_model = self.r.entity.rotate_poly_renderer.model[
            ind
        ].v_color = self.colors[state]
        # txu_manager = self.r.root.gameworld.texture_manager
        # a = txu_manager.loaded_textures
        # print('loaded_textures', a)
        # a = txu_manager
        ##print(a)
        ##print(dir(a))

        ##txu = txu_manager.get_texture_by_name('warning')
        # txu = txu_manager.get_texkey_from_name('warning')
        # a = rend_model
        # print(a)
        # print(dir(a))
        # width, height = 100,100
        # uvs = [0., 0., 1., 1.]
        ##rend_model.set_textured_rectangle(width, height, uvs)

    ## rend_model.set_textured_rectangle(txu)
    # rend_model.flip_textured_rectangle_horizontally()



