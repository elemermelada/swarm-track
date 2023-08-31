from util.environment_setup import add_tw_stations, get_bodies
from util.dynamical_models import basic_propagator
from util.graphs import (
    init_observation_plot,
    init_trajectory_graph,
    plot_ephemeris,
    plot_mars,
    plot_observations,
)

from observation.observation_setup import (
    add_dsn_viability_check,
    add_tw_viability_check,
    create_1w_dsn_links,
    create_1w_tw_links,
    create_simple_1w_doppler_sensors,
)

from estimation.estimation_setup import (
    create_gravimetry_parameters_to_estimate,
)
from estimation.estimation import (
    create_estimator,
    estimate,
)

from init.MEX_10TW import (
    simulation_start_epoch,
    simulation_end_epoch,
    observation_times,
    bodies_to_propagate,
    tw_number,
)
from util.point_distributions import fibonacci_sphere
from util.propagation import retrieve_propagated_state_history

import numpy as np

USE_3D = True
TW_NUMBER = tw_number


def simulate_observations(
    initial_state=None,
    premultiplied_mars_harmonics=None,
    verbose=False,
    observe=None,
    a=5000,
):
    new_bodies = get_bodies(
        simulation_start_epoch,
        simulation_end_epoch,
    )
    add_tw_stations(new_bodies.get("Mars"), TW_NUMBER, fibonacci_sphere)
    links = create_1w_tw_links(TW_NUMBER, "MEX" if observe is None else observe)

    # General observation settings
    # light_time_correction_settings = (
    # observation.first_order_relativistic_light_time_correction(["Sun"])
    # )
    # add_radiation_pressure(new_bodies, {"name": "Sens"})

    # Add doppler "sensors"
    (
        new_observation_settings_list,
        new_observation_simulation_settings,
        observable_type,
    ) = create_simple_1w_doppler_sensors(
        links,
        None,
        observation_times,
        lambda observation_type, elevation_angle, observation_simulation_settings, links: add_tw_viability_check(
            observation_type,
            elevation_angle,
            observation_simulation_settings,
            links,
        ),
        noise=0.1,
    )

    # override_mars_harmonics.normalized_cosine_coefficients[]
    propagator_settings_estimation = basic_propagator(
        simulation_start_epoch,
        simulation_end_epoch,
        new_bodies,
        bodies_to_propagate,
        ["Mars"],
        initial_state_error=0.0,
        override_initial_state=initial_state,
        # gravity_order=0,
    )

    parameters_to_estimate = create_gravimetry_parameters_to_estimate(
        propagator_settings_estimation, new_bodies
    )
    estimator = create_estimator(
        new_bodies,
        parameters_to_estimate,
        new_observation_settings_list,
        propagator_settings_estimation,
    )

    from tudatpy.kernel.numerical_simulation import estimation

    # Get simulated observations as ObservationCollection
    simulated_observations = estimation.simulate_observations(
        new_observation_simulation_settings,
        estimator.observation_simulators,
        new_bodies,
    )

    return (
        [
            antenna_results[-1].observations_history
            for antenna_results in simulated_observations.sorted_observation_sets[
                observable_type
            ].values()
        ],
        simulated_observations,
        estimator,
    )


_, actual_observations, _ = simulate_observations(None, observe="MEX")
_, flawed_observations, estimator = simulate_observations(
    initial_state=np.array(
        [
            4.02619229e06 + 1 * -2.62e3 + 0 * 2.68e3,
            -5.57611562e06 + 0 * -1.85e3 + 0 * 1.8e3,
            5.55651973e06 + 0 * -1.93e3 + 0 * 1.95e3,
            1.02259367e03,
            5.05922102e02,
            1.94562060e03,
        ]
    ),
    observe="MEX",
)

result = estimate(estimator, actual_observations)
