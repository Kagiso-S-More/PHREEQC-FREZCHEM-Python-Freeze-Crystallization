#########################
######  Water Recovery and Cross-Model Performance  ########
#########################

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# ============================================================
# FILE PATHS
# ============================================================

ROOT = Path(__file__).resolve().parents[2]
WORKDIR = ROOT
(ROOT / "figures").mkdir(parents=True, exist_ok=True)

INPUT_FILE = ROOT / "model_results" / "FC_frezchem_thermodynamic_results_final.xlsx"

OUTPUT_PNG = ROOT / "figures" / "Figure_6_Cross_Model_Performance.png"
OUTPUT_PDF = ROOT / "figures" / "Figure_6_Cross_Model_Performance.pdf"

# ============================================================
# FIGURE SETTINGS
# ============================================================

TITLE_FS = 13
LABEL_FS = 13
TICK_FS = 11
LEGEND_FS = 9

LINE_WIDTH = 1.7
MARKER_SIZE = 6

plt.rcParams.update({
    "font.family": "Arial",
    "font.size": TICK_FS,
    "axes.titlesize": TITLE_FS,
    "axes.labelsize": LABEL_FS,
    "xtick.labelsize": TICK_FS,
    "ytick.labelsize": TICK_FS,
    "legend.fontsize": LEGEND_FS,
    "axes.linewidth": 1.0,
})

# ============================================================
# READ FINAL RESULTS
# ============================================================

c3 = pd.read_excel(
    INPUT_FILE,
    sheet_name="C3_FREZ_Detailed"
)

c5 = pd.read_excel(
    INPUT_FILE,
    sheet_name="C5_FREZ_Detailed"
)

oli_c3 = pd.read_excel(
    INPUT_FILE,
    sheet_name="OLI_C3_Raw"
)

oli_c5 = pd.read_excel(
    INPUT_FILE,
    sheet_name="OLI_C5_Raw"
)

# Sort from warm to cold
c3 = (
    c3.sort_values("temperature_c", ascending=False)
    .reset_index(drop=True)
)

c5 = (
    c5.sort_values("temperature_c", ascending=False)
    .reset_index(drop=True)
)

oli_c3 = (
    oli_c3.sort_values("temperature_c", ascending=False)
    .reset_index(drop=True)
)

oli_c5 = (
    oli_c5.sort_values("temperature_c", ascending=False)
    .reset_index(drop=True)
)

# ============================================================
# MATCH PHREEQC TO THE EXACT OLI TEMPERATURES
# ============================================================

# OLI was evaluated at:
# 25, 20, 15, 10, 5, 0, -5, -10, -15, -20, -25 °C
#
# The PHREEQC simulation has a 1 °C grid, so exact matching
# can be performed without interpolation.

c3_match = pd.merge(
    oli_c3[[
        "temperature_c",
        "oli_ice_recovery_pct"
    ]],
    c3[[
        "temperature_c",
        "ice_recovery_pct"
    ]],
    on="temperature_c",
    how="inner"
)

c5_match = pd.merge(
    oli_c5[[
        "temperature_c",
        "oli_ice_recovery_pct"
    ]],
    c5[[
        "temperature_c",
        "ice_recovery_pct"
    ]],
    on="temperature_c",
    how="inner"
)

# Rename for clarity
c3_match = c3_match.rename(
    columns={
        "ice_recovery_pct": "phreeqc_ice_recovery_pct"
    }
)

c5_match = c5_match.rename(
    columns={
        "ice_recovery_pct": "phreeqc_ice_recovery_pct"
    }
)

# ============================================================
# CALCULATE ICE-RECOVERY ERRORS
# ============================================================

# Error convention:
# PHREEQC - OLI
#
# Positive = PHREEQC overprediction
# Negative = PHREEQC underprediction

c3_match["error_pp"] = (
    c3_match["phreeqc_ice_recovery_pct"]
    - c3_match["oli_ice_recovery_pct"]
)

c5_match["error_pp"] = (
    c5_match["phreeqc_ice_recovery_pct"]
    - c5_match["oli_ice_recovery_pct"]
)

