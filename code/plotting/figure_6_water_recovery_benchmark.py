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

WORKDIR = Path(r"C:\Users\Kagiso\PHREEQC-Python")

INPUT_FILE = WORKDIR / "FC_frezchem_thermodynamic_results_final.xlsx"

OUTPUT_PNG = WORKDIR / "Figure_6_Cross_Model_Performance.png"
OUTPUT_PDF = WORKDIR / "Figure_6_Cross_Model_Performance.pdf"

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
