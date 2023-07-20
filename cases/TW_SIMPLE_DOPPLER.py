from util.environment_setup import add_radiation_pressure
from util.dynamical_models import basic_propagator
from util.graphs import (
    init_trajectory_graph,
    plot_ephemeris,
    plot_mars,
    plot_trajectory_from_spice,
)

from observation.observation_setup import create_simple_1w_doppler_sensors
from observation.observation import perform_observations

from estimation.estimation_setup import create_simple_parameters_to_estimate
from estimation.estimation import create_estimator, estimate
from estimation.estimation_postprocessing import retrieve_best_iteration_state_history

from init.MEX_10TW_SHORT import (
    bodies,
    simulation_start_epoch,
    simulation_end_epoch,
    links,
    light_time_correction_settings,
    observation_times,
)

# Add radiation pressure to environment
add_radiation_pressure(bodies)

# Create trajectory plot + mars
ax, fig = init_trajectory_graph()
ax = plot_trajectory_from_spice(
    ax, "MEX", simulation_start_epoch, simulation_end_epoch, axis=[1, 2]
)
ax = plot_mars(ax)

# Add doppler "sensors"
(
    observation_settings_list,
    observation_simulation_settings,
) = create_simple_1w_doppler_sensors(
    links, light_time_correction_settings, observation_times
)

# Create observations
simulated_observations = perform_observations(
    observation_settings_list,
    bodies,
    observation_simulation_settings,
)

# Estimate
propagator_settings_estimation = basic_propagator(
    simulation_start_epoch,
    simulation_end_epoch,
    bodies,
    ["MEX"],
    ["Mars"],
)
parameters_to_estimate = create_simple_parameters_to_estimate(
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
ax = plot_ephemeris(ax, state_history * 1e-3, color="k", linestyle="--")
ax.legend()
fig.tight_layout()
fig.savefig("out/estimate.png")
