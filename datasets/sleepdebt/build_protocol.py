"""
this scripts use the "protocol.yaml" file and then update it to
"updated_protocol.yaml" to incorporate the Total Sleep Time (TST) information
for mppg protocols .

Note: The protocols  which exists in the protocol.yaml file will also
appear in the updated_protocol.yaml file, new protocols will be added at the end.
"""

import ast
from pathlib import Path
from typing import Any, Dict

import pandas as pd

from utils.get import get_box, get_protocols
from utils.save import save_to_yaml

BOX_PATH = {
    "blood_time": Path("archives/sleepdebt/dataset_with_sleepdebt_at_clocktime/"),
}


def update_protocol_yml_mppg_ctl_10h(
    subject: str, data: dict, blood_time: list
) -> None:
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
    if len(blood_time) == 1 and isinstance(blood_time[0], list):
        blood_time = blood_time[0]
    protocol_key = f"protocol_mppg_ctl_10H_{subject}"
    data["protocols"][protocol_key] = {
        "description": "MPPG 10H TIB",
        "dataset": f"mppg_ctl_10H_{subject}",
        "t_awake_l": {"repeat1": {"count": 11, "value": 960}},
        "t_sleep_l": {"repeat1": {"count": 11, "value": 480}},
        "title": f"Control sample: 10 hr of normal sleep schedule.n=(28#4).{subject} ",
        "blood_sample_time": blood_time,
    }

    tst_values = mppg_duffy["Total Sleep Time (TST) mins"].tolist()
    sleep = {}
    awake = {}
    for i, value in enumerate(tst_values[0 : len(tst_values)], start=1):

        key = f"append{i}"
        # if round(value) == 0:
        #     sleep[key] = [1]
        # else:
        sleep[key] = [round(value)]

        awake[key] = [1440 - round(value)]

    # Update the YAML structure
    data["protocols"][protocol_key]["t_awake_l"].update(awake)
    data["protocols"][protocol_key]["t_sleep_l"].update(sleep)


def update_protocol_yml_mppg_ctl_8h(subject: str, data: dict, blood_time: list) -> None:
    """
    Update the protocol YAML file with the TST
    values for the MPPG control 8H TIB protocol.
    """
    mppg_duffy = pd.read_excel(
        "/Users/pujasaha/Desktop/SleepDebt/TST_data_from_Jean/"
        + "MPPG_HF_CTRL_individual_sleep_10-30-19_for_Puja_2024-12-12.xlsx",
        sheet_name=subject,
    )

    if len(blood_time) == 1 and isinstance(blood_time[0], list):
        blood_time = blood_time[0]

    protocol_key = f"protocol_mppg_ctl_8H_{subject}"
    data["protocols"][protocol_key] = {
        "description": "MPPG 8H TIB",
        "dataset": f"mppg_ctl_8H_{subject}",
        "t_awake_l": {"repeat1": {"count": 11, "value": 960}},
        "t_sleep_l": {"repeat1": {"count": 11, "value": 480}},
        "title": f"Control sample: 8 hr of normal sleep schedule. n=(21#3).{subject} ",
        "blood_sample_time": blood_time,
    }

    tst_values = mppg_duffy["TST min RECALC"].dropna().tolist()
    sleep = {}
    awake = {}
    for i, value in enumerate(tst_values[7 : len(tst_values)], start=1):

        key = f"append{i}"
        # if round(value) == 0:
        #     sleep[key] = [1]
        # else:
        sleep[key] = [round(value)]
        """
        if i == 1:
            awake[key] = [1500 - round(value)]
        elif i in [2, 4, 6]:
            awake[key] = [480 - round(value)]  # 24 hr protocols
        elif i in [3, 5]:
            awake[key] = [960 - round(value)]
        elif i == 7:
            awake[key] = [840 - round(value)]
        else:
        """
        awake[key] = [1440 - round(value)]

    # Update the YAML structure
    data["protocols"][protocol_key]["t_awake_l"].update(awake)
    data["protocols"][protocol_key]["t_sleep_l"].update(sleep)


