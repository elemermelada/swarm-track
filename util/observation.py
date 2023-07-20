def perform_observations(
    estimation_setup,
    estimation,
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
    from tudatpy.kernel.numerical_simulation import estimation, estimation_setup
    from tudatpy.kernel.numerical_simulation.estimation_setup import observation

    from util.observation_setup import create_cart_link

    links = create_cart_link(observation, "MEX")

    # Add cartesian "sensors"
    TYPE = observation.position_observable_type
    from util.observation_setup import add_simple_cartesian_observation_settings

    observation_settings_list = add_simple_cartesian_observation_settings(
        observation,
        links,
    )
    from util.observation_setup import add_observation_simulators

    observation_simulation_settings = add_observation_simulators(
        observation,
        observation_times,
        links,
        TYPE,
        reference_link_end_type=observation.observed_body,
    )

    # Create observations
    simulated_observations = perform_observations(
        estimation_setup,
        estimation,
        observation_settings_list,
        bodies,
        observation_simulation_settings,
    )

    from util.observation_postprocessing import (
        retrieve_ephemeris_from_cartesian_observations,
    )

    return retrieve_ephemeris_from_cartesian_observations(simulated_observations)
