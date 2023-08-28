import os
import numpy as np
from tudatpy.kernel import constants
from tudatpy.kernel.numerical_simulation import environment_setup
from tudatpy.kernel.numerical_simulation.estimation_setup import observation
from tudatpy.kernel.interface import spice
from util.environment_setup import get_bodies

current_directory = os.getcwd()

spice.load_standard_kernels()
spice.load_kernel(
    current_directory + "/kernels/em16_tgo_fsp_133_01_20200309_20200822_v02.bsp"
)

# Set simulation start (January 1st, 2004 - 00:00) and end epochs (January 11th, 2004 - 00:00)
simulation_start_epoch = 20.0 * constants.JULIAN_YEAR + 100 * constants.JULIAN_DAY
simulation_duration = 20.0 * constants.JULIAN_DAY
simulation_end_epoch = simulation_start_epoch + simulation_duration

bodies_to_propagate = ["Phobos"]
central_bodies = ["Mars"]

initial_state = spice.get_body_cartesian_state_at_epoch(
    target_body_name=bodies_to_propagate[0],
    observer_body_name="Mars",
    reference_frame_name="J2000",
    aberration_corrections="none",
    ephemeris_time=simulation_start_epoch,
)

tw_number = 0  # No. of TW beacons

### CELESTIAL BODIES ###
bodies = get_bodies(
    simulation_start_epoch, simulation_end_epoch, extra_body={"name": "TGO"}
)


# General observation settings
light_time_correction_settings = (
    observation.first_order_relativistic_light_time_correction(["Sun"])
)
observation_times = np.arange(simulation_start_epoch, simulation_end_epoch, 60.0)
