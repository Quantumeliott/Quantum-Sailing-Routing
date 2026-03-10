import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button
from matplotlib.patches import Polygon, Rectangle
from matplotlib.animation import FuncAnimation
from dijkstra import dijkstra
from qaoa import simulation
from weather import get_wind_at_time

def interactive_windy_pro(env, time_max=50):
    
    fig, ax = plt.subplots(figsize=(8, 6), facecolor="#323232")
    plt.subplots_adjust(bottom=0.2, right=0.85)

    x_coords = np.sort(np.unique(env.points[:, 0]))
    y_coords = np.sort(np.unique(env.points[:, 1]))
    X, Y = np.meshgrid(x_coords, y_coords)

    race_data = {'waypoints_q': None, 'waypoints_c': None}

    trail_line_q, = ax.plot([], [], color="#58a6ff", linewidth=2.5, linestyle='-', alpha=0.9, zorder=5, label="Quantum")
    trail_line_c, = ax.plot([], [], color="#ff7800", linewidth=2.5, linestyle='--', alpha=0.9, zorder=4, label="Classique")
    ax.legend(loc='upper left', facecolor='#323232', labelcolor='white')

    boats = [
        {'hull': None, 'sail': None, 'color': '#58a6ff', 'label': 'QAOA_aer'},   
        {'hull': None, 'sail': None, 'color': '#ff7800', 'label': 'Dijkstra'} 
    ]
    def finish_line():
        rect = Rectangle((35, 39), 0.5, 10, facecolor='black', hatch='////', alpha=1)
        from matplotlib.transforms import Affine2D
        rot = Affine2D().rotate(np.pi/4).translate(90, 40)
        rect.set_transform(rot + ax.transData)
        ax.add_patch(rect)

    def draw_scale_bar():
        ax_scale = fig.add_axes([0.05, 0.05, 0.15, 0.03], facecolor='none')
        ax_scale.barh(0, 5, height=0.3, color='white', edgecolor='white', align='center')
        ax_scale.text(5/2, 0.8, "5 nm", color='white', fontsize=9, ha='center', fontweight='bold')
        ax_scale.set_xlim(0, 10 * 1.2)
        ax_scale.set_ylim(-1, 1)
        ax_scale.axis('off')

    def init_boats(x, y, a_b=0):
        for i, b in enumerate(boats):
            b['hull'] = Polygon([[0,0], [0,0], [0,0]], closed=True, facecolor=b['color'], zorder=10+i)
            b['sail'] = Polygon([[0,0], [0,0], [0,0]], closed=True, facecolor='white', zorder=10+i)
            ax.add_patch(b['hull'])
            ax.add_patch(b['sail'])
            update_boat(i, x, y, a_b)

    def update_boat(boat_id, x, y, a_b):
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
    x_b, y_b = 5, 5
    a_b = 5*np.pi/4
    
    def get_wind_vectors(t):
        df_t = get_wind_at_time(env, time=t).sort_values(by=['y', 'x'])
        u_raw = df_t.wind_speed.values * np.cos(np.radians((270 - df_t.wind_dir.values) % 360))
        v_raw = df_t.wind_speed.values * np.sin(np.radians((270 - df_t.wind_dir.values) % 360))
        U = u_raw.reshape(len(y_coords), len(x_coords))
        V = v_raw.reshape(len(y_coords), len(x_coords))
        speed = np.sqrt(U**2 + V**2)
        return U, V, speed
    
    U_full, V_full, speed0 = get_wind_vectors(0)
    step = 2  
    X_sub = X[::step, ::step]
    Y_sub = Y[::step, ::step]

    im = ax.imshow(speed0, extent=[X.min(), X.max(), Y.min(), Y.max()], 
                   origin='lower', cmap='gist_earth', alpha=0.8, 
                   interpolation='lanczos', vmin=0, vmax=35)

    q = ax.quiver(X_sub, Y_sub, U_full[::step, ::step], V_full[::step, ::step], 
                  color='black', alpha=0.4, scale=800, width=0.002, pivot='mid')

    ax.set_xticks([]); ax.set_yticks([])
    for s in ax.spines.values(): s.set_visible(False)
    title = ax.set_title(f"LIVE WIND FORECAST - 0h", color='white', loc='center', pad=20)

    ax_slider = fig.add_axes([0.8, 0.1, 0.02, 0.8], facecolor='#161b22')
    slider = Slider(ax_slider, 'Time', 0, time_max, valinit=0, orientation='vertical', color="#0077b8")
    
    cax = fig.add_axes([0.88, 0.2, 0.02, 0.5])
    cb = fig.colorbar(im, cax=cax)
    cb.set_label('Wind Speed (knots)', color='white', weight='bold')
    cb.ax.yaxis.set_tick_params(color='white', labelcolor='white')
    
    global anim  

    def button():
        ax_answer = fig.add_axes([0.35, 0.10, 0.30, 0.05]) 
        btn_answer = Button(ax_answer, 'START RACE', color="#0A250F", hovercolor='#238636')
        btn_answer.label.set_color('white')
        btn_answer.label.set_weight('bold')
        btn_answer.label.set_fontsize(10)

        def show_path(event):
            title.set_text("CALCULATING PATHS...")
            title.set_color('#f1e05a') 
            fig.canvas.draw()
            fig.canvas.flush_events() 

            print("Lancement Dijkstra...")
            noeudc, tc, tfc = dijkstra(env) 
            
            print("Lancement QAOA...")
            coords_q, tq, tfq = simulation(env)

            # On met les données en mémoire globale pour le slider
            race_data['waypoints_c'] = [(x, y, t) for (x, y), t in zip(env.points[noeudc], tc)]
            race_data['waypoints_q'] = [(x, y, t) for (x, y), t in zip(coords_q, tq)]

            title.set_text("RACE : QAOA vs DIJKSTRA !")
            title.set_color('#ffffff') 

            max_t = max(tfc, tfq)
            num_frames = 150      
            time_steps = np.linspace(0, max_t, num_frames)

            def animate(frame):
                current_t = time_steps[frame]
                
                U_t, V_t, speed_t = get_wind_vectors(current_t)
                im.set_data(speed_t)
                q.set_UVC(U_t[::step, ::step], V_t[::step, ::step])
                
                # Bateau Quantique
                xq, yq, idx_q, angle_q = get_pos_at_time(race_data['waypoints_q'], current_t)
                trail_x_q = [wp[0] for wp in race_data['waypoints_q'][:idx_q]] + [xq]
                trail_y_q = [wp[1] for wp in race_data['waypoints_q'][:idx_q]] + [yq]
                trail_line_q.set_data(trail_x_q, trail_y_q)
                update_boat(0, xq, yq, angle_q)

                # Bateau Classique
                xc, yc, idx_c, angle_c = get_pos_at_time(race_data['waypoints_c'], current_t)
                trail_x_c = [wp[0] for wp in race_data['waypoints_c'][:idx_c]] + [xc]
                trail_y_c = [wp[1] for wp in race_data['waypoints_c'][:idx_c]] + [yc]
                trail_line_c.set_data(trail_x_c, trail_y_c)
                update_boat(1, xc, yc, angle_c)

                # On avance le slider silencieusement
                slider.eventson = False 
                slider.set_val(current_t)
                slider.eventson = True
                
                if frame == num_frames - 1:
                    title.set_text(f" RÉSULTATS \n Dijkstra (Orange) h : {tfc:.1f} | QAOA (Bleu) : {tfq:.1f} h")
                    title.set_color("#ffffff")
                    
                else:
                    title.set_text(f"RACE IN PROGRESS - {int(current_t)}h{int((current_t%1)*60):02d}")
                    title.set_color('#ffffff')
                    
                return boats[0]['hull'], boats[0]['sail'], boats[1]['hull'], boats[1]['sail'], trail_line_q, trail_line_c, im, q

            global anim
            anim = FuncAnimation(fig, animate, frames=num_frames, interval=60, blit=False, repeat=False)
            fig.canvas.draw()

        btn_answer.on_clicked(show_path)
        fig.btn_answer = btn_answer
    
    def update(val):
        t = slider.val
        U_t, V_t, speed_t = get_wind_vectors(t)
        im.set_data(speed_t)
        q.set_UVC(U_t[::step, ::step], V_t[::step, ::step])
        title.set_text(f"LIVE WIND FORECAST - {int(t)}h{int((t%1)*60):02d}")

        if race_data['waypoints_q'] is not None and race_data['waypoints_c'] is not None:
            # QAOA
            xq, yq, idx_q, angle_q = get_pos_at_time(race_data['waypoints_q'], t)
            trail_x_q = [wp[0] for wp in race_data['waypoints_q'][:idx_q]] + [xq]
            trail_y_q = [wp[1] for wp in race_data['waypoints_q'][:idx_q]] + [yq]
            trail_line_q.set_data(trail_x_q, trail_y_q)
            update_boat(0, xq, yq, angle_q)

            # Classique
            xc, yc, idx_c, angle_c = get_pos_at_time(race_data['waypoints_c'], t)
            trail_x_c = [wp[0] for wp in race_data['waypoints_c'][:idx_c]] + [xc]
            trail_y_c = [wp[1] for wp in race_data['waypoints_c'][:idx_c]] + [yc]
            trail_line_c.set_data(trail_x_c, trail_y_c)
            update_boat(1, xc, yc, angle_c)
            
        fig.canvas.draw_idle()

    button()
    draw_scale_bar()
    slider.on_changed(update)
    init_boats(x_b, y_b, a_b)
    finish_line()
    plt.show()