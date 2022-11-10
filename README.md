# gama-gym
## Installation instructions
- [ ] Python
- [ ] The following Python packages:

### Dependencies
### Install gama-gym package
Note: remember to activate your python virtual environment before installing the package

Once you cloned/downloaded the repository, from the root project directory:

```
pip install -e .
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
