from tudatpy.kernel.numerical_simulation import estimation, estimation_setup
from tudatpy.kernel.numerical_simulation.estimation_setup import observation

from observation.observation_setup import (
    create_cart_link,
    add_observation_simulators,
    add_simple_cartesian_observation_settings,
)


def perform_observations(
    observation_settings_list,
    bodies,
    observation_simulation_settings,
):
    # Create observation simulators
    observation_simulators = estimation_setup.create_observation_simulators(
        observation_settings_list, bodies
    )
    # Get simulated observations as ObservationCollection
    simulated_observations = estimation.simulate_observations(
        observation_simulation_settings, observation_simulators, bodies
    )

    return simulated_observations


def create_cartesian_observations(observation_times, bodies):
    links = create_cart_link("MEX")

    # Add cartesian "sensors"
    observable_type = observation.position_observable_type

    observation_settings_list = add_simple_cartesian_observation_settings(
        links,
    )

    observation_simulation_settings = add_observation_simulators(
        observation_times,
        links,
        observable_type,
        reference_link_end_type=observation.observed_body,
    )

    # Create observations
    simulated_observations = perform_observations(
        observation_settings_list,
        bodies,
        observation_simulation_settings,
    )

    return observation_settings_list, simulated_observations
