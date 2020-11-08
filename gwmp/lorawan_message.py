import base64
import struct
from enum import IntEnum

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher
from cryptography.hazmat.primitives.ciphers.algorithms import AES
from cryptography.hazmat.primitives.ciphers.modes import ECB

from .util import compute_encryption_vector, key_string_to_bytes, xor_bytes

JOIN_ACCEPT_DELAY1 = 5 * 1000 * 1000  # microseconds


class FrameControl:
    def __init__(
        self,
        adr: bool = False,
        adr_ack_req: bool = False,
        ack: bool = False,
        options_len: int = 0,
    ):
        self.adr = adr
        self.adr_ack_req = adr_ack_req
        self.ack = ack
        self.options_len = options_len

    @classmethod
    def loads(cls, frame_ctrl: int):
        try:
            adr = bool(frame_ctrl & 0b10000000)
            adr_ack_req = bool(frame_ctrl & 0b01000000)
            ack = bool(frame_ctrl & 0b00100000)
            options_length = frame_ctrl & 0b00000111
        except Exception:
            raise TypeError("Corrupted frame control field")

        return cls(adr, adr_ack_req, ack, options_length)


class LorawanType(IntEnum):
    JOIN_REQUEST = 0b000
    JOIN_ACCEPT = 0b001
    UNCONFIRMED_DATA_UP = 0b010
    UNCONFIRMED_DATA_DOWN = 0b011
    CONFIRMED_DATA_UP = 0b100
    CONFIRMED_DATA_DOWN = 0b101


class LorawanMessage:
    LORAWAN_VERSION_1 = 0

    def __init__(
        self,
        lorawan_type: int,
        version: int,
        mic,
        address: str,
        counter: int,
        control: FrameControl,
        options: str,
        port: int,
        payload: str,
    ):
        self.lorawan_type: int = lorawan_type
        self.version: int = version
        self.mic = mic
        self.address: str = address
        self.counter: int = counter
        self.control: FrameControl = control  # declared in frame_control field
        self.options: str = options
        self.port: int = port
        self.payload: str = payload
        self.original_len: int = len(payload)

    @classmethod
    def deserialize(cls, data, app_key=None):
        (
            lorawan_type,
            lorawan_version,
            mac_layer_payload,
            mic,
        ) = cls.__deserialize_mac_layer(data)
        (
            dev_address,
            frame_cnt,
            frame_ctrl,
            options,
            port,
            payload,
        ) = cls.__deserialize_frame_layer(mac_layer_payload)

        message = cls(
            lorawan_type,
            lorawan_version,
            mic,
            dev_address,
            frame_cnt,
            frame_ctrl,
            options,
            port,
            payload,
        )

        if app_key is not None:
            # serialize / deserialize payload
            message.payload = message.encrypt(app_key)

        return message

    @staticmethod
    def __deserialize_mac_layer(r_data):
        data = str(r_data)
        data += "=" * (4 - len(data) % 4)  # add padding to be multiple of 4
        # res = base64.urlsafe_b64decode(data)
        res = base64.b64decode(data)
        mac_header = res[0]
        lorawan_type = (mac_header & 0b11100000) >> 5
        lorawan_version = mac_header & 0b00000011
        payload = res[1 : len(res) - 4]
        mic = res[len(res) - 4 :]
        return lorawan_type, lorawan_version, payload, mic

    @staticmethod
    def __deserialize_frame_layer(data):
        dev_address, frame_ctrl, frame_cnt = struct.unpack("<LBH", data[:7])
        frame_ctrl = FrameControl.loads(frame_ctrl)
        options = data[7 : frame_ctrl.options_len] if frame_ctrl.options_len > 0 else ""

        if len(data[7 + frame_ctrl.options_len :]) > 0:
            port = data[7 + frame_ctrl.options_len]
            payload = data[8 + frame_ctrl.options_len :]
        else:
            port = -1
            payload = ""

        return (
            dev_address,
            frame_cnt,
            frame_ctrl,
            options,
            port,
            payload,
        )

    def encrypt(self, key_string):
        data = self.payload
        key = key_string_to_bytes(key_string)

        data += b"\0" * (AES.block_size - len(data) % AES.block_size)  # add padding
        cypher = Cipher(AES(key), ECB(), backend=default_backend()).encryptor()

        vector = compute_encryption_vector(len(data), self.address, self.counter)
        s = cypher.update(vector) + cypher.finalize()

        return xor_bytes(data, s)

    def decrypt(self, key_string):
        """Decryption is symmetrical to encryption"""
        return self.encrypt(key_string)
