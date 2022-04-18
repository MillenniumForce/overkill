#!/usr/bin/env python

"""Tests for `overkill` package."""

import random
from threading import Thread
import pytest

from click.testing import CliRunner

from overkill import overkill
from overkill import cli
from overkill.utils import server_messaging_standards
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
    HOST = "127.0.0.1"
    PORT = random.randint(1024, 65534)

    m = MockMaster(HOST, PORT)
    cc = overkill.ClusterCompute(1, (HOST, PORT))

    t = Thread(target=m.recieve_connection, daemon=True)
    t.start()
    cc.map("foo", "bar")
    t.join()

    assert m.recieved["type"] == server_messaging_standards._DISTRIBUTE
