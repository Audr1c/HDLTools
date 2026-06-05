`define CLR_RESET  "\033[0m"
`define CLR_RED    "\033[1;31m"
`define CLR_GREEN  "\033[1;32m"
`define CLR_YELLOW "\033[1;33m"
`define CLR_BLUE   "\033[1;34m"

`define PERIOD 10

`timescale 1ns / 1ps
string formatted_msg_RegFile;

module RegFile_tb;

    int errors = 0;
    int tests_run = 0;

    // ----------------------------------------------------------------------
    // Signals
    // ----------------------------------------------------------------------
    logic  [31:0] in;
    logic  [4:0] rd;
    logic  [4:0] rs1;
    logic  [4:0] rs2;
    logic RegWrite;
    logic clk = 0;
    logic rst;
    logic  [31:0] out1;
    logic  [31:0] out2;

    always
        #(`PERIOD/2) clk = ~clk;

    // ----------------------------------------------------------------------
    // DUT Instantiation
    // ----------------------------------------------------------------------
    RegFile dut (
        .in       (in),
        .rd       (rd),
        .rs1      (rs1),
        .rs2      (rs2),
        .RegWrite (RegWrite),
        .clk      (clk),
        .rst      (rst),
        .out1     (out1),
        .out2     (out2)
    );

    // ----------------------------------------------------------------------
    // Verification Task
    // ----------------------------------------------------------------------
    task verification_RegFile(
        input  logic [31:0] in_test,
        input  logic [4:0] rd_test,
        input  logic [4:0] rs1_test,
        input  logic [4:0] rs2_test,
        input  logic RegWrite_test,
        input  logic rst_test,
        input  logic [31:0] out1_expect,
        input  logic [31:0] out2_expect
    );
        begin
            tests_run++;

            // Apply inputs
            in = in_test;
            rd = rd_test;
            rs1 = rs1_test;
            rs2 = rs2_test;
            RegWrite = RegWrite_test;
            rst = rst_test;
            #(`PERIOD);

            if (out1 !== out1_expect || out2 !== out2_expect) begin
                formatted_msg_RegFile = $sformatf("  [ ERROR ] Test %02d: in:%h rd:%h rs1:%h rs2:%h RegWrite:%h rst:%h | Actual out1:%h (Expected:%h), Actual out2:%h (Expected:%h)",
                    tests_run, in_test, rd_test, rs1_test, rs2_test, RegWrite_test, rst_test, out1, out1_expect, out2, out2_expect);
                $display("%s%s%s", `CLR_RED, formatted_msg_RegFile, `CLR_RESET);
                errors++;
            end else begin
                formatted_msg_RegFile = $sformatf("  [SUCCESS] Test %02d: in:%h rd:%h rs1:%h rs2:%h RegWrite:%h rst:%h = out1:%h, out2:%h",
                    tests_run, in_test, rd_test, rs1_test, rs2_test, RegWrite_test, rst_test, out1, out2);
                $display("%s%s%s", `CLR_GREEN, formatted_msg_RegFile, `CLR_RESET);
            end
        end
    endtask

    initial begin
        // Wait for master start trigger
        @(master_tb.master_is_done);

        formatted_msg_RegFile = $sformatf("-- RegFile Test Bench --");
        $display("%s%s%s", `CLR_BLUE, formatted_msg_RegFile, `CLR_RESET);
        rst = 1;
        #20;
        rst = 0;

        // Warning by default
        $display("%s[ WARNING ] Test cases not implemented!%s", `CLR_RED, `CLR_RESET);

        // ==========================================
        // 1. Initial Test Cases
        // ==========================================
        $display("* Running test cases...");
        verification_RegFile(8'h00, 8'h00, 8'h00, 8'h00, 0, 0, 8'h00, 8'h00);

        // ==========================================
        // End of Simulation
        // ==========================================
        formatted_msg_RegFile = $sformatf("   END : %0d Tests executed | %0d Errors(s)", tests_run, errors);
        if (errors == 0) $display("%s%s%s", `CLR_GREEN, formatted_msg_RegFile, `CLR_RESET);
        else             $display("%s%s%s", `CLR_RED, formatted_msg_RegFile, `CLR_RESET);

        // Trigger completion event in master
        -> master_tb.RegFile_is_done;

    end

endmodule