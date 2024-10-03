"""test scripts for utils/make.py"""

import pytest
import yaml

from utils.make import make_protocol_list, make_sleep_wake_tuple


@pytest.fixture(name="expected_protocol_list")
def protocol_list():
    """This function returns the list of protocols"""
    return [
        "protocol1",
        "protocol2",
        "protocol3",
        "protocol4",
        "protocol5",
        "protocol6",
        "protocol7",
        "protocol8_1",
        "protocol8_2",
        "protocol8_3",
        "protocol8_4",
        "protocol8_5",
        "protocol8_6",
        "protocol8_7",
        "protocol8_8",
        "protocol8_9",
        "protocol9",
        "protocol10",
        "protocol11",
        "protocol12",
        "protocol13",
    ]


def test_make_protocol_list(expected_protocol_list: list):
    """
    Protocols in the yaml file are named as "protocol1", "protocol2", etc.
    Protocol for Forced Dysynchrony  is named as "protocol8_1" and "protocol8_2".
    Because different subject has
    different sleep/wake schedule.
    """
    info = make_protocol_list()
    assert (
        info == expected_protocol_list
    ), "The actual output does not match the expected output."


# Function to read a YAML file
def read_yaml(file_path):
    """This function reads a yaml file and returns the data"""
    with open(file_path, encoding="utf-8") as file:
        data = yaml.safe_load(file)
    return data


@pytest.fixture(name="input_yaml_construct_protocol")
def get_toy_protocol():
    """This function reads the yaml file and returns the data"""
    file_path = "tests/utils/test_protocol.yaml"
    return read_yaml(file_path)


@pytest.fixture(name="expected_protocol")
def expected_output_from_make_sleep_wake_tuple():
    """This function returns the expected protocol"""
    return (
        [960, 2160],
        [480, 480],
    )


def test_make_sleep_wake_tuple(
    input_yaml_construct_protocol: dict, expected_protocol: tuple
):
    """This function tests the function construct_protocol in the adenosine_model.py"""
    protocols = make_sleep_wake_tuple(input_yaml_construct_protocol, "protocol1")

    assert (
        protocols == expected_protocol
    ), "The actual output does not match the expected output."
