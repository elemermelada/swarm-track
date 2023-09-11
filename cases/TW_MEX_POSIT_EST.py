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
    create_positioning_parameters_to_estimate,
)
from estimation.estimation import (
    create_estimator,
    estimate,
)

from init.MEX_10TW import (
    simulation_start_epoch,
    simulation_end_epoch,
    bodies_to_propagate,
)
from util.math import vector_rms

import numpy as np

# dists = [pole_sphere, equatorial_sphere]
dist = pole_sphere
twn = [90, 30, 90, 90, 90, 90]
spread = [30.0, 30.0, 5.0, 30.0, 30.0, 30.0]
freq = [10.0, 10.0, 10.0, 30.0, 10.0, 10.0]
error = [1e-1, 1e-1, 1e-1, 1e-1, 2e0, 1e-1]
noise = [
    5e-2,
    5e-2,
    5e-2,
    5e-2,
    5e-2,
    5e-3,
]
twn = [90]
spread = [30.0]
freq = [30.0]
error = [0e-1]
noise = [5e-2]
for j in range(len(noise)):
    TW_NUMBER = twn[0]

    tw_stations = dist(TW_NUMBER, sigma=spread[j])
    new_bodies = get_bodies()
    add_tw_stations(new_bodies.get("Mars"), TW_NUMBER, lambda x: tw_stations)
    REAL_POSITION = [
        new_bodies.get("Mars")
        .ground_station_list[f"TW{k}"]
        .station_state.cartesian_positon_at_reference_epoch
        for k in range(TW_NUMBER)
    ]

    erraneous_beacons = add_error_to_coordinates(
        REAL_POSITION, 3389526.6666666665, 1e-1, cart=True
    )

    FAKE_POSITION = add_error_to_coordinates(
        erraneous_beacons, 3389526.6666666665, 1e1, indeces=[4], cart=True
    )

    for i in range(12):
        simulation_start_epocha = simulation_start_epoch + 1.5 * 86400 * i
        simulation_end_epocha = simulation_end_epoch + 1.5 * 86400 * i
        observation_times = np.arange(
            simulation_start_epocha,
            simulation_end_epocha,
            freq[j],
        )

        def simulate_observations(
            initial_state_perturbation=None,
            observe=None,
            err=0.0,
        ):
            new_bodies = get_bodies()
            stat = REAL_POSITION if err == 0.0 else FAKE_POSITION
            add_tw_stations(
                new_bodies.get("Mars"), TW_NUMBER, lambda x: stat, cart=True
            )
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
                noise=noise[j],
            )

            # override_mars_harmonics.normalized_cosine_coefficients[]
            propagator_settings_estimation = basic_propagator(
                simulation_start_epocha,
                simulation_end_epocha,
                new_bodies,
                bodies_to_propagate,
                ["Mars"],
                initial_state_error=0.0,
                initial_state_perturbation=initial_state_perturbation,
                # gravity_order=0,
            )

            parameters_to_estimate = create_positioning_parameters_to_estimate(
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

        (
            actual_observations_results,
            actual_observations,
            _,
        ) = simulate_observations(None, observe="MEX")
        (
            flawed_observations_results,
            flawed_observations,
            estimator,
        ) = simulate_observations(
            initial_state_perturbation=np.array(
                [
                    0.01e3,
                    0e3,
                    0e3,
                    0e0,
                    0e0,
                    0e0,
                ]
            ),
            observe="MEX",
            err=error[j] + 1,
        )
        obs_diff = observations_difference(
            actual_observations_results, flawed_observations_results
        )
        print(
            vector_rms(
                np.concatenate(
                    [[l[0] for l in v] for v in [list(t.values()) for t in obs_diff[0]]]
                )
            )
        )
        from tudatpy.kernel.interface import spice

        solution = spice.get_body_cartesian_state_at_epoch(
            target_body_name=bodies_to_propagate[0],
            observer_body_name="Mars",
            reference_frame_name="J2000",
            aberration_corrections="none",
            ephemeris_time=simulation_start_epocha,
        )
        result = estimate(estimator, actual_observations)
        final_parameters = np.array(result.parameter_history)[:, -1]

        from util.point_distributions import geo_2_cart

        station_position = geo_2_cart(tw_stations[0], 3389526.6666666665)

        path = f"out/"
        if not os.path.exists(path):
            os.makedirs(path)
        with open(
            f"{path}/POSIT_RESULTS_TW_{dist.__name__}_{TW_NUMBER}_{spread[j]}_{freq[j]}_{error[j]}_{noise[j]}.out",
            "+a",
        ) as f:
            f.write(
                f"{(simulation_end_epocha-simulation_start_epocha)/86400}, {np.sqrt(np.sum((final_parameters[0:3]-solution[0:3])**2))}, {np.sqrt(np.sum((final_parameters[3:6]-solution[3:6])**2))}, {vector_rms(result.final_residuals)}, {', '.join([str(eph) for eph in final_parameters])}, {', '.join([str(REAL_POSITION[4][k]-FAKE_POSITION[4][k]) for k in range(len(REAL_POSITION[4]))])}, {', '.join([str(REAL_POSITION[4][k]-final_parameters[6+k]) for k in range(len(REAL_POSITION[4]))])}\n"
            )