def update_protocol_yml_mppg_csr_5h(subject, data, blood_time):
    """
    Update the protocol YAML file with the TST values for the MPPG CSR 5H TIB protocol.
    """
    mppg_duffy = pd.read_excel(
        "/Users/pujasaha/Desktop/SleepDebt/TST_data_from_Jean/"
        + "MPPG_P2_Individual_sleep_11-27-19_for_Puja_2024-12-12.xlsx",
        sheet_name=subject,
    )
    if len(blood_time) == 1 and isinstance(blood_time[0], list):
        blood_time = blood_time[0]
    protocol_key = f"protocol_mppg_csr_5H_{subject}"

    data["protocols"][protocol_key] = {
        "description": "MPPG 5H TIB",
        "dataset": f"mppg_csr_5H_{subject}",
        "t_awake_l": {"repeat1": {"count": 11, "value": 960}},
        "t_sleep_l": {"repeat1": {"count": 11, "value": 480}},
        "title": "Two days of 8 hr sleep/night, 21days of "
        + f"5 hr sleep at night (Chronic Sleep Restriction). n=(97#5).{subject}.",
        "blood_sample_time": blood_time,
    }

    tst_values = mppg_duffy["TST min RECALC"].dropna().tolist()
    print(len(tst_values))
    sleep = {}
    awake = {}
    for i, value in enumerate(tst_values[7 : len(tst_values)], start=1):
        # print(i, value)
        key = f"append{i}"
        # if round(value) == 0:
        #     sleep[key] = [1]
        # else:
        sleep[key] = [round(value)]
        """
        if i == 1:
            awake[key] = [1500 - round(value)]
        elif i in [2, 4, 6]:
            awake[key] = [480 - round(value)]  # 24 hr protocols
        elif i in [3, 5]:
            awake[key] = [960 - round(value)]
        elif i == 7:
            awake[key] = [840 - round(value)]
        else:
        """
        awake[key] = [1440 - round(value)]

    # Update the YAML structure
    data["protocols"][protocol_key]["t_awake_l"].update(awake)
    data["protocols"][protocol_key]["t_sleep_l"].update(sleep)


