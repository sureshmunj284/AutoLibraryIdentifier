#!/usr/bin/env python3
import os
import re
import sys

# ---------------------------------------------------------------
# Configuration: paths to the "slow" LIBERTY files for each library
# ---------------------------------------------------------------
LIB_PATHS = {
    "RAK": "/tech/libraries/RAK_LIBS/lib/max/slow.lib",                        
    "NANGATE": "/tech/libraries/NangateOpenCellLibrary_PDKv1_3_v2010_12/Front_End/Liberty/CCS/NangateOpenCellLibrary_slow_ccs.lib",
    "Skywater": "/tech/libraries/sky130_fd_sc_ms/Liberty",
    "rf_2p_136d_74w_1m_4b": "/tech/designs/cpu_sys/dummyNL4KLE_tech/memories/rf_2p_136d_74w_1m_4b.lib",
    "rf_2p_256d_76w_1m_4b": "/tech/designs/cpu_sys/dummyNL4KLE_tech/memories/rf_2p_256d_76w_1m_4b.lib",
    "rf_2p_512d_76w_2m_4b": "/tech/designs/cpu_sys/dummyNL4KLE_tech/memories/rf_2p_512d_76w_2m_4b.lib",
    "sram_sp_512d_32w_4m_2b": "/tech/designs/cpu_sys/dummyNL4KLE_tech/memories/sram_sp_512d_32w_4m_2b.lib",
    "sram_sp_16384d_36w_16m_8b": "/tech/designs/cpu_sys/dummyNL4KLE_tech/memories/sram_sp_16384d_36w_16m_8b.lib",
    "sram_sp_32768d_33w_16m_8b": "/tech/designs/cpu_sys/dummyNL4KLE_tech/memories/sram_sp_32768d_33w_16m_8b.lib"
}

# ---------------------------------------------------------------
# Function: Detect which standard cell libraries are used
# ---------------------------------------------------------------
def detect_library(netlist_file):
    try:
        with open(netlist_file, 'r') as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"Error: File '{netlist_file}' not found.")
        sys.exit(1)

    # Regex patterns for each library
    rak_pattern = re.compile(r'\b[A-Z0-9]+X\d+\b')
    nangate_pattern = re.compile(r'\b[A-Z0-9]+_X\d+\b')
    sky_pattern = re.compile(r'\bsky130_fd_sc_\w{2}__\w+_\d+\b')
    rf_2p_136d_74w_1m_4b_pattern = re.compile('rf_2p_136d_74w_1m_4b')
    rf_2p_256d_76w_1m_4b_pattern = re.compile('rf_2p_256d_76w_1m_4b')
    rf_2p_512d_76w_2m_4b_pattern = re.compile('rf_2p_512d_76w_2m_4b')
    sram_sp_512d_32w_4m_2b_pattern = re.compile('sram_sp_512d_32w_4m_2b')
    sram_sp_16384d_36w_16m_8b_pattern = re.compile('sram_sp_16384d_36w_16m_8b')
    sram_sp_32768d_33w_16m_8b_pattern = re.compile('sram_sp_32768d_33w_16m_8b')

    counts = {
        "RAK": 0,
        "NANGATE": 0,
        "Skywater": 0,
        "rf_2p_136d_74w_1m_4b": 0,
        "rf_2p_256d_76w_1m_4b": 0,
        "rf_2p_512d_76w_2m_4b": 0,
        "sram_sp_512d_32w_4m_2b": 0,
        "sram_sp_16384d_36w_16m_8b": 0,
        "sram_sp_32768d_33w_16m_8b": 0
        }


    for line in lines:
        if '__' in line:
            continue
        if rak_pattern.search(line): counts["RAK"] += 1
        if nangate_pattern.search(line): counts["NANGATE"] += 1
        if sky_pattern.search(line): counts["Skywater"] += 1
        if rf_2p_136d_74w_1m_4b_pattern.search(line): counts["rf_2p_136d_74w_1m_4b"] += 1
        if rf_2p_256d_76w_1m_4b_pattern.search(line): counts["rf_2p_256d_76w_1m_4b"] += 1
        if rf_2p_512d_76w_2m_4b_pattern.search(line): counts["rf_2p_512d_76w_2m_4b"] += 1
        if sram_sp_512d_32w_4m_2b_pattern.search(line): counts["sram_sp_512d_32w_4m_2b"] += 1
        if sram_sp_16384d_36w_16m_8b_pattern.search(line): counts["sram_sp_16384d_36w_16m_8b"] += 1
        if sram_sp_32768d_33w_16m_8b_pattern.search(line): counts["sram_sp_32768d_33w_16m_8b"] += 1

    detected_libs = [lib for lib, cnt in counts.items() if cnt > 0]

    with open("library_detect.rpt", "w") as rpt:
        rpt.write("Library Detection Report\n========================\n")
        rpt.write(f"Netlist File: {netlist_file}\n\n")
        for lib, cnt in counts.items():
            rpt.write(f"{lib:8s}: {cnt}\n")
        rpt.write("\nDetected Libraries:\n-------------------\n")
        rpt.writelines(f"{lib}\n" for lib in detected_libs) if detected_libs else rpt.write("No known library cell names found.\n")

    if detected_libs:
        print(f"Detected Libraries: {', '.join(detected_libs)}")
    else:
        print("No known library cell names found.")
    print("Report generated: library_detect.rpt")

    return detected_libs

