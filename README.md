# Proteomics 🩸

[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/release/python-312/)
![GitHub Actions](https://github.com/AdrienSpecht/proteomics/actions/workflows/build.yml/badge.svg)
![Coverage](https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/AdrienSpecht/bfba49c1003e973932c4de7dcc3e969a/raw/proteomics_feature_setup.txt)

This repository documents the project and saves scripts for data construction and data analysis.

## ⚙️ Installation

Clone the repository:

```shell
git clone https://github.com/AdrienSpecht/proteomics
```

Run setup.sh:

```shell
cd proteomics
./setup.sh
```

The `setup.sh` script automates the initial configuration of your development environment to ensure consistency and efficiency. It installs essential tools such as pyenv for Python version management and VSCode extensions to streamline your coding workflow:

-   isort: Automatically sorts Python imports.
-   pylint: Linter for code errors and standards.
-   mypy: Static type checker.
-   pylance: Language support for Python.
-   black: Code formatter adhering to [PEP 8](https://pep8.org/).
-   shell-format: Formatter for shell scripts.

The script also creates a virtual environment from the `requirements.txt`, sets up configuration files for VSCode and GitHub Actions, and configures your Python path. This ensures that everyone has a consistent workspace, reducing setup time, review time, and facilitating smoother collaboration.
