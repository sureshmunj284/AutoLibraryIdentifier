#!/usr/bin/env python3
import os
import re
import sys

# ---------------------------------------------------------------
# Configuration: Paths to Liberty files for each known library
# ---------------------------------------------------------------
LIB_PATHS = {
    "RAK": "Set your path",
    "NANGATE": "Set your path",
    "Skywater": "Set your path",
    "rf_2p_136d_74w_1m_4b": "Set your path",
    "rf_2p_256d_76w_1m_4b": "Set your path",
    "rf_2p_512d_76w_2m_4b": "Set your path",
    "sram_sp_512d_32w_4m_2b": "Set your path",
    "sram_sp_16384d_36w_16m_8b": "Set your path",
    "sram_sp_32768d_33w_16m_8b": "Set your path"
}

# ---------------------------------------------------------------
# Detect which libraries are used in the given netlist
# ---------------------------------------------------------------
def detect_library(netlist_file):
    try:
        with open(netlist_file, 'r') as f:
            lines = f.readlines()
    except FileNotFoundError:
        sys.exit(f"❌ Error: File '{netlist_file}' not found.")

    patterns = {
        "RAK": re.compile(r'\b[A-Z0-9]+X\d+\b'),
        "NANGATE": re.compile(r'\b[A-Z0-9]+_X\d+\b'),
        "Skywater": re.compile(r'\bsky130_fd_sc_\w{2}__\w+_\d+\b'),
        "rf_2p_136d_74w_1m_4b": re.compile('rf_2p_136d_74w_1m_4b'),
        "rf_2p_256d_76w_1m_4b": re.compile('rf_2p_256d_76w_1m_4b'),
        "rf_2p_512d_76w_2m_4b": re.compile('rf_2p_512d_76w_2m_4b'),
        "sram_sp_512d_32w_4m_2b": re.compile('sram_sp_512d_32w_4m_2b'),
        "sram_sp_16384d_36w_16m_8b": re.compile('sram_sp_16384d_36w_16m_8b'),
        "sram_sp_32768d_33w_16m_8b": re.compile('sram_sp_32768d_33w_16m_8b')
    }

    counts = {lib: 0 for lib in patterns}
    for line in lines:
        if '__' in line:
            continue
        for lib, pat in patterns.items():
            if pat.search(line):
                counts[lib] += 1

    detected_libs = [lib for lib, cnt in counts.items() if cnt > 0]
    return counts, detected_libs

# ---------------------------------------------------------------
# Create setup files in the same directory as the netlist
# ---------------------------------------------------------------
def create_setup_files(netlist_file, counts, detected_libs):
    project_dir = os.path.dirname(os.path.abspath(netlist_file))
    if not os.path.isdir(project_dir):
        os.makedirs(project_dir)

    # Build library paths
    lib_paths = [LIB_PATHS[lib] for lib in detected_libs if lib in LIB_PATHS]

    # --- 1️⃣ Write Report ---
    rpt_path = os.path.join(project_dir, "library_detect.rpt")
    with open(rpt_path, "w") as rpt:
        rpt.write("Library Detection Report\n========================\n")
        rpt.write(f"Netlist File: {netlist_file}\n\n")
        for lib, cnt in counts.items():
            rpt.write(f"{lib:30s}: {cnt}\n")
        rpt.write("\nDetected Libraries:\n-------------------\n")
        if detected_libs:
            for lib in detected_libs:
                rpt.write(f"{lib}\n")
        else:
            rpt.write("No known library cell names found.\n")

    # --- 2️⃣ Write set_all_libs.tcl ---
    tcl_path = os.path.join(project_dir, "set_all_libs.tcl")
    with open(tcl_path, "w") as tcl:
        tcl.write("# Auto-generated TCL setup file\n")
        tcl.write('puts "Loading all detected libraries..."\n')
        tcl.write(f"set lib_used \"{' '.join(lib_paths)}\"\n")
        tcl.write("read_lib $lib_used\n")
        tcl.write('puts "All libraries loaded successfully."\n')

    # --- 3️⃣ Write .tempusrc ---
    rc_path = os.path.join(project_dir, ".tempusrc")
    with open(rc_path, "w") as rc:
        rc.write(f"source {tcl_path}\n")
        rc.write('puts "📦 Loading default Tempus setup..."\n')

    print(f"✅ Generated:\n  {rpt_path}\n  {tcl_path}\n  {rc_path}\n")

# ---------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------
if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("Usage: python3 Auto_LibraryIdentifier.py <netlist_file>")

    netlist_file = sys.argv[1]
    counts, detected_libs = detect_library(netlist_file)

    if detected_libs:
        create_setup_files(netlist_file, counts, detected_libs)
        print("✅ Library detection and setup completed.")
    else:
        print("⚠️  No known libraries detected in the given netlist.")
