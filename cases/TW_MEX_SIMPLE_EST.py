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
from util.math import vector_rms
from util.point_distributions import (
    add_error_to_coordinates,
    equatorial_sphere,
    fibonacci_sphere,
)
from util.propagation import retrieve_propagated_state_history

import numpy as np

USE_3D = True
TW_NUMBER = tw_number

tw_stations = equatorial_sphere(TW_NUMBER)
tw_stations_wrapper = lambda err: (
    lambda x: add_error_to_coordinates(tw_stations, 3389.5e3, err)
)


def simulate_observations(
    initial_state_perturbation=None,
    observe=None,
    err=0.0,
):
    new_bodies = get_bodies(
        simulation_start_epoch,
        simulation_end_epoch,
    )
    add_tw_stations(new_bodies.get("Mars"), TW_NUMBER, tw_stations_wrapper(err))
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
        noise=5e-2,
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


_, actual_observations, _ = simulate_observations(None, observe="MEX")
_, flawed_observations, estimator = simulate_observations(
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
    err=5e-2,
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
with open("out/timestamps_bench_TW.out", "+a") as f:
    f.write(
        f"{(simulation_end_epoch-simulation_start_epoch)/86400}, {vector_rms(final_parameters[0:3]-solution[0:3])}, {vector_rms(final_parameters[3:6]-solution[3:6])}\n"
    )
