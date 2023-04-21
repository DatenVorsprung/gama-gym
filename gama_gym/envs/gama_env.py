from __future__ import annotations

import abc
from typing import Any, SupportsFloat
import gymnasium
from gymnasium.core import RenderFrame, ObsType, ActType

from gama_gym.envs.gama_client import GamaClient


class GamaEnv(abc.ABC, gymnasium.Env):

    def __init__(self,
                 host: str,
                 port: int,
                 gaml_file_path: str,
                 experiment_name: str,
                 n_steps: int = 1,
                 params: list[Any] = None) -> None:
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
        self.agents = self._client.expression(exp_id=self._exp_id, expression='agents')[1:-1].split(', ')

    def reset(self, *, seed: int | None = None, options: dict[str, Any] | None = None) -> tuple[
        ObsType, dict[str, Any]]:
        options = options or {}
        params = options.get('params', self._params)
        self._client.stop(exp_id=self._exp_id)
        self._client.reload(exp_id=self._exp_id, parameters=params)
        obs, _, _, _, info = self.read_state(exp_id=self._exp_id, client=self._client)
        return obs, info


    @abc.abstractmethod
    def read_state(self, exp_id: str, client: GamaClient) -> tuple[ObsType, SupportsFloat | dict, bool, bool, dict]:
        pass


    @abc.abstractmethod
    def apply_action(self, exp_id: str, client: GamaClient, action: ActType) -> None:
        pass


    def step(self, action: ActType) -> tuple[ObsType, SupportsFloat, bool, bool, dict[str, Any]]:
        self.apply_action(
            exp_id=self._exp_id,
            client=self._client,
            action=action
        )
        self._client.step(exp_id=self._exp_id, nb_step=self._n_steps, sync=True)
        obs, reward, done, truncated, info = self.read_state(exp_id=self._exp_id, client=self._client)
        return obs, reward, done, truncated, info


    def render(self) -> RenderFrame | list[RenderFrame] | None:
        pass


    def close(self):
        self._client.close()
