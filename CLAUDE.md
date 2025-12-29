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
   - `subroutines/WARMUP_CYCLE.SPF` - Core warmup routine that spins the spindle at specified RPM while executing a movement pattern

### WARMUP_CYCLE.SPF - The Core Subroutine

All main programs call `WARMUP_CYCLE(RPM, DURATION)` which:
- Spins spindle at specified RPM
- Executes timed movement pattern (90° moves + 45° diagonal moves)
- Uses **SUPA (machine-absolute positioning)** for all moves
- Pattern coordinates: X0 to X-5, Y0 to Y-5, Z0 to Z-4 (inches, negative direction from machine zero)
- Pattern repeats until duration (seconds) elapses

### G-code Conventions and Critical Syntax Rules

All programs follow these patterns:

**MPF Main Program Structure (REQUIRED):**
```gcode
; Program comments

EXTERN WARMUP_CYCLE(REAL, REAL)  ; REQUIRED for calling PROC with parameters

G70 G90 G17  ; G70=inch mode (positions only), G90=absolute, G17=XY plane
G700         ; G700=feedrate in inches/min (CRITICAL - G70 does NOT affect feedrate)

; Safe homing sequence
G0 SUPA Z0        ; Retract Z to machine zero FIRST (avoid collisions)
G0 SUPA X0 Y0     ; Then move X and Y to machine zero

WARMUP_CYCLE(3600, 600)  ; Subroutine calls

M5   ; Spindle stop
M02  ; End of program (use M02, not M30 for this controller)
```

**SPF Subroutine Structure (REQUIRED):**
```gcode
PROC WARMUP_CYCLE(REAL _RPM, REAL _DURATION)

DEF INT CYCLES
DEF INT COUNT
DEF REAL START_TIME
DEF REAL END_TIME
DEF REAL ELAPSED_TIME

G700  ; Feedrate in inches/min

M3 S=_RPM

; Capture start time (MUST use DO keyword with $AC_TIME)
DO START_TIME=$AC_TIME

; Loop logic using FOR (NOT WHILE)
FOR COUNT = 1 TO CYCLES
  ; Movement commands
  G1 SUPA Z-4 F100
  ; ... more moves
ENDFOR

; Capture end time and calculate actual elapsed time
DO END_TIME=$AC_TIME
ELAPSED_TIME = END_TIME - START_TIME

MSG("Warmup cycle complete - Actual time: "<<ELAPSED_TIME<<" seconds")

RET  ; REQUIRED - Returns from PROC (NOT ENDPROC or M17)
```

**CRITICAL Syntax Rules:**

1. **EXTERN Declaration**: REQUIRED in MPF files before calling PROC subroutines with parameters
2. **Feedrate Units**:
   - `G70` = Position coordinates in inches
   - `G700` = Feedrate in inches/min (MUST be specified separately)
   - `G71` = Position coordinates in mm
   - `G710` = Feedrate in mm/min
3. **PROC Termination**: Use `RET` (NOT `ENDPROC` or `M17`)
4. **Main Program Termination**: Use `M02` (NOT `M30` on this controller)
5. **Loop Structures**: Use `FOR...ENDFOR` (NOT `WHILE...ENDWHILE`)
6. **System Variables**: `$AC_TIME` can ONLY be used with `DO` keyword (e.g., `DO START_TIME=$AC_TIME`) to capture actual execution time in seconds
7. **SUPA Positioning**: All positioning uses `SUPA` (machine-absolute coordinates)
8. **Z-Axis Limits**: With SUPA, Z must be ≤ 0 (Z0 = machine zero, positive Z violates upper software limit)
9. **Output Messages**: Use `MSG("text"<<variable<<)` to display messages with variables. Example: `MSG("Total time: "<<_DURATION<<" seconds")`

## Machine-Specific Parameters

- **Max spindle speed**: 12,000 RPM
- **Critical safety check**: Monitor temperature rise during warmup. If >20°C (68°F), reduce to 1200 RPM (10% max)
- **Movement envelope**: Programs assume safe travel in X0 to X-5, Y0 to Y-5, Z0 to Z-4 (inches, negative direction from machine zero)

## Deployment

Programs must be manually transferred to the Siemens controller:

1. Copy `subroutines/WARMUP_CYCLE.SPF` to the controller's Subprograms folder (same directory as MPF files)
2. Copy main programs from `routines/` folder (.MPF files) to the controller's main program directory
3. Run `TEST.MPF` first to validate installation before running other routines

**File Naming:**
- Main programs: `FILENAME.MPF`
- Subroutines: `FILENAME.SPF`
- Controller may internally rename to `_N_FILENAME_MPF` or `_N_FILENAME_SPF` format

## Development Guidelines

### Modifying Warmup Sequences

When adjusting warmup parameters in main programs (in `routines/` folder):
- **RPM percentages** are based on 12,000 RPM max (e.g., 30% = 3600 RPM)
- **Duration** is in seconds (e.g., 600 = 10 minutes)
- Follow spindle manufacturer's warmup recommendations (see User Manual 25.17)

### Modifying Movement Patterns

If changing the movement pattern in `subroutines/WARMUP_CYCLE.SPF`:
- Always use `SUPA` for machine-absolute positioning
- **Z-axis restrictions**: Use Z0 or negative values only (positive Z violates upper limit with SUPA)
- Maintain safe Z-axis retraction before X/Y moves
- Set appropriate feedrate with `F` value (e.g., F100 = 100 inches/min with G700)
- Test with `routines/TEST.MPF` (short duration cycles) before full warmup runs
- Verify moves stay within machine travel limits

### Safety Considerations

- Monitor for abnormal noise, vibration, or overheating during program execution
- The FOR loop in WARMUP_CYCLE.SPF uses counter-based timing (approximate)
- G4 F5 provides 5-second dwell after spindle start to reach target RPM
- Z-axis always retracts to 0 (or safe negative value) before X/Y moves to prevent collisions
- Software limit switches prevent movement beyond safe boundaries

### Common Errors and Solutions

**"Illegal End of Program"**: Use `M02` instead of `M30` in main programs

**"Illegal End of File"**: Use `RET` (not `ENDPROC` or `M17`) to end PROC subroutines

**"Software Switch Violated"**: Z-axis with SUPA must be ≤ 0 (no positive Z values)

**"File Not Found" for subroutine**: Ensure WARMUP_CYCLE.SPF is in same directory as MPF files, add `EXTERN` declaration

**Slow feedrate**: Verify `G700` is set (G70 only affects position coordinates, not feedrate)

**Syntax error in DO statement**: `$AC_TIME` can only be used with `DO` keyword (e.g., `DO START_TIME=$AC_TIME`), not in regular variable assignments like `START_TIME = $AC_TIME`
