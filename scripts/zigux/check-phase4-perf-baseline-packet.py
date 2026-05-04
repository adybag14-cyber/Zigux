#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import tempfile
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve()
ROOT = SCRIPT_PATH.parents[2] if len(SCRIPT_PATH.parents) > 2 else SCRIPT_PATH.parent

REQUIRED_FILES = [
    "Documentation/zigux/README.md",
    "Documentation/zigux/phase4-gate-evidence.md",
    "Documentation/zigux/phase4-validation-matrix.md",
    "zigux/tests/README.md",
    "zigux/tests/phase4_perf_baseline_manifest.json",
    "zigux/tests/phase4_perf_baseline_survey.zig",
]

DOCS_README_MARKERS = [
    "make -C zigux phase4-perf-baseline-survey",
    "phase4-perf-baseline-survey-tests",
    "perf_thresholds_unapproved_until_bounded_phase4_benchmarks_land",
]

TESTS_README_MARKERS = [
    "zigux/tests/phase4_perf_baseline_survey.zig",
    "zigux/tests/phase4_perf_baseline_manifest.json",
    "make -C zigux phase4-perf-baseline-survey",
    "perf_thresholds_unapproved_until_bounded_phase4_benchmarks_land",
]

MATRIX_MARKERS = [
    "| `zigux/tests/phase4_perf_baseline_survey.zig` |",
    "phase4-perf-baseline-survey-tests",
    "make -C zigux phase4-perf-baseline-survey",
    "perf_thresholds_unapproved_until_bounded_phase4_benchmarks_land",
    "benchmark command and acceptable limit are still unapproved for both landed gates",
    "land one bounded benchmark command and one acceptable limit per gate before Phase 4 claims perf coverage",
]

SURVEY_MARKERS = [
    "phase4_perf_baseline_manifest.json",
    "phase4-perf-baseline-survey-tests",
    "make -C zigux phase4-perf-baseline-survey",
    "threshold_pending_until_runtime_atomic64_scope_widens",
    "threshold_pending_until_bitmap_gate_grows_beyond_bounded_correctness_checks",
    "unapproved_until_runtime_atomic64_scope_widens",
    "unapproved_until_bitmap_gate_grows_beyond_bounded_correctness_checks",
    "pending threshold-plan record per shipped rollback gate",
]

GATE_EVIDENCE_TEXT_MARKERS = [
    "PHASE4_GATE_EVIDENCE_CHECK=pass",
    "PHASE4_PERF_BASELINE_MANIFEST_BLOB_SHA=",
    "PHASE4_PERF_BASELINE_SURVEY_BLOB_SHA=",
    "phase4_perf_baseline_survey.zig",
    "pending threshold-plan record per shipped rollback gate",
    "make -C zigux phase4-runtime-atomic64-diff",
    "make -C zigux phase4-bitmap-diff",
    "unapproved_until_runtime_atomic64_scope_widens",
    "unapproved_until_bitmap_gate_grows_beyond_bounded_correctness_checks",
]


def git_blob_sha1(payload: bytes) -> str:
    header = f"blob {len(payload)}\0".encode("utf-8")
    return hashlib.sha1(header + payload).hexdigest()


def read_text(root: Path, relative_path: str) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def read_json(root: Path, relative_path: str) -> object:
    return json.loads(read_text(root, relative_path))


def missing_text(text: str, prefix: str, markers: list[str]) -> list[str]:
    return [f"{prefix}:{marker}" for marker in markers if marker not in text]


