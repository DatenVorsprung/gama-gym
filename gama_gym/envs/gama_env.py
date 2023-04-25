from __future__ import annotations

import abc
from typing import Any, SupportsFloat, Callable

import gymnasium
from gymnasium.core import RenderFrame, ObsType, ActType

from gama_gym.envs.gama_client import GamaClient


class ABCGamaEnv(abc.ABC, gymnasium.Env):

    def __init__(self,
                 host: str,
                 port: int,
                 gaml_file_path: str,
                 experiment_name: str,
                 n_steps: int = 1,
                 max_steps: int = None,
                 params: list[Any] = None) -> None:
        self._steps = 0
        self._max_steps = max_steps
        self._params = params or []
        self._client = GamaClient(host=host, port=port)
        self._gaml_file_path = gaml_file_path
        self._experiment_name = experiment_name
        self._exp_id = None
        self._n_steps = n_steps
        self._exp_id = self._client.load(
            model=self._gaml_file_path,
            experiment=self._experiment_name,
            parameters=self._params,
            console=False,
            status=False,
            dialog=False
        )

    @property
    def client(self):
        return self._client

    @property
    def experiment_id(self):
        return self._exp_id


    @property
    @abc.abstractmethod
    def observation_space(self):
        pass

    @property
    @abc.abstractmethod
    def action_space(self):
        pass

    @abc.abstractmethod
    def get_observation(self) -> dict[str, ObsType]:
        pass

    @abc.abstractmethod
    def get_reward(self, last_obs: ObsType, last_action: ActType) -> dict[str, SupportsFloat]:
        pass

    @abc.abstractmethod
    def has_terminated(self, last_obs: ObsType, last_action: ActType) -> bool:
        pass

    @abc.abstractmethod
    def apply_action(self, action: ActType) -> None:
        pass

    def reset(self, *,
              seed: int | None = None,
              options: dict[str, Any] | None = None) \
            -> tuple[dict[str, ObsType], dict[str, Any]]:
        options = options or {}
        params = options.get('params', self._params)
        self._client.stop(exp_id=self._exp_id)
        self._client.reload(exp_id=self._exp_id, parameters=params)
        obs = self.get_observation()
        return obs, {}

    def step(self, action: ActType) -> tuple[ObsType, dict[str, SupportsFloat], bool, bool, dict[str, Any]]:
        self.apply_action(action)
        self.client.step(
            exp_id=self._exp_id,
            nb_step=self._n_steps,
            sync=True
        )
        self._steps += 1
        obs = self.get_observation()
        reward = self.get_reward(obs, action)
        terminated = self.has_terminated(obs, action)
        truncated = self._steps > self._max_steps if self._max_steps else False
        return obs, reward, terminated, truncated, {}

    def render(self) -> RenderFrame | list[RenderFrame] | None:
        pass

    def close(self):
        self._client.close()
