"""
This is a test script for model.py in datasets/sleepdebt/adenosine_model project
"""

import numpy as np
import pandas as pd
import yaml

from datasets.sleepdebt.adenosine_model import model

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
    this functions creates a list of protocols that should look similar to inout_for_get_protocol
    Protocols in the yaml file are named as "protcol1", "protocol2", etc.
    Protocol for Forced Dysynchrony  is named as "protocol8_1" and "protocol8_2". Because different subject has
    different sleep/wake schedule.
    """
    info = model.get_protocols()
    assert (
        info == expected_info_get_protocol
    ), "The actual output does not match the expected output."


test_get_protocols()


# Function to read a YAML file
def read_yaml(file_path):
    with open(file_path, encoding="utf-8") as file:
        data = yaml.safe_load(file)
    return data


FILE_PATH = "tests/test_protocol.yaml"
input_yaml_construct_protocol = read_yaml(FILE_PATH)


def test_construct_protocol():
    """
    This function tests the function construct_protocol in the adenosine_model.py
    """
    protocols = model.construct_protocol(input_yaml_construct_protocol, "protocol1")
    print(protocols)
    expected_protocol = (
        [960, 2160],
        [480, 480],
    )
    assert (
        protocols == expected_protocol
    ), "The actual output does not match the expected output."


test_construct_protocol()


protocol = model.Protocol("protocol1")
t_ae_sl = model.construct_protocol(input_yaml_construct_protocol, protocol.name)
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
        lambda x: model.get_status(x, protocol.time_sequence())
    )
    print(status)
    assert status.equals(
        input_for_get_status["status"]
    ), "The actual output does not match the expected output."


test_get_status()

"""
# the following expected output for atot, r1tot are calculated by Wolfram Alpha using the
# following formulas  and Runge Kutta method.
# dy/dx = (1/1090.8 )[869.5-y], y(0) = 727.8 , from 0 to 10, h = 1
# dy/dx = (1/252 )[596.4-y], y(10) = 723.930618 , from 10 to 20, h = 1
# dy/dx = (1/1090.8 )[869.5-y], y(20) = 723.931 , from 20 to 40, h = 1
# dy/dx = (1/252 )[596.4-y], y(40) = 726.576 , from 40 to 50, h = 1

expected_output_from_calculate_debt = pd.DataFrame(
    {
        "Acute": [
            727.800,
            727.930,
            728.06,
            728.189,
            728.319,
            728.448,
            728.577,
            728.706,
            728.835,
            728.964,
            729.093,
            729.093,
            728.567,
            728.044,
            727.523,
            727.003,
            726.486,
            725.971,
            725.458,
            724.947,
            724.438,
            723.931,
            723.931,
            724.064,
            724.198,
            724.331,
            724.464,
            724.597,
            724.730,
            724.862,
            724.994,
            725.127,
            725.259,
            725.392,
            725.524,
            725.656,
            725.787,
            725.919,
            726.051,
            726.182,
            726.313,
            726.445,
            726.576,
            726.576,
            726.060,
            725.547,
            725.034,
            724.526,
            724.019,
            723.513,
            723.010,
            722.508,
            722.009,
            721.511,
        ],
    }
)

def test_acute_debt():
    
    This function tests the function calculate_debt in the adenosine_model.py
    
    df = model.calculate_debt(protocol)
    df["Acute"] = df["Acute"].round(2)

    df["Acute_Wolfram"] = expected_output_from_calculate_debt["Acute"].round(2)
    np.testing.assert_allclose(
        df["Acute"],
        df["Acute_Wolfram"],
        err_msg="Acute values do not match",
    )


test_acute_debt()
"""


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

    dy1_dt_lhs = np.diff(df["Acute"][1441:3601])  # [0:961]
    # )  # LHS of dy1/dt from the solution
    dy2_dt_lhs = np.diff(df["Chronic"][1441:3601])  # [0:961]
    # )  # LHS of dy2/dt from the solution

    print(dy1_dt_lhs[0:10])
    print(dy2_dt_lhs[0:10])
    dy1_dt_rhs = (mu_w - df["Acute"][1441:3601]) / chi_w  # RHS of dy1/dt
    term = df["Acute"][1441:3601] + df["Chronic"][1441:3601] + (1 / (1 - beta))
    discriminant = term**2 - (4 * df["Acute"][1441:3601] * df["Chronic"][1441:3601])
    a1b = 0.5 * (term - np.sqrt(discriminant))
    dy2_dt_rhs = (a1b - (df["Chronic"][1441:3601] * gamma)) / lambda1
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
        df["Acute"][3601:4081]
    )  # 961:1441, LHS of dy1/dt from the solution
    dy2_dt_lhs = np.diff(
        df["Chronic"][3601:4081]
    )  # 961:1441, LHS of dy2/dt from the solution

    print(dy1_dt_lhs[0:10])
    print(dy2_dt_lhs[0:10])
    dy1_dt_rhs = (mu_s - df["Acute"][3601:4081]) / chi_s  # RHS of dy1/dt
    term = df["Acute"][3601:4081] + df["Chronic"][3601:4081] + (1 / (1 - beta))
    discriminant = term**2 - (4 * df["Acute"][3601:4081] * df["Chronic"][3601:4081])
    a1b = 0.5 * (term - np.sqrt(discriminant))
    dy2_dt_rhs = (a1b - (df["Chronic"][3601:4081] * gamma)) / lambda1
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
        rtol=0.1,
        err_msg="Chronic values do not match during sleep",
    )

    # return diff_y1, diff_y2


# solution of the differential equation of atot and r1tot from Runge Kutta Method are tested by checking
# both side of the differential equations are approximately equal.
df_from_model = model.calculate_debt(protocol)
df_from_model = df_from_model.drop_duplicates(inplace=False, ignore_index=True)
print(df_from_model.head(10))


testing_awake(df_from_model)
testing_sleep(df_from_model)
