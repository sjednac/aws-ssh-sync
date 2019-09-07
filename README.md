# SSH config synchronisation for AWS

[![Build Status](https://travis-ci.org/sbilinski/aws-ssh-sync.svg?branch=master)](https://travis-ci.org/sbilinski/aws-ssh-sync) 
[![PyPI version](https://badge.fury.io/py/aws-ssh-sync.svg)](https://badge.fury.io/py/aws-ssh-sync)

Generate `ssh_config` files, based on current [Amazon EC2](https://aws.amazon.com/ec2/) state.

## Features

* Connect to one or more regions at once.
* Filter EC2 instances by name. Useful for including relevant nodes only or for creating separate config sets for the same environment (e.g. use a different `User` for different nodes).
* Identify hosts using tags or instance IDs:
    * Index duplicates (e.g. in autoscaling groups) using instance launch time.
    * Include a global name prefix and/or a region ID to identify the connection in a unique way.
* Use public or private IPs.
* Set various SSH params:
    * Skip strict host checking, if needed. Can be useful when working with (internal) autoscaling groups.
    * Provide a server alive interval to keep the connection from timing out.
    * Use custom identity files.
    * Setup a proxy command for utilizing jump hosts.
    * ...
* Write to `stdout` or a [master file with config-key substitution](#file-output). Useful for working with tools, that don't support the `Include` directive.

## Installation

You can install the latest package using `pip`:

```bash
pip install aws-ssh-sync
```

## Usage

To get a full list of options:
```bash
aws_ssh_sync --help
```

### Preview

The easiest way to get a **preview** of the current config in AWS is to print the output directly to `stdout`:

```bash
aws_ssh_sync --profile <profile> --region <region>
```

### Utilising the 'Include' directive

If you want to **isolate** the generated config, you can write it to a dedicated file, and `Include` it in the main config. The base use-case is as follows:

```bash
aws_ssh_sync --profile <profile> --region <region> > ~/.ssh/config.d/<some_file>
```

To extend your `~/.ssh/config`, add the following line:

```
Include config.d/*
```

### <a name="file-output"></a>Working with a single config file

Splitting config into multiple, small files keeps things elegant and clean - you should probably stick to that, if you can. 

Unfortunatelly, some tools may still have trouble with the `Include` directive itself. If you want to use a single file (e.g. `~/.ssh/config`) for keeping all configuration, then you can specify the `--output-file` together with a `--config-key`:

```bash
aws_ssh_sync --profile <profile> --region <region> --config-key <key> --output-file <path>
``` 

Behaviour:

* Configuration is written to the `--output-file` rather than `stdout`.
* If the file doesn't exist, then it will be created.
* If a section identified by `--config-key` exists, then it will be replaced. 
* If no `--config-key` was found, then a new section will be appended to the file.
* **No backup file is created at the moment.**

## References

* [Origin, motivation and acknowledgements](http://mintbeans.com/aws-ssh-sync/) - blog post.
