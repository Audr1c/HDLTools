# SystemVerilog Tool - Module & Testbench Designer

A sleek, modern Python & Pygame-based graphical application to simplify designing, parsing, and generating SystemVerilog modules and testbenches. It features a live-updating visual block diagram, High-DPI crisp text rendering, and a responsive resizable window layout.

## Features

- **High-DPI Sharp Font Rendering**: Automatically configures system DPI awareness on Windows to prevent canvas blurriness, rendering pixel-perfect, highly readable text.
- **Fully Resizable Window**: Responsive layouts automatically adapt sidebar elements, visual viewports, action buttons, and scroll views to fill screen width and height.
- **Standalone vs. With Master Simulation Modes**:
  - **Standalone**: Generates a self-contained simulation file with native `$dumpfile` / `$dumpvars` commands and a `$finish;` directive.
  - **With Master**: Integrates multiple sub-testbenches into a top-level `master_tb.sv` sequence structure. Sub-testbenches wait for `@(master_tb.master_is_done);` and trigger completion via `-> master_tb.<module_name>_is_done;`.
- **Automatic Code Generation**:
  - Automatically prepends `` `timescale 1ns / 1ps `` to every generated module and testbench.
  - Generates self-checking validation tasks (`task verification_<name>`) that apply input signals, wait for clock edge/delay propagation, and assert/compare output states with ANSI-colored success/error terminal logs.
  - Includes a default red warning prompt alerting you that test cases are not implemented.
- **Real-Time Visual Block Diagram**: Live schematic visualizing module port directions. Clocks (Cyan with square wave icon), Resets (Pink with reset icon), Inputs (Blue), and Outputs (Green) are color-coded.
- **Interactive UI**:
  - **Text Selection**: Full support inside input text fields for dragging selection, Shift+Arrow selection, Ctrl+A (Select All), Ctrl+C (Copy), and Ctrl+V (Paste via native Tkinter).
  - **Discrete Deletion**: Desaturated light pink delete buttons that turn bright red on hover with no bulky background box.
  - **Save Floppy Button**: A unified, elegant vector floppy disk icon in the top-right corner to save the active view (Module Code, Testbench Code, or Master TB).

## How to Run

1. Ensure **Python 3** and **Pygame** are installed:
   ```powershell
   pip install pygame
   ```
2. Launch the application:
   ```powershell
   python app.py
   ```

## Keyboard Shortcuts in Input Fields
- **Ctrl + A**: Select all text inside the active input field.
- **Ctrl + C**: Copy selected text (or all text if none is selected).
- **Ctrl + V**: Paste text from system clipboard.
- **Shift + Left / Right**: Select character range.
- **Tab / Shift + Tab**: Cycle focus between input fields (ports scroll area will automatically focus and scroll elements into view).

## License

This project is licensed under the **MIT License**.

```text
MIT License

Copyright (c) 2026

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
