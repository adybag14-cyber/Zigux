#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path
from typing import Any


HANDOFF_NOTE_PATH = Path("Documentation/zigux/phase15-handoff-next-steps-survey.md")
MANIFEST_PATH = Path("zigux/tests/phase15_handoff_next_steps_manifest.json")

EXPECTED_LANE_KEY = "P15-L12"
EXPECTED_PHASE = "Phase 15"
FUTURE_TARGETS_KEY = "next_bounded_future_target_markers"
REQUIRED_SECTION_MARKER = "## Next bounded future targets"
FORBIDDEN_TARGET_MARKERS = (
    "direct Zig deep-core bridge",
    "port-ready",
    "port readiness",
    "approved freeze-map status change",
)
REQUIRED_TARGET_FAMILIES = (
    "review-checklist.md",
    "zigux/tests/README.md",
    "Documentation/zigux/README.md",
    "BOOTSTRAP_COMMIT_LEDGER.md",
    "phase15-freeze-map-governance.md",
    "kernel/workqueue.c",
)


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _read_manifest(path: Path) -> dict[str, Any]:
    return json.loads(_read_text(path))


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _as_string_list(value: Any, field: str, failures: list[str]) -> list[str]:
    if not isinstance(value, list):
        failures.append(f"manifest_field_not_list:{field}")
        return []
    entries: list[str] = []
    for index, entry in enumerate(value):
        if not isinstance(entry, str):
            failures.append(f"manifest_field_non_string:{field}:{index}")
            continue
        entries.append(entry)
    return entries


def collect_failures(root: Path) -> list[str]:
    failures: list[str] = []
    note_path = root / HANDOFF_NOTE_PATH
    manifest_path = root / MANIFEST_PATH

    if not note_path.exists():
        failures.append(f"missing_handoff_note:{HANDOFF_NOTE_PATH}")
    if not manifest_path.exists():
        failures.append(f"missing_handoff_manifest:{MANIFEST_PATH}")
    if failures:
        return failures

    note = _read_text(note_path)
    manifest = _read_manifest(manifest_path)

    if manifest.get("lane_key") != EXPECTED_LANE_KEY:
        failures.append(f"lane_key:{manifest.get('lane_key')!r}")
    if manifest.get("phase") != EXPECTED_PHASE:
        failures.append(f"phase:{manifest.get('phase')!r}")
    if manifest.get("handoff_note") != HANDOFF_NOTE_PATH.as_posix():
        failures.append(f"handoff_note:{manifest.get('handoff_note')!r}")

    if REQUIRED_SECTION_MARKER not in note:
        failures.append("missing_next_bounded_future_targets_section")

    future_targets = _as_string_list(manifest.get(FUTURE_TARGETS_KEY), FUTURE_TARGETS_KEY, failures)
    if not future_targets:
        failures.append("empty_next_bounded_future_target_markers")

    for target in future_targets:
        if target not in note:
            failures.append(f"missing_future_target_marker:{target}")
        for forbidden in FORBIDDEN_TARGET_MARKERS:
            if forbidden in target:
                failures.append(f"forbidden_future_target_marker:{forbidden}:{target}")

    for family in REQUIRED_TARGET_FAMILIES:
        if not any(family in target for target in future_targets):
            failures.append(f"missing_future_target_family:{family}")

    return failures


def _sample_manifest() -> str:
    payload = {
        "lane_key": EXPECTED_LANE_KEY,
        "phase": EXPECTED_PHASE,
        "surveyed_commit": "current-master-readback-2026-05-27",
        "handoff_note": HANDOFF_NOTE_PATH.as_posix(),
        FUTURE_TARGETS_KEY: [
            "reread `Documentation/zigux/review-checklist.md` together with `Documentation/zigux/phase15-shared-summary-gap.md`, `Documentation/zigux/phase15-architecture-council-review-process.md`, and the current directly materialized governance packet whenever the shared Architecture Council prompts drift",
            "reread `zigux/tests/README.md` together with `scripts/zigux/check-phase15-tests-readme-alignment.py`, `Documentation/zigux/phase15-shared-summary-gap.md`, and the current directly materialized governance packet whenever the tests-root reminder drifts, rather than treating a dedicated Phase 15 review section as still-unlanded by default",
            "keep the landed docs-root reminder surface `Documentation/zigux/README.md` aligned with `scripts/zigux/check-phase15-docs-readme-alignment.py`, `Documentation/zigux/phase15-shared-summary-gap.md`, and the directly materialized governance packet instead of carrying docs-root Phase 15 coverage as an active shared-summary gap",
            "if `zigux-alpha/README.md` or `zigux-alpha/BOOTSTRAP_COMMIT_LEDGER.md` changes its scope note, reread this handoff note before using the ledger to explain any later-lane Phase 15 next step",
            "keep the landed `Documentation/zigux/phase15-freeze-map-governance.md`, `Documentation/zigux/phase15-architecture-council-review-process.md`, `Documentation/zigux/phase15-architecture-council-decision-record-template.md`, `Documentation/zigux/phase15-architecture-council-decision-index.md`, `Documentation/zigux/phase15-governance-lane-sequencing.md`, `Documentation/zigux/phase15-readiness-gate-survey.md`, `Documentation/zigux/phase15-indefinite-c-policy.md`, `zigux/tests/phase15_freeze_map_governance.zig`, `zigux/tests/phase15_parity_scorecard.json`, `zigux/tests/phase15_parity_scorecard.zig`, `zigux/tests/phase15_architecture_council_review_process_manifest.json`, `zigux/tests/phase15_architecture_council_review_process.zig`, `zigux/tests/phase15_architecture_council_review_process_build.zig`, `zigux/tests/phase15_governance_lane_sequencing_manifest.json`, `zigux/tests/phase15_governance_lane_sequencing.zig`, `zigux/tests/phase15_indefinite_c_policy.json`, `zigux/tests/phase15_indefinite_c_policy.zig`, `zigux/tests/phase15_handoff_next_steps.zig`, `zigux/tests/phase15_build.zig`, `zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig`, `zigux/tests/phase15_readiness_gate_manifest.json`, `zigux/tests/phase15_handoff_next_steps_manifest.json`, `scripts/zigux/check-phase15-docs-readme-alignment.py`, `scripts/zigux/check-phase15-scripts-readme-alignment.py`, `scripts/zigux/check-phase15-review-checklist-study-only-alignment.py`, `scripts/zigux/check-phase15-readiness-gate-packet.py`, `scripts/zigux/check-phase15-architecture-council-packet.py`, and `scripts/zigux/validate-phase15.py` companions aligned with the shared-summary gap note before any freeze-map status change discussion",
            "if future work touches `kernel/workqueue.c` or `kernel/trace/ring_buffer.c`, keep it study-only unless a smaller-than-boundary seam is explicitly recorded in the governance packet",
        ],
    }
    return json.dumps(payload, indent=2) + "\n"


