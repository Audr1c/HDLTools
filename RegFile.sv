// Mock Register File module for verification
module RegFile (
    input  logic [31:0] in,
    input  logic [4:0]  rd,
    input  logic [4:0]  rs1,
    input  logic [4:0]  rs2,
    input  logic        RegWrite,
    input  logic        clk,
    input  logic        rst,
    output logic [31:0] out1,
    output logic [31:0] out2
);
    // sequential regfile representation
    logic [31:0] registers [31:0];
    assign out1 = registers[rs1];
    assign out2 = registers[rs2];
    
    always_ff @(posedge clk) begin
        if (rst) begin
            for (int i = 0; i < 32; i++) registers[i] <= 32'd0;
        end else if (RegWrite && rd != 5'd0) begin
            registers[rd] <= in;
        end
    end
endmodule
