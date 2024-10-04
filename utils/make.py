"""
make scripts
"""

from box.manager import BoxManager
from datasets.sleepdebt.protocol import Protocol
from utils.get import get_parameters


def make_protocol_list() -> list:
    "getting protocols list as string"
    protocol_list = []
    for i in range(1, 14):  # Assuming you have 3 protocols
        if i == 8:
            for j in range(1, 10):
                function_name = f"protocol{i}_{j}"
                # print(function_name)
                protocol_list.append(function_name)
        else:
            function_name = f"protocol{i}"
            # print(function_name)
            protocol_list.append(function_name)
    # print(protocol_list)
    return protocol_list


def make_protocol_object_list(protocol_list: list, definition: str) -> list[Protocol]:
    """
    Create protocol objects
    """
    definition = "def_2"
    return [Protocol(name, definition) for name in protocol_list]


def make_sleep_wake_tuple(protocol_data: dict, protocol_name: str) -> tuple:
    """construct protocol from yaml file"""
    print(protocol_name)
    protocol = protocol_data["protocols"][protocol_name]

    # Construct t_awake_l
    t_awake_l = []
    for item in protocol["t_awake_l"]:
        # print(type(item))
        if "repeat" in item:
            repeat_value = protocol["t_awake_l"][item][
                "value"
            ]  # Ensure value is an integer
            repeat_count = protocol["t_awake_l"][item][
                "count"
            ]  # Ensure count is an integer
            t_awake_l.extend([repeat_value] * repeat_count)

        elif "append" in item:
            append_value = protocol["t_awake_l"][
                item
            ]  # Ensure append value is an integer
            t_awake_l.extend(append_value)  # Use append for single values

        else:
            raise ValueError(f"Invalid key in t_awake_l: {item}")

    # Construct t_sleep_l
    t_sleep_l = []
    for item in protocol["t_sleep_l"]:
        if "repeat" in item:
            repeat_value = protocol["t_sleep_l"][item][
                "value"
            ]  # Ensure value is an integer
            repeat_count = protocol["t_sleep_l"][item][
                "count"
            ]  # Ensure count is an integer
            t_sleep_l.extend([repeat_value] * repeat_count)
        elif "append" in item:
            append_value = protocol["t_sleep_l"][
                item
            ]  # Ensure append value is an integer
            t_sleep_l.extend(append_value)  # Use append for single values
        else:
            raise ValueError(f"Invalid key in t_sleep_l: {item}")

    return t_awake_l, t_sleep_l


def make_parameters_dict(box1: BoxManager) -> dict:
    """
    Get the parameters from box and then save them in a dictionary
    """
    adenosine = get_parameters(box1)
    param_dict = {
        "au_i": adenosine["parameters"]["set1"]["au_i"],
        "kd1": min(max(adenosine["parameters"]["set1"]["kd1"], 1), 10),
        "kd2": min(max(adenosine["parameters"]["set1"]["kd2"], 100), 10000),
        "k1": adenosine["parameters"]["set1"]["k1"],
        "param3": min(max(adenosine["parameters"]["set1"]["param3"], 0), 1),
        "chi_w": adenosine["parameters"]["set1"][
            "chi_w"
        ],  # time constant for exponential decay during wake (h)
        "chi_s": adenosine["parameters"]["set1"][
            "chi_s"
        ],  # time constant for exponential decay during sleep (h)
        "lambda1": adenosine["parameters"]["set1"]["lambdas"] * 60,  # 306, 291
        "mu_s": 596.4,
        "mu_w": 869.5,
    }
    return param_dict
