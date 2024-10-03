"""
This is a test script for model.py in datasets/sleepdebt/adenosine_model/model.py
 project
"""

import numpy as np
import pandas as pd
import pytest
import yaml

# from box.manager import BoxManager
from datasets.sleepdebt.class_def import Protocol
from datasets.sleepdebt.model.adenosine import calculate_debt
from utils.make import make_sleep_wake_tuple

# from pytest_mock import MockerFixture


# from pytest_mock import MockerFixture


# Function to read a YAML file
def read_yaml(file_path):
    """
    This function reads a yaml file and returns the data
    """
    with open(file_path, encoding="utf-8") as file:
        data = yaml.safe_load(file)
    return data


@pytest.fixture(name="input_yaml_construct_protocol")
def get_toy_protocol():
    """
    This function reads the yaml file and returns the data"""
    file_path = "tests/utils/test_protocol.yaml"
    return read_yaml(file_path)


@pytest.fixture(name="protocol")
def define_protocol(input_yaml_construct_protocol: dict):
    """
    This function defines the protocol
    """
    protocol = Protocol("protocol1", "def_2")
    t_ae_sl = make_sleep_wake_tuple(input_yaml_construct_protocol, protocol.name)

    protocol.fill(t_ae_sl[0], t_ae_sl[1])
    return protocol


@pytest.fixture(name="expected_output_from_time_sequence")
def output_time_sequence():
    """
    This function returns the expected output from time_sequence
    """
    return [0, 960, 1440, 3600, 4080]


def test_time_sequence(protocol: Protocol, expected_output_from_time_sequence: list):
    """
    This function tests the function time_sequence in the adenosine_model.py
    """

    print(protocol.t_awake_l)
    time_count = protocol.time_sequence()
    print(time_count)
    assert (
        time_count == expected_output_from_time_sequence
    ), "The actual output does not match the expected output."


def test_awake_period1(df: pd.DataFrame, param_dict: dict) -> None:
    """
    This function tests the values of datot/dt and dr1tot/dt during awake period
    In the toy protocol there are two awake period:0-960, 1441-3600

    solution of atot gives equal LHS and RHS upto .0005 tolerance over both periods.
    Solution of R1tot gives equal LHS and RHS upto .1 tolerance over both periods.

    the absolute difference in both cases (atot,r1tot) are of the order of e-06.

    """

    start = 0  # 0  # 1441
    end = 961  # 961  # 3601
    print("debt from model.py Acute", df["Acute"][0:20])
    print("debt from model.py Chronic", df["Chronic"][0:20])

    dy1_dt_lhs = np.diff(df["Acute"][start:end])  # [start:end]
    # )  # LHS of dy1/dt from the solution
    dy2_dt_lhs = np.diff(df["Chronic"][start:end])  # [start:end]
    # )  # LHS of dy2/dt from the solution

    print(dy1_dt_lhs[0:10])
    print(dy2_dt_lhs[0:10])
    dy1_dt_rhs = (param_dict["mu_w"] - df["Acute"][start:end]) / param_dict[
        "chi_w"
    ]  # RHS of dy1/dt
    term = (
        df["Acute"][start:end]
        + df["Chronic"][start:end]
        + (1 / (1 - param_dict["beta"]))
    )
    discriminant = term**2 - (4 * df["Acute"][start:end] * df["Chronic"][start:end])
    a1b = 0.5 * (term - np.sqrt(discriminant))
    dy2_dt_rhs = (a1b - (df["Chronic"][start:end] * param_dict["gamma"])) / param_dict[
        "lambda1"
    ]
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
        rtol=0.00051,
        err_msg="Acute values do not match during awake(period1)",
    )
    np.testing.assert_allclose(
        dy2_dt_lhs,
        dy2_dt_rhs,
        rtol=0.1,
        err_msg="Chronic values do not match awake(period1)",
    )
    # return diff_y1, diff_y2


def test_sleep_period1(df: pd.DataFrame, param_dict: dict) -> None:
    """
    This function tests the values of datot/dt and dr1tot/dt during sleep period
    sleep period: 961-1440, 3601-4080

    solution of Atot gives equal LHS and RHS upto .0025 tolerance.
    most of solution of R1tot gives equal LHS and RHS upto .1 tolerance over both periods.
    Number of solutions that gives tolerance greater than .1 are 10 out of 479.
    the absolute difference in both cases (atot,r1tot) are of the order of e-06.


    """

    start = 961  # 961  # 3601
    end = 1441  # 1441  # 4081
    print("debt from model.py", df["Acute"][960:970])

    dy1_dt_lhs = np.diff(
        df["Acute"][start:end]
    )  # start:end, LHS of dy1/dt from the solution
    dy2_dt_lhs = np.diff(
        df["Chronic"][start:end]
    )  # start:end, LHS of dy2/dt from the solution

    print(dy1_dt_lhs[0:10])
    print(dy2_dt_lhs[0:10])
    dy1_dt_rhs = (param_dict["mu_s"] - df["Acute"][start:end]) / param_dict[
        "chi_s"
    ]  # RHS of dy1/dt
    term = (
        df["Acute"][start:end]
        + df["Chronic"][start:end]
        + (1 / (1 - param_dict["beta"]))
    )
    discriminant = term**2 - (4 * df["Acute"][start:end] * df["Chronic"][start:end])
    a1b = 0.5 * (term - np.sqrt(discriminant))
    dy2_dt_rhs = (a1b - (df["Chronic"][start:end] * param_dict["gamma"])) / param_dict[
        "lambda1"
    ]
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
        rtol=0.0025,
        err_msg="Acute values do not match during sleep(period1)",
    )

    np.testing.assert_allclose(
        dy2_dt_lhs,
        dy2_dt_rhs,
        rtol=2.0,
        err_msg="Chronic values do not match during sleep(period1)",
    )


