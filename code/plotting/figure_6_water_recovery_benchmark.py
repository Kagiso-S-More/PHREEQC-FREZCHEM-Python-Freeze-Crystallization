###########################


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

OUTPUT_PNG = (
    ROOT / "figures" /
    "Figure_5_Freeze_Concentration_Chemistry_MassBalance.png"
)

OUTPUT_PDF = (
    ROOT / "figures" /
    "Figure_5_Freeze_Concentration_Chemistry_MassBalance.pdf"
)

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

# Sort from warm to cold
c3 = (
    c3.sort_values(
        "temperature_c",
        ascending=False
    )
    .reset_index(drop=True)
)

c5 = (
    c5.sort_values(
        "temperature_c",
        ascending=False
    )
    .reset_index(drop=True)
)

# ============================================================
# ABSOLUTE MASS-BALANCE ERRORS
# ============================================================

# Component error is already stored as the maximum component
# balance error at each temperature node.

c3["component_error_abs"] = (
    c3["max_component_balance_error_pct"].abs()
)

c5["component_error_abs"] = (
    c5["max_component_balance_error_pct"].abs()
)

# Water error may contain positive/negative residuals.
# Plot its magnitude.

c3["water_error_abs"] = (
    c3["water_balance_error_pct"].abs()
)

c5["water_error_abs"] = (
    c5["water_balance_error_pct"].abs()
)

# ============================================================
# HELPER FUNCTION
# ============================================================

def style_axis(ax):
    """
    Apply journal-style formatting:
    - full four-sided border
    - inward ticks
    - ticks on all four sides
    - temperature axis from 25 to -25 °C
    """

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


# ============================================================
# CREATE 3 × 2 FIGURE
# ============================================================

fig, axes = plt.subplots(
    nrows=3,
    ncols=2,
    figsize=(12, 14)
)

ax1, ax2, ax3, ax4, ax5, ax6 = axes.flatten()

# ============================================================
# (a) CONCENTRATION FACTOR
# ============================================================

ax1.plot(
    c3["temperature_c"],
    c3["concentration_factor"],
    linewidth=LINE_WIDTH,
    label="C3"
)

ax1.plot(
    c5["temperature_c"],
    c5["concentration_factor"],
    linewidth=LINE_WIDTH,
    linestyle="--",
    label="C5"
)

ax1.set_title(
    r"$\bf{(a)}$ Concentration factor",
    fontsize=TITLE_FS,
    pad=10
)

ax1.set_xlabel(
    "Temperature (°C)",
    fontsize=LABEL_FS
)

ax1.set_ylabel(
    "Concentration factor",
    fontsize=LABEL_FS
)

ax1.legend(
    frameon=False,
    fontsize=LEGEND_FS
)

style_axis(ax1)

# ============================================================
# (b) LIQUID-WATER FRACTION
# ============================================================

ax2.plot(
    c3["temperature_c"],
    c3["liquid_water_fraction"],
    linewidth=LINE_WIDTH,
    label="C3"
)

ax2.plot(
    c5["temperature_c"],
    c5["liquid_water_fraction"],
    linewidth=LINE_WIDTH,
    linestyle="--",
    label="C5"
)

ax2.set_title(
    r"$\bf{(b)}$ Liquid-water fraction",
    fontsize=TITLE_FS,
    pad=10
)

ax2.set_xlabel(
    "Temperature (°C)",
    fontsize=LABEL_FS
)

ax2.set_ylabel(
    "Liquid-water fraction",
    fontsize=LABEL_FS
)

ax2.legend(
    frameon=False,
    fontsize=LEGEND_FS
)

style_axis(ax2)

# ============================================================
# (c) NORMALISED AQUEOUS CONCENTRATIONS
# ============================================================

# ------------------------------------------------------------
# Na+
# Same colour for C3/C5;
# solid line = C3
# dashed line = C5
# ------------------------------------------------------------

