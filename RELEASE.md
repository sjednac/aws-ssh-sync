# Release process

## Generating distribution archives

To create the source and binary distributions:

```bash
pipenv run ./setup.py sdist bdist_wheel
```

## Installing the package offline

To install the package **locally**, without publishing:

```bash
pip install dist/*.whl
```

## Publishing the package

To publish the package to [pypi](https://pypi.org/project/aws-ssh-sync/):

```bash
pipenv run python -m twine upload --repository-url https://upload.pypi.org/legacy/ dist/*
```

## References

* [Packaging Python Projects](https://packaging.python.org/tutorials/packaging-projects/)
