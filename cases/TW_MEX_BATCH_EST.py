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

from util.propagation import retrieve_propagated_state_history

# dists = [pole_sphere, equatorial_sphere]
dist = pole_sphere
print(dist.__name__)
twn = [90, 30, 90, 90, 90, 90]
spread = [30.0, 30.0, 5.0, 30.0, 30.0, 30.0]
freq = [10.0, 10.0, 10.0, 30.0, 10.0, 10.0]
error = [1e-1, 1e-1, 1e-1, 1e-1, 10e0, 1e-1]
noise = [
    5e-2,
    5e-2,
    5e-2,
    5e-2,
    5e-2,
    5e-3,
]
sl = 0
twn = [twn[sl]]
spread = [spread[sl]]
freq = [freq[sl]]
error = [error[sl]]
noise = [noise[sl]]
# twn = [90]
# spread = [30.0]
# freq = [10.0]
# error = [1e-1]
# noise = [5e-2]
j = 0
TW_NUMBER = twn[j]

tw_stations = dist(TW_NUMBER, sigma=spread[j])
tw_stations_cart = [geo_2_cart(coord, 3389526.6666666665) for coord in tw_stations]

ne_bodies = get_bodies()
add_tw_stations(ne_bodies.get("Mars"), TW_NUMBER, lambda x: tw_stations_cart, cart=True)
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

propagator_settings_estimation = basic_propagator(
    simulation_start_epoch + (0),
    simulation_end_epoch + 0.8 * 86400 * 12,
    ne_bodies,
    bodies_to_propagate,
    ["Mars"],
    initial_state_error=0.0,
    # gravity_order=0,
)

real_state_history, _ = retrieve_propagated_state_history(
    propagator_settings_estimation, ne_bodies, False
)

for i in range(12):

    def simulate_observations(
        initial_state_perturbation=None,
        observe=None,
        err=0.0,
        step=0,
        override_initial_state=None,
    ):
        observation_times = np.arange(
            simulation_start_epoch + 0.8 * 86400 * step,
            simulation_end_epoch + 0.8 * 86400 * step,
            freq[j],
        )
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
            simulation_start_epoch
            + (
                0
                if override_initial_state is None and initial_state_perturbation is None
                else 0.8 * 86400 * step
            ),
            simulation_end_epoch + 0.8 * 86400 * step,
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
            propagator_settings_estimation,
        )

    new_init = None

    (
        actual_observations_results,
        actual_observations,
        _,
        _,
    ) = simulate_observations(None, observe="MEX", step=i)
    (
        flawed_observations_results,
        flawed_observations,
        estimator,
        _,
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
            if new_init is None
            else None
        ),
        observe="MEX",
        err=error[j],
        step=i,
        override_initial_state=new_init,
    )
    obs_diff = observations_difference(
        actual_observations_results, flawed_observations_results
    )
    from tudatpy.kernel.interface import spice

    result = estimate(estimator, actual_observations)
    final_parameters = np.array(result.parameter_history)[:, -1]
    # override_mars_harmonics.normalized_cosine_coefficients[]
    propagator_settings_estimation = basic_propagator(
        simulation_start_epoch + 0.8 * 86400 * i,
        simulation_end_epoch + 0.8 * 86400 * i,
        ne_bodies,
        bodies_to_propagate,
        ["Mars"],
        initial_state_error=0.0,
        override_initial_state=final_parameters,
    )

    ### Propagate to see wassup
    # ax, fig = init_trajectory_graph(threeD=USE_3D)

    state_history, time_vector = retrieve_propagated_state_history(
        propagator_settings_estimation, ne_bodies, False
    )
    next_init = state_history[simulation_start_epoch + 0.8 * 86400 * (i + 1)]

    solution = real_state_history[simulation_start_epoch + 0.8 * 86400 * (i)]
    path = f"out"
    if not os.path.exists(path):
        os.makedirs(path)
    with open(
        f"{path}/BATCH_RESULTS_TW_{dist.__name__}_{TW_NUMBER}_{spread[j]}_{freq[j]}_{error[j]}_{noise[j]}.out",
        "+a",
    ) as f:
        f.write(
            f"{0.8*i}, {np.sqrt(np.sum((final_parameters[0:3]-solution[0:3])**2))}, {np.sqrt(np.sum((final_parameters[3:6]-solution[3:6])**2))}, {vector_rms(result.final_residuals)}, {', '.join([str(eph) for eph in final_parameters])}\n"
        )
