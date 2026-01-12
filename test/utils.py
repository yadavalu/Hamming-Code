from functools import reduce


def calculate_msg(data_8_bit):
    c = [0] * 13
    # Place data in positions 3, 5, 6, 7, 9, 10, 11, 12
    c[3] = data_8_bit[0]
    c[5], c[6], c[7] = data_8_bit[1], data_8_bit[2], data_8_bit[3]
    c[9], c[10], c[11], c[12] = data_8_bit[4], data_8_bit[5], data_8_bit[6], data_8_bit[7]

    c[1] = c[3] ^ c[5] ^ c[7] ^ c[9] ^ c[11]  # P0001
    c[2] = c[3] ^ c[6] ^ c[7] ^ c[10] ^ c[11]  # P0010
    c[4] = c[5] ^ c[6] ^ c[7] ^ c[12]  # P0100  
    c[8] = c[9] ^ c[10] ^ c[11] ^ c[12]  # P1000

    # Overall Parity (P0)
    c[0] = reduce(lambda x, y: x ^ y, c[1:])
    
    return c

def get_msg(num):
    bit_str = get_8_bit_bin_list(num)
    return [bit_str[3]] + bit_str[5:]

def get_8_bit_bin_list(value):
    return [int(bit) for bit in format(value, '08b')]

def get_dec(bin_list):
    return sum(bit * (1 << idx) for idx, bit in enumerate(reversed(bin_list)))
