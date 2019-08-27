# -*- coding: utf-8 -*-

import boto3
import pytest

from botocore.stub import Stubber
from unittest.mock import MagicMock


@pytest.fixture(autouse=True)
def ec2_region_name():
    yield "eu-central-1"


@pytest.fixture(autouse=True)
def ec2_client(ec2_region_name):
    yield boto3.client("ec2", region_name=ec2_region_name)


@pytest.fixture(autouse=True)
def ec2_client_mock(ec2_client, monkeypatch):
    monkeypatch.setattr(boto3.session.Session,
                        "client",
                        MagicMock(return_value=ec2_client))


@pytest.fixture(autouse=True)
def ec2_stub(ec2_client):
    with Stubber(ec2_client) as stubber:
        yield stubber
        stubber.assert_no_pending_responses()
