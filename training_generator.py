import argparse
import json
import math
import os
import random
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

import numpy as np

from ai.can.database import CANDatabase
from ai.core.config import AIConfig
from ai.core.diagnostics_engine import DiagnosticsEngine
from ai.ml.loader import MLLoader
from ai.rules.base import RuleEngine
from ai.rules.engine_rules import create_engine_rules


@dataclass(frozen=True)
class SplitConfig:
    train_size: int
    val_size: int
    test_size: int


@dataclass(frozen=True)
class OutputPaths:
    raw_train_jsonl: str
    raw_val_jsonl: str
    raw_test_jsonl: str
    openai_train_jsonl: str
    openai_val_jsonl: str
    anthropic_train_jsonl: str
    anthropic_val_jsonl: str
    active_learning_json: str


FAULTS: Tuple[str, ...] = (
    "normal_operation",
    "engine_issue",
    "sensor_fault",
    "electrical_fault",
    "vacuum_leak",
    "fuel_starvation",
    "maf_bias",
    "exhaust_leak",
)


def _clamp(x: float, lo: float, hi: float) -> float:
    return float(min(hi, max(lo, x)))


def _rand_uniform(rng: random.Random, lo: float, hi: float) -> float:
    return float(lo + (hi - lo) * rng.random())


def _normal(rng: random.Random, mean: float, std: float) -> float:
    return float(rng.gauss(mean, std))


def _choice_weighted(rng: random.Random, items: Sequence[str], weights: Sequence[float]) -> str:
    total = float(sum(weights))
    if total <= 0:
        return rng.choice(list(items))
    roll = rng.random() * total
    acc = 0.0
    for item, w in zip(items, weights):
        acc += float(w)
        if roll <= acc:
            return item
    return items[-1]


def _entropy_from_probs(probs: Dict[str, float]) -> float:
    e = 0.0
    for p in probs.values():
        if p and p > 0:
            e -= float(p) * math.log(float(p) + 1e-12)
    return float(e)


def _difficulty_for_index(i: int, total: int) -> str:
    if total <= 0:
        return "easy"
    t = i / max(1, total - 1)
    if t < 0.40:
        return "easy"
    if t < 0.70:
        return "medium"
    if t < 0.90:
        return "hard"
    return "expert"


def _base_vehicle_context(rng: random.Random) -> Dict[str, Any]:
    makes = ["Ford", "Toyota", "VW", "BMW", "GM", "Hyundai", "Kia", "Nissan"]
    engines = ["I4", "V6", "V8", "Turbo I4", "Diesel I4"]
    year = int(_clamp(round(_normal(rng, 2014, 6)), 2002, 2026))
    return {
        "make": rng.choice(makes),
        "model": f"Model-{rng.randint(1, 12)}",
        "year": year,
        "engine_type": rng.choice(engines),
    }


def _base_operating_point(rng: random.Random, difficulty: str) -> Dict[str, float]:
    ambient_c = _clamp(_normal(rng, 22, 10), -10, 45)
    throttle = _clamp(_normal(rng, 12, 10), 0, 65)
    idle_rpm = _clamp(_normal(rng, 780, 70), 650, 950)
    rpm = idle_rpm + throttle * _rand_uniform(rng, 35, 65)
    rpm = _clamp(rpm, 650, 4500)

    load = _clamp((throttle / 100.0) * _rand_uniform(rng, 0.6, 1.2) + (rpm - 700) / 6000.0, 0.0, 1.0)
    coolant_c = _clamp(85 + 15 * load + _normal(rng, 0, 2.0) + (ambient_c - 22) * 0.05, 65, 110)

    batt_v = _clamp(_normal(rng, 14.2, 0.25), 12.6, 14.8)
    fuel_pressure = _clamp(_normal(rng, 45, 2.0), 36, 55)

    maf_gps = _clamp(2.5 + 0.015 * rpm + 0.06 * throttle + _normal(rng, 0, 1.0), 2.0, 160.0)
    map_kpa = _clamp(28 + 0.7 * throttle + 0.005 * rpm + _normal(rng, 0, 2.0), 20.0, 105.0)
    lambda_val = _clamp(_normal(rng, 1.0, 0.03), 0.85, 1.15)
    stft = _clamp(_normal(rng, 0.0, 2.0), -15.0, 25.0)
    ltft = _clamp(_normal(rng, 0.0, 1.5), -10.0, 20.0)

    if difficulty in {"hard", "expert"}:
        lambda_val = _clamp(lambda_val + _normal(rng, 0.0, 0.02), 0.85, 1.2)
        stft = _clamp(stft + _normal(rng, 0.0, 1.5), -20.0, 30.0)

    return {
        "ambient_c": float(ambient_c),
        "throttle_position": float(throttle),
        "engine_rpm": float(rpm),
        "coolant_temp": float(coolant_c),
        "battery_voltage": float(batt_v),
        "fuel_pressure": float(fuel_pressure),
        "maf_gps": float(maf_gps),
        "map_kpa": float(map_kpa),
        "lambda": float(lambda_val),
        "stft": float(stft),
        "ltft": float(ltft),
    }


