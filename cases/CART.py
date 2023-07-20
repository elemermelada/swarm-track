# Load required tudatpy modules
from util.environment_setup import add_radiation_pressure
from util.graphs import (
    init_trajectory_graph,
    plot_mars,
    plot_trajectory_from_spice,
    scatter_ephemeris,
)

from observation.observation import create_cartesian_observations

from init.MEX0TW import (
    bodies,
    simulation_start_epoch,
    simulation_end_epoch,
    observation_times,
)

# Add radiation pressure to environment
add_radiation_pressure(bodies)

# Create trajectory plot
ax, fig = init_trajectory_graph()
ax = plot_trajectory_from_spice(
    ax,
    "MEX",
    simulation_start_epoch,
    simulation_end_epoch,
)
ax = plot_mars(ax)
ax.legend()
fig.tight_layout()
fig.savefig("out/truth.png")

cartesian_observations = create_cartesian_observations(observation_times, bodies)

ax = scatter_ephemeris(ax, cartesian_observations * 1e-3, color="r")
ax.legend()
fig.tight_layout()
fig.savefig("out/observations.png")
