# gama-gym
## Installation instructions
Note: remember to activate your python virtual environment before installing the package

From the root project directory:

```
pip install -e .
```
## Basic usage
You can use gama-gym as any gym environment. You need to pass gama-gym configuration as following:
```
import gym
env = gym.make('GamaEnv-v0',
             headless_directory      = headless_dir,
             headless_script_path    = run_headless_script_path,
             gaml_experiment_path    = gaml_file_path,
             gaml_experiment_name    = experiment_name,
             gama_server_url         = "localhost",
             gama_server_port        = 6868)

env_args = {
    'run_dssat_location': '/opt/dssat_pdi/run_dssat',  # assuming (modified) DSSAT has been installed in /opt/dssat_pdi
    'log_saving_path': './logs/dssat-pdi.log',  # if you want to save DSSAT outputs for inspection
    # 'mode': 'irrigation',  # you can choose one of those 3 modes
    # 'mode': 'fertilization',
    'mode': 'all',
    'seed': 123456,
    'random_weather': True,  # if you want stochastic weather
}
env = gym.make('gym_dssat_pdi:GymDssatPdi-v0', **env_args)
```
