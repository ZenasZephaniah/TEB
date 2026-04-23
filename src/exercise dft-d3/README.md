# Analysis Results README

This file explains the main generated analysis folders in `D:\MLInChemistry\class3`.

## Main result folders

### `packing_efficiency_results/`

This folder contains the packing-efficiency analysis built from the configuration-level `delta_E` tables.

It is split into:

- `binary/`
  Results for binary systems (`metal-O` and `metal-S`)
- `ternary/`
  Results for ternary systems (`metal_1-metal_2-O` and `metal_1-metal_2-S`)

Inside each of those, you will usually find:

- `tables/`
  Merged data tables combining `delta_E` with packing-efficiency descriptors
- `plots/`
  Static PNG plots showing packing-efficiency trends
- `README.md`
  A short explanation of that specific sub-analysis

Important files:

- `packing_vs_delta_merged.csv`
  One row per configuration with both `delta_E` and packing metrics
- `chemsys_summary.csv`
  One row per chemsys summarizing intra-compound and inter-compound trends
- `configuration_packing_metrics.csv`
  Packing descriptors computed from the structures
- `packing_parse_errors.csv`
  Parsing or matching failures, if any

Purpose:

- examine whether packing efficiency is related to `delta_E`
- compare structure-level trends and chemsys-level trends

### `max_delta_point_results/`

This folder contains summary outputs where only one representative point is kept per category.

Selection rule used there:

- binary: one selected point per `(metal, ligand)`
- ternary: one selected point per `(metal pair, ligand)`

Files:

- `tables/binary_max_delta_points.csv`
  Selected binary rows
- `tables/ternary_max_delta_points.csv`
  Selected ternary rows
- `plots/binary_max_delta_points.png`
  Static binary plot
- `plots/ternary_max_delta_points.png`
  Static ternary plot
- `plots/binary_max_delta_points.html`
  Interactive binary version
- `plots/ternary_max_delta_points.html`
  Interactive ternary version

Purpose:

- reduce many configurations to one representative point per group
- compare groups quickly without plotting every configuration

Important note:

- this folder uses the explicitly chosen representative-point rule from that analysis step
- it is different from plotting full distributions or grouped means/medians

### `bar_graph_statistics/`

This folder contains grouped bar graphs built from the binary and ternary `delta_E` tables.

It includes grouped statistics for:

- `min`
- `max`
- `mean`
- `median`

for both:

- binary oxygen
- binary sulfur
- ternary oxygen
- ternary sulfur

Structure:

- `tables/`
  Grouped summary CSVs
- `plots/`
  Bar graphs for each statistic and ligand split
- `README.md`
  A short explanation of the grouped-statistics interpretation

Important files:

- `tables/binary_grouped_statistics.csv`
- `tables/ternary_grouped_statistics.csv`

Example plot names:

- `binary_oxygen_min_delta_bar.png`
- `binary_sulfur_mean_delta_bar.png`
- `ternary_oxygen_median_delta_bar.png`
- `ternary_sulfur_max_delta_bar.png`

Purpose:

- compare grouped `delta_E` summaries across metals or metal pairs
- visualize which systems are strongest, weakest, or typical according to the chosen statistic

Interpretation tip:

- `min delta_E` corresponds to the most negative `delta_E`, which matches the “strongest dip / strongest artifact” interpretation from your artifact summary
- `max delta_E` means the numerically largest value, usually the one closest to zero when all values are negative

### `binary_electronegativity_vs_delta/`

This folder contains binary-only scatter plots comparing metal electronegativity with grouped `delta_E` statistics.

It uses metal Pauling electronegativity on the x-axis and grouped binary `delta_E` values on the y-axis.

Plots included:

- oxygen: `min`, `max`, `mean`, `median`
- sulfur: `min`, `max`, `mean`, `median`

Structure:

- `tables/`
  Binary grouped statistics with electronegativity added
- `plots/`
  The 8 electronegativity-vs-`delta_E` scatter plots
- `README.md`
  A short explanation of the analysis

Important file:

- `tables/binary_grouped_statistics_with_electronegativity.csv`

Purpose:

- test whether metal electronegativity correlates with grouped binary `delta_E`
- compare O and S trends separately

## Related helper scripts

These scripts generated or support the folders above:

- `packing_efficiency_analysis.py`
- `plot_binary_metal_focus.py`
- `plot_binary_metal_focus_interactive.py`
- `plot_ternary_pair_focus_interactive.py`
- `max_delta_point_plots.py`
- `bar_graph_statistics.py`
- `binary_electronegativity_vs_delta.py`

## Quick guide

If you want:

- full packing-based configuration analysis:
  open `packing_efficiency_results/`
- one representative point per group:
  open `max_delta_point_results/`
- grouped summary bar graphs:
  open `bar_graph_statistics/`
- electronegativity trend analysis for binary systems:
  open `binary_electronegativity_vs_delta/`
