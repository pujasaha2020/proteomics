# test script for model.py in adenosine project

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
    print(info)
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
        [10, 20],
        [10, 10],
    )
    assert (
        protocols == expected_protocol
    ), "The actual output does not match the expected output."


test_construct_protocol()


protocol = model.Protocol("protocol1")
t_ae_sl = model.construct_protocol(input_yaml_construct_protocol, protocol.name)
protocol.fill(t_ae_sl[0], t_ae_sl[1])
print(protocol.t_awake_l)


expected_output_from_time_sequence = [0, 10, 20, 40, 50]


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
    {"time": [7, 15, 24], "status": ["awake", "sleep", "awake"]}
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
    print(input_for_get_status["status"])
    assert status.equals(
        input_for_get_status["status"]
    ), "The actual output does not match the expected output."


test_get_status()

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


def test_calculate_debt():
    """
    This function tests the function calculate_debt in the adenosine_model.py
    """
    df = model.calculate_debt(protocol)
    # print(df[["time", "Acute"]].round(2))
    df["Acute"] = df["Acute"].round(2)
    df["Acute_Wolfram"] = expected_output_from_calculate_debt["Acute"].round(2)
    # print(df[3:31])

    assert (
        df["Acute"]
        .round(2)
        .equals(expected_output_from_calculate_debt["Acute"].round(2))
    ), "The actual output does not match the expected output."


test_calculate_debt()
