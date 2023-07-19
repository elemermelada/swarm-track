def create_ow_links(observation, tw_number, body):
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


def create_cart_link(observation, body):
    cart_link_ends = dict()
    cart_link_ends[observation.observed_body] = observation.body_origin_link_end_id(
        body
    )
    cart_link_definition = observation.LinkDefinition(cart_link_ends)
    return [cart_link_definition]


def add_simple_doppler_observation_settings(
    observation,
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


def add_simple_range_observation_settings(
    observation,
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
    observation,
    links,
    observation_settings_list: list = list(),
    bias=None,
):
    cartesian_bias_settings = None
    if bias:  # TODO - fix this shit maybe
        cartesian_bias_settings = observation.absolute_bias([bias])

    for link in links:
        observation_settings_list.append(
            observation.cartesian_position(
                link,
                bias_settings=None,
            )
        )
    return observation_settings_list


def add_observation_simulators(
    observation,
    observation_times,
    links,
    observation_type,
    observation_simulation_settings: list = list(),
):
    for link in links:
        observation_simulation_settings.append(
            observation.tabulated_simulation_settings(
                observation_type, link, observation_times
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
    observation_simulation_settings,
    links,
):
    for i in range(len(links)):
        viability_settings = [
            observation.elevation_angle_viability(["Mars", f"TW{i}"], elevation_angle)
        ]
        observation.add_viability_check_to_observable_for_link_ends(
            observation_simulation_settings,
            viability_settings,
            observation_type,
            links[i],
        )
