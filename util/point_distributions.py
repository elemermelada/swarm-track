import numpy as np


def fibonacci_sphere(samples=10):
    coordinates = np.zeros((samples, 2))
    phi = np.pi * (np.sqrt(5.0) - 1.0)  # golden angle in radians

    for i in range(samples):
        y = 1 - (i / float(samples - 1)) * 2  # y goes from 1 to -1
        radius = np.sqrt(1 - y * y)  # radius at y

        theta = phi * i  # golden angle increment

        x = np.cos(theta) * radius
        z = np.sin(theta) * radius

        lat = np.rad2deg(np.arctan2(z, np.sqrt(x * x + y * y)))
        long = np.rad2deg(np.arctan2(y, x))

        coordinates[i] = (lat, long)

    return coordinates


def random_sphere(samples=10):
    coordinates = np.zeros((samples, 2))

    for i in range(samples):
        lat = np.random.random() * 180 - 90
        long = np.random.random() * 360 - 180
        coordinates[i] = (lat, long)

    return coordinates


def pole_sphere(samples=10, sigma=30.0):
    coordinates = np.zeros((samples, 2))

    for i in range(samples):
        lat = np.random.normal(90, sigma)
        if lat > 90:
            lat = 180 - lat
        long = np.random.random() * 360 - 180
        coordinates[i] = (lat, long)

    return coordinates


def equatorial_sphere(samples=10, sigma=10.0):
    coordinates = np.zeros((samples, 2))

    for i in range(samples):
        lat = np.random.normal(0, sigma)
        long = -180 + 360 * i / (samples - 1)
        coordinates[i] = (lat, long)

    return coordinates
