from __future__ import annotations

import subprocess
import shutil
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
GENERATED_DIR = ROOT / "phreeqc_generated_files"
GENERATED_DIR.mkdir(parents=True, exist_ok=True)
WORKDIR = GENERATED_DIR

PHREEQC_EXE = Path(
    shutil.which("phreeqc")
    or r"C:\Program Files\USGS\phreeqc-3.8.6-17100-x64\bin\ClrRelease\phreeqc.exe"
)
DATABASE = ROOT / "database" / "frezchem.dat"
if not DATABASE.exists():
    DATABASE = PHREEQC_EXE.parent.parent / "database" / "frezchem.dat"

COMPOSITION_FILE = ROOT / "input_data" / "C3_C5.xlsx"
OLI_FILE = ROOT / "input_data" / "OLI_Simulation_C3_and_C5_Brine.xlsx"
OUTPUT_EXCEL = ROOT / "sensitivity_results/FC_FREZCHEM_Sensitivity_Results.xlsx"
OUTPUT_EXCEL.parent.mkdir(parents=True, exist_ok=True)

START_TEMP = 25.0
END_TEMP = -25.0
TEMP_STEP = -1.0

PHASE_MOL_EPS = 1.0e-12

DENSITY_OVERRIDE = {
    "C3": 1.04708,
    "C5": 1.04708,
}

CP_BRINE_KJ_KG_K = 3.80
LATENT_HEAT_ICE_KJ_KG = 333.55
COP_ASSUMED = 3.0
WATER_DENSITY_KG_M3 = 1000.0
MW_WATER_KG_MOL = 0.01801528

MW = {
    "Na": 22.989769,
    "K": 39.0983,
    "Mg": 24.305,
    "Ca": 40.078,
    "Cl": 35.45,
    "SO4": 96.06,
    "HCO3": 61.0168,
}

MW_NA = 22.989769
MW_CL = 35.45
MW_SO4 = 96.06
MW_H2O = 18.01528

MW_MIRABILITE = 2 * MW_NA + MW_SO4 + 10 * MW_H2O
MW_HYDROHALITE = MW_NA + MW_CL + 2 * MW_H2O

PHASE_STOICH = {
    "Ice": {
        "water": 1.0,
    },
    "Mirabilite": {
        "Na": 2.0,
        "S6": 1.0,
        "water": 10.0,
    },
    "Halite": {
        "Na": 1.0,
        "Cl": 1.0,
        "water": 0.0,
    },
    "Hydrohalite": {
        "Na": 1.0,
        "Cl": 1.0,
        "water": 2.0,
    },
    "Calcite": {
        "Ca": 1.0,
        "C4": 1.0,
        "water": 0.0,
    },
    "Gypsum": {
        "Ca": 1.0,
        "S6": 1.0,
        "water": 2.0,
    },
}

SOLID_PHASES = [
    "Mirabilite",
    "Halite",
    "Hydrohalite",
    "Calcite",
    "Gypsum",
]

def load_compositions() -> Dict[str, Dict[str, float]]:
    """
    Read C3 and C5 compositions from C3_C5.xlsx.

    IMPORTANT:
    frezchem.dat does not define Br in its standard master-species system.
    Therefore Br is deliberately excluded from this FREZCHEM sensitivity run.
    The omission is reported in the output workbook and should be disclosed
    when comparing with the original pitzer.dat calculation.
    """
    if not COMPOSITION_FILE.exists():
        raise FileNotFoundError(
            f"Composition workbook not found:\n{COMPOSITION_FILE}"
        )

    df = pd.read_excel(COMPOSITION_FILE)

    required = [
        "Case ID",
        "pH",
        "TDS, mg/L",
        "Cl, mg/L",
        "Na, mg/L",
        "SO4, mg/L",
        "Mg, mg/L",
        "Ca, mg/L",
        "K, mg/L",
        "HCO3, mg/L",
    ]

    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Missing columns in composition file: {missing}")

    cases = {}

    for _, row in df.iterrows():
        case_name = str(row["Case ID"]).strip()
        if case_name not in {"C3", "C5"}:
            continue

        cases[case_name] = {
            "pH": float(row["pH"]),
            "TDS": float(row["TDS, mg/L"]),
            "Na": float(row["Na, mg/L"]),
            "K": float(row["K, mg/L"]),
            "Mg": float(row["Mg, mg/L"]),
            "Ca": float(row["Ca, mg/L"]),
            "Cl": float(row["Cl, mg/L"]),
            "SO4": float(row["SO4, mg/L"]),
            "HCO3": float(row["HCO3, mg/L"]),
            "density": DENSITY_OVERRIDE.get(case_name),
        }

    if "C3" not in cases or "C5" not in cases:
        raise ValueError("Both C3 and C5 must be present in C3_C5.xlsx.")

    return cases

def make_temperature_grid(
    start: float,
    end: float,
    step: float,
) -> List[float]:
    if step >= 0:
        raise ValueError("TEMP_STEP must be negative.")

    temps = []
    t = start

    while t >= end - 1e-9:
        temps.append(round(t, 6))
        t += step

    return temps

TEMPERATURES = make_temperature_grid(
    START_TEMP,
    END_TEMP,
    TEMP_STEP,
)

def run_phreeqc(
    input_text: str,
    input_path: Path,
    output_path: Path,
) -> Tuple[bool, str]:

    input_path.write_text(input_text, encoding="utf-8")

    if not Path(PHREEQC_EXE).exists():
        raise FileNotFoundError(
            f"PHREEQC executable not found:\n{PHREEQC_EXE}"
        )

    if not Path(DATABASE).exists():
        raise FileNotFoundError(
            f"FREZCHEM database not found:\n{DATABASE}"
        )

    cmd = [
        PHREEQC_EXE,
        str(input_path),
        str(output_path),
        DATABASE,
    ]

    result = subprocess.run(
        cmd,
        shell=False,
        capture_output=True,
        text=True,
    )

    if result.returncode == 0:
        return True, ""

    message = (
        f"PHREEQC return code: {result.returncode}\n"
        f"{result.stdout}\n"
        f"{result.stderr}"
    )

    if output_path.exists():
        try:
            text = output_path.read_text(
                encoding="utf-8",
                errors="ignore",
            )
            message += (
                "\n\nLast lines of PHREEQC output:\n"
                + "\n".join(text.splitlines()[-80:])
            )
        except Exception:
            pass

    return False, message

