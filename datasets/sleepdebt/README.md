## Calculate sleep debt at every minute

**Read before you move forward**

Adenosine Model:https://journals.plos.org/ploscompbiol/article/file?id=10.1371/journal.pcbi.1005759&type=printable

Unified Model: https://www.sciencedirect.com/science/article/pii/S0022519313001811

**First step in sleep deprivation analysis**

**NOTE**: you have to be in `proteomics' directory, to run the following scripts, otherwise it will not be able to access box token and other dependencies.

Scripts in this folder, calculate sleepdebt at every minute from two different models: adenosine and unified.

To run adenosine model:

```shell
python datasets/sleepdebt/adenosine_model/model.py
```

In `adenosine_model`:

- `parameters.yaml`: have parameters needed to run the model. Scripts read this yaml file directly from box.
- `protocols.yaml`: have protocols from all studies. Scripts read this yaml file directly from box.
- `plotting.py`: this scripts do the plotting of sleepdebt curve, indicates the time when the blood is collected.
- `model.py`: this is the main script to run the model and get the sleepdebt.

**What to expect from `model.py'**

- The output of the models are stored in box.
- All the csv files containing sleep debt at every minute are stored in
  `archives/sleep_debt/SleepDebt_Data/ligand_receptor_model/sleepdebt/`
- All the plots of sleep debt curves are stored in
  `"results/sleep_debt/sleepDebt_curves/ligand_receptor_model/`

To run unified model:

```shell
python datasets/sleepdebt/unified_model/sleepdebt_calculation.py
```

In `unified_model`:

- `protocols.yaml`: have protocols from all studies. Scripts read this yaml file directly from box. Same as in `adenosine_model`.
- `plotting.py`: this scripts do the plotting of sleepdebt curve, indicates the time when the blood is collected.
- `model.py`: this scripts includes the solution to differential equations.
- `sleepdebt_calculation.py`: this is the main script to run the model and get the sleepdebt.

**What to expect from `sleepdebt_calculation.py'**

- The output of the models are stored in box.
- All the csv files containing sleep debt at every minute are stored in
  `archives/sleep_debt/SleepDebt_Data/unified_model/sleepdebt/`
- All the plots of sleep debt curves are stored in
  `results/sleep_debt/sleepDebt_curves/unified_model/`

**TODO**: there are many functions which are common in both folders. Those will be eventually be moved to a common place.

For question, comments and bug please contact Puja Saha @ puja2023@stanford.edu .
