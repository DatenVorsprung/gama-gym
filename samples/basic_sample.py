import asyncio
import os

import gymnasium
import numpy as np

import user_local_variables as lv


async def main():
    CURRENT_DIRECTORY = os.path.abspath(os.getcwd())

    env = gymnasium.make('GamaEnv-v0',
                         headless_directory=lv.headless_dir,
                         headless_script_path=lv.run_headless_script_path,
                         gaml_experiment_path=CURRENT_DIRECTORY + r"/TCP_model_env_rc2.gaml",
                         env_yaml_config_path=CURRENT_DIRECTORY + r"/env_config.yml",
                         gaml_experiment_name="one_simulation",
                         gama_server_url="localhost",
                         gama_server_port=6868,
                         disable_env_checker=True)
    # Test that run 2 complete episodes with the same environment
    n_iters = 2
    for iter in range(n_iters):
        initial_observation = env.reset()
        print('initial_observation ', initial_observation)
        done = False
        while not done:
            action = np.random.rand(1, 5).flatten()
            next_observation, reward, done, term, info = env.step(action)
            print('done ', done)


if __name__ == "__main__":
    asyncio.run(main())
