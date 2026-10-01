# PHREEQC Files from Sensitivity Analysis

The sensitivity-analysis workflow generates approximately **6,800 PHREEQC files**, comprising temperature- and scenario-specific PHREEQC input (`.pqi`), standard-output (`.out`), and selected-output (`.txt`) files.

The complete set of generated PHREEQC files is not included in this GitHub repository because of the large number of individual files and practical GitHub browser-upload limitations. Only the sensitivity-analysis code and associated summary results required to reproduce the analysis are provided.

## Reproducing the PHREEQC Files

The complete set of approximately 6,800 PHREEQC files can be regenerated automatically by running the sensitivity-analysis script from the repository root:

```bash
python code/sensitivity_analysis.py
```

During execution, the script automatically creates the PHREEQC input, standard-output, and selected-output files associated with each sensitivity-analysis simulation.

Therefore, the omitted files are **generated intermediate computational files rather than additional source data**. Running the supplied sensitivity-analysis code with the specified PHREEQC–FREZCHEM environment reproduces these files locally.

The consolidated sensitivity-analysis results are provided in:

```text
sensitivity_results/FC_FREZCHEM_Sensitivity_Results.xlsx
```

See the main repository `README.md` for the required Python, PHREEQC, thermodynamic database, and dependency versions.
