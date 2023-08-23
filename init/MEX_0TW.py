import os
import numpy as np
from tudatpy.kernel import constants
from tudatpy.kernel.numerical_simulation import environment_setup
from tudatpy.kernel.numerical_simulation.estimation_setup import observation
from tudatpy.kernel.interface import spice
from util.environment_setup import get_bodies

current_directory = os.getcwd()

spice.load_standard_kernels()
spice.load_kernel(current_directory + "/kernels/ORMM_T19_031222180906_00052.BSP")
spice.load_kernel(current_directory + "/kernels/ORMM_T19_040201000000_00060.BSP")
spice.load_kernel(current_directory + "/kernels/ORMM_T19_040301000000_00068.BSP")
spice.load_kernel(current_directory + "/kernels/ORMM_T19_040401000000_00072.BSP")


# Set simulation start (January 1st, 2004 - 00:00) and end epochs (January 11th, 2004 - 00:00)
simulation_start_epoch = 4.0 * constants.JULIAN_YEAR + 100.0 * constants.JULIAN_DAY
simulation_duration = 20.0 * constants.JULIAN_DAY
simulation_end_epoch = simulation_start_epoch + simulation_duration

initial_state = spice.get_body_cartesian_state_at_epoch(
    target_body_name="MEX",
    observer_body_name="Mars",
    reference_frame_name="J2000",
    aberration_corrections="none",
    ephemeris_time=simulation_start_epoch,
)

tw_number = 0  # No. of TW beacons

### CELESTIAL BODIES ###
bodies = get_bodies(simulation_start_epoch, simulation_end_epoch)

bodies_to_propagate = ["MEX"]
central_bodies = ["Mars"]

# General observation settings
light_time_correction_settings = (
    observation.first_order_relativistic_light_time_correction(["Sun"])
)
observation_times = np.arange(simulation_start_epoch, simulation_end_epoch, 60.0)
