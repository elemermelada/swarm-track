from tudatpy.kernel.astro import element_conversion


def get_bodies(simulation_start_epoch, simulation_end_epoch, environment_setup):
    bodies_to_create = ["Mars", "Phobos", "Deimos", "Sun", "Jupiter", "Earth"]

    # Create default body settings for bodies_to_create, with "Mars"/"J2000" as the global frame origin and orientation
    global_frame_origin = "Mars"
    global_frame_orientation = "ECLIPJ2000"
    body_settings = environment_setup.get_default_body_settings(
        bodies_to_create, global_frame_origin, global_frame_orientation
    )
    body_settings.add_empty_settings("MEX")
    spice_ephemeris_settings = environment_setup.ephemeris.direct_spice(
        frame_origin=global_frame_origin,
        frame_orientation=global_frame_orientation,
        body_name_to_use="MEX",
    )
    body_settings.get(
        "MEX"
    ).ephemeris_settings = environment_setup.ephemeris.tabulated_from_existing(
        ephemeris_settings=spice_ephemeris_settings,
        start_time=simulation_start_epoch,
        end_time=simulation_end_epoch,
        time_step=60,
        # interpolator_settings = None,
    )

    # Create system of bodies
    bodies = environment_setup.create_system_of_bodies(body_settings)

    ### VEHICLE BODY ###
    # Create vehicle object
    # bodies.create_empty_body("MEX")
    bodies.get("MEX").mass = 1000.0
    return bodies


def add_radiation_pressure(bodies, environment_setup):
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
        bodies, "MEX", radiation_pressure_settings
    )


def add_tw_stations(environment_setup, body, number, distribution):
    for i, (station_latitude, station_longitude) in enumerate(distribution(number)):
        station_altitude = 252.0
        # Add the ground station to the environment
        environment_setup.add_ground_station(
            body,
            f"TW{i}",
            [station_altitude, station_latitude, station_longitude],
            element_conversion.geodetic_position_type,
        )
