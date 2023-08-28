import numpy as np


def vector_rms(vector):
    return np.sqrt(np.sum(vector**2) / len(vector))


def observations_rms(observations_array, new_observations_array):
    total_rms = 0
    for i in range(len(observations_array)):
        observations: dict = observations_array[i]
        new_observations: dict = new_observations_array[i]
        observation_epochs = observations.keys()
        partial_sum = 0
        missing_observations = 0
        present_observations = 0
        for t in observation_epochs:
            observation = observations[t]
            try:
                new_observation = new_observations[t]
            except:
                missing_observations += len(observation)
                continue
            partial_sum += np.sum((observation - new_observation) ** 2)
            present_observations += len(observation)

        total_rms += np.sqrt(partial_sum / present_observations)

    return total_rms


def fix_angle(angle, mode=1):
    if mode == 2:
        if angle < 0:
            angle += 2 * np.pi
        if angle > 2 * np.pi:
            angle -= 2 * np.pi
        return angle

    if angle < -np.pi:
        angle += 2 * np.pi
    if angle > np.pi:
        angle -= 2 * np.pi
    return angle
