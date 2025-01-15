"""
this scripts use the "protocol.yaml" file and then update it to 
"updated_protocol.yaml" to incorporate the Total Sleep Time (TST) information
for mppg protocols .

Note: The protocols  which exists in the protocol.yaml file will also
appear in the updated_protocol.yaml file, new protocols will be added at the end.
"""

from pathlib import Path
from typing import Any, Dict

import pandas as pd

from utils.get import get_box, get_protocols
from utils.save import save_to_yaml


def update_protocol_yml_mppg_ctl_10h(subject: str, data: dict) -> None:
    """
    Update the protocol YAML file with the
    TST values for the MPPG control 10H TIB protocol.
    """
    # TST starts from SP8.
    mppg_duffy = pd.read_excel(
        "/Users/pujasaha/Desktop/SleepDebt/TST_data_from_Jean/"
        + "MPPG_P2_LF_sleep_data_for_Puja_2024-12-12.xlsx",
        sheet_name=subject,
    )

    protocol_key = f"protocol_mppg_ctl_10H_{subject}"
    blood_sample_time = [11.60, 11.76, 11.94, 12.10, 12.26, 12.43, 12.60]
    data["protocols"][protocol_key] = {
        "description": "MPPG 10H TIB",
        "dataset": f"mppg_ctl_10H_{subject}",
        "t_awake_l": {"repeat1": {"count": 15, "value": 960}},
        "t_sleep_l": {"repeat1": {"count": 15, "value": 480}},
        "title": "Control sample: 10 hr of normal sleep schedule. n=26#4 ",
        "blood_sample_time": [x + 4 for x in blood_sample_time],
    }

    tst_values = mppg_duffy["Total Sleep Time (TST) mins"].tolist()
    sleep = {}
    awake = {}
    for i, value in enumerate(tst_values[0 : len(tst_values)], start=1):

        key = f"append{i}"
        if round(value) == 0:
            sleep[key] = [1]
        else:
            sleep[key] = [round(value)]

        awake[key] = [1440 - round(value)]

    # Update the YAML structure
    data["protocols"][protocol_key]["t_awake_l"].update(awake)
    data["protocols"][protocol_key]["t_sleep_l"].update(sleep)


def update_protocol_yml_mppg_ctl_8h(subject: str, data: dict) -> None:
    """
    Update the protocol YAML file with the TST
    values for the MPPG control 8H TIB protocol.
    """
    mppg_duffy = pd.read_excel(
        "/Users/pujasaha/Desktop/SleepDebt/TST_data_from_Jean/"
        + "MPPG_HF_CTRL_individual_sleep_10-30-19_for_Puja_2024-12-12.xlsx",
        sheet_name=subject,
    )

    protocol_key = f"protocol_mppg_ctl_8H_{subject}"
    blood_sample_time = [11.53, 11.74, 11.95, 12.03, 12.2, 12.37, 12.53]
    data["protocols"][protocol_key] = {
        "description": "MPPG 8H TIB",
        "dataset": f"mppg_ctl_8H_{subject}",
        "t_awake_l": {"repeat1": {"count": 11, "value": 960}},
        "t_sleep_l": {"repeat1": {"count": 11, "value": 480}},
        "title": "Control sample: 8 hr of normal sleep schedule. n=26#4 ",
        "blood_sample_time": [x + 4 for x in blood_sample_time],
    }

    tst_values = mppg_duffy["TST min RECALC"].dropna().tolist()
    sleep = {}
    awake = {}
    for i, value in enumerate(tst_values[0 : len(tst_values)], start=1):

        key = f"append{i}"
        if round(value) == 0:
            sleep[key] = [1]
        else:
            sleep[key] = [round(value)]

        if i == 1:
            awake[key] = [1500 - round(value)]
        elif i in [2, 4, 6]:
            awake[key] = [480 - round(value)]  # 24 hr protocols
        elif i in [3, 5]:
            awake[key] = [960 - round(value)]
        elif i == 7:
            awake[key] = [840 - round(value)]
        else:
            awake[key] = [1440 - round(value)]

    # Update the YAML structure
    data["protocols"][protocol_key]["t_awake_l"].update(awake)
    data["protocols"][protocol_key]["t_sleep_l"].update(sleep)


