######################
###  Thermodynamic Phase Evolution and Crystallization Onset   ###
######################

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# ============================================================
# FILE PATHS
# ============================================================

WORKDIR = Path(r"C:\Users\Kagiso\PHREEQC-Python")

INPUT_FILE = WORKDIR / "FC_frezchem_thermodynamic_results_final.xlsx"

OUTPUT_PNG = WORKDIR / "Figure_4_Phase_Evolution.png"
OUTPUT_PDF = WORKDIR / "Figure_4_Phase_Evolution.pdf"

# ============================================================
# FIGURE SETTINGS
# ============================================================

TITLE_FS = 13
LABEL_FS = 13
TICK_FS = 11
LEGEND_FS = 9

LINE_WIDTH = 1.7
MARKER_SIZE = 5

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

# Read raw OLI benchmark results
oli_c3 = pd.read_excel(
    INPUT_FILE,
    sheet_name="OLI_C3_Raw"
)

oli_c5 = pd.read_excel(
    INPUT_FILE,
    sheet_name="OLI_C5_Raw"
)

# Sort all datasets from warm to cold
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

oli_c3 = (
    oli_c3.sort_values(
        "temperature_c",
        ascending=False
    )
    .reset_index(drop=True)
)

oli_c5 = (
    oli_c5.sort_values(
        "temperature_c",
        ascending=False
    )
    .reset_index(drop=True)
)

# ============================================================
# CALCULATE GYPSUM SULPHATE RECOVERY
# ============================================================

# One mole of gypsum contains one mole of sulphate.
# Initial S(VI) inventory is taken from the initial model state.

c3_initial_s6 = c3.loc[0, "S6_mol"]
c5_initial_s6 = c5.loc[0, "S6_mol"]

c3["so4_recovery_as_gypsum_pct"] = (
    c3["gypsum_cumulative_mol"]
    / c3_initial_s6
    * 100
)

c5["so4_recovery_as_gypsum_pct"] = (
    c5["gypsum_cumulative_mol"]
    / c5_initial_s6
    * 100
)

# ============================================================
# HELPER FUNCTIONS
# ============================================================

