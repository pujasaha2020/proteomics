# this is a python script to test unified model.
import numpy as np
import pandas as pd
import pytest
import yaml

# from box.manager import BoxManager
from datasets.sleepdebt.unified_model.sleepdebt_calculation import (
    Protocol,
    calculate_debt,
    construct_protocol,
)


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
    file_path = "tests/test_protocol.yaml"
    return read_yaml(file_path)


@pytest.fixture(name="protocol")
def define_protocol(input_yaml_construct_protocol: dict):
    """
    This function defines the protocol
    """
    protocol = Protocol("protocol1", "def_2")
    t_ae_sl = construct_protocol(input_yaml_construct_protocol, protocol.name)

    protocol.fill(t_ae_sl[0], t_ae_sl[1])
    return protocol


def test_awake_period1(df: pd.DataFrame, param_dict: dict) -> None:
    """
    This function tests the values of dl/dt and ds/dt during awake period
    In the toy protocol there are two awake period:0-960, 1441-3600


    """

    start = 0  # 0  # 1441
    end = 961  # 961  # 3601

    multiply_l_with_u = df["l_debt"][start:end] * param_dict["U"]
    multiply_s_with_u = df["s_debt"][start:end] * param_dict["U"]
    print("debt from model.py l", multiply_l_with_u[0:20])
    print("debt from model.py s", multiply_s_with_u[0:20])
    dl_dt_lhs = np.diff(multiply_l_with_u)  # [start:end]
    # )  # LHS of dy1/dt from the solution
    ds_dt_lhs = np.diff(multiply_s_with_u)  # [start:end]
    # )  # LHS of dy2/dt from the solution

    print(dl_dt_lhs[0:10])
    print(ds_dt_lhs[0:10])

    dl_dt_rhs = (-multiply_l_with_u[start:end] + param_dict["U"]) / param_dict["TAU_LA"]

    # RHS of dy1/dt
    ds_dt_rhs = (-multiply_s_with_u[start:end] + param_dict["U"]) / param_dict[
        "TAU_W"
    ]  # RHS of dy2/dt
    print(dl_dt_rhs[0:10])
    print(ds_dt_rhs[0:10])

    if len(dl_dt_lhs) != len(dl_dt_rhs):
        min_len = min(len(dl_dt_lhs), len(dl_dt_rhs))
        dl_dt_lhs = dl_dt_lhs[:min_len]
        dl_dt_rhs = dl_dt_rhs[:min_len]

    if len(ds_dt_lhs) != len(ds_dt_rhs):
        min_len = min(len(ds_dt_lhs), len(ds_dt_rhs))
        ds_dt_lhs = ds_dt_lhs[:min_len]
        ds_dt_rhs = ds_dt_rhs[:min_len]

    # diff_y1 = np.abs(dy1_dt_lhs - dy1_dt_rhs)  # Difference for y1
    # diff_y2 = np.abs(dy2_dt_lhs - dy2_dt_rhs)  # Difference for y2
    np.testing.assert_allclose(
        dl_dt_lhs,
        dl_dt_rhs,
        rtol=0.005,
        err_msg="l(t) values do not match during awake(period1)",
    )

    np.testing.assert_allclose(
        ds_dt_lhs,
        ds_dt_rhs,
        rtol=0.0003,
        err_msg="s(t) values do not match awake(period1)",
    )
    #
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
    multiply_l_with_u = df["l_debt"][start:end] * param_dict["U"]
    multiply_s_with_u = df["s_debt"][start:end] * param_dict["U"]

    print("debt from model.py l", multiply_l_with_u[0:20])
    print("debt from model.py s", multiply_s_with_u[0:20])

    dl_dt_lhs = np.diff(multiply_l_with_u)  # [start:end]
    # )  # LHS of dy1/dt from the solution
    ds_dt_lhs = np.diff(multiply_s_with_u)  # [start:end]
    # )  # LHS of dy2/dt from the solution

    print(dl_dt_lhs[0:10])
    print(ds_dt_lhs[0:10])

    dl_dt_rhs = (-multiply_l_with_u - 2 * param_dict["U"]) / param_dict["TAU_LA"]
    # RHS of dy1/dt
    ds_dt_rhs = -(multiply_s_with_u - multiply_l_with_u) / param_dict["TAU_S"]
    # RHS of dy2/dt

    print(dl_dt_rhs[0:10])
    print(ds_dt_rhs[0:10])

    if len(dl_dt_lhs) != len(dl_dt_rhs):
        min_len = min(len(dl_dt_lhs), len(dl_dt_rhs))
        dl_dt_lhs = dl_dt_lhs[:min_len]
        dl_dt_rhs = dl_dt_rhs[:min_len]

    if len(ds_dt_lhs) != len(ds_dt_rhs):
        min_len = min(len(ds_dt_lhs), len(ds_dt_rhs))
        ds_dt_lhs = ds_dt_lhs[:min_len]
        ds_dt_rhs = ds_dt_rhs[:min_len]

    # diff_y1 = np.abs(dy1_dt_lhs - dy1_dt_rhs)  # Difference for y1
    # diff_y2 = np.abs(dy2_dt_lhs - dy2_dt_rhs)  # Difference for y2

    np.testing.assert_allclose(
        dl_dt_lhs,
        dl_dt_rhs,
        rtol=0.0005,
        err_msg="l(t) values do not match during sleep(period1)",
    )

    np.testing.assert_allclose(
        ds_dt_lhs,
        ds_dt_rhs,
        rtol=0.008,
        err_msg="s(t) values do not match sleep(period1)",
    )


