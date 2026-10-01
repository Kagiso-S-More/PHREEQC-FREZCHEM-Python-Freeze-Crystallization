# PHREEQC–FREZCHEM-Python Freeze Crystallization Model

Open-source computational framework for modelling sequential freeze crystallization and resource recovery from seawater reverse-osmosis (SWRO) brines. The repository contains the PHREEQC–FREZCHEM–Python model, sensitivity-analysis workflow, figure-generation scripts, input datasets, model outputs, and supporting PHREEQC input/output files associated with the study.

## Computational approach

Python controls the sequential cooling calculations and executes the PHREEQC command-line program directly using `subprocess`; no PhreeqPy or IPhreeqc Python wrapper is required. The framework uses **PHREEQC 3.8.6-17100** with the `frezchem.dat` thermodynamic database for sub-zero equilibrium calculations.

The principal simulations evaluate the C3 and C5 SWRO brines over a temperature range of **25 to −25 °C** using **1 °C cooling increments**. At each temperature node, PHREEQC calculates aqueous speciation, thermodynamic activities, saturation states, and equilibrium phase quantities, while Python manages sequential state transfer, product recovery, data processing, and output generation.

The permitted equilibrium phase assemblage comprises:

- Ice(s)
- Mirabilite
- Halite
- Hydrohalite
- Calcite
- Gypsum

Newly formed ice and mineral phases are treated as recovered products, and the residual aqueous state is propagated to the subsequent temperature node according to the sequential fractional-crystallization framework described in the associated manuscript.

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
  C3_C5.xlsx
  OLI_Simulation_C3_and_C5_Brine.xlsx

model_results/
  FC_frezchem_thermodynamic_results_final.xlsx

sensitivity_results/
  FC_FREZCHEM_Sensitivity_Results.xlsx
  phreeqc_files_for_Sensitivity_Analysis/

phreeqc_generated_files_for_main_model/

figures/
  Phase_Evolution.pdf
  Cross_Model_Performance.pdf
  Energy_Requirements.pdf
  FC_Chem_MassBalance.pdf

requirements.txt
capture_environment.py
LICENSE
CITATION.cff
README.md
```

## Software requirements

The manuscript calculations were performed using:

- **PHREEQC:** 3.8.6-17100
- **Python:** 3.13.9
- **NumPy:** 2.5.3
- **pandas:** 3.0.6
- **Matplotlib:** 3.11.2
- **openpyxl:** 3.1.5
- **Thermodynamic database:** `frezchem.dat`

Python dependencies are also specified in `requirements.txt`.

## Input data

The `input_data/` directory contains the source datasets required for the principal simulations and cross-model benchmarking:

- `C3_C5.xlsx` — C3 and C5 SWRO brine compositions used as inputs to the PHREEQC–FREZCHEM model.
- `OLI_Simulation_C3_and_C5_Brine.xlsx` — OLI Systems Version 12 simulation results used for cross-model benchmarking against the PHREEQC–FREZCHEM predictions.

These files allow the principal model calculations and benchmarking analyses to be reproduced directly from the repository.

## Running the main model

From the repository root, execute:

```bash
python code/frezchem_model.py
```

The main model performs the sequential PHREEQC–FREZCHEM calculations for C3 and C5 and generates the corresponding thermodynamic and recovery results.

The principal output workbook is written to:

```text
model_results/FC_frezchem_thermodynamic_results.xlsx
```

The final workbook corresponding to the manuscript calculations is also provided as:

```text
model_results/FC_frezchem_thermodynamic_results_final.xlsx
```

## Running the sensitivity analysis

Execute:

```bash
python code/sensitivity_analysis.py
```

The sensitivity-analysis results are written to:

```text
sensitivity_results/FC_FREZCHEM_Sensitivity_Results.xlsx
```

The associated PHREEQC files generated during the sensitivity calculations are retained in:

```text
sensitivity_results/phreeqc_files_for_Sensitivity_Analysis/
```

## Reproducing the manuscript figures

The manuscript plotting scripts can be executed individually from the repository root:

```bash
python code/plotting/figure_4_phase_evolution.py
python code/plotting/figure_5_freeze_concentration.py
python code/plotting/figure_6_water_recovery_benchmark.py
python code/plotting/figure_7_energy.py
```

The scripts use the supplied model and benchmarking results to reproduce the principal multi-panel figures reported in the manuscript. Figure outputs are written to the `figures/` directory.

## PHREEQC-generated files

The sequential modelling workflow generates temperature-specific PHREEQC input (`.pqi`), standard-output (`.out`), and selected-output (`.txt`) files. Files corresponding to the principal C3 and C5 simulations are retained in:

```text
phreeqc_generated_files_for_main_model/
```

The sensitivity-analysis PHREEQC files are retained separately in:

```text
sensitivity_results/phreeqc_files_for_Sensitivity_Analysis/
```

These files are provided to support inspection of the individual equilibrium calculations and improve reproducibility of the sequential modelling workflow.

## OLI benchmarking

PHREEQC–FREZCHEM predictions were benchmarked against independent simulations performed using **OLI Systems Version 12**. Comparisons were performed at common temperature nodes and evaluated using phase behaviour, ice and mineral recovery, endpoint differences, mean absolute error (MAE), root mean square error (RMSE), mean bias error (MBE), and maximum absolute error (MaxAE).

The OLI benchmark results required for the comparisons are provided in:

```text
input_data/OLI_Simulation_C3_and_C5_Brine.xlsx
```

OLI Systems is proprietary software and is not distributed with this repository.

## Reproducibility workflow

To reproduce the principal computational results:

1. Install Python and the required packages listed above or in `requirements.txt`.
2. Install PHREEQC 3.8.6-17100 and ensure that the PHREEQC executable is accessible to the model.
3. Ensure that the required `frezchem.dat` thermodynamic database is available to PHREEQC.
4. Run `python code/frezchem_model.py` to reproduce the principal C3 and C5 simulations.
5. Run `python code/sensitivity_analysis.py` to reproduce the sensitivity analysis.
6. Run the individual scripts in `code/plotting/` to reproduce the principal manuscript figures.

The supplied result workbooks and PHREEQC-generated files provide reference outputs for comparison with a reproduced run.

## Scope and limitations

The framework represents **equilibrium sequential fractional crystallization** rather than crystallization kinetics. Nucleation induction time, crystal-growth rates, crystal-size distributions, hydrodynamics, ion entrapment within ice, adhering brine, ice washing, and product-water quality are not explicitly simulated.

The energy calculations included in the framework represent simplified refrigeration-energy estimates based on sensible cooling and latent heat removal. They should not be interpreted as complete process specific energy consumption because auxiliary requirements such as pumping, mixing, heat losses, ice separation and washing, and crystal handling are excluded.

Model predictions should therefore be interpreted as thermodynamic screening results rather than experimentally validated full-scale process predictions.

## License

The Python source code developed for this repository is released under the **MIT License**. Third-party software, thermodynamic databases, and OLI Systems materials remain subject to their respective licensing and distribution terms and are not relicensed by this repository.

## Citation

If you use this computational framework, please cite the associated manuscript and the corresponding versioned GitHub release. Citation metadata for the repository are provided in `CITATION.cff`.
