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
    return [data_block ^ s_block for data_block, s_block in zip(array.array('B', first), array.array('B', second))]
