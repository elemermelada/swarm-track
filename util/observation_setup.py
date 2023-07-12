def create_links(observation, tw_number, body):
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


def add_simple_doppler_observation_settings(
    observation,
    tw_number,
    links,
    observation_settings_list: list = list(),
    light_time_correction_settings=None,
):
    light_time_correction_settings = (
        observation.first_order_relativistic_light_time_correction(["Sun"])
    )
    for i in range(tw_number):
        observation_settings_list.append(
            observation.one_way_doppler_instantaneous(
                links[i],
                light_time_correction_settings=[light_time_correction_settings],
            )
        )
    return observation_settings_list


def add_simple_range_observation_settings(
    observation,
    tw_number,
    links,
    observation_settings_list: list = list(),
    light_time_correction_settings=None,
    bias=0.01,
):
    range_bias_settings = observation.absolute_bias([bias])
    for i in range(tw_number):
        observation_settings_list.append(
            observation.one_way_range(
                links[i],
                light_time_correction_settings=[light_time_correction_settings],
                bias_settings=range_bias_settings,
            )
        )
    return observation_settings_list


def add_observation_simulators(
    observation,
    observation_times,
    links,
    tw_number,
    observation_type,
    observation_simulation_settings: list = list(),
):
    for i in range(tw_number):
        observation_simulation_settings.append(
            observation.tabulated_simulation_settings(
                observation_type, links[i], observation_times
            )
        )
    return observation_simulation_settings


def add_noise(
    observation, noise_level, observation_type, observation_simulation_settings
):
    observation.add_gaussian_noise_to_observable(
        observation_simulation_settings, noise_level, observation_type
    )


def add_viability_check(
    observation,
    observation_type,
    elevation_angle,
    tw_number,
    observation_simulation_settings,
    links,
):
    for i in range(tw_number):
        viability_settings = [
            observation.elevation_angle_viability(["Mars", f"TW{i}"], elevation_angle)
        ]
        observation.add_viability_check_to_observable_for_link_ends(
            observation_simulation_settings,
            viability_settings,
            observation_type,
            links[i],
        )
