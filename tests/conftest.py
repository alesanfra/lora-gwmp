import pathlib

import pytest


@pytest.fixture
def data_folder():
    return pathlib.Path(__file__).parent / "data"
