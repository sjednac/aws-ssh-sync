#!/usr/bin/env python
# -*- coding: utf-8 -*-

import boto3
import os
import sys

from argparse import ArgumentParser
from collections import namedtuple
from functools import reduce
from operator import attrgetter

SSHTarget = namedtuple(
    'SSHTarget',
    'id name name_index host_name user strict_host_key_checking'
)


def _ec2_regions(config):
    """Return a list of AWS regions."""
    # TODO: whitelist and blacklist support
    # response = boto3.client('ec2').describe_regions()
    # return [region['RegionName'] for region in response['Regions']]
    return ['eu-central-1']


def _ec2_instances(config, region):
    """Return a list of running instance descriptors for a given region"""
    ec2 = boto3.client('ec2', region_name=region)

    response = ec2.describe_instances(
        Filters=[
            {'Name': 'instance-state-name', 'Values': ['running']}
        ]
    )

    instance_lists = [r['Instances'] for r in response['Reservations']]
    instance_lists_flatten = reduce(lambda l1, l2: l1 + l2, instance_lists)

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
            return f"{config.config_key}_{base_name}"

    return SSHTarget(
        id=instance['InstanceId'],
        name=name(instance),
        name_index=None,
        host_name=instance['PrivateIpAddress'],
        user=config.user,
        strict_host_key_checking=not config.no_strict_host_checking
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
    parser = ArgumentParser(
        description="Generate ssh_config files from AWS.",
        epilog="Check ssh_config man page for an output format reference."
    )

    parser.add_argument("-k", "--config-key",
                        help="identify output using an explicit config key",
                        default=os.environ.get('AWS_PROFILE', 'default'))
    parser.add_argument("-p", "--name-prefix",
                        help="add prefix to all host names",
                        default=None)
    parser.add_argument("-S", "--no-strict-host-checking",
                        help="no strict host key checking (ignore `known_hosts` file)",
                        action="store_true",
                        default=False)
    parser.add_argument("-u", "--user",
                        help="sign in as user",
                        default="ec2-user")

    return parser.parse_args(list(args))


def main(*args):
    """Main function"""
    config = _parse_config(*args)

    print(f"# BEGIN [{config.config_key}]")
    print(f"# Generated automatically by `{os.path.basename(__file__)}`.")
    print(f"")

    for region in _ec2_regions(config):
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
