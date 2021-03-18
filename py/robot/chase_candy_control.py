from cymunk import Vec2d
from math import radians, sqrt  # , degrees


class RobotMixinChaseCandyControl:

    def init_chase_candy_control(self):
        self.state_count = 20
        self.states = [None for i in range(self.state_count)]
        self.poss = [None for i in range(self.state_count)]

        self.stuck_rel_vec = None
        self.stuck_angle = 110
        self.stuck_counter = 0

    def chase_candy(self, candy):
        self.candy = candy

        self.t_body = self.candy.body

    def camera_get_target(self):
        """Returns relative position and orientation of target

        possibly with simulated error
        """
        # pos = self.body.position
        # t_pos = self.t_body.position
        # t_dir = [t_xy - xy for xy, t_xy in zip(pos, t_pos)]

        global_vec = self.t_body.position - self.body.position

        ori = self.body.angle
        rel_vec = global_vec
        rel_vec.rotate(-ori - radians(90))
        # print(degrees(rel_vec.angle))
        return rel_vec

    def add_state(self, state):
        self.states.append(state)
        self.states.pop(0)
        self.poss.append(self.body.velocity)
        self.poss.pop(0)

    def get_state(self, L, R, LR, LM, RM, M, ALL, NONE):
        if L:
            return "L"
        if R:
            return "R"
        if LR:
            return "LR"
        if LM:
            return "LM"
        if RM:
            return "RM"
        if M:
            return "M"
        if ALL:
            return "ALL"
        if NONE:
            return "NONE"

    def goto_target(self):

        imp = (100, 100)

        rel_vec = self.camera_get_target()

        max_angle_dif = radians(10)

        def get_length(x, y):
            return sqrt(x * x + y * y)

        near_target_dist = (
            max(
                [
                    us.distance_range + get_length(*us.us_pos)
                    for us in self.ultrasounds.values()
                ]
            )
            * 1.2
        )

        close_target_dist = 3 * near_target_dist

        # print(near_target_dist, '<<<near')
        n_rel_vec = rel_vec.normalized()
        ang_vel = 0

        dets = self.ultrasound_detections()

        LR = dets == [True, False, True]
        L = dets == [True, False, False]
        R = dets == [False, False, True]
        LM = dets == [True, True, False]
        RM = dets == [False, True, True]
        M = dets == [False, True, False]
        ALL = all(dets)
        NONE = not any(dets)

        state = self.get_state(L, R, LR, LM, RM, M, ALL, NONE)
        self.add_state(state)
        # print(self.states)
        # print(self.poss)

        ALL_sum = sum(1 for s in self.states if s == "ALL")
        M_sum = sum(1 for s in self.states if s == "M")
        NONE_sum = sum(1 for s in self.states if s == "NONE")

        is_ALL = ALL_sum > self.state_count / 2
        is_M = M_sum > self.state_count / 2
        is_NONE = NONE_sum > self.state_count / 2

        if is_ALL:
            self.add_state("STUCK")
        if is_M:
            self.add_state("STUCK")

        is_stuck = "STUCK" in self.states and not "INIT" in self.states
        is_near = rel_vec.length < near_target_dist
        is_close = rel_vec.length < close_target_dist

        if is_close:
            # slow down on closing
            if not is_M and not is_ALL:
                # but not when totally obstacled around
                n_rel_vec = n_rel_vec * 0.5

        stuck_sum = 500
        sum_vec = Vec2d(0, 0)
        for p in self.poss:
            if p is not None:
                sum_vec = sum_vec + p
        # print(sum_vec)

        self.stuck_counter += int(is_stuck)
        if self.stuck_counter > 50:
            self.stuck_angle *= -1
            self.stuck_counter = 0

        if sum_vec.length < stuck_sum:
            # if not is_stuck and not is_near:
            if not is_near:
                if not is_NONE:
                    self.add_state("STUCK")
        #   else:
        #      self.stuck_angle *= -1
        # self.stuck_rel_vec = rel_vec
        # self.stuck_rel_vec.rotate(self.stuck_angle)

        assert len(dets) == 3
        # if us_count is not 3, following algorithm may missbehave

        is_stuck = "STUCK" in self.states and not "INIT" in self.states

        if is_stuck and not is_near:
            # rel_vec = self.stuck_rel_vec
            rel_vec.rotate_degrees(self.stuck_angle)

        if abs(rel_vec.angle) > max_angle_dif:
            ang_vel = -(rel_vec.angle) * 1

        if is_stuck:
            vel_vec = n_rel_vec
            self.control.go(vel_vec, ang_vel, self.stuck_angle)
            return

        if is_near:
            ang_vel = ang_vel * 5.5
            vel_vec = n_rel_vec * 0.5
            self.control.go(vel_vec, ang_vel)
        else:
            vel_vec = n_rel_vec
            if NONE or LR:
                self.control.go(vel_vec, ang_vel)
            elif ALL or M:
                # self.control.go(vel_vec, ang_vel, 'br')
                # self.control.go(Vec2d(0,0), 10)
                self.control.go(vel_vec, ang_vel, "right")
                return
            elif L or LM:
                self.control.go(vel_vec, ang_vel, "right")
                return
            elif R or RM:
                self.control.go(vel_vec, ang_vel, "left")
                return

