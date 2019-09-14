#!/usr/bin/env python
# -*- coding: utf-8 -*-

import boto3
import os
import re
import sys

from . import __version__
from argparse import ArgumentParser, SUPPRESS
from collections import namedtuple
from functools import reduce

SSHTarget = namedtuple(
    'SSHTarget',
    'id launch_time name name_index host port user identity_file identities_only server_alive_interval strict_host_key_checking proxy_command'
)


def _ec2_instances(config, region):
    """Return a list of running instance descriptors for a given region"""
    session = boto3.session.Session(profile_name=config.profile)

    ec2 = session.client("ec2", region_name=region)

    filters = [{"Name": "instance-state-name", "Values": ["running"]}]
    if config.ec2_filter_name and len(config.ec2_filter_name) > 0:
        filters.append(
            {'Name': 'tag:Name', 'Values': config.ec2_filter_name}
        )

    response = ec2.describe_instances(Filters=filters)

    instance_lists = [r["Instances"]
                      for r in response["Reservations"] if "Instances" in r]
    instance_lists_flatten = reduce(lambda l1, l2: l1 + l2, instance_lists, [])

    return instance_lists_flatten


def _ssh_target(config, region, instance):
    """Make an SSH target from an EC2 instance"""

    def name(instance):
        iterator = (t['Value'] for t in instance['Tags']
                    if 'Key' in t and t['Key'] == 'Name')

        base_name = next(iterator, instance['InstanceId'])

        if config.region_prefix:
            base_name = f"{region}-{base_name}"

        if config.name_prefix:
            base_name = f"{config.name_prefix}{base_name}"

        return base_name

    def host(instance):
        public_addr = instance["PublicIpAddress"] if "PublicIpAddress" in instance else None
        private_addr = instance["PrivateIpAddress"]

        if config.address == "public_private":
            return public_addr if public_addr else private_addr
        elif config.address == "public":
            return public_addr
        elif config.address == "private":
            return private_addr
        else:
            assert False, f"Invalid address selector: {config.address}"

    return SSHTarget(
        id=instance['InstanceId'],
        launch_time=instance['LaunchTime'],
        name=name(instance),
        name_index=None,
        host=host(instance),
        port=config.port,
        user=config.user,
        identity_file=config.identity_file,
        identities_only=not config.no_identities_only,
        server_alive_interval=config.server_alive_interval,
        strict_host_key_checking=not config.skip_strict_host_checking,
        proxy_command=config.proxy_command
    )


def _ssh_targets(config, region):
    """Fetch a list of indexed SSH targets for a given region."""

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
            # Don't alter the name, if instance ID is already in it, as it's explicit enough.
            return target

        fields = target._asdict()
        fields['name'] = f"{target.name}{target.name_index}"
        return SSHTarget(**fields)

    targets_raw = [_ssh_target(config, region, instance)
                   for instance in _ec2_instances(config, region)]
    targets_filtered = [target for target in targets_raw if target.host]
    targets_sorted = sorted(
        targets_filtered, key=lambda t: (t.name, t.launch_time))
    targets_indexed = reduce(lambda acc, target: acc + [add_index(target, acc[-1] if len(acc) > 0 else None)],
                             targets_sorted, [])
    targets_renamed = [change_name(target) for target in targets_indexed]

    return targets_renamed


def _ssh_config_header(config):
    """Return a `config`-based header for the ssh_config"""
    return f"# BEGIN [{config.config_key}]"


def _ssh_config_footer(config):
    """Return a `config`-based footer for the ssh_config"""
    return f"# END [{config.config_key}]"


