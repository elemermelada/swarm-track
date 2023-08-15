from observation.observation_postprocessing import (
    retrieve_observations_with_link,
)
from util.environment_setup import add_radiation_pressure
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
    add_dsn_viability_check,
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

from init.MEX_DSN import (
    bodies,
    simulation_start_epoch,
    simulation_end_epoch,
    links,
    light_time_correction_settings,
    observation_times,
    dsn_antennae_names,
)

from util.propagation import retrieve_propagated_state_history

USE_3D = True

# Add radiation pressure to environment
add_radiation_pressure(bodies)

# Create trajectory plot + mars
ax, fig = init_trajectory_graph(threeD=USE_3D)
ax = plot_trajectory_from_spice(
    ax, "MEX", simulation_start_epoch, simulation_end_epoch, axis=[1, 2], threeD=USE_3D
)
ax = plot_mars(ax, USE_3D)
# fig.show()

# Add doppler "sensors"
(
    observation_settings_list,
    observation_simulation_settings,
) = create_simple_1w_doppler_sensors(
    links,
    light_time_correction_settings,
    observation_times,
    lambda observation_type, elevation_angle, observation_simulation_settings, links: add_dsn_viability_check(
        observation_type,
        elevation_angle,
        observation_simulation_settings,
        links,
        dsn_antennae_names,
    ),
)

# Update trajectory using dynamical model


# Create observations
simulated_observations = perform_observations(
    observation_settings_list,
    bodies,
    observation_simulation_settings,
)

fig2, ax2 = init_observation_plot()
colors = ["b", "r", "g"]
for i in range(3):
    filtered_observations = retrieve_observations_with_link(simulated_observations, i)
    plot_observations(
        ax2, filtered_observations, start_date=simulation_start_epoch, color=colors[i]
    )

fig2.show()
fig2.savefig("out/2way.png")

# Estimate
propagator_settings_estimation = basic_propagator(
    simulation_start_epoch,
    simulation_end_epoch,
    bodies,
    ["MEX"],
    ["Mars"],
    initial_state_error=0.0,
)

### Propagate to see wassup
state_history, time_vector = retrieve_propagated_state_history(
    propagator_settings_estimation, bodies, True
)
scatter_ephemeris(ax, state_history * 1e-3, threeD=USE_3D, color="r")
fig.show()

fig3, ax3 = init_observation_plot()
residuals = get_ephemeris_residuals_from_spice(state_history, time_vector)
ax3.plot(time_vector, residuals)
fig3.show()

parameters_to_estimate = create_gravimetry_parameters_to_estimate(
    propagator_settings_estimation, bodies
)
estimator = create_estimator(
    bodies,
    parameters_to_estimate,
    observation_settings_list,
    propagator_settings_estimation,
)
estimation_output = estimate(estimator, simulated_observations)

state_history = retrieve_best_iteration_state_history(estimation_output, clean=True)
ax = plot_ephemeris(ax, state_history * 1e-3, threeD=USE_3D, color="k", linestyle="--")
ax.legend()
fig.tight_layout()
fig.savefig("out/estimate.png")
fig.show()
