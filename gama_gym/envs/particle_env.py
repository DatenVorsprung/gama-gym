from __future__ import annotations

from typing import SupportsFloat, Any

import gymnasium.spaces
import numpy as np
from gymnasium.core import ActType, ObsType
from gama_gym.envs.gama_client import GamaClient
from gama_gym.envs.gama_env import GamaEnv


class ParticleEnv(GamaEnv):

    def __init__(self,
                 host: str,
                 port: int,
                 gaml_file_path: str,
                 experiment_name: str,
                 n_steps: int = 1,
                 n_particles: int = 10) -> None:
        number_of_particles = GamaClient.Parameter(type='int', value=n_particles, name='number_of_particles')

        super().__init__(host, port, gaml_file_path, experiment_name, n_steps, [number_of_particles])
        self.observation_space = gymnasium.spaces.Dict(dict(
            (agent, gymnasium.spaces.Box(low=np.array([-2.5, -2.5, -2.5]), high=np.array([2.5, 2.5, 2.5])))
            for agent
            in self.agents
        ))
        self.action_space = gymnasium.spaces.Dict(dict(
            (agent, gymnasium.spaces.Box(low=np.array([-5, 0]), high=np.array([5, 359])))
            for agent
            in self.agents
        ))

    def read_state(self, exp_id: str, client: GamaClient) -> tuple[ObsType, SupportsFloat | dict, bool, bool, dict]:
        obs = {}
        for i in range(len(self.agents)):
            o = client.expression(exp_id=exp_id, expression=f'agents[{i}].location')
            obs[f'cell{i}'] = np.array([float(c) for c in o[1:-1].split(',')])
        return obs, 0, False, False, dict()

    def apply_action(self, exp_id: str, client: GamaClient, action: ActType) -> None:
        for agent, act in action.items():
            client.expression(exp_id, expression='do cell0.move(0.4,50)')


if __name__ == '__main__':
    env = ParticleEnv(
        n_particles=10,
        host='localhost',
        port=6868,
        gaml_file_path='/home/axel/Projects/gama-gym/samples/particles.gaml',
        experiment_name='particles_experiment'
    )
    obs, info = env.reset()
    action = env.action_space.sample()
    obs, reward, done, truncated, info = env.step(action)
    print(obs)
