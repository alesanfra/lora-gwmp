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

import base64
import struct

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher
from cryptography.hazmat.primitives.ciphers.algorithms import AES
from cryptography.hazmat.primitives.ciphers.modes import ECB

from util import key_string_to_bytes, compute_encryption_vector, xor_bytes

JOIN_ACCEPT_DELAY1 = 5000000  # 5 million microseconds (5 seconds)
MAX_TMST = 0x100000000  # 2^32


class LorawanMessage:
    JOIN_REQUEST = 0b000
    JOIN_ACCEPT = 0b001
    UNCONFIRMED_DATA_UP = 0b010
    UNCONFIRMED_DATA_DOWN = 0b011
    CONFIRMED_DATA_UP = 0b100
    CONFIRMED_DATA_DOWN = 0b101
    LORAWAN_VERSION_1 = 0

    def __init__(self,
                 lorawan_type=None,
                 version=None,
                 mic=None,
                 address=None,
                 counter=None,
                 control=None,
                 options=None,
                 port=None,
                 payload=None):

        self.lorawan_type = lorawan_type
        self.version = version
        self.mic = mic
        self.address: str = address
        self.counter: int = counter
        self.control: FrameControl = control  # declared in frame_control field
        self.options: str = options
        self.port: int = port
        self.payload: str = payload

    @classmethod
    def deserialize(cls, data):
        lorawan_type, lorawan_version, mac_layer_payload, mic = cls.__deserialize_mac_layer(data)
        return cls.__deserialize_frame_layer(lorawan_type, lorawan_version, mac_layer_payload, mic)

    @classmethod
    def __deserialize_mac_layer(cls, r_data):
        data = str(r_data)
        data += '=' * (4 - len(data) % 4)  # add padding to be multiple of 4
        # res = base64.urlsafe_b64decode(data)
        res = base64.b64decode(data)
        mac_header = res[0]
        lorawan_type = (mac_header & 0b11100000) >> 5
        lorawan_version = mac_header & 0b00000011
        payload = res[1:len(res) - 4]
        mic = res[len(res) - 4:]
        return lorawan_type, lorawan_version, payload, mic

    @classmethod
    def __deserialize_frame_layer(cls, lorawan_type, version, data, mic):
        dev_address, frame_ctrl, frame_cnt = struct.unpack("<LBH", data[:7])
        frame_ctrl = FrameControl.deserialize(frame_ctrl)
        options = data[7:frame_ctrl.options_len] if frame_ctrl.options_len > 0 else ""

        if len(data[7 + frame_ctrl.options_len:]) > 0:
            port = data[7 + frame_ctrl.options_len]
            payload = data[8 + frame_ctrl.options_len:]
        else:
            port = -1
            payload = ""

        return cls(lorawan_type, version, mic, dev_address, frame_cnt, frame_ctrl, options, port, payload)

    def encrypt(self, key_string):
        data = self.payload
        key = key_string_to_bytes(key_string)

        data += b"\0" * (AES.block_size - len(data) % AES.block_size)  # add padding
        cypher = Cipher(AES(key), ECB(), backend=default_backend()).encryptor()

        vector = compute_encryption_vector(len(data), self.address, self.counter)
        s = cypher.update(vector) + cypher.finalize()

        return xor_bytes(data, s)

    def decrypt(self, key):
        return self.encrypt(key)


class FrameControl:
    def __init__(self, adr=False, adr_ack_req=False, ack=False, options_length=0):
        self.adr = adr
        self.adr_ack_req = adr_ack_req
        self.ack = ack
        self.options_len = options_length

    @classmethod
    def deserialize(cls, frame_ctrl):
        try:
            adr = bool(frame_ctrl & 0b10000000)
            adr_ack_req = bool(frame_ctrl & 0b01000000)
            ack = bool(frame_ctrl & 0b00100000)
            options_length = frame_ctrl & 0b00000111
        except Exception:
            raise TypeError('corrupted frame control field')

        return cls(adr, adr_ack_req, ack, options_length)
