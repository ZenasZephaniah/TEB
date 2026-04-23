# Ternary Packing Efficiency vs delta_E

- rows in merged table: `1186`
- unique chemsys: `198`
- unique configurations: `1186`
- overall corr(packing_fraction, delta_E): `-0.4795`
- chemsys with usable within-chemsys correlation: `121`
- parse / matching errors: `0`

## Tables

- `configuration_packing_metrics.csv`: one row per configuration with packing descriptors
- `packing_vs_delta_merged.csv`: delta rows merged with packing descriptors
- `chemsys_summary.csv`: one row per chemsys for inter-compound comparison
- `packing_parse_errors.csv`: parse or matching failures

## Recommended starting points

- Use `packing_vs_delta_merged.csv` for configuration-level analysis
- Use `chemsys_summary.csv` for equal-weight chemsys comparison
- Use `packing_vs_delta_corr` and `packing_vs_delta_slope` for intra-compound trends

## Strongest negative within-chemsys correlations

- `Cd-Mn-S`: `-1.0000` with `2` configurations
- `Hf-Zr-O`: `-1.0000` with `2` configurations
- `Re-Sc-O`: `-1.0000` with `2` configurations
- `Ti-Y-S`: `-1.0000` with `2` configurations
- `Cd-V-O`: `-1.0000` with `2` configurations
- `Ni-Rh-O`: `-1.0000` with `2` configurations
- `Nb-Zr-O`: `-1.0000` with `2` configurations
- `Hf-Mo-S`: `-1.0000` with `2` configurations
- `Co-Sc-O`: `-1.0000` with `2` configurations
- `Cu-Nb-O`: `-1.0000` with `2` configurations

## Strongest positive within-chemsys correlations

- `Cd-Ti-O`: `1.0000` with `2` configurations
- `Rh-Sc-O`: `1.0000` with `2` configurations
- `Co-Ta-S`: `1.0000` with `2` configurations
- `Cr-Nb-S`: `1.0000` with `2` configurations
- `Nb-Ti-S`: `1.0000` with `2` configurations
- `Fe-Ta-S`: `1.0000` with `2` configurations
- `Mo-Zn-O`: `1.0000` with `2` configurations
- `Co-Mo-O`: `1.0000` with `2` configurations
- `Cr-Ni-S`: `1.0000` with `2` configurations
- `Hg-Y-O`: `1.0000` with `2` configurations
