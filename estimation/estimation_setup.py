from tudatpy.kernel.numerical_simulation import estimation_setup


def create_parameters_to_estimate(propagator_settings_estimation, bodies):
    parameter_settings = estimation_setup.parameter.initial_states(
        propagator_settings_estimation, bodies
    )
    parameter_settings.append(
        estimation_setup.parameter.gravitational_parameter("Mars")
    )

    parameters_to_estimate = estimation_setup.create_parameter_set(
        parameter_settings, bodies
    )
    return parameters_to_estimate
