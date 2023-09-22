import numpy as np
from tudatpy.kernel import constants
from tudatpy.kernel.interface import spice

from estimation.estimation import create_estimator
from estimation.estimation_setup import create_gravimetry_parameters_to_estimate
from observation.observation_postprocessing import (
    ephemeris_difference,
    observations_difference,
)

from observation.observation_setup import (
    add_dsn_viability_check,
    create_1w_dsn_links,
    create_simple_1w_doppler_sensors,
)
from util.dynamical_models import basic_propagator
from util.environment_setup import add_dsn_stations, get_bodies

from init.MEX_DSN import (
    observation_times,
    dsn_antennae_names,
    bodies_to_propagate,
)
from util.graphs import init_observation_plot
from util.propagation import retrieve_propagated_state_history

new_bodies = get_bodies()
add_dsn_stations(new_bodies.get_body("Earth"))


def simulate_observations(
    initial_state_perturbation=None,
    override_initial_state=None,
    observe=None,
    start_day=0.0,
    duration=0.5,
    noise=0.0,
):
    from tudatpy.kernel import constants

    # Set simulation start (January 1st, 2004 - 00:00) and end epochs (January 11th, 2004 - 00:00)
    simulation_start_epoch = (
        4.0 * constants.JULIAN_YEAR + (100 + start_day) * constants.JULIAN_DAY
    )
    simulation_duration = duration * constants.JULIAN_DAY
    simulation_end_epoch = simulation_start_epoch + simulation_duration
    observation_times = np.arange(simulation_start_epoch, simulation_end_epoch, 60.0)

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
        propagator_settings_estimation,
        estimator,
    )


duration = 1.0

data = np.loadtxt("out/BATCH_RESULTS_DSN_r_1s.out", delimiter=",", dtype=float)
initial_dates = data[:, 0]
initial_epochs = np.array(
    [
        4.0 * constants.JULIAN_YEAR + (100 + start_day) * constants.JULIAN_DAY
        for start_day in initial_dates
    ]
)
initial_states = data[:, 3:9]

real_initial_state = spice.get_body_cartesian_state_at_epoch(
    target_body_name="MEX",
    observer_body_name="Mars",
    reference_frame_name="J2000",
    aberration_corrections="none",
    ephemeris_time=initial_epochs[0],
)
real_observations, propagator_settings_estimation, _ = simulate_observations(
    override_initial_state=real_initial_state,
    start_day=initial_dates[0],
    duration=initial_dates[-1] - initial_dates[0] + duration,
    observe="MEX",
    noise=2e-4,
)
real_ephemeris, _ = retrieve_propagated_state_history(
    propagator_settings_estimation, new_bodies, clean=False
)

fig, axes = init_observation_plot(n_axes=4)
fig2, axes2 = init_observation_plot(n_axes=4)
fig3, axes3 = init_observation_plot(n_axes=4)

