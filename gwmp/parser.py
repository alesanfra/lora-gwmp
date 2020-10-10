import csv
import json

from .lorawan_message import LorawanMessage
from .util import waspmote_power_to_dbm


def parse(input_file_name, output_file_name, app_key):
    with open(input_file_name, "r") as input_file:
        rows = input_file.readlines()

    with open(output_file_name, "w") as output_file:

        csvwriter = csv.writer(output_file)
        csvwriter.writerow(
            [
                "Test number",
                "TX power",
                "Spreading Factor",
                "Payload Length",
                "RSSI",
                "LSNR",
            ]
        )

        for row in rows:
            parsed = parse_message(row, app_key)
            if parsed:
                csvwriter.writerow(parsed)


def parse_message(message, app_key):
    payload = json.loads(message)

    for message in payload.get("rxpk", []):

        # skip corrupted packets
        if message["stat"] != 1:
            continue

        try:
            lorawan_message = LorawanMessage.deserialize(
                message["data"], app_key=app_key
            )
            test_n, power, sf, pay_len = extract_test(lorawan_message.payload)
        except Exception as e:
            print("Error: {}".format(str(e)))
            continue

        return (
            str(test_n),
            str(power),
            str(sf),
            str(lorawan_message.original_len),
            str(message["rssi"]),
            str(message["lsnr"]),
        )


def extract_test(message):
    test_n = message[8]
    conf = message[9]
    # cod_rate = conf // 30
    power = waspmote_power_to_dbm(((conf % 30) // 6) + 1)
    sf = 12 - (conf % 6)
    # self.log.info("{}\t4/{}\t\t{}dBm\tsf{}".format(test_n, cod_rate + 5, power, data_rate))
    return test_n, power, sf, len(message)
