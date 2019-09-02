# -*- coding: utf-8 -*-

from aws_ssh_sync.main import make_ssh_config


def test_default_config_to_stdout(ec2_stub, ec2_region_name, capsys, monkeypatch):

    monkeypatch.setenv("AWS_PROFILE", "default")
    monkeypatch.setenv("AWS_REGION", ec2_region_name)

    ec2_stub.add_response(
        "describe_instances",
        expected_params={
            "Filters": [
                {"Name": "instance-state-name", "Values": ["running"]}
            ]
        },
        service_response={
            "Reservations": [
                {
                    "Instances": [
                        {
                            "InstanceId": "i-1",
                            "PrivateIpAddress": "192.168.0.1",
                            "PublicIpAddress": "42.42.42.42",
                            "LaunchTime": "2019-01-01 09:00:00+00:00",
                            "Tags": []
                        },
                        {
                            "InstanceId": "i-2",
                            "PrivateIpAddress": "192.168.0.2",
                            "LaunchTime": "2018-01-01 09:00:00+00:00",
                            "Tags": [{"Key": "Name", "Value": "clusterfoo"}]
                        },
                        {
                            "InstanceId": "i-3",
                            "PrivateIpAddress": "192.168.0.3",
                            "LaunchTime": "2017-01-01 09:00:00+00:00",
                            "Tags": [{"Key": "Name", "Value": "clusterfoo"}]
                        }
                    ]
                }
            ]
        }
    )

    make_ssh_config()

    out, err = capsys.readouterr()

    assert err == ""
    assert out == f"""\
# BEGIN [default]
# Generated automatically by `aws_ssh_sync`.

## {ec2_region_name}

### i-3
Host clusterfoo0
\tHostName 192.168.0.3
\tUser ec2-user
\tIdentitiesOnly yes

### i-2
Host clusterfoo1
\tHostName 192.168.0.2
\tUser ec2-user
\tIdentitiesOnly yes

### i-1
Host i-1
\tHostName 42.42.42.42
\tUser ec2-user
\tIdentitiesOnly yes

# END [default]
"""


def test_extended_config_to_stdout(ec2_stub, ec2_region_name, capsys):
    ec2_stub.add_response(
        "describe_instances",
        expected_params={
            "Filters": [
                {"Name": "instance-state-name", "Values": ["running"]},
                {'Name': 'tag:Name', 'Values': ['*node*']}
            ]
        },
        service_response={
            "Reservations": [
                {
                    "Instances": [
                        {
                            "InstanceId": "i-1",
                            "PrivateIpAddress": "192.168.0.1",
                            "PublicIpAddress": "11.11.11.11",
                            "LaunchTime": "2018-01-01 09:00:00+00:00",
                            "Tags": [{"Key": "Name", "Value": "publicnode"}]
                        },
                        {
                            "InstanceId": "i-2",
                            "PrivateIpAddress": "192.168.0.2",
                            "PublicIpAddress": "22.22.22.22",
                            "LaunchTime": "2019-01-01 09:00:00+00:00",
                            "Tags": [{"Key": "Name", "Value": "publicnode"}]
                        },
                        {
                            "InstanceId": "i-3",
                            "PrivateIpAddress": "192.168.0.3",
                            "LaunchTime": "2017-01-01 09:00:00+00:00",
                            "Tags": [{"Key": "Name", "Value": "privatenode"}]
                        },
                    ]
                }
            ]
        }
    )

    make_ssh_config(
        "-p", "default",
        "-r", ec2_region_name,
        "-f", "*node*",
        "-a", "public",
        "-k", "test_key",
        "-P", "test-prefix-",
        "-R",
        "-U", "tester",
        "-I", "~/.ssh/id_rsa.test",
        "-A", "100",
        "-O",
        "-S"
    )

    out, err = capsys.readouterr()

    assert err == ""
    assert out == f"""\
# BEGIN [test_key]
# Generated automatically by `aws_ssh_sync`.

## {ec2_region_name}

### i-1
Host test-prefix-{ec2_region_name}-publicnode0
\tHostName 11.11.11.11
\tUser tester
\tIdentityFile ~/.ssh/id_rsa.test
\tServerAliveInterval 100
\tStrictHostKeyChecking no
\tUserKnownHostsFile=/dev/null

### i-2
Host test-prefix-{ec2_region_name}-publicnode1
\tHostName 22.22.22.22
\tUser tester
\tIdentityFile ~/.ssh/id_rsa.test
\tServerAliveInterval 100
\tStrictHostKeyChecking no
\tUserKnownHostsFile=/dev/null

# END [test_key]
"""


def test_no_instances_to_stdout(ec2_stub, ec2_region_name, capsys):

    ec2_stub.add_response(
        "describe_instances",
        expected_params={
            "Filters": [
                {"Name": "instance-state-name", "Values": ["running"]}
            ]
        },
        service_response={
            "Reservations": [
            ]
        }
    )

    make_ssh_config(
        "-r", ec2_region_name
    )

    out, err = capsys.readouterr()

    assert err == ""
    assert out == f"""\
# BEGIN [default]
# Generated automatically by `aws_ssh_sync`.

## {ec2_region_name}

# END [default]
"""
