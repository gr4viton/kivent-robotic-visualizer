from enum import Enum, auto
from typing import List
from pydantic import BaseModel, Field


class Material(BaseModel):
    code: str = Field(description="snake_case code of the thing")

    passable: bool  # other objects can go through it
    reflects_sound: bool  # ultrasound detectable
    reflects_light: bool  # laser detectable


class Materials:
    solid = Material(
        code="solid",
        passable=False,
        reflects_sound=True,
        reflects_light=True,
    )
    glass = Material(
        code="glass",
        passable=False,
        reflects_sound=True,
        reflects_light=False,
    )
    air = Material(  # can be used for the ultrasound detection triangles
        code="air",
        passable=True,
        reflects_sound=False,
        reflects_light=False,
    )
    fog = Material(
        code="fog",
        passable=True,
        reflects_sound=False,
        reflects_light=True,
    )
    water = Material(
        code="water",
        passable=True,  # there should be a friction coeficient
        reflects_sound=True,  # i hope so
        reflects_light=True,
    )

# class ThingTypes:
#     wall = ThingType(
#         code = "wall",
#         collision_group = 1
#         material = Materials.solid
#     )

class CollisionGroup:
    id: int
#    thing_class: Thing
    thing_class = None


class ThingParameters:
    material: Material
    collision_group: CollisionGroup

class Thing:
    code: str
    # thing_parameters: ThingParameters
    material: Material
    collision_group: CollisionGroup



class CollisionGroups:
    last_id = 0

    collision_groups = {}

    @classmethod
    # def get_new_group(cls, thing_class):
    def get_new_group(cls, thing_class=None):
        # if not isinstance(thing_class, Thing):
        #     raise TypeError("You need to pass Thing class when requesting a free collision_group.")
        collision_group_exists = cls.collision_groups.get(thing_class) is not None
        # if collision_group_exists:


        # new_group = CollisionGroup(id=cls.last_id, thing_class=thing_class)
        new_group = "Fungis"
        cls.last_id += 1
        return new_group


class Wall(Thing):
    _code = "wall"
    _material = Materials.solid,
    _collision_group = CollisionGroups.get_new_group()

    def __init__(self):
        # super().__init__(code="wall", material=self._material, collision_group=self._collision_group)
        pass

    def init_entities():
        # create entities
        pass

    def init_collisions():
        # setup collisions
        pass
    # def on_click()


class DetectionZone(Thing):
    code = "air_detection_zone"
    # collision_group = CollisionGroups.get_new_group() # each detection_zone has to have its own new collision group for the detection to work
    collision_group = CollisionGroups.get_new_group()

    @property
    def collision_id(self):
        return collision_group.id  # IDK

    def __init__(self, material, detectable_materials):
        collision_group = CollisionGroups.get_new_group(self.__class__)
        super().__init__(code="wall", material=self._material, collision_group=collision_group)

        # rather detectable_material_properties
        # - reflect_sound = true

        # super().__init__(self._code="wall", thing_parameters=self._thing_parameters)
        # create entities
        # setup collisions
        # - based on the material
        # - based on the detectable_materials
        pass


def main():
    thing = Wall()
    thing2 = Wall()
    # print(Wall.collision_group)
    # print(AirDetectionZone.collision_group)
    # ultrasound_zone = DetectionZone(material=Material.air, detectable_materials=[])
    # on click
    # if isinstance(thing, Wall):

if __name__ == "__main__":
    main()