def _apply_faults(
    rng: random.Random,
    base: Dict[str, float],
    faults_present: List[str],
    difficulty: str,
) -> Tuple[Dict[str, float], List[str], Dict[str, Any]]:
    x = dict(base)
    dtcs: List[str] = []
    dq: Dict[str, Any] = {
        "corruption_level": 0.0,
        "dropouts": [],
        "contradictory": False,
        "ood": False,
    }

    def add_dtc(code: str):
        if code not in dtcs:
            dtcs.append(code)

    if "electrical_fault" in faults_present:
        x["battery_voltage"] = _clamp(_normal(rng, 11.4, 0.6), 9.8, 12.6)
        x["engine_rpm"] = _clamp(x["engine_rpm"] + _normal(rng, 0.0, 150.0), 450, 4500)
        add_dtc("P0562")

    if "engine_issue" in faults_present:
        x["coolant_temp"] = _clamp(_normal(rng, 112, 8), 100, 132)
        x["engine_rpm"] = _clamp(x["engine_rpm"] + _normal(rng, 0.0, 120.0), 450, 4500)
        add_dtc(rng.choice(["P0217", "P0118"]))
        if rng.random() < 0.45:
            add_dtc("P0300")

    if "sensor_fault" in faults_present:
        add_dtc(rng.choice(["P0130", "P0133", "P0117"]))
        if rng.random() < 0.35:
            x["coolant_temp"] = _clamp(_normal(rng, 120, 10), 80, 140)
        if rng.random() < 0.30 and "lambda" in x:
            x["lambda"] = _clamp(_normal(rng, 1.0, 0.12), 0.75, 1.35)

    if any(f in faults_present for f in ("vacuum_leak", "fuel_starvation", "maf_bias", "exhaust_leak")):
        lean_severity = 0.0
        if "vacuum_leak" in faults_present:
            lean_severity = max(lean_severity, _rand_uniform(rng, 0.12, 0.28))
            x["engine_rpm"] = _clamp(x["engine_rpm"] + _normal(rng, 0.0, 90.0), 450, 4500)
            x["stft"] = _clamp(x["stft"] + _rand_uniform(rng, 6, 18), -20, 35)
            add_dtc("P0171")
            if rng.random() < 0.25:
                add_dtc("P0507")

        if "fuel_starvation" in faults_present:
            lean_severity = max(lean_severity, _rand_uniform(rng, 0.18, 0.40))
            x["fuel_pressure"] = _clamp(_normal(rng, 28, 4), 12, 34)
            x["stft"] = _clamp(x["stft"] + _rand_uniform(rng, 10, 22), -20, 40)
            add_dtc(rng.choice(["P0171", "P0087"]))
            if rng.random() < 0.35:
                add_dtc("P0300")

        if "maf_bias" in faults_present:
            lean_severity = max(lean_severity, _rand_uniform(rng, 0.10, 0.26))
            x["maf_gps"] = _clamp(x["maf_gps"] * _rand_uniform(rng, 0.65, 0.85), 1.0, 160.0)
            x["stft"] = _clamp(x["stft"] + _rand_uniform(rng, 3, 14), -20, 35)
            if rng.random() < 0.7:
                add_dtc("P0171")
            if rng.random() < 0.45:
                add_dtc("P0101")

        if "exhaust_leak" in faults_present:
            lean_severity = max(lean_severity, _rand_uniform(rng, 0.08, 0.22))
            if rng.random() < 0.65:
                add_dtc("P0171")
            if rng.random() < 0.30:
                add_dtc("P0133")

        x["lambda"] = _clamp(x["lambda"] + lean_severity, 0.85, 1.55)
        x["coolant_temp"] = _clamp(x["coolant_temp"] + 8.0 * lean_severity, 65, 135)

    if difficulty in {"hard", "expert"}:
        if rng.random() < (0.10 if difficulty == "hard" else 0.18):
            dq["contradictory"] = True
            dq["ood"] = True
            x["lambda"] = _clamp(_normal(rng, 0.92, 0.02), 0.80, 1.05)
            x["stft"] = _clamp(_normal(rng, 18, 4), 5, 35)
            if rng.random() < 0.5:
                x["fuel_pressure"] = _clamp(_normal(rng, 24, 3), 10, 34)

    corruption = 0.0
    if difficulty == "medium":
        corruption = 0.06
    elif difficulty == "hard":
        corruption = 0.12
    elif difficulty == "expert":
        corruption = 0.20

    dq["corruption_level"] = float(corruption)

    if corruption > 0:
        for k in ("engine_rpm", "coolant_temp", "battery_voltage", "fuel_pressure", "maf_gps", "map_kpa", "lambda"):
            if k not in x:
                continue
            sigma = 0.0
            if k == "engine_rpm":
                sigma = 80.0 * corruption
            elif k in {"coolant_temp"}:
                sigma = 6.0 * corruption
            elif k in {"battery_voltage"}:
                sigma = 0.6 * corruption
            elif k in {"fuel_pressure"}:
                sigma = 7.0 * corruption
            elif k in {"maf_gps"}:
                sigma = 12.0 * corruption
            elif k in {"map_kpa"}:
                sigma = 4.0 * corruption
            elif k in {"lambda"}:
                sigma = 0.10 * corruption
            x[k] = float(x[k] + _normal(rng, 0.0, sigma))

    if difficulty in {"hard", "expert"}:
        dropout_prob = 0.04 if difficulty == "hard" else 0.08
        candidates = ["maf_gps", "map_kpa", "fuel_pressure", "ltft"]
        for k in candidates:
            if rng.random() < dropout_prob:
                dq["dropouts"].append(k)

    return x, dtcs, dq


