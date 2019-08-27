# SSH config synchronisation for AWS

Generate `ssh_config` files, based on current EC2 state.

## Usage

Using a virtual [pipenv](https://github.com/pypa/pipenv) environment is recommended, but not strictly required. If you have all the dependencies present on your operating system, then you can simply launch the script.

The base use-case is as follows:

```bash
AWS_PROFILE=<profile_id> pipenv run ./aws_ssh_sync.py > ~/.ssh/config.d/<profile_id>
```

You can extend your `~/.ssh/config` file to include any additional config as such:

```
Include config.d/*
```
