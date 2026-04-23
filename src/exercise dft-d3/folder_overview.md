# Folder Overview

This note summarizes what is present in `D:\MLInChemistry\class3` and what the main CSV files contain.

## Root folder

The main working folders are:

- `all_d_metals/`
  Binary systems: one metal + one ligand (`M-O` or `M-S`)
- `all_3_metals/`
  Ternary systems: two different metals + one ligand (`M1-M2-O` or `M1-M2-S`)

Other root files:

- `artifact_summary_report.txt`
  A text summary generated from the processed binary and ternary results
- `temp.py`
  A helper/report script that reads summary CSVs and writes `artifact_summary_report.txt`
- `prompt.md`
  Currently empty

## `all_d_metals/`

This folder contains the binary analysis pipeline and its outputs.

Contents:

- `csv/` (`58` files)
  Raw Materials Project export CSVs for binary systems
- `aggregated/` (`58` files)
  Strain-scan output CSVs produced from the raw structures
- `delta_analysis/`
  Contains per-compound delta-energy summary CSVs, one combined CSV, and a `plots/` folder with per-structure images
- `plots/` (`58` files)
  Basic per-compound plots of cell length vs `Edis`
- `comparison_plots_top_bottom_binary/` (`13` files)
  High-level summary plots/tables comparing strongest vs weakest accepted binary artifacts
- `run_all.py`
  Main binary pipeline script
- `parallel.py`
  Parallel binary workflow code
- `delta_calc.py`
  Computes dip / delta-energy summaries from aggregated scans
- `figure.py`
  Builds the binary comparison plots and summary tables

### Binary compounds present

There are `29` metals, each with oxide and sulfide versions:

`Ag, Au, Cd, Co, Cr, Cu, Fe, Hf, Hg, Ir, Mn, Mo, Nb, Ni, Os, Pd, Pt, Re, Rh, Ru, Sc, Ta, Tc, Ti, V, W, Y, Zn, Zr`

So the raw binary compound list is:

`Ag-O, Ag-S, Au-O, Au-S, Cd-O, Cd-S, Co-O, Co-S, Cr-O, Cr-S, Cu-O, Cu-S, Fe-O, Fe-S, Hf-O, Hf-S, Hg-O, Hg-S, Ir-O, Ir-S, Mn-O, Mn-S, Mo-O, Mo-S, Nb-O, Nb-S, Ni-O, Ni-S, Os-O, Os-S, Pd-O, Pd-S, Pt-O, Pt-S, Re-O, Re-S, Rh-O, Rh-S, Ru-O, Ru-S, Sc-O, Sc-S, Ta-O, Ta-S, Tc-O, Tc-S, Ti-O, Ti-S, V-O, V-S, W-O, W-S, Y-O, Y-S, Zn-O, Zn-S, Zr-O, Zr-S`

### What the binary CSV types contain

Raw CSVs in `all_d_metals/csv/` use this schema:

- `Synthesizable`
- `Material ID`
- `Formula`
- `Crystal System`
- `Space Group Symbol`
- `Space Group Number`
- `Sites`
- `Energy Above Hull`
- `Formation Energy`
- `Predicted Stable`
- `Volume`
- `Density`
- `Band Gap`
- `Is Gap Direct`
- `Is Metal`
- `Magnetic Ordering`
- `Total Magnetization`
- `Structure`

Meaning:

- one row = one Materials Project material for that binary chemsystem
- `Structure` stores the structure text used later to generate POSCARs / scans

Aggregated CSVs in `all_d_metals/aggregated/` use:

- `source`
- `cell_length`
- `CN_C`
- `CN_A`
- `C6_C`
- `C6_A`
- `Edis`

Meaning:

- one row = one sampled strain point for one source structure
- these files are used to build the energy-vs-cell-length curves

Delta-analysis CSVs in `all_d_metals/delta_analysis/` use:

- `chemsys`
- `source`
- `n_points`
- `dip_method`
- `dip_cell_length`
- `E_min`
- `E_expected`
- `delta_E`
- `left_x`
- `right_x`
- `baseline_slope`

Meaning:

- one row = one detected dip / artifact summary for one source structure
- `all_deltaE_combined.csv` stacks all accepted binary delta rows together

### Current binary processing coverage

- raw CSVs: `58`
- aggregated CSVs: `58`
- per-compound delta CSVs: `37`
- combined binary delta CSV: `1` (`all_deltaE_combined.csv`)

