// Mock ALU module for verification
module alu (
    input  logic [31:0] in1,
    input  logic [31:0] in2,
    input  logic [3:0]  alu_ctrl,
    output logic [31:0] out,
    output logic        zero
);
    // combinatorial assignment example
    assign out = (alu_ctrl == 4'd0) ? (in1 + in2) : 32'd0;
    assign zero = (out == 32'd0);
endmodule
