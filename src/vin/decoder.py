"""
src/vin/decoder.py

Top-level VIN decoding orchestrator.
Chains Layer 0 → Layer 1 → Layer 2 → final epistemologically-rich VinDecodeResult
"""

from typing import Optional
from pathlib import Path

from .vin_validator_layer0 import validate_vin, VinValidationError
from .layer1_iso import decode_iso, IsoLayer1Result
from .layer2_oem_grammar import OemGrammarDecoder, Layer2Result
from .models import (
    VinDecodeResult,
    EpistemologicalValue,
    EpistemologicalStatus,
    SourceType,
    FieldSource,
    DecodeContext
)


def decode_vin(
    vin: str,
    market_hint: Optional[str] = None,          # "ZA", "EU", "US", etc.
    rules_path: Optional[str] = None            # Optional override for rules file
) -> VinDecodeResult:
    """
    Main entry point for VIN decoding.
    Returns a complete, epistemologically annotated result.
    
    Philosophy reminder:
    - Never return naked values
    - Every piece of information carries source, confidence, status, and explanation
    """
    result = VinDecodeResult(
        vin_normalized=vin.strip().upper(),
        is_valid=False,
        wmi=EpistemologicalValue(None, status=EpistemologicalStatus.UNKNOWN, confidence=0.0),
        manufacturer=EpistemologicalValue(None, status=EpistemologicalStatus.UNKNOWN, confidence=0.0),
        country_of_origin=EpistemologicalValue(None, status=EpistemologicalStatus.UNKNOWN, confidence=0.0),
        model_year=EpistemologicalValue(None, status=EpistemologicalStatus.UNKNOWN, confidence=0.0),
        assembly_plant_code=EpistemologicalValue(None, status=EpistemologicalStatus.UNKNOWN, confidence=0.0),
        assembly_plant=EpistemologicalValue(None, status=EpistemologicalStatus.UNKNOWN, confidence=0.0),
        serial_number=EpistemologicalValue(None, status=EpistemologicalStatus.UNKNOWN, confidence=0.0),
        overall_confidence=0.0
    )

    # Layer 0: Sanity & Physics
    is_valid, normalized_vin, error = validate_vin(vin)
    result.is_valid = is_valid
    result.vin_normalized = normalized_vin

    if not is_valid:
        result.epistemology_notes.append(f"Layer 0 failed: {error}")
        result.warnings.append("VIN structurally invalid — all further decoding aborted")
        return result

    # Layer 1: Deterministic ISO Decode
    try:
        iso_result: IsoLayer1Result = decode_iso(normalized_vin)
        
        result.wmi = iso_result.wmi
        result.manufacturer = iso_result.manufacturer
        result.country_of_origin = iso_result.country_of_origin
        result.model_year = iso_result.model_year
        result.assembly_plant_code = iso_result.assembly_plant_code
        result.assembly_plant = iso_result.assembly_plant
        result.serial_number = iso_result.serial_number

    except Exception as e:
        result.epistemology_notes.append(f"Layer 1 failed: {str(e)}")
        result.warnings.append("ISO decoding failed — partial results only")

    # Layer 2: OEM Grammar Decoder (VDS)
    if result.manufacturer.value and result.manufacturer.confidence > 0.9:
        try:
            # Use default or custom rules path
            rules_file = rules_path or "src/vin/rules/dacos_vin_rules_v0.0.4.json"
            decoder = OemGrammarDecoder(rules_path=rules_file)
            
            layer2_result: Layer2Result = decoder.evaluate(
                vin=normalized_vin,
                iso_result=iso_result,
                market_hint=market_hint
            )

            # Merge Layer 2 findings into final result
            for match in layer2_result.matches:
                rule = match.rule
                for key, value in rule.meaning.items():
                    # Create inferred value with strong epistemology
                    ev = EpistemologicalValue(
                        value=value,
                        status=EpistemologicalStatus.INFERRED if match.confidence < 0.95 else EpistemologicalStatus.CONFIRMED,
                        confidence=match.confidence,
                        sources=[
                            FieldSource(
                                source_type=SourceType.LAYER_2_VDS_RULE,
                                source_id=rule.rule_id,
                                confidence=match.confidence,
                                notes=f"Market: {market_hint or 'none'}"
                            )
                        ],
                        explanation=f"Matched VDS rule '{rule.rule_id}' → {key}: {value}"
                    )
                    
                    # Assign to appropriate field (extend as needed)
                    if key == "engine_family":
                        result.engine_family = ev
                    elif key == "displacement_cc":
                        result.displacement_cc = ev
                    elif key == "model":
                        result.model = ev
                    elif key == "series":
                        result.series = ev
                    elif key == "trim_level":
                        result.trim_level = ev
                    elif key == "body_type":
                        result.body_type = ev
                    elif key == "cylinders":
                        result.cylinders = ev
                    elif key == "config":
                        result.engine_config = ev
                    elif key == "fuel":
                        result.fuel_type = ev
                    elif key in ("plant", "assembly"):
                        result.assembly_location = ev
                    # ... add more mappings as rules expand

            if layer2_result.conflicts:
                result.conflicts.extend(layer2_result.conflicts)

            result.epistemology_notes.extend(layer2_result.notes)

        except Exception as e:
            result.epistemology_notes.append(f"Layer 2 failed: {str(e)}")
            result.warnings.append("OEM VDS decoding failed — no inferred fields")

    # Final aggregation
    result.overall_confidence = max(
        [v.confidence for v in vars(result).values() if isinstance(v, EpistemologicalValue)],
        default=0.0
    )

    if market_hint:
        result.epistemology_notes.append(f"Market hint applied: {market_hint}")

    return result

    # ── Layer 3: Market Context Resolver ─────────────────────────────────────
    try:
        from .layer3_market import apply_market_context

        boosted_fields, l3_notes, l3_warnings = apply_market_context(
            vin_normalized=result.vin_normalized,
            layer1_result=iso_result,      # pass the original layer1 result
            layer2_result=layer2_result,
            context=DecodeContext(market_hint=market_hint)
        )

        # Merge boosted/enhanced fields into final result
        for field_name, ev in boosted_fields.items():
            # Simple overwrite for now – later add proper conflict resolution
            if field_name == "engine_family":
                result.engine_family = ev
            elif field_name == "displacement_cc":
                result.displacement_cc = ev
            elif field_name == "model":
                result.model = ev
            elif field_name in ("plant", "assembly", "assembly_location"):
                result.assembly_location = ev
            # Add more field mappings as needed

        result.epistemology_notes.extend(l3_notes)
        result.warnings.extend(l3_warnings)

    except ImportError:
        result.epistemology_notes.append("Layer 3 not available (import failed)")
    except Exception as e:
        result.epistemology_notes.append(f"Layer 3 failed: {str(e)}")
        
        # ── Layer 4: Commercial Knowledge Injectors (stub) ───────────────────────
    try:
        from .layer4_commercial_stub import commercial_enrichment_stub

        enriched_fields, l4_notes, l4_warnings = commercial_enrichment_stub(
            vin_normalized=result.vin_normalized,
            manufacturer=result.manufacturer.value,
            model_year=result.model_year.value if result.model_year.value else None,
            context=DecodeContext(market_hint=market_hint)
        )

        # Merge enriched fields (simple overwrite for now)
        for field_name, ev in enriched_fields.items():
            if field_name == "engine_family":
                result.engine_family = ev
            elif field_name == "displacement_cc":
                result.displacement_cc = ev
            elif field_name == "assembly":
                result.assembly_location = ev
            # Add more mappings as the stub grows

        result.epistemology_notes.extend(l4_notes)
        result.warnings.extend(l4_warnings)

    except ImportError:
        result.epistemology_notes.append("Layer 4 stub not available (import failed)")
    except Exception as e:
        result.epistemology_notes.append(f"Layer 4 stub failed: {str(e)}")
    
        # ── Layer 5: ECU Cross-Validation (highest truth tier) ───────────────────
    try:
        from .layer5_ecu_stub import ecu_cross_validation_stub

        # Collect all fields from Layers 1–4
        current_fields = {
            k: v for k, v in vars(result).items()
            if isinstance(v, EpistemologicalValue) and v.value is not None
        }

        ecu_fields, l5_notes, l5_warnings = ecu_cross_validation_stub(
            vin_normalized=result.vin_normalized,
            lower_layer_fields=current_fields,
            context=DecodeContext(market_hint=market_hint)
        )

        # ECU overrides everything — replace fields directly
        for field_name, ev in ecu_fields.items():
            setattr(result, field_name, ev)

        result.epistemology_notes.extend(l5_notes)
        result.warnings.extend(l5_warnings)

    except ImportError:
        result.epistemology_notes.append("Layer 5 (ECU) stub not available (import failed)")
    except Exception as e:
        result.epistemology_notes.append(f"Layer 5 (ECU) stub failed: {str(e)}")
    
# Quick example usage / smoke test
if __name__ == "__main__":
    test_vin = "WBA5A7C54FG142391"  # Example BMW 330i
    context = DecodeContext(market_hint="ZA")

    result = decode_vin(test_vin, market_hint=context.market_hint)

    print("Final VIN Decode Result:")
    print(f"VIN: {result.vin_normalized}")
    print(f"Valid: {result.is_valid}")
    print(f"Overall Confidence: {result.overall_confidence:.2f}")
    
    for field, ev in vars(result).items():
        if isinstance(ev, EpistemologicalValue) and ev.value is not None:
            print(f"{field:20}: {ev.value} | {ev.status.value} | conf={ev.confidence:.2f}")
            if ev.explanation:
                print(f"   └─ {ev.explanation}")