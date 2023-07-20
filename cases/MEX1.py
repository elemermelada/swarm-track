# Load required standard modules
import numpy as np

# Load required tudatpy modules
from tudatpy.kernel.interface import spice
from tudatpy.kernel import numerical_simulation
from tudatpy.kernel.numerical_simulation import environment_setup
from tudatpy.kernel.numerical_simulation import propagation_setup
from tudatpy.kernel.numerical_simulation import estimation, estimation_setup

from util.environment_setup import add_radiation_pressure
from util.estimation_postprocessing import retrieve_best_iteration_state_history

from util.observation import perform_observations
from util.dynamical_models import basic_propagator
from util.estimation import create_estimator, estimate
from util.estimation_setup import create_parameters_to_estimate

from util.graphs import (
    init_trajectory_graph,
    plot_ephemeris,
    plot_mars,
    plot_trajectory_from_spice,
)

from init.MEX10TWSHORT import (
    bodies,
    simulation_start_epoch,
    simulation_end_epoch,
    links,
    light_time_correction_settings,
    observation_times,
)
from util.observation_setup import create_simple_doppler_sensors

# Add radiation pressure to environment
add_radiation_pressure(bodies, environment_setup)

# Create trajectory plot + mars
ax, fig = init_trajectory_graph()
ax = plot_trajectory_from_spice(
    ax, spice, "MEX", simulation_start_epoch, simulation_end_epoch, axis=[1, 2]
)

# Add doppler "sensors"
(
    observation_settings_list,
    observation_simulation_settings,
) = create_simple_doppler_sensors(
    links, light_time_correction_settings, observation_times
)

# # Add range "sensors"
# (
#     observation_settings_list,
#     observation_simulation_settings,
# ) = create_simple_range_sensors(
#     links, light_time_correction_settings, observation_times
# )

# Create observations
simulated_observations = perform_observations(
    estimation_setup,
    estimation,
    observation_settings_list,
    bodies,
    observation_simulation_settings,
)

# Estimate
propagator_settings_estimation = basic_propagator(
    propagation_setup,
    spice,
    simulation_start_epoch,
    simulation_end_epoch,
    bodies,
    ["MEX"],
    ["Mars"],
)
parameters_to_estimate = create_parameters_to_estimate(
    estimation_setup, propagator_settings_estimation, bodies
)
estimator = create_estimator(
    numerical_simulation,
    bodies,
    parameters_to_estimate,
    observation_settings_list,
    propagator_settings_estimation,
)
estimation_output = estimate(estimation, estimator, simulated_observations)

state_history = retrieve_best_iteration_state_history(estimation_output, clean=True)
ax = plot_ephemeris(ax, state_history * 1e-3, color="k", linestyle="--")
ax.legend()
fig.tight_layout()
fig.savefig("out/estimate.png")
