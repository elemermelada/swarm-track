# Load required standard modules
import numpy as np

# Load required tudatpy modules
from tudatpy.kernel.interface import spice
from tudatpy.kernel.numerical_simulation import environment_setup
from tudatpy.kernel.numerical_simulation import estimation, estimation_setup
from tudatpy.kernel.numerical_simulation.estimation_setup import observation

from util.environment_setup import add_radiation_pressure

from util.observation import create_cartesian_observations

from util.graphs import (
    init_trajectory_graph,
    plot_mars,
    plot_trajectory_from_spice,
    scatter_ephemeris,
)

from init.MEX1TW import bodies, simulation_start_epoch, simulation_end_epoch

# Add radiation pressure to environment
add_radiation_pressure(bodies, environment_setup)

# Create trajectory plot
ax, fig = init_trajectory_graph()
ax = plot_trajectory_from_spice(
    ax,
    spice,
    "MEX",
    simulation_start_epoch,
    simulation_end_epoch,
)
ax = plot_mars(ax, spice)
ax.legend()
fig.tight_layout()
fig.savefig("out/truth.png")

# General observation settings
observation_times = np.arange(simulation_start_epoch, simulation_end_epoch, 60.0)

cartesian_observations = create_cartesian_observations(
    observation, estimation_setup, estimation, observation_times, bodies
)

ax = scatter_ephemeris(ax, cartesian_observations * 1e-3, color="r")
ax.legend()
fig.tight_layout()
fig.savefig("out/observations.png")
