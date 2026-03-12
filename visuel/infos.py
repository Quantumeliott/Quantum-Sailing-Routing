import numpy as np
from data import get_wind_at_time

def get_wind_vectors(t, env, x_coords,y_coords) :
        df_t = get_wind_at_time(env, time=t).sort_values(by=['y', 'x'])
        u_raw = df_t.wind_speed.values * np.cos(np.radians((270 - df_t.wind_dir.values) % 360))
        v_raw = df_t.wind_speed.values * np.sin(np.radians((270 - df_t.wind_dir.values) % 360))
        U = u_raw.reshape(len(y_coords), len(x_coords))
        V = v_raw.reshape(len(y_coords), len(x_coords))
        speed = np.sqrt(U**2 + V**2)
        return U, V, speed

def get_pos_at_time(waypoints, target_t):
        times = [wp[2] for wp in waypoints]
        if target_t >= times[-1]:
            return waypoints[-1][0], waypoints[-1][1], len(waypoints)-1, 0
        
        idx = np.searchsorted(times, target_t)
        if idx == 0:
            return waypoints[0][0], waypoints[0][1], 0, 0

        t0, t1 = times[idx-1], times[idx]
        x0, y0 = waypoints[idx-1][0], waypoints[idx-1][1]
        x1, y1 = waypoints[idx][0], waypoints[idx][1]
        
        ratio = (target_t - t0) / (t1 - t0) if t1 > t0 else 1.0
        curr_x = x0 + ratio * (x1 - x0)
        curr_y = y0 + ratio * (y1 - y0)
        angle = np.arctan2(y1 - y0, x1 - x0) + np.pi
        
        return curr_x, curr_y, idx, angle