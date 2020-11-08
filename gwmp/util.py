import array
import struct

from cryptography.hazmat.primitives.ciphers.algorithms import AES


def key_string_to_bytes(key_string):
    num = int(key_string, 16)
    return struct.pack(">QQ", num >> 64, num & 0xFFFFFFFFFFFFFFFF)


def compute_encryption_vector(data_length, address, counter):
    vector = bytes(0)
    for i in range(data_length // AES.block_size):
        vector += struct.pack("<BLBLLBB", 0x01, 0x00, 0x00, address, counter, 0, i + 1)
    return vector


def xor_bytes(first, second):
    return [
        data_block ^ s_block
        for data_block, s_block in zip(
            array.array("B", first), array.array("B", second)
        )
    ]


def waspmote_power_to_dbm(power_index):
    """Convert Libelium Waspmote power index to dBm"""
    return 17 - (3 * power_index)
