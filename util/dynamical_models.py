import numpy as np

from tudatpy.kernel.numerical_simulation import propagation_setup
from tudatpy.kernel.interface import spice

from estimation.estimation import inverse_transform_vector, transform_vector


def basic_propagator(
    simulation_start_epoch,
    simulation_end_epoch,
    bodies,
    bodies_to_propagate,
    central_bodies,
    initial_state_error=None,
    override_initial_state=None,
    initial_state_perturbation=None,
    gravity_order=4,
):
    accelerations_settings_mars_express_estimation = dict(
        Mars=[
            propagation_setup.acceleration.point_mass_gravity()
            if bodies.get("Mars").rotation_model.body_fixed_frame_name == "Mars_fixed"
            else propagation_setup.acceleration.spherical_harmonic_gravity(
                gravity_order, gravity_order
            )
        ],
        Deimos=[propagation_setup.acceleration.point_mass_gravity()],
        Earth=[propagation_setup.acceleration.point_mass_gravity()],
        Jupiter=[propagation_setup.acceleration.point_mass_gravity()],
        Sun=[
            propagation_setup.acceleration.point_mass_gravity(),
            # propagation_setup.acceleration.cannonball_radiation_pressure(),
        ],
    )

    if bodies_to_propagate[0] != "Phobos":
        accelerations_settings_mars_express_estimation["Phobos"] = [
            propagation_setup.acceleration.point_mass_gravity()
        ]
    # Create updated global accelerations dictionary
    acceleration_settings_estimation = {
        bodies_to_propagate[0]: accelerations_settings_mars_express_estimation
    }

    # Create updated acceleration models
    acceleration_models_estimation = propagation_setup.create_acceleration_models(
        bodies, acceleration_settings_estimation, bodies_to_propagate, central_bodies
    )

    # Obtain an initial state
    initial_state = override_initial_state
    if initial_state is None:
        initial_state = spice.get_body_cartesian_state_at_epoch(
            target_body_name=bodies_to_propagate[0],
            observer_body_name="Mars",
            reference_frame_name="J2000",
            aberration_corrections="none",
            ephemeris_time=simulation_start_epoch,
        )
        if not initial_state_perturbation is None:
            init_pos = inverse_transform_vector(
                initial_state_perturbation, initial_state
            )
            init_vel = inverse_transform_vector(
                initial_state_perturbation, initial_state, velocity=True
            )
            initial_state = initial_state + np.concatenate((init_pos, init_vel))

    if not initial_state_error is None:
        initial_state = np.multiply(
            initial_state,
            1 + np.ones(len(initial_state)) * initial_state_error,
        )

    integrator_settings = propagation_setup.integrator.runge_kutta_fixed_step_size(
        initial_time_step=60.0,
        coefficient_set=propagation_setup.integrator.CoefficientSets.rkdp_87,
    )
    termination_settings = propagation_setup.propagator.time_termination(
        simulation_end_epoch
    )

    propagator_settings_estimation = propagation_setup.propagator.translational(
        central_bodies=central_bodies,
        acceleration_models=acceleration_models_estimation,
        bodies_to_integrate=bodies_to_propagate,
        initial_states=initial_state,
        initial_time=simulation_start_epoch,
        integrator_settings=integrator_settings,
        termination_settings=termination_settings,
        # propagator=propagation_setup.propagator.TranslationalPropagatorType.unified_state_model_quaternions,
    )

    return propagator_settings_estimation
