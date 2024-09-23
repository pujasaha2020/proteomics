## Prepare sleepdebt dataset for Biomarker and prediction analysis

If you have generated the sleep debt at every minute from both models in `datasets/sleepdebt`, now you are ready to prepare final dataset for biomarker analysis and prediction model. This final dataset includes debt only at specific time when blood was collected or proteomics are available.

**IMPORTANT**: This process below give you a dataset without the "proteins" columns. You need to merge that later.

This scripts structures the data and extract sleep debt at blood collection time when proteomics data is also available.

```shell
python run_analysis.py
```

All the files in this folder which ends with `\*\_study.py` are specific to different protocols.
Each of them structure the data and then apply the sleep debt at the time when proteomics data is available.

The main script "run_analysis.py" does the following jobs:

- It removes the rows which do not have any proteins and pass them to each `\*\_study.py`. It only filters the columns : "ids", "infos", "profile".
- It also pass the full dataset to `zeitzer_study.py` to get sleep wake schedule. It is explained at the top of "run_analysis.py".
- Get the dataframe from each protocol(`\*\_study.py`) and concatenate them together. Also it produces result from both models , unified and adenosine.
- The final output dataframe from this script will have : "ids", "infos", "profile" , "adenosine", "unified". **Note**: no proteomics here.
- The dataset is named as `{input*version}\_with_sleep_debt*{date_of_generation}\_PS.csv`. The file will be saved to box at:
  `archives/sleep_debt/SleepDebt_Data/dataset_with_sleepdebt_at_clocktime/`.

## How sleepdebt is extracted at specific time

To understand how the sleepdebt at specific time is extracted for each protocol, please read the documentation in `day5_study.py`. Pretty much same format is followed for other studies.

**IMPORTANT**: once you run "run_analysis.py" on new/updated dataset,
gets the number of subjects and samples in each study from get_no_of_subjects_samples().
Then update that in box `protocol.yaml` --> `title` line. No need to update `protocol.yaml`
in github. The code always reads it from box directly.

For question, comments and bug please contact Puja Saha @ puja2023@stanford.edu .
