def perform_observations(estimation_setup, estimation, observation_settings_list, bodies, observation_simulation_settings):
    # Create observation simulators
    observation_simulators = estimation_setup.create_observation_simulators(
        observation_settings_list, bodies)
    # Get MEX simulated observations as ObservationCollection
    simulated_observations = estimation.simulate_observations(
        observation_simulation_settings,
        observation_simulators,
        bodies)
    
    return simulated_observations