line_na_c3, = ax3.plot(
    c3["temperature_c"],
    c3["Na_normalized"],
    linewidth=LINE_WIDTH,
    linestyle="-",
    label="C3 Na$^+$"
)

ax3.plot(
    c5["temperature_c"],
    c5["Na_normalized"],
    linewidth=LINE_WIDTH,
    linestyle="--",
    color=line_na_c3.get_color(),
    label="C5 Na$^+$"
)

# ------------------------------------------------------------
# Cl-
# ------------------------------------------------------------

line_cl_c3, = ax3.plot(
    c3["temperature_c"],
    c3["Cl_normalized"],
    linewidth=LINE_WIDTH,
    linestyle="-",
    label="C3 Cl$^-$"
)

ax3.plot(
    c5["temperature_c"],
    c5["Cl_normalized"],
    linewidth=LINE_WIDTH,
    linestyle="--",
    color=line_cl_c3.get_color(),
    label="C5 Cl$^-$"
)

# ------------------------------------------------------------
# SO4^2-
# Workbook stores this as S6_normalized.
# S(VI) represents the aqueous sulphate component used
# in the PHREEQC model.
# ------------------------------------------------------------

line_so4_c3, = ax3.plot(
    c3["temperature_c"],
    c3["S6_normalized"],
    linewidth=LINE_WIDTH,
    linestyle="-",
    label="C3 SO$_4^{2-}$"
)

ax3.plot(
    c5["temperature_c"],
    c5["S6_normalized"],
    linewidth=LINE_WIDTH,
    linestyle="--",
    color=line_so4_c3.get_color(),
    label="C5 SO$_4^{2-}$"
)

# Initial normalized concentration = 1

ax3.axhline(
    y=1.0,
    color="black",
    linestyle=":",
    linewidth=1.0,
    alpha=0.7
)

ax3.set_title(
    r"$\bf{(c)}$ Normalised aqueous concentrations",
    fontsize=TITLE_FS,
    pad=10
)

ax3.set_xlabel(
    "Temperature (°C)",
    fontsize=LABEL_FS
)

ax3.set_ylabel(
    r"$C_i/C_{i,0}$",
    fontsize=LABEL_FS
)

ax3.legend(
    frameon=False,
    fontsize=LEGEND_FS,
    ncol=2
)

style_axis(ax3)

# ============================================================
# (d) IONIC STRENGTH AND WATER ACTIVITY
# ============================================================

# ------------------------------------------------------------
# LEFT AXIS: IONIC STRENGTH
# ------------------------------------------------------------

line_i_c3, = ax4.plot(
    c3["temperature_c"],
    c3["ionic_strength_mol_kgw"],
    linewidth=LINE_WIDTH,
    linestyle="-",
    label="C3 ionic strength"
)

line_i_c5, = ax4.plot(
    c5["temperature_c"],
    c5["ionic_strength_mol_kgw"],
    linewidth=LINE_WIDTH,
    linestyle="--",
    label="C5 ionic strength"
)

ax4.set_xlabel(
    "Temperature (°C)",
    fontsize=LABEL_FS
)

ax4.set_ylabel(
    "Ionic strength (mol kg$^{-1}$ water)",
    fontsize=LABEL_FS
)

# ------------------------------------------------------------
# RIGHT AXIS: WATER ACTIVITY
# ------------------------------------------------------------

ax4_right = ax4.twinx()

line_aw_c3, = ax4_right.plot(
    c3["temperature_c"],
    c3["water_activity"],
    linewidth=LINE_WIDTH,
    linestyle="-.",
    label="C3 water activity"
)

line_aw_c5, = ax4_right.plot(
    c5["temperature_c"],
    c5["water_activity"],
    linewidth=LINE_WIDTH,
    linestyle=":",
    label="C5 water activity"
)

ax4_right.set_ylabel(
    "Water activity",
    fontsize=LABEL_FS
)

