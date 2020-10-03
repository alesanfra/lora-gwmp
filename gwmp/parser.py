import json
import logging

from .lorawan_message import LorawanMessage
from .util import convert_power


class GatewayMessageHandler:
    def __init__(self, app_key, log=None):
        self.app_key = app_key
        self.log = log or logging.getLogger(__name__)

    def parse(self, input_file_name, output_file_name):

        with open(input_file_name, "r") as input_file:
            rows = input_file.readlines()

        with open(output_file_name, "wb") as output_file:
            for row in rows:
                parsed = self.parse_row(row)
                # FIXME: replace with csv.writer
                if parsed:
                    output_file.write(
                        bytes("{},{},{},{},{},{}\n".format(*parsed), encoding="ascii")
                    )
                    self.log.info("{},{},{},{},{},{}".format(*parsed))

    def parse_row(self, message):
        payload = json.loads(message)

        for message in payload.get("rxpk", []):

            # skip corrupted packets
            if message["stat"] != 1:
                continue

            try:
                lorawan_message = LorawanMessage.deserialize(message["data"])
                decrypted = lorawan_message.decrypt(self.app_key)
                test_n, power, sf, pay_len = self.extract_test(decrypted)
            except Exception as e:
                self.log.error("Error: {}".format(str(e)))
                continue

            return (
                str(test_n),
                str(power),
                str(sf),
                str(len(lorawan_message.payload)),
                str(message["rssi"]),
                str(message["lsnr"]),
            )

    @staticmethod
    def extract_test(message):
        test_n = message[8]
        conf = message[9]
        # cod_rate = conf // 30
        power = convert_power(((conf % 30) // 6) + 1)
        sf = 12 - (conf % 6)
        # self.log.info("{}\t4/{}\t\t{}dBm\tsf{}".format(test_n, cod_rate + 5, power, data_rate))
        return test_n, power, sf, len(message)
