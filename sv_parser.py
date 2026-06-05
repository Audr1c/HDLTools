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
    # We remove common types to leave only the identifier(s)
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

    # What remains should be the port name(s), potentially comma separated if Verilog-style inside body
    # e.g. "a, b"
    names = [n.strip() for n in re.split(r'\s*,\s*', s) if n.strip()]
    
    ports = []
    for name in names:
        # Clean up any remaining junk (like assignments like = 0)
        name = re.split(r'\s*=\s*', name)[0].strip()
        # Verify it's a valid identifier
        if re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', name):
            # Clean width representation
            clean_width = width
            if width == "1" or not width:
                clean_width = "1"
            ports.append({
                "name": name,
                "dir": direction,
                "width": clean_width
            })

    # Update defaults for next port inheritance
    return ports, direction, port_type, width

def parse_sv_file(file_content):
    """
    Parses SystemVerilog/Verilog content.
    Returns: (module_name, list_of_ports)
    Each port is a dict: {"name": str, "dir": "IN"|"OUT"|"INOUT", "width": str}
    """
    code = strip_comments(file_content)
    
    # 1. Find the module definition
    # Regex to find: module <name>
    mod_match = re.search(r'\bmodule\s+([a-zA-Z_][a-zA-Z0-9_]*)', code)
    if not mod_match:
        return None, []
        
    module_name = mod_match.group(1)
    
    # Extract the module declaration area (from 'module' to first ';')
    start_pos = mod_match.start()
    semi_pos = code.find(';', start_pos)
    if semi_pos == -1:
        return module_name, []
        
    decl_area = code[start_pos:semi_pos]
    
    # Check if there is a port list parentheses (...) in the declaration area
    # Note: there might be a parameter list #(...) first.
    # Let's find the port list string.
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
                
    # If we have parentheses:
    # If we have 1 set of paren: it's the port list (unless it's preceded by #, then it's parameter list)
    # If we have 2 sets of paren: the first one is parameters, the second is ports
    ports_paren = None
    if len(paren_indices) == 1:
        # Check if preceded by #
        before = decl_area[:paren_indices[0][0]].strip()
        if not before.endswith('#'):
            ports_paren = paren_indices[0]
    elif len(paren_indices) >= 2:
        # Second one is ports
        ports_paren = paren_indices[1]
        
    if ports_paren:
        port_list_str = decl_area[ports_paren[0]+1 : ports_paren[1]]

    # Also extract the module body (from first ';' to 'endmodule')
    end_match = re.search(r'\bendmodule\b', code[semi_pos:])
    body_str = ""
    if end_match:
        body_str = code[semi_pos+1 : semi_pos+1 + end_match.start()]
    else:
        body_str = code[semi_pos+1:]

    # Parse ports
    ports = []
    port_names_seen = set()
    
    # Defaults for inheritance
    curr_dir = "IN"
    curr_type = ""
    curr_width = "1"
    
    # A. Parse the port list (ANSI style)
    if port_list_str.strip():
        # Split by comma outside brackets/parens
        declarations = split_outside_brackets(port_list_str, ',')
        for decl in declarations:
            parsed, curr_dir, curr_type, curr_width = parse_port_declaration(
                decl, curr_dir, curr_type, curr_width
            )
            for p in parsed:
                if p["name"] not in port_names_seen:
                    ports.append(p)
                    port_names_seen.add(p["name"])

    # B. Parse the body (for non-ANSI declarations or additional port specifiers)
    # We search for lines ending in ';' and check if they declare inputs/outputs
    body_statements = split_outside_brackets(body_str, ';')
    for stmt in body_statements:
        stmt = stmt.strip()
        if not stmt:
            continue
            
        # Check if it starts with input/output/inout
        if re.match(r'^\s*(input|output|inout)\b', stmt):
            parsed, curr_dir, curr_type, curr_width = parse_port_declaration(
                stmt, curr_dir, curr_type, curr_width
            )
            for p in parsed:
                # If already seen (from ANSI port list, e.g. just names), we update its properties
                existing_port = next((x for x in ports if x["name"] == p["name"]), None)
                if existing_port:
                    existing_port["dir"] = p["dir"]
                    existing_port["width"] = p["width"]
                else:
                    ports.append(p)
                    port_names_seen.add(p["name"])

    # Clean widths: convert things like [0:0] or empty to 1
    for p in ports:
        w = p["width"].strip()
        if w == "" or w == "1":
            p["width"] = "1"
        # If it's a range like [7:0], keep it as is.
        
    return module_name, ports

def detect_clk_rst(ports):
    """
    Given a list of ports, identifies the clock and reset ports if they exist.
    Returns: (clk_port_dict, rst_port_dict) or None
    """
    clk_port = None
    rst_port = None
    
    for p in ports:
        name_lower = p["name"].lower()
        if p["dir"] == "IN":
            if name_lower in ["clk", "clock", "i_clk"]:
                clk_port = p
            elif name_lower in ["rst", "reset", "rst_n", "i_rst", "rst_b"]:
                rst_port = p
                
    # Secondary search if exact names aren't found
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
