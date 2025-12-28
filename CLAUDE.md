# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This repository contains CNC machine warmup and break-in programs for the **Syil X7 CNC mill** running the **Siemens Sinumerik 828D controller**. Programs are written in G-code (MPF format) for spindle break-in and warmup procedures to maintain machine health.

**WARNING**: These programs control physical machinery. Use at your own risk. Incorrect modifications can damage equipment or cause injury.

## Documentation Reference

**CRITICAL**: Always refer to `Siemens_Programming_Guide_828D.md` when working with G-code commands. This document contains the authoritative reference for:
- Valid G-code and M-code commands for the Siemens Sinumerik 828D controller
- Exact syntax and parameter requirements for each command
- System variables (e.g., `$AC_TIME`)
- Programming keywords (e.g., `SUPA`, `PROC`, `RET`)
- Controller-specific features and limitations

Before modifying any code or adding new commands, verify the command syntax and behavior in the documentation to ensure correctness and prevent machine errors.

### How to Search the Programming Guide

**IMPORTANT**: The `Siemens_Programming_Guide_828D.md` file is VERY LARGE (870KB, 590 pages). **DO NOT read the entire file** as it will consume excessive context and slow down your response.

**ALWAYS use intelligent search tools** to find specific information:

1. **Use grep for keyword searches:**
   ```bash
   grep -i "keyword" Siemens_Programming_Guide_828D.md
   grep -A 5 -B 2 "G-code" Siemens_Programming_Guide_828D.md  # Include context lines
   ```

2. **Use grep with regular expressions for patterns:**
   ```bash
   grep -E "G[0-9]{1,3}" Siemens_Programming_Guide_828D.md  # Find G-codes
   grep -E "\$AC_[A-Z_]+" Siemens_Programming_Guide_828D.md  # Find system variables
   ```

3. **Use awk/sed for structured extraction:**
   ```bash
   awk '/## Page [0-9]+/,/---/' Siemens_Programming_Guide_828D.md  # Extract specific pages
   ```

4. **Combine tools for precise searches:**
   ```bash
   grep -i "SUPA" Siemens_Programming_Guide_828D.md | head -20  # Find first 20 SUPA references
   ```

**Search Strategy:**
- Start with targeted grep searches for specific commands, keywords, or syntax
- Use `-i` flag for case-insensitive searches
- Use `-A` (after) and `-B` (before) flags to get context around matches
- Pipe results through `head` or `tail` to limit output
- Only read specific sections after identifying relevant page numbers

## Code Architecture

### Program Structure

The codebase uses a two-tier architecture:

1. **Main Programs (.MPF files)** - Top-level routines in `routines/` folder:
   - `routines/TEST.MPF` - Quick validation program (5-second cycles)
   - `routines/DAILY.MPF` - Daily warmup (20 min total)
   - `routines/IDLE_72_HOURS.MPF` - Extended warmup after 72h idle (60 min total)
   - `routines/IDLE_2_WEEKS.MPF` - Extended warmup after 2+ weeks idle (30 min total)
   - `routines/FIRST_SPINDLE_RUN_IN.MPF` - Initial break-in procedure (165 min total)

2. **Subroutines (.SPF files)** - Reusable procedures in `subroutines/` folder:
   - `subroutines/_N_WARMUP_CYCLE_SPF` - Core warmup routine that spins the spindle at specified RPM while executing a movement pattern

### _N_WARMUP_CYCLE_SPF - The Core Subroutine

All main programs call `WARMUP_CYCLE(RPM, DURATION)` which:
- Spins spindle at specified RPM
- Executes timed movement pattern (90° moves + 45° diagonal moves)
- Uses **SUPA (machine-absolute positioning)** for all moves
- Pattern coordinates: X0-5, Y0-5, Z0 to -4 (inches)
- Pattern repeats until duration (seconds) elapses

### G-code Conventions

All programs follow these patterns:

**Initialization:**
```gcode
G70 G90 G17  ; G70=inch mode, G90=absolute positioning, G17=XY plane
```

**Safe homing sequence:**
```gcode
G0 SUPA Z0        ; Retract Z to machine zero FIRST (avoid collisions)
G0 SUPA X0 Y0     ; Then move X and Y to machine zero
```

**SUPA keyword:** All positioning uses `SUPA` (machine-absolute coordinates) to ensure consistent behavior regardless of work coordinate offsets.

**Program termination:**
```gcode
M5   ; Spindle stop
M30  ; End of program
```

## Machine-Specific Parameters

- **Max spindle speed**: 12,000 RPM
- **Critical safety check**: Monitor temperature rise during warmup. If >20°C (68°F), reduce to 1200 RPM (10% max)
- **Movement envelope**: Programs assume safe travel in X0-5", Y0-5", Z0 to -4"

## Deployment

Programs must be manually transferred to the Siemens controller:

1. Copy `subroutines/_N_WARMUP_CYCLE_SPF` to the controller's SubRoutines folder
2. Copy main programs from `routines/` folder (.MPF files) to the controller's main program directory
3. Run `TEST.MPF` first to validate installation before running other routines

## Development Guidelines

### Modifying Warmup Sequences

When adjusting warmup parameters in main programs (in `routines/` folder):
- **RPM percentages** are based on 12,000 RPM max (e.g., 30% = 3600 RPM)
- **Duration** is in seconds (e.g., 600 = 10 minutes)
- Follow spindle manufacturer's warmup recommendations (see User Manual 25.17)

### Modifying Movement Patterns

If changing the movement pattern in `subroutines/_N_WARMUP_CYCLE_SPF`:
- Always use `SUPA` for machine-absolute positioning
- Maintain safe Z-axis retraction before X/Y moves
- Test with `routines/TEST.MPF` (short duration cycles) before full warmup runs
- Verify moves stay within machine travel limits

### Safety Considerations

- Monitor for abnormal noise, vibration, or overheating during program execution
- The WHILE loop in _N_WARMUP_CYCLE_SPF uses `$AC_TIME` (system variable) for timing
- G4 F5 provides 5-second dwell after spindle start to reach target RPM
- Z-axis always retracts to 0 before X/Y moves to prevent collisions
