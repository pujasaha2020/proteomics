## Sleepdebt extraction

To prepare the dataset for sleepdebt analysis
hat sleep debt at blood collection time when proteomics data is also available.

```shell
python run_analysis.py
```

All the files in this folder which ends with "\_study.py" are specific to different protocols.
Each of them structure the data and then apply the sleep debt at the time when proteomics data is available.

The main script "run_analysis.py" does the follwoing jobs:

- It removes the rows which do not have any proteins and pass them to each "\*\_study.py".
- it also pass the full dataset to "zeitzer_study.py" to get sleep wake schedule. It is explained at the top of "run_analysis.py".
- get the dataframe from each protocol("\*\_study.py") and concatenate them together. Also it produces result from both models , unified and adenosine.
- the final output dataframe from this script will have : "ids", "infos", "profile" , "adenosine", "unified". Note: no proteomics here.
- the dataset is named as "{input*version}\_with_sleep_debt*{date_of_generation}\_PS.csv". The file will be saved to box at:
  "archives/sleep_debt/SleepDebt_Data/dataset_with_sleepdebt_at_clocktime/".
