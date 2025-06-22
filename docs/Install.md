# Installing Docmancer

## Prerequisites

- Python 3.8+
- Poetry (for dependency and environment management)
Install Poetry if you haven;t already:
    ```bash
    curl -sSL https://install.python-poetry.org | python3 -
    ```
> [!NOTE]
> After installation, restart your terminal or run source $HOME/.poetry/env.

## Installation Steps

1. Clone the Repository
    ```bash
    git clone https://github.com/brody-clark/docmancer.git
    cd docmancer
    ```
2. Install dependencies
    ```bash
    poetry install
    ```
3. Test the Tool (Optional)
    ```bash
    poetry run docmancer --help
    ```
4. Install as a Global CLI Tool
    ```bash
    poetry install --with main
    poetry build
    poetry install --no-root
    ```
5. Confirm Installation
    ```bash
    docmancer --help
    ```

## Uninstallation

To remove the tool:
```bash
poetry env remove python 
```