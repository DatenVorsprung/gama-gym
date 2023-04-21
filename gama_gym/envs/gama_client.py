from __future__ import annotations

import dataclasses
import json
from typing import Any

import websockets
from websockets.sync import client


class GamaClient:

    @dataclasses.dataclass
    class Parameter:
        type: str
        value: Any
        name: str

    def __init__(self, host: str, port: int):
        self._conn: websockets.ClientConnection = client.connect(f'ws://{host}:{port}', close_timeout=1.0)
        res = json.loads(self._conn.recv())
        if res['type'] != 'ConnectionSuccessful':
            raise ConnectionError(f'Connection failed. {res["type"]}: {res["message"]}')


    def load(self,
             model: str,
             experiment: str,
             console: bool = False,
             status: bool = False,
             dialog: bool = False,
             parameters: list[Parameter] = None,
             until: str = ''):
        parameters = parameters or []
        command = {
            'type': 'load',
            'model': model,
            'experiment': experiment,
            'console': console,
            'status': status,
            'dialog': dialog,
            'parameters': [p.__dict__ for p in parameters],
            'until': until
        }
        return self._send_command(command)

    def exit(self):
        command = {
            'type': 'exit'
        }
        return self._send_command(command)

    def play(self, exp_id: str, sync: bool = None):
        command = {
            'type': 'play',
            'exp_id': exp_id,
            'sync': sync
        }
        return self._send_command(command)

    def pause(self, exp_id: str):
        command = {
            'type': 'pause',
            'exp_id': exp_id
        }
        return self._send_command(command)

    def step(self, exp_id: str, nb_step: int = 1, sync: bool = False):
        command = {
            'type': 'step',
            'exp_id': exp_id,
            'nb_step': nb_step,
            'sync': sync
        }
        return self._send_command(command)

    def step_back(self, exp_id: str, nb_step: int = 1, sync: bool = False):
        command = {
            'type': 'stepBack',
            'exp_id': exp_id,
            'nb_step': nb_step,
            'sync': sync
        }
        return self._send_command(command)

    def stop(self, exp_id: str):
        command = {
            'type': 'stop',
            'exp_id': exp_id
        }
        return self._send_command(command)

    def reload(self, exp_id: str, parameters: list[Parameter] = None, until: str = ""):
        parameters = parameters or []
        command = {
            'type': 'reload',
            'exp_id': exp_id,
            'parameters': [p.__dict__ for p in parameters],
            'until': until
        }
        return self._send_command(command)

    def expression(self, exp_id: str, expression: str):
        command = {
            'type': 'expression',
            'exp_id': exp_id,
            'expr': expression
        }
        return self._send_command(command)

    def close(self):
        self._conn.close()

    def _send_command(self, command):
        self._conn.send(json.dumps(command))
        res = self._conn.recv()
        res = json.loads(res)
        if res['type'] == 'UnableToExecuteRequest':
            raise ValueError(res['content'])
        return res['content']

if __name__ == '__main__':
    client = GamaClient(host='localhost', port=6868)

    model = '/TouristFlow/TouristFlow.gaml'
    exp_id = client.load(model=model, experiment='Salzburghotelsmuseums')
    print('Loaded experiment: ', exp_id)
    res = client.expression(exp_id, 'length(species(people).population)')
    while int(res) == 0:
        client.step(exp_id=exp_id, sync=True)
        res = client.expression(exp_id, 'length(species(people).population)')

    obs = client.expression(exp_id=exp_id, expression='do get_observation;')
    response = client.step(exp_id=exp_id, sync=True)
    obs = client.expression(exp_id=exp_id, expression='do get_observation;')
    response = client.expression(exp_id=exp_id, expression='nb_cells')
    print('nb_cells: ', response)
    response = client.expression(exp_id=exp_id, expression='agents[0].actionspace')
    print('actspace: ', response)
    # client.exit()
    client.close()
