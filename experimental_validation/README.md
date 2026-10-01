# Experimental Validation

This directory contains the independent experimental-validation workflow for the PHREEQC–FREZCHEM freeze-crystallization framework.

## Files

- `frezpy_experiment_test.py` — runs the validation simulation.
- `plot_experimental_validation.py` — reproduces the supplementary validation figure.

No external Excel input file is required. The leachate composition and experimental/OLI comparison values are embedded directly in the validation script.

## Validation basis

The validation uses previously published freeze-crystallization data for a concentrated industrial leachate brine. Although the matrix differs from SWRO reject, both are concentrated aqueous electrolyte systems governed by the same fundamental freeze-crystallization processes: ice formation, freeze concentration of the residual liquid, and salt crystallization.

Experimental data provide the physical validation case. OLI Systems results are used separately as an independent thermodynamic cross-model benchmark and are not treated as experimental validation.

## Validation feed

- pH: 8.60
- TDS: 50,050 mg/L
- Na: 12,500 mg/L
- K: 100 mg/L
- Mg: 174 mg/L
- Ca: 61 mg/L
- Cl: 8,000 mg/L
- SO4: 16,000 mg/L
- HCO3: 296.777653 mg/L
- Density: 1.03211 kg/L

The simulation runs from 25 to -25 °C at -1 °C increments.

## Experimental comparison

The experimental run treated 273 L of leachate and recovered 118.7 kg of ice during a 5.5 h run. Ice recovery and mirabilite formation are used for experimental validation. Hydrohalite is not used as an experimental-validation target because it was not recovered experimentally.

## OLI benchmark

OLI results at 25, 0, -4 and -21 °C are embedded in the script and provide an independent cross-model comparison.

## Equilibrium phases

Ice(s), Mirabilite, Halite, Hydrohalite, Calcite and Gypsum.

## Required software

- PHREEQC 3.8.6-17100
- `frezchem.dat`
- Python 3.13.9
- NumPy
- pandas
- Matplotlib
- openpyxl

See the repository-level `requirements.txt` and `requirements-lock.txt` for dependency information.

## Run

```bash
python frezpy_experiment_test.py
```

The principal output is `frezpy_experiment_validation_results.xlsx`. The workflow also generates `LEACHATE_FREZCHEM_results.csv` and temperature-specific PHREEQC input, output and selected-output files.

## Reproduce the supplementary figure

```bash
python plot_experimental_validation.py
```

Outputs:

- `Figure_S_Experimental_Validation.png`
- `Figure_S_Experimental_Validation.pdf`

The four panels show FrezPy–OLI ice recovery, predicted sulphate recovery as mirabilite, FrezPy versus OLI ice-recovery agreement, and component/water mass-balance performance.

## Interpretation

The industrial-leachate experiment provides an independent physical test of the freeze-crystallization framework but does not imply identical recovery efficiencies for SWRO reject brines. The SWRO results are therefore interpreted as equilibrium thermodynamic recovery potentials.

## License

The Python code in this directory is released under the same MIT License as the main repository.
