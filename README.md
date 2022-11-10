# gama-gym
## Installation instructions

### Dependencies

* Gama (by now working with version GAMA_1.8.2_Linux_with_JDK_09.16.22_972c449b)
* Python
* The following Python packages:
  * gym==0.23.1

### Install gama-gym package


Clone/download the gama-gym repository in your computer:

```
git clone git@github.com:gama-platform/gama-gym.git {GAMA_GYM_DIR}
```


Then you can install it in your local project environment by calling:
Note: remember to activate your python virtual environment before installing the package

```
pip install -e {GAMA_GYM_DIR}
```

### Download Gama with JDK (Baptiste, JDK is required isnt?)
```
https://github.com/gama-platform/gama/releases/
```

Gama-gym uses Gama in headless mode so you would need to give execution rights to the headless directory. 
For example, in a linux environment:
```
chmod +x {GAMA_PATH}/headless/gama-headless.sh
```
## Basic usage
You can use gama-gym as any gym environment. You need to pass gama-gym configuration as following:
```
import gym
env = gym.make('GamaEnv-v0',
             headless_directory      = {GAMA_PATH}/headless, # Root directory for gama headless
             headless_script_path    = {GAMA_PATH}/headless/gama-headless.sh, # Path to the script that runs gama headless
             gaml_experiment_path    = {GAMA_MODEL_PATH}, # Path to gaml file containing the Gama simulation model to run
             gaml_experiment_name    = {EXPERIMENT_NAME}, # Name of the experiment to run as named in the Gama gaml model
             gama_server_url         = "localhost",
             gama_server_port        = 6868)

```

## Usage with rllib
In what follows we provide a brief example of how to use gama-gym with rllib.

```
import gym
from ray.rllib.agents.ppo import PPOTrainer #Import from rllib the algorithm you want to use, in this case PPO
from ray.tune.registry import register_env # Import for registering the environment
from gama_gym.envs import GamaEnv #Import the environment to use
```
