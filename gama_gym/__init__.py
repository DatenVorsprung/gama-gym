from gym.envs.registration import register

register(id='GamaEnv-v0', entry_point='gama_gym.envs:GamaEnv', max_episode_steps=10)