def _select_faults(rng: random.Random, difficulty: str) -> List[str]:
    if difficulty == "easy":
        primary = _choice_weighted(
            rng,
            FAULTS,
            [0.35, 0.12, 0.10, 0.10, 0.10, 0.10, 0.08, 0.05],
        )
        return [primary] if primary != "normal_operation" else ["normal_operation"]

    if difficulty == "medium":
        primary = _choice_weighted(
            rng,
            FAULTS,
            [0.22, 0.12, 0.12, 0.10, 0.14, 0.14, 0.10, 0.06],
        )
        if primary == "normal_operation":
            return ["normal_operation"]
        if primary in {"vacuum_leak", "fuel_starvation", "maf_bias", "exhaust_leak"} and rng.random() < 0.25:
            return [primary, rng.choice([f for f in ("vacuum_leak", "fuel_starvation", "maf_bias", "exhaust_leak") if f != primary])]
        return [primary]

    if difficulty == "hard":
        primary = _choice_weighted(
            rng,
            FAULTS,
            [0.12, 0.12, 0.13, 0.12, 0.17, 0.18, 0.12, 0.04],
        )
        if primary == "normal_operation":
            primary = rng.choice([f for f in FAULTS if f != "normal_operation"])
        faults = [primary]
        if rng.random() < 0.45:
            if primary in {"vacuum_leak", "fuel_starvation", "maf_bias", "exhaust_leak"}:
                faults.append(rng.choice([f for f in ("vacuum_leak", "fuel_starvation", "maf_bias", "exhaust_leak") if f != primary]))
            else:
                faults.append(rng.choice(["sensor_fault", "electrical_fault"]))
        return sorted(list(set(faults)))

    primary = rng.choice([f for f in FAULTS if f != "normal_operation"])
    faults = [primary]
    if rng.random() < 0.65:
        faults.append(rng.choice([f for f in FAULTS if f not in faults and f != "normal_operation"]))
    if rng.random() < 0.25:
        faults.append(rng.choice([f for f in FAULTS if f not in faults and f != "normal_operation"]))
    return sorted(list(set(faults)))