def update_protocol_yml_mppg_csr_5h(subject, data):
    """
    Update the protocol YAML file with the TST values for the MPPG CSR 5H TIB protocol.
    """
    mppg_duffy = pd.read_excel(
        "/Users/pujasaha/Desktop/SleepDebt/TST_data_from_Jean/"
        + "MPPG_P2_Individual_sleep_11-27-19_for_Puja_2024-12-12.xlsx",
        sheet_name=subject,
    )

    protocol_key = f"protocol_mppg_csr_5H_{subject}"

    blood_sample_time = [
        11.53,
        11.72,
        11.86,
        12.03,
        12.2,
        12.37,
        12.53,
        18.53,
        18.7,
        18.99,
        19.03,
        19.21,
        19.37,
        19.54,
        40.53,
        40.7,
        40.87,
        41.03,
        41.2,
        41.37,
        41.53,
    ]
    data["protocols"][protocol_key] = {
        "description": "MPPG 5H TIB",
        "dataset": f"mppg_csr_5H_{subject}",
        "t_awake_l": {"repeat1": {"count": 11, "value": 960}},
        "t_sleep_l": {"repeat1": {"count": 11, "value": 480}},
        "title": "Two days of 8 hr sleep/night, 21days of "
        + "5 hr sleep at night (Chronic Sleep Restriction). n=96#5 .",
        "blood_sample_time": [x + 4 for x in blood_sample_time],
    }

    tst_values = mppg_duffy["TST min RECALC"].dropna().tolist()
    print(len(tst_values))
    sleep = {}
    awake = {}
    for i, value in enumerate(tst_values[0 : len(tst_values)], start=1):
        # print(i, value)
        key = f"append{i}"
        if round(value) == 0:
            sleep[key] = [1]
        else:
            sleep[key] = [round(value)]

        if i == 1:
            awake[key] = [1500 - round(value)]
        elif i in [2, 4, 6]:
            awake[key] = [480 - round(value)]  # 24 hr protocols
        elif i in [3, 5]:
            awake[key] = [960 - round(value)]
        elif i == 7:
            awake[key] = [840 - round(value)]
        else:
            awake[key] = [1440 - round(value)]

    # Update the YAML structure
    data["protocols"][protocol_key]["t_awake_l"].update(awake)
    data["protocols"][protocol_key]["t_sleep_l"].update(sleep)


def update_protocol_yml_mppg_csr_56h(subject, data):
    """
    Update the protocol YAML file with the TST values
    for the MPPG CSR 5.6H TIB protocol.
    """

    protocol_key = f"protocol_mppg_csr_56H_{subject}"
    blood_sample_time = [
        11.6,
        11.76,
        11.93,
        12.1,
        12.28,
        12.43,
        12.59,
        18.59,
        18.93,
        19.1,
        19.26,
        19.43,
        40.59,
        40.76,
        40.93,
        41.1,
        41.26,
        41.43,
        41.59,
    ]
    data["protocols"][protocol_key] = {
        "description": "MPPG 56H TIB",
        "dataset": f"mppg_csr_56H_{subject}",
        "t_awake_l": {"repeat1": {"count": 11, "value": 960}},
        "t_sleep_l": {"repeat1": {"count": 11, "value": 480}},
        "title": "Two days of 10 hr sleep/night, 21days of "
        + "5.6 hr sleep at night (Chronic Sleep Restriction). n= 53#4",
        "blood_sample_time": [x + 4 for x in blood_sample_time],
    }

    sleep = {}
    awake = {}

    # for sample 3619, which has missing TST data.
    # Subject  was disempaneled from the study on Day 7,
    # so there are only baseline samples.
    if subject == "3619HY":
        for i in range(1, 8):
            key = f"append{i}"
            sleep[key] = [480]
            awake[key] = [960]
    else:
        mppg_duffy = pd.read_excel(
            "/Users/pujasaha/Desktop/SleepDebt/TST_data_from_Jean/"
            + "MPPG_P2_Individual_sleep_11-27-19_for_Puja_2024-12-12.xlsx",
            sheet_name=subject,
        )
        tst_values = mppg_duffy["TST min RECALC"].dropna().tolist()

        for i, value in enumerate(tst_values[0 : len(tst_values)], start=1):

            key = f"append{i}"
            if round(value) == 0:
                sleep[key] = [1]
            else:
                sleep[key] = [round(value)]

            if i == 1:
                awake[key] = [1500 - round(value)]
            elif i in [2, 4, 6]:
                awake[key] = [480 - round(value)]  # 24 hr protocols
            elif i in [3, 5]:
                awake[key] = [960 - round(value)]
            elif i == 7:
                awake[key] = [900 - round(value)]

            else:
                awake[key] = [1440 - round(value)]

    # Update the YAML structure
    data["protocols"][protocol_key]["t_awake_l"].update(awake)
    data["protocols"][protocol_key]["t_sleep_l"].update(sleep)


