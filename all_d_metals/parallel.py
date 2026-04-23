#!/usr/bin/env python3
"""
full_pipeline_3d_oxides_parallel.py
Fixed parallel version using concurrent.futures for nested parallelism
"""

import os
import sys
import time
import csv
import re
import shutil
import subprocess
from pathlib import Path
from typing import List, Tuple, Dict, Optional
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
from functools import partial

# external libs
try:
    from mp_api.client import MPRester
    from pymatgen.io.cif import CifWriter
    from pymatgen.core import Structure
    import pandas as pd
    import matplotlib
    matplotlib.use('Agg')  # Non-interactive backend for parallel plotting
    import matplotlib.pyplot as plt
except Exception as e:
    print("Missing dependency:", e)
    print("Install requirements: pip install mp-api pymatgen pandas matplotlib")
    sys.exit(1)

# --------------- USER CONFIG ---------------
MP_KEY_ENV = "MP_API_KEY"
MP_KEY_FILE = os.path.expanduser("~/.mp_api_key")
DEFAULT_METALS = ["Sc","Ti","V","Cr","Mn","Fe","Co","Ni","Cu","Zn"]
ROOT_DIR = Path("mp_pipeline_results")
CSV_DIR = ROOT_DIR / "csv"
POSCAR_DIR = ROOT_DIR / "poscars"
STRAIN_DIR = ROOT_DIR / "strains"
AGG_DIR = ROOT_DIR / "aggregated"
PLOT_DIR = ROOT_DIR / "plots"
S_DFTD3_CMD = "s-dftd3"
STRAIN_INDICES = list(range(-5, 30))
SLEEP_BETWEEN_API = 0.08
TIMEOUT_RUN = 900

# PARALLELIZATION SETTINGS
N_METAL_WORKERS = 10   # Run 10 metals in parallel
N_DFTD3_WORKERS = 4    # Each metal uses 4 workers for s-dftd3 calculations

FIELDS = [
    "material_id", "formula_pretty", "symmetry.crystal_system",
    "symmetry.symbol", "symmetry.number", "nsites",
    "energy_above_hull", "formation_energy_per_atom", "is_stable",
    "volume", "density", "band_gap", "is_gap_direct", "is_metal",
    "ordering", "total_magnetization",
]

# ---------------- helpers ------------------
def get_api_key() -> Optional[str]:
    k = os.environ.get(MP_KEY_ENV)
    if k:
        return k.strip()
    if os.path.exists(MP_KEY_FILE):
        return open(MP_KEY_FILE).read().strip()
    return None

def ensure_dirs():
    for d in [ROOT_DIR, CSV_DIR, POSCAR_DIR, STRAIN_DIR, AGG_DIR, PLOT_DIR]:
        d.mkdir(parents=True, exist_ok=True)

def sanitize_filename(s: str) -> str:
    if s is None:
        return "unknown"
    s = str(s).strip()
    s = re.sub(r'[^A-Za-z0-9._-]', '_', s)
    return s