# ---------------------------------------------------------------
# Function: Create helper and master setup files
# ---------------------------------------------------------------
def set_environment_variable(libraries):
    all_tcl_files, all_csh_files, all_paths = [], [], []

    for library_name in libraries:
        lib_path = LIB_PATHS.get(library_name)
        if not lib_path:
            print(f"Warning: No LIBERTY path found for {library_name}")
            continue

        os.environ["LIB_USED"] = lib_path
        print(f"Set environment variable: LIB_USED={lib_path}")

        tcl_file = f"set_lib_used_{library_name}.tcl"
        csh_file = f"set_lib_used_{library_name}.csh"
        all_tcl_files.append(tcl_file)
        all_csh_files.append(csh_file)
        all_paths.append(lib_path)

        # Generate tcsh helper
        with open(csh_file, "w") as f:
            f.write(f'setenv LIB_USED "{lib_path}"\n')

        # Generate tcl helper (for Tempus)
        with open(tcl_file, "w") as f:
            f.write(f'set lib_used "{lib_path}"\n')
            f.write('puts "LIB_USED set to $lib_used"\n')

        print(f"\nGenerated helper files for {library_name}:")
        print(f"  1. {csh_file} → use in tcsh:   source {csh_file}")
        print(f"  2. {tcl_file} → use in Tempus: source {tcl_file}")

    # ---------------- TCL MASTER ----------------
    if all_tcl_files:
        with open("set_all_libs.tcl", "w") as f:
            f.write("# Auto-generated master TCL library setup\n")
            f.write('puts "Loading all detected libraries..."\n\n')
            for lib_path in all_paths:
                f.write(f'puts "{lib_path}"\n')
            f.write('\nset lib_used "')
            f.write(" ".join(all_paths))
            f.write('"\n')
            f.write('puts "All libraries loaded successfully."\n')

    # ---------------- CSH MASTER ----------------
    if all_csh_files:
        with open("set_all_libs.csh", "w") as f:
            f.write("# Auto-generated master C-shell library setup\n\n")
            f.write(f'setenv LIB_USED "{":".join(all_paths)}"\n')
            f.write('echo "All libraries loaded successfully."\n')
            f.write('echo ""\n')
            f.write('echo "Library paths:"\n')
            f.write('echo "$LIB_USED" | tr ":" "\\n"\n')

    print("\nMaster files created:")
    print("  • set_all_libs.tcl → use in Tempus: source set_all_libs.tcl")
    print("  • set_all_libs.csh → use in tcsh:   source set_all_libs.csh")

# ---------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 Auto_LibraryIdentifier.py <netlist_file>")
        sys.exit(1)
    netlist_file = sys.argv[1]
    libraries = detect_library(netlist_file)
    if libraries:
        set_environment_variable(libraries) 
