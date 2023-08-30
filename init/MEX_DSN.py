import os
import numpy as np
from tudatpy.kernel import constants
from tudatpy.kernel.numerical_simulation import environment_setup
from tudatpy.kernel.numerical_simulation.estimation_setup import observation
from tudatpy.kernel.interface import spice

from util.environment_setup import get_bodies


from observation.observation_setup import create_1w_dsn_links, create_2w_dsn_links

current_directory = os.getcwd()

spice.load_standard_kernels()
spice.load_kernel(current_directory + "/kernels/ORMM_T19_031222180906_00052.BSP")
spice.load_kernel(current_directory + "/kernels/ORMM_T19_040201000000_00060.BSP")
spice.load_kernel(current_directory + "/kernels/ORMM_T19_040301000000_00068.BSP")
spice.load_kernel(current_directory + "/kernels/ORMM_T19_040401000000_00072.BSP")


# Set simulation start (January 1st, 2004 - 00:00) and end epochs (January 11th, 2004 - 00:00)
simulation_start_epoch = 4.0 * constants.JULIAN_YEAR + 100.0 * constants.JULIAN_DAY
simulation_duration = 1.0 * constants.JULIAN_DAY
simulation_end_epoch = simulation_start_epoch + simulation_duration

### CELESTIAL BODIES ###
bodies = get_bodies(
    simulation_start_epoch,
    simulation_end_epoch,
)

bodies_to_propagate = ["MEX"]
central_bodies = ["Mars"]

# Add TW stations and create links to MEX
dsn_antennae_names = [
    # "DSS-13",
    "DSS-14",
    # "DSS-15",
    # "DSS-24",
    # "DSS-25",
    # "DSS-26",
    # "DSS-34",
    # "DSS-35",
    # "DSS-36",
    "DSS-43",
    # "DSS-45",
    # "DSS-54",
    # "DSS-55",
    "DSS-63",
    # "DSS-65",
]
stations = environment_setup.ground_station.dsn_stations()
for station in stations:
    environment_setup.add_ground_station(bodies.get_body("Earth"), station)
links = create_1w_dsn_links("MEX", dsn_antennae_names)

# General observation settings
light_time_correction_settings = (
    observation.first_order_relativistic_light_time_correction(["Sun"])
)
observation_times = np.arange(simulation_start_epoch, simulation_end_epoch, 60.0)
