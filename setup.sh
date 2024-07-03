#!/bin/bash
echo "Welcome to setup! :)"
echo "==================="

#######################################################
# Function to check if a command exists
command_exists() {
    command -v "$1" &>/dev/null
}

#######################################################
# Function to install pyenv
install_pyenv() {
    if ! command_exists pyenv; then
        echo "Installing pyenv..."
        curl https://pyenv.run | bash
    fi

    # Add pyenv to bashrc/zshrc
    local pyenv_config='
export PYENV_ROOT="$HOME/.pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init --path)"
eval "$(pyenv init -)"
'

    if [[ "$SHELL" == */zsh ]]; then
        echo "$pyenv_config" >>"$HOME/.zshrc"
        source "$HOME/.zshrc"
    elif [[ "$SHELL" == */bash ]]; then
        echo "$pyenv_config" >>"$HOME/.bashrc"
        source "$HOME/.bashrc"
    else
        echo "Unsupported shell. Please add pyenv to your shell configuration manually."
    fi

}

#######################################################
# Function to install VSCode extensions
install_vscode_extensions() {
    code --install-extension ms-python.python
    code --install-extension ms-python.isort
    code --install-extension ms-python.pylint
    code --install-extension ms-python.vscode-mypy
    code --install-extension ms-python.vscode-pylance
    code --install-extension streetsidesoftware.code-spell-checker
    code --install-extension ms-python.black-formatter
    code --install-extension ms-toolsai.jupyter
    code --install-extension esbenp.prettier-vscode
    code --install-extension eamodio.gitlens
    code --install-extension foxundermoon.shell-format
    code --install-extension tomoki1207.pdf
    code --install-extension GrapeCity.gc-excelviewer
    code --install-extension kisstkondoros.vscode-gutter-preview
    code --install-extension redhat.vscode-yaml
    echo "VSCode extensions installed."
    echo "----------------------------"

}

#######################################################
# Function to create .vscode/settings.json
create_vscode_settings() {
    local env_path="$(pwd)/env/bin/python"
    local settings_content=$(
        cat <<EOF
{
    "python.defaultInterpreterPath": "$env_path",
    "black-formatter.interpreter": ["$env_path"],
    "pylint.interpreter": ["$env_path"],
    "isort.interpreter": ["$env_path"],
    "files.exclude": {
        "**/*.pyc": true,
        "**/__pycache__": true,
        ".github": true,
        ".vscode": true,
        "env": true
    },
    "files.autoSaveWhenNoErrors": true,
    "[shellscript]": {
        "editor.defaultFormatter": "foxundermoon.shell-format"
    },
    "[python]": {
        "editor.defaultFormatter": "ms-python.black-formatter",
        "editor.formatOnSave": true,
        "editor.codeActionsOnSave": {
            "source.organizeImports": "always"
        }
    },
    "editor.tabSize": 3,
    "editor.defaultFormatter": "esbenp.prettier-vscode",
    "editor.formatOnSave": true,
    "notebook.formatOnSave.enabled": true,
    "notebook.formatOnCellExecution": true,
    "notebook.defaultFormatter": "ms-python.black-formatter",
    "python.analysis.diagnosticMode": "workspace",
    "python.languageServer": "Pylance",
    "black-formatter.args": ["--line-length=88"],
    "pylint.args": ["--max-line-length=88"],
}
EOF
    )

    # Create the .vscode directory if it doesn't exist
    mkdir -p .vscode

    # Write the content to the settings.json file
    echo "$settings_content" >.vscode/settings.json
    echo "VSCode settings saved."
    echo "----------------------------"

}

#######################################################
# Function to create .github/workflows/checks.yml
create_github_workflow() {
    local checks_yml_content='name: Checks

on: [push, pull_request]

jobs:
  checks:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: "3.12"

    - name: Cache dependencies
      uses: actions/cache@v2
      with:
        path: ~/.cache/pip
        key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements.txt') }}
        restore-keys: |
          ${{ runner.os }}-pip-

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install black pylint isort mypy pytest

    - name: Run Black
      run: black --check .

    - name: Run Pylint
      run: pylint **/*.py

    - name: Run Isort
      run: isort --check-only .

    - name: Run Mypy
      run: mypy .

    - name: Run Tests
      run: |
        if ls tests/*.py 1> /dev/null 2>&1; then
          pytest
        else
          echo "No test files found"
        fi
'

    # Create the .github/workflows directory if it doesn't exist
    mkdir -p .github/workflows

    # Write the content to the checks.yml file
    echo "$checks_yml_content" >.github/workflows/checks.yml

    echo "GitHub Action saved."
    echo "----------------------------"

}

#######################################################
# Function to create .gitignore
create_gitignore() {
    local gitignore_content='.vscode/
.github/
.gitignore/
env/
__pycache__/
*.pyc
*.pyo
*.pyd
*.DS_Store
.env
box/*.yaml
'

    # Create the .gitignore file
    echo "$gitignore_content" >.gitignore
    echo ".gitignore created."
    echo "----------------------------"
}

#######################################################
# Function to create and set up the virtual environment
create_virtual_env() {

    # Check if pyenv is installed
    if ! command_exists pyenv; then
        echo "pyenv could not be found. Please install pyenv first."
        exit 1
    fi

    # Set the global Python version using pyenv
    pyenv install -s 3.12.4
    pyenv global 3.12.4

    # Create the virtual environment
    python -m venv env

    # Activate the virtual environment
    source env/bin/activate

    # Check if requirements.txt exists and install packages
    if [ -f "requirements.txt" ]; then
        pip install --upgrade pip
        pip install -r requirements.txt
        echo "Installed packages from requirements.txt."
    else
        echo "requirements.txt not found. Skipping package installation."
    fi

    echo "Environment ready."
}

###################### MAIN ###########################

# Check if the `code` command is available
if ! command_exists code; then
    echo "The 'code' command could not be found. Please ensure Visual Studio Code is installed and the 'code' command is available in your PATH."
    echo "To install the 'code' command in PATH, follow these steps:"
    echo "1. Open Visual Studio Code."
    echo "2. Press Cmd+Shift+P (on Mac) or Ctrl+Shift+P (on Windows/Linux)."
    echo "3. Type 'Shell Command: Install 'code' command in PATH' and select the option."
    exit 1
fi

# Install
install_pyenv

# Install VSCode extensions
install_vscode_extensions

# Create .vscode/settings.json
create_vscode_settings

# Create .github/workflows/checks.yml
create_github_workflow

# Create .gitignore
create_gitignore

# Create and set up the virtual environment
create_virtual_env

# Add the current module to the Python path
echo "export PYTHONPATH=\"$(pwd)/src:\$PYTHONPATH\"" >>env/bin/activate

# First access to Box (assuming box/oauth2.py is necessary)
if [ -f "box/oauth2.py" ]; then
    source env/bin/activate
    python box/oauth2.py
else
    echo "box/oauth2.py not found. Skipping Box authentication setup."
fi

# Final word
echo "==================="
echo "That's it! Enjoy :)"
