import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
from data import MarineEnvironment
import matplotlib.patheffects as patheffects
from matplotlib.patches import Polygon, Rectangle
from matplotlib.widgets import Button

def interactive_windy_pro(env, time_max=150):
    # Setup du style sombre profond
    fig, ax = plt.subplots(figsize=(8, 6), facecolor="#323232")
    plt.subplots_adjust(bottom=0.2, right=0.85)

    # Grille 2D haute résolution pour l'affichage (interpolation)
    x_coords = np.sort(np.unique(env.points[:, 0]))
    y_coords = np.sort(np.unique(env.points[:, 1]))
    X, Y = np.meshgrid(x_coords, y_coords)

    def button():
        ax_answer = fig.add_axes([0.35, 0.10, 0.30, 0.05]) 

        btn_answer = Button(ax_answer, 'Show the Answers', 
                            color="#0A250F",      # Fond sombre
                            hovercolor='#238636') # Vert au survol (type GitHub)

        # Stylisation du texte
        btn_answer.label.set_color('white')
        btn_answer.label.set_weight('bold')
        btn_answer.label.set_fontsize(10)

        # 3. La fonction de callback
        def show_path(event):
            title.set_text("OPTIMIZING PATH WITH QAOA...")
            title.set_color('#58a6ff')
            fig.canvas.draw_idle()

        btn_answer.on_clicked(show_path)

    def draw_scale_bar():
        ax_scale = fig.add_axes([0.05, 0.05, 0.15, 0.03], facecolor='none')
    
        ax_scale.barh(0, 5, height=0.3, color='white', edgecolor='white', align='center')
        
        ax_scale.text(5/2, 0.8, f"{5} nm", color='white', 
                    fontsize=9, ha='center', fontweight='bold')
        
        # 4. Nettoyage de l'axe de l'échelle (on ne veut pas voir les bordures)
        ax_scale.set_xlim(0, 10 * 1.2)
        ax_scale.set_ylim(-1, 1)
        ax_scale.axis('off')

    button()
    draw_scale_bar()
    x_b = 5
    y_b = -45
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

    def boat(x,y):
        hull = Polygon([
            (x, y),
            (x + 3*np.cos(a_b+0.3), y + 3*np.sin(a_b+0.3)),
            (x + 3*np.cos(a_b-0.3), y + 3*np.sin(a_b-0.3))
        ], closed=True, facecolor='black')
        ax.add_patch(hull)

        # voile : triangle plus fin et tourné vers l’arrière
        sail = Polygon([
                (x + np.cos(a_b), y + np.sin(a_b)),
                (x + 2*np.cos(a_b+1.2), y + 2*np.sin(a_b+1.2)),
                (x + 2*np.cos(a_b-1.2), y + 2*np.sin(a_b-1.2))
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
    title = ax.set_title(f"LIVE WIND FORECAST - {0}h", color='white', loc='center', pad=20)

    # Slider vertical stylisé
    ax_slider = fig.add_axes([0.8, 0.1, 0.02, 0.8], facecolor='#161b22')
    slider = Slider(ax_slider, '', 0, time_max, valinit=0, orientation='vertical', color='#58a6ff')
    
    def heatmap_color():
        im = ax.imshow(speed0, extent=[X.min(), X.max(), Y.min(), Y.max()], 
               origin='lower', cmap='gist_earth', alpha=0.8, 
               interpolation='lanczos', vmin=0, vmax=30)

        cax = fig.add_axes([0.88, 0.2, 0.02, 0.5]) # [gauche, bas, largeur, hauteur]
        cb = fig.colorbar(im, cax=cax, orientation='vertical')

        cb.set_label('Wind Speed (knots)', color='white', size=10, weight='bold')
        cb.ax.yaxis.set_tick_params(color='white', labelcolor='white')
        cb.outline.set_edgecolor('white')

        # Optionnel : ajouter des graduations spécifiques
        cb.set_ticks([0, 5, 10, 15, 20, 25, 30])

    def update(val):
        t = slider.val
        U_t, V_t, speed_t = get_wind_vectors(t)
        im.set_data(speed_t)
        q.set_UVC(U_t, V_t)
        title.set_text(f"LIVE WIND FORECAST - {int(t)}h{int((t%1)*60):02d}")
        fig.canvas.draw_idle()
    heatmap_color()
    slider.on_changed(update)
    boat(x_b, y_b)
    finish_line()
    plt.show()