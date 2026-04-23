# Binary Packing Efficiency vs delta_E

- rows in merged table: `848`
- unique chemsys: `37`
- unique configurations: `848`
- overall corr(packing_fraction, delta_E): `-0.4156`
- chemsys with usable within-chemsys correlation: `32`
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

- `Mn-S`: `-0.8895` with `5` configurations
- `V-S`: `-0.8381` with `13` configurations
- `Sc-O`: `-0.8347` with `8` configurations
- `Fe-S`: `-0.8190` with `12` configurations
- `Y-S`: `-0.8011` with `4` configurations
- `Ta-S`: `-0.7823` with `6` configurations
- `Cr-S`: `-0.7185` with `7` configurations
- `Ti-S`: `-0.7046` with `14` configurations
- `Ta-O`: `-0.6899` with `6` configurations
- `Nb-S`: `-0.6390` with `13` configurations

## Strongest positive within-chemsys correlations

- `Zn-O`: `0.9709` with `5` configurations
- `Hf-O`: `0.8925` with `8` configurations
- `Zn-S`: `0.7103` with `98` configurations
- `Pd-O`: `0.6167` with `3` configurations
- `Pd-S`: `0.3166` with `3` configurations
- `Ni-S`: `0.2586` with `12` configurations
- `Nb-O`: `0.1876` with `17` configurations
- `Sc-S`: `0.1622` with `3` configurations
- `Y-O`: `-0.0930` with `19` configurations
- `Cr-O`: `-0.1059` with `52` configurations
