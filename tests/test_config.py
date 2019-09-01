# -*- coding: utf-8 -*-

import aws_ssh_sync


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

    aws_ssh_sync.main()

    out, err = capsys.readouterr()

    assert err == ""
    assert out == f"""\
# BEGIN [default]
# Generated automatically by `aws_ssh_sync.py`.

## {ec2_region_name}

### i-3
Host clusterfoo0
\tHostName 192.168.0.3
\tUser ec2-user

### i-2
Host clusterfoo1
\tHostName 192.168.0.2
\tUser ec2-user

### i-1
Host i-1
\tHostName 192.168.0.1
\tUser ec2-user

# END [default]
"""


def test_extended_config_to_stdout(ec2_stub, ec2_region_name, capsys):
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
                            "LaunchTime": "2018-01-01 09:00:00+00:00",
                            "Tags": [{"Key": "Name", "Value": "servicenode"}]
                        },
                        {
                            "InstanceId": "i-2",
                            "PrivateIpAddress": "192.168.0.2",
                            "LaunchTime": "2019-01-01 09:00:00+00:00",
                            "Tags": [{"Key": "Name", "Value": "servicenode"}]
                        }
                    ]
                }
            ]
        }
    )

    aws_ssh_sync.main(
        "-r", ec2_region_name,
        "-k", "test_key",
        "-P", "test_prefix_",
        "-U", "tester",
        "-S"
    )

    out, err = capsys.readouterr()

    assert err == ""
    assert out == f"""\
# BEGIN [test_key]
# Generated automatically by `aws_ssh_sync.py`.

## {ec2_region_name}

### i-1
Host test_prefix_servicenode0
\tHostName 192.168.0.1
\tUser tester
\tStrictHostKeyChecking no
\tUserKnownHostsFile=/dev/null

### i-2
Host test_prefix_servicenode1
\tHostName 192.168.0.2
\tUser tester
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

    aws_ssh_sync.main(
        "-r", ec2_region_name
    )

    out, err = capsys.readouterr()

    assert err == ""
    assert out == f"""\
# BEGIN [default]
# Generated automatically by `aws_ssh_sync.py`.

## {ec2_region_name}

# END [default]
"""