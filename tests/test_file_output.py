# -*- coding: utf-8 -*-

import pytest

from aws_ssh_sync.main import make_ssh_config


@pytest.fixture
def _file_requests(ec2_stub, ec2_region_name, monkeypatch):
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
                            "LaunchTime": "2017-01-01 09:00:00+00:00",
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
                            "LaunchTime": "2019-01-01 09:00:00+00:00",
                            "Tags": [{"Key": "Name", "Value": "clusterfoo"}]
                        }
                    ]
                }
            ]
        }
    )


@pytest.fixture
def _file_requests_config(ec2_region_name):
    return f"""\
# BEGIN [testprofile]
# Generated automatically by `aws_ssh_sync`.

## {ec2_region_name}

### i-2
Host clusterfoo0
\tHostName 192.168.0.2
\tUser ec2-user
\tIdentitiesOnly yes

### i-3
Host clusterfoo1
\tHostName 192.168.0.3
\tUser ec2-user
\tIdentitiesOnly yes

### i-1
Host i-1
\tHostName 192.168.0.1
\tUser ec2-user
\tIdentitiesOnly yes

# END [testprofile]
"""


def test_output_to_new_file(_file_requests, _file_requests_config, tmp_path):

    target_file = tmp_path / "ssh_test.conf"

    make_ssh_config(
        "-o", str(target_file)
    )

    assert target_file.read_text() == _file_requests_config


def test_output_to_existing_file(_file_requests, _file_requests_config, tmp_path):

    target_file = tmp_path / "ssh_test.conf"
    target_file.write_text("foo\nbar\n")

    make_ssh_config(
        "-o", str(target_file)
    )

    assert target_file.read_text() == f"foo\nbar\n{_file_requests_config}"


def test_output_to_existing_file_with_section(_file_requests, _file_requests_config, tmp_path):

    target_file = tmp_path / "ssh_test.conf"
    target_file.write_text("""\
foo

# BEGIN [testprofile]

Some old stuff, that should be replaced.

# END [testprofile]

bar
""")

    make_ssh_config(
        "-o", str(target_file)
    )

    assert target_file.read_text() == f"""\
foo

{_file_requests_config}

bar
"""