This means all raw binary systems were aggregated, but only a subset currently has accepted delta-analysis CSV outputs.

## `all_3_metals/`

This folder contains the ternary analysis pipeline and its outputs.

Contents:

- `csv/` (`812` files)
  Raw Materials Project export CSVs for ternary systems
- `aggregated/` (`430` files)
  Strain-scan output CSVs for ternary compounds that were processed
- `delta_analysis_ternary/`
  Contains per-compound delta-energy summary CSVs, one combined CSV, and a `plots/` folder with per-structure images
- `plots/` (`430` files)
  Basic per-compound plots of cell length vs `Edis`
- `comparison_plots/` (`231` files)
  Older/general ternary comparison outputs
- `comparison_plots_top/` (`50` files)
  Top-ranked ternary comparisons
- `comparison_plots_top_bottom_ternary/` (`19` files)
  High-level strongest-vs-weakest ternary summary plots/tables
- `run.py`
  Main ternary pipeline script
- `delta.py`
  Computes ternary dip / delta-energy summaries
- `figure.py`
  Builds ternary comparison plots and summary tables

### Ternary compounds present

The ternary folder uses unordered distinct metal pairs from the same `29` metals listed above, with two ligands:

- `M1-M2-O`
- `M1-M2-S`

There are `406` unique metal pairs, so:

- `406 x 2 = 812` raw ternary chemsystem CSVs

Examples:

- `Ag-Au-O`, `Ag-Au-S`
- `Ag-Fe-O`, `Ag-Fe-S`
- `Co-Ni-O`, `Co-Ni-S`
- `Ti-Zr-O`, `Ti-Zr-S`
- `Y-Zr-O`, `Y-Zr-S`
- `Zn-Zr-O`, `Zn-Zr-S`

These are distinct-metal pairs only; there are no same-metal ternary names like `Sc-Sc-O`.

### What the ternary CSV types contain

Raw CSVs in `all_3_metals/csv/` use the same schema as the binary raw CSVs:

- `Synthesizable`
- `Material ID`
- `Formula`
- `Crystal System`
- `Space Group Symbol`
- `Space Group Number`
- `Sites`
- `Energy Above Hull`
- `Formation Energy`
- `Predicted Stable`
- `Volume`
- `Density`
- `Band Gap`
- `Is Gap Direct`
- `Is Metal`
- `Magnetic Ordering`
- `Total Magnetization`
- `Structure`

Aggregated CSVs in `all_3_metals/aggregated/` use:

- `source`
- `cell_length`
- `CN_C`
- `CN_A`
- `C6_C`
- `C6_A`
- `Edis`

Delta-analysis CSVs in `all_3_metals/delta_analysis_ternary/` use:

- `chemsys`
- `metal_1`
- `metal_2`
- `ligand`
- `source`
- `n_points`
- `dip_method`
- `dip_cell_length`
- `E_min`
- `E_expected`
- `delta_E`
- `left_x`
- `right_x`
- `baseline_slope`

Meaning:

- one row = one detected dip / artifact summary for one ternary source structure
- `all_ternary_deltaE_combined.csv` stacks all accepted ternary delta rows together

### Current ternary processing coverage

- raw CSVs: `812`
- aggregated CSVs: `430`
- per-compound delta CSVs: `198`
- combined ternary delta CSV: `1` (`all_ternary_deltaE_combined.csv`)

This means the ternary search space is much larger, and only part of it has been fully processed into aggregated and delta-analysis outputs.

## Summary of naming conventions

Raw export CSV names:

- binary: `M-L_table_export_with_structures.csv`
- ternary: `M1-M2-L_table_export_with_structures.csv`

Aggregated scan CSV names:

- binary: `M-L_output.csv`
- ternary: `M1-M2-L_output.csv`

Delta-analysis CSV names:

- binary: `M-L_deltaE.csv`
- ternary: `M1-M2-L_deltaE.csv`

Combined delta CSV names:

- binary: `all_deltaE_combined.csv`
- ternary: `all_ternary_deltaE_combined.csv`

## Most important interpretation

The project is organized in layers:

1. Raw Materials Project export CSVs with structure text
2. Aggregated strain-scan CSVs with `cell_length` and `Edis`
3. Delta-analysis CSVs with dip positions and `delta_E`
4. Plot folders and comparison-summary folders built from the processed CSVs
