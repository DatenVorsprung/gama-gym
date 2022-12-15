import gym
from gama_gym.envs import GamaEnv #TODO: think if we can get rid of this import in someway
import user_local_variables as lv
import os
import numpy as np

CURRENT_DIRECTORY = os.path.abspath(os.getcwd())

try:
    #Create the environment
    env = gym.make('GamaEnv-v0',
             headless_directory      = lv.headless_dir,
             headless_script_path    = lv.run_headless_script_path,    
             gaml_experiment_path    = CURRENT_DIRECTORY+r"/TCP_model_env_rc2.gaml",
             env_yaml_config_path    = CURRENT_DIRECTORY+r"/env_config.yml",
             gaml_experiment_name    = "one_simulation",
             gama_server_url         = "localhost",
             gama_server_port        = 6868)

    # Evaluate null policy
    print('Evaluating null policy...')
    null_returns = evaluate(null_policy)
    print('Done null_returns', null_returns)
finally:
    env.close()

def null_policy(obs):
    '''
    Do not apply any action
    '''
    return { "theta_economy": 0, "theta_management": 0, "f_management": 0, "theta_environment": 0, "f_environment":0 }

def evaluate(policy, n_episodes=10):
    '''evaluates a policy for n_episodes episodes'''
    returns = [None] * n_episodes

    for episode in range(n_episodes):
        done = False
        obs = env.reset()
        ep_return = 0

        while not done:
            action = policy(obs)
            obs, reward, done, _ = env.step(action)
            if reward is not None:
                ep_return += reward

        returns[episode] = ep_return

    return returns