# ============================================================
# ERROR-STATISTIC FUNCTION
# ============================================================

def error_statistics(df):

    error = df["error_pp"].to_numpy()

    mae = np.mean(np.abs(error))

    rmse = np.sqrt(
        np.mean(error ** 2)
    )

    mbe = np.mean(error)

    max_abs = np.max(
        np.abs(error)
    )

    return {
        "N": len(error),
        "MAE": mae,
        "RMSE": rmse,
        "MBE": mbe,
        "MAX_ABS": max_abs
    }


c3_stats = error_statistics(c3_match)
c5_stats = error_statistics(c5_match)

# ============================================================
# EXTRACT FINAL -25 °C RESULTS
# ============================================================

c3_end = c3.loc[
    np.isclose(
        c3["temperature_c"],
        -25
    )
].iloc[0]

c5_end = c5.loc[
    np.isclose(
        c5["temperature_c"],
        -25
    )
].iloc[0]

oli_c3_end = oli_c3.loc[
    np.isclose(
        oli_c3["temperature_c"],
        -25
    )
].iloc[0]

oli_c5_end = oli_c5.loc[
    np.isclose(
        oli_c5["temperature_c"],
        -25
    )
].iloc[0]

# ============================================================
# FINAL RECOVERY ARRAYS
# ============================================================

categories = [
    "Ice",
    "SO$_4^{2-}$\nas mirabilite",
    "Na as\nhydrohalite",
    "Cl as\nhydrohalite"
]

# C3
c3_phreeqc_final = np.array([
    c3_end["ice_recovery_pct"],
    c3_end["so4_recovery_as_mirabilite_pct"],
    c3_end["na_recovery_as_hydrohalite_pct"],
    c3_end["cl_recovery_as_hydrohalite_pct"]
])

c3_oli_final = np.array([
    oli_c3_end["oli_ice_recovery_pct"],
    oli_c3_end["oli_so4_recovery_as_mirabilite_pct"],
    oli_c3_end["oli_na_recovery_as_hydrohalite_pct"],
    oli_c3_end["oli_cl_recovery_as_hydrohalite_pct"]
])

# C5
c5_phreeqc_final = np.array([
    c5_end["ice_recovery_pct"],
    c5_end["so4_recovery_as_mirabilite_pct"],
    c5_end["na_recovery_as_hydrohalite_pct"],
    c5_end["cl_recovery_as_hydrohalite_pct"]
])

c5_oli_final = np.array([
    oli_c5_end["oli_ice_recovery_pct"],
    oli_c5_end["oli_so4_recovery_as_mirabilite_pct"],
    oli_c5_end["oli_na_recovery_as_hydrohalite_pct"],
    oli_c5_end["oli_cl_recovery_as_hydrohalite_pct"]
])

# ============================================================
# HELPER FUNCTIONS
# ============================================================

def style_temperature_axis(ax):

    ax.tick_params(
        axis="both",
        which="both",
        direction="in",
        top=True,
        right=True
    )

    for spine in ax.spines.values():
        spine.set_visible(True)
        spine.set_linewidth(1.0)

    ax.set_xlim(25, -25)

    ax.set_xticks([
        25, 15, 5, -5, -15, -25
    ])


def style_axis(ax):

    ax.tick_params(
        axis="both",
        which="both",
        direction="in",
        top=True,
        right=True
    )

    for spine in ax.spines.values():
        spine.set_visible(True)
        spine.set_linewidth(1.0)


# ============================================================
# CREATE 2 × 2 FIGURE
# ============================================================

fig, axes = plt.subplots(
    nrows=2,
    ncols=2,
    figsize=(12, 9.5)
)

ax1, ax2, ax3, ax4 = axes.flatten()

# ============================================================
# (a) C3 ICE RECOVERY
# ============================================================

ax1.plot(
    c3["temperature_c"],
    c3["ice_recovery_pct"],
    linewidth=LINE_WIDTH,
    label="PHREEQC-FREZCHEM"
)

ax1.plot(
    oli_c3["temperature_c"],
    oli_c3["oli_ice_recovery_pct"],
    linestyle="none",
    marker="o",
    markersize=MARKER_SIZE,
    label="OLI"
)

