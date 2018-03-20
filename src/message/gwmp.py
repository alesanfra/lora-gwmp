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

import struct

GWMP_MESSAGE_FORMAT = ">BHB"
GATEWAY_ADDRESS_FORMAT = ">Q"


class GWMPMessage:
    # GWMP message types
    PUSH_DATA = 0x00
    PUSH_ACK = 0x01
    PULL_DATA = 0x02
    PULL_ACK = 0x04
    PULL_RESP = 0x03
    TX_ACK = 0x05

    def __init__(self, version, token, type, gateway, payload):
        self.version = version
        self.token = token
        self.type = type
        self.gateway = gateway
        self.payload = payload

    @classmethod
    def from_gateway_message(cls, data):
        """Build GWMP message"""
        size = struct.calcsize(GWMP_MESSAGE_FORMAT)
        version, token, gwmp_type = struct.unpack(GWMP_MESSAGE_FORMAT, data[:size])
        if gwmp_type in (cls.TX_ACK, cls.PULL_RESP, cls.PULL_ACK):
            gateway = 0
        else:
            gateway = struct.unpack(GATEWAY_ADDRESS_FORMAT, data[size:size + 8])[0]
        payload = data[size + 8:]
        return cls(version, token, gwmp_type, gateway, payload)

    def get_gateway(self):
        return str(hex(self.gateway))
