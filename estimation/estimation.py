from tudatpy.kernel.numerical_simulation import estimation
from tudatpy.kernel import numerical_simulation
from tudatpy.kernel.interface import spice
from tudatpy.kernel.astro import element_conversion
import numpy as np

from util.math import fix_angle


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


def estimate(estimator, simulated_observations, max_iters=10):
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


def get_orbital_residuals_from_spice(propagated_state, time_vector, mu, orbiter="MEX"):
    residuals = []
    spice_elements_array = []
    prop_elements_array = []
    for i in range(len(time_vector)):
        t = time_vector[i]
        spice_state = spice.get_body_cartesian_state_at_epoch(
            target_body_name=orbiter,
            observer_body_name="Mars",
            reference_frame_name="J2000",
            aberration_corrections="none",
            ephemeris_time=t,
        )
        spice_elements = element_conversion.cartesian_to_keplerian(spice_state, mu)
        spice_elements_array.append(spice_elements)
        prop_elements = element_conversion.cartesian_to_keplerian(
            propagated_state[i, :], mu
        )
        prop_elements_array.append(prop_elements)
        residual = spice_elements - prop_elements
        residual[-1] = fix_angle(residual[-1])
        residual[-2] = fix_angle(residual[-2])
        residuals.append(residual)
    return (
        np.array(residuals),
        np.array(spice_elements_array),
        np.array(prop_elements_array),
    )


def transform_vector(v, state, velocity=False, all=False):
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

    if all:
        return [
            np.dot(v[0:3], r_vector),
            np.dot(v[0:3], s_vector),
            np.dot(v[0:3], w_vector),
            np.dot(v[3:6], r_vector),
            np.dot(v[3:6], s_vector),
            np.dot(v[3:6], w_vector),
        ]

    return [
        np.dot(v[0:3], r_vector),
        np.dot(v[0:3], s_vector),
        np.dot(v[0:3], w_vector),
    ]


def inverse_transform_vector(v, state, velocity=False):
    trans_matrix = np.zeros((3, 3))
    trans_matrix[0, :] = transform_vector(np.array([1, 0, 0]), state, False)
    trans_matrix[1, :] = transform_vector(np.array([0, 1, 0]), state, False)
    trans_matrix[2, :] = transform_vector(np.array([0, 0, 1]), state, False)

    if velocity:
        return np.matmul(trans_matrix, v[3:6])
    return np.matmul(trans_matrix, v[0:3])


def get_ephemeris_residuals_from_spice(
    propagated_state, time_vector, velocity=True, orbiter="MEX"
):
    return (
        np.array(
            [
                transform_vector(
                    propagated_state[i]
                    - spice.get_body_cartesian_state_at_epoch(
                        target_body_name=orbiter,
                        observer_body_name="Mars",
                        reference_frame_name="J2000",
                        aberration_corrections="none",
                        ephemeris_time=time_vector[i],
                    ),
                    propagated_state[i],
                    velocity=velocity,
                )
                for i in range(len(propagated_state))
            ]
        ),
        np.array(
            [
                transform_vector(
                    spice.get_body_cartesian_state_at_epoch(
                        target_body_name=orbiter,
                        observer_body_name="Mars",
                        reference_frame_name="J2000",
                        aberration_corrections="none",
                        ephemeris_time=time_vector[i],
                    ),
                    propagated_state[i],
                    velocity=velocity,
                )
                for i in range(len(propagated_state))
            ]
        ),
        np.array(
            [
                transform_vector(
                    propagated_state[i],
                    propagated_state[i],
                    velocity=velocity,
                )
                for i in range(len(propagated_state))
            ]
        ),
    )