def validate_manifest(manifest: object) -> list[str]:
    missing: list[str] = []
    if not isinstance(manifest, dict):
        return ["manifest:not_object"]
    if manifest.get("lane_key") != "P4-L20":
        missing.append("manifest:lane_key")
    if manifest.get("phase") != "Phase 4":
        missing.append("manifest:phase")
    if manifest.get("owner") != "Validation and Perf Team":
        missing.append("manifest:owner")
    if manifest.get("rollback_owner") != "Validation and Perf Team":
        missing.append("manifest:rollback_owner")

    surveyed_gates = manifest.get("surveyed_gates")
    if not isinstance(surveyed_gates, list) or len(surveyed_gates) != 2:
        missing.append("manifest:surveyed_gates")

    pending = manifest.get("pending_threshold_plans")
    if not isinstance(pending, list) or len(pending) != 2:
        missing.append("manifest:pending_threshold_plans")
        return missing

    expected = {
        "zigux/tests/atomic64_diff.zig": {
            "owner": "ABI and Runtime Team",
            "rollback_owner": "ABI and Runtime Team",
            "posture": "threshold_pending_until_runtime_atomic64_scope_widens",
            "status": "pending_scope_widening",
            "current_replay": "make -C zigux phase4-runtime-atomic64-diff",
            "placeholder": "unapproved_until_runtime_atomic64_scope_widens",
        },
        "zigux/tests/bitmap_diff.zig": {
            "owner": "Shared Subsystems Pod",
            "rollback_owner": "Shared Subsystems Pod",
            "posture": "threshold_pending_until_bitmap_gate_grows_beyond_bounded_correctness_checks",
            "status": "pending_bounded_benchmark",
            "current_replay": "make -C zigux phase4-bitmap-diff",
            "placeholder": "unapproved_until_bitmap_gate_grows_beyond_bounded_correctness_checks",
        },
    }

    for item in pending:
        if not isinstance(item, dict):
            missing.append("manifest:pending_item_not_object")
            continue
        surface = item.get("surface")
        if surface not in expected:
            missing.append(f"manifest:unexpected_surface:{surface}")
            continue
        info = expected[surface]
        if item.get("gate_owner") != info["owner"]:
            missing.append(f"manifest:gate_owner:{surface}")
        if item.get("gate_rollback_owner") != info["rollback_owner"]:
            missing.append(f"manifest:gate_rollback_owner:{surface}")
        if item.get("threshold_posture") != info["posture"]:
            missing.append(f"manifest:threshold_posture:{surface}")
        if item.get("status") != info["status"]:
            missing.append(f"manifest:status:{surface}")
        if item.get("current_correctness_replay") != info["current_replay"]:
            missing.append(f"manifest:current_correctness_replay:{surface}")
        if item.get("benchmark_command") != info["placeholder"]:
            missing.append(f"manifest:benchmark_command:{surface}")
        if item.get("acceptable_limit") != info["placeholder"]:
            missing.append(f"manifest:acceptable_limit:{surface}")

    gaps = manifest.get("gaps")
    if not isinstance(gaps, list) or len(gaps) != 4:
        missing.append("manifest:gaps")
    else:
        expected_gaps = {
            "phase4-perf-baseline-survey-manifest": ("starter_landed", "survey_manifest"),
            "phase4-perf-baseline-survey-gate": ("starter_landed", "validation"),
            "phase4-perf-baseline-atomic64-command": ("ready_next", "perf_command"),
            "phase4-perf-baseline-bitmap-command": ("ready_next", "perf_command"),
        }
        for gap in gaps:
            if not isinstance(gap, dict):
                missing.append("manifest:gap_not_object")
                continue
            gap_id = gap.get("id")
            if gap_id not in expected_gaps:
                missing.append(f"manifest:unexpected_gap:{gap_id}")
                continue
            status, kind = expected_gaps[gap_id]
            if gap.get("status") != status:
                missing.append(f"manifest:gap_status:{gap_id}")
            if gap.get("kind") != kind:
                missing.append(f"manifest:gap_kind:{gap_id}")

    return missing


