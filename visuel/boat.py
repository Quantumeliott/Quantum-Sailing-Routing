from matplotlib.patches import Polygon
import numpy as np

def init_boats(x, y, boats, ax, a_b=0):
        for i, b in enumerate(boats):
            b['hull'] = Polygon([[0,0], [0,0], [0,0]], closed=True, facecolor=b['color'], zorder=10+i)
            b['sail'] = Polygon([[0,0], [0,0], [0,0]], closed=True, facecolor='white', zorder=10+i)
            ax.add_patch(b['hull'])
            ax.add_patch(b['sail'])
            update_boat(i, x, y, a_b, boats)

def update_boat(boat_id, x, y, a_b, boats):
    hull_coords = [
        (x, y),
        (x + 3*np.cos(a_b+0.3), y + 3*np.sin(a_b+0.3)),
        (x + 3*np.cos(a_b-0.3), y + 3*np.sin(a_b-0.3))
    ]
    boats[boat_id]['hull'].set_xy(hull_coords)

    sail_coords = [
        (x + np.cos(a_b), y + np.sin(a_b)),
        (x + 2*np.cos(a_b+1.2), y + 2*np.sin(a_b+1.2)),
        (x + 2*np.cos(a_b-1.2), y + 2*np.sin(a_b-1.2))
    ]
    boats[boat_id]['sail'].set_xy(sail_coords)