#!/usr/bin/env python
# -*- coding: utf-8 -*-

import boto3
import os

from collections import namedtuple
from functools import reduce
from operator import attrgetter

SSHTarget = namedtuple(
    'SSHTarget',
    'id name name_index host user strict_host_key_checking'
)


def _ec2_regions():
    """Return a list of AWS regions."""
    # TODO: whitelist and blacklist support
    # response = boto3.client('ec2').describe_regions()
    # return [region['RegionName'] for region in response['Regions']]
    return ['eu-central-1']


def _ec2_instances(region):
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


def _ssh_targets(region):
    """Return a list of potential SSH targets for a given region"""

    def _name(instance):
        """Make a name for an EC2 instance"""
        iterator = (t['Value'] for t in instance['Tags']
                    if 'Key' in t and t['Key'] == 'Name')

        return next(iterator, instance['InstanceId'])

    def _target(instance):
        """Make an SSH target from an EC2 instance"""
        return SSHTarget(
            id=instance['InstanceId'],
            name=_name(instance),
            name_index=None,
            host=instance['PrivateIpAddress'],
            # TODO: Dynamic user
            user="ec2-user",
            # TODO: Make this dynamic.
            strict_host_key_checking=True
        )

    def _indexed(targets):
        """Index targets by name, so that ['foo','foo','bar'] can become ['foo-0','foo-1','bar-0']."""

        def add_index(target_cur, target_prv):
            if target_prv and target_cur.name == target_prv.name:
                name_index = target_prv.name_index + 1
            else:
                name_index = 0

            fields = target_cur._asdict()
            fields['name_index'] = name_index
            return SSHTarget(**fields)

        targets_sorted = sorted(targets, key=attrgetter('name'))
        targets_indexed = reduce(lambda acc, target: acc + [add_index(target, acc[-1] if len(acc) > 0 else None)],
                                 targets_sorted, [])
        return targets_indexed

    targets_raw = [_target(instance) for instance in _ec2_instances(region)]
    targets_indexed = _indexed(targets_raw)

    return targets_indexed


def main():
    """Main function"""

    config_id = os.environ.get('AWS_PROFILE', 'default')

    print(f"# BEGIN: aws-ssh-sync {config_id}")
    print(f"# Generated automatically by `aws_ssh_sync`.")
    print(f"")

    for region in _ec2_regions():
        print(f"### {region}")
        print("")

        for target in _ssh_targets(region):
            # TODO: support global name prefix for autocomplete with multiple files
            if target.name == target.id:
                host_name = target.name
            else:
                host_name = f"{target.name}{target.name_index}"

            print(f"# {target.id}")
            print(f"Host {host_name}")
            print(f"\tHostName {target.host}")
            if target.user:
                print(f"\tUser {target.user}")
            if not target.strict_host_key_checking:
                print(f"\tStrictHostKeyChecking no")
                print(f"\tUserKnownHostsFile=/dev/null")
            print("")

    print(f"# END: aws-ssh-sync {config_id}")


if __name__ == "__main__":
    main()
