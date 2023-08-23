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

# Set simulation start (January 1st, 2004 - 00:00) and end epochs (January 11th, 2004 - 00:00)
simulation_start_epoch = 4.0 * constants.JULIAN_YEAR + 100.0 * constants.JULIAN_DAY
simulation_duration = 5.0 * constants.JULIAN_DAY
simulation_end_epoch = simulation_start_epoch + simulation_duration

bodies_to_propagate = ["Sens"]
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

# General observation settings
light_time_correction_settings = (
    observation.first_order_relativistic_light_time_correction(["Sun"])
)
observation_times = np.arange(simulation_start_epoch, simulation_end_epoch, 30.0)

ORBIT_A = 5000
