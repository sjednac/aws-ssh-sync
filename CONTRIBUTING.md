# Contributing 

:sparkles:First of all, thanks for taking the time to contribute! :sparkles:

## General workflow

Unless you're fixing a typo or want to fix something trivial, please follow the process below:

1. Create an issue in **GitHub**, describing the problem or the feature request, so that we can disuss it first.
1. If you want to work on the issue yourself, please state so in the description or add a comment.
1. Fork the repository. 
1. Create a new branch in your repository, commit your changes (check the [coding standards](#Coding-standards) section below) and open a pull request.

## Coding standards

Before you open a pull request:

1. Make sure that any new features and/or changes are reflected in the `README.md` file. 
1. Make sure that the code is formatted properly:

```bash
pipenv run autopep8 -ir .
```

1. Make sure that unit tests are passing:

```bash
pipenv run pytest
```
