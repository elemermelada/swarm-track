import os
import numpy as np
from tudatpy.kernel import constants
from tudatpy.kernel.numerical_simulation import environment_setup
from tudatpy.kernel.numerical_simulation.estimation_setup import observation
from tudatpy.kernel.interface import spice

from util.environment_setup import add_tw_stations, get_bodies
from util.point_distributions import fibonacci_sphere, equatorial_sphere

from observation.observation_setup import create_1w_tw_links

current_directory = os.getcwd()

spice.load_standard_kernels()
spice.load_kernel(current_directory + "/kernels/ORMM_T19_031222180906_00052.BSP")
spice.load_kernel(current_directory + "/kernels/ORMM_T19_040201000000_00060.BSP")
spice.load_kernel(current_directory + "/kernels/ORMM_T19_040301000000_00068.BSP")
spice.load_kernel(current_directory + "/kernels/ORMM_T19_040401000000_00072.BSP")
# Set simulation start (January 1st, 2004 - 00:00) and end epochs (January 11th, 2004 - 00:00)
simulation_start_epoch = 4.0 * constants.JULIAN_YEAR + 100.0 * constants.JULIAN_DAY
simulation_duration = 3 * constants.JULIAN_DAY
simulation_end_epoch = simulation_start_epoch + simulation_duration

tw_number = 50  # No. of TW beacons

### CELESTIAL BODIES ###
bodies = get_bodies()

bodies_to_propagate = ["MEX"]
central_bodies = ["Mars"]

# Add TW stations and create links to MEX
add_tw_stations(bodies.get("Mars"), tw_number, equatorial_sphere)
links = create_1w_tw_links(tw_number, "MEX")

# General observation settings
light_time_correction_settings = (
    observation.first_order_relativistic_light_time_correction(["Sun"])
)
observation_times = np.arange(simulation_start_epoch, simulation_end_epoch, 30.0)
