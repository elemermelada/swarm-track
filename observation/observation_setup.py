from tudatpy.kernel.numerical_simulation import estimation_setup
from tudatpy.kernel.numerical_simulation.estimation_setup import observation
import numpy as np


def create_1w_tw_links(tw_number, body):
    links = []
    for i in range(tw_number):
        one_way_link_ends = dict()
        one_way_link_ends[
            observation.transmitter
        ] = observation.body_reference_point_link_end_id("Mars", f"TW{i}")
        one_way_link_ends[observation.receiver] = observation.body_origin_link_end_id(
            body
        )
        one_way_link_definition = observation.LinkDefinition(one_way_link_ends)
        links.append(one_way_link_definition)
    return links


def create_1w_dsn_links(body, dsn_antennae):
    links = []

    for antenna in dsn_antennae:
        one_way_link_ends = dict()
        one_way_link_ends[
            observation.transmitter
        ] = observation.body_reference_point_link_end_id("Earth", antenna)
        one_way_link_ends[observation.receiver] = observation.body_origin_link_end_id(
            body
        )
        one_way_link_definition = observation.LinkDefinition(one_way_link_ends)
        links.append(one_way_link_definition)

    return links


def create_2w_dsn_links(body, dsn_antennae):
    links = []
    for antenna in dsn_antennae:
        two_way_link_ends = dict()
        two_way_link_ends[
            observation.transmitter
        ] = observation.body_reference_point_link_end_id("Earth", antenna)
        two_way_link_ends[
            observation.retransmitter
        ] = observation.body_origin_link_end_id(body)
        two_way_link_ends[
            observation.receiver
        ] = observation.body_reference_point_link_end_id("Earth", antenna)
        two_way_link_definition = observation.LinkDefinition(two_way_link_ends)
        links.append(two_way_link_definition)
    return links


def create_cart_link(body):
    cart_link_ends = dict()
    cart_link_ends[observation.observed_body] = observation.body_origin_link_end_id(
        body
    )
    cart_link_definition = observation.LinkDefinition(cart_link_ends)
    return [cart_link_definition]


def add_simple_1w_doppler_observation_settings(
    links,
    observation_settings_list: list = list(),
    light_time_correction_settings=None,
):
    light_time_correction_settings = (
        observation.first_order_relativistic_light_time_correction(["Sun"])
    )
    for link in links:
        observation_settings_list.append(
            observation.one_way_doppler_instantaneous(
                link,
                light_time_correction_settings=[light_time_correction_settings],
            )
        )
    return observation_settings_list


def add_simple_2w_doppler_observation_settings(
    links,
    observation_settings_list: list = list(),
    light_time_correction_settings=None,
):
    light_time_correction_settings = (
        observation.first_order_relativistic_light_time_correction(["Sun"])
    )
    for link in links:
        observation_settings_list.append(
            observation.two_way_doppler_averaged(
                link,
                light_time_correction_settings=[light_time_correction_settings],
            )
        )
    return observation_settings_list


def add_simple_1w_range_observation_settings(
    links,
    observation_settings_list: list = list(),
    light_time_correction_settings=None,
    bias=0.01,
):
    range_bias_settings = observation.absolute_bias([bias])
    for link in links:
        observation_settings_list.append(
            observation.one_way_range(
                link,
                light_time_correction_settings=[light_time_correction_settings],
                bias_settings=range_bias_settings,
            )
        )
    return observation_settings_list


def add_simple_cartesian_observation_settings(
    links,
    observation_settings_list: list = list(),
):
    for link in links:
        observation_settings_list.append(
            observation.cartesian_position(
                link,
                bias_settings=None,
            )
        )
    return observation_settings_list


def add_observation_simulators(
    observation_times,
    links,
    observation_type,
    observation_simulation_settings: list = list(),
    reference_link_end_type=None,
):
    reference_link = (
        reference_link_end_type if reference_link_end_type else observation.receiver
    )
    for link in links:
        observation_simulation_settings.append(
            observation.tabulated_simulation_settings(
                observation_type,
                link,
                observation_times,
                reference_link_end_type=reference_link,
            )
        )
    return observation_simulation_settings


def add_noise(noise_level, observation_type, observation_simulation_settings):
    observation.add_gaussian_noise_to_observable(
        observation_simulation_settings, noise_level, observation_type
    )


def add_tw_viability_check(
    observation_type,
    elevation_angle,
    observation_simulation_settings,
    links,
):
    for i in range(len(links)):
        viability_settings = [
            observation.elevation_angle_viability(["Mars", f"TW{i}"], elevation_angle),
            observation.body_avoidance_viability(
                ["Earth", f"TW{i}"], "Sun", np.deg2rad(5)
            ),
        ]
        observation.add_viability_check_to_observable_for_link_ends(
            observation_simulation_settings,
            viability_settings,
            observation_type,
            links[i],
        )


