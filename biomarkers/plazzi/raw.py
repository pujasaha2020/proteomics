from pathlib import Path

import numpy as np
import pandas as pd
import somadata
from tqdm import tqdm

from utils.get import get_box

MY_ROOT = "/Users/adrienspecht"

import sys

sys.path.append(MY_ROOT + "/mignot_lab/adrien/Codes")


def get_adat_id(path):
    """Get the sample ids from the ad"""
    adat = somadata.read_adat(path)
    samples = adat.pick_on_meta(axis=0, name="SampleType", values=["Sample"])
    sample_ids = samples.index.get_level_values("SampleId").astype(str)
    return sample_ids


################################################################
#  OPEN RAW DATA
################################################################
box = get_box()
file = box.get_file(
    Path(
        "doc/mignot/jing/SomaScan SS-2453470 (362 EDTA plasma) sample info final to Adrien Hyatt 06132024.xlsx"
    )
)

context = pd.read_excel(file)
ethnicity_map = {
    "caucasian": "white",
    "Caucasian": "white",
    "caucasican": "white",
    "Mixed": "hispanic",
    "caucasic": "white",
    "asian": "asian",
    "African": "black",
    "Latino": "hispanic",
    "Other": "hispanic",
    "Black": "black",
    np.nan: np.nan,
}
context["race"] = context["Self-Identified Race"].apply(lambda x: ethnicity_map[x])
context["DbID"] = context["DbID"].astype(str)
context["sample_id"] = context["Tube Unique ID/2D Barcode (First Replicate)"].astype(
    str
)
cd_vanda = context["Referrer"] == "Sandra Smieszek (Vandapharma)"
context.loc[cd_vanda, "sample_id"] = context[cd_vanda]["sample_id"].apply(
    lambda x: x.split(" ")[1]
)
context["sample_id"] = context["sample_id"].apply(lambda x: x.replace(" ", ""))
modification = {
    "DbID13373": "13373",
    "DbID4961": "4961",
    "DbID18252": "18252",
    "DbID18369": "18369",
    "DbID18658": "18658",
    "DbID18665": "18665",
    "DbID18889": "18889",
    "DbID18894": "18894",
    "DbID18976": "18976",
    "DbID18988": "18988",
    "DbID19667": "19667",
    "DbID19678": "19678",
    "DbID19681": "19681",
    "DbID19708": "19708",
    "DbID20133": "20133",
    "DbID21282": "22_12380",
}
context["sample_id"] = context["sample_id"].replace(modification)
file = box.get_file(
    Path(
        "doc/mignot/jing/SS-2343561 SS-2453470 Europe 30 EDTA plasma Blood time final to Adrien 09112024.xlsx"
    )
)
context1 = pd.read_excel(file)


context1.rename(
    columns={"barcode ID": "sample_id", "Blood draw time": "time"}, inplace=True
)
context1 = context1[["sample_id", "time"]].set_index("sample_id")
context.set_index("sample_id", inplace=True)
context["time"] = context1["time"]
context.reset_index(inplace=True)
context.rename(
    columns={
        "Age": "age",
        "DbID": "subject_id",
        "Gender": "sex",
        "Dx (1)": "dr_x",
        "Dx Ling": "dr_y",
        "CSF Hcrt concentration crude (1)": "hypocretin",
        "Self-Identified Race": "ethnicity",
    },
    inplace=True,
)
context["subject_id"] = context["subject_id"].astype(str)
context.replace(".", np.nan, inplace=True)

