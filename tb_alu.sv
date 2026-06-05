`define CLR_RESET  "\033[0m"
`define CLR_RED    "\033[1;31m"
`define CLR_GREEN  "\033[1;32m"
`define CLR_YELLOW "\033[1;33m"
`define CLR_BLUE   "\033[1;34m"

`timescale 1ns / 1ps
string formatted_msg_alu;

module alu_tb;

    int errors = 0;
    int tests_run = 0;

    // ----------------------------------------------------------------------
    // Signals
    // ----------------------------------------------------------------------
    logic  [31:0] in1;
    logic  [31:0] in2;
    logic  [3:0] alu_ctrl;
    logic  [31:0] out;
    logic zero;

    // ----------------------------------------------------------------------
    // DUT Instantiation
    // ----------------------------------------------------------------------
    alu dut (
        .in1      (in1),
        .in2      (in2),
        .alu_ctrl (alu_ctrl),
        .out      (out),
        .zero     (zero)
    );

    // ----------------------------------------------------------------------
    // Verification Task
    // ----------------------------------------------------------------------
    task verification_alu(
        input  logic [31:0] in1_test,
        input  logic [31:0] in2_test,
        input  logic [3:0] alu_ctrl_test,
        input  logic [31:0] out_expect,
        input  logic zero_expect
    );
        begin
            tests_run++;

            // Apply inputs
            in1 = in1_test;
            in2 = in2_test;
            alu_ctrl = alu_ctrl_test;
            #10;

            if (out !== out_expect || zero !== zero_expect) begin
                formatted_msg_alu = $sformatf("  [ ERROR ] Test %02d: in1:%h in2:%h alu_ctrl:%h | Actual out:%h (Expected:%h), Actual zero:%h (Expected:%h)",
                    tests_run, in1_test, in2_test, alu_ctrl_test, out, out_expect, zero, zero_expect);
                $display("%s%s%s", `CLR_RED, formatted_msg_alu, `CLR_RESET);
                errors++;
            end else begin
                formatted_msg_alu = $sformatf("  [SUCCESS] Test %02d: in1:%h in2:%h alu_ctrl:%h = out:%h, zero:%h",
                    tests_run, in1_test, in2_test, alu_ctrl_test, out, zero);
                $display("%s%s%s", `CLR_GREEN, formatted_msg_alu, `CLR_RESET);
            end
        end
    endtask

    initial begin
        // Wait for master start trigger
        @(master_tb.master_is_done);

        formatted_msg_alu = $sformatf("-- alu Test Bench --");
        $display("%s%s%s", `CLR_BLUE, formatted_msg_alu, `CLR_RESET);
        // Warning by default
        $display("%s[ WARNING ] Test cases not implemented!%s", `CLR_RED, `CLR_RESET);

        // ==========================================
        // 1. Initial Test Cases
        // ==========================================
        $display("* Running test cases...");
        verification_alu(8'h00, 8'h00, 8'h00, 8'h00, 0);

        // ==========================================
        // End of Simulation
        // ==========================================
        formatted_msg_alu = $sformatf("   END : %0d Tests executed | %0d Errors(s)", tests_run, errors);
        if (errors == 0) $display("%s%s%s", `CLR_GREEN, formatted_msg_alu, `CLR_RESET);
        else             $display("%s%s%s", `CLR_RED, formatted_msg_alu, `CLR_RESET);

        // Trigger completion event in master
        -> master_tb.alu_is_done;

    end

endmodule