ax4.set_title(
    r"$\bf{(d)}$ Ionic strength and water activity",
    fontsize=TITLE_FS,
    pad=10
)

# Combined legend

lines_ax4 = [
    line_i_c3,
    line_i_c5,
    line_aw_c3,
    line_aw_c5
]

labels_ax4 = [
    line.get_label()
    for line in lines_ax4
]

ax4.legend(
    lines_ax4,
    labels_ax4,
    frameon=False,
    fontsize=LEGEND_FS,
    ncol=2,
    loc="center left"
)

# Format primary axis
style_axis(ax4)

# Format secondary axis
ax4_right.tick_params(
    axis="y",
    which="both",
    direction="in",
    right=True
)

for spine in ax4_right.spines.values():
    spine.set_visible(True)
    spine.set_linewidth(1.0)

# ============================================================
# (e) COMPONENT MASS-BALANCE ERROR
# ============================================================

ax5.plot(
    c3["temperature_c"],
    c3["component_error_abs"],
    linewidth=LINE_WIDTH,
    label="C3"
)

ax5.plot(
    c5["temperature_c"],
    c5["component_error_abs"],
    linewidth=LINE_WIDTH,
    linestyle="--",
    label="C5"
)

ax5.set_title(
    r"$\bf{(e)}$ Component mass-balance error",
    fontsize=TITLE_FS,
    pad=10
)

ax5.set_xlabel(
    "Temperature (°C)",
    fontsize=LABEL_FS
)

ax5.set_ylabel(
    "Maximum absolute error (%)",
    fontsize=LABEL_FS
)

ax5.legend(
    frameon=False,
    fontsize=LEGEND_FS
)

style_axis(ax5)

# ============================================================
# (f) WATER MASS-BALANCE ERROR
# ============================================================

ax6.plot(
    c3["temperature_c"],
    c3["water_error_abs"],
    linewidth=LINE_WIDTH,
    label="C3"
)

ax6.plot(
    c5["temperature_c"],
    c5["water_error_abs"],
    linewidth=LINE_WIDTH,
    linestyle="--",
    label="C5"
)

ax6.set_title(
    r"$\bf{(f)}$ Water mass-balance error",
    fontsize=TITLE_FS,
    pad=10
)

ax6.set_xlabel(
    "Temperature (°C)",
    fontsize=LABEL_FS
)

ax6.set_ylabel(
    "Absolute error (%)",
    fontsize=LABEL_FS
)

ax6.legend(
    frameon=False,
    fontsize=LEGEND_FS
)

style_axis(ax6)

# ============================================================
# LAYOUT
# ============================================================