def test_awake_period2(df: pd.DataFrame, param_dict: dict) -> None:
    """
    This function tests the values of dl/dt and ds/dt during awake period
    In the toy protocol there are two awake period:0-960, 1441-3600


    """

    start = 1441  # 0  # 1441
    end = 3601  # 961  # 3601

    multiply_l_with_u = df["l_debt"][start:end] * param_dict["U"]
    multiply_s_with_u = df["s_debt"][start:end] * param_dict["U"]
    print("debt from model.py l", multiply_l_with_u[0:20])
    print("debt from model.py s", multiply_s_with_u[0:20])
    dl_dt_lhs = np.diff(multiply_l_with_u)  # [start:end]
    # )  # LHS of dy1/dt from the solution
    ds_dt_lhs = np.diff(multiply_s_with_u)  # [start:end]
    # )  # LHS of dy2/dt from the solution

    print(dl_dt_lhs[0:10])
    print(ds_dt_lhs[0:10])

    dl_dt_rhs = (-multiply_l_with_u + param_dict["U"]) / param_dict["TAU_LA"]

    # RHS of dy1/dt
    ds_dt_rhs = (-multiply_s_with_u + param_dict["U"]) / param_dict[
        "TAU_W"
    ]  # RHS of dy2/dt
    print(dl_dt_rhs[0:10])
    print(ds_dt_rhs[0:10])

    if len(dl_dt_lhs) != len(dl_dt_rhs):
        min_len = min(len(dl_dt_lhs), len(dl_dt_rhs))
        dl_dt_lhs = dl_dt_lhs[:min_len]
        dl_dt_rhs = dl_dt_rhs[:min_len]

    if len(ds_dt_lhs) != len(ds_dt_rhs):
        min_len = min(len(ds_dt_lhs), len(ds_dt_rhs))
        ds_dt_lhs = ds_dt_lhs[:min_len]
        ds_dt_rhs = ds_dt_rhs[:min_len]

    # diff_y1 = np.abs(dy1_dt_lhs - dy1_dt_rhs)  # Difference for y1
    # diff_y2 = np.abs(dy2_dt_lhs - dy2_dt_rhs)  # Difference for y2
    np.testing.assert_allclose(
        dl_dt_lhs,
        dl_dt_rhs,
        rtol=0.0005,
        err_msg="l(t) values do not match during awake(period2)",
    )

    np.testing.assert_allclose(
        ds_dt_lhs,
        ds_dt_rhs,
        rtol=0.0003,
        err_msg="s(t) values do not match awake(period2)",
    )
    #
    # return diff_y1, diff_y2