ax1.set_title(
    r"$\bf{(a)}$ C3 ice recovery",
    fontsize=TITLE_FS,
    pad=10
)

ax1.set_xlabel(
    "Temperature (°C)",
    fontsize=LABEL_FS
)

ax1.set_ylabel(
    "Cumulative ice recovery (%)",
    fontsize=LABEL_FS
)

ax1.set_ylim(
    0,
    100
)

ax1.legend(
    frameon=False,
    fontsize=LEGEND_FS
)

style_temperature_axis(ax1)

# ============================================================
# (b) C5 ICE RECOVERY
# ============================================================

ax2.plot(
    c5["temperature_c"],
    c5["ice_recovery_pct"],
    linewidth=LINE_WIDTH,
    label="PHREEQC-FREZCHEM"
)

ax2.plot(
    oli_c5["temperature_c"],
    oli_c5["oli_ice_recovery_pct"],
    linestyle="none",
    marker="s",
    markersize=MARKER_SIZE,
    label="OLI"
)

ax2.set_title(
    r"$\bf{(b)}$ C5 ice recovery",
    fontsize=TITLE_FS,
    pad=10
)

ax2.set_xlabel(
    "Temperature (°C)",
    fontsize=LABEL_FS
)

ax2.set_ylabel(
    "Cumulative ice recovery (%)",
    fontsize=LABEL_FS
)

ax2.set_ylim(
    0,
    100
)

ax2.legend(
    frameon=False,
    fontsize=LEGEND_FS
)

style_temperature_axis(ax2)

# ============================================================
# (c) ICE-RECOVERY ERROR AT COMMON TEMPERATURES
# ============================================================

ax3.plot(
    c3_match["temperature_c"],
    c3_match["error_pp"],
    marker="o",
    markersize=MARKER_SIZE,
    linewidth=LINE_WIDTH,
    label="C3"
)

ax3.plot(
    c5_match["temperature_c"],
    c5_match["error_pp"],
    marker="s",
    markersize=MARKER_SIZE,
    linewidth=LINE_WIDTH,
    linestyle="--",
    label="C5"
)

# Zero-error reference line
ax3.axhline(
    y=0,
    color="black",
    linestyle=":",
    linewidth=1.0
)

ax3.set_title(
    r"$\bf{(c)}$ Ice-recovery prediction error",
    fontsize=TITLE_FS,
    pad=10
)

ax3.set_xlabel(
    "Temperature (°C)",
    fontsize=LABEL_FS
)

ax3.set_ylabel(
    "PHREEQC − OLI (percentage points)",
    fontsize=LABEL_FS
)

ax3.legend(
    frameon=False,
    fontsize=LEGEND_FS
)

style_temperature_axis(ax3)

# ============================================================
# (d) FINAL RECOVERY COMPARISON AT -25 °C
# ============================================================

x = np.arange(
    len(categories)
)

width = 0.19

# Four bars per recovery indicator:
# C3 PHREEQC
# C3 OLI
# C5 PHREEQC
# C5 OLI

bars1 = ax4.bar(
    x - 1.5 * width,
    c3_phreeqc_final,
    width,
    label="C3 PHREEQC"
)

bars2 = ax4.bar(
    x - 0.5 * width,
    c3_oli_final,
    width,
    label="C3 OLI"
)

bars3 = ax4.bar(
    x + 0.5 * width,
    c5_phreeqc_final,
    width,
    label="C5 PHREEQC"
)

bars4 = ax4.bar(
    x + 1.5 * width,
    c5_oli_final,
    width,
    label="C5 OLI"
)

ax4.set_title(
    r"$\bf{(d)}$ Final recovery at −25 °C",
    fontsize=TITLE_FS,
    pad=10
)

ax4.set_ylabel(
    "Recovery (%)",
    fontsize=LABEL_FS
)

ax4.set_xlabel(
    "Recovered component",
    fontsize=LABEL_FS
)

ax4.set_xticks(x)

ax4.set_xticklabels(
    categories
)

ax4.set_ylim(
    0,
    105
)

ax4.legend(
    frameon=False,
    fontsize=LEGEND_FS,
    ncol=2
)

