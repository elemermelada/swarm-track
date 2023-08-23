from tudatpy.kernel.astro import element_conversion
from tudatpy.kernel.numerical_simulation import environment_setup
import numpy as np


def get_bodies(
    simulation_start_epoch,
    simulation_end_epoch,
    override_mars_harmonics=None,
    remove_mars_rotation=False,
    extra_body=None,
):
    bodies_to_create = ["Mars", "Phobos", "Deimos", "Sun", "Jupiter", "Earth"]

    # Create default body settings for bodies_to_create, with "Mars"/"J2000" as the global frame origin and orientation
    global_frame_origin = "Mars"
    global_frame_orientation = "J2000"
    body_settings = environment_setup.get_default_body_settings(
        bodies_to_create, global_frame_origin, global_frame_orientation
    )
    # original_settings = body_settings.get("Mars").gravity_field_settings
    if remove_mars_rotation:
        # define parameters describing the constant orientation between frames
        target_frame = "Mars_fixed"
        constant_orientation = np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]])
        # create rotation model settings and assign to body settings of "Earth"
        body_settings.get(
            "Mars"
        ).rotation_model_settings = environment_setup.rotation_model.constant_rotation_model(
            global_frame_orientation, target_frame, constant_orientation
        )

    if extra_body is None:
        body_settings.add_empty_settings("MEX")
    else:
        body_settings.add_empty_settings(extra_body["name"])
    # spice_ephemeris_settings = environment_setup.ephemeris.direct_spice(
    #     frame_origin=global_frame_origin,
    #     frame_orientation=global_frame_orientation,
    #     body_name_to_use="MEX",
    # )
    # body_settings.get(
    #     "MEX"
    # ).ephemeris_settings = environment_setup.ephemeris.tabulated_from_existing(
    #     ephemeris_settings=spice_ephemeris_settings,
    #     start_time=simulation_start_epoch,
    #     end_time=simulation_end_epoch,
    #     time_step=60,
    #     # interpolator_settings = None,
    # )

    # Override mars gravitational coefficients
    if not override_mars_harmonics is None:
        original_settings = body_settings.get("Mars").gravity_field_settings
        final_settings = override_mars_harmonics

        # Cosine coefficients
        for i in range(len(override_mars_harmonics["normalized_cosine_coefficients"])):
            for j in range(
                len(override_mars_harmonics["normalized_cosine_coefficients"][i])
            ):
                if (
                    override_mars_harmonics["normalized_cosine_coefficients"][i][j]
                    is None
                ):
                    final_settings["normalized_cosine_coefficients"][i][
                        j
                    ] = original_settings.normalized_cosine_coefficients[i][j]

        # Sine coefficients
        for i in range(len(override_mars_harmonics["normalized_sine_coefficients"])):
            for j in range(
                len(override_mars_harmonics["normalized_sine_coefficients"][i])
            ):
                if (
                    override_mars_harmonics["normalized_sine_coefficients"][i][j]
                    is None
                ):
                    final_settings["normalized_sine_coefficients"][i][
                        j
                    ] = original_settings.normalized_sine_coefficients[i][j]

        body_settings.get(
            "Mars"
        ).gravity_field_settings = environment_setup.gravity_field.spherical_harmonic(
            original_settings.gravitational_parameter,
            original_settings.reference_radius,
            final_settings["normalized_cosine_coefficients"],
            final_settings["normalized_sine_coefficients"],
            original_settings.associated_reference_frame,
        )
    # Create system of bodies
    bodies = environment_setup.create_system_of_bodies(body_settings)
    if extra_body is None:
        bodies.get("MEX").mass = 1000.0
    else:
        bodies.get(extra_body["name"]).mass = 1000.0
    return bodies


def add_radiation_pressure(bodies, extra_body=None):
    # Create radiation pressure settings
    reference_area_radiation = 4.0
    radiation_pressure_coefficient = 1.2
    occulting_bodies = ["Mars"]
    radiation_pressure_settings = environment_setup.radiation_pressure.cannonball(
        "Sun",
        reference_area_radiation,
        radiation_pressure_coefficient,
        occulting_bodies,
    )
    # Add the radiation pressure interface to the environment
    environment_setup.add_radiation_pressure_interface(
        bodies,
        "MEX" if extra_body is None else extra_body["name"],
        radiation_pressure_settings,
    )


def add_tw_stations(mars, number, distribution):
    for i, (station_latitude, station_longitude) in enumerate(distribution(number)):
        station_altitude = 252.0
        # Add the ground station to the environment
        environment_setup.add_ground_station(
            mars,
            f"TW{i}",
            [station_altitude, station_latitude, station_longitude],
            element_conversion.geodetic_position_type,
        )


def add_dsn_stations(earth):
    stations = environment_setup.ground_station.dsn_stations()
    for station in stations:
        environment_setup.add_ground_station(earth, station)
