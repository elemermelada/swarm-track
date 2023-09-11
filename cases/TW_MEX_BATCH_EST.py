import os
from observation.observation_postprocessing import observations_difference
from util.point_distributions import (
    add_error_to_coordinates,
    pole_sphere,
    equatorial_sphere,
    fibonacci_sphere,
    random_sphere,
)
from util.environment_setup import add_tw_stations, get_bodies
from util.dynamical_models import basic_propagator

from observation.observation_setup import (
    add_tw_viability_check,
    create_1w_tw_links,
    create_simple_1w_doppler_sensors,
)

from estimation.estimation_setup import (
    create_gravimetry_parameters_to_estimate,
)
from estimation.estimation import (
    create_estimator,
    estimate,
    transform_vector,
)

from init.MEX_10TW import (
    simulation_start_epoch,
    simulation_end_epoch,
    bodies_to_propagate,
)
from util.math import vector_rms

import numpy as np

from util.propagation import retrieve_propagated_state_history

dists = [fibonacci_sphere, random_sphere]
# dists = [pole_sphere, equatorial_sphere]
for dist in dists:
    twn = 90
    spread = 30.0
    freq = 10.0
    USE_3D = True
    TW_NUMBER = twn

    tw_stations = dist(TW_NUMBER, sigma=spread)
    tw_stations_wrapper = lambda err: (
        lambda x: add_error_to_coordinates(tw_stations, 3389.5e3, err)
    )

    new_bodies = get_bodies()
    add_tw_stations(new_bodies.get("Mars"), TW_NUMBER, tw_stations_wrapper(1e-1))

    def simulate_observations(
        initial_state_perturbation=None,
        override_initial_state=None,
        observe=None,
        start_day=0.0,
        duration=0.5,
    ):
        from tudatpy.kernel import constants

        # Set simulation start (January 1st, 2004 - 00:00) and end epochs (January 11th, 2004 - 00:00)
        simulation_start_epoch = (
            4.0 * constants.JULIAN_YEAR + (100 + start_day) * constants.JULIAN_DAY
        )
        simulation_duration = duration * constants.JULIAN_DAY
        simulation_end_epoch = simulation_start_epoch + simulation_duration
        observation_times = np.arange(simulation_start_epoch, simulation_end_epoch, 1.0)

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
            noise=1e-2,
        )

        # override_mars_harmonics.normalized_cosine_coefficients[]
        propagator_settings_estimation = basic_propagator(
            simulation_start_epoch,
            simulation_end_epoch,
            new_bodies,
            bodies_to_propagate,
            ["Mars"],
            initial_state_error=0.0,
            override_initial_state=override_initial_state,
            initial_state_perturbation=initial_state_perturbation,
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

    def get_estimator(
        estimator_initial_state_perturbation,
        observator_override_initial_state=None,
        start_day=0.0,
        duration=0.5,
    ):
        _, actual_observations, _ = simulate_observations(
            override_initial_state=observator_override_initial_state,
            observe="MEX",
            start_day=start_day,
            duration=duration,
        )
        _, flawed_observations, estimator = simulate_observations(
            initial_state_perturbation=np.array(estimator_initial_state_perturbation),
            observe="MEX",
            start_day=start_day,
            duration=duration,
        )
        from tudatpy.kernel.interface import spice
        from tudatpy.kernel import constants

        solution = (
            spice.get_body_cartesian_state_at_epoch(
                target_body_name=bodies_to_propagate[0],
                observer_body_name="Mars",
                reference_frame_name="J2000",
                aberration_corrections="none",
                ephemeris_time=(
                    4.0 * constants.JULIAN_YEAR
                    + (100 + start_day) * constants.JULIAN_DAY
                ),
            )
            if observator_override_initial_state is None
            else observator_override_initial_state
        )
        return estimator, actual_observations, solution

    def get_state_diff(initial_state, initial_time, time):
        from tudatpy.kernel.interface import spice
        from tudatpy.kernel import constants

        state_from_spice = spice.get_body_cartesian_state_at_epoch(
            target_body_name=bodies_to_propagate[0],
            observer_body_name="Mars",
            reference_frame_name="J2000",
            aberration_corrections="none",
            ephemeris_time=(
                4.0 * constants.JULIAN_YEAR + (100 + time) * constants.JULIAN_DAY
            ),
        )

        # override_mars_harmonics.normalized_cosine_coefficients[]
        propagator_settings_estimation = basic_propagator(
            4.0 * constants.JULIAN_YEAR + (100 + initial_time) * constants.JULIAN_DAY,
            4.0 * constants.JULIAN_YEAR + (100 + time) * constants.JULIAN_DAY,
            new_bodies,
            bodies_to_propagate,
            ["Mars"],
            initial_state_error=0.0,
            override_initial_state=initial_state,
        )

        ### Propagate to see wassup
        # ax, fig = init_trajectory_graph(threeD=USE_3D)
        state_history, time_vector = retrieve_propagated_state_history(
            propagator_settings_estimation, new_bodies, True
        )

        return transform_vector(
            state_history[-1] - state_from_spice, state_from_spice, all=True
        )

    sim_start = 0.0
    obs_duration = 1
    obs_overlap = 0.2

    from tudatpy.kernel.interface import spice
    from tudatpy.kernel import constants

    real_initial_state = spice.get_body_cartesian_state_at_epoch(
        target_body_name="MEX",
        observer_body_name="Mars",
        reference_frame_name="J2000",
        aberration_corrections="none",
        ephemeris_time=4.0 * constants.JULIAN_YEAR
        + (100 + sim_start) * constants.JULIAN_DAY,
    )
    propagator_settings_estimation = basic_propagator(
        4.0 * constants.JULIAN_YEAR + (100 + sim_start) * constants.JULIAN_DAY,
        4.0 * constants.JULIAN_YEAR + (100 + sim_start + 12) * constants.JULIAN_DAY,
        new_bodies,
        bodies_to_propagate,
        ["Mars"],
    )
    real_ephemeris, _ = retrieve_propagated_state_history(
        propagator_settings_estimation, new_bodies, clean=False
    )

    for init_diff_direction in range(3):
        init_state_perturbation = np.array(
            [1e3 if init_diff_direction == i else 0 for i in range(6)]
        )
        override_init_state = None
        for step in range(12):
            current_time = sim_start + step * (obs_duration - obs_overlap)
            estimator, actual_observations, solution = get_estimator(
                init_state_perturbation,
                observator_override_initial_state=override_init_state,
                start_day=current_time,
                duration=obs_duration,
            )
            result = estimate(estimator, actual_observations)
            final_parameters = np.array(result.parameter_history)[:, -1]
            next_time = sim_start + (step + 1) * (obs_duration - obs_overlap)
            from tudatpy.kernel import constants

            override_init_state = real_ephemeris[
                4.0 * constants.JULIAN_YEAR + (100 + next_time) * constants.JULIAN_DAY
            ]
            init_state_perturbation = get_state_diff(
                final_parameters, current_time, next_time
            )
            with open(
                f"out/BATCH_RESULTS_DSN_{['r','s','w'][init_diff_direction]}_1s.out",
                "a+",
            ) as f:
                f.write(
                    f"{current_time}, {np.sqrt(np.sum((final_parameters[0:3]-solution[0:3])**2))}, {np.sqrt(np.sum((final_parameters[3:6]-solution[3:6])**2))}, {', '.join([str(param) for param in final_parameters])}\n",
                )