style_axis(ax4)

# ============================================================
# LAYOUT
# ============================================================

fig.subplots_adjust(
    left=0.09,
    right=0.98,
    bottom=0.10,
    top=0.96,
    wspace=0.28,
    hspace=0.35
)

# ============================================================
# SAVE
# ============================================================

fig.savefig(
    OUTPUT_PNG,
    dpi=600,
    bbox_inches="tight"
)

fig.savefig(
    OUTPUT_PDF,
    bbox_inches="tight"
)

plt.show()

# ============================================================
# PRINT ICE ERROR STATISTICS
# ============================================================

print("\n============================================")
print("FIGURE 6 GENERATED SUCCESSFULLY")
print("============================================")

print(f"\nPNG:\n{OUTPUT_PNG}")
print(f"\nPDF:\n{OUTPUT_PDF}")

print("\n============================================")
print("ICE RECOVERY ERROR STATISTICS")
print("PHREEQC - OLI")
print("============================================")

print("\nC3")
print(f"N = {c3_stats['N']}")
print(f"MAE = {c3_stats['MAE']:.6f} pp")
print(f"RMSE = {c3_stats['RMSE']:.6f} pp")
print(f"MBE = {c3_stats['MBE']:.6f} pp")
print(
    f"Maximum absolute error = "
    f"{c3_stats['MAX_ABS']:.6f} pp"
)

print("\nC5")
print(f"N = {c5_stats['N']}")
print(f"MAE = {c5_stats['MAE']:.6f} pp")
print(f"RMSE = {c5_stats['RMSE']:.6f} pp")
print(f"MBE = {c5_stats['MBE']:.6f} pp")
print(
    f"Maximum absolute error = "
    f"{c5_stats['MAX_ABS']:.6f} pp"
)

# ============================================================
# PRINT POINT-BY-POINT ICE COMPARISON
# ============================================================

print("\n============================================")
print("C3 ICE COMPARISON")
print("============================================")

print(
    c3_match[
        [
            "temperature_c",
            "phreeqc_ice_recovery_pct",
            "oli_ice_recovery_pct",
            "error_pp"
        ]
    ].to_string(index=False)
)

print("\n============================================")
print("C5 ICE COMPARISON")
print("============================================")

print(
    c5_match[
        [
            "temperature_c",
            "phreeqc_ice_recovery_pct",
            "oli_ice_recovery_pct",
            "error_pp"
        ]
    ].to_string(index=False)
)

# ============================================================
# PRINT FINAL RECOVERY COMPARISON
# ============================================================

print("\n============================================")
print("FINAL RECOVERY COMPARISON AT -25 °C")
print("============================================")

final_table = pd.DataFrame({
    "Recovery indicator": [
        "Ice",
        "SO4 as mirabilite",
        "Na as hydrohalite",
        "Cl as hydrohalite"
    ],

    "C3 PHREEQC": c3_phreeqc_final,
    "C3 OLI": c3_oli_final,
    "C3 Delta_pp": (
        c3_phreeqc_final
        - c3_oli_final
    ),

    "C5 PHREEQC": c5_phreeqc_final,
    "C5 OLI": c5_oli_final,
    "C5 Delta_pp": (
        c5_phreeqc_final
        - c5_oli_final
    )
})

print(
    final_table.round(3).to_string(index=False)
)


#####################
####   Energy Requirements and Process Implications   #######
#####################

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# ============================================================
# FILE PATHS
# ============================================================

ROOT = Path(__file__).resolve().parents[2]
WORKDIR = ROOT

INPUT_FILE = ROOT / "model_results" / "FC_frezchem_thermodynamic_results_final.xlsx"

OUTPUT_PNG = ROOT / "figures" / "Figure_7_Energy_Requirements.png"
OUTPUT_PDF = ROOT / "figures" / "Figure_7_Energy_Requirements.pdf"

# ============================================================
# ENERGY PARAMETERS
# ============================================================

CP_BRINE = 3.80          # kJ kg^-1 K^-1
DELTA_H_FUS = 333.55     # kJ kg^-1 ice
COP = 3.0

