## Setting up the environment

### Install dependencies
we use uv to manage dependencies and build the package.
```bash
# Install uv if you don't have it already
curl -sSf https://install.pypa.io/get-pip.py | python3 -
pip install uv

# run unit tests
uv run pytest tests/unit

# run integration tests
export ACI_API_KEY=<your-api-key>
export LINKED_ACCOUNT_OWNER_ID=<your-linked-account-owner-id>
uv run pytest tests/it
```

### Coding style
- Install `pre-commit` hooks: `pre-commit install`
- Setup you preferred editor to use `ruff` formatter
  - e.g., you might need to install `ruff` formatter extension in VS Code or Cursor, and configure the setting as below

      ```json

      {
          "[python]": {
            "editor.formatOnSave": true,
            "editor.defaultFormatter": "charliermarsh.ruff",
            "editor.codeActionsOnSave": {
              "source.organizeImports.ruff": "always"
            }
          }
      }
      ```

### Build and publish the package

```bash
uv sync
uv build
uv publish --token $PYPI_API_TOKEN
```
