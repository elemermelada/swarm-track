import numpy as np


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
