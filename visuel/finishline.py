from matplotlib.patches import Rectangle
import numpy as np

def finish_line(ax):
        rect = Rectangle((35, 39), 0.5, 10, facecolor='black', hatch='////', alpha=1)
        from matplotlib.transforms import Affine2D
        rot = Affine2D().rotate(np.pi/4).translate(90, 40)
        rect.set_transform(rot + ax.transData)
        ax.add_patch(rect)