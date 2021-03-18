from cymunk import Vec2d
from math import radians, sin, cos


class RobotMecanumControl:
    def __init__(self, root, robot):
        self.root = root
        self.r = robot

        self.ang_vel_max = radians(30)

        self.wheel_vectors = []
        w, h = self.r.siz

        # needs to be smaller as the impulses are detected by ultrasounds
        a = 2 / 3
        w, h = [w / a, h / a]

        # wheel = [position_of_wheel, vector_when_moving_wheel_in_frontal_direction
        self.wheels = [
            [Vec2d(-w, +h), Vec2d(+1, +1)],  # lf
            [Vec2d(+w, +h), Vec2d(-1, +1)],  # rf
            [Vec2d(-w, -h), Vec2d(-1, +1)],  # lb
            [Vec2d(+w, -h), Vec2d(+1, +1)],  # rb
        ]

    def set_ang_vel(self, ang_vel):
        ang_vel = self.ang_vel_max if ang_vel > self.ang_vel_max else ang_vel

        self.r.body.torque(ang_vel)

    def calc_wheel_speed(self, vel_vec, ang_vel):
        """Simple mecanum wheel control algorithm

        http://thinktank.wpi.edu/resources/346/ControllingMecanumDrive.pdf
        """

        vd = vel_vec.length
        th = vel_vec.angle
        dth = ang_vel

        th45 = th + radians(45)
        wheel_speeds = [
            vd * sin(th45) + dth,
            vd * cos(th45) - dth,
            vd * cos(th45) + dth,
            vd * sin(th45) - dth,
        ]
        max_s = max(wheel_speeds)
        if max_s > 1:
            wheel_speeds = [s / max_s for s in wheel_speeds]

        return wheel_speeds

    def apply_wheel_speed(self, wheel_speeds):
        """wheel_speeds in range 0 - 1

        lf, rf, lb, rb
        """
        # rotate ccw
        # wheel_speeds = [+1, +1, +1,+ 1] # go straight
        # wheel_speeds = [+1, +0, +0, +1] # go front left
        # wheel_speeds = [+0, -1, -1, 0] # go back left
        # wheel_speeds = [+1, -1, -1, +1] # strafe left
        # wheel_speeds = [+1, -1, +1, -1] # rotate CW

        imp_value = 1000  # strength of actuators
        # imp_value = 500

        # print(self.wheels)
        b = self.r.body
        ori = b.angle
        for v, wheel_speed in zip(self.wheels, wheel_speeds):
            wheel_pos, wheel_force_dir = v
            imp_vec = wheel_force_dir * imp_value * wheel_speed

            loc_wheel_pos = Vec2d(wheel_pos)
            loc_imp_vec = Vec2d(imp_vec)
            [v.rotate(ori) for v in [loc_wheel_pos, loc_imp_vec]]
            # print('wheel_pos')
            # print(loc_wheel_pos, wheel_pos)
            b.apply_impulse(loc_imp_vec, loc_wheel_pos)

    def go(self, vel_vec, ang_vel, direction=None):
        if direction is not None:
            side = 90
            if type(direction) is str:
                if direction.lower() == "right":
                    vel_vec.rotate_degrees(side)
                if direction.lower() == "left":
                    vel_vec.rotate_degrees(360 - side)
                if direction.lower() == "backleft":
                    vel_vec.rotate_degrees(-120)
            else:
                vel_vec.rotate_degrees(direction)
        wheel_speeds = self.calc_wheel_speed(vel_vec, ang_vel)
        self.apply_wheel_speed(wheel_speeds)
