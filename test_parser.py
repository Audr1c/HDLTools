from sv_parser import parse_sv_file, detect_clk_rst

# 1. Mock ANSI-style SystemVerilog module
ansi_code = """
// Beautiful comments here
module my_awesome_adder #(
    parameter DATA_WIDTH = 8,
    parameter ADDR_WIDTH = 12
)(
    input  logic                   clk,    // Clock input
    input  logic                   rst_n,  // Active-low asynchronous reset
    input  logic [DATA_WIDTH-1:0]  a_in,   // Input A
    input  logic [DATA_WIDTH-1:0]  b_in,   // Input B
    output logic                   valid_out,
    output logic [DATA_WIDTH:0]    sum_out // Sum output with overflow bit
);

    // Module body logic goes here
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            sum_out <= 0;
            valid_out <= 0;
        end else begin
            sum_out <= a_in + b_in;
            valid_out <= 1;
        end
    end

endmodule
"""

# 2. Mock Non-ANSI-style Verilog module
non_ansi_code = """
/*
  Multiline comment
  For older Verilog modules
*/
module legacy_multiplier(clk, rst, data_in, mult_in, result);
    input clk;
    input rst;
    input [7:0] data_in, mult_in;
    output reg [15:0] result;

    always @(posedge clk) begin
        if (rst)
            result <= 0;
        else
            result <= data_in * mult_in;
    end
endmodule
"""

def test_parser():
    print("=== Testing SystemVerilog Parser ===")
    
    # Test ANSI Module
    print("\n--- Parsing ANSI Module ---")
    mod_name, ports = parse_sv_file(ansi_code)
    print(f"Parsed Module Name: {mod_name}")
    print("Parsed Ports:")
    for p in ports:
        print(f"  Name: {p['name']:<12} | Dir: {p['dir']:<3} | Width: {p['width']}")
        
    clk, rst = detect_clk_rst(ports)
    print(f"Clock detected: {clk['name'] if clk else 'None'}")
    print(f"Reset detected: {rst['name'] if rst else 'None'}")
    
    assert mod_name == "my_awesome_adder", "Module name mismatch"
    assert len(ports) == 6, f"Expected 6 ports, got {len(ports)}"
    assert clk is not None, "Clock not detected"
    assert rst is not None, "Reset not detected"
    assert ports[2]['width'] == "[DATA_WIDTH-1:0]", "Width expression mismatch"
    
    # Test Non-ANSI Module
    print("\n--- Parsing Non-ANSI Module ---")
    mod_name, ports = parse_sv_file(non_ansi_code)
    print(f"Parsed Module Name: {mod_name}")
    print("Parsed Ports:")
    for p in ports:
        print(f"  Name: {p['name']:<12} | Dir: {p['dir']:<3} | Width: {p['width']}")
        
    clk, rst = detect_clk_rst(ports)
    print(f"Clock detected: {clk['name'] if clk else 'None'}")
    print(f"Reset detected: {rst['name'] if rst else 'None'}")
    
    assert mod_name == "legacy_multiplier", "Module name mismatch"
    assert len(ports) == 5, f"Expected 5 ports, got {len(ports)}"
    assert clk is not None, "Clock not detected"
    assert rst is not None, "Reset not detected"
    # test comma separated names
    assert any(p['name'] == 'mult_in' for p in ports), "Comma separated port mult_in missing"
    assert next(p for p in ports if p['name'] == 'data_in')['width'] == "[7:0]", "Width parsing failure"
    assert next(p for p in ports if p['name'] == 'result')['width'] == "[15:0]", "Width parsing failure"
    
    print("\n[SUCCESS] All parser tests passed!")

if __name__ == "__main__":
    test_parser()
