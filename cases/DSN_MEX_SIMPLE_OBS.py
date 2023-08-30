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


new_bodies = get_bodies(
    simulation_start_epoch,
    simulation_end_epoch,
)
add_dsn_stations(new_bodies.get_body("Earth"))


def simulate_observations(
    initial_state=None,
    observe=None,
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
        noise=0.0,
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
        axes[i].legend()

    return axes


show_obs(simulate_observations(None, observe="MEX"), axes, "k", which=[0, 1, 2])
show_obs(
    simulate_observations(None, observe="Mars"),
    axes,
    "r",
    scatter=False,
    which=[1, 3, 5],
)

fig2.tight_layout()
fig2.savefig("out/DSN_MEX_SIMPLE_obs.svg")
fig2.show()
