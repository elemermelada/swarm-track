from matplotlib import pyplot as plt
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
    # observation_times,
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
    noise=2e-4,
    obs_f=1.0,
):
    observation_times = np.arange(simulation_start_epoch, simulation_end_epoch, obs_f)
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


def init_plot():
    fig = plt.figure()

    gs = fig.add_gridspec(3, 3)
    ax1 = fig.add_subplot(gs[0, 0:3])
    ax2 = fig.add_subplot(gs[1, 0:3])
    ax3 = fig.add_subplot(gs[2, 0:3])
    axes = [ax1, ax2, ax3]

    return fig, axes


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


actual_observations_results, actual_observations, _ = simulate_observations(
    None, observe="MEX"
)
flawed_observations_results, flawed_observations, estimator = simulate_observations(
    initial_state_perturbation=np.array(
        [
            1e03,
            0e06,
            0e06,
            0e03,
            0e02,
            0e03,
        ]
    ),
    observe="MEX",
    noise=0.0,
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
final_observation_results, _, _ = simulate_observations(
    override_initial_state=final_parameters, noise=0.0, observe="MEX"
)
with open("out/timestamps_bench_DSN.out", "+a") as f:
    f.write(
        f"{(simulation_end_epoch-simulation_start_epoch)/86400}, {np.linalg.norm(final_parameters[0:3]-solution[0:3])}, {np.linalg.norm(final_parameters[3:6]-solution[3:6])}\n"
    )

fig2, axes = init_plot()
resu = observations_difference(actual_observations_results, final_observation_results)
show_obs(resu, axes, "b")
[ax.set_xlim([0, 1]) for ax in axes]
[ax.tick_params(axis="both", which="major", labelsize=14) for ax in axes]
fig2.tight_layout()
fig2.savefig("out/DSN_SENS_obs_1.0.svg")
fig2.show()

fig3, axes2 = init_plot()
noiseless_observation_results, _, _ = simulate_observations(noise=0.0, observe="MEX")
resu = observations_difference(final_observation_results, noiseless_observation_results)
show_obs(resu, axes2, "b")
[ax.set_xlim([0, 1]) for ax in axes2]
[ax.tick_params(axis="both", which="major", labelsize=14) for ax in axes2]
fig3.tight_layout()
fig3.savefig("out/DSN_SENS_obs_noiseless_1.0.svg")
fig3.show()
