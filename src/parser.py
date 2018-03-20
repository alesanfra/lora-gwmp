"""
This file is part of LoraParser.

LoraParser is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

LoraParser is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with LoraParser. If not, see <http://www.gnu.org/licenses/>.
"""

import json
import logging
import re

from message.lorawan import LorawanMessage

BASE_PATH = "../data/"
APP_KEY = "000102030405060708090A0B0C0D0E0F"


def sf(data_rate):
    return re.findall(r"SF\d{1,2}", data_rate)[0]


def convert_power(power_index):
    """Convert wapmote power index to dBm"""
    return 17 - (3 * power_index)


class Packet:
    def __init__(self, dist, sf, payload_len, rssi, lsnr, freq, cod_rate, payload):
        self.cod_rate = cod_rate
        self.freq = freq
        self.lsnr = lsnr
        self.rssi = rssi
        self.payload_len = payload_len
        self.sf = sf
        self.dist = dist
        self.payload = payload

    @classmethod
    def from_gateway_message(cls, dist, msg, lorawan_message, payload):
        return cls(dist=dist,
                   sf=sf(msg['datr']),
                   payload_len=len(lorawan_message.payload),
                   rssi=msg['rssi'],
                   lsnr=msg['lsnr'],
                   freq=msg['freq'],
                   cod_rate=msg['codr'],
                   payload=payload)

    def row(self):
        # TODO: modificare questa funzione per ottenere il formato csv corretto
        return self.dist, self.sf, self.payload_len, self.rssi, self.lsnr, self.cod_rate, self.payload


class GatewayMessageHandler:
    def __init__(self, log, devices):
        self.log = log
        self.devices = devices

    def parse(self, file_name):
        with open(file_name, 'r') as f:
            self.log.info("Opened file {}".format(file_name))

            for row in f.readlines():
                self.parse_row(row)

    def parse_row(self, message):
        payload = json.loads(message)

        for message in payload.get("rxpk", []):
            # self.log.info(str(message))
            if message['stat'] != 1:
                continue

            try:
                lorawan_message = LorawanMessage.deserialize(message['data'])

                # self.log.info(lorawan_message.__dict__)

                # self.log.info("Handle message {}".format(str(lorawan_message.payload)))
                decrypted = lorawan_message.decrypt(APP_KEY)
                # self.log.info("Decrypted {}".format(decrypted))
                test = self.log_test(decrypted)
            except Exception as e:
                self.log.error("Error: {}".format(str(e)))
                continue

            self.log.info(Packet.from_gateway_message('boh', message, lorawan_message, test).row())

    def log_test(self, message):
        test_n = message[8]
        conf = message[9]
        cod_rate = conf // 30
        power = convert_power(((conf % 30) // 6) + 1)
        data_rate = 12 - (conf % 6)
        self.log.info("{}\t4/{}\t\t{}dBm\tsf{}".format(test_n, cod_rate + 5, power, data_rate))
        return "{},4/{},{}dBm,sf{}".format(test_n, cod_rate + 5, power, data_rate)


if __name__ == "__main__":
    logging.basicConfig(format='%(message)s', level=logging.INFO)
    handler = GatewayMessageHandler(logging.getLogger('LoraParser'), [])
    handler.parse(BASE_PATH + "received.txt")
