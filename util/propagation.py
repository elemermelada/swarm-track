from tudatpy.kernel import numerical_simulation
import numpy as np


def retrieve_propagated_state_history(propagator_settings, bodies, clean=False):
    dynamics_simulator = numerical_simulation.create_dynamics_simulator(
        bodies, propagator_settings
    )
    propagation_results = dynamics_simulator.propagation_results
    state_history = propagation_results.state_history
    if clean:
        return np.array(list(state_history.values())), np.array(
            list(state_history.keys())
        )
    return state_history, None
