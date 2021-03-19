

class CollisionControl:
    """Not yet used?!."""
    def __init__(self, ultrasound_count):

        self.ultrasound_count = ultrasound_count

        self.collision_objects = []

        self.add_object_type("wall", 1)
        self.add_object_type("obstacle", 2)
        self.add_object_type("robot", 10)
        self.add_object_type("candy", 42)
        #  self.add_object_type('ultrasound

        self.ultrasound_offset = 100
        us_collision_ids = [self.ultrasound_offset + i for i in range(ultrasound_count)]

        self.add_category("ultrasound_cone", us_collision_ids, False, False)

    def get_collision_ids(self):
        return {
            o.name: o.collision_id
            for o in self.collide_control.collision_objects
        }

    def add_category(
        self,
        object_type,
        collision_id_list,
        collide=True,
        ultrasound_detectable=True,
    ):
        for collision_id in collision_id_list:
            self.add_object_type(
                object_type, collision_id, collide, ultrasound_detectable
            )

    def add_object_type(
        self,
        object_type,
        collision_id,
        collide=True,
        ultrasound_detectable=True,
    ):
        col_obj = {
            "object_type": object_type,
            "collision_id": collision_id,
            "collide": collide,
            "ultrasound_detectable": ultrasound_detectable,
        }
        self.collision_objects.append(col_obj)
