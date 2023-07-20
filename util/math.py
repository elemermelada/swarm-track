import numpy as np


def vector_rms(vector):
    return np.sqrt(np.sum(vector**2 / len(vector)))
