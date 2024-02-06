`timescale 1ns/1ps
`default_nettype none

/*
Written for the FT2232HQ on the CMod A7 board.
- UART Interface supports 7/8 bit data, 1/2 stop bits, and Odd/Even/Mark/Space/No Parity.
- defaulting to 8N1.
- See FTDI AN 120 Aliasing VCP Baud Rates for details, but salient points for valid baudrates.
  - links should be within 3% of the spec'd clock
  - #Mhz basedivided by n + (0.125, 0.25, 0.375, 0.625, 0.5, 0.75, 0.875)
  - TL;DR a few clock cycles won't matter too much if clk > 3*BAUDRATE.
  TODO(avinash)
    - fix ready/valid to be axi4-lite compliant.
*/

module uart_driver(
  clk, rst,
  rx_data, rx_valid,
  tx_data, tx_valid, tx_ready,
  uart_tx, uart_rx
);


// These are set for the CMod A7, modify for different clocks/baudrates!
parameter CLK_HZ = 12_000_000;
parameter BAUDRATE = 115200;
// Depth of synchronizer (measure of MTBF).
parameter SYNC_DEPTH = 3;
// A derived parameter.
localparam OVERSAMPLE = CLK_HZ/BAUDRATE;


// 8N1 - probably shouldn't change this.
parameter DATA_BITS = 8;
parameter PARITY = 0;
parameter STOP_BITS = 1;

input wire clk, rst;
input wire uart_rx;
output logic uart_tx;

input wire [DATA_BITS-1:0] tx_data;
output logic [DATA_BITS-1:0] rx_data;
input wire tx_valid;
output logic rx_valid, tx_ready;

logic [SYNC_DEPTH-1:0] input_buffer;
logic uart_rx_synced;
always_comb uart_rx_synced = input_buffer[SYNC_DEPTH-1];
always_ff@(posedge clk) begin : input_synchronizer
  if(rst) begin
    input_buffer <= -1;
  end else begin
    input_buffer[0] <= uart_rx;
    input_buffer[SYNC_DEPTH-1:1] <= input_buffer[SYNC_DEPTH-2:0];
  end
end

enum logic [1:0] {
  S_IDLE = 0,
  S_START,
  S_DATA,
  S_STOP
} tx_state, rx_state;


endmodule