def _build_live_data(
    rng: random.Random,
    difficulty: str,
) -> Tuple[Dict[str, Any], List[str], str, Dict[str, Any]]:
    faults_present = _select_faults(rng, difficulty)
    primary_fault = faults_present[0] if faults_present else "normal_operation"

    base = _base_operating_point(rng, difficulty)
    values, dtcs, dq = _apply_faults(rng, base, faults_present, difficulty)

    live_params: Dict[str, Any] = {
        "engine_rpm": {"value": float(values["engine_rpm"]), "unit": "rpm"},
        "coolant_temp": {"value": float(values["coolant_temp"]), "unit": "C"},
        "battery_voltage": {"value": float(values["battery_voltage"]), "unit": "V"},
        "throttle_position": {"value": float(values["throttle_position"]), "unit": "%"},
        "fuel_pressure": {"value": float(values["fuel_pressure"]), "unit": "psi"},
        "maf_gps": {"value": float(values["maf_gps"]), "unit": "g/s"},
        "map_kpa": {"value": float(values["map_kpa"]), "unit": "kPa"},
        "lambda": {"value": float(values["lambda"]), "unit": ""},
        "stft": {"value": float(values["stft"]), "unit": "%"},
        "ltft": {"value": float(values["ltft"]), "unit": "%"},
        "ambient_temp": {"value": float(values["ambient_c"]), "unit": "C"},
    }

    for k in dq.get("dropouts", []):
        if k in live_params:
            live_params[k]["value"] = None

    data = {
        "live_parameters": live_params,
        "dtc_codes": dtcs,
        "vehicle_context": _base_vehicle_context(rng),
    }

    return data, faults_present, primary_fault, dq


def _summarize_observations(live_data: Dict[str, Any]) -> str:
    p = live_data.get("live_parameters", {})
    def g(name: str) -> Optional[float]:
        v = p.get(name, {}).get("value")
        return float(v) if isinstance(v, (int, float)) else None

    rpm = g("engine_rpm")
    ect = g("coolant_temp")
    vbatt = g("battery_voltage")
    fp = g("fuel_pressure")
    lam = g("lambda")
    stft = g("stft")
    dtcs = live_data.get("dtc_codes", [])

    parts: List[str] = []
    if rpm is not None:
        parts.append(f"RPM={rpm:.0f}")
    if ect is not None:
        parts.append(f"ECT={ect:.1f}C")
    if vbatt is not None:
        parts.append(f"VBAT={vbatt:.2f}V")
    if fp is not None:
        parts.append(f"FuelP={fp:.1f}psi")
    if lam is not None:
        parts.append(f"Lambda={lam:.2f}")
    if stft is not None:
        parts.append(f"STFT={stft:.1f}%")
    if dtcs:
        parts.append(f"DTCs={','.join(dtcs)}")
    return "; ".join(parts) if parts else "No usable live parameters."