def validate_root(root: Path) -> list[str]:
    missing = [f"file:{path}" for path in REQUIRED_FILES if not (root / path).exists()]
    if missing:
        return missing

    docs_readme = read_text(root, "Documentation/zigux/README.md")
    tests_readme = read_text(root, "zigux/tests/README.md")
    matrix = read_text(root, "Documentation/zigux/phase4-validation-matrix.md")
    survey = read_text(root, "zigux/tests/phase4_perf_baseline_survey.zig")
    gate_evidence = read_text(root, "Documentation/zigux/phase4-gate-evidence.md")
    manifest = read_json(root, "zigux/tests/phase4_perf_baseline_manifest.json")

    missing.extend(missing_text(docs_readme, "docs_readme", DOCS_README_MARKERS))
    missing.extend(missing_text(tests_readme, "tests_readme", TESTS_README_MARKERS))
    missing.extend(missing_text(matrix, "matrix", MATRIX_MARKERS))
    missing.extend(missing_text(survey, "survey", SURVEY_MARKERS))
    missing.extend(missing_text(gate_evidence, "gate_evidence", GATE_EVIDENCE_TEXT_MARKERS))
    missing.extend(validate_manifest(manifest))

    manifest_blob = git_blob_sha1((root / "zigux/tests/phase4_perf_baseline_manifest.json").read_bytes())
    survey_blob = git_blob_sha1((root / "zigux/tests/phase4_perf_baseline_survey.zig").read_bytes())
    if f"PHASE4_PERF_BASELINE_MANIFEST_BLOB_SHA={manifest_blob}" not in gate_evidence:
        missing.append(f"gate_evidence:manifest_blob:{manifest_blob}")
    if f"PHASE4_PERF_BASELINE_SURVEY_BLOB_SHA={survey_blob}" not in gate_evidence:
        missing.append(f"gate_evidence:survey_blob:{survey_blob}")

    return missing


