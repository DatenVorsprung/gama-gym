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
from gama_gym.envs import GamaEnv #Import the environment to use
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

# register the custom environment in ray
env = 'GamaEnv-v0'
register_env(env, lambda config: GamaEnv(headless_directory      = {HEADLESS_DIR},
                          headless_script_path    = {HEADLESS_SCRIPT_PATH},
                          gaml_experiment_path    = {GAML_FILE_PATH},
                          gaml_experiment_name    = {EXPERIMENT_NAME},
                          gama_server_url         = "localhost",
                          gama_server_port        = 6868,
                          )             )
# Create our RLlib Trainer.
config = {
   "env": "GamaEnv-v0", # Environment (RLlib understands openAI gym registered strings),
   "num_workers": 1,    # Use environment workers (aka "rollout workers") that parallely collect samples from their own environment clone(s).
   "framework": "tf",   # Change this to "framework: torch", if you are using PyTorch. Also, use "framework: tf2" for tf2.x eager execution.
   "model": {
         "fcnet_hiddens": [32],
         "fcnet_activation": "relu",
         }, # Tune default model given the environment's observation- and action spaces.
   "rollout_fragment_length": 20,
   "train_batch_size": 20,
   "sgd_minibatch_size": 10,
   }
trainer = PPOTrainer(config=config)

# Run it for n training iterations. A training iteration includes
# parallel sample collection by the environment workers as well as
# loss calculation on the collected batch and a model update.
for _ in range(3):
   # Perform one iteration of training the policy with PPO
   result = trainer.train()
   print('result')
   print(result)


```
