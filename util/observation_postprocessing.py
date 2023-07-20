import numpy as np


def retrieve_ephemeris_from_cartesian_observations(simulated_observations):
    return np.reshape(simulated_observations.concatenated_observations, (-1, 3))
