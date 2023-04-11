from ast import literal_eval
import asyncio
import json
import subprocess
from asyncio import Future

import gym
import time
import sys
import socket
from _thread import start_new_thread
import numpy as np
import numpy.typing as npt
from typing import Optional, Dict, List

from gama_client.command_types import CommandTypes
from gym import spaces
import psutil
from gama_client.base_client import GamaBaseClient
import yaml

import nest_asyncio

nest_asyncio.apply()


class GamaEnv(gym.Env):
    # USER LOCAL VARIABLES
    headless_dir: str  # Root directory for gama headless
    run_headless_script_path: str  # Path to the script that runs gama headless
    gaml_file_path: str  # Path to the gaml file containing the experiment/simulation to run
    experiment_name: str  # Name of the experiment to run

    # ENVIRONMENT CONSTANTS
    max_episode_steps: int = 11

    # Gama-server control variables
    gama_server_url: str = ""
    gama_server_port: int = -1
    gama_server_handler: GamaBaseClient = None
    gama_server_sock_id: str = ""  # represents the current socket used to communicate with gama-server
    gama_server_exp_id: str = ""  # represents the current experiment being manipulated by gama-server
    gama_server_connected: asyncio.Event = None
    gama_server_event_loop = None
    gama_server_pid: int = -1

    # Simulation execution variables
    gama_socket = None
    gama_simulation_as_file = None  # For some reason the typing doesn't work
    gama_simulation_connection = None  # Resulting from socket create connection

    # Futures for gama client events
    experiment_future: Future
    play_future: Future
    pause_future: Future
    expression_future: Future
    step_future: Future
    stop_future: Future

    state: dict

    def __init__(self, headless_directory: str, headless_script_path: str,
                 gaml_experiment_path: str, gaml_experiment_name: str,
                 gama_server_url: str, env_yaml_config_path: str, gama_server_port: int,
                 gama_experiment_params: Optional[List[Dict]] = None):

        self.headless_dir = headless_directory
        self.run_headless_script_path = headless_script_path
        self.gaml_file_path = gaml_experiment_path
        self.experiment_name = gaml_experiment_name
        self.gama_server_url = gama_server_url
        self.gama_server_port = gama_server_port
        self.experiment_params = gama_experiment_params or []

        self.action_variables = None
        self.observation_space = None
        self._config = None
        self._load_config(env_yaml_config_path)
        for key in ['observation', 'action']:
            self._make_gym_spaces(key=key)

        # setting an event loop for the parallel processes
        self.gama_server_event_loop = asyncio.get_running_loop()
        asyncio.set_event_loop(self.gama_server_event_loop)
        self.gama_server_connected = asyncio.Event()

        self.init_gama_server()

        print("END INIT")

    async def message_handler(self, message: Dict):
        print("received", message)
        if "command" in message:
            if message["command"]["type"] == CommandTypes.Load.value:
                self.experiment_future.set_result(message)
            elif message["command"]["type"] == CommandTypes.Play.value:
                self.play_future.set_result(message)
            elif message["command"]["type"] == CommandTypes.Pause.value:
                self.pause_future.set_result(message)
            elif message["command"]["type"] == CommandTypes.Expression.value:
                self.expression_future.set_result(message)
            elif message["command"]["type"] == CommandTypes.Step.value:
                self.step_future.set_result(message)
            elif message["command"]["type"] == CommandTypes.Stop.value:
                self.stop_future.set_result(message)
            else:
                raise Exception("Unknown command type")

    def run_gama_server(self):
        cmd = f"cd \"{self.headless_dir}\" && \"{self.run_headless_script_path}\" -v -socket {self.gama_server_port}"
        print("running gama headless with command: ", cmd)
        server = subprocess.Popen(cmd, shell=True)
        self.gama_server_pid = server.pid
        print("gama server pid:", self.gama_server_pid)

    def init_gama_server(self):

        # Run gama server from the filesystem
        start_new_thread(self.run_gama_server, ())

        # try to connect to gama-server
        self.gama_server_handler = GamaBaseClient(self.gama_server_url, self.gama_server_port, self.message_handler)
        self.gama_server_sock_id = ""
        for i in range(30):
            try:
                self.gama_server_event_loop.run_until_complete(asyncio.sleep(2))
                print("try to connect")
                self.gama_server_event_loop.run_until_complete(self.gama_server_handler.connect())
                if self.gama_server_handler.socket_id != "":
                    self.gama_server_sock_id = self.gama_server_handler.socket_id
                    print("connection successful", self.gama_server_sock_id)
                    break
            except Exception as e:
                print("Connection failed")
                print(e)

        if self.gama_server_sock_id == "":
            print("unable to connect to gama server")
            sys.exit(-1)

        self.gama_server_connected.set()

    def step(self, action):
        try:
            print("STEP")
            # sending actions
            str_action = json.dumps(action) + "\n"
            print("model sending action:", str_action)
            print(self.gama_simulation_connection)

            self.gama_simulation_as_file.write(str_action)
            self.gama_simulation_as_file.flush()
            print("model sent action, now waiting for reward")
            # we wait for the reward
            policy_reward = self.gama_simulation_as_file.readline()
            reward = float(policy_reward)

            print("model received reward:", policy_reward, " as a float: ", reward)
            self.state, end = self.read_observations()
            print("observations received", self.state, end)
            # If it was the final step, we need to send a message back to the simulation once everything done to acknowledge that it can now close
            if end:
                self.gama_simulation_as_file.write("END\n")
                self.gama_simulation_as_file.flush()
                self.gama_simulation_as_file.close()
                self.gama_simulation_connection.shutdown(socket.SHUT_RDWR)
                self.gama_simulation_connection.close()
                self.gama_socket.shutdown(socket.SHUT_RDWR)
                self.gama_socket.close()
        except ConnectionResetError:
            print("connection reset, end of simulation")
        except Exception:
            print("EXCEPTION during execution")
            print(sys.exc_info()[0])
            sys.exit(-1)
        print("END STEP")
        truncated = False
        return self.state, reward, end, truncated, {}

    # Must reset the simulation to its initial state
    # Should return the initial observations
    def reset(self, *, seed: Optional[int] = None, options: Optional[dict] = None):
        print("RESET")
        print("self.gama_simulation_as_file", self.gama_simulation_as_file)
        print("self.gama_simulation_connection", self.gama_simulation_connection)
        super().reset(seed=seed, options=options)
        # Check if the environment terminated
        if self.gama_simulation_connection is not None:
            print("self.gama_simulation_connection.fileno()",
                  self.gama_simulation_connection.fileno())
            if self.gama_simulation_connection.fileno() != -1:
                self.gama_simulation_connection.shutdown(socket.SHUT_RDWR)
                self.gama_simulation_connection.close()
                self.gama_socket.shutdown(socket.SHUT_RDWR)
                self.gama_socket.close()
        if self.gama_simulation_as_file is not None:
            self.gama_simulation_as_file.close()
            self.gama_simulation_as_file = None

        tic_setting_gama = time.time()

        # Starts the simulation and get initial state
        self.gama_server_event_loop.run_until_complete(self.run_gama_simulation())

        self.wait_for_gama_to_connect()

        self.state, end = self.read_observations()
        print('\t', 'setting up gama', time.time() - tic_setting_gama)
        print('after reset self.state', self.state)
        print('after reset end', end)
        print("END RESET")
        return self.state, {}

    def clean_subprocesses(self):
        if self.gama_server_pid > 0:
            parent = psutil.Process(self.gama_server_pid)
            for child in parent.children(recursive=True):  # or parent.children() for recursive=False
                child.kill()
            parent.kill()

    def __del__(self):
        self.clean_subprocesses()

    async def close(self):
        await self.gama_server_handler.exit()

    # Init the server + run gama
    async def run_gama_simulation(self):

        # Waiting for the gama_server websocket to be initialized
        await self.gama_server_connected.wait()

        print("creating TCP server")
        sim_port = self.init_server_simulation_control()

        # initialize the experiment
        try:
            print("asking gama-server to start the experiment")
            self.experiment_future = asyncio.get_running_loop().create_future()
            await self.gama_server_handler.load(self.gaml_file_path, self.experiment_name,
                                                True, True, True,
                                                parameters=[{"type": "int", "name": "port",
                                                             "value": sim_port}] + self.experiment_params)
            gama_result = await self.experiment_future
            self.gama_server_exp_id = gama_result["content"]

        except Exception as e:
            print("Unable to init the experiment: ", self.gaml_file_path, self.experiment_name, e)
            sys.exit(-1)

        if self.gama_server_exp_id == "" or self.gama_server_exp_id is None:
            print("Unable to compile or initialize the experiment")
            sys.exit(-1)

        print("asking gama-server to play")
        self.play_future = asyncio.get_running_loop().create_future()
        await self.gama_server_handler.play(self.gama_server_exp_id, socket_id=self.gama_server_sock_id)
        play_result = await self.play_future
        if not play_result['type'] == 'CommandExecutedSuccessfully':
            print("Unable to run the experiment")
            sys.exit(-1)
        print("experiment started")

    def init_server_simulation_control(self) -> int:
        """Initialize the socket to communicate with gama

        Returns:
            int: _description_
        """
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print("Socket successfully created")

        s.bind(('', 0))  # localhost + port given by the os
        port = s.getsockname()[1]
        print(f"Socket bound to {port}")

        s.listen()
        print("Socket started listening")

        self.gama_socket = s
        return port

    def wait_for_gama_to_connect(self):
        """Connect with the current running gama simulation
        """
        # The server is waiting for clients to connect
        self.gama_simulation_connection, addr = self.gama_socket.accept()
        print("gama connected:", self.gama_simulation_connection, addr)
        self.gama_simulation_as_file = self.gama_simulation_connection.makefile(mode='rw')

    def read_observations(self):
        """Reads the observations from the simulation

        Returns:
            _type_: _description_
        """
        received_observations: str = self.gama_simulation_as_file.readline()
        print("model received:", received_observations)

        over = "END" in received_observations
        obs = literal_eval(received_observations.replace("END", ""))
        return obs, over

    def _load_config(self, env_yaml_config_path: str):
        with open(env_yaml_config_path, 'r') as file:
            self._config = yaml.safe_load(file)
        self.observation_variables = self._config['observation']
        self.action_variables = self._config['action']
        # self.context_variables = setting_dict[setting]['context']
        # if self.experiment_number is None:
        #  self.experiment_number = setting_dict[setting]['experiment_number']

    def _make_gym_spaces(self, key):
        key_spaces = {}
        if key == 'action':
            key_variables = self.action_variables
        elif key == 'observation':
            key_variables = self.observation_variables
        else:
            raise ValueError('"key" parameter must be in ["observation", "action"]')

        if not key_variables:
            return {}

        key_data = self._config[key]

        for key_variable in key_variables:
            key_variable_dic = key_data[key_variable]
            if 'type' not in [*key_variable_dic]:
                raise ValueError(f'"type" must be specified for {key} variable "{key_variable}"')
            type_ = key_variable_dic['type']
            if type_ == 'float' or type_ == 'int':
                if ('high' not in [*key_variable_dic]) or ('low' not in [*key_variable_dic]):
                    raise ValueError(f'"high" and "low" must be specified for {key} variable "{key_variable}"')
                low = key_variable_dic['low']
                high = key_variable_dic['high']
                shape = literal_eval(key_variable_dic.get('shape', "()"))
                space = spaces.Box(low=low, high=high, shape=shape, dtype=type_)
            elif type_ == 'discrete':
                if 'size' not in [*key_variable_dic]:
                    raise ValueError(f'"size" must be specified for {key} variable "{key_variable}"')
                size = key_variable_dic['size']
                space = spaces.Discrete(size)

            if type_ == 'array':
                if 'subtype' not in [*key_variable_dic]:
                    raise ValueError(f'"subtype" must be specified for {key} variable "{key_variable}"')
                subtype = key_variable_dic['subtype']
                if 'size' not in [*key_variable_dic]:
                    raise ValueError(f'"size" must be specified for {key} variable "{key_variable}"')
                size = key_variable_dic['size']
                if subtype == 'float':
                    if ('high' not in [*key_variable_dic]) or ('low' not in [*key_variable_dic]):
                        raise ValueError(f'"high" and "low" must be specified for {key} variable "{key_variable}"')
                    low = key_variable_dic['low']
                    high = key_variable_dic['high']
                    space = spaces.Box(low=low, high=high, shape=(size,))
                elif subtype == 'discrete':
                    atomic_spaces = []
                    if 'subsize' not in [*key_variable_dic]:
                        raise ValueError(f'"subsize" must be specified for {key} variable "{key_variable}"')
                    sub_size = key_variable_dic['subsize']
                    for element in range(size):
                        atomic_spaces.append(spaces.Discrete(sub_size))
                    space = spaces.Tuple(atomic_spaces)
                elif subtype == 'int':
                    if ('high' not in [*key_variable_dic]) or ('low' not in [*key_variable_dic]):
                        raise ValueError(f'"high" and "low" must be specified for {key} variable "{key_variable}"')
                    low = key_variable_dic['low']
                    high = key_variable_dic['high']
                    atomic_spaces = []
                    sub_size = high - low + 1
                    for element in range(size):
                        atomic_spaces.append(spaces.Discrete(sub_size))
                    space = spaces.Tuple(atomic_spaces)
                else:
                    raise ValueError(
                        f'{key} variable {key_variable} subtype {subtype} not in {["float", "int", "discrete"]}')

            key_spaces[key_variable] = space
            if key == 'observation':
                self.observation_space = spaces.Dict(key_spaces)
            else:
                self.action_space = spaces.Dict(key_spaces)