def test_sleep_period2(df: pd.DataFrame, param_dict: dict) -> None:
    """
    This function tests the values of datot/dt and dr1tot/dt during sleep period
    sleep period: 961-1440, 3601-4080

    solution of Atot gives equal LHS and RHS upto .0025 tolerance.
    most of solution of R1tot gives equal LHS and RHS upto .1 tolerance over both periods.
    Number of solutions that gives tolerance greater than .1 are 10 out of 479.
    the absolute difference in both cases (atot,r1tot) are of the order of e-06.


    """

    start = 3601  # 961  # 3601
    end = 4081  # 1441  # 4081
    multiply_l_with_u = df["l_debt"][start:end] * param_dict["U"]
    multiply_s_with_u = df["s_debt"][start:end] * param_dict["U"]

    print("debt from model.py l", multiply_l_with_u[0:20])
    print("debt from model.py s", multiply_s_with_u[0:20])

    dl_dt_lhs = np.diff(multiply_l_with_u)  # [start:end]
    # )  # LHS of dy1/dt from the solution
    ds_dt_lhs = np.diff(multiply_s_with_u)  # [start:end]
    # )  # LHS of dy2/dt from the solution

    print(dl_dt_lhs[0:10])
    print(ds_dt_lhs[0:10])

    dl_dt_rhs = (-multiply_l_with_u - 2 * param_dict["U"]) / param_dict["TAU_LA"]
    # RHS of dy1/dt
    ds_dt_rhs = -(multiply_s_with_u - multiply_l_with_u) / param_dict["TAU_S"]
    # RHS of dy2/dt

    print(dl_dt_rhs[0:10])
    print(ds_dt_rhs[0:10])

    if len(dl_dt_lhs) != len(dl_dt_rhs):
        min_len = min(len(dl_dt_lhs), len(dl_dt_rhs))
        dl_dt_lhs = dl_dt_lhs[:min_len]
        dl_dt_rhs = dl_dt_rhs[:min_len]

    if len(ds_dt_lhs) != len(ds_dt_rhs):
        min_len = min(len(ds_dt_lhs), len(ds_dt_rhs))
        ds_dt_lhs = ds_dt_lhs[:min_len]
        ds_dt_rhs = ds_dt_rhs[:min_len]

    # diff_y1 = np.abs(dy1_dt_lhs - dy1_dt_rhs)  # Difference for y1
    # diff_y2 = np.abs(dy2_dt_lhs - dy2_dt_rhs)  # Difference for y2

    np.testing.assert_allclose(
        dl_dt_lhs,
        dl_dt_rhs,
        rtol=0.0005,
        err_msg="l(t) values do not match during sleep(period2)",
    )

    np.testing.assert_allclose(
        ds_dt_lhs,
        ds_dt_rhs,
        rtol=0.008,
        err_msg="s(t) values do not match sleep(period2)",
    )


# solution of the differential equation of atot and r1tot from
# Runge Kutta Method are tested by checking
# both side of the differential equations are approximately equal.


@pytest.fixture(name="param_dict")
def parameters() -> dict:
    """
    This function returns the parameters
    """
    model_parameters = {
        "U": 24.1,
        "TAU_LA": 4.06 * 24 * 60,  # 4.06
        "TAU_W": 40 * 60,
        "TAU_S": 1 * 60,
    }

    return model_parameters


@pytest.fixture(name="df")
def df_model(protocol: Protocol) -> pd.DataFrame:
    """
    This function returns the dataframe for testing the model
    """
    debt = calculate_debt(protocol)
    print(debt.shape)
    debt.drop_duplicates(inplace=True)
    debt.reset_index(inplace=True, drop=True)
    print(debt.head())
    return debt