T_INITIAL = 25.0         # °C

# Density used only to convert recovered ice mass to an
# equivalent recovered-water volume.
RHO_WATER = 1000.0       # kg m^-3

# ============================================================
# FIGURE SETTINGS
# ============================================================

TITLE_FS = 13
LABEL_FS = 13
TICK_FS = 11
LEGEND_FS = 9

LINE_WIDTH = 1.7

plt.rcParams.update({
    "font.family": "Arial",
    "font.size": TICK_FS,
    "axes.titlesize": TITLE_FS,
    "axes.labelsize": LABEL_FS,
    "xtick.labelsize": TICK_FS,
    "ytick.labelsize": TICK_FS,
    "legend.fontsize": LEGEND_FS,
    "axes.linewidth": 1.0,
})

# ============================================================
# READ FINAL FREZCHEM RESULTS
# ============================================================

c3 = pd.read_excel(
    INPUT_FILE,
    sheet_name="C3_FREZ_Detailed"
)

c5 = pd.read_excel(
    INPUT_FILE,
    sheet_name="C5_FREZ_Detailed"
)

c3 = (
    c3.sort_values("temperature_c", ascending=False)
    .reset_index(drop=True)
)

c5 = (
    c5.sort_values("temperature_c", ascending=False)
    .reset_index(drop=True)
)

# ============================================================
# CHECK AVAILABLE COLUMNS
# ============================================================

print("\nC3 columns:")
print(c3.columns.tolist())

# ============================================================
# IDENTIFY CUMULATIVE ICE MASS
# ============================================================

# First try likely direct ice-mass columns.

possible_ice_columns = [
    "ice_mass_kg",
    "cumulative_ice_mass_kg",
    "ice_kg",
    "cumulative_ice_kg"
]

ice_mass_col = None

for col in possible_ice_columns:
    if col in c3.columns:
        ice_mass_col = col
        break

# ============================================================
# INITIAL WATER MASS
# ============================================================

# The workbook contains liquid_water_fraction and
# ice_recovery_pct. If direct cumulative ice mass is absent,
# reconstruct it from the initial water inventory.

possible_water_columns = [
    "initial_water_mass_kg",
    "water_mass_kg",
    "water_kg",
    "liquid_water_kg",
    "water_kg_liquid"
]

water_mass_col = None

for col in possible_water_columns:
    if col in c3.columns:
        water_mass_col = col
        break

# ------------------------------------------------------------
# Determine initial water mass
# ------------------------------------------------------------

if water_mass_col is not None:

    MW0_C3 = float(c3.loc[0, water_mass_col])
    MW0_C5 = float(c5.loc[0, water_mass_col])

else:

    # The simulations were formulated on a 1 kg-water basis
    # unless another initial water-mass field is present.
    #
    # Because SEC is normalized by recovered water volume,
    # the absolute basis cancels provided the same basis is
    # used consistently.

    MW0_C3 = 1.0
    MW0_C5 = 1.0

    print(
        "\nNo explicit initial-water-mass column found. "
        "Using a 1 kg initial-water basis."
    )

# ============================================================
# CALCULATE CUMULATIVE ICE MASS
# ============================================================

if ice_mass_col is not None:

    c3["ice_mass_calc_kg"] = c3[ice_mass_col]
    c5["ice_mass_calc_kg"] = c5[ice_mass_col]

else:

    c3["ice_mass_calc_kg"] = (
        c3["ice_recovery_pct"] / 100.0
        * MW0_C3
    )

    c5["ice_mass_calc_kg"] = (
        c5["ice_recovery_pct"] / 100.0
        * MW0_C5
    )

# ============================================================
# CALCULATE SENSIBLE HEAT
# ============================================================

# Positive cooling interval:
# Delta T = T_initial - T

c3["delta_T_C"] = (
    T_INITIAL - c3["temperature_c"]
)

c5["delta_T_C"] = (
    T_INITIAL - c5["temperature_c"]
)

# Sensible cooling of the initial brine basis.
#
# This follows the simplified formulation used in Section 2.5.

c3["Q_sensible_kJ"] = (
    MW0_C3
    * CP_BRINE
    * c3["delta_T_C"]
)

