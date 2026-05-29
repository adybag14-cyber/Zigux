#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import tempfile


SELF_PATH = Path(__file__).resolve()
ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) > 2 else SELF_PATH.parent

MANIFEST_PATH = "zigux/tests/phase10_virtio_mmio_manifest.json"
EXPECTED_FREEZE_FIELDS = {
    "lane_key": "P10-L11",
    "freeze_map": "Documentation/zigux/freeze-map.md",
    "freeze_boundary_status": "aligned",
    "freeze_status_change_claimed": False,
    "risky_transport_posture": "blocked_on_risky_transport",
    "allowed_evidence_kinds": [
        "driver_local_lab_slices",
        "survey_manifests",
        "shared_validation_gates",
    ],
    "forbidden_transport_claims": [
        "queue_setup_reset_paths",
        "queue_reset_execution",
        "irq_parity",
        "dma_paths",
        "probe_remove_lifecycle",
        "freeze_restore_lifecycle",
    ],
    "architecture_council_reopen_required": True,
    "architecture_council_reopen_attached": False,
}

DRIFT_CASES = {
    "lane_key": "P10-L10",
    "freeze_map": "Documentation/zigux/phase10-virtio-mmio-survey.md",
    "freeze_boundary_status": "transport_ready",
    "freeze_status_change_claimed": True,
    "risky_transport_posture": "transport_ready",
    "allowed_evidence_kinds": [
        "driver_local_lab_slices",
        "survey_manifests",
        "transport_claims",
    ],
    "forbidden_transport_claims": [
        "queue_setup_reset_paths",
        "queue_reset_execution",
        "irq_parity",
        "dma_paths",
        "probe_remove_lifecycle",
    ],
    "architecture_council_reopen_required": False,
    "architecture_council_reopen_attached": True,
}


def read_manifest(root: Path) -> dict[str, object]:
    manifest_path = root / MANIFEST_PATH
    try:
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise SystemExit(f"missing:{MANIFEST_PATH}") from None
    if not isinstance(data, dict):
        raise SystemExit(f"problem:{MANIFEST_PATH}:not_a_json_object")
    return data


def validate_manifest(manifest: dict[str, object]) -> list[str]:
    problems: list[str] = []
    for field_name, expected_value in EXPECTED_FREEZE_FIELDS.items():
        actual_value = manifest.get(field_name)
        if actual_value != expected_value:
            problems.append(f"{MANIFEST_PATH}:{field_name}:{actual_value!r}")
    return problems


def write_manifest(root: Path, manifest: dict[str, object]) -> None:
    manifest_path = root / MANIFEST_PATH
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def fixture_manifest() -> dict[str, object]:
    return {
        "phase": "Phase 10",
        "anchor": "drivers/virtio/virtio_mmio.c",
        **EXPECTED_FREEZE_FIELDS,
    }


def run_self_test() -> int:
    baseline = fixture_manifest()
    baseline_problems = validate_manifest(baseline)
    if baseline_problems:
        raise SystemExit(
            "phase10-mmio-freeze-boundary-fields:self-test-baseline-failed:"
            + ",".join(baseline_problems)
        )

    for field_name, drift_value in DRIFT_CASES.items():
        manifest = fixture_manifest()
        manifest[field_name] = drift_value
        problems = validate_manifest(manifest)
        expected_problem = f"{MANIFEST_PATH}:{field_name}:"
        if not any(problem.startswith(expected_problem) for problem in problems):
            raise SystemExit(
                "phase10-mmio-freeze-boundary-fields:drift-not-detected:"
                f"{field_name}"
            )

    with tempfile.TemporaryDirectory(prefix="zigux_phase10_mmio_freeze_boundary_") as tmp_dir:
        root = Path(tmp_dir)
        write_manifest(root, fixture_manifest())
        problems = validate_manifest(read_manifest(root))
        if problems:
            raise SystemExit(
                "phase10-mmio-freeze-boundary-fields:self-test-file-roundtrip-failed:"
                + ",".join(problems)
            )

    print("PHASE10_MMIO_FREEZE_BOUNDARY_FIELDS_SELF_TEST=pass")
    print(f"PHASE10_MMIO_FREEZE_BOUNDARY_FIELDS_SELF_TEST_CASE_COUNT={len(DRIFT_CASES) + 2}")
    return 0


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        description="Validate Phase 10 virtio-MMIO freeze-boundary manifest fields."
    )
    parser.add_argument("--root", default=ROOT, type=Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args(argv)

    if args.self_test:
        return run_self_test()

    problems = validate_manifest(read_manifest(args.root))
    if problems:
        print("PHASE10_MMIO_FREEZE_BOUNDARY_FIELDS=fail")
        for problem in problems:
            print(f"problem:{problem}")
        return 1

    print("PHASE10_MMIO_FREEZE_BOUNDARY_FIELDS=pass")
    print(f"PHASE10_MMIO_FREEZE_BOUNDARY_FIELD_COUNT={len(EXPECTED_FREEZE_FIELDS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