def read_selected_output(selected_path: Path) -> pd.DataFrame:
    return pd.read_csv(
        selected_path,
        sep=r"\s+",
        comment="#",
        engine="python",
    )

def user_punch_block(
    selected_path: Path,
    include_phases: bool,
) -> str:

    file_name = selected_path.as_posix()

    if not include_phases:
        return f"""
SELECTED_OUTPUT 1
    -file {file_name}
    -reset false
    -user_punch true
USER_PUNCH 1
    -headings Temp_C pH Water_kg Alk_eq_kgw Mu aw Na_mol K_mol Mg_mol Ca_mol Cl_mol S6_mol C4_mol Na_m K_m Mg_m Ca_m Cl_m S6_m C4_m Na_act Cl_act SO4_act SI_Ice SI_Mirabilite SI_Halite SI_Hydrohalite SI_Calcite SI_Gypsum Iterations
    10 PUNCH TC, -LA("H+"), TOT("water"), ALK, MU, ACT("H2O")
    20 PUNCH TOTMOLE("Na"), TOTMOLE("K"), TOTMOLE("Mg"), TOTMOLE("Ca")
    30 PUNCH TOTMOLE("Cl"), TOTMOLE("S(6)"), TOTMOLE("C(4)")
    40 PUNCH TOT("Na"), TOT("K"), TOT("Mg"), TOT("Ca")
    50 PUNCH TOT("Cl"), TOT("S(6)"), TOT("C(4)")
    60 PUNCH ACT("Na+"), ACT("Cl-"), ACT("SO4-2")
    70 PUNCH SI("Ice(s)"), SI("Mirabilite"), SI("Halite"), SI("Hydrohalite"), SI("Calcite"), SI("Gypsum")
    80 PUNCH ITERATIONS
"""

    return f"""
SELECTED_OUTPUT 1
    -file {file_name}
    -reset false
    -user_punch true
USER_PUNCH 1
    -headings Temp_C pH Water_kg Alk_eq_kgw Mu aw Na_mol K_mol Mg_mol Ca_mol Cl_mol S6_mol C4_mol Na_m K_m Mg_m Ca_m Cl_m S6_m C4_m Na_act Cl_act SO4_act SI_Ice SI_Mirabilite SI_Halite SI_Hydrohalite SI_Calcite SI_Gypsum Ice_mol Mirabilite_mol Halite_mol Hydrohalite_mol Calcite_mol Gypsum_mol Iterations
    10 PUNCH TC, -LA("H+"), TOT("water"), ALK, MU, ACT("H2O")
    20 PUNCH TOTMOLE("Na"), TOTMOLE("K"), TOTMOLE("Mg"), TOTMOLE("Ca")
    30 PUNCH TOTMOLE("Cl"), TOTMOLE("S(6)"), TOTMOLE("C(4)")
    40 PUNCH TOT("Na"), TOT("K"), TOT("Mg"), TOT("Ca")
    50 PUNCH TOT("Cl"), TOT("S(6)"), TOT("C(4)")
    60 PUNCH ACT("Na+"), ACT("Cl-"), ACT("SO4-2")
    70 PUNCH SI("Ice(s)"), SI("Mirabilite"), SI("Halite"), SI("Hydrohalite"), SI("Calcite"), SI("Gypsum")
    80 PUNCH EQUI("Ice(s)"), EQUI("Mirabilite"), EQUI("Halite"), EQUI("Hydrohalite"), EQUI("Calcite"), EQUI("Gypsum")
    90 PUNCH ITERATIONS
"""

def build_initial_input(
    case_name: str,
    brine: Dict[str, float],
    selected_path: Path,
) -> str:

    density_line = ""
    if brine["density"] is not None:
        density_line = f"    density {brine['density']:.8f}"

    punch = user_punch_block(
        selected_path=selected_path,
        include_phases=False,
    )

    return f"""
TITLE {case_name} initial brine - FREZCHEM
SOLUTION 1
    temp {START_TEMP:.2f}
    pH {brine['pH']:.8f}
    units mg/L
{density_line}
    Na {brine['Na']:.10f}
    K {brine['K']:.10f}
    Mg {brine['Mg']:.10f}
    Ca {brine['Ca']:.10f}
    Cl {brine['Cl']:.10f}
    S(6) {brine['SO4']:.10f} as SO4
    Alkalinity {brine['HCO3']:.10f} as HCO3
{punch}
END
""".strip() + "\n"

def build_state_input(
    case_name: str,
    temp_c: float,
    pH: float,
    water_kg: float,
    element_moles: Dict[str, float],
    selected_path: Path,
    equilibrium_phases: bool,
) -> str:

    if water_kg <= 0:
        raise ValueError("Water mass must be greater than zero.")

    molality = {
        key: value / water_kg
        for key, value in element_moles.items()
    }

    phases = ""

    if equilibrium_phases:
        phases = """
EQUILIBRIUM_PHASES 1
    Ice(s)       0.0 0.0
    Mirabilite   0.0 0.0
    Halite       0.0 0.0
    Hydrohalite  0.0 0.0
    Calcite      0.0 0.0
    Gypsum       0.0 0.0
"""

    punch = user_punch_block(
        selected_path=selected_path,
        include_phases=equilibrium_phases,
    )

    return f"""
TITLE {case_name} FREZCHEM sequential FC at {temp_c:.2f} C
SOLUTION 1
    temp {temp_c:.8f}
    pH {pH:.10f}
    units mol/kgw
    -water {water_kg:.12f}
    Na {molality['Na']:.14e}
    K {molality['K']:.14e}
    Mg {molality['Mg']:.14e}
    Ca {molality['Ca']:.14e}
    Cl {molality['Cl']:.14e}
    S(6) {molality['S6']:.14e}
    C(4) {molality['C4']:.14e}
{phases}
{punch}
END
""".strip() + "\n"

MOLE_COLUMNS = {
    "Na": "Na_mol",
    "K": "K_mol",
    "Mg": "Mg_mol",
    "Ca": "Ca_mol",
    "Cl": "Cl_mol",
    "S6": "S6_mol",
    "C4": "C4_mol",
}

MOLALITY_COLUMNS = {
    "Na": "Na_m",
    "K": "K_m",
    "Mg": "Mg_m",
    "Ca": "Ca_m",
    "Cl": "Cl_m",
    "S6": "S6_m",
    "C4": "C4_m",
}

def row_to_moles(row: pd.Series) -> Dict[str, float]:
    output = {}
    for key, col in MOLE_COLUMNS.items():
        value = row.get(col, 0.0)
        if pd.isna(value):
            value = 0.0
        output[key] = float(value)
    return output