def _sample_note(manifest: dict[str, Any]) -> str:
    targets = "\n".join(
        f"{index + 1}. {target}"
        for index, target in enumerate(manifest[FUTURE_TARGETS_KEY])
    )
    return f"""# Phase 15 Handoff Next Steps Survey

## Status

- `PHASE15_LANE_KEY=P15-L12`

## Next bounded future targets

{targets}
"""


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="phase15_handoff_future_targets_") as tmp_dir:
        root = Path(tmp_dir)
        manifest = json.loads(_sample_manifest())
        _write(root / MANIFEST_PATH, _sample_manifest())
        _write(root / HANDOFF_NOTE_PATH, _sample_note(manifest))
        failures = collect_failures(root)
        if failures:
            raise AssertionError(f"baseline fixture should pass: {failures}")

        missing_target_root = root / "missing_target"
        manifest = json.loads(_sample_manifest())
        missing_target = manifest[FUTURE_TARGETS_KEY][1]
        _write(missing_target_root / MANIFEST_PATH, json.dumps(manifest, indent=2) + "\n")
        _write(
            missing_target_root / HANDOFF_NOTE_PATH,
            _sample_note(manifest).replace(f"2. {missing_target}\n", "", 1),
        )
        failures = collect_failures(missing_target_root)
        if failures != [f"missing_future_target_marker:{missing_target}"]:
            raise AssertionError(f"unexpected missing-target failure: {failures}")

        missing_family_root = root / "missing_family"
        manifest = json.loads(_sample_manifest())
        manifest[FUTURE_TARGETS_KEY] = [
            target for target in manifest[FUTURE_TARGETS_KEY] if "kernel/workqueue.c" not in target
        ]
        _write(missing_family_root / MANIFEST_PATH, json.dumps(manifest, indent=2) + "\n")
        _write(missing_family_root / HANDOFF_NOTE_PATH, _sample_note(manifest))
        failures = collect_failures(missing_family_root)
        if failures != ["missing_future_target_family:kernel/workqueue.c"]:
            raise AssertionError(f"unexpected missing-family failure: {failures}")

        wrong_type_root = root / "wrong_type"
        manifest = json.loads(_sample_manifest())
        manifest[FUTURE_TARGETS_KEY] = "reread review-checklist.md"
        _write(wrong_type_root / MANIFEST_PATH, json.dumps(manifest, indent=2) + "\n")
        _write(wrong_type_root / HANDOFF_NOTE_PATH, "## Next bounded future targets\n")
        failures = collect_failures(wrong_type_root)
        expected = [
            "manifest_field_not_list:next_bounded_future_target_markers",
            "empty_next_bounded_future_target_markers",
            "missing_future_target_family:review-checklist.md",
            "missing_future_target_family:zigux/tests/README.md",
            "missing_future_target_family:Documentation/zigux/README.md",
            "missing_future_target_family:BOOTSTRAP_COMMIT_LEDGER.md",
            "missing_future_target_family:phase15-freeze-map-governance.md",
            "missing_future_target_family:kernel/workqueue.c",
        ]
        if failures != expected:
            raise AssertionError(f"unexpected wrong-type failure: {failures}")

        forbidden_root = root / "forbidden"
        manifest = json.loads(_sample_manifest())
        manifest[FUTURE_TARGETS_KEY][0] += " after direct Zig deep-core bridge approval"
        _write(forbidden_root / MANIFEST_PATH, json.dumps(manifest, indent=2) + "\n")
        _write(forbidden_root / HANDOFF_NOTE_PATH, _sample_note(manifest))
        failures = collect_failures(forbidden_root)
        if len(failures) != 1 or not failures[0].startswith(
            "forbidden_future_target_marker:direct Zig deep-core bridge:"
        ):
            raise AssertionError(f"unexpected forbidden-marker failure: {failures}")

    print("PHASE15_HANDOFF_FUTURE_TARGETS_SELF_TEST=pass")
    print("PHASE15_HANDOFF_FUTURE_TARGETS_SELF_TEST_CASES=5")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify that the Phase 15 handoff note preserves its bounded future-target inventory."
    )
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="repository root")
    parser.add_argument("--self-test", action="store_true", help="run synthetic checker fixtures")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = collect_failures(args.root)
    if failures:
        print("PHASE15_HANDOFF_FUTURE_TARGETS=fail")
        for failure in failures:
            print(f"ERROR: {failure}")
        return 1

    print("PHASE15_HANDOFF_FUTURE_TARGETS=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
