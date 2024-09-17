## calculate Sleepdebt

Scripts in this folder, calculate sleepdebt at every minute from two different models: adenosine and unified.

To run adenosine model:

```shell
python sleepdebt/adenosine_model/model.py
```

In `adenosine_model`:

- `parameters.yaml`: have parameters needed to run the model. Scripts read this yaml file directly from box.
- `protocols.yaml`: have protocols from all studies. Scripts read this yaml file directly from box.
- `plotting.py`: this scripts do the plotting of sleepdebt curve, indicates the time when the blood is collected.
- `model.py`: this is the main script to run the model and get the sleepdebt.

To run unified model:

```shell
python sleepdebt/unified_model/sleepdebt_calculation.py
```

In `unified_model`:

- `parameters.yaml`: have parameters needed to run the model. Scripts read this yaml file directly from box.
- `protocols.yaml`: have protocols from all studies. Scripts read this yaml file directly from box. Same as in `adenosine_model`.
- `plotting.py`: this scripts do the plotting of sleepdebt curve, indicates the time when the blood is collected.
- `model.py`: this scripts includes the solution to differential equations.
- `sleepdebt_calculation.py`: this is the main script to run the model and get the sleepdebt.

TODO: there are many functions which are common in both folders. Those will be eventually be moved to a common place.
