import struct
from enum import IntEnum

GWMP_MESSAGE_FORMAT = ">BHB"
GATEWAY_ADDRESS_FORMAT = ">Q"


class GatewayMessageType(IntEnum):
    PUSH_DATA = 0x00
    PUSH_ACK = 0x01
    PULL_DATA = 0x02
    PULL_ACK = 0x04
    PULL_RESP = 0x03
    TX_ACK = 0x05


class GatewayMessage:
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
        if gwmp_type in (
            GatewayMessageType.TX_ACK,
            GatewayMessageType.PULL_RESP,
            GatewayMessageType.PULL_ACK,
        ):
            gateway = 0
        else:
            gateway = struct.unpack(GATEWAY_ADDRESS_FORMAT, data[size : size + 8])[0]
        payload = data[size + 8 :]
        return cls(version, token, gwmp_type, gateway, payload)