# --------------- MP data fetch ----------------
def fetch_chemsys_write_csv(chemsys: str, api_key: str, max_results: int = None) -> Path:
    out_csv = CSV_DIR / f"{chemsys.replace(' ', '')}_table_export_with_structures.csv"
    
    print(f"[{chemsys}] Fetching from Materials Project...")
    with MPRester(api_key) as mpr:
        docs = mpr.materials.summary.search(chemsys=chemsys, fields=FIELDS, all_fields=False)
        docs = list(docs)
        if max_results:
            docs = docs[:max_results]
    
    print(f"[{chemsys}] Found {len(docs)} materials")
    
    rows = []
    for i, d in enumerate(docs, 1):
        mid = d.material_id
        try:
            with MPRester(api_key) as mpr:
                struct = mpr.materials.get_structure_by_material_id(mid)
            cif_text = str(CifWriter(struct))
        except Exception as exc:
            print(f"[{chemsys}] Warning: can't fetch structure {mid}: {exc}")
            cif_text = ""
        
        row = {
            "Synthesizable": True,
            "Material ID": mid,
            "Formula": d.formula_pretty,
            "Crystal System": getattr(d.symmetry, "crystal_system", None),
            "Space Group Symbol": getattr(d.symmetry, "symbol", None),
            "Space Group Number": getattr(d.symmetry, "number", None),
            "Sites": d.nsites,
            "Energy Above Hull": d.energy_above_hull,
            "Formation Energy": d.formation_energy_per_atom,
            "Predicted Stable": d.is_stable,
            "Volume": d.volume,
            "Density": d.density,
            "Band Gap": d.band_gap,
            "Is Gap Direct": d.is_gap_direct,
            "Is Metal": d.is_metal,
            "Magnetic Ordering": d.ordering,
            "Total Magnetization": d.total_magnetization,
            "Structure": cif_text,
        }
        rows.append(row)
        
        if i % 10 == 0:
            print(f"[{chemsys}] {i}/{len(docs)} fetched...")
        time.sleep(SLEEP_BETWEEN_API)
    
    df = pd.DataFrame(rows)
    df.to_csv(out_csv, index=False, quoting=csv.QUOTE_ALL)
    print(f"[{chemsys}] Wrote CSV: {out_csv}")
    return out_csv

# ------------- CSV -> POSCAR ------------------
def csv_to_poscars(csv_file: Path, out_poscar_dir: Path) -> int:
    out_poscar_dir.mkdir(parents=True, exist_ok=True)
    written = 0
    
    with open(csv_file, newline='', encoding='utf-8', errors='replace') as fh:
        reader = csv.DictReader(fh)
        if reader.fieldnames is None:
            raise SystemExit("No header found in CSV.")
        
        low_to_field = {name.lower().replace(" ", "").replace("_", ""): name 
                       for name in reader.fieldnames}
        
        def find_field(candidates):
            for cand in candidates:
                key = cand.lower().replace(" ", "").replace("_", "")
                if key in low_to_field:
                    return low_to_field[key]
            for name in reader.fieldnames:
                lname = name.lower()
                for cand in candidates:
                    if cand.lower() in lname:
                        return name
            return None
        
        formula_key = find_field(["formula"])
        structure_key = find_field(["structure", "cif", "structure_str"])
        material_key = find_field(["materialid", "material id", "material", "mpid"])
        
        if not formula_key or not structure_key:
            raise SystemExit("Couldn't find required columns in CSV.")
        
        for idx, row in enumerate(reader):
            try:
                formula = row.get(formula_key, "").strip() or f"unknown_{idx}"
                structure_str = row.get(structure_key, "")
                if not structure_str:
                    continue
                
                mid_raw = row.get(material_key, "").strip() if material_key else ""
                mid = mid_raw.replace("mp-", "").strip() if mid_raw else str(idx)
                
                safe_formula = sanitize_filename(formula)
                safe_mid = sanitize_filename(mid)
                
                cif_name = f"{safe_formula}_{safe_mid}.cif"
                cif_path = out_poscar_dir / cif_name
                
                with open(cif_path, "w", encoding="utf-8") as cf:
                    cf.write(structure_str)
                
                try:
                    structure = Structure.from_file(str(cif_path))
                except Exception as e:
                    cif_path.unlink(missing_ok=True)
                    continue
                
                poscar_name = f"{safe_formula}_{safe_mid}_POSCAR"
                poscar_path = out_poscar_dir / poscar_name
                
                with open(poscar_path, "w", encoding="utf-8") as pf:
                    pf.write(structure.to(fmt="poscar"))
                
                written += 1
            except Exception as exc:
                print(f"[poscar] Failed for row {idx}: {exc}")
    
    print(f"[poscar] Total POSCARs created: {written}")
    return written