def write_fixture_tree(root: Path) -> None:
    manifest = {
        "lane_key": "P4-L20",
        "phase": "Phase 4",
        "owner": "Validation and Perf Team",
        "rollback_owner": "Validation and Perf Team",
        "surveyed_commit": "3ba64cd4e41a4de1c8fd8dbaecb23702ad9701a3",
        "surveyed_gates": [
            {
                "surface": "zigux/tests/atomic64_diff.zig",
                "gate_owner": "ABI and Runtime Team",
                "gate_rollback_owner": "ABI and Runtime Team",
                "threshold_posture": "threshold_pending_until_runtime_atomic64_scope_widens",
            },
            {
                "surface": "zigux/tests/bitmap_diff.zig",
                "gate_owner": "Shared Subsystems Pod",
                "gate_rollback_owner": "Shared Subsystems Pod",
                "threshold_posture": "threshold_pending_until_bitmap_gate_grows_beyond_bounded_correctness_checks",
            },
        ],
        "pending_threshold_plans": [
            {
                "surface": "zigux/tests/atomic64_diff.zig",
                "gate_owner": "ABI and Runtime Team",
                "gate_rollback_owner": "ABI and Runtime Team",
                "threshold_posture": "threshold_pending_until_runtime_atomic64_scope_widens",
                "current_correctness_replay": "make -C zigux phase4-runtime-atomic64-diff",
                "benchmark_command": "unapproved_until_runtime_atomic64_scope_widens",
                "acceptable_limit": "unapproved_until_runtime_atomic64_scope_widens",
                "status": "pending_scope_widening",
                "why_not_approved_yet": "correctness-only coverage",
            },
            {
                "surface": "zigux/tests/bitmap_diff.zig",
                "gate_owner": "Shared Subsystems Pod",
                "gate_rollback_owner": "Shared Subsystems Pod",
                "threshold_posture": "threshold_pending_until_bitmap_gate_grows_beyond_bounded_correctness_checks",
                "current_correctness_replay": "make -C zigux phase4-bitmap-diff",
                "benchmark_command": "unapproved_until_bitmap_gate_grows_beyond_bounded_correctness_checks",
                "acceptable_limit": "unapproved_until_bitmap_gate_grows_beyond_bounded_correctness_checks",
                "status": "pending_bounded_benchmark",
                "why_not_approved_yet": "acceptable limit",
            },
        ],
        "gaps": [
            {
                "id": "phase4-perf-baseline-survey-manifest",
                "status": "starter_landed",
                "kind": "survey_manifest",
                "zigux_destination": "zigux/tests/phase4_perf_baseline_manifest.json",
                "why_now": "manifest-backed survey packet",
            },
            {
                "id": "phase4-perf-baseline-survey-gate",
                "status": "starter_landed",
                "kind": "validation",
                "zigux_destination": "zigux/tests/phase4_perf_baseline_survey.zig",
                "why_now": "correctness-only posture",
            },
            {
                "id": "phase4-perf-baseline-atomic64-command",
                "status": "ready_next",
                "kind": "perf_command",
                "zigux_destination": "zigux/tests/atomic64_diff.zig",
                "why_now": "benchmark command plus one acceptable limit",
            },
            {
                "id": "phase4-perf-baseline-bitmap-command",
                "status": "ready_next",
                "kind": "perf_command",
                "zigux_destination": "zigux/tests/bitmap_diff.zig",
                "why_now": "benchmark command plus one acceptable limit",
            },
        ],
    }

    survey = "\n".join(SURVEY_MARKERS) + "\n"
    docs_readme = "\n".join(DOCS_README_MARKERS) + "\n"
    tests_readme = "\n".join(TESTS_README_MARKERS) + "\n"
    matrix = "\n".join(MATRIX_MARKERS) + "\n"

    files = {
        "Documentation/zigux/README.md": docs_readme,
        "Documentation/zigux/phase4-validation-matrix.md": matrix,
        "zigux/tests/README.md": tests_readme,
        "zigux/tests/phase4_perf_baseline_manifest.json": json.dumps(manifest, indent=2) + "\n",
        "zigux/tests/phase4_perf_baseline_survey.zig": survey,
    }
    for relative_path, content in files.items():
        target = root / relative_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")

    manifest_blob = git_blob_sha1((root / "zigux/tests/phase4_perf_baseline_manifest.json").read_bytes())
    survey_blob = git_blob_sha1((root / "zigux/tests/phase4_perf_baseline_survey.zig").read_bytes())
    gate_evidence = "\n".join(
        [
            "PHASE4_GATE_EVIDENCE_CHECK=pass",
            f"PHASE4_PERF_BASELINE_MANIFEST_BLOB_SHA={manifest_blob}",
            f"PHASE4_PERF_BASELINE_SURVEY_BLOB_SHA={survey_blob}",
            "phase4_perf_baseline_survey.zig",
            "pending threshold-plan record per shipped rollback gate",
            "make -C zigux phase4-runtime-atomic64-diff",
            "make -C zigux phase4-bitmap-diff",
            "unapproved_until_runtime_atomic64_scope_widens",
            "unapproved_until_bitmap_gate_grows_beyond_bounded_correctness_checks",
        ]
    )
    target = root / "Documentation/zigux/phase4-gate-evidence.md"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(gate_evidence + "\n", encoding="utf-8")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase4_perf_baseline_") as tmp_dir:
        root = Path(tmp_dir)
        write_fixture_tree(root)
        assert not validate_root(root), validate_root(root)

        docs_readme = root / "Documentation/zigux/README.md"
        docs_readme.write_text(
            docs_readme.read_text(encoding="utf-8").replace(
                "make -C zigux phase4-perf-baseline-survey\n", "", 1
            ),
            encoding="utf-8",
        )
        missing = validate_root(root)
        assert "docs_readme:make -C zigux phase4-perf-baseline-survey" in missing, missing

        write_fixture_tree(root)
        manifest_path = root / "zigux/tests/phase4_perf_baseline_manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["pending_threshold_plans"][0]["benchmark_command"] = "wrong"
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        missing = validate_root(root)
        assert "manifest:benchmark_command:zigux/tests/atomic64_diff.zig" in missing, missing

        write_fixture_tree(root)
        gate_evidence = root / "Documentation/zigux/phase4-gate-evidence.md"
        gate_evidence.write_text(
            gate_evidence.read_text(encoding="utf-8").replace(
                "PHASE4_PERF_BASELINE_SURVEY_BLOB_SHA=", "PHASE4_PERF_BASELINE_SURVEY_MISSING=", 1
            ),
            encoding="utf-8",
        )
        missing = validate_root(root)
        assert any(item.startswith("gate_evidence:survey_blob:") for item in missing), missing

    print("PHASE4_PERF_BASELINE_PACKET_SELF_TEST=pass")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the Phase 4 perf-baseline packet."
    )
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    missing = validate_root(ROOT)
    if missing:
        print("PHASE4_PERF_BASELINE_PACKET=fail")
        print("MISSING_PHASE4_PERF_BASELINE_PACKET_START")
        for item in missing:
            print(item)
        print("MISSING_PHASE4_PERF_BASELINE_PACKET_END")
        return 1

    print("PHASE4_PERF_BASELINE_PACKET=pass")
    print(f"PHASE4_PERF_BASELINE_PACKET_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
