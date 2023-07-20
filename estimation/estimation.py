from tudatpy.kernel.numerical_simulation import estimation


def create_estimator(
    numerical_simulation,
    bodies,
    parameters_to_estimate,
    observation_settings_list,
    propagator_settings,
):
    estimator = numerical_simulation.Estimator(
        bodies, parameters_to_estimate, observation_settings_list, propagator_settings
    )
    return estimator


def estimate(estimator, simulated_observations):
    convergence_checker = estimation.estimation_convergence_checker(
        maximum_iterations=5, number_of_iterations_without_improvement=2
    )
    estimation_input = estimation.EstimationInput(
        simulated_observations, convergence_checker=convergence_checker
    )

    estimation_input.define_estimation_settings(
        reintegrate_variational_equations=False, save_state_history_per_iteration=True
    )

    estimation_output = estimator.perform_estimation(estimation_input)
    return estimation_output
