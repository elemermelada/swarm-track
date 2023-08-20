from util.environment_setup import get_bodies
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
)
from util.propagation import retrieve_propagated_state_history


USE_3D = True


def simulate_observations(
    initial_state=None,
    premultiplied_mars_harmonics=None,
    verbose=False,
    observe=None,
    a=5000,
):
    import numpy as np

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
    # TODO - refactor this pls
    from tudatpy.kernel.numerical_simulation import environment_setup

    stations = environment_setup.ground_station.dsn_stations()
    for station in stations:
        environment_setup.add_ground_station(new_bodies.get_body("Earth"), station)
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
        ),
        noise=0.0,
    )

    if initial_state is None:
        R = a * 1e3
        TYPE = 1
        MU = new_bodies.get("Mars").gravitational_parameter

        x_E = (
            new_bodies.get("Earth").ephemeris.get_cartesian_state(
                simulation_start_epoch
            )[0:3]
            - new_bodies.get("Mars").ephemeris.get_cartesian_state(
                simulation_start_epoch
            )[0:3]
        )
        v1 = np.array([x_E[1], -x_E[0], 0])
        v1 = np.sign(R) * v1 / np.linalg.norm(v1)
        v2 = TYPE * np.cross(x_E, v1) / np.linalg.norm(np.cross(x_E, v1))

        r = v1 * np.abs(R)
        v = v2 * np.sqrt(MU / np.abs(R))
        initial_state = np.concatenate((r, v))

    # override_mars_harmonics.normalized_cosine_coefficients[]
    propagator_settings_estimation = basic_propagator(
        simulation_start_epoch,
        simulation_end_epoch,
        new_bodies,
        bodies_to_propagate,
        ["Mars"],
        initial_state_error=0.0,
        override_initial_state=initial_state,
        # gravity_order=gravity_order,
    )

    ### Propagate to see wassup
    ax, fig = init_trajectory_graph(threeD=USE_3D)
    state_history, time_vector = retrieve_propagated_state_history(
        propagator_settings_estimation, new_bodies, True
    )
    plot_ephemeris(ax, state_history * 1e-3, threeD=USE_3D, color="r")
    plot_mars(ax, threeD=USE_3D)
    fig.show()

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
    # Creating some plots here...
    v1 = [
        new_bodies.get("Earth").ephemeris.get_cartesian_state(t)[0:6]
        for t in time_vector
    ]
    v2b = [
        new_bodies.get("Mars").ephemeris.get_cartesian_state(t)[0:6]
        for t in time_vector
    ]
    v2 = [s[0:6] for s in state_history]
    v2 = [v2[i] + v2b[i] for i in range(len(v2))]  # Add mars to orbiter ephemeris
    v3 = [
        np.dot(v1[i][0:3] - v2[i][0:3], v1[i][3:6] - v2[i][3:6])
        / np.linalg.norm(v1[i][0:3] - v2[i][0:3])
        for i in range(len(v1))
    ]
    v3b = [
        np.dot(v1[i][0:3] - v2b[i][0:3], v1[i][3:6] - v2b[i][3:6])
        / np.linalg.norm(v1[i][0:3] - v2b[i][0:3])
        for i in range(len(v1))
    ]
    # aaa = [v3[i] - v3b[i] for i in range(len(v3))]
    # aaa = {key: value for key, value in zip(time_vector, aaa)}
    obs = {key: value for key, value in zip(time_vector, v3)}
    obsb = {key: value for key, value in zip(time_vector, v3b)}
    fig, ax = init_observation_plot(n_axes=1)
    plot_observations(ax[0], obs, simulation_start_epoch)
    plot_observations(ax[0], obsb, simulation_start_epoch, color="r")
    fig.show()

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
    for i in range(3):
        filtered_observations = sim_obs[mult * (i + 1) - 1]
        plot_observations(
            axes[i],
            filtered_observations,
            start_date=simulation_start_epoch,
            # color=colors[i],
            color=color,
            scatter=scatter,
        )

    return axes


show_obs(simulate_observations(None, observe="Mars"), axes, "r", scatter=False)
show_obs(simulate_observations(None, observe="Sens", a=15000), axes, "b")
show_obs(simulate_observations(None, observe="Sens", a=-15000), axes, "g")
fig2.show()
