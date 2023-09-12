import os
from observation.observation_postprocessing import observations_difference
from util.point_distributions import (
    add_error_to_coordinates,
    geo_2_cart,
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
)

from init.MEX_10TW import (
    simulation_start_epoch,
    simulation_end_epoch,
    bodies_to_propagate,
)
from util.math import vector_rms

import numpy as np

# dists = [pole_sphere, equatorial_sphere]
dist = fibonacci_sphere
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
for j in range(len(noise)):
    for i in range(12):
        USE_3D = True
        TW_NUMBER = twn[j]

        tw_stations = dist(TW_NUMBER, sigma=spread[j])
        tw_stations_cart = [
            geo_2_cart(coord, 3389526.6666666665) for coord in tw_stations
        ]

        ne_bodies = get_bodies()
        add_tw_stations(
            ne_bodies.get("Mars"), TW_NUMBER, lambda x: tw_stations_cart, cart=True
        )
        REAL_POSITION = [
            ne_bodies.get("Mars")
            .ground_station_list[f"TW{k}"]
            .station_state.cartesian_positon_at_reference_epoch
            for k in range(TW_NUMBER)
        ]
        FAKE_POSITION = REAL_POSITION

        tw_stations_wrapper = lambda err: (
            lambda x: add_error_to_coordinates(
                np.array(REAL_POSITION), 3389526.6666666665, err, cart=True
            )
        )

        observation_times = np.arange(
            simulation_start_epoch, simulation_end_epoch, freq[j]
        )

        def simulate_observations(
            initial_state_perturbation=None,
            observe=None,
            err=0.0,
        ):
            new_bodies = get_bodies()
            add_tw_stations(
                new_bodies.get("Mars"), TW_NUMBER, tw_stations_wrapper(err), cart=True
            )
            links = create_1w_tw_links(TW_NUMBER, "MEX" if observe is None else observe)

            global FAKE_POSITION
            FAKE_POSITION = [
                new_bodies.get("Mars")
                .ground_station_list[f"TW{k}"]
                .station_state.cartesian_positon_at_reference_epoch
                for k in range(TW_NUMBER)
            ]
            print(
                vector_rms(
                    np.array(
                        [
                            np.mean(REAL_POSITION[i] - FAKE_POSITION[i])
                            for i in range(len(REAL_POSITION))
                        ]
                    )
                )
            )
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
                simulation_start_epoch,
                simulation_end_epoch,
                new_bodies,
                bodies_to_propagate,
                ["Mars"],
                initial_state_error=0.0,
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
                    1e3,
                    0e3,
                    0e3,
                    0e0,
                    0e0,
                    0e0,
                ]
            ),
            observe="MEX",
            err=error[j],
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
            ephemeris_time=simulation_start_epoch,
        )
        result = estimate(estimator, actual_observations)
        final_parameters = np.array(result.parameter_history)[:, -1]

        path = f"out"
        if not os.path.exists(path):
            os.makedirs(path)
        with open(
            f"{path}/SINGLE_RESULTS_TW_{dist.__name__}_{TW_NUMBER}_{spread[j]}_{freq[j]}_{error[j]}_{noise[j]}.out",
            "+a",
        ) as f:
            f.write(
                f"{(simulation_end_epoch-simulation_start_epoch)/86400}, {np.sqrt(np.sum((final_parameters[0:3]-solution[0:3])**2))}, {np.sqrt(np.sum((final_parameters[3:6]-solution[3:6])**2))}, {vector_rms(result.final_residuals)}, {', '.join([str(eph) for eph in final_parameters])}\n"
            )