def row_to_molalities(row: pd.Series) -> Dict[str, float]:
    output = {}
    for key, col in MOLALITY_COLUMNS.items():
        value = row.get(col, 0.0)
        if pd.isna(value):
            value = 0.0
        output[key] = float(value)
    return output

def initialize_case(
    case_name: str,
    brine: Dict[str, float],
) -> Dict:

    selected_path = WORKDIR / f"{case_name}_FREZ_initial_selected.txt"
    input_path = WORKDIR / f"{case_name}_FREZ_initial.pqi"
    output_path = WORKDIR / f"{case_name}_FREZ_initial.out"

    input_text = build_initial_input(
        case_name=case_name,
        brine=brine,
        selected_path=selected_path,
    )

    success, message = run_phreeqc(
        input_text=input_text,
        input_path=input_path,
        output_path=output_path,
    )

    if not success:
        raise RuntimeError(message)

    selected = read_selected_output(selected_path)
    row = selected.iloc[-1]

    return {
        "water_kg": float(row["Water_kg"]),
        "pH": float(row["pH"]),
        "moles": row_to_moles(row),
        "molalities": row_to_molalities(row),
        "row": row,
    }

def run_temperature_state(
    case_name: str,
    temp_c: float,
    pH: float,
    water_kg: float,
    element_moles: Dict[str, float],
    stage: str,
    equilibrium_phases: bool,
) -> Tuple[pd.Series | None, str]:

    temp_label = f"{temp_c:+06.1f}".replace(".", "p")

    selected_path = (
        WORKDIR / f"{case_name}_FREZ_{stage}_{temp_label}.txt"
    )
    input_path = (
        WORKDIR / f"{case_name}_FREZ_{stage}_{temp_label}.pqi"
    )
    output_path = (
        WORKDIR / f"{case_name}_FREZ_{stage}_{temp_label}.out"
    )

    input_text = build_state_input(
        case_name=case_name,
        temp_c=temp_c,
        pH=pH,
        water_kg=water_kg,
        element_moles=element_moles,
        selected_path=selected_path,
        equilibrium_phases=equilibrium_phases,
    )

    success, message = run_phreeqc(
        input_text=input_text,
        input_path=input_path,
        output_path=output_path,
    )

    if not success:
        return None, message

    selected = read_selected_output(selected_path)
    return selected.iloc[-1], ""

def solid_component_moles(
    cumulative_phases: Dict[str, float],
    component: str,
) -> float:

    total = 0.0

    for phase, phase_moles in cumulative_phases.items():
        if phase == "Ice":
            continue

        coefficient = PHASE_STOICH[phase].get(component, 0.0)
        total += coefficient * phase_moles

    return total

def hydrated_water_moles(
    cumulative_phases: Dict[str, float],
) -> float:

    total = 0.0

    for phase in SOLID_PHASES:
        hydration = PHASE_STOICH[phase].get("water", 0.0)
        total += hydration * cumulative_phases.get(phase, 0.0)

    return total

def component_balance_errors(
    initial_moles: Dict[str, float],
    aqueous_moles: Dict[str, float],
    cumulative_phases: Dict[str, float],
) -> Dict[str, float]:

    errors = {}

    for component, initial in initial_moles.items():
        if abs(initial) < 1e-30:
            errors[component] = np.nan
            continue

        accounted = (
            aqueous_moles.get(component, 0.0)
            + solid_component_moles(
                cumulative_phases,
                component,
            )
        )

        errors[component] = (
            (accounted - initial)
            / initial
            * 100.0
        )

    return errors

def water_balance_error(
    initial_water_kg: float,
    liquid_water_kg: float,
    cumulative_ice_mol: float,
    cumulative_phases: Dict[str, float],
) -> float:

    initial_water_mol = initial_water_kg / MW_WATER_KG_MOL
    liquid_water_mol = liquid_water_kg / MW_WATER_KG_MOL

    accounted = (
        liquid_water_mol
        + cumulative_ice_mol
        + hydrated_water_moles(cumulative_phases)
    )

    return (
        (accounted - initial_water_mol)
        / initial_water_mol
        * 100.0
    )

def approximate_solute_mass_kg(
    moles: Dict[str, float],
) -> float:

    mass_g = 0.0
    mass_g += moles["Na"] * MW["Na"]
    mass_g += moles["K"] * MW["K"]
    mass_g += moles["Mg"] * MW["Mg"]
    mass_g += moles["Ca"] * MW["Ca"]
    mass_g += moles["Cl"] * MW["Cl"]
    mass_g += moles["S6"] * MW["SO4"]
    mass_g += moles["C4"] * MW["HCO3"]

    return mass_g / 1000.0

