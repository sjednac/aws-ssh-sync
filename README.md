# SSH config synchronisation for AWS

Generate `ssh_config` files, based on current EC2 state.

## Usage

Using a virtual [pipenv](https://github.com/pypa/pipenv) environment is recommended, but not strictly required. If you have all [dependencies](Pipfile) present, you can launch the script directly.

To get the full list of options:
```bash
pipenv run ./aws_ssh_sync.py -h
```

### Preview

The easiest way to get a **preview** of the current config in AWS is to print the output directly to `stdout`:

```bash
AWS_PROFILE=<profile_id> pipenv run ./aws_ssh_sync.py --region <region>
```

### Utilising the 'Include' directive

If you want to keep the generated config **separately**, then you can write it to a dedicated file and `Include` it in the main config. The base use-case is as follows:

```bash
AWS_PROFILE=<profile_id> pipenv run ./aws_ssh_sync.py --region <region> > ~/.ssh/config.d/<some_file>
```

To extend your `~/.ssh/config` add the following:

```
Include config.d/*
```

**NOTE:** Some tools may have trouble with the `Include` directive.
