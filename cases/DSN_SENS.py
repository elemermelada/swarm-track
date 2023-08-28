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
)

from init.SENS import (
    simulation_start_epoch,
    simulation_end_epoch,
    observation_times,
    dsn_antennae_names,
    bodies_to_propagate,
    ORBIT_A,
)
from util.propagation import retrieve_propagated_state_history
import numpy as np
from tudatpy.kernel.numerical_simulation import estimation

fig_ax = None
USE_3D = True


def plot_doppler_effect(new_bodies, state_history, time_vector, fig_ax=None):
    earth_ephemeris = [
        new_bodies.get("Earth").ephemeris.get_cartesian_state(t)[0:6]
        for t in time_vector
    ]
    mars_ephemeris = [
        new_bodies.get("Mars").ephemeris.get_cartesian_state(t)[0:6]
        for t in time_vector
    ]
    orbiter_ephemeris = [
        state_history[i] + mars_ephemeris[i] for i in range(len(state_history))
    ]  # Add mars to orbiter ephemeris
    doppler_orbiter_from_earth = [
        np.dot(
            earth_ephemeris[i][0:3] - orbiter_ephemeris[i][0:3],
            earth_ephemeris[i][3:6] - orbiter_ephemeris[i][3:6],
        )
        / np.linalg.norm(earth_ephemeris[i][0:3] - orbiter_ephemeris[i][0:3])
        for i in range(len(earth_ephemeris))
    ]
    doppler_mars_from_earth = [
        np.dot(
            earth_ephemeris[i][0:3] - mars_ephemeris[i][0:3],
            earth_ephemeris[i][3:6] - mars_ephemeris[i][3:6],
        )
        / np.linalg.norm(earth_ephemeris[i][0:3] - mars_ephemeris[i][0:3])
        for i in range(len(earth_ephemeris))
    ]
    orbiter_observations = {
        key: value for key, value in zip(time_vector, doppler_orbiter_from_earth)
    }
    mars_observations = {
        key: value for key, value in zip(time_vector, doppler_mars_from_earth)
    }
    color = "b"
    if fig_ax is None:
        fig, ax = init_observation_plot(n_axes=1)
    else:
        color = "g"
        fig, ax = fig_ax
    plot_observations(
        ax[0],
        {
            t: orbiter_observations[t] - mars_observations[t]
            for t in list(orbiter_observations.keys())
        },
        simulation_start_epoch,
        marker="o",
        color=color,
    )
    # plot_observations(
    #     ax[0], mars_observations, simulation_start_epoch, color="r", marker="o"
    # )
    return fig, ax


def create_initial_state(R, TYPE, new_bodies):
    MU = new_bodies.get("Mars").gravitational_parameter

    x_E = (
        new_bodies.get("Earth").ephemeris.get_cartesian_state(simulation_start_epoch)[
            0:3
        ]
        - new_bodies.get("Mars").ephemeris.get_cartesian_state(simulation_start_epoch)[
            0:3
        ]
    )
    earth_ephemeris = np.array([x_E[1], -x_E[0], 0])
    earth_ephemeris = np.sign(R) * earth_ephemeris / np.linalg.norm(earth_ephemeris)
    orbiter_ephemeris = (
        TYPE
        * np.cross(x_E, earth_ephemeris)
        / np.linalg.norm(np.cross(x_E, earth_ephemeris))
    )

    r = earth_ephemeris * np.abs(R)
    v = orbiter_ephemeris * np.sqrt(MU / np.abs(R))
    return np.concatenate((r, v))


def simulate_observations(
    initial_state=None,
    premultiplied_mars_harmonics=None,
    verbose=False,
    observe=None,
    a=5000,
):
    mars_harmonics = (
        np.array(premultiplied_mars_harmonics) * 1e-3
        if not premultiplied_mars_harmonics is None
        else None
    )
    if verbose:
        print("Evaluate x:", mars_harmonics)
    override_mars_harmonics = None

    override_mars_harmonics = dict(
        normalized_cosine_coefficients=np.full((5, 5), None),
        normalized_sine_coefficients=np.full((5, 5), None),
    )

    if not mars_harmonics is None:
        override_mars_harmonics["normalized_cosine_coefficients"][2][
            1:3
        ] = mars_harmonics[0:2]
        override_mars_harmonics["normalized_sine_coefficients"][2][
            0:3
        ] = mars_harmonics[2:5]

    new_bodies = get_bodies(
        simulation_start_epoch,
        simulation_end_epoch,
        override_mars_harmonics=override_mars_harmonics,
        extra_body={"name": "Sens"},
    )
    add_dsn_stations(new_bodies.get_body("Earth"))
    links = create_1w_dsn_links(
        "Sens" if observe is None else observe, dsn_antennae_names
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

    if initial_state is None:
        R = a * 1e3
        TYPE = 1
        initial_state = create_initial_state(R, TYPE, new_bodies)

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

    ### Propagate to see wassup
    # ax, fig = init_trajectory_graph(threeD=USE_3D)
    state_history, time_vector = retrieve_propagated_state_history(
        propagator_settings_estimation, new_bodies, True
    )
    # plot_ephemeris(ax, state_history * 1e-3, threeD=USE_3D, color="r")
    # plot_mars(ax, threeD=USE_3D)
    # fig.show()

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

    # Creating some plots here...
    if not observe == "Mars":
        global fig_ax
        fig_ax = plot_doppler_effect(
            new_bodies, state_history, time_vector, fig_ax=fig_ax
        )

    return [
        antenna_results[-1].observations_history
        for antenna_results in simulated_observations.sorted_observation_sets[
            observable_type
        ].values()
    ]


fig2, axes = init_observation_plot()


def show_obs(sim_obs, axes, color, scatter=True):
    obs_count = len(sim_obs)
    ant_count = len(dsn_antennae_names)
    mult = int(obs_count / ant_count)
    for i in range(ant_count):
        filtered_observations = sim_obs[mult * (i + 1) - 1]
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


show_obs(simulate_observations(None, observe="Mars"), axes, "r", scatter=False)
show_obs(simulate_observations(None, observe="Sens", a=ORBIT_A), axes, "b")
show_obs(simulate_observations(None, observe="Sens", a=-ORBIT_A), axes, "g")
fig2.tight_layout()
fig2.savefig("out/DSN_SENS_obs.svg")
fig2.show()

fig, ax = fig_ax
fig.tight_layout()
fig.savefig("out/DSN_SENS_Doppler.svg")
fig.show()