def simulate_case(
    case_name: str,
    brine: Dict[str, float],
) -> Tuple[pd.DataFrame, Dict]:

    print("\n" + "=" * 70)
    print(f"STARTING FREZCHEM THERMODYNAMIC RUN: {case_name}")
    print("=" * 70)

    initial = initialize_case(
        case_name=case_name,
        brine=brine,
    )

    initial_water_kg = float(initial["water_kg"])
    initial_moles = initial["moles"].copy()
    initial_molalities = initial["molalities"].copy()

    current_water_kg = initial_water_kg
    current_moles = initial_moles.copy()
    current_pH = float(initial["pH"])

    cumulative_phases = {
        "Ice": 0.0,
        "Mirabilite": 0.0,
        "Halite": 0.0,
        "Hydrohalite": 0.0,
        "Calcite": 0.0,
        "Gypsum": 0.0,
    }

    cumulative_q_sensible = 0.0
    cumulative_q_latent = 0.0

    records = []
    previous_temp = START_TEMP

    status = {
        "case": case_name,
        "status": "Completed",
        "last_successful_temperature_c": START_TEMP,
        "message": "",
    }

    for step_index, temp_c in enumerate(TEMPERATURES):

        print(f"{case_name}: {temp_c:6.1f} °C")

        if step_index == 0:
            q_sensible_step = 0.0
        else:
            solute_mass_kg = approximate_solute_mass_kg(current_moles)
            liquid_brine_mass = current_water_kg + solute_mass_kg
            delta_t = abs(temp_c - previous_temp)

            q_sensible_step = (
                liquid_brine_mass
                * CP_BRINE_KJ_KG_K
                * delta_t
            )

        cumulative_q_sensible += q_sensible_step

        pre_row, error = run_temperature_state(
            case_name=case_name,
            temp_c=temp_c,
            pH=current_pH,
            water_kg=current_water_kg,
            element_moles=current_moles,
            stage="pre",
            equilibrium_phases=False,
        )

        if pre_row is None:
            status["status"] = "Stopped: pre-equilibrium failure"
            status["last_successful_temperature_c"] = previous_temp
            status["message"] = error
            print(error)
            break

        eq_row, error = run_temperature_state(
            case_name=case_name,
            temp_c=temp_c,
            pH=current_pH,
            water_kg=current_water_kg,
            element_moles=current_moles,
            stage="eq",
            equilibrium_phases=True,
        )

        if eq_row is None:
            status["status"] = "Stopped: equilibrium failure"
            status["last_successful_temperature_c"] = previous_temp
            status["message"] = error
            print(error)
            break

        equilibrium_water_kg = float(eq_row["Water_kg"])
        equilibrium_moles = row_to_moles(eq_row)
        equilibrium_molalities = row_to_molalities(eq_row)
        equilibrium_pH = float(eq_row["pH"])

        phase_step = {
            "Ice": max(0.0, float(eq_row["Ice_mol"])),
            "Mirabilite": max(0.0, float(eq_row["Mirabilite_mol"])),
            "Halite": max(0.0, float(eq_row["Halite_mol"])),
            "Hydrohalite": max(0.0, float(eq_row["Hydrohalite_mol"])),
            "Calcite": max(0.0, float(eq_row["Calcite_mol"])),
            "Gypsum": max(0.0, float(eq_row["Gypsum_mol"])),
        }

        for phase in cumulative_phases:
            cumulative_phases[phase] += phase_step[phase]

        ice_step_kg = (
            phase_step["Ice"]
            * MW_WATER_KG_MOL
        )

        cumulative_ice_kg = (
            cumulative_phases["Ice"]
            * MW_WATER_KG_MOL
        )

        q_latent_step = (
            ice_step_kg
            * LATENT_HEAT_ICE_KJ_KG
        )

        cumulative_q_latent += q_latent_step

        liquid_water_fraction = (
            equilibrium_water_kg
            / initial_water_kg
        )

        concentration_factor = (
            initial_water_kg
            / equilibrium_water_kg
        )

        ice_recovery_pct = (
            cumulative_ice_kg
            / initial_water_kg
            * 100.0
        )

        so4_recovery_mirabilite = (
            cumulative_phases["Mirabilite"]
            / initial_moles["S6"]
            * 100.0
            if initial_moles["S6"] > 0
            else np.nan
        )

        na_in_nacl_phases = (
            cumulative_phases["Halite"]
            + cumulative_phases["Hydrohalite"]
        )

        cl_in_nacl_phases = (
            cumulative_phases["Halite"]
            + cumulative_phases["Hydrohalite"]
        )

        na_recovery_nacl = (
            na_in_nacl_phases
            / initial_moles["Na"]
            * 100.0
            if initial_moles["Na"] > 0
            else np.nan
        )

        cl_recovery_nacl = (
            cl_in_nacl_phases
            / initial_moles["Cl"]
            * 100.0
            if initial_moles["Cl"] > 0
            else np.nan
        )

        na_recovery_hydrohalite = (
            cumulative_phases["Hydrohalite"]
            / initial_moles["Na"]
            * 100.0
            if initial_moles["Na"] > 0
            else np.nan
        )

        cl_recovery_hydrohalite = (
            cumulative_phases["Hydrohalite"]
            / initial_moles["Cl"]
            * 100.0
            if initial_moles["Cl"] > 0
            else np.nan
        )

        errors = component_balance_errors(
            initial_moles=initial_moles,
            aqueous_moles=equilibrium_moles,
            cumulative_phases=cumulative_phases,
        )

        finite_errors = [
            abs(v)
            for v in errors.values()
            if np.isfinite(v)
        ]

        max_component_error = (
            max(finite_errors)
            if finite_errors
            else np.nan
        )

        water_error = water_balance_error(
            initial_water_kg=initial_water_kg,
            liquid_water_kg=equilibrium_water_kg,
            cumulative_ice_mol=cumulative_phases["Ice"],
            cumulative_phases=cumulative_phases,
        )

        total_q_cooling = (
            cumulative_q_sensible
            + cumulative_q_latent
        )

        electrical_energy_kwh = (
            total_q_cooling
            / 3600.0
            / COP_ASSUMED
        )

        recovered_water_m3 = (
            cumulative_ice_kg
            / WATER_DENSITY_KG_M3
        )

        sec = (
            electrical_energy_kwh
            / recovered_water_m3
            if recovered_water_m3 > 0
            else np.nan
        )

        record = {
            "case": case_name,
            "step": step_index,
            "temperature_c": temp_c,

            "water_before_equilibrium_kg": current_water_kg,
            "equilibrium_liquid_water_kg": equilibrium_water_kg,

            "ice_step_mol": phase_step["Ice"],
            "ice_step_kg": ice_step_kg,
            "cumulative_ice_mol": cumulative_phases["Ice"],
            "cumulative_ice_kg": cumulative_ice_kg,
            "ice_recovery_pct": ice_recovery_pct,
            "liquid_water_fraction": liquid_water_fraction,
            "concentration_factor": concentration_factor,

            "pH": equilibrium_pH,
            "ionic_strength_mol_kgw": float(eq_row["Mu"]),
            "water_activity": float(eq_row["aw"]),
            "phreeqc_iterations": float(eq_row["Iterations"]),

            "si_ice_pre": float(pre_row["SI_Ice"]),
            "si_ice_post": float(eq_row["SI_Ice"]),
            "si_mirabilite_pre": float(pre_row["SI_Mirabilite"]),
            "si_mirabilite_post": float(eq_row["SI_Mirabilite"]),
            "si_halite_pre": float(pre_row["SI_Halite"]),
            "si_halite_post": float(eq_row["SI_Halite"]),
            "si_hydrohalite_pre": float(pre_row["SI_Hydrohalite"]),
            "si_hydrohalite_post": float(eq_row["SI_Hydrohalite"]),
            "si_calcite_pre": float(pre_row["SI_Calcite"]),
            "si_calcite_post": float(eq_row["SI_Calcite"]),
            "si_gypsum_pre": float(pre_row["SI_Gypsum"]),
            "si_gypsum_post": float(eq_row["SI_Gypsum"]),

            "mirabilite_step_mol": phase_step["Mirabilite"],
            "halite_step_mol": phase_step["Halite"],
            "hydrohalite_step_mol": phase_step["Hydrohalite"],
            "calcite_step_mol": phase_step["Calcite"],
            "gypsum_step_mol": phase_step["Gypsum"],

            "mirabilite_cumulative_mol": cumulative_phases["Mirabilite"],
            "halite_cumulative_mol": cumulative_phases["Halite"],
            "hydrohalite_cumulative_mol": cumulative_phases["Hydrohalite"],
            "calcite_cumulative_mol": cumulative_phases["Calcite"],
            "gypsum_cumulative_mol": cumulative_phases["Gypsum"],

            "so4_recovery_as_mirabilite_pct": so4_recovery_mirabilite,
            "na_recovery_as_nacl_phases_pct": na_recovery_nacl,
            "cl_recovery_as_nacl_phases_pct": cl_recovery_nacl,
            "na_recovery_as_hydrohalite_pct": na_recovery_hydrohalite,
            "cl_recovery_as_hydrohalite_pct": cl_recovery_hydrohalite,

            "q_sensible_step_kj": q_sensible_step,
            "q_latent_step_kj": q_latent_step,
            "q_sensible_cumulative_kj": cumulative_q_sensible,
            "q_latent_cumulative_kj": cumulative_q_latent,
            "q_total_cooling_kj": total_q_cooling,
            "electrical_energy_kwh": electrical_energy_kwh,
            "sec_kwh_m3_recovered_ice_equivalent": sec,

            "max_component_balance_error_pct": max_component_error,
            "water_balance_error_pct": water_error,
        }

        for element in MOLE_COLUMNS:
            record[f"{element}_mol"] = equilibrium_moles[element]
            record[f"{element}_mol_kgw"] = equilibrium_molalities[element]

            initial_value = initial_molalities[element]
            record[f"{element}_normalized"] = (
                equilibrium_molalities[element] / initial_value
                if abs(initial_value) > 1e-30
                else np.nan
            )

            record[f"{element}_balance_error_pct"] = errors[element]

        records.append(record)

        current_water_kg = equilibrium_water_kg
        current_moles = equilibrium_moles.copy()
        current_pH = equilibrium_pH

        previous_temp = temp_c
        status["last_successful_temperature_c"] = temp_c

    return pd.DataFrame(records), status

