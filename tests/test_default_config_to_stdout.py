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
# BEGIN: aws-ssh-sync default
# Generated automatically by `aws_ssh_sync`.

### {ec2_region_name}

# i-2
Host clusterfoo0
\tHostName 192.168.0.2
\tUser ec2-user

# i-3
Host clusterfoo1
\tHostName 192.168.0.3
\tUser ec2-user

# i-1
Host i-1
\tHostName 192.168.0.1
\tUser ec2-user

# END: aws-ssh-sync default
"""