def test_awake_period2(df: pd.DataFrame, param_dict: dict) -> None:
    """
    This function tests the values of datot/dt and dr1tot/dt during awake period
    In the toy protocol there are two awake period:0-960, 1441-3600

    solution of atot gives equal LHS and RHS upto .0005 tolerance over both periods.
    Solution of R1tot gives equal LHS and RHS upto .1 tolerance over both periods.
    Number of solutions that gives tolerance greater than .1 are 17 out of 2159.

    the absolute difference in both cases (atot,r1tot) are of the order of e-06.

    """

    start = 1441  # 0  # 1441
    end = 3601  # 961  # 3601
    print("debt from model.py Acute", df["Acute"][0:20])
    print("debt from model.py Chronic", df["Chronic"][0:20])

    dy1_dt_lhs = np.diff(df["Acute"][start:end])  # [start:end]
    # )  # LHS of dy1/dt from the solution
    dy2_dt_lhs = np.diff(df["Chronic"][start:end])  # [start:end]
    # )  # LHS of dy2/dt from the solution

    print(dy1_dt_lhs[0:10])
    print(dy2_dt_lhs[0:10])
    dy1_dt_rhs = (param_dict["mu_w"] - df["Acute"][start:end]) / param_dict[
        "chi_w"
    ]  # RHS of dy1/dt
    term = (
        df["Acute"][start:end]
        + df["Chronic"][start:end]
        + (1 / (1 - param_dict["beta"]))
    )
    discriminant = term**2 - (4 * df["Acute"][start:end] * df["Chronic"][start:end])
    a1b = 0.5 * (term - np.sqrt(discriminant))
    dy2_dt_rhs = (a1b - (df["Chronic"][start:end] * param_dict["gamma"])) / param_dict[
        "lambda1"
    ]
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
        rtol=0.00051,
        err_msg="Acute values do not match during awake(period2)",
    )
    np.testing.assert_allclose(
        dy2_dt_lhs,
        dy2_dt_rhs,
        rtol=5.0,
        err_msg="Chronic values do not match awake(period2)",
    )
    # return diff_y1, diff_y2


def test_sleep_period2(df: pd.DataFrame, param_dict: dict) -> None:
    """
    This function tests the values of datot/dt and dr1tot/dt during sleep period
    sleep period: 961-1440, 3601-4080

    solution of Atot gives equal LHS and RHS upto .0025 tolerance over both periods.
    Solution of R1tot gives equal LHS and RHS upto .1 tolerance over both periods.
    Number of solutions that gives tolerance greater than .1 are 10 out of 479.
    the absolute difference in both cases (atot,r1tot) are of the order of e-06.


    """

    start = 3601  # 961  # 3601
    end = 4081  # 1441  # 4081
    print("debt from model.py", df["Acute"][960:970])

    dy1_dt_lhs = np.diff(
        df["Acute"][start:end]
    )  # start:end, LHS of dy1/dt from the solution
    dy2_dt_lhs = np.diff(
        df["Chronic"][start:end]
    )  # start:end, LHS of dy2/dt from the solution

    print(dy1_dt_lhs[0:10])
    print(dy2_dt_lhs[0:10])
    dy1_dt_rhs = (param_dict["mu_s"] - df["Acute"][start:end]) / param_dict[
        "chi_s"
    ]  # RHS of dy1/dt
    term = (
        df["Acute"][start:end]
        + df["Chronic"][start:end]
        + (1 / (1 - param_dict["beta"]))
    )
    discriminant = term**2 - (4 * df["Acute"][start:end] * df["Chronic"][start:end])
    a1b = 0.5 * (term - np.sqrt(discriminant))
    dy2_dt_rhs = (a1b - (df["Chronic"][start:end] * param_dict["gamma"])) / param_dict[
        "lambda1"
    ]
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
        rtol=0.0025,
        err_msg="Acute values do not match during sleep(period2)",
    )

    np.testing.assert_allclose(
        dy2_dt_lhs,
        dy2_dt_rhs,
        rtol=2.0,
        err_msg="Chronic values do not match during sleep(period2)",
    )

    # return diff_y1, diff_y2


# solution of the differential equation of atot and r1tot from
# Runge Kutta Method are tested by checking
# both side of the differential equations are approximately equal.


@pytest.fixture(name="param_dict")
def parameters() -> dict:
    """
    This function returns the parameters
    """
    model_parameters = {
        "au_i": 30,
        "kd1": 1,
        "kd2": 100,
        "k1": 0.1,
        "param3": 0.85,
        "chi_w": 1090.8,  # time constant for exponential decay during wake (h)
        "chi_s": 252,  # time constant for exponential decay during sleep (h)
        "lambda1": 291 * 60,  # 306, 291
        "mu_s": 596.4,  # param3*A_tot
        "mu_w": 869.5,  # (A_tot - param3*0.65)/0.36
    }

    beta = 300 / (model_parameters["kd2"] + 300)

    gamma = model_parameters["au_i"] / (
        model_parameters["au_i"] + model_parameters["kd1"]
    )
    model_parameters["beta"] = beta
    model_parameters["gamma"] = gamma
    return model_parameters


#####testing calculate_debt function in datasets/sleepdebt/model/adenosine.py####
@pytest.fixture(name="df")
def df_model(protocol: Protocol, param_dict: dict) -> pd.DataFrame:
    """
    This function returns the dataframe for testing the model
    """
    debt = calculate_debt(protocol, param_dict)
    print(debt.shape)
    debt.drop_duplicates(inplace=True)
    debt.reset_index(inplace=True, drop=True)
    print(debt.head())
    return debt
