# -*- coding: utf-8 -*-

from aws_ssh_sync.main import make_ssh_config


def test_default_config_to_stdout(ec2_stub, ec2_region_name, capsys, monkeypatch):

    monkeypatch.setenv("AWS_PROFILE", "testprofile")
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
# BEGIN [testprofile]
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

# END [testprofile]
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
        "--profile", "testprofile",
        "--region", ec2_region_name,
        "--ec2-filter-name", "*node*",
        "--address", "public",
        "--config-key", "test_key",
        "--region-prefix",
        "--name-prefix", "test-prefix-",
        "--port", "22",
        "--user", "tester",
        "--identity-file", "~/.ssh/id_rsa.test",
        "--server-alive-interval", "100",
        "--no-identities-only",
        "--skip-strict-host-checking",
        "--proxy-command", "ssh ec2-user@jumphost nc %h %p"
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
\tPort 22
\tUser tester
\tIdentityFile ~/.ssh/id_rsa.test
\tServerAliveInterval 100
\tStrictHostKeyChecking no
\tUserKnownHostsFile=/dev/null
\tProxyCommand ssh ec2-user@jumphost nc %h %p

### i-2
Host test-prefix-{ec2_region_name}-publicnode1
\tHostName 22.22.22.22
\tPort 22
\tUser tester
\tIdentityFile ~/.ssh/id_rsa.test
\tServerAliveInterval 100
\tStrictHostKeyChecking no
\tUserKnownHostsFile=/dev/null
\tProxyCommand ssh ec2-user@jumphost nc %h %p

# END [test_key]
"""


def test_no_instances_to_stdout(ec2_stub, ec2_region_name, capsys, monkeypatch):

    monkeypatch.setenv("AWS_PROFILE", "testprofile")
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
            ]
        }
    )

    make_ssh_config()

    out, err = capsys.readouterr()

    assert err == ""
    assert out == f"""\
# BEGIN [testprofile]
# Generated automatically by `aws_ssh_sync`.

## {ec2_region_name}

# END [testprofile]
"""
