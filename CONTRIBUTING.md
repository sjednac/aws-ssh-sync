# Contributing 

:sparkles:First of all, thanks for taking the time to contribute! :sparkles:

There are plenty of [options](https://linux.die.net/man/5/ssh_config), that are not covered by the script yet. If you want to add a new feature, please read ahead. Bugfixes, documentation improvements and general suggestions are also more than welcome!

## General workflow

Unless you're fixing a typo or want to fix something trivial, please follow these steps:

1. Create an [issue](/issues) in **GitHub**, describing the problem or the feature request, so that we can disuss it first.
1. If you want to work on the issue yourself, please state so in the description or add a comment.
1. Fork the repository, commit your changes (check the brief [coding standards](#Coding-standards) section below) and open a pull request.

## Coding standards

Before you open a pull request:

1. [Rebase your branch](https://gist.github.com/ravibhure/a7e0918ff4937c9ea1c456698dcd58aa) against `upstream/master`. Squash any unncessary commits, if possible (`git rebase -i ...`).
1. Make sure that any new features and/or changes are reflected in the `README.md` file. 
1. Make sure that the code is formatted properly:

```bash
pipenv run autopep8 -ir .
```

4. Make sure that all unit tests are passing:

```bash
pipenv run pytest
```

5. If you want to check the script in action, you can use the following command: 

```bash
pipenv run python -m aws_ssh_sync.main
```

6. If you change any dependencies, then it might be a good idea to build and install a `pip` package locally. Check instructions in [RELEASE.md](RELEASE.md) for more details.
