# Release process

## Generating distribution archives

To create the source and binary distributions:

```bash
pipenv run ./setup.py sdist bdist_wheel
```

## Installing the package

To install the package **locally**, without publishing:

```
pip install dist/*.whl
```

## References

* [Packaging Python Projects](https://packaging.python.org/tutorials/packaging-projects/)
