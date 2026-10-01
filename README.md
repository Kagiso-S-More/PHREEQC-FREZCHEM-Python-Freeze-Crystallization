# PHREEQC–FREZCHEM Freeze Crystallization Model

Open-source computational framework for sequential freeze crystallization and resource recovery from seawater reverse-osmosis (SWRO) brines. The repository contains the manuscript model, sensitivity-analysis workflow, plotting scripts, model outputs and supporting PHREEQC files.

## Computational approach

Python controls the sequential cooling calculation and calls the PHREEQC command-line executable directly using `subprocess`; no PhreeqPy or IPhreeqc Python wrapper is used. The supplied scripts target PHREEQC **3.8.6-17100** and use `frezchem.dat` for the sub-zero thermodynamic calculations. The manuscript calculations use C3 and C5 brines over **25 to -25 °C** with a **-1 °C temperature increment**.

The equilibrium phase set in the supplied model comprises Ice(s), Mirabilite, Halite, Hydrohalite, Calcite and Gypsum. Newly formed solids are handled sequentially by the model according to the fractional-crystallization workflow described in the manuscript.

## Repository structure

```text
code/
  frezchem_model.py
  sensitivity_analysis.py
  plotting/
    figure_4_phase_evolution.py
    figure_5_freeze_concentration.py
    figure_6_water_recovery_benchmark.py
    figure_7_energy.py
input_data/
model_results/
sensitivity_results/
phreeqc_generated_files/
  C3/
  C5/
figures/
database/
requirements.txt
capture_environment.py
LICENSE
CITATION.cff
```

## Required software

- PHREEQC 3.8.6-17100
- Python (record the exact manuscript Python version before release)
- NumPy
- pandas
- Matplotlib
- openpyxl
- `frezchem.dat`

`requirements.txt` lists the required Python packages. For publication-grade reproducibility, run `python capture_environment.py` **inside the exact environment used for the final manuscript calculations**. This creates `requirements-lock.txt` from `pip freeze` and `PYTHON_VERSION.txt`; commit both files before creating the GitHub release. This avoids inventing dependency versions that cannot be recovered reliably from the scripts alone.

## Input files

Place the following files in `input_data/`:

- `C3_C5.xlsx`
- `OLI_Simulation_C3_and_C5_Brine.xlsx`

See `input_data/README.md`.

Place the exact manuscript `frezchem.dat` in `database/` if redistribution is permitted.

## Run the main model

From the repository root:

```bash
python code/frezchem_model.py
```

The principal workbook is written to:

```text
model_results/FC_frezchem_thermodynamic_results.xlsx
```

The repository also contains the supplied final manuscript result workbook as `model_results/FC_frezchem_thermodynamic_results_final.xlsx`.

## Run the sensitivity analysis

```bash
python code/sensitivity_analysis.py
```

The sensitivity workbook is written to:

```text
sensitivity_results/FC_FREZCHEM_Sensitivity_Results.xlsx
```

## Reproduce manuscript figures

The plotting scripts use the supplied final model workbook and can be run individually:

```bash
python code/plotting/figure_4_phase_evolution.py
python code/plotting/figure_5_freeze_concentration.py
python code/plotting/figure_6_water_recovery_benchmark.py
python code/plotting/figure_7_energy.py
```

PNG/PDF outputs are written to `figures/`.

## PHREEQC-generated files

The main and sensitivity workflows create temperature-specific PHREEQC input, standard-output and selected-output files. The author will add the manuscript-run files to `phreeqc_generated_files/C3/` and `phreeqc_generated_files/C5/` before publication.

## OLI benchmark

The comparison dataset was produced using **OLI Systems version 12**. Add the exact OLI input/benchmark workbook to `input_data/` as described above. OLI is proprietary software and is not distributed with this repository.

## Reproducibility checklist before public release

1. Add `C3_C5.xlsx` and `OLI_Simulation_C3_and_C5_Brine.xlsx`.
2. Add/document the exact `frezchem.dat` used.
3. Add the generated PHREEQC `.pqi`, `.out` and selected-output `.txt` files.
4. Run `python capture_environment.py` in the original manuscript environment and commit `requirements-lock.txt` and `PYTHON_VERSION.txt`.
5. Replace the placeholder repository URL in `CITATION.cff`.
6. Run the model, sensitivity analysis and all four plotting scripts from a clean checkout.
7. Create a GitHub release/tag (recommended: `v1.0.0-manuscript`).

## License

The Python source code in this repository is released under the MIT License. Third-party software, thermodynamic databases and OLI materials remain subject to their respective terms and are not relicensed by this repository.

## Citation

Please cite the associated manuscript and the versioned GitHub release when using this computational framework.
