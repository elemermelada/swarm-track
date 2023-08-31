import numpy as np


def retrieve_ephemeris_from_cartesian_observations(simulated_observations):
    return np.reshape(simulated_observations.concatenated_observations, (-1, 3))


def retrieve_observations_with_type(observations_output, observation_type):
    observation_start = observations_output.observable_type_start_index_and_size[
        observation_type
    ][0]
    observation_length = observations_output.observable_type_start_index_and_size[
        observation_type
    ][1]
    observation_end = observation_start + observation_length
    filtered_observations = {}
    # Filter link ids
    link_ids = observations_output["concatenated_link_definition_ids"]
    link_ids = link_ids[observation_start:observation_end]
    filtered_observations["concatenated_link_definition_ids"] = link_ids
    # Filter times
    times = observations_output["concatenated_link_definition_ids"]
    times = times[observation_start:observation_end]
    filtered_observations["concatenated_times"] = times
    # Filter observations
    observations = observations_output["concatenated_observations"]
    observations = observations[observation_start:observation_end]
    filtered_observations["concatenated_observations"] = observations

    return filtered_observations


def retrieve_observations_with_link(observations_output, observation_link):
    observation_selector = (
        np.array(observations_output.concatenated_link_definition_ids)
        == observation_link
    )
    filtered_observations = {}
    # Filter times
    times = np.array(observations_output.concatenated_times)
    times = times[observation_selector]
    filtered_observations["concatenated_times"] = times

    # Filter observations
    observations = observations_output.concatenated_observations
    observations = observations[observation_selector]
    filtered_observations["concatenated_observations"] = observations

    return filtered_observations


def observations_difference(observations_array, new_observations_array):
    diff = []
    for i in range(len(observations_array)):
        observations: dict = observations_array[i]
        new_observations: dict = new_observations_array[i]
        observation_epochs = observations.keys()
        antenna_diff = dict()
        for t in observation_epochs:
            observation = observations[t]
            try:
                new_observation = new_observations[t]
            except:
                if False:  # XXX - being silly
                    antenna_diff[t] = observation
                continue
            antenna_diff[t] = observation - new_observation

        diff.append(antenna_diff)

    return diff, 0, 0
