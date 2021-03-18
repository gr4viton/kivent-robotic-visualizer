

class RobotMixinUltrasoundControl:
    #   @property
    #  def ultrasounds(self):

    #    return self.Ultrasounds

    def ultrasound_hit(self, ultrasound_id, object_ent_id):
        return self.ultrasound_detection(ultrasound_id, object_ent_id, True)

    def ultrasound_miss(self, ultrasound_id, object_ent_id):
        return self.ultrasound_detection(ultrasound_id, object_ent_id, False)

    def ultrasound_detection(self, ultrasound_id, object_ent_id, state):
        us = self.ultrasounds[ultrasound_id]
        # us.detected = state
        us.set_detected_state(state)

        self.colors = {True: (0, 0, 0, 255), False: (0, 128, 255, 255)}
        # print(object_ent_id)
        # entity = self.root.entities[object_ent_id]
        # print(entity)
        # rend_model = entity.rotate_poly_renderer
        # rend_model.model[ind].v_color = self.colors[state]

        return us.name

    def ultrasound_status(self):
        return "|".join(
            [
                "{}={}".format(us.name, us.detected)
                for us in self.ultrasounds.values()
            ]
        )

    def reset_ultrasounds(self):
        for us in self.ultrasounds.values():
            us.detected = False

    def ultrasound_detections(self):

        return [us.detected for us in self.ultrasounds.values()]

    def is_this_us_mine(self, us_id):
        for us in self.ultrasounds.values():
            if us.us_id == us_id:
                return True