fig.subplots_adjust(
    left=0.09,
    right=0.92,
    bottom=0.07,
    top=0.97,
    wspace=0.35,
    hspace=0.38
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

# ============================================================
# FIND MAXIMUM MASS-BALANCE ERRORS
# ============================================================

c3_comp_idx = (
    c3["component_error_abs"]
    .idxmax()
)

c5_comp_idx = (
    c5["component_error_abs"]
    .idxmax()
)

c3_water_idx = (
    c3["water_error_abs"]
    .idxmax()
)

c5_water_idx = (
    c5["water_error_abs"]
    .idxmax()
)

# ============================================================
# PRINT RESULTS FOR TABLE 4 / RESULTS TEXT
# ============================================================

print("\n============================================")
print("FIGURE 5 GENERATED SUCCESSFULLY")
print("============================================")

print(f"\nPNG:\n{OUTPUT_PNG}")
print(f"\nPDF:\n{OUTPUT_PDF}")

print("\n============================================")
print("FINAL VALUES AT -25 °C")
print("============================================")

print("\nC3")
print(
    f"Ice recovery = "
    f"{c3_end['ice_recovery_pct']:.2f}%"
)
print(
    f"Concentration factor = "
    f"{c3_end['concentration_factor']:.4f}"
)
print(
    f"Liquid-water fraction = "
    f"{c3_end['liquid_water_fraction']:.6f}"
)
print(
    f"Ionic strength = "
    f"{c3_end['ionic_strength_mol_kgw']:.6f} mol/kgw"
)
print(
    f"Water activity = "
    f"{c3_end['water_activity']:.6f}"
)
print(
    f"Na normalized = "
    f"{c3_end['Na_normalized']:.4f}"
)
print(
    f"Cl normalized = "
    f"{c3_end['Cl_normalized']:.4f}"
)
print(
    f"SO4 normalized = "
    f"{c3_end['S6_normalized']:.4f}"
)

print("\nC5")
print(
    f"Ice recovery = "
    f"{c5_end['ice_recovery_pct']:.2f}%"
)
print(
    f"Concentration factor = "
    f"{c5_end['concentration_factor']:.4f}"
)
print(
    f"Liquid-water fraction = "
    f"{c5_end['liquid_water_fraction']:.6f}"
)
print(
    f"Ionic strength = "
    f"{c5_end['ionic_strength_mol_kgw']:.6f} mol/kgw"
)
print(
    f"Water activity = "
    f"{c5_end['water_activity']:.6f}"
)
print(
    f"Na normalized = "
    f"{c5_end['Na_normalized']:.4f}"
)
print(
    f"Cl normalized = "
    f"{c5_end['Cl_normalized']:.4f}"
)
print(
    f"SO4 normalized = "
    f"{c5_end['S6_normalized']:.4f}"
)

print("\n============================================")
print("MAXIMUM MASS-BALANCE ERRORS")
print("============================================")

print(
    f"\nC3 maximum component error = "
    f"{c3.loc[c3_comp_idx, 'component_error_abs']:.6f}% "
    f"at "
    f"{c3.loc[c3_comp_idx, 'temperature_c']:.0f} °C"
)

print(
    f"C5 maximum component error = "
    f"{c5.loc[c5_comp_idx, 'component_error_abs']:.6f}% "
    f"at "
    f"{c5.loc[c5_comp_idx, 'temperature_c']:.0f} °C"
)

print(
    f"\nC3 maximum water error = "
    f"{c3.loc[c3_water_idx, 'water_error_abs']:.6f}% "
    f"at "
    f"{c3.loc[c3_water_idx, 'temperature_c']:.0f} °C"
)

print(
    f"C5 maximum water error = "
    f"{c5.loc[c5_water_idx, 'water_error_abs']:.6f}% "
    f"at "
    f"{c5.loc[c5_water_idx, 'temperature_c']:.0f} °C"
)

# ============================================================
# IDENTIFY WHICH COMPONENT CONTROLS THE MAXIMUM ERROR
# ============================================================

component_error_columns = [
    "Na_balance_error_pct",
    "K_balance_error_pct",
    "Mg_balance_error_pct",
    "Ca_balance_error_pct",
    "Cl_balance_error_pct",
    "S6_balance_error_pct",
    "C4_balance_error_pct"
]

print("\n============================================")
print("COMPONENT RESPONSIBLE FOR MAXIMUM ERROR")
print("============================================")

for case_name, df, idx in [
    ("C3", c3, c3_comp_idx),
    ("C5", c5, c5_comp_idx)
]:

    row_errors = (
        df.loc[idx, component_error_columns]
        .astype(float)
        .abs()
    )

    controlling_column = row_errors.idxmax()

    controlling_component = (
        controlling_column
        .replace("_balance_error_pct", "")
    )

    signed_error = df.loc[
        idx,
        controlling_column
    ]

    print(
        f"\n{case_name}: "
        f"{controlling_component} controls the maximum "
        f"component error at "
        f"{df.loc[idx, 'temperature_c']:.0f} °C; "
        f"signed error = {signed_error:.6f}%"
    )
