from __future__ import annotations

import abc
from typing import Any, SupportsFloat, Callable

import gymnasium
from gymnasium.core import RenderFrame, ObsType, ActType

from gama_gym.envs.gama_client import GamaClient

ObservationFn = Callable[[str, GamaClient], tuple[ObsType, dict]]
StepFn = Callable[[ObsType, ActType, dict], tuple[ObsType, dict[str, SupportsFloat], bool, dict]]


class GamaEnv(abc.ABC, gymnasium.Env):

    def __init__(self,
                 host: str,
                 port: int,
                 gaml_file_path: str,
                 experiment_name: str,
                 obs_fn: ObservationFn,
                 step_fn: StepFn,
                 n_steps: int = 1,
                 params: list[Any] = None) -> None:
        self._params = params or []
        self._obs_fn = obs_fn
        self._step_fn = step_fn
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

        self.agents = self._client.expression(exp_id=self._exp_id, expression='agents')[1:-1].split(', ')

    def reset(self, *,
              seed: int | None = None,
              options: dict[str, Any] | None = None) \
            -> tuple[dict[str, ObsType], dict[str, Any]]:
        options = options or {}
        params = options.get('params', self._params)
        self._client.stop(exp_id=self._exp_id)
        self._client.reload(exp_id=self._exp_id, parameters=params)
        obs, info = self._obs_fn(self._exp_id, self._client)
        return obs, info

    @abc.abstractmethod
    def apply_action(self, exp_id: str, client: GamaClient, action: ActType) -> None:
        pass

    def step(self, action: ActType) -> tuple[ObsType, dict[str, SupportsFloat], bool, bool, dict[str, Any]]:
        obs, rewards, done, info = self._step_fn(self._exp_id, self._client, action)
        self._client.step(exp_id=self._exp_id, nb_step=self._n_steps, sync=True)
        return obs, rewards, done, False, info

    def render(self) -> RenderFrame | list[RenderFrame] | None:
        pass

    def close(self):
        self._client.close()
