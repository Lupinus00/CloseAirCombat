import math
import yaml
import os
import pdb
import numpy as np
from collections import OrderedDict
from gym import spaces
from .selfplay_task import BaseTask
from ..core.catalog import Catalog as c
from ..reward_functions import AltitudeReward, MissileAttackReward, PostureReward, RelativeAltitudeReward, SmoothActionReward
from ..termination_conditions import ExtremeState, LowAltitude, Overload, ShootDown, Timeout
from ..utils.utils import lonlat2dis, get_AO_TA_R


class SelfPlayWithMissileTask(BaseTask):
    def __init__(self, config: str):
        super().__init__(config)

        self.reward_functions = [
            MissileAttackReward(self.config),
            AltitudeReward(self.config),
            PostureReward(self.config),
            RelativeAltitudeReward(self.config),
            SmoothActionReward(self.config),
        ]

        self.termination_conditions = [
            ShootDown(self.config),
            ExtremeState(self.config),
            Overload(self.config),
            LowAltitude(self.config),
            Timeout(self.config),
        ]

        self.bloods = dict([(agent, 100) for agent in self.config.init_config.keys()])

    def init_variables(self):
        self.state_var = [
            c.position_long_gc_deg,
            c.position_lat_geod_deg,
            c.position_h_sl_ft,
            c.attitude_roll_rad,
            c.attitude_pitch_rad,
            c.attitude_heading_true_rad,
            c.velocities_v_north_fps,
            c.velocities_v_east_fps,
            c.velocities_v_down_fps,
            c.velocities_vc_fps,
            c.accelerations_n_pilot_x_norm,
            c.accelerations_n_pilot_y_norm,
            c.accelerations_n_pilot_z_norm,
        ]
        self.action_var = [
            c.fcs_aileron_cmd_norm,                 # [-1., 1.]    spaces.Discrete(41)
            c.fcs_elevator_cmd_norm,                # [-1., 1.]    spaces.Discrete(41)
            c.fcs_rudder_cmd_norm,                  # [-1., 1.]    spaces.Discrete(41)
            c.fcs_throttle_cmd_norm,                # [0.4, 0.9]    spaces.Discrete(30)
        ]
        self.render_var = [
            c.position_long_gc_deg,
            c.position_lat_geod_deg,
            c.position_h_sl_ft,
            c.attitude_roll_rad,
            c.attitude_pitch_rad,
            c.attitude_heading_true_rad,
        ]

    def get_action_space(self):
        act_space = spaces.Dict(
            OrderedDict({
                "aileron": spaces.Discrete(41),
                "elevator": spaces.Discrete(41),
                'rudder': spaces.Discrete(41),
                "throttle": spaces.Discrete(30),
            }))
        return act_space

    def get_observation_space(self):
        space = OrderedDict()
        for fighter_name in list(self.config.init_config.keys()):
            space[fighter_name] = spaces.Dict(
                OrderedDict({
                    'ego_info': spaces.Box(low=-10, high=10., shape=(22,)),
                }))
        return spaces.Dict(space)

    def reset(self, env):
        """Task-specific reset, include reward function reset.

        Must call it after `env.get_observation()`
        """
        self.bloods = dict([(agent, 100) for agent in env.agent_names])
        return super().reset(env)

    def get_reward(self, env, agent_id, info={}):
        """
        Must call it after `env.get_observation()`
        """
        return super().get_reward(env, agent_id, info)

    def get_termination(self, env, agent_id, info={}):
        return super().get_termination(env, agent_id, info)
