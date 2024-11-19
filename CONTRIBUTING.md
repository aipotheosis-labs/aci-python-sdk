## Setting up the environment

### Install dependencies with poetry and pyenv
we use poetry to manage dependencies and build the package and pyenv to manage python versions.
for example (assuming you have pyenv and poetry installed):
```bash
# install python 3.10
pyenv install 3.10
# set local python version for sdk repo
pyenv local 3.10
# set version for poetry
poetry env use 3.10
# install dependencies
poetry install
```

### Coding style
all the following tools are part of `pyproject.toml` dev dependencies, and are automatically installed when running `poetry install`

- use `black` to format the code
- use `flake8` to lint the code
- use `mypy` to type check the code
- use `isort` to sort the imports
- use `pre-commit` to run the above tools as pre-commit hooks
- Install `pre-commit` hooks: `pre-commit install`
- Setup you preferred editor to use `Black` formatter
  - e.g., you might need to install `Black` formatter extension in VS Code, and configure the setting as below
    ```json
    {
    "editor.formatOnSave": true,
    "editor.defaultFormatter": "ms-python.black-formatter"
    }
    ```

### Codee changes
