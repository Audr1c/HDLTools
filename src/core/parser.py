import re

def strip_comments(code):
    # Remove block comments /* ... */
    code = re.sub(r'/\*.*?\*/', ' ', code, flags=re.DOTALL)
    # Remove line comments // ...
    code = re.sub(r'//.*?\n', '\n', code)
    return code

def split_outside_brackets(s, delim=','):
    """Splits a string by a delimiter, but ignores delimiters inside [] or ()."""
    parts = []
    current = []
    b_depth = 0 # [] depth
    p_depth = 0 # () depth
    
    for char in s:
        if char == '[':
            b_depth += 1
        elif char == ']':
            b_depth -= 1
        elif char == '(':
            p_depth += 1
        elif char == ')':
            p_depth -= 1
            
        if char == delim and b_depth == 0 and p_depth == 0:
            parts.append("".join(current).strip())
            current = []
        else:
            current.append(char)
            
    if current:
        parts.append("".join(current).strip())
        
    return [p for p in parts if p]

def parse_port_declaration(decl_str, default_dir="IN", default_type="", default_width="1"):
    """
    Parses a single port declaration string like 'input logic [7:0] data_in'
    or a simple name 'data_in' (which would inherit defaults).
    Returns a dict list (in case of comma-separated declarations like 'input a, b') 
    and the updated defaults.
    """
    s = decl_str.strip()
    if not s:
        return [], default_dir, default_type, default_width

    # Check direction
    dir_match = re.search(r'\b(input|output|inout)\b', s)
    direction = default_dir
    if dir_match:
        dir_name = dir_match.group(1)
        direction = "IN" if dir_name == "input" else ("OUT" if dir_name == "output" else "INOUT")
        # Remove direction from string
        s = re.sub(r'\b' + dir_name + r'\b', '', s, count=1).strip()

    # Check for range [MSB:LSB]
    width = default_width
    range_match = re.search(r'\[([^\]]+)\]', s)
    if range_match:
        width = f"[{range_match.group(1).strip()}]"
        # Remove range from string
        s = re.sub(r'\[[^\]]+\]', '', s, count=1).strip()
    elif dir_match:
        # If a direction was specified but no range, it resets the default width to "1"
        width = "1"

    # Check type (logic, reg, wire, signed, etc.)
    type_patterns = [r'\blogic\b', r'\breg\b', r'\bwire\b', r'\bsigned\b', r'\bunsigned\b']
    port_type = default_type
    
    has_type_in_decl = False
    for pat in type_patterns:
        if re.search(pat, s):
            has_type_in_decl = True
            s = re.sub(pat, '', s).strip()
            
    if has_type_in_decl:
        port_type = "logic" # default representation
    elif dir_match:
        # Reset type if direction is specified
        port_type = ""

    # What remains should be the port name(s), potentially comma separated
    names = [n.strip() for n in re.split(r'\s*,\s*', s) if n.strip()]
    
    ports = []
    for name in names:
        name = re.split(r'\s*=\s*', name)[0].strip()
        if re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', name):
            clean_width = width
            if width == "1" or not width:
                clean_width = "1"
            ports.append({
                "name": name,
                "dir": direction,
                "width": clean_width
            })

    return ports, direction, port_type, width

