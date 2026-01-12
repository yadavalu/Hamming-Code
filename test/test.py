# SPDX-FileCopyrightText: © 2024 Tiny Tapeout
# SPDX-License-Identifier: Apache-2.0

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles

from random import randint
from test.utils import calculate_msg


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


async def test_random_msg_1_bit_flip(dut, err=randint(0, 12)):
    await reset(dut)

    msg_val = randint(0, 255)
    data_in_bits = [int(b) for b in format(msg_val, '08b')[::-1]] # LSB first
    full_code = calculate_msg(data_in_bits)

    noised = full_code.copy()
    noised[err] ^= 1

    # Format for Pins
    # ui_in gets data bits from indices: 3, 5, 6, 7, 9, 10, 11, 12
    ui_val = sum(noised[idx] << i for i, idx in enumerate([3, 5, 6, 7, 9, 10, 11, 12]))
    # uio_in[6:2] gets parity bits from indices: 0, 1, 2, 4, 8
    uio_val = sum(noised[idx] << i for i, idx in enumerate([0, 1, 2, 4, 8])) << 2  # bitshift to ignore flags

    dut._log.info(f"Testing message: {msg_val}, full code: {full_code}, noised: {noised}")
    dut._log.info(f"Input: {ui_val}, {uio_val}")

    dut.ui_in.value = ui_val
    dut.uio_in.value = uio_val

    await ClockCycles(dut.clk, 2)

    dut._log.info(f"Output: {dut.uo_out.value}, {dut.uio_out.value}")

    assert dut.uo_out.value == msg_val, f"Expected corrected output to be {msg_val}, but got {dut.uo_out.value}"
    flag_str = str(dut.uio_out.value)
    flag = int(flag_str[-2:], 2)
    assert flag == 1, f"Expected single error flag to be high and double error flag to be low, but got {flag}"
    

async def test_random_msg_2_bit_flip(dut):
    await reset(dut)

    msg_val = randint(0, 255)
    data_in_bits = [int(b) for b in format(msg_val, '08b')[::-1]] # LSB first
    full_code = calculate_msg(data_in_bits)

    noised = full_code.copy()
    err1 = randint(0, 12)
    err2 = random_exclude(0, 12, [err1])
    noised[err1] ^= 1
    noised[err2] ^= 1

    # Format for Pins
    # ui_in gets data bits from indices: 3, 5, 6, 7, 9, 10, 11, 12
    ui_val = sum(noised[idx] << i for i, idx in enumerate([3, 5, 6, 7, 9, 10, 11, 12]))
    # uio_in[6:2] gets parity bits from indices: 0, 1, 2, 4, 8
    uio_val = sum(noised[idx] << i for i, idx in enumerate([0, 1, 2, 4, 8])) << 2  # bitshift to ignore flags

    dut._log.info(f"Testing message: {msg_val}, full code: {full_code}, noised: {noised}")
    dut._log.info(f"Input: {ui_val}, {uio_val}")

    dut.ui_in.value = ui_val
    dut.uio_in.value = uio_val

    await ClockCycles(dut.clk, 2)

    dut._log.info(f"Output: {dut.uo_out.value}, {dut.uio_out.value}")

    assert dut.uo_out.value == ui_val, f"Expected uncorrected output to be {ui_val}, but got {dut.uo_out.value}"
    flag_str = str(dut.uio_out.value)
    flag = int(flag_str[-2:], 2)
    assert flag == 3, f"Expected single error flag and double error flag to be high, but got {flag}"


async def test_random_msg_0_bit_flip(dut):
    await reset(dut)

    msg_val = randint(0, 255)
    data_in_bits = [int(b) for b in format(msg_val, '08b')[::-1]] # LSB first
    full_code = calculate_msg(data_in_bits)

    # Format for Pins
    # ui_in gets data bits from indices: 3, 5, 6, 7, 9, 10, 11, 12
    ui_val = sum(full_code[idx] << i for i, idx in enumerate([3, 5, 6, 7, 9, 10, 11, 12]))
    # uio_in[6:2] gets parity bits from indices: 0, 1, 2, 4, 8
    uio_val = sum(full_code[idx] << i for i, idx in enumerate([0, 1, 2, 4, 8])) << 2  # bitshift to ignore flags
    dut._log.info(f"Testing message: {msg_val}, full code: {full_code}")
    dut._log.info(f"Input: {ui_val}, {uio_val}")

    dut.ui_in.value = ui_val
    dut.uio_in.value = uio_val

    await ClockCycles(dut.clk, 2)

    dut._log.info(f"Output: {dut.uo_out.value}, {dut.uio_out.value}")

    assert dut.uo_out.value == msg_val, f"Expected corrected output to be {msg_val}, but got {dut.uo_out.value}"
    flag_str = str(dut.uio_out.value)
    flag = int(flag_str[-2:], 2)
    assert flag == 0, f"Expected single error flag and double error flag to be low, but got {flag}"
    
async def reset(dut):
    dut._log.info("Reset")
    dut.ena.value = 1
    dut.ui_in.value = 0
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

def random_exclude(range_start, range_end, excludes):
    r = randint(range_start, range_end)
    while r in excludes:
        r = randint(range_start, range_end)
    return r

