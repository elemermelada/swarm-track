from util.graphs import (
    init_distributions_graph,
    plot_stations,
)
from util.point_distributions import (
    fibonacci_sphere,
    random_sphere,
    equatorial_sphere,
    pole_sphere,
)
import numpy as np

distributions = [pole_sphere, equatorial_sphere]
tw_numbers = [30, 90]
spread = [5.0, 30.0]


for dist in distributions:
    fig, axes = init_distributions_graph(len(tw_numbers) * len(spread))
    for j in range(len(spread)):
        for i in range(len(tw_numbers)):
            tw_number = tw_numbers[i]
            sp = spread[j]
            ax = axes[2 * j + i]

            stations = dist(tw_number, sigma=sp)
            plot_stations(ax, stations)

    fig.tight_layout()
    fig.savefig("out/" + dist.__name__ + ".svg")
    fig.show()