def parse_sv_file(file_content):
    """Parses SystemVerilog/Verilog content. Returns (module_name, list_of_ports)."""
    code = strip_comments(file_content)
    
    mod_match = re.search(r'\bmodule\s+([a-zA-Z_][a-zA-Z0-9_]*)', code)
    if not mod_match:
        return None, []
        
    module_name = mod_match.group(1)
    
    start_pos = mod_match.start()
    semi_pos = code.find(';', start_pos)
    if semi_pos == -1:
        return module_name, []
        
    decl_area = code[start_pos:semi_pos]
    port_list_str = ""
    
    # Find all top-level parentheses in decl_area
    paren_indices = []
    depth = 0
    p_start = -1
    for idx, char in enumerate(decl_area):
        if char == '(':
            if depth == 0:
                p_start = idx
            depth += 1
        elif char == ')':
            depth -= 1
            if depth == 0 and p_start != -1:
                paren_indices.append((p_start, idx))
                p_start = -1
                
    ports_paren = None
    if len(paren_indices) == 1:
        before = decl_area[:paren_indices[0][0]].strip()
        if not before.endswith('#'):
            ports_paren = paren_indices[0]
    elif len(paren_indices) >= 2:
        ports_paren = paren_indices[1]
        
    if ports_paren:
        port_list_str = decl_area[ports_paren[0]+1 : ports_paren[1]]

    end_match = re.search(r'\bendmodule\b', code[semi_pos:])
    body_str = ""
    if end_match:
        body_str = code[semi_pos+1 : semi_pos+1 + end_match.start()]
    else:
        body_str = code[semi_pos+1:]

    ports = []
    port_names_seen = set()
    
    curr_dir = "IN"
    curr_type = ""
    curr_width = "1"
    
    # ANSI style port list
    if port_list_str.strip():
        declarations = split_outside_brackets(port_list_str, ',')
        for decl in declarations:
            parsed, curr_dir, curr_type, curr_width = parse_port_declaration(
                decl, curr_dir, curr_type, curr_width
            )
            for p in parsed:
                if p["name"] not in port_names_seen:
                    ports.append(p)
                    port_names_seen.add(p["name"])

    # Non-ANSI style declarations in body
    body_statements = split_outside_brackets(body_str, ';')
    for stmt in body_statements:
        stmt = stmt.strip()
        if not stmt:
            continue
            
        if re.match(r'^\s*(input|output|inout)\b', stmt):
            parsed, curr_dir, curr_type, curr_width = parse_port_declaration(
                stmt, curr_dir, curr_type, curr_width
            )
            for p in parsed:
                existing_port = next((x for x in ports if x["name"] == p["name"]), None)
                if existing_port:
                    existing_port["dir"] = p["dir"]
                    existing_port["width"] = p["width"]
                else:
                    ports.append(p)
                    port_names_seen.add(p["name"])

    for p in ports:
        w = p["width"].strip()
        if w == "" or w == "1":
            p["width"] = "1"
        
    return module_name, ports

def detect_clk_rst(ports):
    clk_port = None
    rst_port = None
    
    for p in ports:
        name_lower = p["name"].lower()
        if p["dir"] == "IN":
            if name_lower in ["clk", "clock", "i_clk"]:
                clk_port = p
            elif name_lower in ["rst", "reset", "rst_n", "i_rst", "rst_b"]:
                rst_port = p
                
    if not clk_port:
        for p in ports:
            if p["dir"] == "IN" and "clk" in p["name"].lower():
                clk_port = p
                break
                
    if not rst_port:
        for p in ports:
            if p["dir"] == "IN" and "rst" in p["name"].lower():
                rst_port = p
                break
                
    return clk_port, rst_port

def strip_vhdl_comments(code):
    return re.sub(r'--.*?\n', '\n', code)