# ------------- s-dftd3 parsing ----------------
def parse_output_for_props(text: str, cation_symbol: Optional[str]=None, 
                          anion_symbol: Optional[str]=None) -> Tuple[str,str,str,str,str]:
    CN_c = CN_a = C6_c = C6_a = "N/A"
    Edis = "N/A"
    lines = text.splitlines()
    
    for ln in lines:
        m = re.search(r"Dispersion\s+energy[:\s]+([-\d\.Ee+]+)", ln, re.I)
        if m:
            Edis = m.group(1)
            break
    
    elem_map = {}
    for ln in lines:
        toks = ln.split()
        if len(toks) >= 5:
            sym = toks[2]
            cn = toks[3]
            c6 = toks[4]
            if sym not in elem_map:
                elem_map[sym] = (cn, c6)
    
    if cation_symbol and cation_symbol in elem_map:
        CN_c, C6_c = elem_map[cation_symbol]
    elif elem_map:
        first = next(iter(elem_map))
        CN_c, C6_c = elem_map[first]
    
    if anion_symbol and anion_symbol in elem_map:
        CN_a, C6_a = elem_map[anion_symbol]
    elif len(elem_map) >= 2:
        second = list(elem_map.keys())[1]
        CN_a, C6_a = elem_map[second]
    elif elem_map:
        CN_a, C6_a = elem_map[next(iter(elem_map))]
    
    return CN_c, CN_a, C6_c, C6_a, Edis

# ------------- Single strain runner (no multiprocessing) --------
def run_single_strain(args):
    """Run s-dftd3 for a single strain index"""
    i, base_vectors, orig_lines, target_dir, results_dir, s_dftd3_cmd = args
    
    scale = 0.05 * i
    factor = 1.0 + scale
    new_vectors = [[v * factor for v in vec] for vec in base_vectors]
    
    poscar_name = f"POSCAR{i}"
    poscar_path = target_dir / poscar_name
    
    new_lines = list(orig_lines)
    while len(new_lines) < 5:
        new_lines.append("")
    
    def fmt_vec(v):
        return "{:18.10f} {:18.10f} {:18.10f}".format(v[0], v[1], v[2])
    
    new_lines[2] = fmt_vec(new_vectors[0])
    new_lines[3] = fmt_vec(new_vectors[1])
    new_lines[4] = fmt_vec(new_vectors[2])
    
    with open(poscar_path, "w") as wf:
        wf.write("\n".join(new_lines) + "\n")
    
    out_path = results_dir / f"out{i}.txt"
    cmd = [s_dftd3_cmd, "-i", "vasp", str(poscar_path), "--zero", "pbe", "--property", "--verbose"]
    
    try:
        if shutil.which(s_dftd3_cmd) is None:
            with open(out_path, "w") as outf:
                outf.write(f"=== RUN SKIPPED: {s_dftd3_cmd} not found in PATH ===\n")
        else:
            with open(out_path, "w") as outf:
                subprocess.run(cmd, stdout=outf, stderr=subprocess.STDOUT, timeout=TIMEOUT_RUN)
    except Exception as e:
        with open(out_path, "a") as outf:
            outf.write(f"\n\n=== RUN ERROR ===\n{e}\n")
    
    return i, poscar_path, out_path