for i in range(len(initial_states)):
    fake_observations, propagator_settings_estimation, _ = simulate_observations(
        override_initial_state=initial_states[i],
        start_day=initial_dates[i],
        duration=duration,
        observe="MEX",
    )
    residuals = observations_difference(
        observations_array=fake_observations,
        new_observations_array=real_observations,
        sign=-1,
    )[0]
    for j in range(len(residuals)):
        antenna_results = residuals[j]
        axes[j].plot(
            (np.array(list(antenna_results.keys())) - initial_epochs[0]) / 86400,
            list(antenna_results.values()),
            "x",
            color=["b", "r", "g"][i % 3],
        )
        axes[j].set_title(dsn_antennae_names[j])
        axes[j].set_xlim([0, initial_dates[-1] + 1])

    old_ephemeris = dict()  # XXX- worst code ever
    try:
        old_ephemeris = fake_ephemeris
    except:
        1

    fake_ephemeris, _ = retrieve_propagated_state_history(
        propagator_settings_estimation, new_bodies, clean=False
    )

    ephemeris_comp, ephemeris_comp_norm, _ = ephemeris_difference(
        old_ephemeris, fake_ephemeris
    )

    tmpkey = list(fake_ephemeris.keys())[0]

    ephemeris_diff, ephemeris_diff_norm, _ = ephemeris_difference(
        real_ephemeris, fake_ephemeris
    )
    show_velocity = 0
    for k in range(3):
        axes2[k].plot(
            (np.array(list(ephemeris_diff.keys())) - initial_epochs[0]) / 86400,
            np.array(list(ephemeris_diff.values()))[:, k + 3 * show_velocity],
            "-",
            color=["b", "r", "g"][i % 3],
        )
        axes2[k].set_title(["r", "s", "w"][k])
        axes2[k].set_xlim([0, initial_dates[-1] + 1])
    if len(ephemeris_diff_norm.keys()) != 0:
        axes2[-1].plot(
            (np.array(list(ephemeris_diff_norm.keys())) - initial_epochs[0]) / 86400,
            np.array(list(ephemeris_diff_norm.values()))[:, show_velocity],
            "-",
            color=["b", "r", "g"][i % 3],
        )
        axes2[-1].set_title("Distance")
        axes2[-1].set_xlim([0, initial_dates[-1] + 1])

    for k in range(3):
        if len(ephemeris_comp.keys()) == 0:
            break
        axes3[k].plot(
            (np.array(list(ephemeris_comp.keys())) - initial_epochs[0]) / 86400,
            np.array(list(ephemeris_comp.values()))[:, k + 3 * show_velocity],
            "-",
            color=["b", "r", "g"][i % 3],
        )
        axes3[k].set_title(["r", "s", "w"][k])
        axes3[k].set_xlim([0, initial_dates[-1] + 1])
    if len(ephemeris_comp_norm.keys()) != 0:
        axes3[-1].plot(
            (np.array(list(ephemeris_comp_norm.keys())) - initial_epochs[0]) / 86400,
            np.array(list(ephemeris_comp_norm.values()))[:, show_velocity],
            "-",
            color=["b", "r", "g"][i % 3],
        )
        axes3[-1].set_title("Distance")
        axes3[-1].set_xlim([0, initial_dates[-1] + 1])


lns1 = axes[-1].plot(data[:, 0], data[:, 1], "b-o", label="Initial state error (m)")
ax2 = axes[-1].twinx()
lns2 = ax2.plot(data[:, 0], data[:, 2], "r-o", label="Initial state error (m/s)")

lns = lns1 + lns2
labs = [l.get_label() for l in lns]
axes[-1].legend(lns, labs, loc=0)
ax2.spines["right"].set_color("r")
ax2.spines["left"].set_color("b")
ax2.set_xlim([0, initial_dates[-1] + 1])


[axes[i].grid(True) for i in range(4)]
[axes[i].set_title(axes[i].get_title(), fontsize=36) for i in range(4)]
[axes[i].set_xticklabels(axes[i].get_xticklabels(), fontsize=18) for i in range(4)]
[axes[i].set_yticklabels(axes[i].get_yticklabels(), fontsize=18) for i in range(4)]
fig.tight_layout()
fig.savefig("out/DSN_MEX_BATCH_res.svg")
fig.show()

[axes2[i].grid(True) for i in range(4)]
[axes2[i].set_title(axes2[i].get_title(), fontsize=36) for i in range(4)]
[axes2[i].set_xticklabels(axes2[i].get_xticklabels(), fontsize=18) for i in range(4)]
[axes2[i].set_yticklabels(axes2[i].get_yticklabels(), fontsize=18) for i in range(4)]
fig2.tight_layout()
fig2.savefig("out/DSN_MEX_BATCH_pos_res.svg")
fig2.show()

[axes3[i].grid(True) for i in range(4)]
[axes3[i].set_title(axes3[i].get_title(), fontsize=36) for i in range(4)]
[axes3[i].set_xticklabels(axes3[i].get_xticklabels(), fontsize=18) for i in range(4)]
[axes3[i].set_yticklabels(axes3[i].get_yticklabels(), fontsize=18) for i in range(4)]
fig3.tight_layout()
fig3.savefig("out/DSN_MEX_BATCH_pos_comp.svg")
fig3.show()