def phase_onset_interval(
    df: pd.DataFrame,
    phase_column: str,
    threshold: float = PHASE_MOL_EPS,
) -> Dict[str, float]:

    if df.empty:
        return {
            "upper_temperature_c": np.nan,
            "lower_temperature_c": np.nan,
            "first_active_temperature_c": np.nan,
        }

    data = (
        df.sort_values("temperature_c", ascending=False)
        .reset_index(drop=True)
    )

    active = data[phase_column] > threshold
    indices = data.index[active].tolist()

    if not indices:
        return {
            "upper_temperature_c": np.nan,
            "lower_temperature_c": np.nan,
            "first_active_temperature_c": np.nan,
        }

    idx = indices[0]
    lower = float(data.loc[idx, "temperature_c"])

    upper = (
        np.nan
        if idx == 0
        else float(data.loc[idx - 1, "temperature_c"])
    )

    return {
        "upper_temperature_c": upper,
        "lower_temperature_c": lower,
        "first_active_temperature_c": lower,
    }

def build_phase_onset_table(
    results: Dict[str, pd.DataFrame],
) -> pd.DataFrame:

    phase_map = {
        "Ice(s)": "ice_step_mol",
        "Mirabilite": "mirabilite_step_mol",
        "Halite": "halite_step_mol",
        "Hydrohalite": "hydrohalite_step_mol",
        "Calcite": "calcite_step_mol",
        "Gypsum": "gypsum_step_mol",
    }

    rows = []

    for case, df in results.items():
        for phase, column in phase_map.items():
            onset = phase_onset_interval(
                df,
                column,
            )

            rows.append({
                "case": case,
                "phase": phase,
                "model": "PHREEQC-frezchem.dat",
                **onset,
            })

    return pd.DataFrame(rows)

def build_summary(
    results: Dict[str, pd.DataFrame],
) -> pd.DataFrame:

    rows = []

    for case, df in results.items():
        if df.empty:
            continue

        last = df.iloc[-1]

        rows.append({
            "case": case,
            "final_temperature_c": last["temperature_c"],
            "ice_recovery_pct": last["ice_recovery_pct"],
            "concentration_factor": last["concentration_factor"],
            "so4_recovery_as_mirabilite_pct":
                last["so4_recovery_as_mirabilite_pct"],
            "na_recovery_as_nacl_phases_pct":
                last["na_recovery_as_nacl_phases_pct"],
            "cl_recovery_as_nacl_phases_pct":
                last["cl_recovery_as_nacl_phases_pct"],
            "na_recovery_as_hydrohalite_pct":
                last["na_recovery_as_hydrohalite_pct"],
            "cl_recovery_as_hydrohalite_pct":
                last["cl_recovery_as_hydrohalite_pct"],
            "halite_cumulative_mol":
                last["halite_cumulative_mol"],
            "hydrohalite_cumulative_mol":
                last["hydrohalite_cumulative_mol"],
            "ionic_strength_mol_kgw":
                last["ionic_strength_mol_kgw"],
            "water_activity":
                last["water_activity"],
            "max_component_balance_error_pct":
                df["max_component_balance_error_pct"].abs().max(),
            "max_abs_water_balance_error_pct":
                df["water_balance_error_pct"].abs().max(),
            "sec_kwh_m3_recovered_ice_equivalent":
                last["sec_kwh_m3_recovered_ice_equivalent"],
        })

    return pd.DataFrame(rows)

SENSITIVITY_FRACTION = 0.10
SENSITIVITY_COMPONENTS = ["Na", "Cl", "SO4", "Mg", "Ca"]

PHASE_ONSET_COLUMNS = {
    "Mirabilite": "mirabilite_step_mol",
    "Hydrohalite": "hydrohalite_step_mol",
}

PRE_SI_COLUMNS = {
    "Mirabilite": "si_mirabilite_pre",
    "Hydrohalite": "si_hydrohalite_pre",
}

