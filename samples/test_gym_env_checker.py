import gym
from gym.utils.env_checker import check_env
from gama_gym.envs import GamaEnv  # TODO: think if we can get rid of this import in someway
import user_local_variables as lv
import os
import asyncio

CURRENT_DIRECTORY = os.path.abspath(os.getcwd())


async def main():
    env = None
    try:
        # Create the environment
        env = gym.make('GamaEnv-v0',
                       headless_directory=lv.headless_dir,
                       headless_script_path=lv.run_headless_script_path,
                       gaml_experiment_path=CURRENT_DIRECTORY + r"/TCP_model_env_rc2.gaml",
                       env_yaml_config_path=CURRENT_DIRECTORY + r"/env_config.yml",
                       gaml_experiment_name="one_simulation",
                       gama_server_url="localhost",
                       gama_server_port=6868)
        # Use the gym checker to perform a sanity check to make sure that it conforms to the API
        check_env(env)
        print("Check successful!")
    finally:
        if env is not None:
            env.close()


if __name__ == '__main__':
    asyncio.run(main())
