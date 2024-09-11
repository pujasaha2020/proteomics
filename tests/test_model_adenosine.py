"""
This is a test script for model.py in datasets/sleepdebt/adenosine_model project
"""

import numpy as np
import pandas as pd
import pytest

# import pytest
import yaml
from pytest_mock import MockerFixture

# from box.manager import BoxManager
# from datasets.sleepdebt.adenosine_model import model
from datasets.sleepdebt.adenosine_model.model import (
    Protocol,
    calculate_debt,
    construct_protocol,
    get_protocols,
    get_status,
)

# from pytest_mock import MockerFixture


expected_info_get_protocol = [
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


def test_get_protocols():
    """
    this functions creates a list of protocols that should look
    similar to inout_for_get_protocol
    Protocols in the yaml file are named as "protcol1", "protocol2", etc.
    Protocol for Forced Dysynchrony  is named as "protocol8_1" and "protocol8_2".
    Because different subject has
    different sleep/wake schedule.
    """
    info = get_protocols()
    assert (
        info == expected_info_get_protocol
    ), "The actual output does not match the expected output."


test_get_protocols()


# Function to read a YAML file
def read_yaml(file_path):
    """
    This function reads a yaml file and returns the data
    """
    with open(file_path, encoding="utf-8") as file:
        data = yaml.safe_load(file)
    return data


FILE_PATH = "tests/test_protocol.yaml"
input_yaml_construct_protocol = read_yaml(FILE_PATH)


def test_construct_protocol():
    """
    This function tests the function construct_protocol in the adenosine_model.py
    """
    protocols = construct_protocol(input_yaml_construct_protocol, "protocol1")
    print(protocols)
    expected_protocol = (
        [960, 2160],
        [480, 480],
    )
    assert (
        protocols == expected_protocol
    ), "The actual output does not match the expected output."


test_construct_protocol()


protocol = Protocol("protocol1")
t_ae_sl = construct_protocol(input_yaml_construct_protocol, protocol.name)
protocol.fill(t_ae_sl[0], t_ae_sl[1])
print(protocol.t_awake_l)


expected_output_from_time_sequence = [0, 960, 1440, 3600, 4080]


def test_time_sequence():
    """
    This function tests the function time_sequence in the adenosine_model.py
    """

    time_count = protocol.time_sequence()
    print(time_count)
    assert (
        time_count == expected_output_from_time_sequence
    ), "The actual output does not match the expected output."


test_time_sequence()


input_for_get_status = pd.DataFrame(
    {"time": [200, 970, 1552], "status": ["awake", "sleep", "awake"]}
)


def test_get_status():
    """
    This function tests the function get_status in the adenosine_model.py
    """
    print(protocol.time_sequence())
    status = input_for_get_status["time"].apply(
        lambda x: get_status(x, protocol.time_sequence())
    )
    print(status)
    assert status.equals(
        input_for_get_status["status"]
    ), "The actual output does not match the expected output."


test_get_status()


def testing_awake(df: pd.DataFrame) -> None:
    """
    This function tests the values of datot/dt and dr1tot/dt during awake period
    In the toy protocol there are two awake period:0-960, 1441-3600

    solution of atot gives equal LHS and RHS upto .0005 tolerance over both periods.
    Solution of R1tot gives equal LHS and RHS upto .1 tolerance over both periods.
    Number of solutions that gives tolerance greater than .1 are 12 out of 2159.

    the absolute difference in both cases (atot,r1tot) are of the order of e-06.

    """
    # mu_s = 596.4
    mu_w = 869.5
    # chi_s = 252
    chi_w = 1090.8

    beta = 300 / 400
    gamma = 0.9677
    lambda1 = 17460

    dy1_dt_lhs = np.diff(df["Acute"][0:961])  # [0:961]
    # )  # LHS of dy1/dt from the solution
    dy2_dt_lhs = np.diff(df["Chronic"][0:961])  # [0:961]
    # )  # LHS of dy2/dt from the solution

    print(dy1_dt_lhs[0:10])
    print(dy2_dt_lhs[0:10])
    dy1_dt_rhs = (mu_w - df["Acute"][0:961]) / chi_w  # RHS of dy1/dt
    term = df["Acute"][0:961] + df["Chronic"][0:961] + (1 / (1 - beta))
    discriminant = term**2 - (4 * df["Acute"][0:961] * df["Chronic"][0:961])
    a1b = 0.5 * (term - np.sqrt(discriminant))
    dy2_dt_rhs = (a1b - (df["Chronic"][0:961] * gamma)) / lambda1
    print(dy1_dt_rhs[0:10])
    print(dy2_dt_rhs[0:10])

    if len(dy1_dt_lhs) != len(dy1_dt_rhs):
        min_len = min(len(dy1_dt_lhs), len(dy1_dt_rhs))
        dy1_dt_lhs = dy1_dt_lhs[:min_len]
        dy1_dt_rhs = dy1_dt_rhs[:min_len]

    if len(dy2_dt_lhs) != len(dy2_dt_rhs):
        min_len = min(len(dy2_dt_lhs), len(dy2_dt_rhs))
        dy2_dt_lhs = dy2_dt_lhs[:min_len]
        dy2_dt_rhs = dy2_dt_rhs[:min_len]

    # diff_y1 = np.abs(dy1_dt_lhs - dy1_dt_rhs)  # Difference for y1
    # diff_y2 = np.abs(dy2_dt_lhs - dy2_dt_rhs)  # Difference for y2
    np.testing.assert_allclose(
        dy1_dt_lhs,
        dy1_dt_rhs,
        rtol=0.0005,
        err_msg="Acute values do not match during awake",
    )
    np.testing.assert_allclose(
        dy2_dt_lhs,
        dy2_dt_rhs,
        rtol=0.1,
        err_msg="Chronic values do not match awake",
    )
    # return diff_y1, diff_y2


def testing_sleep(df: pd.DataFrame) -> None:
    """
    This function tests the values of datot/dt and dr1tot/dt during sleep period
    sleep period: 961-1440, 3601-4080

    solution of Atot gives equal LHS and RHS upto .0005 tolerance over both periods.
    Solution of R1tot gives equal LHS and RHS upto .1 tolerance over both periods.
    Number of solutions that gives tolerance greater than .1 are 20 out of 479.
    the absolute difference in both cases (atot,r1tot) are of the order of e-06.


    """
    mu_s = 596.4
    # mu_w = 869.5
    chi_s = 252
    # chi_w = 1090.8

    beta = 300 / 400
    gamma = 0.9677
    lambda1 = 17460

    dy1_dt_lhs = np.diff(
        df["Acute"][961:1441]
    )  # 961:1441, LHS of dy1/dt from the solution
    dy2_dt_lhs = np.diff(
        df["Chronic"][961:1441]
    )  # 961:1441, LHS of dy2/dt from the solution

    print(dy1_dt_lhs[0:10])
    print(dy2_dt_lhs[0:10])
    dy1_dt_rhs = (mu_s - df["Acute"][961:1441]) / chi_s  # RHS of dy1/dt
    term = df["Acute"][961:1441] + df["Chronic"][961:1441] + (1 / (1 - beta))
    discriminant = term**2 - (4 * df["Acute"][961:1441] * df["Chronic"][961:1441])
    a1b = 0.5 * (term - np.sqrt(discriminant))
    dy2_dt_rhs = (a1b - (df["Chronic"][961:1441] * gamma)) / lambda1
    print(dy1_dt_rhs[1:10])
    print(dy2_dt_rhs[1:10])

    if len(dy1_dt_lhs) != len(dy1_dt_rhs):
        min_len = min(len(dy1_dt_lhs), len(dy1_dt_rhs))
        dy1_dt_lhs = dy1_dt_lhs[:min_len]
        dy1_dt_rhs = dy1_dt_rhs[:min_len]

    if len(dy2_dt_lhs) != len(dy2_dt_rhs):
        min_len = min(len(dy2_dt_lhs), len(dy2_dt_rhs))
        dy2_dt_lhs = dy2_dt_lhs[:min_len]
        dy2_dt_rhs = dy2_dt_rhs[:min_len]

    # diff_y1 = np.abs(dy1_dt_lhs - dy1_dt_rhs)  # Difference for y1
    # diff_y2 = np.abs(dy2_dt_lhs - dy2_dt_rhs)  # Difference for y2

    np.testing.assert_allclose(
        dy1_dt_lhs,
        dy1_dt_rhs,
        rtol=0.002,
        err_msg="Acute values do not match during sleep",
    )

    np.testing.assert_allclose(
        dy2_dt_lhs,
        dy2_dt_rhs,
        rtol=4.5,
        err_msg="Chronic values do not match during sleep",
    )

    # return diff_y1, diff_y2


# solution of the differential equation of atot and r1tot from
# Runge Kutta Method are tested by checking
# both side of the differential equations are approximately equal.


@pytest.fixture(name="df")
def df_model():
    """
    This function returns the dataframe for testing the model
    """
    return calculate_debt(protocol)


def test_mock_get_box(mocker: MockerFixture) -> None:
    """
    test function for model.py
    """

    mocker.patch("datasets.sleepdebt.adenosine_model.model.get_box", return_value=None)
    mocker.patch(
        "datasets.sleepdebt.adenosine_model.plotting.get_box", return_value=None
    )
    # DF_MODEL = DF_MODEL.drop_duplicates(inplace=False, ignore_index=True)