def detect_hdl_language(code_str):
    clean_verilog = re.sub(r'//.*?\n', '\n', code_str)
    clean_verilog = re.sub(r'/\*.*?\*/', ' ', clean_verilog, flags=re.DOTALL)
    clean_vhdl = strip_vhdl_comments(code_str)
    
    vhdl_keywords = [
        r'\bentity\b', r'\barchitecture\b', r'\bstd_logic\b', 
        r'\bstd_logic_vector\b', r'\bdownto\b', r'\bport\b\s*\(', 
        r'\blibrary\b', r'\buse\b\s+ieee\b'
    ]
    vhdl_score = sum(1 for kw in vhdl_keywords if re.search(kw, clean_vhdl, re.IGNORECASE))
    
    sv_keywords = [
        r'\blogic\b', r'\balways_comb\b', r'\balways_ff\b', 
        r'\bassert\s+property\b', r'\btypedef\s+struct\b', r'\binterface\b'
    ]
    sv_score = sum(1 for kw in sv_keywords if re.search(kw, clean_verilog))
    
    v_keywords = [
        r'\bmodule\b', r'\bendmodule\b', r'\binput\b', 
        r'\boutput\b', r'\breg\b', r'\bwire\b', r'\balways\b', r'\bassign\b'
    ]
    v_score = sum(1 for kw in v_keywords if re.search(kw, clean_verilog))
    
    if vhdl_score > 0 and vhdl_score > v_score:
        return "VHDL"
    elif sv_score > 0:
        return "SystemVerilog"
    elif v_score > 0:
        if re.search(r'\blogic\b', clean_verilog):
            return "SystemVerilog"
        else:
            return "Verilog"
    
    return "Unknown"

def parse_vhdl_file(file_content):
    code = strip_vhdl_comments(file_content)
    
    entity_match = re.search(r'\bentity\s+([a-zA-Z_][a-zA-Z0-9_]*)\s+is\b', code, re.IGNORECASE)
    if not entity_match:
        return None, []
        
    entity_name = entity_match.group(1)
    
    start_pos = code.lower().find("port", entity_match.end())
    if start_pos == -1:
        return entity_name, []
        
    open_paren = code.find("(", start_pos)
    if open_paren == -1:
        return entity_name, []
        
    depth = 1
    close_paren = -1
    for idx in range(open_paren + 1, len(code)):
        if code[idx] == '(':
            depth += 1
        elif code[idx] == ')':
            depth -= 1
            if depth == 0:
                close_paren = idx
                break
                
    if close_paren == -1:
        return entity_name, []
        
    port_block = code[open_paren + 1 : close_paren]
    
    ports = []
    statements = port_block.split(';')
    for stmt in statements:
        stmt = stmt.strip()
        if not stmt or ':' not in stmt:
            continue
            
        parts = stmt.split(':', 1)
        names_part = parts[0].strip()
        type_part = parts[1].strip()
        
        names = [n.strip() for n in names_part.split(',') if n.strip()]
        
        dir_match = re.match(r'^(inout|in|out|buffer|linkage)\b', type_part, re.IGNORECASE)
        if not dir_match:
            continue
            
        dir_str = dir_match.group(1).lower()
        direction = "IN"
        if dir_str == "in":
            direction = "IN"
        elif dir_str == "out" or dir_str == "buffer":
            direction = "OUT"
        elif dir_str == "inout":
            direction = "INOUT"
            
        rest_type = type_part[dir_match.end():].strip()
        if ':=' in rest_type:
            rest_type = rest_type.split(':=')[0].strip()
            
        width = "1"
        vector_match = re.search(r'std_logic_vector\s*\(([^)]+)\)', rest_type, re.IGNORECASE)
        if vector_match:
            bounds = vector_match.group(1).strip()
            downto_match = re.search(r'([0-9a-zA-Z_+\-*/\s]+)\s+downto\s+([0-9a-zA-Z_+\-*/\s]+)', bounds, re.IGNORECASE)
            to_match = re.search(r'([0-9a-zA-Z_+\-*/\s]+)\s+to\s+([0-9a-zA-Z_+\-*/\s]+)', bounds, re.IGNORECASE)
            if downto_match:
                msb = downto_match.group(1).strip()
                lsb = downto_match.group(2).strip()
                width = f"[{msb}:{lsb}]"
            elif to_match:
                lsb = to_match.group(1).strip()
                msb = to_match.group(2).strip()
                width = f"[{lsb}:{msb}]"
            else:
                width = bounds
        else:
            width = "1"
            
        for name in names:
            if re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', name):
                ports.append({
                    "name": name,
                    "dir": direction,
                    "width": width
                })
                
    return entity_name, ports
