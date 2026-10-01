from __future__ import annotations

import subprocess
import shutil
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd

WORKDIR = Path(__file__).resolve().parent
PHREEQC_EXE = Path(
    shutil.which("phreeqc")
    or r"C:\Program Files\USGS\phreeqc-3.8.6-17100-x64\bin\ClrRelease\phreeqc.exe"
)
DATABASE = WORKDIR / "frezchem.dat"
if not DATABASE.exists():
    DATABASE = PHREEQC_EXE.parent.parent / "database" / "frezchem.dat"


OUTPUT_EXCEL = WORKDIR / "frezpy_experiment_validation_results.xlsx"

START_TEMP = 25.0
END_TEMP = -25.0
TEMP_STEP = -1.0

PHASE_MOL_EPS = 1.0e-12

DENSITY_OVERRIDE = {"LEACHATE": 1.03211}

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
    return {
        "LEACHATE": {
            "pH": 8.60,
            "TDS": 50050.0,
            "Na": 12500.0,
            "K": 100.0,
            "Mg": 174.0,
            "Ca": 61.0,
            "Cl": 8000.0,
            "SO4": 16000.0,
            "HCO3": 296.777653,
            "density": 1.03211,
        }
    }


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

def read_validation_targets() -> Tuple[pd.DataFrame, pd.DataFrame]:
    oli = pd.DataFrame(
        {
            "Temperature_C": [25.0, 0.0, -4.0, -21.0],
            "Stage": ["Feed", "Cooling", "Freeze 1", "Freeze 2"],
            "Water_kg_h": [982.1, 957.8, 101.3, 6.0],
            "Ice_reported": [np.nan, np.nan, 856.5, 95.31],
            "pH_OLI": [np.nan, np.nan, 7.50, 6.71],
            "Mirabilite_kg_h": [0.0, 43.42, 71.99, 1.02],
            "Solution_TDS_kg_h": [50.01, 48.81, 12.93, 2.18],
            "Solution_Cl_kg_h": [7.0, 7.0, 7.0, 1.22],
        }
    )

    initial_water = oli.loc[0, "Water_kg_h"]
    oli["OLI_ice_recovery_pct"] = (
        (initial_water - oli["Water_kg_h"])
        / initial_water
        * 100.0
    )

    experimental = pd.DataFrame(
        [{
            "initial_leachate_volume_L": 273.0,
            "recovered_ice_kg": 118.7,
            "run_duration_h": 5.5,
            "final_ice_TDS_g_L": 4.0,
            "experimental_apparent_ice_recovery_pct":
                118.7 / 273.0 * 100.0,
        }]
    )

    return oli, experimental