def _reasoning_chain(
    live_data: Dict[str, Any],
    engine_result: Dict[str, Any],
    dq: Dict[str, Any],
) -> List[Dict[str, Any]]:
    observations = _summarize_observations(live_data)
    belief = engine_result.get("belief_state", {}) or {}
    ranked = sorted(((k, float(v)) for k, v in belief.items()), key=lambda kv: kv[1], reverse=True)
    top = [{"fault": k, "probability": float(v)} for k, v in ranked[:5]]

    p = live_data.get("live_parameters", {})
    lam = p.get("lambda", {}).get("value")
    fp = p.get("fuel_pressure", {}).get("value")

    analysis_bits: List[str] = []
    if isinstance(lam, (int, float)) and lam > 1.1:
        analysis_bits.append("Lambda indicates a lean condition (air>fuel).")
    if isinstance(fp, (int, float)) and fp < 35:
        analysis_bits.append("Fuel pressure is low, consistent with supply restriction/pump issues.")
    if dq.get("contradictory"):
        analysis_bits.append("Some sensor relationships are contradictory; treat confidence as degraded.")
    if not analysis_bits:
        analysis_bits.append("Sensor patterns are within typical operating ranges or weakly informative.")

    top_names = [k for k, _ in ranked[:2]]
    differentiate = []
    if len(top_names) >= 2:
        a, b = top_names[0], top_names[1]
        differentiate.append(f"Differentiate {a} vs {b} using targeted tests and cross-sensor consistency checks.")

    next_test = engine_result.get("next_test")
    recs = engine_result.get("recommendations", [])
    falsify = []
    if next_test:
        falsify.append(f"Run {next_test} and compare outcome against top hypotheses.")
    if dq.get("dropouts"):
        falsify.append(f"Repeat readings for dropped parameters: {', '.join(dq['dropouts'])}.")

    chain = [
        {"stage": "observe", "content": observations},
        {"stage": "analyze", "content": " ".join(analysis_bits)},
        {"stage": "hypothesize", "content": {"ranked_faults": top}},
        {"stage": "differentiate", "content": " ".join(differentiate) if differentiate else "Compare top hypotheses using discriminating evidence."},
        {"stage": "falsify", "content": " ".join(falsify) if falsify else "Propose a concrete test to rule out the leading hypothesis."},
        {"stage": "recommend", "content": {"next_test": next_test, "recommendations": recs}},
    ]
    return chain


def _target_from_engine(
    live_data: Dict[str, Any],
    engine_result: Dict[str, Any],
    faults_present: List[str],
    primary_fault: str,
    dq: Dict[str, Any],
) -> Dict[str, Any]:
    belief = engine_result.get("belief_state", {}) or {}
    ranked = sorted(((k, float(v)) for k, v in belief.items()), key=lambda kv: kv[1], reverse=True)
    ranked_faults = [{"fault": k, "probability": float(v)} for k, v in ranked]

    confidence = float(engine_result.get("confidence", 0.0) or 0.0)
    next_steps = engine_result.get("recommendations", []) or []
    chain = _reasoning_chain(live_data, engine_result, dq)

    return {
        "ranked_faults": ranked_faults,
        "confidence": confidence,
        "recommended_next_steps": next_steps,
        "next_test": engine_result.get("next_test"),
        "data_quality": dq,
        "reasoning_chain": chain,
        "ground_truth": {
            "faults_present": faults_present,
            "primary_fault": primary_fault,
        },
    }


def _user_prompt(live_data: Dict[str, Any]) -> str:
    payload = json.dumps(live_data, ensure_ascii=False)
    schema = {
        "ranked_faults": [{"fault": "string", "probability": 0.0}],
        "confidence": 0.0,
        "recommended_next_steps": ["string"],
        "next_test": "string|null",
        "data_quality": {"corruption_level": 0.0, "dropouts": ["string"], "contradictory": False, "ood": False},
        "reasoning_chain": [{"stage": "observe|analyze|hypothesize|differentiate|falsify|recommend", "content": "string|object"}],
    }
    return (
        "You are Charlemaine, an automotive diagnostic AI. "
        "Given live OBD/CAN-like data, produce a single JSON object matching this schema exactly: "
        f"{json.dumps(schema, ensure_ascii=False)} "
        "Do not include any extra keys or any markdown.\n"
        f"Live data:\n{payload}"
    )


