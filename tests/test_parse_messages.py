from gwmp import parse, parse_message

APP_KEY = "000102030405060708090A0B0C0D0E0F"


def test_handler(data_folder, tmp_path):
    parse(data_folder / "received.txt", tmp_path / "results.csv", APP_KEY)


def test_parse_message():
    m = (
        '{"rxpk":[{"tmst":114911539,"time":"2015-03-01T20:47:55.316877Z","chan":0,"rfch":1,"freq":868.100000,'
        '"stat":1,"modu":"LORA","datr":"SF7BW125","codr":"4/5","lsnr":9.8,"rssi":-31,"size":23,'
        '"data":"QAMAsqEABAADveh1TF3VY8Lxqn0pjx4="}]}'
    )
    r = parse_message(m, APP_KEY)
    assert r[4] == "-31"
