from estimation.estimation import (
    get_ephemeris_residuals_from_spice,
    get_orbital_residuals_from_spice,
)
from init.MEX_0TW import (
    bodies,
    simulation_start_epoch,
    simulation_end_epoch,
    light_time_correction_settings,
    bodies_to_propagate,
    initial_state,
)
from util.dynamical_models import basic_propagator
from util.environment_setup import add_radiation_pressure
from util.graphs import (
    init_observation_plot,
    init_trajectory_graph,
    plot_ephemeris,
    plot_mars,
    plot_trajectory_from_spice,
    scatter_ephemeris,
    scatter_trajectory_from_spice,
)
from util.propagation import retrieve_propagated_state_history

USE_3D = True

# Add radiation pressure to environment
# add_radiation_pressure(bodies)

## PLOT SPICE TRAJECTORY
ax, fig = init_trajectory_graph(threeD=USE_3D)
ax = plot_trajectory_from_spice(
    ax,
    bodies_to_propagate[0],
    simulation_start_epoch,
    simulation_end_epoch,
    threeD=USE_3D,
    color="r",
)
ax = plot_mars(ax, threeD=USE_3D)

## PROPAGATE TRAJECTORY
propagator_settings = basic_propagator(
    simulation_start_epoch,
    simulation_end_epoch,
    bodies,
    bodies_to_propagate,
    ["Mars"],
    initial_state_error=0.0,
    override_initial_state=initial_state,
    # gravity_order=0,
)

## Propagate to see wassup
# ax, fig = init_trajectory_graph(threeD=USE_3D)
state_history, time_vector = retrieve_propagated_state_history(
    propagator_settings, bodies, clean=True
)
# scatter_ephemeris(ax, state_history * 1e-3, threeD=True)


from tudatpy.kernel.astro import element_conversion

pos_res = get_ephemeris_residuals_from_spice(
    state_history, time_vector, velocity=False, orbiter=bodies_to_propagate[0]
)
vel_res = get_ephemeris_residuals_from_spice(
    state_history, time_vector, orbiter=bodies_to_propagate[0]
)
fig_res, axes_res = init_observation_plot(n_axes=2)
axes_res[0].plot(
    (time_vector - simulation_start_epoch) / 86400, pos_res[:, 0], label="r"
)
axes_res[0].plot(
    (time_vector - simulation_start_epoch) / 86400, pos_res[:, 1], label="s"
)
axes_res[0].plot(
    (time_vector - simulation_start_epoch) / 86400, pos_res[:, 2], label="h"
)
axes_res[1].plot(
    (time_vector - simulation_start_epoch) / 86400, vel_res[:, 0], label="vr"
)
axes_res[1].plot(
    (time_vector - simulation_start_epoch) / 86400, vel_res[:, 1], label="vs"
)
axes_res[1].plot(
    (time_vector - simulation_start_epoch) / 86400, vel_res[:, 2], label="vh"
)
axes_res[0].legend()
axes_res[1].legend()
fig_res.tight_layout()
fig_res.show()

orb_res, _, _ = get_orbital_residuals_from_spice(
    state_history,
    time_vector,
    bodies.get("Mars").gravitational_parameter,
    orbiter=bodies_to_propagate[0],
)

fig_res_orb, axes_res_orb = init_observation_plot(n_axes=6)

axes_res_orb[0].plot((time_vector - simulation_start_epoch) / 86400, orb_res[:, 0])
axes_res_orb[0].title.set_text("a")
axes_res_orb[1].plot((time_vector - simulation_start_epoch) / 86400, orb_res[:, 1])
axes_res_orb[1].title.set_text("e")
axes_res_orb[2].plot((time_vector - simulation_start_epoch) / 86400, orb_res[:, 2])
axes_res_orb[2].title.set_text("i")
axes_res_orb[3].plot((time_vector - simulation_start_epoch) / 86400, orb_res[:, 3])
axes_res_orb[3].title.set_text(r"\omega")
axes_res_orb[4].plot((time_vector - simulation_start_epoch) / 86400, orb_res[:, 4])
axes_res_orb[4].title.set_text(r"\Omega")
axes_res_orb[5].plot((time_vector - simulation_start_epoch) / 86400, orb_res[:, 5])
axes_res_orb[5].title.set_text(r"\theta")
axes_res_orb[6].plot(
    (time_vector - simulation_start_epoch) / 86400,
    [orb_res[i, 5] + orb_res[i, 3] for i in range(len(orb_res[:, 5]))],
)
axes_res_orb[5].title.set_text(r"\theta + \omega")

fig_res_orb.tight_layout()
fig_res_orb.show()


# import numpy as np

# N = 45
# peak_times = 0.588 + np.linspace(0, 0.3155 * (N - 1), N)
# # axes_res[1].scatter(peak_times, peak_times * 0 + 50, color="k")
# # axes_res[0].scatter(peak_times, peak_times * 0, color="k", zorder=3)

# scatter_trajectory_from_spice(
#     ax, "MEX", peak_times * 86400 + simulation_start_epoch, threeD=True, color="k"
# )

fig.show()

print("hm")