def _openai_record(user: str, assistant: str) -> Dict[str, Any]:
    return {
        "messages": [
            {"role": "system", "content": "You are Charlemaine, a careful automotive diagnostic AI."},
            {"role": "user", "content": user},
            {"role": "assistant", "content": assistant},
        ]
    }


def _anthropic_record(user: str, assistant: str) -> Dict[str, Any]:
    return {
        "messages": [
            {"role": "user", "content": user},
            {"role": "assistant", "content": assistant},
        ]
    }


def _write_jsonl(path: str, rows: Iterable[Dict[str, Any]]) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def _make_paths(output_dir: str) -> OutputPaths:
    out = os.path.abspath(output_dir)
    return OutputPaths(
        raw_train_jsonl=os.path.join(out, "train.jsonl"),
        raw_val_jsonl=os.path.join(out, "val.jsonl"),
        raw_test_jsonl=os.path.join(out, "test.jsonl"),
        openai_train_jsonl=os.path.join(out, "train_openai.jsonl"),
        openai_val_jsonl=os.path.join(out, "val_openai.jsonl"),
        anthropic_train_jsonl=os.path.join(out, "train_anthropic.jsonl"),
        anthropic_val_jsonl=os.path.join(out, "val_anthropic.jsonl"),
        active_learning_json=os.path.join(out, "active_learning_candidates.json"),
    )


def _build_engine() -> Tuple[DiagnosticsEngine, CANDatabase]:
    config = AIConfig()
    ml_loader = MLLoader(config)
    ml_loader.load()

    can_db = CANDatabase(config)
    can_db.connect()

    rule_engine = RuleEngine()
    for rule in create_engine_rules():
        rule_engine.add_rule(rule)

    engine = DiagnosticsEngine(config=config, ml_loader=ml_loader, can_db=can_db, rule_engine=rule_engine)
    return engine, can_db


def _augment_variants(
    rng: random.Random,
    live_data: Dict[str, Any],
    variants: int,
) -> List[Dict[str, Any]]:
    if variants <= 1:
        return [live_data]
    outs = [live_data]
    for _ in range(variants - 1):
        copy_ld = json.loads(json.dumps(live_data))
        lp = copy_ld.get("live_parameters", {})
        for k, sigma in (
            ("engine_rpm", 60.0),
            ("coolant_temp", 1.5),
            ("battery_voltage", 0.15),
            ("fuel_pressure", 1.2),
            ("lambda", 0.02),
            ("maf_gps", 1.5),
            ("map_kpa", 0.8),
            ("stft", 0.8),
            ("ltft", 0.6),
        ):
            v = lp.get(k, {}).get("value")
            if isinstance(v, (int, float)):
                lp[k]["value"] = float(v + _normal(rng, 0.0, sigma))
        outs.append(copy_ld)
    return outs


def _active_learning_candidates(rows: List[Dict[str, Any]], top_k: int) -> List[Dict[str, Any]]:
    scored: List[Tuple[float, Dict[str, Any]]] = []
    for r in rows:
        belief = r.get("target", {}).get("ranked_faults", [])
        probs = {item["fault"]: float(item["probability"]) for item in belief if "fault" in item and "probability" in item}
        ent = _entropy_from_probs(probs) if probs else 0.0
        dq = r.get("target", {}).get("data_quality", {}) or {}
        penalty = 0.0
        if dq.get("ood"):
            penalty += 0.25
        if dq.get("contradictory"):
            penalty += 0.35
        score = float(ent + penalty)
        scored.append((score, r))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [
        {"id": r.get("id"), "score": float(s), "difficulty": r.get("metadata", {}).get("difficulty"), "data_quality": r.get("target", {}).get("data_quality")}
        for s, r in scored[: max(0, int(top_k))]
    ]


