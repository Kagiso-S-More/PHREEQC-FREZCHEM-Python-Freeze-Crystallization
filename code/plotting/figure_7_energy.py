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

WORKDIR = Path(r"C:\Users\Kagiso\PHREEQC-Python")

INPUT_FILE = WORKDIR / "FC_frezchem_thermodynamic_results_final.xlsx"

OUTPUT_PNG = WORKDIR / "Figure_7_Energy_Requirements.png"
OUTPUT_PDF = WORKDIR / "Figure_7_Energy_Requirements.pdf"

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