c5["Q_sensible_kJ"] = (
    MW0_C5
    * CP_BRINE
    * c5["delta_T_C"]
)

# ============================================================
# CALCULATE LATENT HEAT
# ============================================================

c3["Q_latent_kJ"] = (
    c3["ice_mass_calc_kg"]
    * DELTA_H_FUS
)

c5["Q_latent_kJ"] = (
    c5["ice_mass_calc_kg"]
    * DELTA_H_FUS
)

# ============================================================
# TOTAL COOLING DUTY
# ============================================================

c3["Q_total_kJ"] = (
    c3["Q_sensible_kJ"]
    + c3["Q_latent_kJ"]
)

c5["Q_total_kJ"] = (
    c5["Q_sensible_kJ"]
    + c5["Q_latent_kJ"]
)

# ============================================================
# ELECTRICAL ENERGY
# ============================================================

# Q / COP gives electrical input in kJ.
# Divide by 3600 to convert kJ to kWh.

c3["electrical_energy_kWh"] = (
    c3["Q_total_kJ"]
    / COP
    / 3600.0
)

c5["electrical_energy_kWh"] = (
    c5["Q_total_kJ"]
    / COP
    / 3600.0
)

# ============================================================
# RECOVERED ICE-EQUIVALENT VOLUME
# ============================================================

c3["recovered_water_m3"] = (
    c3["ice_mass_calc_kg"]
    / RHO_WATER
)

c5["recovered_water_m3"] = (
    c5["ice_mass_calc_kg"]
    / RHO_WATER
)

# ============================================================
# SPECIFIC REFRIGERATION ENERGY
# ============================================================

# SEC is undefined before ice forms.
# Use NaN rather than infinity or zero.

c3["SEC_kWh_m3"] = np.where(
    c3["recovered_water_m3"] > 0,
    c3["electrical_energy_kWh"]
    / c3["recovered_water_m3"],
    np.nan
)

c5["SEC_kWh_m3"] = np.where(
    c5["recovered_water_m3"] > 0,
    c5["electrical_energy_kWh"]
    / c5["recovered_water_m3"],
    np.nan
)

# ============================================================
# HELPER FUNCTIONS
# ============================================================

def style_temperature_axis(ax):

    ax.tick_params(
        axis="both",
        which="both",
        direction="in",
        top=True,
        right=True
    )

    for spine in ax.spines.values():
        spine.set_visible(True)
        spine.set_linewidth(1.0)

    ax.set_xlim(25, -25)

    ax.set_xticks([
        25, 15, 5, -5, -15, -25
    ])


def style_axis(ax):

    ax.tick_params(
        axis="both",
        which="both",
        direction="in",
        top=True,
        right=True
    )

    for spine in ax.spines.values():
        spine.set_visible(True)
        spine.set_linewidth(1.0)


# ============================================================
# CREATE FIGURE
# ============================================================

fig, axes = plt.subplots(
    nrows=1,
    ncols=2,
    figsize=(12, 5.2)
)

ax1, ax2 = axes

# ============================================================
# (a) ENERGY REQUIREMENT VS TEMPERATURE
# ============================================================

ax1.plot(
    c3["temperature_c"],
    c3["SEC_kWh_m3"],
    linewidth=LINE_WIDTH,
    label="C3"
)

ax1.plot(
    c5["temperature_c"],
    c5["SEC_kWh_m3"],
    linewidth=LINE_WIDTH,
    linestyle="--",
    label="C5"
)

ax1.set_title(
    r"$\bf{(a)}$ Refrigeration energy vs temperature",
    fontsize=TITLE_FS,
    pad=10
)

ax1.set_xlabel(
    "Temperature (°C)",
    fontsize=LABEL_FS
)

ax1.set_ylabel(
    "Energy requirement "
    "(kWh m$^{-3}$ recovered ice-equivalent)",
    fontsize=LABEL_FS
)

ax1.legend(
    frameon=False,
    fontsize=LEGEND_FS
)

style_temperature_axis(ax1)

# ============================================================
# (b) ENERGY REQUIREMENT VS ICE RECOVERY
# ============================================================

