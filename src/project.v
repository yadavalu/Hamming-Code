/*
 * Copyright (c) 2024 Your Name
 * SPDX-License-Identifier: Apache-2.0
 */

`default_nettype none

module tt_um_hamming_code_13_8 (
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
  assign uio_oe = 8'b00000011; 
  assign uio_out[7:2] = 6'b0;

  reg [12:0] dwp;
  always @(*) begin
    // Hamming Mapping for 13 bits
    dwp[0] = uio_in[2]; // Overall Parity P0
    dwp[1] = uio_in[3]; // P0001
    dwp[2] = uio_in[4]; // P0010
    dwp[4] = uio_in[5]; // P0100
    dwp[8] = uio_in[6]; // P1000

    dwp[3]     = ui_in[0];
    dwp[7:5]   = ui_in[3:1];
    dwp[12:9]  = ui_in[7:4];
  end

  reg [3:0] syndrome;
  reg overall_parity;
  integer i;

  always @(*) begin
    syndrome = 4'b0;
    overall_parity = dwp[0];
    for (i = 1; i <= 12; i = i + 1) begin
      if (dwp[i]) syndrome = syndrome ^ i[3:0];
      overall_parity = overall_parity ^ dwp[i];
    end
  end

  reg [12:0] corrected;
  always @(*) begin
    corrected = dwp;
    if (overall_parity) begin // SECDED Logic: Odd parity means 1 flip
      if (syndrome == 0) corrected[0] = ~dwp[0];
      else if (syndrome <= 12) corrected[syndrome] = ~dwp[syndrome];
    end
  end

  assign uio_out[1] = (syndrome != 0 && !overall_parity);
  assign uio_out[0] = overall_parity | uio_out[1]; 

  // Map back to outputs
  assign uo_out[0]   = corrected[3];
  assign uo_out[3:1] = corrected[7:5];
  assign uo_out[7:4] = corrected[12:9];

  // List all unused inputs to prevent warnings
  wire _unused = &{ena, clk, rst_n, 1'b0};

endmodule
