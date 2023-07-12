def create_estimator(numerical_simulation, bodies, parameters_to_estimate, observation_settings_list, propagator_settings):
    estimator = numerical_simulation.Estimator(
    bodies,
    parameters_to_estimate,
    observation_settings_list,
    propagator_settings)
    return estimator

def estimate(estimation, estimator, simulated_observations):
    estimation_input = estimation.EstimationInput(
        simulated_observations)

    estimation_input.define_estimation_settings(
        reintegrate_variational_equations=False,
        save_state_history_per_iteration=True)

    estimation_output = estimator.perform_estimation(estimation_input)
    return estimation_output