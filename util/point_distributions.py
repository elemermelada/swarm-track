import numpy as np


def geo_2_cart(coordinates: np.array, radius: float):
    lat_rad, long_rad = np.deg2rad(coordinates)
    x = radius * np.cos(long_rad) * np.cos(lat_rad)
    y = radius * np.sin(long_rad) * np.cos(lat_rad)
    z = radius * np.sin(lat_rad)
    return np.array([x, y, z])


def cart_2_geo(coordinates: np.array, radius: float):
    x, y, z = coordinates / radius

    lat = np.rad2deg(np.arctan2(z, np.sqrt(x * x + y * y)))
    long = np.rad2deg(np.arctan2(y, x))

    return np.array([lat, long])


def fibonacci_sphere(samples=10, sigma=0.0):
    coordinates = np.zeros((samples, 2))
    phi = np.pi * (np.sqrt(5.0) - 1.0)  # golden angle in radians

    for i in range(samples):
        y = 1 - (i / float(samples - 1)) * 2  # y goes from 1 to -1
        radius = np.sqrt(1 - y * y)  # radius at y

        theta = phi * i  # golden angle increment

        x = np.cos(theta) * radius
        z = np.sin(theta) * radius

        coordinates[i] = cart_2_geo(np.array([x, y, z]), 1)

    return coordinates


def random_sphere(samples=10, sigma=0.0):
    coordinates = np.zeros((samples, 2))

    for i in range(samples):
        X = np.random.random() * 2 - 1
        lat = np.sign(X) * np.arccos(np.abs(X))
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


def equatorial_sphere(samples=10, sigma=30.0):
    coordinates = np.zeros((samples, 2))

    for i in range(samples):
        lat = np.random.normal(0, sigma / 2)
        # long = -180 + 360 * i / (samples)
        long = np.random.random() * 360 - 180
        coordinates[i] = (lat, long)

    return coordinates


def add_error_to_coordinates(
    coordinates_array: np.array, radius: float, error: float, indeces: int = None
):
    result_coordinates = []
    for i in range(len(coordinates_array)) if (indeces is None) else indeces:
        coordinates = coordinates_array[i]
        cart_coords = geo_2_cart(coordinates, radius)
        cart_coords_w_error = np.array(
            [np.random.normal(cart_coord, error) for cart_coord in cart_coords]
        )
        result_coordinates.append(cart_2_geo(cart_coords_w_error, radius))
    return result_coordinates