def build_validation_comparison(
    model_df: pd.DataFrame,
    oli_df: pd.DataFrame,
    experimental_df: pd.DataFrame,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    model = model_df.copy()

    oli_compare = oli_df[
        [
            "Temperature_C",
            "Stage",
            "Water_kg_h",
            "Ice_reported",
            "Mirabilite_kg_h",
            "OLI_ice_recovery_pct",
        ]
    ].copy()

    oli_compare = oli_compare.rename(
        columns={"Temperature_C": "temperature_c"}
    )

    merged = pd.merge(
        model,
        oli_compare,
        on="temperature_c",
        how="inner",
    )

    initial_oli_water = float(
        oli_df.loc[
            oli_df["Temperature_C"].idxmax(),
            "Water_kg_h",
        ]
    )

    merged["FrezPy_mirabilite_step_kg_h_equivalent"] = (
        merged["mirabilite_step_mol"]
        * MW_MIRABILITE
        / 1000.0
        / merged["water_before_equilibrium_kg"]
        * initial_oli_water
    )

    merged["FrezPy_mirabilite_cumulative_kg_h_equivalent"] = (
        merged["mirabilite_cumulative_mol"]
        * MW_MIRABILITE
        / 1000.0
        / model.iloc[0]["water_before_equilibrium_kg"]
        * initial_oli_water
    )

    merged["ice_error_pp"] = (
        merged["ice_recovery_pct"]
        - merged["OLI_ice_recovery_pct"]
    )

    ice_valid = (
        np.isfinite(merged["ice_recovery_pct"])
        & np.isfinite(merged["OLI_ice_recovery_pct"])
    )

    metrics = []

    if ice_valid.any():
        err = merged.loc[
            ice_valid, "ice_error_pp"
        ].to_numpy(dtype=float)

        metrics.append(
            {
                "comparison": "FrezPy vs OLI",
                "variable": "Ice recovery",
                "N_matched": len(err),
                "MAE_pp": np.mean(np.abs(err)),
                "RMSE_pp": np.sqrt(np.mean(err ** 2)),
                "MBE_pp": np.mean(err),
                "Max_abs_error_pp": np.max(np.abs(err)),
            }
        )

    exp_recovery = float(
        experimental_df.iloc[0][
            "experimental_apparent_ice_recovery_pct"
        ]
    )

    final_model = model.iloc[-1]

    metrics.append(
        {
            "comparison": "FrezPy vs experiment",
            "variable": "Ice recovery",
            "N_matched": 1,
            "MAE_pp": abs(
                float(final_model["ice_recovery_pct"])
                - exp_recovery
            ),
            "RMSE_pp": abs(
                float(final_model["ice_recovery_pct"])
                - exp_recovery
            ),
            "MBE_pp": (
                float(final_model["ice_recovery_pct"])
                - exp_recovery
            ),
            "Max_abs_error_pp": abs(
                float(final_model["ice_recovery_pct"])
                - exp_recovery
            ),
        }
    )

    return merged, pd.DataFrame(metrics)


if __name__ == "__main__":
    print("\n" + "=" * 72)
    print("FREZPY EXPERIMENTAL VALIDATION")
    print("=" * 72)

    print("\nPHREEQC executable:", Path(PHREEQC_EXE).exists())
    print("frezchem.dat:", Path(DATABASE).exists())
    print("\nTemperature grid:")
    print(TEMPERATURES)

    cases = load_compositions()
    results = {}
    statuses = []

    for case, composition in cases.items():
        try:
            df, status = simulate_case(
                case_name=case,
                brine=composition,
            )
            results[case] = df
            statuses.append(status)
        except Exception as exc:
            statuses.append(
                {
                    "case": case,
                    "status": "Fatal error",
                    "last_successful_temperature_c": np.nan,
                    "message": str(exc),
                }
            )
            print(f"\n{case} failed:")
            print(str(exc))

    status_df = pd.DataFrame(statuses)
    onset_df = build_phase_onset_table(results)
    summary_df = build_summary(results)

    oli_df, experimental_df = read_validation_targets()

    validation_df = pd.DataFrame()
    metrics_df = pd.DataFrame()

    if "LEACHATE" in results and not results["LEACHATE"].empty:
        validation_df, metrics_df = build_validation_comparison(
            model_df=results["LEACHATE"],
            oli_df=oli_df,
            experimental_df=experimental_df,
        )

    with pd.ExcelWriter(
        OUTPUT_EXCEL,
        engine="openpyxl",
    ) as writer:
        if "LEACHATE" in results:
            results["LEACHATE"].to_excel(
                writer,
                sheet_name="FrezPy_Detailed",
                index=False,
            )

        onset_df.to_excel(
            writer,
            sheet_name="Phase_Onset",
            index=False,
        )

        summary_df.to_excel(
            writer,
            sheet_name="Recovery_Summary",
            index=False,
        )

        oli_df.to_excel(
            writer,
            sheet_name="OLI_Leachate",
            index=False,
        )

        experimental_df.to_excel(
            writer,
            sheet_name="Experimental_Ice",
            index=False,
        )

        if not validation_df.empty:
            validation_df.to_excel(
                writer,
                sheet_name="Validation_Comparison",
                index=False,
            )

        if not metrics_df.empty:
            metrics_df.to_excel(
                writer,
                sheet_name="Validation_Metrics",
                index=False,
            )

        status_df.to_excel(
            writer,
            sheet_name="Simulation_Status",
            index=False,
        )

    if "LEACHATE" in results:
        results["LEACHATE"].to_csv(
            WORKDIR / "LEACHATE_FREZCHEM_results.csv",
            index=False,
        )

    print("\n" + "=" * 72)
    print("VALIDATION RUN FINISHED")
    print("=" * 72)
    print(f"\nOutput workbook:\n{OUTPUT_EXCEL}")

    print("\nSimulation status:")
    print(status_df.to_string(index=False))

    print("\nPhase-onset intervals:")
    print(onset_df.to_string(index=False))

    print("\nRecovery summary:")
    print(summary_df.to_string(index=False))

    print("\nExperimental ice target:")
    print(experimental_df.to_string(index=False))

    if not metrics_df.empty:
        print("\nValidation metrics:")
        print(metrics_df.to_string(index=False))

