#!/usr/bin/env python
# -*- coding: utf-8 -*-

import boto3
import os
import sys

from argparse import ArgumentParser, SUPPRESS
from collections import namedtuple
from functools import reduce
from operator import attrgetter

SSHTarget = namedtuple(
    'SSHTarget',
    'id name name_index host_name user strict_host_key_checking'
)


def _ec2_instances(config, region):
    """Return a list of running instance descriptors for a given region"""
    session = boto3.session.Session(profile_name=config.profile)

    ec2 = session.client("ec2", region_name=region)

    response = ec2.describe_instances(
        Filters=[
            {"Name": "instance-state-name", "Values": ["running"]}
        ]
    )

    instance_lists = [r["Instances"]
                      for r in response["Reservations"] if "Instances" in r]
    instance_lists_flatten = reduce(lambda l1, l2: l1 + l2, instance_lists, [])

    return instance_lists_flatten


def _ssh_target(config, instance):
    """Make an SSH target from an EC2 instance"""

    def name(instance):
        iterator = (t['Value'] for t in instance['Tags']
                    if 'Key' in t and t['Key'] == 'Name')

        base_name = next(iterator, instance['InstanceId'])

        if config.name_prefix:
            return f"{config.name_prefix}{base_name}"
        else:
            return base_name

    return SSHTarget(
        id=instance['InstanceId'],
        name=name(instance),
        name_index=None,
        host_name=instance['PrivateIpAddress'],
        user=config.user,
        strict_host_key_checking=not config.skip_strict_host_checking
    )


def _ssh_targets(config, region):
    """Return a list of indexed SSH targets for a given region"""

    def add_index(target_cur, target_prv):
        if target_prv and target_cur.name == target_prv.name:
            name_index = target_prv.name_index + 1
        else:
            name_index = 0

        fields = target_cur._asdict()
        fields['name_index'] = name_index
        return SSHTarget(**fields)

    def change_name(target):
        if target.id in target.name:
            # Don't alter the name, if ID is already of it, as it's explicit enough.
            return target

        fields = target._asdict()
        fields['name'] = f"{target.name}{target.name_index}"
        return SSHTarget(**fields)

    targets_raw = [_ssh_target(config, instance)
                   for instance in _ec2_instances(config, region)]
    targets_sorted = sorted(targets_raw, key=attrgetter('name'))
    targets_indexed = reduce(lambda acc, target: acc + [add_index(target, acc[-1] if len(acc) > 0 else None)],
                             targets_sorted, [])
    targets_renamed = [change_name(target) for target in targets_indexed]

    return targets_renamed


def _parse_config(*args):
    def env_value(key, default=None, map_env_value=lambda x: x):
        if key in os.environ:
            return {"default": map_env_value(os.environ.get(key))}
        elif default:
            return {"default": default}
        else:
            return {"required": True}

    parser = ArgumentParser(
        description="Generate ssh_config files from AWS.",
        epilog="Check ssh_config man page for an output format reference.",
        add_help=False
    )

    # Docs
    parser._optionals.title = "Docs"
    parser.add_argument("-v", "--version",
                        help="Print current version number and exit.",
                        action="version",
                        # TODO: Manage version in a more sensible way
                        version="0.1.0")
    parser.add_argument("-h", "--help",
                        help="Print this help message and exit.",
                        action="help",
                        default=SUPPRESS)

    # AWS
    aws_group = parser.add_argument_group("AWS")
    aws_group.add_argument("-p", "--profile",
                           help="Use specific AWS profile. Falls back to AWS_PROFILE, then 'default'.",
                           **env_value("AWS_PROFILE", default="default"))
    aws_group.add_argument("-r", "--region",
                           help="Connect to region(s). Falls back to AWS_REGION.",
                           nargs="+",
                           **env_value("AWS_REGION", map_env_value=lambda x: [x]))

    # Output
    output_group = parser.add_argument_group("Output")
    output_group.add_argument("-k", "--config-key",
                              help="Use an explicit key to identify this 'config'. Falls back to AWS_PROFILE, then 'default'.",
                              **env_value("AWS_PROFILE", default="default"))

    # SSH
    ssh_group = parser.add_argument_group("SSH")
    ssh_group.add_argument("-P", "--name-prefix",
                           help="Add a prefix to all host identifiers.",
                           default="")
    ssh_group.add_argument("-U", "--user",
                           help="Sign in as user.",
                           default="ec2-user")
    ssh_group.add_argument("-S", "--skip-strict-host-checking",
                           help="Skip strict host key checking and ignore any entries in the `known_hosts` file.",
                           action="store_true",
                           default=False)

    return parser.parse_args(list(args))


def main(*args):
    """Main function"""
    config = _parse_config(*args)

    print(f"# BEGIN [{config.config_key}]")
    print(f"# Generated automatically by `{os.path.basename(__file__)}`.")
    print(f"")

    for region in config.region:
        print(f"## {region}")
        print("")

        for target in _ssh_targets(config, region):
            print(f"### {target.id}")
            print(f"Host {target.name}")
            print(f"\tHostName {target.host_name}")
            if target.user:
                print(f"\tUser {target.user}")
            if not target.strict_host_key_checking:
                print(f"\tStrictHostKeyChecking no")
                print(f"\tUserKnownHostsFile=/dev/null")
            print("")

    print(f"# END [{config.config_key}]")


if __name__ == "__main__":
    main(*sys.argv[1:])
