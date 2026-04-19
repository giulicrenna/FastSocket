# Contributing

Contributions are welcome! Follow these steps to collaborate.

## Development setup

```bash
git clone https://github.com/giulicrenna/FastSocket.git
cd FastSocket
pip install -e ".[dev]"
```

## Running tests

```bash
pytest tests/
```

## Code style

- Follow [PEP 8](https://peps.python.org/pep-0008/).
- Use `typing` annotations in public signatures.
- Add docstrings to public classes and methods.

## Pull Requests

1. Create a branch from `main`.
2. Make changes with descriptive commits.
3. Open a PR explaining the motivation for the change.
4. Wait for review before merging.

## Reporting bugs

Use [GitHub Issues](https://github.com/giulicrenna/FastSocket/issues) and include:

- Python and FastSocket version.
- Minimal reproduction of the problem.
- Full traceback if applicable.
