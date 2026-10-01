from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


# ======================================================================
# USER SETTINGS
# ======================================================================

WORKDIR = Path(__file__).resolve().parent

RESULTS_FILE = (
    WORKDIR / "frezpy_experiment_validation_results.xlsx"
)

OUTPUT_PNG = (
    WORKDIR / "Figure_S_Experimental_Validation.png"
)

OUTPUT_PDF = (
    WORKDIR / "Figure_S_Experimental_Validation.pdf"
)

LABEL_SIZE = 13
TICK_SIZE = 12
LEGEND_SIZE = 10
PANEL_SIZE = 13


# ======================================================================
# LOAD RESULTS
# ======================================================================

df = pd.read_excel(
    RESULTS_FILE,
    sheet_name="FrezPy_Detailed",
)

comparison = pd.read_excel(
    RESULTS_FILE,
    sheet_name="Validation_Comparison",
)

df = (
    df.sort_values(
        "temperature_c",
        ascending=False,
    )
    .reset_index(drop=True)
)

comparison = (
    comparison.sort_values(
        "temperature_c",
        ascending=False,
    )
    .reset_index(drop=True)
)


# ======================================================================
# CREATE FIGURE
# ======================================================================

fig, axes = plt.subplots(
    2,
    2,
    figsize=(12, 9),
)

ax1, ax2, ax3, ax4 = axes.flatten()


# ======================================================================
# (a) ICE RECOVERY: FREZPY VS OLI
# ======================================================================

ax1.plot(
    df["temperature_c"],
    df["ice_recovery_pct"],
    marker="o",
    markersize=4,
    linewidth=1.8,
    label="FrezPy",
)

ax1.scatter(
    comparison["temperature_c"],
    comparison["OLI_ice_recovery_pct"],
    marker="s",
    s=50,
    label="OLI",
    zorder=5,
)

ax1.set_xlabel(
    "Temperature (°C)",
    fontsize=LABEL_SIZE,
)

ax1.set_ylabel(
    "Ice recovery (%)",
    fontsize=LABEL_SIZE,
)

ax1.set_xlim(25, -25)
ax1.set_ylim(0, 105)

ax1.grid(
    alpha=0.25,
)

ax1.legend(
    frameon=False,
    fontsize=LEGEND_SIZE,
)


# ======================================================================
# (b) MIRABILITE RECOVERY
# ======================================================================

ax2.plot(
    df["temperature_c"],
    df["so4_recovery_as_mirabilite_pct"],
    marker="o",
    markersize=4,
    linewidth=1.8,
)

ax2.set_xlabel(
    "Temperature (°C)",
    fontsize=13,
)

ax2.set_ylabel(
    "SO₄ recovery as mirabilite (%)",
    fontsize=13,
)

ax2.set_xlim(25, -25)
ax2.set_ylim(0, 105)
ax2.grid(alpha=0.25)


# ======================================================================
# (c) FREZPY VS OLI ICE RECOVERY
# ======================================================================

valid = comparison[
    comparison["OLI_ice_recovery_pct"].notna()
    & comparison["ice_recovery_pct"].notna()
].copy()

ax3.scatter(
    valid["OLI_ice_recovery_pct"],
    valid["ice_recovery_pct"],
    s=60,
    zorder=5,
)

lims = [0, 105]

ax3.plot(
    lims,
    lims,
    linestyle="--",
    linewidth=1.4,
    label="1:1 agreement",
)

for _, row in valid.iterrows():

    ax3.annotate(
        f'{row["temperature_c"]:.0f} °C',
        (
            row["OLI_ice_recovery_pct"],
            row["ice_recovery_pct"],
        ),
        xytext=(6, 6),
        textcoords="offset points",
        fontsize=10,
    )

ax3.set_xlabel(
    "OLI ice recovery (%)",
    fontsize=LABEL_SIZE,
)

ax3.set_ylabel(
    "FrezPy ice recovery (%)",
    fontsize=LABEL_SIZE,
)

ax3.set_xlim(lims)
ax3.set_ylim(lims)

ax3.grid(
    alpha=0.25,
)

ax3.legend(
    frameon=False,
    fontsize=LEGEND_SIZE,
)


# ======================================================================
# (d) MASS-BALANCE PERFORMANCE
# ======================================================================

component_error = np.abs(
    pd.to_numeric(
        df["max_component_balance_error_pct"],
        errors="coerce",
    )
)

water_error = np.abs(
    pd.to_numeric(
        df["water_balance_error_pct"],
        errors="coerce",
    )
)

ax4.plot(
    df["temperature_c"],
    component_error,
    linewidth=1.8,
    label="Component balance",
)

ax4.plot(
    df["temperature_c"],
    water_error,
    linewidth=1.8,
    linestyle="--",
    label="Water balance",
)

ax4.set_xlabel(
    "Temperature (°C)",
    fontsize=13,
)

ax4.set_ylabel(
    "Absolute balance error (%)",
    fontsize=13,
)

ax4.set_xlim(25, -25)

ax4.grid(alpha=0.25)

ax4.legend(
    frameon=False,
    fontsize=10,
)


# ======================================================================
# COMMON AXIS FORMATTING
# ======================================================================

for ax in axes.flatten():

    # Ticks facing inward on all four sides
    ax.tick_params(
        axis="both",
        which="major",
        direction="in",
        labelsize=TICK_SIZE,
        length=5,
        width=0.8,
        top=True,
        right=True,
    )

    ax.tick_params(
        axis="both",
        which="minor",
        direction="in",
        length=3,
        width=0.7,
        top=True,
        right=True,
    )

    # Full frame around each plot
    for spine in ax.spines.values():
        spine.set_visible(True)
        spine.set_linewidth(0.8)


# ======================================================================
# PANEL LABELS
# ======================================================================

panel_labels = [
    "(a)",
    "(b)",
    "(c)",
    "(d)",
]

for ax, label in zip(
    axes.flatten(),
    panel_labels,
):

    ax.text(
        -0.13,
        1.06,
        label,
        transform=ax.transAxes,
        fontsize=PANEL_SIZE,
        fontweight="bold",
        va="bottom",
        ha="left",
        clip_on=False,
    )


# ======================================================================
# LAYOUT
# ======================================================================

fig.subplots_adjust(
    left=0.11,
    right=0.98,
    bottom=0.10,
    top=0.94,
    wspace=0.30,
    hspace=0.38,
)


# ======================================================================
# SAVE FIGURE
# ======================================================================

fig.savefig(
    OUTPUT_PNG,
    dpi=600,
    bbox_inches="tight",
)

fig.savefig(
    OUTPUT_PDF,
    bbox_inches="tight",
)

plt.show()

print(f"Saved: {OUTPUT_PNG}")
print(f"Saved: {OUTPUT_PDF}")
