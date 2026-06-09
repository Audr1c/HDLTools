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
    assert next(p for p in ports if p['name'] == 'data_in')['width'] == "[7:0]", "Width parsing failure"
    assert next(p for p in ports if p['name'] == 'result')['width'] == "[15:0]", "Width parsing failure"
    
    # Test VHDL parsing
    vhdl_code = """
    library ieee;
    use ieee.std_logic_1164.all;
    
    entity my_vhdl_module is
        port (
            clk      : in  std_logic;
            rst_n    : in  std_logic;
            data_in  : in  std_logic_vector(7 downto 0);
            data_out : out std_logic_vector(0 to 15)
        );
    end my_vhdl_module;
    """
    print("\n--- Parsing VHDL Module ---")
    from sv_parser import parse_vhdl_file, detect_hdl_language
    mod_name, ports = parse_vhdl_file(vhdl_code)
    print(f"Parsed VHDL Name: {mod_name}")
    print("Parsed Ports:")
    for p in ports:
        print(f"  Name: {p['name']:<12} | Dir: {p['dir']:<3} | Width: {p['width']}")
    
    assert mod_name == "my_vhdl_module"
    assert len(ports) == 4
    assert next(p for p in ports if p['name'] == 'clk')['width'] == "1"
    assert next(p for p in ports if p['name'] == 'data_in')['width'] == "[7:0]"
    assert next(p for p in ports if p['name'] == 'data_out')['width'] == "[0:15]"
    
    # Test Language Detection
    print("\n--- Testing HDL Language Detection ---")
    assert detect_hdl_language(ansi_code) == "SystemVerilog"
    assert detect_hdl_language(non_ansi_code) == "Verilog"
    assert detect_hdl_language(vhdl_code) == "VHDL"
    print("Language detection checks passed!")
    
    print("\n[SUCCESS] All parser tests passed!")

if __name__ == "__main__":
    test_parser()
