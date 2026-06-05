import os
from sv_parser import parse_sv_file
from sv_generator import generate_testbench_code, generate_master_tb_code

def test_integration():
    print("=== Testing Advanced Testbench Generation ===")
    
    # 1. Parse ALU (Asynchronous)
    with open("alu.sv", "r") as f:
        alu_content = f.read()
    alu_name, alu_ports = parse_sv_file(alu_content)
    
    print(f"Parsed Module: {alu_name}")
    
    # Generate ALU Testbench (Chained, triggers master_tb.alu_is_done, no finish)
    alu_tb_code = generate_testbench_code(
        alu_name, alu_ports,
        is_sync_reset=False, is_active_low_reset=True,
        tb_mode="chained", wait_event="", trigger_event="master_tb.alu_is_done",
        call_finish=False
    )
    
    with open("tb_alu.sv", "w") as f:
        f.write(alu_tb_code)
    print("Generated tb_alu.sv successfully!")
    
    # 2. Parse RegFile (Synchronous)
    with open("RegFile.sv", "r") as f:
        rf_content = f.read()
    rf_name, rf_ports = parse_sv_file(rf_content)
    
    print(f"Parsed Module: {rf_name}")
    
    # Generate RegFile Testbench (Chained, waits for master_tb.alu_is_done, triggers nothing, calls finish)
    rf_tb_code = generate_testbench_code(
        rf_name, rf_ports,
        is_sync_reset=True, is_active_low_reset=False, # active high reset
        tb_mode="chained", wait_event="master_tb.alu_is_done", trigger_event="",
        call_finish=True
    )
    
    with open("tb_RegFile.sv", "w") as f:
        f.write(rf_tb_code)
    print("Generated tb_RegFile.sv successfully!")
    
    # 3. Generate Master Testbench
    sub_tbs = [
        {"module_name": "alu", "wait_event": "", "trigger_event": "master_tb.alu_is_done"},
        {"module_name": "RegFile", "wait_event": "master_tb.alu_is_done", "trigger_event": ""}
    ]
    master_tb_code = generate_master_tb_code(sub_tbs)
    
    with open("master_tb.sv", "w") as f:
        f.write(master_tb_code)
    print("Generated master_tb.sv successfully!")
    
    # Quick sanity checks on contents
    print("\n--- Verifying content of generated tb_alu.sv ---")
    assert "`define CLR_RED" in alu_tb_code, "Missing color macros"
    assert "task verification_alu(" in alu_tb_code, "Missing verification task"
    assert "-> master_tb.alu_is_done;" in alu_tb_code, "Missing completion trigger event"
    assert "$finish;" not in alu_tb_code, "ALU TB should not call $finish"
    print("tb_alu.sv checks passed!")
    
    print("\n--- Verifying content of generated tb_RegFile.sv ---")
    assert "always" in rf_tb_code and "`PERIOD" in rf_tb_code, "Missing clock generation block"
    assert "@(master_tb.alu_is_done);" in rf_tb_code, "Missing start event listener"
    assert "$finish;" in rf_tb_code, "RegFile TB should call $finish"
    print("tb_RegFile.sv checks passed!")
    
    print("\n--- Verifying content of generated master_tb.sv ---")
    assert "event alu_is_done;" in master_tb_code, "Missing synchronized event declaration"
    assert "alu_tb u_alu_tb();" in master_tb_code, "Missing alu_tb instantiation"
    assert "RegFile_tb u_RegFile_tb();" in master_tb_code, "Missing RegFile_tb instantiation"
    print("master_tb.sv checks passed!")
    
    print("\n[SUCCESS] Integration generation test completed successfully!")

if __name__ == "__main__":
    test_integration()
