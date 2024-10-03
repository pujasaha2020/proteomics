## Welcome to Sleep Deprivation Analysis!!

## Step 1: Calculate sleep debt at every minute

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

**What to expect from `create_debt.py' (adenosine model)**

- The output of the models are stored in box.
- All the csv files containing sleep debt at every minute are stored in
  `archives/sleepdebt/sleepdebt_data/ligand_receptor_model/sleepdebt/`
- All the plots of sleep debt curves are stored in
  `results/sleepdebt/sleepdebt_curves/ligand_receptor_model/`

To run unified model:

```shell
python datasets/sleepdebt/create_debt.py --model "adenosine" --definition "def_2"
```

Currently we are using "def_2", change it depending on what you need. Three definitions exists.

**What to expect from `sleepdebt_calculation.py' (unified model)**

- The output of the models are stored in box.
- All the csv files containing sleep debt at every minute are stored in
  `archives/sleepdebt/sleepdebt_data/unified_model/sleepdebt/`
- All the plots of sleep debt curves are stored in
  `results/sleepdebt/sleepDebt_curves/unified_model/`

## Step 2: Prepare sleepdebt dataset for Biomarker and prediction analysis

If you have generated the sleep debt at every minute from both models above, now you are ready to prepare final dataset for biomarker analysis and prediction model. This final dataset includes debt only at specific time when blood was collected or proteomics are available.

**IMPORTANT**: This process below give you a dataset without the "proteins" columns. You need to merge that later.

**NOTE**: you have to be in `proteomics' directory, to run the following scripts, otherwise it will not be able to access box token and other dependencies.

```shell
python datasets/sleepdebt/extract_debt.py
```

All the files in this folder which ends with `dataset/sleepdebt/studies/\*\_study.py` are specific to different protocols.
Each of them structure the data and then apply the sleep debt at the time when proteomics data is available.

**What to expect from `extract_debt.py'**

- The final output dataframe from this script will have : "ids", "infos", "profile" , "adenosine", "unified". **Note**: no proteomics here.
- The dataset is named as `data_{input_version}_with_sleep_debt_{date_of_generation}_PS.csv`. The file will be saved to box at:
  `archives/sleepdebt/sleepdebt_data/dataset_with_sleepdebt_at_clocktime/`.
- This scripts also create a file that contains, count of subjects and samples, blood times of the subject with the maximum number of samples.  
  this file (`count_{input_version}_{date_of_generation}_PS.csv`) is also saved: `archives/sleepdebt/sleepdebt_data/dataset_with_sleepdebt_at_clocktime/`

**IMPORTANT**: once you run `extract_debt.py` on new/updated dataset,
gets the number of subjects and samples in each study from `count_{input*version}_{date_of_generation}_PS.csv`.
Then update that in box `protocol.yaml`-->`title` line.

## How sleepdebt is extracted at specific time

To understand how the sleepdebt at specific time is extracted for each protocol, please read the documentation in `day5_study.py`. Pretty much same format is followed for other studies.

For question, comments and bug please contact Puja Saha @ puja2023@stanford.edu .
