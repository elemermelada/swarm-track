from util.graphs import init_distributions_graph, init_trajectory_graph, plot_sphere
from util.point_distributions import (
    fibonacci_sphere,
    random_sphere,
    equatorial_sphere,
    pole_sphere,
)
import numpy as np

distributions = [equatorial_sphere]
tw_numbers = [10, 30, 50, 100]

for dist in distributions:
    fig, axes = init_distributions_graph(len(tw_numbers))
    for i in range(len(tw_numbers)):
        tw_number = tw_numbers[i]
        ax = axes[i]
        plot_sphere(ax, 1.0, fn=30)

        stations = dist(tw_number)
        for station in stations:
            lat, long = station
            x = np.cos(np.deg2rad(long)) * np.cos(np.deg2rad(lat))
            y = np.sin(np.deg2rad(long)) * np.cos(np.deg2rad(lat))
            z = np.sin(np.deg2rad(lat))
            ax.plot(x, y, z, "or")
        ax.set_title(f"{tw_number} stations")
        # Hide grid lines
        ax.grid(False)

        # Hide axes ticks
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_zticks([])
        # Make panes transparent
        ax.xaxis.pane.fill = False  # Left pane
        ax.yaxis.pane.fill = False  # Right pane
        # Transparent spines
        ax.w_xaxis.line.set_color((1.0, 1.0, 1.0, 0.0))
        ax.w_yaxis.line.set_color((1.0, 1.0, 1.0, 0.0))
        ax.w_zaxis.line.set_color((1.0, 1.0, 1.0, 0.0))

        # Transparent panes
        ax.w_xaxis.set_pane_color((1.0, 1.0, 1.0, 0.0))
        ax.w_yaxis.set_pane_color((1.0, 1.0, 1.0, 0.0))
        ax.set_box_aspect((1, 1, 1))

    fig.tight_layout()
    fig.savefig("out/" + dist.__name__ + ".svg")
    fig.show()
