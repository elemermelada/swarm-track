from tudatpy.kernel.numerical_simulation import estimation_setup


def create_simple_parameters_to_estimate(propagator_settings_estimation, bodies):
    parameter_settings = estimation_setup.parameter.initial_states(
        propagator_settings_estimation, bodies
    )

    parameters_to_estimate = estimation_setup.create_parameter_set(
        parameter_settings, bodies
    )
    return parameters_to_estimate


def create_gravimetry_parameters_to_estimate(propagator_settings_estimation, bodies):
    parameter_settings = estimation_setup.parameter.initial_states(
        propagator_settings_estimation, bodies
    )
    # parameter_settings.append(
    #     estimation_setup.parameter.spherical_harmonics_c_coefficients(
    #         "Mars",
    #         minimum_degree=2,
    #         minimum_order=0,
    #         maximum_degree=2,
    #         maximum_order=2,
    #     )
    # )

    # parameter_settings.append(
    #     estimation_setup.parameter.spherical_harmonics_s_coefficients(
    #         "Mars",
    #         minimum_degree=2,
    #         minimum_order=0,
    #         maximum_degree=2,
    #         maximum_order=2,
    #     )
    # )

    parameters_to_estimate = estimation_setup.create_parameter_set(
        parameter_settings, bodies
    )
    return parameters_to_estimate
