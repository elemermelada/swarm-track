from util.environment_setup import add_dsn_stations, get_bodies
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
    create_1w_dsn_links,
    create_simple_1w_doppler_range_sensors,
    create_simple_1w_doppler_sensors,
    create_simple_1w_range_sensors,
)

from estimation.estimation_setup import (
    create_gravimetry_parameters_to_estimate,
)
from estimation.estimation import (
    create_estimator,
    estimate,
)

from init.MEX_DSN import (
    simulation_start_epoch,
    simulation_end_epoch,
    observation_times,
    dsn_antennae_names,
    bodies_to_propagate,
)
from util.math import vector_rms
from util.propagation import retrieve_propagated_state_history
import numpy as np
from tudatpy.kernel.numerical_simulation import estimation

USE_3D = True


new_bodies = get_bodies()
add_dsn_stations(new_bodies.get_body("Earth"))


def simulate_observations(
    initial_state_perturbation=None,
    override_initial_state=None,
    observe=None,
):
    links = create_1w_dsn_links(observe, dsn_antennae_names)

    # General observation settings
    # light_time_correction_settings = (
    # observation.first_order_relativistic_light_time_correction(["Sun"])
    # )
    # add_radiation_pressure(new_bodies, {"name": "Sens"})

    # Add doppler "sensors"
    # (
    #     new_observation_settings_list,
    #     new_observation_simulation_settings,
    #     observable_type,
    # ) = create_simple_1w_doppler_range_sensors(
    #     links,
    #     None,
    #     observation_times,
    #     lambda observation_type, elevation_angle, observation_simulation_settings, links: add_dsn_viability_check(
    #         observation_type,
    #         elevation_angle,
    #         observation_simulation_settings,
    #         links,
    #         dsn_antennae_names,
    #         fake=True if observe == "Mars" else False,
    #     ),
    #     doppler_noise=2e-4,
    #     range_noise=2e-2,
    # )
    from tudatpy.kernel.numerical_simulation.estimation_setup import observation

    observation_settings_list = [
        observation.one_way_doppler_instantaneous(link) for link in links
    ] + [observation.one_way_range(link) for link in links]

    observation_simulation_settings1 = [
        observation.tabulated_simulation_settings(
            observation.one_way_instantaneous_doppler_type, link, observation_times
        )
        for link in links
    ]
    observation_simulation_settings2 = [
        observation.tabulated_simulation_settings(
            observation.one_way_range_type, link, observation_times
        )
        for link in links
    ]

    observation_simulation_settings = (
        observation_simulation_settings1 + observation_simulation_settings2
    )

    noise_level = 2e-4
    observation.add_gaussian_noise_to_observable(
        observation_simulation_settings1,
        noise_level,
        observation.one_way_instantaneous_doppler_type,
    )
    noise_level = 2e-2
    observation.add_gaussian_noise_to_observable(
        observation_simulation_settings2,
        noise_level,
        observation.one_way_range_type,
    )

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
        observation_settings_list,
        propagator_settings_estimation,
    )

    # Get simulated observations as ObservationCollection
    simulated_observations = estimation.simulate_observations(
        observation_simulation_settings,
        estimator.observation_simulators,
        new_bodies,
    )

    return (
        [
            antenna_results[-1].observations_history
            for antenna_results in simulated_observations.sorted_observation_sets[
                observation.one_way_range_type
            ].values()
        ],
        simulated_observations,
        estimator,
    )


fig2, axes = init_observation_plot()


def show_obs(sim_obs, axes, color, scatter=True, which=None):
    sim_obs, _, _ = sim_obs
    obs_count = len(sim_obs)
    ant_count = len(dsn_antennae_names)
    mult = int(obs_count / ant_count)
    for i in range(ant_count):
        filtered_observations = sim_obs[mult * (i) if which is None else which[i]]
        plot_observations(
            axes[i],
            filtered_observations,
            start_date=simulation_start_epoch,
            # color=colors[i],
            color=color,
            scatter=scatter,
            title=dsn_antennae_names[i],
        )

    return axes


_, actual_observations, _ = simulate_observations(None, observe="MEX")
_, flawed_observations, estimator = simulate_observations(
    override_initial_state=np.array(
        [
            4.02623428e06,
            -5.57611567e06,
            5.55648914e06,
            1.02260251e03,
            5.05921148e02,
            1.94561622e03,
        ]
    ),
    observe="MEX",
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
with open("out/timestamps_bench_DSN.out", "+a") as f:
    f.write(
        f"{(simulation_end_epoch-simulation_start_epoch)/86400}, {np.linalg.norm(final_parameters[0:3]-solution[0:3])}, {np.linalg.norm(final_parameters[3:6]-solution[3:6])}\n"
    )

fig2.tight_layout()
# fig2.savefig("out/DSN_SENS_obs.svg")
fig2.show()
