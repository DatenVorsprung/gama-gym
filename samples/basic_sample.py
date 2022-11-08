import gym
import gama_gym #TODO: think if we can get rid of this import in someway
#Create the environment
env = gym.make('GamaEnv-v0',
             headless_directory      = r"/home/mvinyalssal/Documents/GAMA_1.8.2_Linux_with_JDK_11.08.22_a02b4025/headless",
             headless_script_path    = r"/home/mvinyalssal/Documents/GAMA_1.8.2_Linux_with_JDK_11.08.22_a02b4025/headless/gama-headless.sh",    
             gaml_experiment_path    = "TCP_model_env_rc2.gaml",
             gaml_experiment_name    = "one_simulation",
             gama_server_url         = "localhost",
             gama_server_port        = 6868)