def add_dsn_viability_check(
    observation_type,
    elevation_angle,
    observation_simulation_settings,
    links,
    dsn_antennae_names,
    fake=False,
):
    for i in range(len(links)):
        viability_settings = [
            observation.elevation_angle_viability(
                ["Earth", dsn_antennae_names[i]],
                elevation_angle,
            ),
            observation.body_occultation_viability(
                ["Earth", dsn_antennae_names[i]], "Mars"
            ),
            observation.body_avoidance_viability(
                ["Earth", dsn_antennae_names[i]], "Sun", np.deg2rad(5)
            ),
        ]
        if fake:
            viability_settings = []

        observation.add_viability_check_to_observable_for_link_ends(
            observation_simulation_settings,
            viability_settings,
            observation_type,
            links[i],
        )


def create_simple_1w_doppler_sensors(
    links,
    light_time_correction_settings,
    observation_times,
    add_viability_check_fcn=add_tw_viability_check,
    noise=1.0e-3,
):
    observable_type = observation.one_way_instantaneous_doppler_type
    observation_settings_list = add_simple_1w_doppler_observation_settings(
        links,
        light_time_correction_settings=light_time_correction_settings,
    )
    observation_simulation_settings = add_observation_simulators(
        observation_times, links, observable_type
    )
    if noise:
        add_noise(
            noise,
            observable_type,
            observation_simulation_settings,
        )
    add_viability_check_fcn(
        observable_type,
        np.deg2rad(15),
        observation_simulation_settings,
        links,
    )
    return observation_settings_list, observation_simulation_settings, observable_type


def create_simple_2w_doppler_sensors(
    links,
    light_time_correction_settings,
    observation_times,
    add_viability_check_fcn=add_tw_viability_check,
):
    observable_type = observation.two_way_instantaneous_doppler_type
    observation_settings_list = add_simple_2w_doppler_observation_settings(
        links,
        light_time_correction_settings=light_time_correction_settings,
    )
    observation_simulation_settings = add_observation_simulators(
        observation_times, links, observable_type
    )
    add_noise(
        1.0e-3,
        observable_type,
        observation_simulation_settings,
    )
    add_viability_check_fcn(
        observable_type,
        np.deg2rad(15),
        observation_simulation_settings,
        links,
    )
    return observation_settings_list, observation_simulation_settings


def create_2w_doppler_sensors(
    links,
    light_time_correction_settings,
    observation_times,
    add_viability_check_fcn=add_tw_viability_check,
):
    observable_type = observation.two_way_instantaneous_doppler_type
    observation_settings_list = add_simple_2w_doppler_observation_settings(
        links,
        light_time_correction_settings=light_time_correction_settings,
    )
    observation_simulation_settings = add_observation_simulators(
        observation_times, links, observable_type
    )
    add_noise(
        1.0e-3,
        observable_type,
        observation_simulation_settings,
    )
    add_viability_check_fcn(
        observable_type,
        np.deg2rad(15),
        observation_simulation_settings,
        links,
    )
    return observation_settings_list, observation_simulation_settings


def create_2w_doppler_sensors(links, light_time_correction_settings, observation_times):
    observable_type = observation.two_way_instantaneous_doppler_type
    observation_settings_list = add_simple_2w_doppler_observation_settings(
        links,
        light_time_correction_settings=light_time_correction_settings,
    )
    observation_simulation_settings = add_observation_simulators(
        observation_times, links, observable_type
    )
    add_noise(
        1.0e-3,
        observable_type,
        observation_simulation_settings,
    )
    add_tw_viability_check(
        observable_type,
        np.deg2rad(15),
        observation_simulation_settings,
        links,
    )
    return observation_settings_list, observation_simulation_settings


def create_simple_1w_range_sensors(
    links, light_time_correction_settings, observation_times
):
    observable_type = observation.one_way_range_type
    observation_settings_list = add_simple_1w_range_observation_settings(
        links,
        light_time_correction_settings=light_time_correction_settings,
    )
    observation_simulation_settings = add_observation_simulators(
        observation_times,
        links,
        observable_type,
    )
    add_noise(
        1.0,
        observable_type,
        observation_simulation_settings,
    )
    add_tw_viability_check(
        observable_type,
        np.deg2rad(15),
        observation_simulation_settings,
        links,
    )
    return observation_settings_list, observation_simulation_settings, observable_type