# Only plot nodes where ice exists.

c3_energy = c3[
    c3["ice_recovery_pct"] > 0
].copy()

c5_energy = c5[
    c5["ice_recovery_pct"] > 0
].copy()

ax2.plot(
    c3_energy["ice_recovery_pct"],
    c3_energy["SEC_kWh_m3"],
    linewidth=LINE_WIDTH,
    label="C3"
)

ax2.plot(
    c5_energy["ice_recovery_pct"],
    c5_energy["SEC_kWh_m3"],
    linewidth=LINE_WIDTH,
    linestyle="--",
    label="C5"
)

ax2.set_title(
    r"$\bf{(b)}$ Energy-water recovery relationship",
    fontsize=TITLE_FS,
    pad=10
)

ax2.set_xlabel(
    "Cumulative ice recovery (%)",
    fontsize=LABEL_FS
)

ax2.set_ylabel(
    "Energy requirement "
    "(kWh m$^{-3}$ recovered ice-equivalent)",
    fontsize=LABEL_FS
)

ax2.legend(
    frameon=False,
    fontsize=LEGEND_FS
)

style_axis(ax2)

# ============================================================
# LAYOUT
# ============================================================

fig.subplots_adjust(
    left=0.09,
    right=0.98,
    bottom=0.16,
    top=0.92,
    wspace=0.30
)

# ============================================================
# SAVE FIGURE
# ============================================================

fig.savefig(
    OUTPUT_PNG,
    dpi=600,
    bbox_inches="tight"
)

fig.savefig(
    OUTPUT_PDF,
    bbox_inches="tight"
)

plt.show()

# ============================================================
# FINAL -25 °C VALUES
# ============================================================

c3_end = c3.loc[
    np.isclose(
        c3["temperature_c"],
        -25
    )
].iloc[0]

c5_end = c5.loc[
    np.isclose(
        c5["temperature_c"],
        -25
    )
].iloc[0]

print("\n============================================")
print("FIGURE 7 GENERATED SUCCESSFULLY")
print("============================================")

print(f"\nPNG:\n{OUTPUT_PNG}")
print(f"\nPDF:\n{OUTPUT_PDF}")

print("\n============================================")
print("FINAL ENERGY RESULTS AT -25 °C")
print("============================================")

print("\nC3")
print(
    f"Ice recovery = "
    f"{c3_end['ice_recovery_pct']:.2f}%"
)
print(
    f"Sensible heat = "
    f"{c3_end['Q_sensible_kJ']:.6f} kJ"
)
print(
    f"Latent heat = "
    f"{c3_end['Q_latent_kJ']:.6f} kJ"
)
print(
    f"Total cooling duty = "
    f"{c3_end['Q_total_kJ']:.6f} kJ"
)
print(
    f"Electrical energy = "
    f"{c3_end['electrical_energy_kWh']:.6f} kWh"
)
print(
    f"Energy requirement = "
    f"{c3_end['SEC_kWh_m3']:.3f} "
    f"kWh/m3 recovered ice-equivalent"
)

print("\nC5")
print(
    f"Ice recovery = "
    f"{c5_end['ice_recovery_pct']:.2f}%"
)
print(
    f"Sensible heat = "
    f"{c5_end['Q_sensible_kJ']:.6f} kJ"
)
print(
    f"Latent heat = "
    f"{c5_end['Q_latent_kJ']:.6f} kJ"
)
print(
    f"Total cooling duty = "
    f"{c5_end['Q_total_kJ']:.6f} kJ"
)
print(
    f"Electrical energy = "
    f"{c5_end['electrical_energy_kWh']:.6f} kWh"
)
print(
    f"Energy requirement = "
    f"{c5_end['SEC_kWh_m3']:.3f} "
    f"kWh/m3 recovered ice-equivalent"
)

print("\n============================================")
print("ENERGY PARAMETERS")
print("============================================")

print(f"Cp brine = {CP_BRINE:.2f} kJ/kg/K")
print(
    f"Latent heat of fusion = "
    f"{DELTA_H_FUS:.2f} kJ/kg"
)
print(f"COP = {COP:.1f}")