FINAL_OUTPUT_COLUMNS = {
    "ice_recovery_pct": "Ice recovery (%)",
    "so4_recovery_as_mirabilite_pct": "SO4 recovery as mirabilite (%)",
    "na_recovery_as_hydrohalite_pct": "Na recovery as hydrohalite (%)",
    "cl_recovery_as_hydrohalite_pct": "Cl recovery as hydrohalite (%)",
    "concentration_factor": "Concentration factor (-)",
    "ionic_strength_mol_kgw": "Ionic strength (mol/kgw)",
    "water_activity": "Water activity (-)",
    "sec_kwh_m3_recovered_ice_equivalent": "SEC (kWh/m3 recovered ice-equivalent)",
}


def safe_label(text: str) -> str:
    return (
        str(text)
        .replace("+", "plus")
        .replace("-", "minus")
        .replace("%", "pct")
        .replace(" ", "_")
        .replace("/", "_")
    )


def build_scenarios() -> List[Dict]:
    scenarios = [{
        "scenario": "Baseline",
        "component": "Baseline",
        "perturbation_fraction": 0.0,
        "multiplier": 1.0,
    }]

    for component in SENSITIVITY_COMPONENTS:
        scenarios.append({
            "scenario": f"{component}_minus10pct",
            "component": component,
            "perturbation_fraction": -SENSITIVITY_FRACTION,
            "multiplier": 1.0 - SENSITIVITY_FRACTION,
        })
        scenarios.append({
            "scenario": f"{component}_plus10pct",
            "component": component,
            "perturbation_fraction": SENSITIVITY_FRACTION,
            "multiplier": 1.0 + SENSITIVITY_FRACTION,
        })

    return scenarios


def perturb_composition(
    baseline: Dict[str, float],
    component: str,
    multiplier: float,
) -> Dict[str, float]:
    modified = baseline.copy()

    if component != "Baseline":
        if component not in modified:
            raise KeyError(
                f"Component '{component}' is not present in the brine composition."
            )
        modified[component] = float(modified[component]) * float(multiplier)

    return modified


def interpolate_si_zero_crossing(
    df: pd.DataFrame,
    si_column: str,
) -> float:
    if df.empty or si_column not in df.columns:
        return np.nan

    data = (
        df[["temperature_c", si_column]]
        .dropna()
        .sort_values("temperature_c", ascending=False)
        .reset_index(drop=True)
    )

    if len(data) < 2:
        return np.nan

    for i in range(1, len(data)):
        t1 = float(data.loc[i - 1, "temperature_c"])
        t2 = float(data.loc[i, "temperature_c"])
        s1 = float(data.loc[i - 1, si_column])
        s2 = float(data.loc[i, si_column])

        if s1 == 0.0:
            return t1
        if s2 == 0.0:
            return t2

        if (s1 < 0.0 <= s2) or (s1 > 0.0 >= s2):
            if abs(s2 - s1) < 1.0e-30:
                return np.nan
            return t1 + (0.0 - s1) * (t2 - t1) / (s2 - s1)

    return np.nan


def extract_run_summary(
    base_case: str,
    scenario: Dict,
    run_name: str,
    composition: Dict[str, float],
    df: pd.DataFrame,
    status: Dict,
) -> Dict:
    row = {
        "base_case": base_case,
        "scenario": scenario["scenario"],
        "component": scenario["component"],
        "perturbation_fraction": scenario["perturbation_fraction"],
        "perturbation_percent": scenario["perturbation_fraction"] * 100.0,
        "multiplier": scenario["multiplier"],
        "run_name": run_name,
        "status": status.get("status", ""),
        "last_successful_temperature_c":
            status.get("last_successful_temperature_c", np.nan),
        "message": status.get("message", ""),
        "input_pH": composition["pH"],
        "input_TDS_mg_L_reported": composition["TDS"],
        "input_Na_mg_L": composition["Na"],
        "input_Cl_mg_L": composition["Cl"],
        "input_SO4_mg_L": composition["SO4"],
        "input_Mg_mg_L": composition["Mg"],
        "input_Ca_mg_L": composition["Ca"],
        "input_K_mg_L": composition["K"],
        "input_HCO3_mg_L": composition["HCO3"],
    }

    if df.empty:
        for column in FINAL_OUTPUT_COLUMNS:
            row[column] = np.nan

        for phase in PHASE_ONSET_COLUMNS:
            row[f"{phase.lower()}_onset_upper_c"] = np.nan
            row[f"{phase.lower()}_onset_lower_c"] = np.nan
            row[f"{phase.lower()}_first_active_c"] = np.nan
            row[f"{phase.lower()}_si0_interpolated_c"] = np.nan

        row["max_component_balance_error_pct"] = np.nan
        row["max_abs_water_balance_error_pct"] = np.nan
        return row

    final = df.iloc[-1]

    for column in FINAL_OUTPUT_COLUMNS:
        row[column] = float(final[column])

    for phase, phase_column in PHASE_ONSET_COLUMNS.items():
        onset = phase_onset_interval(
            df=df,
            phase_column=phase_column,
            threshold=PHASE_MOL_EPS,
        )
        prefix = phase.lower()
        row[f"{prefix}_onset_upper_c"] = onset["upper_temperature_c"]
        row[f"{prefix}_onset_lower_c"] = onset["lower_temperature_c"]
        row[f"{prefix}_first_active_c"] = onset["first_active_temperature_c"]
        row[f"{prefix}_si0_interpolated_c"] = interpolate_si_zero_crossing(
            df,
            PRE_SI_COLUMNS[phase],
        )

    row["max_component_balance_error_pct"] = float(
        df["max_component_balance_error_pct"].abs().max()
    )
    row["max_abs_water_balance_error_pct"] = float(
        df["water_balance_error_pct"].abs().max()
    )

    return row


