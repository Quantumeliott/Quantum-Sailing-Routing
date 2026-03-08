import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
from data import MarineEnvironment
import matplotlib.patheffects as patheffects
from matplotlib.patches import Polygon, Rectangle

def interactive_windy_pro(env, time_max=150):
    # Setup du style sombre profond
    fig, ax = plt.subplots(figsize=(8, 6), facecolor="#323232")
    plt.subplots_adjust(bottom=0.2, right=0.85)

    # Grille 2D haute résolution pour l'affichage (interpolation)
    x_coords = np.sort(np.unique(env.points[:, 0]))
    y_coords = np.sort(np.unique(env.points[:, 1]))
    X, Y = np.meshgrid(x_coords, y_coords)

    x_b = 5
    y_b=-45
    a_b= 5*np.pi/4
    def finish_line():
        finish_width = 0.5
        finish_height = 10
        rect = Rectangle((-finish_width/2, -finish_height/2),
                        finish_width, finish_height,
                        facecolor='black', hatch='////', alpha=1)
        from matplotlib.transforms import Affine2D
        rot = Affine2D().rotate(np.pi/4).translate(90, 40)
        rect.set_transform(rot + ax.transData)
        ax.add_patch(rect)

    def boat():
        hull = Polygon([
            (x_b, y_b),
            (x_b + 3*np.cos(a_b+0.3), y_b + 3*np.sin(a_b+0.3)),
            (x_b + 3*np.cos(a_b-0.3), y_b + 3*np.sin(a_b-0.3))
        ], closed=True, facecolor='black')
        ax.add_patch(hull)

        # voile : triangle plus fin et tourné vers l’arrière
        sail = Polygon([
                (x_b + np.cos(a_b), y_b + np.sin(a_b)),
                (x_b + 2*np.cos(a_b+1.2), y_b + 2*np.sin(a_b+1.2)),
                (x_b + 2*np.cos(a_b-1.2), y_b + 2*np.sin(a_b-1.2))
            ], closed=True, facecolor='black')
        ax.add_patch(sail)
    
    step = 2  # Affiche 1 flèche sur 3 (divise par 9 le nombre de calculs)
    X_sub = X[::step, ::step]
    Y_sub = Y[::step, ::step]
    
    def get_wind_vectors(t):
        df_t = env.get_wind_at_time(time=t).sort_values(by=['y', 'x'])
        u_raw = df_t.wind_speed.values * np.cos(np.radians((270 - df_t.wind_dir.values) % 360))
        v_raw = df_t.wind_speed.values * np.sin(np.radians((270 - df_t.wind_dir.values) % 360))
        
        U = u_raw.reshape(len(y_coords), len(x_coords))
        V = v_raw.reshape(len(y_coords), len(x_coords))
        speed = np.sqrt(U**2 + V**2)
        # On renvoie les versions complètes pour le fond et sous-échantillonnées pour les flèches
        return U[::step, ::step], V[::step, ::step], speed
    
    U0, V0, speed0 = get_wind_vectors(0)

    im = ax.imshow(speed0, extent=[X.min(), X.max(), Y.min(), Y.max()], 
                   origin='lower', cmap='gist_earth', alpha=0.8, interpolation='lanczos')

    q = ax.quiver(X_sub, Y_sub, U0, V0,cmap='gist_earth',scale=800, alpha=1, 
                   width=0.002, headwidth=3, pivot='mid')

    for s in ax.spines.values(): s.set_visible(False)

    # Cosmétique
    ax.set_xticks([]); ax.set_yticks([])
    for s in ax.spines.values(): s.set_visible(False)
    title = ax.set_title(f"LIVE WIND FORECAST - {0}h", color='white', loc='left', pad=20)

    # Slider vertical stylisé
    ax_slider = fig.add_axes([0.8, 0.1, 0.02, 0.8], facecolor='#161b22')
    slider = Slider(ax_slider, '', 0, time_max, valinit=0, orientation='vertical', color='#58a6ff')
    
    def update(val):
        t = slider.val
        U_t, V_t, speed_t = get_wind_vectors(t)
        im.set_data(speed_t)
        q.set_UVC(U_t, V_t)
        boat()
        title.set_text(f"LIVE WIND FORECAST - {int(t)}h{int((t%1)*60):02d}")
        fig.canvas.draw_idle()

    slider.on_changed(update)
    boat()
    finish_line()
    plt.show()