def _writer(config):
    """Return a callable 'writer' object that can be used for outputting the config."""

    class FileWriter():
        def __init__(self):
            self.lines = []

        def __enter__(self):
            return self

        def __exit__(self, ex_type, ex_value, ex_traceback):
            if ex_type or ex_value or ex_traceback:
                print(
                    f"An error occured. Write to {config.output_file} aborted.")
                return

            print(
                f"Preparing to write {len(self.lines)} lines to {config.output_file}.."
            )

            if os.path.exists(config.output_file):
                with open(config.output_file, "r") as f:
                    current_content = f.read()
            else:
                current_content = ""

            header = _ssh_config_header(config)
            footer = _ssh_config_footer(config)

            section_pattern = re.compile(
                f"{re.escape(header)}.*?{re.escape(footer)}",
                re.DOTALL
            )

            section_data = "\n".join(self.lines) + "\n"

            if section_pattern.search(current_content):
                print(
                    f"{config.config_key} section exists. Replacing generated content.."
                )

                new_content = section_pattern.sub(
                    section_data,
                    current_content
                )
            else:
                print(
                    f"{config.config_key} section doesn't exist. Appending a new section.."
                )

                new_content = f"{current_content}{section_data}"

            with open(config.output_file, "w") as f:
                print("Committing changes..")
                f.write(new_content)

            print(f"Done.")

        def __call__(self, line):
            self.lines.append(line)

    class StdoutWriter():
        def __enter__(self):
            return self

        def __exit__(self, type, value, traceback):
            pass

        def __call__(self, line):
            print(line)

    if config.output_file:
        return FileWriter()
    else:
        return StdoutWriter()


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
                        version=__version__)
    parser.add_argument("-h", "--help",
                        help="Print this help message and exit.",
                        action="help",
                        default=SUPPRESS)

    # AWS
    aws_group = parser.add_argument_group("AWS")
    aws_group.add_argument("-p", "--profile",
                           help="Use a specific AWS profile. Falls back to AWS_PROFILE, then 'default'.",
                           **env_value("AWS_PROFILE", default="default"))
    aws_group.add_argument("-r", "--region",
                           help="Connect to region(s). Falls back to AWS_REGION.",
                           nargs="+",
                           **env_value("AWS_REGION", map_env_value=lambda x: [x]))
    aws_group.add_argument("-f", "--ec2-filter-name",
                           help=("Define a name filter for the EC2 instance query. Use '*' as a wildcard. Chaining multiple "
                                 "filters works as an 'OR' operator."),
                           metavar="FILTER",
                           nargs="+",
                           default=None)
    aws_group.add_argument("-a", "--address",
                           help="Define how EC2 address resolution should work.",
                           default="public_private",
                           choices=["public_private", "public", "private"])

    # Output
    output_group = parser.add_argument_group("Output")
    output_group.add_argument("-k", "--config-key",
                              help="Use an explicit key to identify this 'config'. Falls back to AWS_PROFILE, then 'default'.",
                              metavar="KEY",
                              **env_value("AWS_PROFILE", default="default"))
    output_group.add_argument("-o", "--output-file",
                              metavar="FILE",
                              help=("Specify an output file location. Overwrites relevant `config-key` section "
                                    "in the file, if it exists. Appends a new section otherwise."))

    # SSH
    ssh_group = parser.add_argument_group("SSH")
    ssh_group.add_argument("--region-prefix",
                           help="Add a region prefix to all SSH host names.",
                           default=False,
                           action="store_true")
    ssh_group.add_argument("--name-prefix",
                           help="Add a string prefix to all SSH host names.",
                           metavar="PREF",
                           default="")
    ssh_group.add_argument("--port",
                           help="Use an explicit port.",
                           metavar="PORT",
                           default=None)
    ssh_group.add_argument("--user",
                           help="Sign in as user.",
                           default="ec2-user")
    ssh_group.add_argument("--identity-file",
                           help="Use specific identity file.",
                           metavar="FILE",
                           default=None)
    ssh_group.add_argument("--server-alive-interval",
                           help="Provide a ServerAliveInterval in seconds.",
                           metavar="SECS",
                           default=None)
    ssh_group.add_argument("--no-identities-only",
                           help="Don't add an IdentitiesOnly directive.",
                           action="store_true",
                           default=False)
    ssh_group.add_argument("--skip-strict-host-checking",
                           help="Skip strict host key checking and ignore any entries in the `known_hosts` file.",
                           action="store_true",
                           default=False)
    ssh_group.add_argument("--proxy-command",
                           help="Provide a ProxyCommand directive.",
                           default=None)

    return parser.parse_args(list(args))


def make_ssh_config(*args):
    """Make an ssh_config setup."""
    config = _parse_config(*args)

    with _writer(config) as out:
        out(_ssh_config_header(config))
        out(f"# Generated automatically by `aws_ssh_sync`.")
        out(f"")

        for region in config.region:
            out(f"## {region}")
            out("")

            for target in _ssh_targets(config, region):
                out(f"### {target.id}")
                out(f"Host {target.name}")
                out(f"\tHostName {target.host}")
                if target.port:
                    out(f"\tPort {target.port}")
                if target.user:
                    out(f"\tUser {target.user}")
                if target.identity_file:
                    out(f"\tIdentityFile {target.identity_file}")
                if target.identities_only:
                    out(f"\tIdentitiesOnly yes")
                if target.server_alive_interval:
                    out(f"\tServerAliveInterval {target.server_alive_interval}")
                if not target.strict_host_key_checking:
                    out(f"\tStrictHostKeyChecking no")
                    out(f"\tUserKnownHostsFile=/dev/null")
                if target.proxy_command:
                    out(f"\tProxyCommand {target.proxy_command}")
                out("")

        out(_ssh_config_footer(config))


def main():
    """Main function"""
    make_ssh_config(*sys.argv[1:])


if __name__ == "__main__":
    main()
