from tudatpy.kernel.numerical_simulation import estimation
from tudatpy.kernel import numerical_simulation
from tudatpy.kernel.interface import spice

import numpy as np


def create_estimator(
    bodies,
    parameters_to_estimate,
    observation_settings_list,
    propagator_settings,
):
    estimator = numerical_simulation.Estimator(
        bodies, parameters_to_estimate, observation_settings_list, propagator_settings
    )
    return estimator


def estimate(estimator, simulated_observations, max_iters=5):
    convergence_checker = estimation.estimation_convergence_checker(
        maximum_iterations=max_iters, number_of_iterations_without_improvement=2
    )
    estimation_input = estimation.EstimationInput(
        simulated_observations, convergence_checker=convergence_checker
    )

    estimation_input.define_estimation_settings(
        reintegrate_variational_equations=True, save_state_history_per_iteration=True
    )

    estimation_output = estimator.perform_estimation(estimation_input)
    return estimation_output


def get_ephemeris_residuals_from_spice(propagated_state, time_vector, velocity=True):
    def transform_vector(v, state):
        r_vector = state[0:3] / np.linalg.norm(state)
        v_vector = state[3:6]
        w_vector = np.cross(r_vector, v_vector)
        w_vector = w_vector / np.linalg.norm(w_vector)
        s_vector = np.cross(w_vector, r_vector)
        s_vector = s_vector / np.linalg.norm(s_vector)

        if velocity:
            return [
                np.dot(v[3:6], r_vector),
                np.dot(v[3:6], s_vector),
                np.dot(v[3:6], w_vector),
            ]

        return [
            np.dot(v[0:3], r_vector),
            np.dot(v[0:3], s_vector),
            np.dot(v[0:3], w_vector),
        ]

    return [
        transform_vector(
            propagated_state[i]
            - spice.get_body_cartesian_state_at_epoch(
                target_body_name="MEX",
                observer_body_name="Mars",
                reference_frame_name="J2000",
                aberration_corrections="none",
                ephemeris_time=time_vector[i],
            ),
            propagated_state[i],
        )
        for i in range(len(propagated_state))
    ]
