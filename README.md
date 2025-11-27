# Auto Library Identifier for Netlists

## Overview
`Auto_LibraryIdentifier.py` is a Python 3 script that analyzes a digital circuit netlist and automatically detects which standard cell and memory libraries are being used. It then generates **helper TCL and C-shell scripts** to set up environment variables for EDA tools like **Cadence Tempus**, enabling seamless library setup.

This tool is useful for EDA engineers working with multiple standard cell libraries and memory macros, automating the library environment setup process.

---

## Features

- Detects standard cell libraries and memory macros in a netlist.
- Generates helper scripts for setting library environment variables:
  - TCL scripts (`.tcl`) for Tempus workflows  
  - C-shell scripts (`.csh`) for terminal setup
- Creates master scripts combining all detected libraries (`set_all_libs.tcl` and `set_all_libs.csh`)
- Generates a **report (`library_detect.rpt`)** summarizing library usage
- Supports **user-provided library paths** for flexibility.

---

## Requirements

- Python 3.x
- Unix/Linux environment for sourcing `.csh` scripts or using TCL scripts in EDA tools
- User must provide the library paths either via **command-line arguments** or **configuration file**.

---

## Usage

1. **Clone the repository**  

```bash
git clone <repository_url>
cd <repository_folder>
