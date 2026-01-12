<!---

This file is used to generate your project datasheet. Please fill in the information below and delete any unused
sections.

You can also include images in this folder and reference them in the markdown. Each image must be less than
512 kb in size, and the combined size of all images must be less than 1 MB.
-->

## How it works

This design is the hardware implementation of the Extended Hamming Code (13, 8) for single-error correcting, double-error detecting (SECDED). Taking in a noisy input of 13-bits, of which 8-bits contain the message, the design outputs the denoised 8-bit message for 1-bit flip errors or outputs the same message if no error or 2-bit flips errors are detected.

### Bit sequence

The following sequence of bits are the input of the project (ui_in)

$$A B C D E F G H I J K L M$$


| Bit | Meaning |
| --- | --------|
| $A$ | Overall parity |
| $B$ | Parity of 0001 (D, F, H, J, L) |
| $C$ | Parity of 0010 (D, G, H, K, L) |
| $D$ | 0th bit of message |
| $E$ | Parity of 0100 (F, G, H, M) |
| $F$ | 1th bit of message |
| $G$ | 2th bit of message |
| $H$ | 3th bit of message |
| $I$ | Parity of 1000 (J, K, L, M) |
| $J$ | 4th bit of message |
| $K$ | 5th bit of message |
| $L$ | 6th bit of message |
| $M$ | 7th bit of message |

## How to test

To test the project:

- encode a 8-bit message into the 13-bit sequence (use [test/utils.py](../test/utils.py))
- introduce an error by flipping any one bit (or more bits)
- send the perturbed data to the ASIC in the correct by sending the message bits as input and parity bits to 2nd-6th input-output (refer to pinout)
- compare the output with the 8-bit message before the error

If a 1-bit flip error is detected, the single_error_flag (0th input-output) pin will be high. If 2-bit flips are detected, both the single_error_flag and double_error_flag (1th input-output) pins will be high. Otherwise, if no error is detected, neither flag pins will be high, both will be low.

## External hardware

The two uio flags (single_error_flag and double_error_flag) can be connected to an LED for a visual count of number of errors.
