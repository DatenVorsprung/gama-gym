import gym
import gama_gym #TODO: think if we can get rid of this import in someway
import user_local_variables as lv

#Create the environment
env = gym.make('GamaEnv-v0',
             headless_directory      = lv.headless_dir,
             headless_script_path    = lv.run_headless_script_path,    
             gaml_experiment_path    = "TCP_model_env_rc2.gaml",
             gaml_experiment_name    = "one_simulation",
             gama_server_url         = "localhost",
             gama_server_port        = 6868)
