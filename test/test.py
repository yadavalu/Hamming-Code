# SPDX-FileCopyrightText: © 2024 Tiny Tapeout
# SPDX-License-Identifier: Apache-2.0

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles

from random import randint


@cocotb.test()
async def test_project(dut):
    dut._log.info("Start")

    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, unit="us")
    cocotb.start_soon(clock.start())

    # Reset
    await reset(dut)

    dut._log.info("Test project behavior")

    for _ in range(20):
        await test_random_msg_1_bit_flip(dut)
    
    # Test MSB (overall parity bit) and LSB flips
    dut._log.info("Test boundaries")
    await test_random_msg_1_bit_flip(dut, err=0)  # overall parity bit
    await test_random_msg_1_bit_flip(dut, err=7)

    # Stress test: double bit flips (should not be corrected)
    dut._log.info("Stress test: 2 bit flips")
    await test_random_msg_2_bit_flip(dut)
    dut._log.info("Stress test: 0 bit flips")
    await test_random_msg_0_bit_flip(dut)



def calculate_parity(msg):
    parity_001 = msg[0] ^ msg[1] ^ msg[3]
    parity_010 = msg[0] ^ msg[2] ^ msg[3]
    parity_100 = msg[1] ^ msg[2] ^ msg[3]

    overall_parity = parity_001 ^ parity_010 ^ parity_100 ^ msg[0] ^ msg[1] ^ msg[2] ^ msg[3]
    
    return [overall_parity, parity_001, parity_010] + [msg[0]] + [parity_100] + msg[1:]

def get_msg(num):
    bit_str = get_8_bit_bin_list(num)
    return [bit_str[3]] + bit_str[5:]

def get_4_bit_bin_list(value):
    return [int(bit) for bit in format(value, '04b')]

def get_8_bit_bin_list(value):
    return [int(bit) for bit in format(value, '08b')]

def get_dec(bin_list):
    return sum(bit * (1 << idx) for idx, bit in enumerate(reversed(bin_list)))

async def test_random_msg_1_bit_flip(dut, err=randint(0, 7)):
    await reset(dut)

    msg = randint(0, 15)
    parity_bits = calculate_parity(get_4_bit_bin_list(msg))

    expected_msg = get_dec(parity_bits)

    dut._log.info(f"Random message: {msg}, bit string: {parity_bits} = {expected_msg}")
    
    # Introduce a single-bit error at a random position
    noised_parity_bits = parity_bits.copy()
    noised_parity_bits[err] ^= 1
    noised_msg = get_dec(noised_parity_bits) 
    dut._log.info(f"Noised bit string: {noised_parity_bits} = {noised_msg}")


    dut.ui_in.value = noised_msg

    await ClockCycles(dut.clk, 1)

    assert dut.uo_out.value == expected_msg, f"Expected uo_out to be {expected_msg} for {noised_msg=}, but got {dut.uo_out.value=}"
    assert dut.uio_out.value == 1, f"Expected single error flag to be high and double error flag to be low"

    dut._log.info(f"Successfully sent {noised_msg=}, received {dut.uo_out.value=}, expected {expected_msg=}. Decoded {get_msg(msg)} from {msg=}")

async def test_random_msg_2_bit_flip(dut):
    await reset(dut)

    msg = randint(0, 15)
    parity_bits = calculate_parity(get_4_bit_bin_list(msg))

    dut._log.info(f"Random message: {msg}, bit string: {parity_bits}")
    
    # Introduce a single-bit error at a random position
    noised_parity_bits = parity_bits.copy()
    err1 = randint(0, 7)
    err2 = randint(0, 7)
    noised_parity_bits[err1] ^= 1
    noised_parity_bits[err2] ^= 1
    noised_msg = get_dec(noised_parity_bits) 
    dut._log.info(f"Noised bit string: {noised_parity_bits} = {noised_msg}")



    dut.ui_in.value = noised_msg

    await ClockCycles(dut.clk, 1)

    assert dut.uo_out.value == noised_msg, f"Expected uo_out to be {noised_msg}, but got {dut.uo_out.value=}"
    assert dut.uio_out.value == 3, f"Expected single error flag and double error flag to be high"

    dut._log.info(f"Successfully received back noised bit string {dut.uo_out.value=}, expected {noised_msg=}")

async def test_random_msg_0_bit_flip(dut):
    await reset(dut)

    msg = randint(0, 15)
    parity_bits = calculate_parity(get_4_bit_bin_list(msg))

    expected_msg = get_dec(parity_bits)

    dut._log.info(f"Random message: {msg}, bit string: {parity_bits}")
    
    dut.ui_in.value = expected_msg

    await ClockCycles(dut.clk, 1)

    assert dut.uo_out.value == expected_msg, f"Expected uo_out to be {expected_msg}, but got {dut.uo_out.value=}"
    assert dut.uio_out.value == 0, f"Expected single error flag and double error flag to be low"
    
    dut._log.info(f"Successfully received back input bit string {dut.uo_out.value=}, expected {expected_msg=}. 0-errors detected.")


async def reset(dut):
    dut._log.info("Reset")
    dut.ena.value = 1
    dut.ui_in.value = 0
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

