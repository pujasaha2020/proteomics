## How to run test scripts

**NOTE**: you have to be in `proteomics' directory, to run the following scripts, otherwise it will not be able to access box token and other dependencies.

This folder has tests scripts that corresponds to different scripts in other folders.

To run all the test scripts with a single command line:

```shell
  pytest tests
```

If you want to run any specific scripts explicitly:

```shell
  pytest <test_script_name>
```

Here is the link to pytest documentation: https://docs.pytest.org/en/7.1.x/contents.html
