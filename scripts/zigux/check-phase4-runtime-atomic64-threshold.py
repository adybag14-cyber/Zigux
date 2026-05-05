#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
REQUIRED_FILES = [
    "zigux/tests/phase4_runtime_atomic64_diff_manifest.json",
    "zigux/tests/phase4_runtime_atomic64_diff_survey.zig",
    "Documentation/zigux/phase4-validation-matrix.md",
    "Documentation/zigux/phase4-gate-evidence.md",
]
EXPECTED_MANIFEST_VALUES = {
    "lane_key": "P4-L04",
    "phase": "Phase 4",
    "roadmap_target_path": "zigux/tests/atomic64_diff.zig",
    "live_gate_path": "zigux/tests/runtime_atomic64_diff.zig",
    "runtime_replay_path": "zigux/tests/runtime_atomic64_diff.zig",
    "threshold_posture": "threshold_pending_until_runtime_atomic64_scope_widens",
}
EXPECTED_MANIFEST_BOOLEANS = {
    "roadmap_atomic64_diff_present": True,
    "roadmap_atomic64_wrapper_targets_runtime_diff": True,
    "phase4_build_present": True,
    "phase4_build_uses_atomic64_wrapper": True,
    "phase4_validator_atomic64_diff_present": True,
    "phase4_validator_runtime_atomic64_diff_present": True,
    "phase9_build_present": True,
    "phase4_validation_matrix_atomic64_diff_note_present": True,
    "phase4_validation_matrix_runtime_atomic64_note_present": True,
}
REQUIRED_GAP_SUMMARY_MARKERS = [
    "zigux/tests/atomic64_diff.zig",
    "zigux/tests/runtime_atomic64_diff.zig",
    "zigux/tests/phase4_build.zig",
    "single bounded replay body",
    "Phase 9",
]
REQUIRED_READY_NEXT_MARKERS = [
    "zigux/tests/atomic64_diff.zig",
    "zigux/tests/runtime_atomic64_diff.zig",
    "zigux/tests/phase4_build.zig",
    "scripts/zigux/validate-phase4.py",
    "Documentation/zigux/phase4-validation-matrix.md",
]
REQUIRED_MATRIX_MARKERS = [
    "zigux/tests/atomic64_diff.zig",
    "zigux/tests/runtime_atomic64_diff.zig",
    "threshold_pending_until_runtime_atomic64_scope_widens",
]
REQUIRED_GATE_EVIDENCE_MARKERS = [
    "PHASE4_RUNTIME_ATOMIC64_MANIFEST_BLOB_SHA=",
    "PHASE4_RUNTIME_ATOMIC64_SURVEY_BLOB_SHA=",
    "`make -C zigux phase4-runtime-atomic64-diff`",
]


def _missing_files(root: Path) -> list[str]:
    missing = []
    for rel in REQUIRED_FILES:
        if not (root / rel).exists():
            missing.append(rel)
    return missing


