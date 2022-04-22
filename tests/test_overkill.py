#!/usr/bin/env python

"""Tests for `overkill` package."""

import random
import time
from threading import Thread

import pytest
from click.testing import CliRunner

from overkill import cli, overkill
from overkill.servers._server_exceptions import NoWorkersError, WorkError
from overkill.servers._server_messaging_standards import DISTRIBUTE
from overkill.servers.master import Master
from overkill.servers.worker import Worker
from tests.utils import MockMaster


@pytest.fixture
def response():
    """Sample pytest fixture.

    See more at: http://doc.pytest.org/en/latest/fixture.html
    """
    # import requests
    # return requests.get('https://github.com/audreyr/cookiecutter-pypackage')


@pytest.mark.skip()
def test_content(response):
    """Sample pytest test function with the pytest fixture as an argument."""
    # from bs4 import BeautifulSoup
    # assert 'GitHub' in BeautifulSoup(response.content).title.string


@pytest.mark.skip()
def test_command_line_interface():
    """Test the CLI."""
    runner = CliRunner()
    result = runner.invoke(cli.main)
    assert result.exit_code == 0
    assert 'overkill.cli.main' in result.output
    help_result = runner.invoke(cli.main, ['--help'])
    assert help_result.exit_code == 0
    assert '--help  Show this message and exit.' in help_result.output


def test_map():
    """Test map function of CC class"""
    HOST = "127.0.0.1"
    PORT = random.randint(1024, 65534)

    m = MockMaster(HOST, PORT)
    cc = overkill.ClusterCompute(1, (HOST, PORT))

    t = Thread(target=m.recieve_connection, daemon=True)
    t.start()
    cc.map("foo", "bar")
    t.join()

    assert m.recieved["type"] == DISTRIBUTE


def test_work_error():
    """Test should raise a WorkError since the user has mispspecified the function for map"""
    m = Master()
    m.start()

    HOST = "127.0.0.1"  # Standard loopback interface address (localhost)
    PORT = random.randint(1024, 65534)

    w = Worker("test")
    w.start()
    w.connect_to_master(*m.get_address())

    # ensure master finishes processing worker before
    # accepting user's request
    time.sleep(0.5)

    cc = overkill.ClusterCompute(1, m.get_address())
    with pytest.raises(WorkError):
        cc.map("foo", [1, 2, 3])

    m.stop()


def test_no_workers_error():
    """Test should raise a NoWorkersError since user requested work before any workers were created"""
    m = Master()
    m.start()

    cc = overkill.ClusterCompute(1, m.get_address())
    with pytest.raises(NoWorkersError):
        cc.map("foo", "bar")

    m.stop()
