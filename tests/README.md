## How to run test scripts

**NOTE**: you have to be in `proteomics' directory, to run the following scripts, otherwise it will not be able to access box token and other dependencies.

This folder has tests scripts that corresponds to different scripts in `datasets` folder.

`test_model_adenosine.py` tests the functions in `datasets/sleepdebt/adenosine_model/model.py`.

To run :

```shell
pytest tests/test_model_adenosine.py
```

`test_model_unified.py` tests the functions in `datasets/sleepdebt/unified_model/sleepdebt_calculation.py`.
Please note there are some common functions in `adenosine_model/model.py` and `unified_model/sleepdebt_calculation.py`, so the common functions are only tested in `tests/test_model_adenosine.py`.

To run :

```shell
pytest tests/test_model_unified.py
```

`test_study.py` corresponds to the scripts `\*\_study.py` in `datasets/proteomics_sleepdebt` folder. All of these scripts are written in same format so only one is tested. For more detail, please look at the documentation inside `test_study.py` and `day5_study.py`.

To run:

```shell
pytest tests/test_study.py
```

Remember, test scripts can not access input from BOX, so there are two toy inputs inside the `tests/adenosine` and `tests/unified`.