def validate_root(root: Path) -> list[str]:
    failures: list[str] = []

    missing = _missing_files(root)
    if missing:
        return [f"missing_file:{item}" for item in missing]

    manifest = json.loads(
        (root / "zigux/tests/phase4_runtime_atomic64_diff_manifest.json").read_text(
            encoding="utf-8"
        )
    )
    for key, expected in EXPECTED_MANIFEST_VALUES.items():
        if manifest.get(key) != expected:
            failures.append(f"manifest:{key}:{manifest.get(key)!r}")
    for key, expected in EXPECTED_MANIFEST_BOOLEANS.items():
        if manifest.get(key) is not expected:
            failures.append(f"manifest:{key}:{manifest.get(key)!r}")

    for marker in REQUIRED_GAP_SUMMARY_MARKERS:
        if marker not in manifest.get("roadmap_gap_summary", ""):
            failures.append(f"manifest:roadmap_gap_summary:{marker}")
    for marker in REQUIRED_READY_NEXT_MARKERS:
        if marker not in manifest.get("ready_next", ""):
            failures.append(f"manifest:ready_next:{marker}")

    matrix = (root / "Documentation/zigux/phase4-validation-matrix.md").read_text(
        encoding="utf-8"
    )
    for marker in REQUIRED_MATRIX_MARKERS:
        if marker not in matrix:
            failures.append(f"matrix:{marker}")

    gate_evidence = (root / "Documentation/zigux/phase4-gate-evidence.md").read_text(
        encoding="utf-8"
    )
    for marker in REQUIRED_GATE_EVIDENCE_MARKERS:
        if marker not in gate_evidence:
            failures.append(f"gate_evidence:{marker}")

    return failures


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="phase4_runtime_atomic64_threshold_") as tmp:
        root = Path(tmp)
        manifest = {
            **EXPECTED_MANIFEST_VALUES,
            **EXPECTED_MANIFEST_BOOLEANS,
            "roadmap_gap_summary": (
                "the roadmap target zigux/tests/atomic64_diff.zig is now present as the "
                "Phase 4 wrapper and zigux/tests/phase4_build.zig runs through it, while "
                "zigux/tests/runtime_atomic64_diff.zig remains the single bounded replay "
                "body that the Phase 9 runtime packet still imports directly"
            ),
            "ready_next": (
                "keep zigux/tests/atomic64_diff.zig, zigux/tests/runtime_atomic64_diff.zig, "
                "zigux/tests/phase4_build.zig, scripts/zigux/validate-phase4.py, "
                "Documentation/zigux/phase4-validation-matrix.md aligned"
            ),
        }
        _write(
            root / "zigux/tests/phase4_runtime_atomic64_diff_manifest.json",
            json.dumps(manifest, indent=2) + "\n",
        )
        _write(root / "zigux/tests/phase4_runtime_atomic64_diff_survey.zig", "// survey\n")
        _write(
            root / "Documentation/zigux/phase4-validation-matrix.md",
            "\n".join(REQUIRED_MATRIX_MARKERS) + "\n",
        )
        _write(
            root / "Documentation/zigux/phase4-gate-evidence.md",
            "\n".join(REQUIRED_GATE_EVIDENCE_MARKERS) + "\n",
        )

        assert validate_root(root) == []

        bad_manifest = dict(manifest)
        bad_manifest["threshold_posture"] = "wrong"
        _write(
            root / "zigux/tests/phase4_runtime_atomic64_diff_manifest.json",
            json.dumps(bad_manifest, indent=2) + "\n",
        )
        assert validate_root(root) == ["manifest:threshold_posture:'wrong'"]

        _write(
            root / "zigux/tests/phase4_runtime_atomic64_diff_manifest.json",
            json.dumps(manifest, indent=2) + "\n",
        )
        _write(root / "Documentation/zigux/phase4-validation-matrix.md", "zigux/tests/atomic64_diff.zig\n")
        assert "matrix:zigux/tests/runtime_atomic64_diff.zig" in validate_root(root)

        _write(
            root / "Documentation/zigux/phase4-validation-matrix.md",
            "\n".join(REQUIRED_MATRIX_MARKERS) + "\n",
        )
        _write(root / "Documentation/zigux/phase4-gate-evidence.md", "PHASE4_RUNTIME_ATOMIC64_MANIFEST_BLOB_SHA=\n")
        assert "gate_evidence:PHASE4_RUNTIME_ATOMIC64_SURVEY_BLOB_SHA=" in validate_root(root)

    print("PHASE4_RUNTIME_ATOMIC64_THRESHOLD_SELF_TEST=pass")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check the bounded Phase 4 runtime atomic64 threshold packet."
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run isolated self-tests without reading the live repo.",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = validate_root(ROOT)
    if failures:
        print("PHASE4_RUNTIME_ATOMIC64_THRESHOLD_PACKET=fail")
        print("PHASE4_RUNTIME_ATOMIC64_THRESHOLD_FAILURES_START")
        for item in failures:
            print(item)
        print("PHASE4_RUNTIME_ATOMIC64_THRESHOLD_FAILURES_END")
        return 1

    print("PHASE4_RUNTIME_ATOMIC64_THRESHOLD_PACKET=pass")
    print(f"PHASE4_RUNTIME_ATOMIC64_THRESHOLD_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(
        "PHASE4_RUNTIME_ATOMIC64_THRESHOLD_REQUIRED_CHECK_COUNT="
        f"{len(EXPECTED_MANIFEST_VALUES) + len(EXPECTED_MANIFEST_BOOLEANS) + len(REQUIRED_GAP_SUMMARY_MARKERS) + len(REQUIRED_READY_NEXT_MARKERS) + len(REQUIRED_MATRIX_MARKERS) + len(REQUIRED_GATE_EVIDENCE_MARKERS)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