def build_effect_table(run_summary: pd.DataFrame) -> pd.DataFrame:
    rows = []

    onset_outputs = {
        "mirabilite_si0_interpolated_c":
            "Mirabilite interpolated SI=0 temperature (°C)",
        "hydrohalite_si0_interpolated_c":
            "Hydrohalite interpolated SI=0 temperature (°C)",
        "mirabilite_first_active_c":
            "Mirabilite first-active temperature (°C)",
        "hydrohalite_first_active_c":
            "Hydrohalite first-active temperature (°C)",
    }

    all_outputs = dict(FINAL_OUTPUT_COLUMNS)
    all_outputs.update(onset_outputs)

    for base_case in ["C3", "C5"]:
        case_data = run_summary[
            run_summary["base_case"].eq(base_case)
        ].copy()

        baseline_rows = case_data[
            case_data["scenario"].eq("Baseline")
        ]

        if baseline_rows.empty:
            continue

        baseline = baseline_rows.iloc[0]

        for component in SENSITIVITY_COMPONENTS:
            minus_rows = case_data[
                case_data["scenario"].eq(f"{component}_minus10pct")
            ]
            plus_rows = case_data[
                case_data["scenario"].eq(f"{component}_plus10pct")
            ]

            if minus_rows.empty or plus_rows.empty:
                continue

            minus = minus_rows.iloc[0]
            plus = plus_rows.iloc[0]

            for output_col, output_name in all_outputs.items():
                y0 = pd.to_numeric(
                    pd.Series([baseline.get(output_col, np.nan)]),
                    errors="coerce",
                ).iloc[0]
                ym = pd.to_numeric(
                    pd.Series([minus.get(output_col, np.nan)]),
                    errors="coerce",
                ).iloc[0]
                yp = pd.to_numeric(
                    pd.Series([plus.get(output_col, np.nan)]),
                    errors="coerce",
                ).iloc[0]

                if not (np.isfinite(y0) and np.isfinite(ym) and np.isfinite(yp)):
                    continue

                minus_change = ym - y0
                plus_change = yp - y0
                full_span = yp - ym
                central_half_range = full_span / 2.0

                relative_minus_pct = (
                    minus_change / y0 * 100.0
                    if abs(y0) > 1.0e-30
                    else np.nan
                )
                relative_plus_pct = (
                    plus_change / y0 * 100.0
                    if abs(y0) > 1.0e-30
                    else np.nan
                )

                normalized_sensitivity = (
                    (yp - ym)
                    / (2.0 * SENSITIVITY_FRACTION * y0)
                    if abs(y0) > 1.0e-30
                    else np.nan
                )

                rows.append({
                    "base_case": base_case,
                    "component": component,
                    "output": output_name,
                    "output_column": output_col,
                    "baseline_value": y0,
                    "minus10_value": ym,
                    "plus10_value": yp,
                    "minus10_change": minus_change,
                    "plus10_change": plus_change,
                    "minus10_relative_change_pct": relative_minus_pct,
                    "plus10_relative_change_pct": relative_plus_pct,
                    "plus_minus_span": full_span,
                    "central_half_range": central_half_range,
                    "absolute_central_half_range":
                        abs(central_half_range),
                    "normalized_sensitivity_coefficient":
                        normalized_sensitivity,
                    "absolute_normalized_sensitivity":
                        abs(normalized_sensitivity)
                        if np.isfinite(normalized_sensitivity)
                        else np.nan,
                })

    return pd.DataFrame(rows)


def build_rank_table(effect_table: pd.DataFrame) -> pd.DataFrame:
    if effect_table.empty:
        return pd.DataFrame()

    ranked = effect_table.copy()

    onset_mask = ranked["output_column"].isin([
        "mirabilite_si0_interpolated_c",
        "hydrohalite_si0_interpolated_c",
        "mirabilite_first_active_c",
        "hydrohalite_first_active_c",
    ])

    ranked["ranking_metric"] = np.where(
        onset_mask,
        ranked["absolute_central_half_range"],
        ranked["absolute_normalized_sensitivity"],
    )

    ranked["ranking_basis"] = np.where(
        onset_mask,
        "Absolute central half-range in onset temperature (°C)",
        "Absolute normalized sensitivity coefficient",
    )

    ranked["sensitivity_rank"] = (
        ranked.groupby(["base_case", "output"])["ranking_metric"]
        .rank(method="min", ascending=False)
    )

    return ranked.sort_values(
        ["base_case", "output", "sensitivity_rank", "component"]
    ).reset_index(drop=True)


def build_top_influences(rank_table: pd.DataFrame) -> pd.DataFrame:
    if rank_table.empty:
        return pd.DataFrame()

    top = rank_table[
        rank_table["sensitivity_rank"].eq(1)
    ].copy()

    columns = [
        "base_case",
        "output",
        "component",
        "baseline_value",
        "minus10_value",
        "plus10_value",
        "minus10_change",
        "plus10_change",
        "ranking_metric",
        "ranking_basis",
    ]

    return top[columns].reset_index(drop=True)


def build_input_table(
    baseline_cases: Dict[str, Dict[str, float]],
    scenarios: List[Dict],
) -> pd.DataFrame:
    rows = []

    for base_case, baseline in baseline_cases.items():
        for scenario in scenarios:
            composition = perturb_composition(
                baseline=baseline,
                component=scenario["component"],
                multiplier=scenario["multiplier"],
            )

            rows.append({
                "base_case": base_case,
                "scenario": scenario["scenario"],
                "component": scenario["component"],
                "perturbation_percent":
                    scenario["perturbation_fraction"] * 100.0,
                "pH": composition["pH"],
                "TDS_mg_L_reported": composition["TDS"],
                "Na_mg_L": composition["Na"],
                "Cl_mg_L": composition["Cl"],
                "SO4_mg_L": composition["SO4"],
                "Mg_mg_L": composition["Mg"],
                "Ca_mg_L": composition["Ca"],
                "K_mg_L": composition["K"],
                "HCO3_mg_L": composition["HCO3"],
                "density_kg_L": composition["density"],
            })

    return pd.DataFrame(rows)


def build_method_notes() -> pd.DataFrame:
    notes = [
        (
            "Sensitivity design",
            "One-at-a-time local sensitivity analysis using -10%, baseline, "
            "and +10% perturbations."
        ),
        (
            "Perturbed inputs",
            "Na, Cl, SO4, Mg, and Ca were perturbed independently."
        ),
        (
            "Fixed inputs",
            "pH, K, HCO3, density override, temperature grid, phase set, "
            "thermodynamic database, and energy assumptions were unchanged."
        ),
        (
            "Number of simulations",
            "22 total simulations: 11 scenarios for C3 and 11 scenarios for C5."
        ),
        (
            "Temperature domain",
            f"{START_TEMP:.0f} to {END_TEMP:.0f} °C at "
            f"{abs(TEMP_STEP):.0f} °C increments."
        ),
        (
            "Thermodynamic database",
            str(DATABASE)
        ),
        (
            "Phase threshold",
            f"{PHASE_MOL_EPS:.1e} mol."
        ),
        (
            "TDS treatment",
            "Reported TDS is retained as descriptive metadata and is not "
            "independently perturbed because the PHREEQC calculation is driven "
            "by the individual ionic concentrations."
        ),
        (
            "Normalized sensitivity coefficient",
            "For non-onset outputs: S = (Y(+10%) - Y(-10%)) / "
            "(2 * 0.10 * Ybaseline)."
        ),
        (
            "Onset sensitivity",
            "Onset temperatures are ranked using the absolute central "
            "half-range in °C rather than a normalized coefficient."
        ),
        (
            "Energy assumptions",
            f"Cp = {CP_BRINE_KJ_KG_K:.2f} kJ/kg/K; latent heat of ice = "
            f"{LATENT_HEAT_ICE_KJ_KG:.2f} kJ/kg; COP = {COP_ASSUMED:.1f}."
        ),
    ]

    return pd.DataFrame(notes, columns=["item", "description"])