def update_protocol_yml_fd(subject, data):
    """
    Update the protocol YAML file with the TST values
    for the MPPG Forced Desynchrony protocol.
    """

    protocol_key = f"protocol_mppg_fd_{subject}"
    blood_sample_time = [
        11.53,
        11.74,
        11.86,
        12.03,
        12.2,
        12.36,
        12.53,
        19.49,
        19.66,
        19.82,
        20.01,
        20.16,
        20.32,
        20.49,
        20.66,
        36.01,
        36.17,
        36.35,
        36.5,
        36.67,
        36.84,
        37.01,
    ]
    data["protocols"][protocol_key] = {
        "description": "MPPG Forced Desynchrony protocol",
        "dataset": f"mppg_fd_{subject}",
        "t_awake_l": {"repeat1": {"count": 11, "value": 960}},
        "t_sleep_l": {"repeat1": {"count": 11, "value": 480}},
        "title": "Forced Desynchrony 11hr 40 min asleep and 16hr 20min awake.n=177#9",
        "blood_sample_time": [x + 4 for x in blood_sample_time],
    }

    sleep = {}
    awake = {}
    if subject == "3557HY61":
        for i in range(1, 8):
            key = f"append{i}"
            sleep[key] = [600]
            awake[key] = [840]
    else:
        mppg_duffy = pd.read_excel(
            "/Users/pujasaha/Desktop/SleepDebt/TST_data_from_Jean/"
            + "MPPG_P1_Sleep_Analysis_03-19-19_for_Puja_2024-11-21.xlsx",
            sheet_name=subject,
        )
        tst_values = mppg_duffy["Total Sleep Time (TST) mins RECALC"].dropna().tolist()

        for i, value in enumerate(tst_values[0 : len(tst_values)], start=1):

            key = f"append{i}"
            if round(value) == 0:
                sleep[key] = [1]
            else:
                sleep[key] = [round(value)]

            if i == 1:
                awake[key] = [1500 - round(value)]
            elif i in [2, 4, 6]:
                awake[key] = [480 - round(value)]  # 24 hr protocols
            elif i in [3, 5]:
                awake[key] = [960 - round(value)]
            elif i == 7:
                awake[key] = [840 - round(value)]
            else:
                awake[key] = [1680 - round(value)]
    # Update the YAML structure
    data["protocols"][protocol_key]["t_awake_l"].update(awake)
    data["protocols"][protocol_key]["t_sleep_l"].update(sleep)


if __name__ == "__main__":

    # mppg ctrl subject with 10 hr time in bed
    subjects_mppg_10h = ["3547HY", "3436HY", "3369HY42", "3552HY"]
    subjects_mppg_8h = ["3776HY", "3789HY", "3547HY82", "3812HY83"]
    subjects_mppg_5h = ["3794HY", "3776HY82", "3665HY82", "29W4HY83", "3828HY"]
    subjects_mppg_56h = ["3608HY", "3445HY", "3665HY", "3619HY"]  # 3619 is missing
    subjects_mppg_fd = [
        "3453HY73",
        "3557HY61",
        "2056HY75",
        "3552HY62",
        "26P2HY83",
        "3453HY52",
        "3536HY83",
        "3536HY52",
        "3552HY73",
    ]

    # load protocol.yml file
    box = get_box()
    existing_protocols = get_protocols(
        box, Path("archives/sleepdebt/yaml_files/protocols.yaml")
    )

    all_subjects_data: Dict[str, Dict[str, Any]] = {"protocols": {}}
    for sub in subjects_mppg_10h:
        print(sub)
        update_protocol_yml_mppg_ctl_10h(sub, all_subjects_data)

    for sub in subjects_mppg_8h:
        print(sub)
        update_protocol_yml_mppg_ctl_8h(sub, all_subjects_data)

    for sub in subjects_mppg_5h:
        print(sub)
        update_protocol_yml_mppg_csr_5h(sub, all_subjects_data)

    for sub in subjects_mppg_56h:
        print(sub)
        update_protocol_yml_mppg_csr_56h(sub, all_subjects_data)

    for sub in subjects_mppg_fd:
        print(sub)
        update_protocol_yml_fd(sub, all_subjects_data)

    # Merge the new protocols into the existing "protocols" key
    if "protocols" in existing_protocols:
        existing_protocols["protocols"].update(all_subjects_data["protocols"])
    else:
        existing_protocols["protocols"] = all_subjects_data["protocols"]

    # Save the updated protocol file
    save_to_yaml(
        box,
        existing_protocols,
        Path("archives/sleepdebt/yaml_files/updated_protocols.yaml"),
    )
