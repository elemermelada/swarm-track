import numpy as np

from util.math import vector_rms


def retrieve_observation_residuals(
    final_residuals, observations, observable_type, link=None
):
    time_vector = observations.concatenated_times

    (
        observables_start,
        observables_count,
    ) = observations.observable_type_start_index_and_size[observable_type]
    observables_end = observables_start + observables_count

    observable_residuals = np.array(final_residuals[observables_start:observables_end])
    observable_time = np.array(time_vector[observables_start:observables_end])

    if not link == None:
        concatenated_links = observations.concatenated_link_definition_ids
        concatenated_links = np.array(
            concatenated_links[observables_start:observables_end]
        )
        observable_residuals = observable_residuals[concatenated_links == link]
        observable_time = observable_time[concatenated_links == link]

    return observable_time, observable_residuals


def retrieve_best_iteration_index(estimation_output, verbose=True) -> int:
    n_iter = estimation_output.residual_history.shape[1]
    residual_history = estimation_output.residual_history
    min_rms = np.inf
    min_rms_i = -1
    for i in range(n_iter):
        if vector_rms(residual_history[:, i]) < min_rms:
            min_rms = vector_rms(residual_history[:, i])
            min_rms_i = i
    if verbose:
        print("Residual:", min_rms, "Iteration:", min_rms_i)
    return min_rms_i


def retrieve_state_history_from_iteration(iteration):
    return iteration.dynamics_results.state_history


def retrieve_best_iteration_state_history(estimation_output, clean=False):
    iter_index = retrieve_best_iteration_index(estimation_output)
    iter = estimation_output.simulation_results_per_iteration[iter_index]
    if clean:
        return np.array(list(retrieve_state_history_from_iteration(iter).values()))
    return retrieve_state_history_from_iteration(iter)