if __name__ == "__main__":
    print("\n" + "=" * 78)
    print("PHREEQC-FREZCHEM FREEZE CRYSTALLIZATION SENSITIVITY ANALYSIS")
    print("=" * 78)

    print("\nPHREEQC executable:", Path(PHREEQC_EXE).exists())
    print("frezchem.dat:", Path(DATABASE).exists())
    print("Composition workbook:", COMPOSITION_FILE.exists())
    print("\nTemperature grid:")
    print(TEMPERATURES)

    baseline_cases = load_compositions()
    scenarios = build_scenarios()

    print("\nSensitivity design:")
    print(f"Cases: {list(baseline_cases.keys())}")
    print(f"Components: {SENSITIVITY_COMPONENTS}")
    print(f"Perturbation: ±{SENSITIVITY_FRACTION * 100:.0f}%")
    print(
        "Total simulations:",
        len(baseline_cases) * len(scenarios),
    )

    detailed_results = {}
    run_summary_rows = []
    status_rows = []

    for base_case in ["C3", "C5"]:
        baseline = baseline_cases[base_case]

        for scenario in scenarios:
            composition = perturb_composition(
                baseline=baseline,
                component=scenario["component"],
                multiplier=scenario["multiplier"],
            )

            run_name = (
                f"{base_case}_{safe_label(scenario['scenario'])}"
            )

            print("\n" + "#" * 78)
            print(
                f"SENSITIVITY RUN: {base_case} | "
                f"{scenario['scenario']}"
            )
            print("#" * 78)

            try:
                df, status = simulate_case(
                    case_name=run_name,
                    brine=composition,
                )

                df.insert(0, "base_case", base_case)
                df.insert(1, "scenario", scenario["scenario"])
                df.insert(2, "perturbed_component", scenario["component"])
                df.insert(
                    3,
                    "perturbation_percent",
                    scenario["perturbation_fraction"] * 100.0,
                )

                detailed_results[run_name] = df

                status_record = status.copy()
                status_record["base_case"] = base_case
                status_record["scenario"] = scenario["scenario"]
                status_record["component"] = scenario["component"]
                status_record["perturbation_percent"] = (
                    scenario["perturbation_fraction"] * 100.0
                )
                status_rows.append(status_record)

                run_summary_rows.append(
                    extract_run_summary(
                        base_case=base_case,
                        scenario=scenario,
                        run_name=run_name,
                        composition=composition,
                        df=df,
                        status=status,
                    )
                )

            except Exception as exc:
                failed_status = {
                    "case": run_name,
                    "status": "Fatal error",
                    "last_successful_temperature_c": np.nan,
                    "message": str(exc),
                    "base_case": base_case,
                    "scenario": scenario["scenario"],
                    "component": scenario["component"],
                    "perturbation_percent":
                        scenario["perturbation_fraction"] * 100.0,
                }
                status_rows.append(failed_status)

                run_summary_rows.append(
                    extract_run_summary(
                        base_case=base_case,
                        scenario=scenario,
                        run_name=run_name,
                        composition=composition,
                        df=pd.DataFrame(),
                        status=failed_status,
                    )
                )

                print(f"\n{run_name} failed:")
                print(str(exc))

    run_summary = pd.DataFrame(run_summary_rows)
    status_df = pd.DataFrame(status_rows)

    effect_table = build_effect_table(run_summary)
    rank_table = build_rank_table(effect_table)
    top_influences = build_top_influences(rank_table)
    input_table = build_input_table(
        baseline_cases=baseline_cases,
        scenarios=scenarios,
    )
    method_notes = build_method_notes()

    combined_detailed = (
        pd.concat(
            detailed_results.values(),
            ignore_index=True,
        )
        if detailed_results
        else pd.DataFrame()
    )

    with pd.ExcelWriter(
        OUTPUT_EXCEL,
        engine="openpyxl",
    ) as writer:
        method_notes.to_excel(
            writer,
            sheet_name="Method_Notes",
            index=False,
        )

        input_table.to_excel(
            writer,
            sheet_name="Sensitivity_Inputs",
            index=False,
        )

        run_summary.to_excel(
            writer,
            sheet_name="Run_Summary",
            index=False,
        )

        effect_table.to_excel(
            writer,
            sheet_name="Sensitivity_Effects",
            index=False,
        )

        rank_table.to_excel(
            writer,
            sheet_name="Sensitivity_Ranking",
            index=False,
        )

        top_influences.to_excel(
            writer,
            sheet_name="Top_Influences",
            index=False,
        )

        status_df.to_excel(
            writer,
            sheet_name="Simulation_Status",
            index=False,
        )

        combined_detailed.to_excel(
            writer,
            sheet_name="All_Detailed_Runs",
            index=False,
        )

        for run_name, df in detailed_results.items():
            sheet_name = run_name[:31]
            df.to_excel(
                writer,
                sheet_name=sheet_name,
                index=False,
            )

    run_summary.to_csv(
        WORKDIR / "FC_FREZCHEM_Sensitivity_Run_Summary.csv",
        index=False,
    )

    effect_table.to_csv(
        WORKDIR / "FC_FREZCHEM_Sensitivity_Effects.csv",
        index=False,
    )

    rank_table.to_csv(
        WORKDIR / "FC_FREZCHEM_Sensitivity_Ranking.csv",
        index=False,
    )

    print("\n" + "=" * 78)
    print("SENSITIVITY ANALYSIS FINISHED")
    print("=" * 78)

    print(f"\nOutput workbook:\n{OUTPUT_EXCEL}")

    if not top_influences.empty:
        print("\nMost influential input for each output:")
        print(top_influences.to_string(index=False))

    print("\nSimulation status:")
    display_columns = [
        "base_case",
        "scenario",
        "status",
        "last_successful_temperature_c",
    ]
    available = [
        c for c in display_columns
        if c in status_df.columns
    ]
    print(status_df[available].to_string(index=False))