def process_single_poscar(poscar_file, chemsys, s_dftd3_cmd, n_workers):
    """Process a single POSCAR file with parallel strain calculations using ThreadPoolExecutor"""
    base_name = poscar_file.stem
    target_dir = STRAIN_DIR / chemsys.replace(' ', '') / base_name
    results_dir = target_dir / "results"
    target_dir.mkdir(parents=True, exist_ok=True)
    results_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        with open(poscar_file, "r", errors="ignore") as pf:
            orig_lines = [ln.rstrip("\n") for ln in pf.readlines()]
    except Exception as e:
        print(f"[{chemsys}] Can't read {poscar_file}: {e}")
        return []
    
    if len(orig_lines) < 5:
        return []
    
    def parse_vector_line(line):
        parts = line.split()
        vals = []
        for p in parts[:3]:
            try:
                vals.append(float(p))
            except:
                vals.append(0.0)
        while len(vals) < 3:
            vals.append(0.0)
        return vals
    
    base_vectors = [
        parse_vector_line(orig_lines[2]),
        parse_vector_line(orig_lines[3]),
        parse_vector_line(orig_lines[4])
    ]
    
    elements = []
    if len(orig_lines) >= 6:
        parts = orig_lines[5].strip().split()
        if parts:
            elements = parts
    
    cation_symbol = elements[0] if elements else None
    anion_symbol = elements[-1] if elements else None
    
    # Prepare args for parallel execution
    strain_args = [
        (i, base_vectors, orig_lines, target_dir, results_dir, s_dftd3_cmd)
        for i in STRAIN_INDICES
    ]
    
    # Use ProcessPoolExecutor instead of Pool to avoid daemon issue
    print(f"[{chemsys}] Processing {poscar_file.name} with {n_workers} workers...")
    results = []
    with ProcessPoolExecutor(max_workers=n_workers) as executor:
        futures = [executor.submit(run_single_strain, arg) for arg in strain_args]
        for future in as_completed(futures):
            try:
                results.append(future.result())
            except Exception as e:
                print(f"[{chemsys}] Strain calculation failed: {e}")
    
    # Collect results
    rows = []
    for i, poscar_path, out_path in results:
        try:
            with open(poscar_path, "r") as pf:
                p_lines = pf.readlines()
            cell_length = p_lines[2].split()[0] if len(p_lines) >= 3 else "N/A"
        except:
            cell_length = "N/A"
        
        try:
            out_text = open(out_path, "r", errors="ignore").read()
        except:
            out_text = ""
        
        CN_c, CN_a, C6_c, C6_a, Edis = parse_output_for_props(
            out_text, cation_symbol, anion_symbol
        )
        
        row = {
            "source": base_name,
            "cell_length": cell_length,
            "CN_C": CN_c,
            "CN_A": CN_a,
            "C6_C": C6_c,
            "C6_A": C6_a,
            "Edis": Edis
        }
        rows.append(row)
    
    return rows

def run_strain_and_collect(poscar_dir: Path, chemsys: str, 
                           s_dftd3_cmd: str = S_DFTD3_CMD,
                           n_workers: int = N_DFTD3_WORKERS) -> Path:
    """Process all POSCARs sequentially, but each with parallel s-dftd3 execution"""
    agg_csv = AGG_DIR / f"{chemsys.replace(' ', '')}_output.csv"
    fieldnames = ["source", "cell_length", "CN_C", "CN_A", "C6_C", "C6_A", "Edis"]
    
    poscar_files = [f for f in sorted(poscar_dir.iterdir()) if f.is_file()]
    
    all_rows = []
    for poscar_file in poscar_files:
        rows = process_single_poscar(poscar_file, chemsys, s_dftd3_cmd, n_workers)
        all_rows.extend(rows)
    
    # Write aggregated CSV
    with open(agg_csv, "w", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_rows)
    
    print(f"[{chemsys}] Aggregated CSV written: {agg_csv}")
    return agg_csv

# --------------- plotting --------------------
def plot_aggregated_csv(agg_csv: Path, chemsys: str, 
                       y_min: float = -0.6, y_max: float = 0.0):
    df = pd.read_csv(agg_csv)
    df["cell_length"] = pd.to_numeric(df["cell_length"], errors="coerce")
    df["Edis"] = pd.to_numeric(df["Edis"], errors="coerce")
    df = df.dropna(subset=["cell_length","Edis","source"])
    
    if df.empty:
        print(f"[{chemsys}] No valid data to plot")
        return
    
    fig, ax = plt.subplots(figsize=(9,6))
    for source, grp in df.groupby("source"):
        ax.plot(grp["cell_length"], grp["Edis"], marker="o", 
               linestyle="-", label=source)
    
    ax.set_xlabel("Cell Length")
    ax.set_ylabel("Dispersion Energy (Edis)")
    ax.set_ylim(y_min, y_max)
    ax.legend(loc="center left", bbox_to_anchor=(1.02, 0.5), 
             fontsize=7, frameon=False)
    plt.title(f"{chemsys}: Edis vs cell length")
    plt.tight_layout()
    
    out_png = PLOT_DIR / f"{chemsys.replace(' ', '')}_cell_length_vs_Edis.png"
    fig.savefig(out_png, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"[{chemsys}] Saved plot: {out_png}")

