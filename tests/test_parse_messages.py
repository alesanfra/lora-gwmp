import pathlib

import pytest

from gwmp.parser import GatewayMessageHandler

APP_KEY = "000102030405060708090A0B0C0D0E0F"


@pytest.fixture
def data_folder():
    return pathlib.Path(__file__).parent / "data"


def test_handler(data_folder):

    handler = GatewayMessageHandler(APP_KEY)
    handler.parse(data_folder / "received.txt", data_folder / "results.csv")