def style_axis(ax):
    """
    Apply consistent journal-style formatting:
    - ticks inside
    - ticks on all four sides
    - full plot borders
    - common temperature range
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


def add_zero_line(ax):
    """
    Add SI = 0 equilibrium reference line.
    """

    ax.axhline(
        y=0,
        color="black",
        linestyle="--",
        linewidth=1.0,
        alpha=0.7
    )


# ============================================================
# CREATE 3 ROW × 2 COLUMN FIGURE
# ============================================================

fig, axes = plt.subplots(
    nrows=3,
    ncols=2,
    figsize=(12, 14)
)

ax1, ax2, ax3, ax4, ax5, ax6 = axes.flatten()

# ============================================================
# (a) ICE SATURATION INDEX
# ============================================================

ax1.plot(
    c3["temperature_c"],
    c3["si_ice_pre"],
    linewidth=LINE_WIDTH,
    label="C3"
)

ax1.plot(
    c5["temperature_c"],
    c5["si_ice_pre"],
    linewidth=LINE_WIDTH,
    linestyle="--",
    label="C5"
)

add_zero_line(ax1)

ax1.set_title(
    r"$\bf{(a)}$ Ice saturation",
    fontsize=TITLE_FS,
    pad=10
)

ax1.set_xlabel(
    "Temperature (°C)",
    fontsize=LABEL_FS
)

ax1.set_ylabel(
    "Pre-equilibrium SI",
    fontsize=LABEL_FS
)

ax1.legend(
    frameon=False,
    fontsize=LEGEND_FS
)

style_axis(ax1)

# ============================================================
# (b) MIRABILITE SATURATION INDEX
# ============================================================

ax2.plot(
    c3["temperature_c"],
    c3["si_mirabilite_pre"],
    linewidth=LINE_WIDTH,
    label="C3"
)

ax2.plot(
    c5["temperature_c"],
    c5["si_mirabilite_pre"],
    linewidth=LINE_WIDTH,
    linestyle="--",
    label="C5"
)

add_zero_line(ax2)

ax2.set_title(
    r"$\bf{(b)}$ Mirabilite saturation",
    fontsize=TITLE_FS,
    pad=10
)

ax2.set_xlabel(
    "Temperature (°C)",
    fontsize=LABEL_FS
)

ax2.set_ylabel(
    "Pre-equilibrium SI",
    fontsize=LABEL_FS
)

ax2.legend(
    frameon=False,
    fontsize=LEGEND_FS
)

style_axis(ax2)

# ============================================================
# (c) HYDROHALITE AND HALITE SATURATION INDICES
# ============================================================

ax3.plot(
    c3["temperature_c"],
    c3["si_hydrohalite_pre"],
    linewidth=LINE_WIDTH,
    label="C3 hydrohalite"
)

ax3.plot(
    c5["temperature_c"],
    c5["si_hydrohalite_pre"],
    linewidth=LINE_WIDTH,
    linestyle="--",
    label="C5 hydrohalite"
)

ax3.plot(
    c3["temperature_c"],
    c3["si_halite_pre"],
    linewidth=LINE_WIDTH,
    linestyle="-.",
    label="C3 halite"
)

ax3.plot(
    c5["temperature_c"],
    c5["si_halite_pre"],
    linewidth=LINE_WIDTH,
    linestyle=":",
    label="C5 halite"
)

add_zero_line(ax3)

ax3.set_title(
    r"$\bf{(c)}$ NaCl-bearing phase saturation",
    fontsize=TITLE_FS,
    pad=10
)

ax3.set_xlabel(
    "Temperature (°C)",
    fontsize=LABEL_FS
)

ax3.set_ylabel(
    "Pre-equilibrium SI",
    fontsize=LABEL_FS
)

ax3.legend(
    frameon=False,
    fontsize=LEGEND_FS,
    ncol=2
)

style_axis(ax3)

# ============================================================
# (d) MIRABILITE RECOVERY
# ============================================================

# PHREEQC-FREZCHEM results:
# continuous lines representing the 1 °C simulation grid.

ax4.plot(
    c3["temperature_c"],
    c3["so4_recovery_as_mirabilite_pct"],
    linewidth=LINE_WIDTH,
    label="C3 PHREEQC"
)

ax4.plot(
    c5["temperature_c"],
    c5["so4_recovery_as_mirabilite_pct"],
    linewidth=LINE_WIDTH,
    linestyle="--",
    label="C5 PHREEQC"
)

# OLI results:
# discrete symbols representing the actual common
# benchmark temperatures without interpolation.

ax4.plot(
    oli_c3["temperature_c"],
    oli_c3["oli_so4_recovery_as_mirabilite_pct"],
    linestyle="none",
    marker="o",
    markersize=MARKER_SIZE,
    label="C3 OLI"
)

ax4.plot(
    oli_c5["temperature_c"],
    oli_c5["oli_so4_recovery_as_mirabilite_pct"],
    linestyle="none",
    marker="s",
    markersize=MARKER_SIZE,
    label="C5 OLI"
)

ax4.set_title(
    r"$\bf{(d)}$ Mirabilite recovery",
    fontsize=TITLE_FS,
    pad=10
)

ax4.set_xlabel(
    "Temperature (°C)",
    fontsize=LABEL_FS
)

ax4.set_ylabel(
    "SO$_4^{2-}$ recovery (%)",
    fontsize=LABEL_FS
)

ax4.set_ylim(0, 105)

ax4.legend(
    frameon=False,
    fontsize=LEGEND_FS,
    ncol=2
)

style_axis(ax4)

# ============================================================
# (e) HYDROHALITE RECOVERY
# ============================================================

# Na-based hydrohalite recovery is used for the
# PHREEQC-OLI comparison.

ax5.plot(
    c3["temperature_c"],
    c3["na_recovery_as_hydrohalite_pct"],
    linewidth=LINE_WIDTH,
    label="C3 PHREEQC"
)

ax5.plot(
    c5["temperature_c"],
    c5["na_recovery_as_hydrohalite_pct"],
    linewidth=LINE_WIDTH,
    linestyle="--",
    label="C5 PHREEQC"
)

ax5.plot(
    oli_c3["temperature_c"],
    oli_c3["oli_na_recovery_as_hydrohalite_pct"],
    linestyle="none",
    marker="o",
    markersize=MARKER_SIZE,
    label="C3 OLI"
)

ax5.plot(
    oli_c5["temperature_c"],
    oli_c5["oli_na_recovery_as_hydrohalite_pct"],
    linestyle="none",
    marker="s",
    markersize=MARKER_SIZE,
    label="C5 OLI"
)

ax5.set_title(
    r"$\bf{(e)}$ Hydrohalite recovery",
    fontsize=TITLE_FS,
    pad=10
)

ax5.set_xlabel(
    "Temperature (°C)",
    fontsize=LABEL_FS
)

ax5.set_ylabel(
    "Na recovery (%)",
    fontsize=LABEL_FS
)

ax5.set_ylim(0, 105)

ax5.legend(
    frameon=False,
    fontsize=LEGEND_FS,
    ncol=2
)

style_axis(ax5)

# ============================================================
# (f) SULPHATE PARTITIONING AT -25 °C
# ============================================================

# Extract final -25 °C model states

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

# Mirabilite sulphate recovery directly from workbook

mirabilite_recovery = np.array([
    c3_end["so4_recovery_as_mirabilite_pct"],
    c5_end["so4_recovery_as_mirabilite_pct"]
])

# Gypsum sulphate recovery calculated directly from
# cumulative gypsum and initial S(VI)

gypsum_recovery = np.array([
    c3_end["so4_recovery_as_gypsum_pct"],
    c5_end["so4_recovery_as_gypsum_pct"]
])

x = np.arange(2)
bar_width = 0.55

bars_mir = ax6.bar(
    x,
    mirabilite_recovery,
    width=bar_width,
    label="Mirabilite"
)

bars_gyp = ax6.bar(
    x,
    gypsum_recovery,
    width=bar_width,
    bottom=mirabilite_recovery,
    label="Gypsum"
)

ax6.set_xticks(x)

ax6.set_xticklabels([
    "C3",
    "C5"
])

ax6.set_ylim(0, 105)

ax6.set_title(
    r"$\bf{(f)}$ Sulphate partitioning at −25 °C",
    fontsize=TITLE_FS,
    pad=10
)

ax6.set_xlabel(
    "Brine",
    fontsize=LABEL_FS
)

ax6.set_ylabel(
    "Initial SO$_4^{2-}$ recovered (%)",
    fontsize=LABEL_FS
)

ax6.legend(
    frameon=False,
    fontsize=LEGEND_FS
)

# ------------------------------------------------------------
# Add numerical labels inside stacked bars
# ------------------------------------------------------------

for i in range(len(x)):

    # Mirabilite percentage
    ax6.text(
        x[i],
        mirabilite_recovery[i] / 2,
        f"{mirabilite_recovery[i]:.1f}%",
        ha="center",
        va="center",
        fontsize=9
    )

    # Gypsum percentage
    ax6.text(
        x[i],
        mirabilite_recovery[i]
        + gypsum_recovery[i] / 2,
        f"{gypsum_recovery[i]:.1f}%",
        ha="center",
        va="center",
        fontsize=9
    )

# Full border and inward ticks for panel (f)

ax6.tick_params(
    axis="both",
    which="both",
    direction="in",
    top=True,
    right=True
)

for spine in ax6.spines.values():
    spine.set_visible(True)
    spine.set_linewidth(1.0)

# ============================================================
# FIGURE LAYOUT
# ============================================================

fig.subplots_adjust(
    left=0.09,
    right=0.98,
    bottom=0.07,
    top=0.97,
    wspace=0.28,
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
# PRINT CHECK VALUES
# ============================================================

print("\nFigure 4 generated successfully.")

print(
    f"PNG saved to:\n{OUTPUT_PNG}"
)

print(
    f"\nPDF saved to:\n{OUTPUT_PDF}"
)

print("\nSulphate partitioning at -25 °C:")

print(
    f"C3: Mirabilite = "
    f"{mirabilite_recovery[0]:.2f}%, "
    f"Gypsum = "
    f"{gypsum_recovery[0]:.2f}%, "
    f"Total = "
    f"{mirabilite_recovery[0] + gypsum_recovery[0]:.2f}%"
)

print(
    f"C5: Mirabilite = "
    f"{mirabilite_recovery[1]:.2f}%, "
    f"Gypsum = "
    f"{gypsum_recovery[1]:.2f}%, "
    f"Total = "
    f"{mirabilite_recovery[1] + gypsum_recovery[1]:.2f}%"
)