# Group dr's annotations into ["IH", "NT1", "NT2", "ctl"]
mapping = {
    # Dr. X's terms
    "I": "NT2",
    "K": "ctl",
    "IH": "IH",
    "IH ": "IH",
    "EDS": "sEDS",
    "NT2": "NT2",
    "A-F": "NT1",
    "A": "NT1",
    "M": "IH",
    "CTRL": "ctl",
    "NT1": "NT1",
    "non-definitive": "NT2",
    "HI": "IH",
    "ctrl": "ctl",
    "IH,nocturnal myoclonus": "IH",
    "Hypersomnia": "IH",
    "ctrl hla negativo": "ctl",
    "non NT1 (IH) from L": "IH",
    "non NT1 (NT2) from I+L": "NT2",
    "non NT1 (sEDS) from M": "sEDS",
    "non NT1 (sEDS) from E2": "sEDS",
    "sEDS": "sEDS",
    "sEDS in Jouvanile PD": "sEDS",
    "sEDS (borderline MSLT SL, may be also used as IH)": "sEDS",
    "sEDS, MIL OAS": "sEDS",
    "A-F+Schizophrenia": "NT1",
    "CTRL BIMBO": "ctl",
    "CTRL psychosis ": "ctl",
    "CTRL for RBD": "ctl",
    "suspect Narcolepsy": "NT1",
    "NT1 con osas di grado severo": "NT1",
    "sospetta NT1": "NT1",
    "NT1 e SHE": "NT1",
    "DSWPD": "DSWPD",
    " DSWPD": "DSWPD",
    # Dr. Y's terms match
    "control": "ctl",
    "NT2 (familial)": "NT2",
}
context["dr_x_simple"] = context["dr_x"].replace(mapping)
context["dr_y_simple"] = context["dr_y"].replace(mapping)
context["dr"] = context["dr_y_simple"].combine_first(context["dr_x_simple"])
assert context.dr.notna().all()
# cd_conflict = (context["dr_x_simple"] != context["dr_y_simple"])
# cd_no_nan = context["dr_x_simple"].notna() & context["dr_y_simple"].notna()
cd_vanda = context["Referrer"] == "Sandra Smieszek (Vandapharma)"
# cd_nt1 =((context["dr_x_simple"] == "NT1") | (context["dr_y_simple"] == "NT1")) & (context["hypocretin"] < 200)
# context.loc[cd_conflict & cd_no_nan & ~cd_vanda & cd_nt1, 'dr'] = "NT1"
context["study_id"] = context["dr"].apply(lambda x: f"plazzi_{x.lower()}")
context.loc[cd_vanda, "study_id"] = "vanda"
context["fluid"] = "edta"
context["processing_duration"] = 0
context["experiment_id"] = context["subject_id"]
context[
    ["melatonin", "clock_time", "dlmo_phase", "mid_sleep", "cortisol_peak", "bmi"]
] = np.nan
context.loc[cd_vanda, "clock_time"] = pd.to_datetime("2022-01-01") + pd.to_timedelta(
    context[cd_vanda].time.astype(str) + ":00"
)
context.loc[~cd_vanda, "clock_time"] = pd.to_datetime("2022-01-01") + pd.to_timedelta(
    "9:30:00"
)
context.reset_index(inplace=True)
subject_ids = context["subject_id"].unique()

PATH_TO_PROTEINS = Path(
    "raw_data/proteins/SS-2453470/SS-2453470_v4.1_EDTAPlasma.hybNorm.medNormInt.plateScale.calibrate.anmlQC.qcCheck.anmlSMP.adat"
)
file = box.get_file(PATH_TO_PROTEINS)

adat_ids = get_adat_id(file)
MATCHING_COLUMNS = [
    "study_id",
    "subject_id",
    "experiment_id",
    "sample_id",
    "sex",
    "age",
    "bmi",
    "race",
    "fluid",
    "processing_duration",
    "mid_sleep",
    "cortisol_peak",
    "clock_time",
    "melatonin",
    "dlmo_phase",
    "proteins",
]

################################################################
#  FUNCTIONS
################################################################


def extract_info2(code):
    """Extract MATCHING_COLUMNS for code."""

    df = context[context.subject_id == code]
    df.reset_index(inplace=True)

    # Proteins column indicates if we have the proteins or not
    df["proteins"] = df["sample_id"].isin(adat_ids)
    df = df[MATCHING_COLUMNS]
    return [df]


def build_all():
    profiles = []
    for ids in tqdm(subject_ids):
        profiles.extend(extract_info2(ids))
    all_data = pd.concat(profiles)
    return all_data


################################################################
#  MAIN
################################################################

if __name__ == "__main__":
    full = build_all()
    print(full.to_string())
