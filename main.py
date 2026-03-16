from data import MarineEnvironment
from map import interactive_windy_pro
import numpy as np

if __name__ == "__main__":
    env = MarineEnvironment(res_x=50, res_y=50, seed=np.random.randint(0, 10000))
    interactive_windy_pro(env)
    