from observation.observation_postprocessing import (
    retrieve_observations_with_link,
)
from optimization.optimizers import (
    GeneticOptimizer,
    SLSQPOptimizer,
    TrustRegionOptimizer,
)
from util.environment_setup import add_radiation_pressure, add_tw_stations, get_bodies
from util.dynamical_models import basic_propagator
from util.graphs import (
    init_observation_plot,
    init_trajectory_graph,
    plot_ephemeris,
    plot_mars,
    plot_observations,
    plot_trajectory_from_spice,
    scatter_ephemeris,
)

from observation.observation_setup import (
    add_tw_viability_check,
    create_1w_tw_links,
    create_simple_1w_doppler_sensors,
    create_simple_2w_doppler_sensors,
)
from observation.observation import perform_observations

from estimation.estimation_setup import (
    create_gravimetry_parameters_to_estimate,
    create_simple_parameters_to_estimate,
)
from estimation.estimation import (
    create_estimator,
    estimate,
    get_ephemeris_residuals_from_spice,
)
from estimation.estimation_postprocessing import retrieve_best_iteration_state_history

from init.MEX_10TW import (
    simulation_start_epoch,
    simulation_end_epoch,
    observation_times,
    tw_number,
)
from util.math import observations_rms, vector_rms
from util.point_distributions import fibonacci_sphere

from util.propagation import retrieve_propagated_state_history

USE_3D = True

# Add radiation pressure to environment

# Create trajectory plot + mars
# ax, fig = init_trajectory_graph(threeD=USE_3D)
# ax = plot_trajectory_from_spice(
#     ax, "MEX", simulation_start_epoch, simulation_end_epoch, axis=[1, 2], threeD=USE_3D
# )
# ax = plot_mars(ax, USE_3D)
# fig.show()

# Add doppler "sensors"


def simulate_observations(
    initial_state=None, premultiplied_mars_harmonics=None, verbose=False
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
    )
    # TODO - refactor this pls
    # Add TW stations and create links to MEX

    from tudatpy.kernel.numerical_simulation import environment_setup
    from tudatpy.kernel.numerical_simulation.estimation_setup import observation

    add_tw_stations(
        environment_setup, new_bodies.get("Mars"), tw_number, fibonacci_sphere
    )
    links = create_1w_tw_links(tw_number, "MEX")

    # General observation settings
    light_time_correction_settings = (
        observation.first_order_relativistic_light_time_correction(["Sun"])
    )
    add_radiation_pressure(new_bodies)

    # Add doppler "sensors"
    (
        new_observation_settings_list,
        new_observation_simulation_settings,
        observable_type,
    ) = create_simple_1w_doppler_sensors(
        links,
        light_time_correction_settings,
        observation_times,
        lambda observation_type, elevation_angle, observation_simulation_settings, links: add_tw_viability_check(
            observation_type,
            elevation_angle,
            observation_simulation_settings,
            links,
        ),
        noise=0.0,
    )

    # override_mars_harmonics.normalized_cosine_coefficients[]
    propagator_settings_estimation = basic_propagator(
        simulation_start_epoch,
        simulation_end_epoch,
        new_bodies,
        ["MEX"],
        ["Mars"],
        initial_state_error=0.0,
        override_initial_state=initial_state,
        # gravity_order=gravity_order,
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
    return [
        antenna_results[-1].observations_history
        for antenna_results in simulated_observations.sorted_observation_sets[
            observable_type
        ].values()
    ]


simulated_observations = simulate_observations(None)


fig2, axes = init_observation_plot(n_axes=tw_number)


def show_obs(sim_obs, axes, color):
    for i in range(tw_number):
        filtered_observations = sim_obs[i]
        plot_observations(
            axes[i],
            filtered_observations,
            start_date=simulation_start_epoch,
            # color=colors[i],
            color=color,
        )

    return axes


show_obs(simulated_observations, axes, "b")
# show_obs(
#     simulate_observations(
#         # [
#         #     4026192.294916528 + 100000,
#         #     -5576115.619678646,
#         #     5556519.733279885,
#         #     1022.5936681553791,
#         #     505.9221023735916,
#         #     1945.6205952667945,
#         # ]
#         gravity_order=2
#     ),
#     axes,
#     "r",
# )
fig2.show()

original_observations = simulated_observations


res = TrustRegionOptimizer(
    lambda x: observations_rms(
        simulate_observations(None, premultiplied_mars_harmonics=(x), verbose=True),
        original_observations,
    ),
    [
        # 0,
        0,
        0,
        0,
        0,
        0,
    ],  # [-0.0008750220924537, 4.022333306382e-10, -8.463302655983e-05, 0.0, 2.303183853552e-11, 4.893941832167e-05]
    # [ 2.23079627e-06 -8.64962661e-05 -2.08299621e-22 -7.91584821e-06 6.64807499e-05]
    [
        # -1e0,
        -1e0,
        -1e0,
        -1e0,
        -1e0,
        -1e0,
    ],
    [
        # -6e-1,
        1e0,
        1e0,
        1e0,
        1e0,
        1e0,
    ],
)

# res = TrustRegionOptimizer(
#     lambda x: vector_rms(
#         simulate_observations(x).concatenated_observations - concatenated_observations
#     ),
#     [
#         4026192.294916528 + 100000,
#         -5576115.619678646,
#         5556519.733279885,
#         1022.5936681553791,
#         505.9221023735916,
#         1945.6205952667945,
#     ],
#     [
#         -1e7,
#         -1e7,
#         -1e7,
#         -1e4,
#         -1e4,
#         -1e4,
#     ],
#     [
#         1e7,
#         1e7,
#         1e7,
#         1e4,
#         1e4,
#         1e4,
#     ],
# )

print(res.x)

# estimation_output = estimate(estimator, simulated_observations, max_iters=10)

# state_history = retrieve_best_iteration_state_history(estimation_output, clean=True)
# ax = plot_ephemeris(ax, state_history * 1e-3, threeD=USE_3D, color="k", linestyle="--")
# ax.legend()
# fig.tight_layout()
# fig.savefig("out/estimate.png")
# fig.show()
