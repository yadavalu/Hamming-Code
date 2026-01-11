<!---

This file is used to generate your project datasheet. Please fill in the information below and delete any unused
sections.

You can also include images in this folder and reference them in the markdown. Each image must be less than
512 kb in size, and the combined size of all images must be less than 1 MB.
-->

## How it works

This design is the hardware implementation of the Extended Hamming Code (8, 4) for single-error correcting, double-error detecting (SECDED). Taking in a noisy input of 8-bits, of which 4-bits contain the message, the design outputs the denoised 8-bit message for 1-bit flip errors or outputs the same message if no error or 2-bit flips errors are detected.

### Bit sequence

The following sequence of bits are the input of the project (ui_in)

$$A B C D E F G H$$


| Bit | Meaning |
| --- | --------|
| $A$ | Overall parity |
| $B$ | Parity of D, F, H |
| $C$ | Parity of D, G, H |
| $D$ | 0th bit of message |
| $E$ | Parity of F, G, H |
| $F$ | 1th bit of message |
| $G$ | 2th bit of message |
| $H$ | 3th bit of message |

## How to test

To test the project:

- encode a 4-bit message into 8-bit sequence
- introduce an error by flipping any one bit (or more bits)
- send the perturbed data to the ASIC in the correct [sequence]()
- compare the output with the 8-bit input before the error
- extract the 4-bit message and compare with the original message

If a 1-bit flip error is detected, the single_error_flag (0th input output) pin will be high. If 2-bit flips are detected, both the single_error_flag and double_error_flag (1th input output) pins will be high. Otherwise, if no error is detected, neither flag pins will be high, both will be low.

## External hardware

The two uio flags (single_error_flag and double_error_flag) can be connected to an LED for a visual count of number of errors.
