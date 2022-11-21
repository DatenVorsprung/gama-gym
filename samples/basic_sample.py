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
             gaml_experiment_name    = "one_simulation",
             gama_server_url         = "localhost",
             gama_server_port        = 6868)
    # Test that run 2 complete episodes with the same environment
    n_iters = 2
    for iter in range(n_iters):
        initial_observation = env.reset()
        print('initial_observation ', initial_observation)
        done = False
        while not done:
            action = np.random.rand(1,5).flatten()
            next_observation, reward, done, info = env.step(action)
            print('done ', done)
finally:
    env.close()
