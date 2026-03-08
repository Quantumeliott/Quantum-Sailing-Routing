from data import MarineEnvironment
from visuel import interactive_windy_pro
import numpy as np

if __name__ == "__main__":
    env = MarineEnvironment(seed=np.random.randint(0, 10000))
    interactive_windy_pro(env, time_max=150)