# --------------- Per-metal pipeline -----------
def process_metal(metal: str, api_key: str):
    """Process a single metal through entire pipeline"""
    chemsys = f"{metal}-O"
    print(f"\n{'='*60}")
    print(f"[{chemsys}] START")
    print(f"{'='*60}")
    
    try:
        chemsys_tag = chemsys.replace(" ", "")
        csv_path = CSV_DIR / f"{chemsys_tag}_table_export_with_structures.csv"
        poscar_out_dir = POSCAR_DIR / chemsys_tag
        
        # Fetch data
        csv_path = fetch_chemsys_write_csv(chemsys, api_key)
        
        # CSV -> POSCAR
        poscar_out_dir.mkdir(parents=True, exist_ok=True)
        csv_to_poscars(csv_path, poscar_out_dir)
        
        # Run strains + s-dftd3
        agg_csv = run_strain_and_collect(poscar_out_dir, chemsys)
        
        # Plot
        plot_aggregated_csv(agg_csv, chemsys)
        
        print(f"[{chemsys}] DONE ✓")
        return chemsys, "SUCCESS"
    
    except Exception as e:
        print(f"[{chemsys}] ERROR: {e}")
        import traceback
        traceback.print_exc()
        return chemsys, f"FAILED: {e}"

# --------------- main pipeline ----------------
def pipeline_parallel(metals: List[str], api_key: str, n_metal_workers: int):
    """Run pipeline for multiple metals in parallel"""
    ensure_dirs()
    
    print(f"\n{'='*60}")
    print(f"Starting parallel pipeline:")
    print(f"  Metals: {metals}")
    print(f"  Metal workers: {n_metal_workers}")
    print(f"  s-dftd3 workers per metal: {N_DFTD3_WORKERS}")
    print(f"  Total potential parallelism: {n_metal_workers * N_DFTD3_WORKERS}")
    print(f"{'='*60}\n")
    
    # Process metals in parallel using ProcessPoolExecutor
    process_func = partial(process_metal, api_key=api_key)
    
    results = []
    with ProcessPoolExecutor(max_workers=n_metal_workers) as executor:
        futures = {executor.submit(process_func, metal): metal for metal in metals}
        for future in as_completed(futures):
            metal = futures[future]
            try:
                result = future.result()
                results.append(result)
            except Exception as e:
                print(f"[{metal}-O] FAILED with exception: {e}")
                results.append((f"{metal}-O", f"FAILED: {e}"))
    
    # Summary
    print(f"\n{'='*60}")
    print("PIPELINE COMPLETE - Summary:")
    print(f"{'='*60}")
    for chemsys, status in results:
        print(f"  {chemsys}: {status}")
    print(f"\nResults directory: {ROOT_DIR}")

# -------------- CLI / Entrypoint --------------
if __name__ == "__main__":
    api_key = get_api_key()
    if not api_key:
        print("Materials Project API key not found.")
        print("Set env var MP_API_KEY or place key in ~/.mp_api_key")
        sys.exit(1)
    
    metals = DEFAULT_METALS.copy()
    if len(sys.argv) > 1:
        metals = sys.argv[1:]
    
    import multiprocessing
    print("Configuration:")
    print(f"  ROOT_DIR: {ROOT_DIR}")
    print(f"  Metals: {metals}")
    print(f"  Available CPUs: {multiprocessing.cpu_count()}")
    print(f"  Metal workers: {N_METAL_WORKERS}")
    print(f"  s-dftd3 workers/metal: {N_DFTD3_WORKERS}")
    print(f"  s-dftd3 command: {S_DFTD3_CMD}")
    
    pipeline_parallel(metals, api_key, N_METAL_WORKERS)
