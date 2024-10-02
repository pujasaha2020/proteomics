## Calculate sleep debt at every minute

**Read before you move forward**

Adenosine Model:https://journals.plos.org/ploscompbiol/article/file?id=10.1371/journal.pcbi.1005759&type=printable

Unified Model: https://www.sciencedirect.com/science/article/pii/S0022519313001811

**First step in sleep deprivation analysis**

**NOTE**: you have to be in `proteomics' directory, to run the following scripts, otherwise it will not be able to access box token and other dependencies.

Scripts in this folder, calculate sleepdebt at every minute from two different models: adenosine and unified.

To run adenosine model:

```shell
python datasets/sleepdebt/create_debt.py --model "adenosine"
```

No need to provide "--definition" for adenosine model.

**What to expect from `create.py' (adenosine model)**

- The output of the models are stored in box.
- All the csv files containing sleep debt at every minute are stored in
  `archives/sleep_debt/SleepDebt_Data/ligand_receptor_model/sleepdebt/`
- All the plots of sleep debt curves are stored in
  `"results/sleep_debt/sleepDebt_curves/ligand_receptor_model/`

To run unified model:

```shell
python datasets/sleepdebt/create_debt.py --model "adenosine" --definition "def_2"
```

Currently we are using "def_2", change it depending on what you need. Three definitions exists.

**What to expect from `sleepdebt_calculation.py' (unified model)**

- The output of the models are stored in box.
- All the csv files containing sleep debt at every minute are stored in
  `archives/sleep_debt/SleepDebt_Data/unified_model/sleepdebt/`
- All the plots of sleep debt curves are stored in
  `results/sleep_debt/sleepDebt_curves/unified_model/`

## Prepare sleepdebt dataset for Biomarker and prediction analysis

If you have generated the sleep debt at every minute from both models above, now you are ready to prepare final dataset for biomarker analysis and prediction model. This final dataset includes debt only at specific time when blood was collected or proteomics are available.

**IMPORTANT**: This process below give you a dataset without the "proteins" columns. You need to merge that later.

This scripts structures the data and extract sleep debt at blood collection time when proteomics data is also available.

**NOTE**: you have to be in `proteomics' directory, to run the following scripts, otherwise it will not be able to access box token and other dependencies.

```shell
python datasets/sleepdebt/extract_debt.py
```

All the files in this folder which ends with `dataset/sleepdebt/studies/\*\_study.py` are specific to different protocols.
Each of them structure the data and then apply the sleep debt at the time when proteomics data is available.

**What to expect from `extract_debt.py'**

- The final output dataframe from this script will have : "ids", "infos", "profile" , "adenosine", "unified". **Note**: no proteomics here.
- The dataset is named as `data_{input_version}_with_sleep_debt_{date_of_generation}_PS.csv`. The file will be saved to box at:
  `archives/sleep_debt/SleepDebt_Data/dataset_with_sleepdebt_at_clocktime/`.
- This scripts also create a file that contains, count of subjects and samples, blood times of the subject with the maximum number of samples.  
  this file (`count_{input_version}_{date_of_generation}_PS.csv`) is also saved: `archives/sleep_debt/SleepDebt_Data/dataset_with_sleepdebt_at_clocktime/`

## How sleepdebt is extracted at specific time

To understand how the sleepdebt at specific time is extracted for each protocol, please read the documentation in `day5_study.py`. Pretty much same format is followed for other studies.

**IMPORTANT**: once you run `extract_debt.py` on new/updated dataset,
gets the number of subjects and samples in each study from `count*{input*version}*{date_of_generation}\_PS.csv`.
Then update that in box `protocol.yaml`-->`title` line.

For question, comments and bug please contact Puja Saha @ puja2023@stanford.edu .
