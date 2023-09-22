from estimation.estimation import (
    get_ephemeris_residuals_from_spice,
    get_orbital_residuals_from_spice,
)
from util.dynamical_models import basic_propagator
from util.environment_setup import add_radiation_pressure
from util.graphs import (
    init_observation_plot,
    init_trajectory_graph,
    plot_ephemeris,
    plot_mars,
    plot_trajectory_from_spice,
    plot_trajectory_parameters,
    scatter_ephemeris,
    scatter_trajectory_from_spice,
)
from util.propagation import retrieve_propagated_state_history

orb_case = input("Orbiter ([MEX], TGO, PHO): ")

if orb_case.upper() == "TGO":
    from init.TGO_0TW import (
        bodies,
        simulation_start_epoch,
        simulation_end_epoch,
        bodies_to_propagate,
        initial_state,
    )
elif orb_case.upper() == "PHO":
    from init.PHOBOS_0TW import (
        bodies,
        simulation_start_epoch,
        simulation_end_epoch,
        bodies_to_propagate,
        initial_state,
    )
else:
    orb_case = "MEX"
    from init.MEX_0TW import (
        bodies,
        simulation_start_epoch,
        simulation_end_epoch,
        bodies_to_propagate,
        initial_state,
    )


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

pos_res, pos_spice, pos_prop = get_ephemeris_residuals_from_spice(
    state_history, time_vector, velocity=False, orbiter=bodies_to_propagate[0]
)
vel_res, vel_spice, vel_prop = get_ephemeris_residuals_from_spice(
    state_history, time_vector, orbiter=bodies_to_propagate[0]
)

orb_res, orb_spice, orb_prop = get_orbital_residuals_from_spice(
    state_history,
    time_vector,
    bodies.get("Mars").gravitational_parameter,
    orbiter=bodies_to_propagate[0],
)

fig_res, axes_res = init_observation_plot(n_axes=9)
plot_trajectory_parameters(
    axes_res, (time_vector - simulation_start_epoch) / 86400, pos_res, vel_res, orb_res
)

fig_res.tight_layout()
fig_res.savefig("out/" + orb_case.upper() + "_res.svg")
fig_res.show()

fig_comp, axes_comp = init_observation_plot(n_axes=6)
plot_trajectory_parameters(
    axes_comp,
    (time_vector - simulation_start_epoch) / 86400,
    pos_spice,
    vel_spice,
    orb_spice,
    selector=(14400, 14400 + 1440, 3),
)

plot_trajectory_parameters(
    axes_comp,
    (time_vector - simulation_start_epoch) / 86400,
    pos_prop,
    vel_prop,
    orb_prop,
    scatter=True,
    selector=(14400, 14400 + 1440, 3),
)

[ax.tick_params(axis="both", which="major", labelsize=18) for ax in axes_comp]
fig_comp.tight_layout()
fig_comp.savefig("out/" + orb_case.upper() + "_comp.svg")
fig_comp.show()


# import numpy as np

# N = 45
# peak_times = 0.588 + np.linspace(0, 0.3155 * (N - 1), N)
# # axes_res[1].scatter(peak_times, peak_times * 0 + 50, color="k")
# # axes_res[0].scatter(peak_times, peak_times * 0, color="k", zorder=3)

# scatter_trajectory_from_spice(
#     ax, "MEX", peak_times * 86400 + simulation_start_epoch, threeD=True, color="k"
# )


fig.show()