def _generate_rows(
    engine: DiagnosticsEngine,
    rng: random.Random,
    count: int,
    augmentation: int,
    start_index: int,
) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for i in range(count):
        difficulty = _difficulty_for_index(start_index + i, start_index + count)
        live_data, faults_present, primary_fault, dq = _build_live_data(rng, difficulty)
        variants = _augment_variants(rng, live_data, augmentation)
        for v_idx, v_live in enumerate(variants):
            engine_result = engine.diagnose(v_live)
            target = _target_from_engine(v_live, engine_result, faults_present, primary_fault, dq)
            user = _user_prompt(v_live)
            assistant = json.dumps({k: target[k] for k in ("ranked_faults", "confidence", "recommended_next_steps", "next_test", "data_quality", "reasoning_chain")}, ensure_ascii=False)
            row_id = f"{start_index + i:06d}_{v_idx}"
            rows.append(
                {
                    "id": row_id,
                    "created_at": datetime.now().isoformat(),
                    "user": user,
                    "assistant": assistant,
                    "live_data": v_live,
                    "target": target,
                    "metadata": {
                        "difficulty": difficulty,
                        "faults_present": faults_present,
                        "primary_fault": primary_fault,
                    },
                }
            )
    return rows


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--train-size", type=int, default=2000)
    parser.add_argument("--val-size", type=int, default=200)
    parser.add_argument("--test-size", type=int, default=300)
    parser.add_argument("--augmentation", type=int, default=2)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output-dir", type=str, default=os.path.join("training_data"))
    parser.add_argument("--formats", type=str, default="openai,anthropic,raw")
    parser.add_argument("--active-learning-top-k", type=int, default=250)
    args = parser.parse_args()

    split = SplitConfig(train_size=int(args.train_size), val_size=int(args.val_size), test_size=int(args.test_size))
    paths = _make_paths(str(args.output_dir))

    rng = random.Random(int(args.seed))
    np.random.seed(int(args.seed))

    engine, can_db = _build_engine()
    try:
        train_rows = _generate_rows(engine, rng, split.train_size, int(args.augmentation), 0)
        val_rows = _generate_rows(engine, rng, split.val_size, max(1, int(args.augmentation) - 1), split.train_size)
        test_rows = _generate_rows(engine, rng, split.test_size, 1, split.train_size + split.val_size)

        formats = {s.strip().lower() for s in str(args.formats).split(",") if s.strip()}

        if "raw" in formats:
            _write_jsonl(paths.raw_train_jsonl, train_rows)
            _write_jsonl(paths.raw_val_jsonl, val_rows)
            _write_jsonl(paths.raw_test_jsonl, test_rows)

        if "openai" in formats:
            _write_jsonl(paths.openai_train_jsonl, (_openai_record(r["user"], r["assistant"]) for r in train_rows))
            _write_jsonl(paths.openai_val_jsonl, (_openai_record(r["user"], r["assistant"]) for r in val_rows))

        if "anthropic" in formats:
            _write_jsonl(paths.anthropic_train_jsonl, (_anthropic_record(r["user"], r["assistant"]) for r in train_rows))
            _write_jsonl(paths.anthropic_val_jsonl, (_anthropic_record(r["user"], r["assistant"]) for r in val_rows))

        candidates = _active_learning_candidates(train_rows, int(args.active_learning_top_k))
        os.makedirs(os.path.dirname(paths.active_learning_json), exist_ok=True)
        with open(paths.active_learning_json, "w", encoding="utf-8") as f:
            json.dump({"candidates": candidates}, f, ensure_ascii=False, indent=2)

        print("Generated training data")
        print(f"Output directory: {os.path.abspath(str(args.output_dir))}")
        print(f"Train rows: {len(train_rows)}")
        print(f"Val rows:   {len(val_rows)}")
        print(f"Test rows:  {len(test_rows)}")
        return 0
    finally:
        can_db.disconnect()


if __name__ == "__main__":
    raise SystemExit(main())

