from __future__ import annotations

import asyncio
import json
from asyncio import sleep
from typing import Any, SupportsFloat
from gama_client.base_client import GamaBaseClient
import gymnasium
from gymnasium.core import RenderFrame, ObsType, ActType

import websockets
from websockets.sync import client

from gama_gym.envs.gama_client import GamaClient


class GamaEnv(gymnasium.Env):

    def __init__(self, host: str, port: int, gaml_file_path: str, experiment_name: str, params: list[Any] = None) -> None:
        self._params = params or []
        self._client = GamaClient(host=host, port=port)
        self._exp_id = self._client.load(
            model=gaml_file_path,
            experiment=experiment_name,
            parameters=params
        )

        self._gaml_file_path = gaml_file_path
        self._experiment_name = experiment_name

    def reset(self, *, seed: int | None = None, options: dict[str, Any] | None = None) -> tuple[
        ObsType, dict[str, Any]]:

        return response, {}

    def step(self, action: ActType) -> tuple[ObsType, SupportsFloat, bool, bool, dict[str, Any]]:
        pass

    def render(self) -> RenderFrame | list[RenderFrame] | None:
        pass

    def close(self):
        super().close()


if __name__ == '__main__':
    env = GamaEnv(
        host='localhost',
        port=6868,
        gaml_file_path='samples/particles.gaml',
        experiment_name='Tuto3D'
    )
    obs, info = env.reset()
    print(obs)
