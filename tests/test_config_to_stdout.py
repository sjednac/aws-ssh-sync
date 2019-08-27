# -*- coding: utf-8 -*-

import aws_ssh_sync


def test_default_config_to_stdout(ec2_stub, ec2_region_name, capsys):

    ec2_stub.add_response(
        'describe_instances',
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
                            "Tags": []
                        },
                        {
                            "InstanceId": "i-2",
                            "PrivateIpAddress": "192.168.0.2",
                            "Tags": [{"Key": "Name", "Value": "clusterfoo"}]
                        },
                        {
                            "InstanceId": "i-3",
                            "PrivateIpAddress": "192.168.0.3",
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

### i-2
Host default_clusterfoo0
\tHostName 192.168.0.2
\tUser ec2-user

### i-3
Host default_clusterfoo1
\tHostName 192.168.0.3
\tUser ec2-user

### i-1
Host default_i-1
\tHostName 192.168.0.1
\tUser ec2-user

# END [default]
"""


def test_extended_config_to_stdout(ec2_stub, ec2_region_name, capsys):
    ec2_stub.add_response(
        'describe_instances',
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
                            "Tags": [{"Key": "Name", "Value": "servicenode"}]
                        },
                        {
                            "InstanceId": "i-2",
                            "PrivateIpAddress": "192.168.0.2",
                            "Tags": [{"Key": "Name", "Value": "servicenode"}]
                        }
                    ]
                }
            ]
        }
    )

    aws_ssh_sync.main(
        "-k", "test_key",
        "-u", "tester",
        "-p", "test_prefix_",
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
