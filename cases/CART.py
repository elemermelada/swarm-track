# Load required tudatpy modules
from estimation.estimation import create_estimator, estimate
from estimation.estimation_postprocessing import retrieve_best_iteration_state_history
from estimation.estimation_setup import (
    create_gravimetry_parameters_to_estimate,
)
from observation.observation_postprocessing import (
    retrieve_ephemeris_from_cartesian_observations,
)
from util.dynamical_models import basic_propagator
from util.environment_setup import add_radiation_pressure
from util.graphs import (
    init_trajectory_graph,
    plot_ephemeris,
    plot_mars,
    plot_trajectory_from_spice,
    scatter_ephemeris,
)

from observation.observation import create_cartesian_observations

from init.MEX0TWSHORT import (
    bodies,
    simulation_start_epoch,
    simulation_end_epoch,
    observation_times,
)

USE_3D = True

# Add radiation pressure to environment
add_radiation_pressure(bodies)

# Create trajectory plot
ax, fig = init_trajectory_graph(threeD=USE_3D)
ax = plot_trajectory_from_spice(
    ax, "MEX", simulation_start_epoch, simulation_end_epoch, threeD=USE_3D
)
ax = plot_mars(ax, threeD=USE_3D)
ax.legend()
fig.tight_layout()
fig.savefig("out/truth.png")

observation_settings_list, simulated_observations = create_cartesian_observations(
    observation_times, bodies
)
cartesian_observations = retrieve_ephemeris_from_cartesian_observations(
    simulated_observations
)
ax = scatter_ephemeris(ax, cartesian_observations * 1e-3, color="r", threeD=USE_3D)

propagator_settings_estimation = basic_propagator(
    simulation_start_epoch,
    simulation_end_epoch,
    bodies,
    ["MEX"],
    ["Mars"],
)
parameters_to_estimate = create_gravimetry_parameters_to_estimate(
    propagator_settings_estimation, bodies
)
estimator = create_estimator(
    bodies,
    parameters_to_estimate,
    observation_settings_list,
    propagator_settings_estimation,
)
estimation_output = estimate(estimator, simulated_observations)
state_history = retrieve_best_iteration_state_history(estimation_output, clean=True)
ax = plot_ephemeris(ax, state_history * 1e-3, color="k", linestyle="--", threeD=USE_3D)
ax.legend()
fig.tight_layout()
fig.savefig("out/estimate.png")
fig.show()
