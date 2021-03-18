class CollisionControl:
    def __init__(self, ultrasound_count):

        self.ultrasound_count = ultrasound_count

        self.collision_objects = []
        self.add_object_type("wall", 1)
        self.add_object_type("obstacle", 2)
        self.add_object_type("robot", 10)
        self.add_object_type("candy", 42)
        #  self.add_object_type('ultrasound

        self.ultrasound_offset = 100
        us_cts = [self.ultrasound_offset + i for i in range(ultrasound_count)]
        self.add_category("ultrasound_cone", us_cts, False, False)

    def get_collision_types(self):
        return {
            o.name: o.collision_type
            for o in self.collide_control.collision_objects
        }

    def add_category(
        self,
        object_type,
        collision_type_list,
        collide=True,
        ultrasound_detectable=True,
    ):
        for ct in collision_type_list:
            self.add_object_type(
                object_type, ct, collide, ultrasound_detectable
            )

    def add_object_type(
        self,
        object_type,
        collision_type,
        collide=True,
        ultrasound_detectable=True,
    ):
        col_obj = {
            "object_type": object_type,
            "collision_type": collision_type,
            "collide": collide,
            "ultrasound_detectable": ultrasound_detectable,
        }
        self.collision_objects.append(col_obj)
