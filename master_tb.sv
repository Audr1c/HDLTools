`timescale 1ns / 1ps

module master_tb;

    // ----------------------------------------------------------------------
    // Synchronization Events
    // ----------------------------------------------------------------------
    event alu_is_done;

    // ----------------------------------------------------------------------
    // Sub-Testbench Instantiations
    // ----------------------------------------------------------------------
    alu_tb u_alu_tb();
    RegFile_tb u_RegFile_tb();

    // ----------------------------------------------------------------------
    // Global Waveform Logging
    // ----------------------------------------------------------------------
    initial begin
        $dumpfile("build/simulation.vcd");
        $dumpvars(0, master_tb); // Dump all sub-modules recursively
    end

endmodule