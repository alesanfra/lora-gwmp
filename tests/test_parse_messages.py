import pathlib

import pytest

from gwmp.parser import parse, parse_message

APP_KEY = "000102030405060708090A0B0C0D0E0F"


@pytest.fixture
def data_folder():
    return pathlib.Path(__file__).parent / "data"


def test_handler(data_folder):
    parse(data_folder / "received.txt", data_folder / "results.csv", APP_KEY)


def test_parse_message():
    m = (
        '{"rxpk":[{"tmst":114911539,"time":"2015-03-01T20:47:55.316877Z","chan":0,"rfch":1,"freq":868.100000,'
        '"stat":1,"modu":"LORA","datr":"SF7BW125","codr":"4/5","lsnr":9.8,"rssi":-31,"size":23,'
        '"data":"QAMAsqEABAADveh1TF3VY8Lxqn0pjx4="}]}'
    )
    r = parse_message(m, APP_KEY)
    assert r[4] == -31
