import os

import pytest

import web


@pytest.fixture
def client():
    flaskr.app.config['TESTING'] = True

    with web.app.test_client() as client:
        yield client


def test_none():
    client.get("/")