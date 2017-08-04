import gym
import numpy as np
import cv2
from collections import deque
from gym import spaces

from dqn.model import DoubleDQN

def get_env(task, seed):
    env_id = task.env_id
    env = gym.make(env_id)
    env.seed(seed)

    env = ProcessFrame84(env)

    return env


def _process_frame84(frame):
    img = np.reshape(frame, [210, 160, 3]).astype(np.float32)
    img = img[:, :, 0] * 0.299 + img[:, :, 1] * 0.587 + img[:, :, 2] * 0.114
    resized_screen = cv2.resize(img, (84, 110), interpolation=cv2.INTER_LINEAR)
    x_t = resized_screen[18:102, :]
    x_t = np.reshape(x_t, [84, 84, 1])
    return x_t.astype(np.uint8)


class ProcessFrame84(gym.Wrapper):
    def __init__(self, env=None):
        super(ProcessFrame84, self).__init__(env)
        self.observation_space = spaces.Box(low=0, high=255, shape=(84, 84, 1))

    def _step(self, action):
        obs, reward, done, info = self.env.step(action)
        return _process_frame84(obs), reward, done, info

    def _reset(self):
        return _process_frame84(self.env.reset())


def atari_main():
    # Get Atari games.
    benchmark = gym.benchmark_spec('Atari40M')

    # Change the index to select a different game.
    task = benchmark.tasks[3]
    print('task: ', task.env_id, 'max steps: ', task.max_timesteps)

    # Run training
    seed = 0 # Use a seed of zero (you may want to randomize the seed!)
    env = get_env(task, seed)

    last_obs = env.reset()

    dqn = DoubleDQN(image_shape=(84, 84, 1), num_actions=env.action_space.n)

    for step in range(1000):
        # env.render()
        action = dqn.choose_action(step, last_obs)
        obs, reward, done, info = env.step(action)
        dqn.learn(step, last_obs, action, reward, done, info)
        if done:
            last_obs = env.reset()
        else:
            last_obs = obs

if __name__ == "__main__":
    atari_main()
