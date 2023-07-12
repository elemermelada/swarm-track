## Post-processing
"""
Finally, to further illustrate the impact certain differences between the applied dynamical models have, we will first plot the behaviour of the simulated observations over time, as well as show how the discrepancy between our estimated solution and the 'ground truth' builds up over time.
"""

final_residuals = estimation_output.final_residuals

fig, ax1 = plt.subplots(1, 1, figsize=(9, 6))

doppler_tw0_time, doppler_tw0_residuals = retrieve_observation_residuals(final_residuals, mex_simulated_observations, observation.one_way_instantaneous_doppler_type, link=2)
ax1.scatter((doppler_tw0_time-simulation_start_epoch)/86400, doppler_tw0_residuals, color="red")

range_tw0_time, range_tw0_residuals = retrieve_observation_residuals(final_residuals, mex_simulated_observations, observation.one_way_range_type, link=2)
ax1.scatter((range_tw0_time-simulation_start_epoch)/86400, range_tw0_residuals, color="blue")

ax1.set_title("Observations as a function of time")
ax1.set_xlabel(r'Time [days]')
ax1.set_ylabel(r'Final Residuals [m]')
plt.tight_layout()
plt.savefig("out/observations.png")


simulator_object = estimation_output.simulation_results_per_iteration[-1]
state_history = simulator_object.dynamics_results.state_history

time2plt = np.vstack(list(state_history.keys()))
time2plt_normalized = (time2plt - time2plt[0]) / (3600*24)

mex_prop = np.vstack(list(state_history.values()))
# mex_sim_obs = np.vstack(list(mex_simulated_observations.values()))

# fig, ax1 = plt.subplots(1, 1, figsize=(9, 6))

# ax1.plot(time2plt_normalized, (mex_prop[:, 0] - mex_sim_obs[:, 0]), label=r'$\Delta x$')
# ax1.plot(time2plt_normalized, (mex_prop[:, 1] - mex_sim_obs[:, 1]), label=r'$\Delta y$')
# ax1.plot(time2plt_normalized, (mex_prop[:, 2] - mex_sim_obs[:, 2]), label=r'$\Delta z$')
# ax1.plot(time2plt_normalized, np.linalg.norm((mex_prop[:, 0:3] - mex_sim_obs[:, 0:3]), axis=1), label=r'$||\Delta X||$')

# ax1.set_title("Element-wise difference between true and estimated states")
# ax1.set_xlabel(r'$Time$ [days]')
# ax1.set_ylabel(r'$\Delta X$ [m]')
# ax1.legend()

# plt.tight_layout()
# plt.savefig("out/estimation.png")

orb_ax.plot(mex_prop[:, 1]*1E-3, mex_prop[:, 2]*1E-3, color="black", linestyle="--", label="Estimation")
# orb_ax.scatter(mex_sim_obs[:, 1]*1E-3, mex_sim_obs[:, 2]*1E-3, color="red", label="Observations")
orb_fig.savefig("out/compare.png")

print("wait")