def update_protocol_yml_mppg_csr_56h(subject, data, blood_time):
    """
    Update the protocol YAML file with the TST values
    for the MPPG CSR 5.6H TIB protocol.
    """
    if len(blood_time) == 1 and isinstance(blood_time[0], list):
        blood_time = blood_time[0]
    protocol_key = f"protocol_mppg_csr_56H_{subject}"

    data["protocols"][protocol_key] = {
        "description": "MPPG 56H TIB",
        "dataset": f"mppg_csr_56H_{subject}",
        "t_awake_l": {"repeat1": {"count": 11, "value": 960}},
        "t_sleep_l": {"repeat1": {"count": 11, "value": 480}},
        "title": f"Two days of 10 hr sleep/night, 21days of "
        + "5.6 hr sleep at night (Chronic Sleep Restriction). n=(54#4).{subject}.",
        "blood_sample_time": blood_time,
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

        for i, value in enumerate(tst_values[7 : len(tst_values)], start=1):

            key = f"append{i}"
            # if round(value) == 0:
            #     sleep[key] = [1]
            # else:
            sleep[key] = [round(value)]
            """
            if i == 1:
                awake[key] = [1500 - round(value)]
            elif i in [2, 4, 6]:
                awake[key] = [480 - round(value)]  # 24 hr protocols
            elif i in [3, 5]:
                awake[key] = [960 - round(value)]
            elif i == 7:
                awake[key] = [900 - round(value)]

            else:
            """
            awake[key] = [1440 - round(value)]

    # Update the YAML structure
    data["protocols"][protocol_key]["t_awake_l"].update(awake)
    data["protocols"][protocol_key]["t_sleep_l"].update(sleep)


def update_protocol_yml_fd(subject, data, blood_time, sp, cycle):
    """
    Update the protocol YAML file with the TST values
    for the MPPG Forced Desynchrony protocol.

    Note: 26P2HY83 and 3536HY83 subjects SP  ends  at 27 that is sooner than the other subjects. We have
    proteomics are available after SP27 for this two subjects. So using actual TIB
    for these two subjects.
    "3557HY61" subject left after the baseline study.
    """
    # making  "blood_time" a flat list
    if len(blood_time) == 1 and isinstance(blood_time[0], list):
        blood_time = blood_time[0]

    protocol_key = f"protocol_mppg_fd_{subject}"
    data["protocols"][protocol_key] = {
        "description": "MPPG Forced Desynchrony protocol",
        "dataset": f"mppg_fd_{subject}",
        "t_awake_l": {"repeat1": {"count": 11, "value": 960}},
        "t_sleep_l": {"repeat1": {"count": 11, "value": 480}},
        "title": f"Forced Desynchrony 11hr 40 min asleep and 16hr 20min awake.n=(172#9).{subject}",
        "blood_sample_time": blood_time,  # [x + 4 for x in blood_sample_time],
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

        # for subject 26P2HY83 and 3536HY83, the TST values are available until SP27. TST for rest of the
        # days are estimated from a Linear Mixed Model (LMM) using the TST data from the rest of the data.
        if subject == "26P2HY83":

            SP_28_36 = [429.1, 433.4, 437.8, 442.2, 446.5, 450.9, 455.3, 459.7, 464.0]
            tst_values = tst_values + SP_28_36

        if subject == "3536HY83":

            SP_28_36 = [479.4, 483.8, 488.2, 492.5, 496.9, 501.3, 505.6, 510.0, 514.4]
            tst_values = tst_values + SP_28_36

        for i, value in enumerate(tst_values[sp : len(tst_values)], start=1):

            key = f"append{i}"
            # if round(value) == 0:
            #     sleep[key] = [1]
            # else:
            sleep[key] = [round(value)]
            """
            if i == 1:
                awake[key] = [1500 - round(value)]
            elif i in [2, 4, 6]:
                awake[key] = [480 - round(value)]  # 24 hr protocols
            elif i in [3, 5]:
                awake[key] = [960 - round(value)]
            """
            if i in [1, 2] or i > 21:
                awake[key] = [1440 - round(value)]

            elif i == 21:
                awake[key] = [cycle - round(value)]

            else:
                awake[key] = [1680 - round(value)]

    # Update the YAML structure
    data["protocols"][protocol_key]["t_awake_l"].update(awake)
    data["protocols"][protocol_key]["t_sleep_l"].update(sleep)


def subject_bloodtime(df_blood, subject, protocol):
    """
    Get the blood collection time for a specific subject."""

    bloodtime_per_subject = df_blood[df_blood["study"] == protocol]["blood_time"].apply(
        lambda x: x.get(subject, None)
    )
    bloodtime_per_subject = bloodtime_per_subject.to_list()
    return bloodtime_per_subject


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
    sub_cycle = {
        "3453HY73": 2123,
        "3453HY52": 1833,
        "3557HY61": 1805,
        "2056HY75": 2093,
        "26P2HY83": 2158,
        "3552HY62": 1532,
        "3536HY83": 1667,
        "3536HY52": 1440,
        "3552HY73": 1629,
    }

    # load protocol.yml file
    box = get_box()
    existing_protocols = get_protocols(
        box, Path("archives/sleepdebt/yaml_files/protocols.yaml")
    )
    blood_time_file = box.get_file(
        BOX_PATH["blood_time"] / "count_121124_AS_2025-03-18_PS.csv"
    )

    blood_collection = pd.read_csv(
        blood_time_file, converters={"blood_time": ast.literal_eval}
    )

    all_subjects_data: Dict[str, Dict[str, Any]] = {"protocols": {}}
    for sub in subjects_mppg_10h:
        print(sub)
        bloodtime = subject_bloodtime(blood_collection, sub, "mppg_10h")

        update_protocol_yml_mppg_ctl_10h(sub, all_subjects_data, bloodtime)

    for sub in subjects_mppg_8h:
        print(sub)
        bloodtime = subject_bloodtime(blood_collection, sub, "mppg_8h")

        update_protocol_yml_mppg_ctl_8h(sub, all_subjects_data, bloodtime)

    for sub in subjects_mppg_5h:
        print(sub)
        bloodtime = subject_bloodtime(blood_collection, sub, "mppg_5h")
        update_protocol_yml_mppg_csr_5h(sub, all_subjects_data, bloodtime)

    for sub in subjects_mppg_56h:
        print(sub)
        bloodtime = subject_bloodtime(blood_collection, sub, "mppg_56h")
        update_protocol_yml_mppg_csr_56h(sub, all_subjects_data, bloodtime)

    for sub in subjects_mppg_fd:
        print(sub)
        SLEEP_PERIOD = 7  # 1 or 7
        bloodtime = subject_bloodtime(blood_collection, sub, "mppg_fd")
        update_protocol_yml_fd(
            sub,
            all_subjects_data,
            bloodtime,
            SLEEP_PERIOD,
            sub_cycle[sub],
        )

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
