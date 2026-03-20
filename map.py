import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button
from matplotlib.animation import FuncAnimation
from classic.dijkstra import dijkstra
from quantique.qaoa import simulation
from quantique_mps.qaoa import simulation_mps
from visuel import *
from visuel.enigme import afficher_enigme
from visuel.finishline import finish_line
from visuel.boat import *
from visuel.infos import *
from visuel.scalebar import draw_scale_bar


def interactive_windy_pro(env, time_max=70):
    
    fig, ax = plt.subplots(figsize=(8, 6), facecolor="#323232")
    plt.subplots_adjust(bottom=0.2, right=0.85)

    x_coords = np.sort(np.unique(env.points[:, 0]))
    y_coords = np.sort(np.unique(env.points[:, 1]))
    X, Y = np.meshgrid(x_coords, y_coords)

    race_data = {'waypoints_q': None, 'waypoints_c': None}

    trail_line_q, = ax.plot([], [], color="#58a6ff", linewidth=2.5, linestyle='-', alpha=0.9, zorder=5, label="Quantum")
    trail_line_c, = ax.plot([], [], color="#ff7800", linewidth=2.5, linestyle='-', alpha=0.9, zorder=4, label="Classique")
    trail_line_qmps, = ax.plot([], [], color="#FF0000", linewidth=2.5, linestyle='-', alpha=0.9, zorder=4, label="Quantum_mps")
    ax.legend(loc='upper left', facecolor='#323232', labelcolor='white')

    boats = [
        {'hull': None, 'sail': None, 'color': '#58a6ff', 'label': 'QAOA_aer'},   
        {'hull': None, 'sail': None, 'color': '#ff7800', 'label': 'Dijkstra'}, 
        {'hull': None, 'sail': None, 'color': "#FF0000", 'label': 'QAOA_mps'} 
    ]

    x_b, y_b = 5, 5
    a_b = np.arctan2(96.0 - y_b, 83.7 - x_b) + np.pi
    
    
    U_full, V_full, speed0 = get_wind_vectors(0, env, x_coords, y_coords )

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
            print("Simulation time : approximately 3 minutes ...")
            answer = afficher_enigme()
            title.set_text("CALCULATING PATHS...")
            title.set_color('#f1e05a') 
            fig.canvas.draw()
            fig.canvas.flush_events() 

            print("Lancement Dijkstra...")
            noeudc, tc, tfc = dijkstra(env) 
            
            print("Lancement QAOA...")
            coords_q, tq, tfq = simulation(env)
            
            print("Lancement QAOA_mps ...")
            coords_qmps, tqmps, tfqmps = simulation_mps(env)

            # On met les données en mémoire globale pour le slider
            race_data['waypoints_c'] = [(x, y, t) for (x, y), t in zip(env.points[noeudc], tc)]
            race_data['waypoints_q'] = [(x, y, t) for (x, y), t in zip(coords_q, tq)]
            race_data['waypoints_qmps'] = [(x, y, t) for (x, y), t in zip(coords_qmps, tqmps)]

            title.set_text("RACE : QAOA vs DIJKSTRA !")
            title.set_color('#ffffff') 

            max_t = max(tfc, tfqmps,tfq)
            num_frames = 150      
            time_steps = np.linspace(0, max_t, num_frames)

            def animate(frame):
                current_t = time_steps[frame]
                
                U_t, V_t, speed_t = get_wind_vectors(current_t, env, x_coords, y_coords)
                im.set_data(speed_t)
                q.set_UVC(U_t[::step, ::step], V_t[::step, ::step])
                
                # Bateau Quantique
                xq, yq, idx_q, angle_q = get_pos_at_time(race_data['waypoints_q'], current_t)
                trail_x_q = [wp[0] for wp in race_data['waypoints_q'][:idx_q]] + [xq]
                trail_y_q = [wp[1] for wp in race_data['waypoints_q'][:idx_q]] + [yq]
                trail_line_q.set_data(trail_x_q, trail_y_q)
                update_boat(0, xq, yq, angle_q, boats)

                # Bateau Quantique mps
                xqmps, yqmps, idx_qmps, angle_qmps = get_pos_at_time(race_data['waypoints_qmps'], current_t)
                trail_x_qmps = [wp[0] for wp in race_data['waypoints_qmps'][:idx_qmps]] + [xqmps]
                trail_y_qmps = [wp[1] for wp in race_data['waypoints_qmps'][:idx_qmps]] + [yqmps]
                trail_line_qmps.set_data(trail_x_qmps, trail_y_qmps)
                update_boat(2, xqmps, yqmps, angle_qmps, boats)

                # Bateau Classique
                xc, yc, idx_c, angle_c = get_pos_at_time(race_data['waypoints_c'], current_t)
                trail_x_c = [wp[0] for wp in race_data['waypoints_c'][:idx_c]] + [xc]
                trail_y_c = [wp[1] for wp in race_data['waypoints_c'][:idx_c]] + [yc]
                trail_line_c.set_data(trail_x_c, trail_y_c)
                update_boat(1, xc, yc, angle_c, boats)

                # On avance le slider silencieusement
                slider.eventson = False 
                slider.set_val(current_t)
                slider.eventson = True
                
                if frame == num_frames - 1:
                    title.set_text(f" RÉSULTATS \n Dijkstra h : {tfc:.1f} | QAOA : {tfq:.1f} h | MPS : {tfqmps:.1f} h")
                    title.set_color("#ffffff")
                    print(answer)
                    
                else:
                    title.set_text(f"RACE IN PROGRESS - {int(current_t)}h{int((current_t%1)*60):02d}")
                    title.set_color('#ffffff')
                    
                return boats[0]['hull'], boats[0]['sail'], boats[1]['hull'], boats[1]['sail'] ,boats[2]['hull'], boats[2]['sail'],  trail_line_q, trail_line_c,trail_line_qmps, im, q

            global anim
            anim = FuncAnimation(fig, animate, frames=num_frames, interval=60, blit=False, repeat=False)
            fig.canvas.draw()

        btn_answer.on_clicked(show_path)
        fig.btn_answer = btn_answer
    
    def update(val):
        t = slider.val
        U_t, V_t, speed_t = get_wind_vectors(t, env, x_coords, y_coords)
        im.set_data(speed_t)
        q.set_UVC(U_t[::step, ::step], V_t[::step, ::step])
        title.set_text(f"LIVE WIND FORECAST - {int(t)}h{int((t%1)*60):02d}")

        if race_data['waypoints_qmps'] is not None and race_data['waypoints_c'] is not None and race_data['waypoints_q'] is not None:
            # QAOA
            xq, yq, idx_q, angle_q = get_pos_at_time(race_data['waypoints_q'], t)
            trail_x_q = [wp[0] for wp in race_data['waypoints_q'][:idx_q]] + [xq]
            trail_y_q = [wp[1] for wp in race_data['waypoints_q'][:idx_q]] + [yq]
            trail_line_q.set_data(trail_x_q, trail_y_q)
            update_boat(0, xq, yq, angle_q, boats)

            # Classique
            xc, yc, idx_c, angle_c = get_pos_at_time(race_data['waypoints_c'], t)
            trail_x_c = [wp[0] for wp in race_data['waypoints_c'][:idx_c]] + [xc]
            trail_y_c = [wp[1] for wp in race_data['waypoints_c'][:idx_c]] + [yc]
            trail_line_c.set_data(trail_x_c, trail_y_c)
            update_boat(1, xc, yc, angle_c, boats)

            # QAOA mps
            xqmps, yqmps, idx_qmps, angle_qmps = get_pos_at_time(race_data['waypoints_qmps'], t)
            trail_x_qmps = [wp[0] for wp in race_data['waypoints_qmps'][:idx_qmps]] + [xqmps]
            trail_y_qmps = [wp[1] for wp in race_data['waypoints_qmps'][:idx_qmps]] + [yqmps]
            trail_line_qmps.set_data(trail_x_qmps, trail_y_qmps)
            update_boat(2, xqmps, yqmps, angle_qmps, boats)
            
            
        fig.canvas.draw_idle()

    button()
    draw_scale_bar(fig)
    slider.on_changed(update)
    init_boats(x_b, y_b, boats, ax, a_b)
    finish_line(ax)
    plt.show()