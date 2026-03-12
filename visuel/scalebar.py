def draw_scale_bar(fig):
        ax_scale = fig.add_axes([0.05, 0.05, 0.15, 0.03], facecolor='none')
        ax_scale.barh(0, 5, height=0.3, color='white', edgecolor='white', align='center')
        ax_scale.text(5/2, 0.8, "5 nm", color='white', fontsize=9, ha='center', fontweight='bold')
        ax_scale.set_xlim(0, 10 * 1.2)
        ax_scale.set_ylim(-1, 1)
        ax_scale.axis('off')