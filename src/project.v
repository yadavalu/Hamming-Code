/*
 * Copyright (c) 2024 Your Name
 * SPDX-License-Identifier: Apache-2.0
 */

`default_nettype none

module tt_um_hamming_code_8_4 (
    input  wire [7:0] ui_in,    // Dedicated inputs
    output wire [7:0] uo_out,   // Dedicated outputs
    input  wire [7:0] uio_in,   // IOs: Input path
    output wire [7:0] uio_out,  // IOs: Output path
    output wire [7:0] uio_oe,   // IOs: Enable path (active high: 0=input, 1=output)
    input  wire       ena,      // always 1 when the design is powered, so you can ignore it
    input  wire       clk,      // clock
    input  wire       rst_n     // reset_n - low to reset
);

  // Tie off unused pins
  assign uio_out[7:2] = 6'b0;
  assign uio_oe[7:2]  = 6'b0;

  reg [2:0] syndrome;
  integer i;

  // Analyse syndrome with XORs
  always @(*) begin
    syndrome = 3'b000;
    for (i = 0; i <= 7; i = i + 1) begin
      if (ui_in[i]) begin
        syndrome = syndrome ^ i[2:0];
      end
    end
  end

  // Check overall parity to identify 0th bit flip or possible double bit error
  reg overall_parity;
  integer j;

  always @(*) begin
    overall_parity = ui_in[0];
    for (j = 1; j <= 7; j = j + 1) begin
        overall_parity = overall_parity ^ ui_in[j];
    end
  end

  // Error detection flag
  wire single_error, double_error;
  assign single_error = overall_parity == 1'b1;
  assign double_error = (syndrome != 3'b000) && (overall_parity == 1'b0);

  assign uio_oe[0]  = 1'b1;
  assign uio_out[0] = single_error | double_error;
  assign uio_oe[1]  = 1'b1;
  assign uio_out[1] = double_error;
  

  // Correct data
  reg [7:0] corrected_data;

  always @(*) begin
    corrected_data = ui_in;
    if (overall_parity == 1'b1) begin
      if (syndrome == 3'b000)
        corrected_data[0] = ~ui_in[0];
      else
        corrected_data[syndrome] = ~ui_in[syndrome];
    end
  end

  assign uo_out = corrected_data;

  // List all unused inputs to prevent warnings
  wire _unused = &{ena, clk, rst_n, uio_in, 1'b0};

endmodule
