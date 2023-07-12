def basic_propagator(propagation_setup, spice, simulation_start_epoch, simulation_end_epoch, bodies, bodies_to_propagate, central_bodies):
    accelerations_settings_mars_express_estimation = dict(
        Mars=[
            propagation_setup.acceleration.spherical_harmonic_gravity(4, 4)
        ],
        Phobos=[
            propagation_setup.acceleration.point_mass_gravity()
        ],
        Deimos=[
            propagation_setup.acceleration.point_mass_gravity()
        ],
        Earth=[
            propagation_setup.acceleration.point_mass_gravity()
        ],
        Jupiter=[
            propagation_setup.acceleration.point_mass_gravity()
        ],
        Sun=[
            propagation_setup.acceleration.point_mass_gravity(),
            propagation_setup.acceleration.cannonball_radiation_pressure()
        ])
    # Create updated global accelerations dictionary
    acceleration_settings_estimation = {"MEX": accelerations_settings_mars_express_estimation}

    # Create updated acceleration models
    acceleration_models_estimation = propagation_setup.create_acceleration_models(
        bodies,
        acceleration_settings_estimation,
        bodies_to_propagate,
        central_bodies)

    initial_state = spice.get_body_cartesian_state_at_epoch(
        target_body_name="MEX",
        observer_body_name="Mars",
        reference_frame_name="ECLIPJ2000",
        aberration_corrections="none",
        ephemeris_time=simulation_start_epoch)

    integrator_settings = propagation_setup.integrator.\
        runge_kutta_fixed_step_size(initial_time_step=60.0,
                                    coefficient_set=propagation_setup.integrator.CoefficientSets.rkdp_87)
    termination_settings = propagation_setup.propagator.time_termination(simulation_end_epoch)

    propagator_settings_estimation = propagation_setup.propagator. \
        translational(central_bodies=central_bodies,
                    acceleration_models=acceleration_models_estimation,
                    bodies_to_integrate=bodies_to_propagate,
                    initial_states=initial_state,
                    initial_time=simulation_start_epoch,
                    integrator_settings=integrator_settings,
                    termination_settings=termination_settings)
    
    return propagator_settings_estimation