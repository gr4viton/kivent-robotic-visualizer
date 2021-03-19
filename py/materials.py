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

class ThingType:
    code: str
    material: Material
    collision_id: int


class ThingParameters:
    material: Material
    collision_id: int


# class ThingTypes:
#     wall = ThingType(
#         code = "wall",
#         collision_id = 1
#         material = Materials.solid
#     )

class CollisionIds:
    last_id = 0

    ids = []

    @classmethod
    def get_free_id(cls):
        free_id = cls.last_id
        cls.last_id += 1
        return free_id


class Wall(ThingType):
    code = "wall"
    material = Materials.solid
    collision_id = CollisionIds.get_free_id()
    def __init__(self):
        # create entities
        # setup collisions
        pass
    # def on_click()


class AirDetectionZone(ThingType):
    code = "air_detection_zone"
    material = Materials.air
    collision_id = CollisionIds.get_free_id()

    def __init__(self, detectable_materials):

        # create entities
        # setup collisions
        # - based on the material
        # - based on the detectable_materials
        pass

def main():
    thing = Wall()
    thing2 = Wall()
    print(Wall.collision_id)
    print(AirDetectionZone.collision_id)
    # on click
    # if isinstance(thing, Wall):

if __name__ == "__main__":
    main()

