import gym
import gama_gym #TODO: think if we can get rid of this import in someway
import user_local_variables as lv

#Create the environment
env = gym.make('GamaEnv-v0',
             headless_directory      = lv.headless_dir,
             headless_script_path    = lv.run_headless_script_path,    
             gaml_experiment_path    = r"/home/mvinyalssal/code/gama-gym/samples/TCP_model_env_rc2.gaml",
             gaml_experiment_name    = "one_simulation",
             gama_server_url         = "localhost",
             gama_server_port        = 6868)

done = False
initial_observation = env.reset()
print('initial_observation ', initial_observation)
while not done:
    action = np.random.rand(1,5).flatten()
    next_observation, reward, done, info = env.step(action)
    print('done', done)
    done = False

