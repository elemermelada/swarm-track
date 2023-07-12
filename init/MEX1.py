import os
from tudatpy.kernel import constants
from tudatpy.kernel.numerical_simulation import environment_setup
from tudatpy.kernel.interface import spice
from util.environment_setup import get_bodies

current_directory = os.getcwd()

spice.load_standard_kernels()
spice.load_kernel(current_directory + "/kernels/ORMM_T19_031222180906_00052.BSP")

# Set simulation start (January 1st, 2004 - 00:00) and end epochs (January 11th, 2004 - 00:00)
simulation_start_epoch = (
    4.0 * constants.JULIAN_YEAR + (4.0 + 1.5) * constants.JULIAN_DAY
)
simulation_duration = 1.0 * constants.JULIAN_DAY
simulation_end_epoch = simulation_start_epoch + simulation_duration
tw_number = 10  # No. of TW beacons

### CELESTIAL BODIES ###
bodies = get_bodies(simulation_start_epoch, simulation_end_epoch, environment_setup)

bodies_to_propagate = ["MEX"]
central_bodies = ["Mars"]
