# Load required standard modules
import numpy as np

# Load required tudatpy modules
from tudatpy.kernel.interface import spice
from tudatpy.kernel import numerical_simulation
from tudatpy.kernel.numerical_simulation import environment_setup
from tudatpy.kernel.numerical_simulation import propagation_setup
from tudatpy.kernel.numerical_simulation import estimation, estimation_setup
from tudatpy.kernel.numerical_simulation.estimation_setup import observation

from util.environment_setup import add_radiation_pressure, add_tw_stations
from util.observation_setup import (
    add_noise,
    add_observation_simulators,
    add_simple_doppler_observation_settings,
    add_simple_range_observation_settings,
    add_viability_check,
    create_links,
)
from util.observation import perform_observations
from util.dynamical_models import basic_propagator
from util.estimation import create_estimator, estimate
from util.estimation_setup import create_parameters_to_estimate

from util.graphs import (
    init_trajectory_graph,
    plot_mars,
    plot_trajectory,
    plot_trajectory_from_spice,
)
from util.point_distributions import fibonacci_sphere

from init.MEX1 import bodies, simulation_start_epoch, simulation_end_epoch, tw_number

# Add radiation pressure to environment
add_radiation_pressure(bodies, environment_setup)

# Create trajectory plot
ax, fig = init_trajectory_graph()
ax = plot_trajectory_from_spice(
    ax, spice, "MEX", simulation_start_epoch, simulation_end_epoch, axis=[0, 2]
)
ax = plot_mars(ax, spice)
ax.legend()
fig.tight_layout()
fig.savefig("out/truth.png")

# Add TW stations and create links to MEX
add_tw_stations(environment_setup, bodies.get("Mars"), tw_number, fibonacci_sphere)
links = create_links(observation, tw_number, "MEX")

# General observation settings
light_time_correction_settings = (
    observation.first_order_relativistic_light_time_correction(["Sun"])
)
observation_times = np.arange(simulation_start_epoch, simulation_end_epoch, 60.0)

# Add doppler "sensors"
observation_settings_list = add_simple_doppler_observation_settings(
    observation,
    tw_number,
    links,
    light_time_correction_settings=light_time_correction_settings,
)
observation_simulation_settings = add_observation_simulators(
    observation, observation_times, links, tw_number, observation.one_way_range_type
)
add_noise(
    observation,
    1.0e-3,
    observation.one_way_instantaneous_doppler_type,
    observation_simulation_settings,
)
add_viability_check(
    observation,
    observation.one_way_instantaneous_doppler_type,
    np.deg2rad(15),
    tw_number,
    observation_simulation_settings,
    links,
)

# Add range "sensors"
observation_settings_list = add_simple_range_observation_settings(
    observation,
    tw_number,
    links,
    light_time_correction_settings=light_time_correction_settings,
    observation_settings_list=observation_settings_list,
)
observation_simulation_settings = add_observation_simulators(
    observation,
    observation_times,
    links,
    tw_number,
    observation.one_way_instantaneous_doppler_type,
    observation_simulation_settings=observation_simulation_settings,
)
add_noise(
    observation, 1.0, observation.one_way_range_type, observation_simulation_settings
)
add_viability_check(
    observation,
    observation.one_way_range_type,
    np.deg2rad(15),
    tw_number,
    observation_simulation_settings,
    links,
)

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
