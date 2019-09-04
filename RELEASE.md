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

## Cleanup

To remove old build artifacts:
```bash
pipenv run ./setup.py clean --all
```

## Update the version

1. Create a tag for the current version: 

```bash
git tag `python -m aws_ssh_sync.main -v`
git push --tags
```

2. Bump the `__version__` in the main [module](aws_ssh_sync/__init__.py)

## References

* [Packaging Python Projects](https://packaging.python.org/tutorials/packaging-projects/)
