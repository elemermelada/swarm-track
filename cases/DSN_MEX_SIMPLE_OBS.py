from observation.observation_postprocessing import observations_difference
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
    create_simple_1w_doppler_sensors,
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
    noise=0.0,
):
    links = create_1w_dsn_links(observe, dsn_antennae_names)

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
        lambda observation_type, elevation_angle, observation_simulation_settings, links: add_dsn_viability_check(
            observation_type,
            elevation_angle,
            observation_simulation_settings,
            links,
            dsn_antennae_names,
            fake=True if observe == "Mars" else False,
        ),
        noise=noise,
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
        # axes[i].legend()

    return axes


real_obs = simulate_observations(None, observe="MEX", noise=2e-4)
fake_obs = simulate_observations(
    # initial_state_perturbation=np.array(
    #     [
    #         # 0 * -2.62e3 + 0 * 2.68e3 + 1e3,
    #         # 0 * -1.85e3 + 0 * 1.8e3 + 1e3,
    #         # 0 * -1.93e3 + 0 * 1.95e3 + 1e3,
    #         # 1e0,
    #         # 1e0,
    #         # 1e0,
    #     ]
    # ),
    # override_initial_state=np.array(
    #     # [
    #     #     4.02623428e06,
    #     #     -5.57611567e06,
    #     #     5.55648914e06,
    #     #     1.02260251e03,
    #     #     5.05921148e02,
    #     #     1.94561622e03,
    #     # ]
    #     [
    #         4.02619372e06,
    #         -5.57611563e06,
    #         5.55651868e06,
    #         1.02259397e03,
    #         5.05922068e02,
    #         1.94562045e03,
    #     ]
    # ),
    observe="MEX",
)

fig, axes = init_observation_plot()

show_obs(real_obs, axes, "k")
show_obs(
    fake_obs,
    axes,
    "r",
)
show_obs(
    simulate_observations(None, observe="Mars"),
    axes,
    "r",
    scatter=False,
)


fig.tight_layout()
fig.savefig("out/DSN_MEX_SIMPLE_obs.svg")
fig.show()

fig2, axes2 = init_observation_plot()

show_obs(
    observations_difference(real_obs[0], fake_obs[0]),
    axes2,
    "b",
)

fig2.tight_layout()
fig2.savefig("out/DSN_MEX_SIMPLE_res_noise_good.svg")
fig2.show()
