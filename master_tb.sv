`timescale 1ns / 1ps

module master_tb;

    // Synchronization Events
    event master_is_done;
    event alu_is_done;
    event RegFile_is_done;

    // Sub-Testbench Instantiations
    alu_tb u_alu_tb();
    RegFile_tb u_RegFile_tb();

    initial begin
        $dumpfile("build/simulation.vcd");
        $dumpvars(0, master_tb); // Record all signals recursively
        
        // Start all testbenches
        -> master_is_done;
        
        // Wait for each testbench to complete sequentially
        @(alu_is_done);
        @(RegFile_is_done);
        
        $finish;
    end

endmodule