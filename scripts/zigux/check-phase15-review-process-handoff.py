#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import tempfile


SELF_PATH = Path(__file__).resolve()
ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) > 2 else SELF_PATH.parent

NOTE_PATH = "Documentation/zigux/phase15-architecture-council-review-process.md"
MANIFEST_PATH = "zigux/tests/phase15_architecture_council_review_process_manifest.json"

NOTE_MARKERS = [
    "## Roadmap Handoff Evidence",
    "- current repo handoff:",
    "## Current enforcement evidence",
]

HANDOFF_INVENTORY_MARKERS = [
    "Documentation/zigux/README.md",
    "Documentation/zigux/freeze-map.md",
    "Documentation/zigux/review-checklist.md",
    "Documentation/zigux/phase15-freeze-map-governance.md",
    "Documentation/zigux/phase15-parity-scorecard.md",
    "Documentation/zigux/phase15-indefinite-c-policy.md",
    "Documentation/zigux/phase15-readiness-gate-survey.md",
    "Documentation/zigux/phase15-handoff-next-steps-survey.md",
    "scripts/zigux/README.md",
    "scripts/zigux/check-phase15-review-process-handoff.py",
    "scripts/zigux/validate-phase15.py",
    "zigux/tests/README.md",
    "zigux/tests/phase15_docs_root_reviewability.zig",
    "zigux/tests/phase15_build.zig",
    "make -C zigux phase15",
]

MANIFEST_ROUTE_MARKERS = [
    "readiness packet",
    "docs-root reviewability guard",
    "scripts-root validator path",
    "tests-root guidance path",
    "dedicated handoff-checker route",
    "current parked maintenance-mode Phase 15 packet",
]

NOTE_LANE_ROUTE_MARKERS = [
    "readiness packet",
    "docs-root reviewability guard",
    "scripts-root validator path",
    "tests-root guidance path",
    "dedicated handoff-checker route",
]

NOTE_HANDOFF_ROUTE_MARKERS = [
    "Documentation/zigux/phase15-readiness-gate-survey.md",
    "zigux/tests/phase15_docs_root_reviewability.zig",
    "scripts/zigux/README.md",
    "scripts/zigux/check-phase15-review-process-handoff.py",
    "scripts/zigux/validate-phase15.py",
    "zigux/tests/README.md",
    "readiness packet",
    "docs-root reviewability guard",
    "scripts-root validator path",
    "dedicated handoff-checker route",
    "tests-root guidance path",
]

CURRENT_ENFORCEMENT_MARKERS = [
    "last reviewed remote `master` head for this packet",
    "Documentation/zigux/review-checklist.md",
    "Documentation/zigux/phase15-readiness-gate-survey.md",
    "scripts/zigux/check-phase15-review-process-handoff.py",
    "python3 scripts/zigux/validate-phase15.py",
    "make -C zigux phase15-validate",
    "Documentation/zigux/README.md",
    "zigux/tests/phase15_docs_root_reviewability.zig",
    "zigux/tests/README.md",
    "phase15-review-process-current-enforcement-evidence-gate",
]


def read_text(root: Path, rel_path: str) -> str:
    return (root / rel_path).read_text(encoding="utf-8")


def load_manifest(root: Path) -> dict:
    return json.loads(read_text(root, MANIFEST_PATH))


def expect_exact_once(text: str, marker: str, label: str, failures: list[str]) -> None:
    count = text.count(marker)
    if count != 1:
        failures.append(f"{label}:{marker}:count={count}")


def note_section(note: str, start_marker: str, end_marker: str | None) -> str | None:
    if start_marker not in note:
        return None
    section = note.split(start_marker, 1)[1]
    if end_marker is not None:
        if end_marker not in section:
            return None
        section = section.split(end_marker, 1)[0]
    return section


def validate(root: Path) -> list[str]:
    failures: list[str] = []

    note_path = root / NOTE_PATH
    manifest_path = root / MANIFEST_PATH
    if not note_path.exists():
        failures.append(f"missing_file:{NOTE_PATH}")
        return failures
    if not manifest_path.exists():
        failures.append(f"missing_file:{MANIFEST_PATH}")
        return failures

    note = read_text(root, NOTE_PATH)
    manifest = load_manifest(root)

    for marker in NOTE_MARKERS:
        if marker not in note:
            failures.append(f"note:{marker}")

    handoff = manifest.get("handoff_evidence", {})
    current_repo_handoff = handoff.get("current_repo_handoff", "")
    current_bounded_lane = handoff.get("current_bounded_lane", "")

    if not isinstance(current_repo_handoff, str):
        failures.append("manifest:handoff_evidence.current_repo_handoff:not_string")
        return failures
    if not isinstance(current_bounded_lane, str):
        failures.append("manifest:handoff_evidence.current_bounded_lane:not_string")
        return failures

    note_current_repo_handoff = note_section(
        note,
        "- current repo handoff:",
        "- current bounded lane:",
    )
    if note_current_repo_handoff is None:
        failures.append("note_inventory_section:missing")
    else:
        for marker in HANDOFF_INVENTORY_MARKERS:
            expect_exact_once(note_current_repo_handoff, marker, "note_inventory", failures)
            expect_exact_once(current_repo_handoff, marker, "manifest_inventory", failures)

    for marker in MANIFEST_ROUTE_MARKERS:
        if marker not in current_bounded_lane:
            failures.append(f"manifest_lane:{marker}")

    note_current_bounded_lane = note_section(
        note,
        "- current bounded lane:",
        "- maintenance-mode next step:",
    )
    if note_current_bounded_lane is None:
        failures.append("note_lane_section:missing")
    else:
        for marker in NOTE_LANE_ROUTE_MARKERS:
            if marker not in note_current_bounded_lane:
                failures.append(f"note_lane:{marker}")

    note_maintenance_handoff = note_section(
        note,
        "## Maintenance-Mode Handoff",
        "## Current enforcement evidence",
    )
    if note_maintenance_handoff is None:
        failures.append("note_handoff_section:missing")
    else:
        for marker in NOTE_HANDOFF_ROUTE_MARKERS:
            if marker not in note_maintenance_handoff:
                failures.append(f"note_handoff:{marker}")

    note_current_enforcement = note_section(
        note,
        "## Current enforcement evidence",
        "## Recorded Gaps",
    )
    if note_current_enforcement is None:
        failures.append("note_current_enforcement_section:missing")
    else:
        for marker in CURRENT_ENFORCEMENT_MARKERS:
            if marker not in note_current_enforcement:
                failures.append(f"note_current_enforcement:{marker}")

    if "current repo handoff" not in note.lower():
        failures.append("note:current_repo_handoff_line")

    return failures


def write_fixture_tree(root: Path) -> None:
    (root / "Documentation/zigux").mkdir(parents=True, exist_ok=True)
    (root / "zigux/tests").mkdir(parents=True, exist_ok=True)

    note = """# Phase 15 Architecture Council Review Process Survey

## Roadmap Handoff Evidence

- current repo handoff: the original documentation-root and freeze-map landing is now carried forward by `Documentation/zigux/README.md`, `Documentation/zigux/freeze-map.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase15-freeze-map-governance.md`, this review-process note, `Documentation/zigux/phase15-parity-scorecard.md`, `Documentation/zigux/phase15-indefinite-c-policy.md`, `Documentation/zigux/phase15-readiness-gate-survey.md`, `Documentation/zigux/phase15-handoff-next-steps-survey.md`, `scripts/zigux/README.md`, `scripts/zigux/check-phase15-review-process-handoff.py`, `scripts/zigux/validate-phase15.py`, `zigux/tests/README.md`, `zigux/tests/phase15_docs_root_reviewability.zig`, `zigux/tests/phase15_build.zig`, and `make -C zigux phase15`
- current bounded lane: `P15-L08` keeps the review-process packet narrowed so the readiness packet, the docs-root reviewability guard, the scripts-root validator path, the dedicated handoff-checker route, and the tests-root guidance path stay explicit together.
- maintenance-mode next step: wait for one named reopen trigger.

## Maintenance-Mode Handoff

- keep `Documentation/zigux/phase15-readiness-gate-survey.md`, `zigux/tests/phase15_docs_root_reviewability.zig`, `scripts/zigux/README.md`, `scripts/zigux/check-phase15-review-process-handoff.py`, `scripts/zigux/validate-phase15.py`, and `zigux/tests/README.md` aligned with the same parked governance bundle so the readiness packet, the docs-root reviewability guard, the scripts-root validator path, dedicated handoff-checker route, and tests-root guidance path do not drift away from the Architecture Council handoff while this lane remains parked.

## Current enforcement evidence

- last reviewed remote `master` head for this packet: `02264a3240cd30ce45c9a932047a0204b7ab5029`
- the review hook was present at that reviewed head in `Documentation/zigux/review-checklist.md`
- the dedicated handoff checker was present there in `scripts/zigux/check-phase15-review-process-handoff.py`
- the shared validator-first governance gate was present there through `python3 scripts/zigux/validate-phase15.py` and `make -C zigux phase15-validate`
- the docs-root, readiness, docs-root reviewability, and tests-root review surfaces were present there in `Documentation/zigux/README.md`, `Documentation/zigux/phase15-readiness-gate-survey.md`, `zigux/tests/phase15_docs_root_reviewability.zig`, and `zigux/tests/README.md`
- landed `phase15-review-process-current-enforcement-evidence-gate`

## Recorded Gaps
"""
    (root / NOTE_PATH).write_text(note, encoding="utf-8")

    manifest = {
        "handoff_evidence": {
            "current_repo_handoff": "The original documentation-root and freeze-map landing is now carried forward by Documentation/zigux/README.md, Documentation/zigux/freeze-map.md, Documentation/zigux/review-checklist.md, Documentation/zigux/phase15-freeze-map-governance.md, the review-process note, Documentation/zigux/phase15-parity-scorecard.md, Documentation/zigux/phase15-indefinite-c-policy.md, Documentation/zigux/phase15-readiness-gate-survey.md, Documentation/zigux/phase15-handoff-next-steps-survey.md, scripts/zigux/README.md, scripts/zigux/check-phase15-review-process-handoff.py, scripts/zigux/validate-phase15.py, zigux/tests/README.md, zigux/tests/phase15_docs_root_reviewability.zig, zigux/tests/phase15_build.zig, and make -C zigux phase15.",
            "current_bounded_lane": "P15-L08 keeps the review-process packet narrowed to one same-packet governance refresh so the Architecture Council handoff stays aligned with the current parked maintenance-mode Phase 15 packet, its dedicated readiness packet, its docs-root reviewability guard, its scripts-root validator path, its dedicated handoff-checker route, and its tests-root guidance path.",
        }
    }
    (root / MANIFEST_PATH).write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def expect_failure(root: Path, expected: str, label: str) -> None:
    failures = validate(root)
    if expected not in failures:
        actual = ",".join(failures) if failures else "none"
        raise SystemExit(f"{label}:expected={expected}:actual={actual}")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase15_handoff_") as tmp_dir:
        tmp_root = Path(tmp_dir)
        write_fixture_tree(tmp_root)

        baseline = validate(tmp_root)
        if baseline:
            raise SystemExit("baseline_failed:" + ",".join(baseline))

        note_path = tmp_root / NOTE_PATH
        original_note = note_path.read_text(encoding="utf-8")
        note_path.write_text(
            original_note.replace("Documentation/zigux/review-checklist.md", "", 1),
            encoding="utf-8",
        )
        expect_failure(
            tmp_root,
            "note_inventory:Documentation/zigux/review-checklist.md:count=0",
            "missing_note_review_checklist",
        )
        note_path.write_text(original_note, encoding="utf-8")

        note_path.write_text(
            original_note.replace(
                "Documentation/zigux/phase15-parity-scorecard.md",
                "Documentation/zigux/phase15-parity-scorecard.md and Documentation/zigux/phase15-parity-scorecard.md",
                1,
            ),
            encoding="utf-8",
        )
        expect_failure(
            tmp_root,
            "note_inventory:Documentation/zigux/phase15-parity-scorecard.md:count=2",
            "duplicate_note_scorecard",
        )
        note_path.write_text(original_note, encoding="utf-8")

        manifest_path = tmp_root / MANIFEST_PATH
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["handoff_evidence"]["current_repo_handoff"] = manifest["handoff_evidence"][
            "current_repo_handoff"
        ].replace("Documentation/zigux/phase15-freeze-map-governance.md, ", "", 1)
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        expect_failure(
            tmp_root,
            "manifest_inventory:Documentation/zigux/phase15-freeze-map-governance.md:count=0",
            "missing_manifest_freeze_map_governance",
        )

        write_fixture_tree(tmp_root)
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["handoff_evidence"]["current_bounded_lane"] = "P15-L08 stays parked."
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        expect_failure(
            tmp_root,
            "manifest_lane:readiness packet",
            "missing_manifest_lane_route_marker",
        )

        write_fixture_tree(tmp_root)
        note_path.write_text(
            original_note.replace("dedicated handoff-checker route", "dedicated route", 1),
            encoding="utf-8",
        )
        expect_failure(
            tmp_root,
            "note_lane:dedicated handoff-checker route",
            "missing_note_lane_route_marker",
        )

        write_fixture_tree(tmp_root)
        note_path.write_text(
            original_note.replace(
                "keep `Documentation/zigux/phase15-readiness-gate-survey.md`, `zigux/tests/phase15_docs_root_reviewability.zig`, `scripts/zigux/README.md`, `scripts/zigux/check-phase15-review-process-handoff.py`, `scripts/zigux/validate-phase15.py`, and `zigux/tests/README.md` aligned",
                "keep `Documentation/zigux/phase15-readiness-gate-survey.md`, `zigux/tests/phase15_docs_root_reviewability.zig`, `scripts/zigux/README.md`, `scripts/zigux/validate-phase15.py`, and `zigux/tests/README.md` aligned",
                1,
            ),
            encoding="utf-8",
        )
        expect_failure(
            tmp_root,
            "note_handoff:scripts/zigux/check-phase15-review-process-handoff.py",
            "missing_note_handoff_checker_route",
        )

        write_fixture_tree(tmp_root)
        note_path.write_text(
            original_note.replace("## Current enforcement evidence", "## Enforcement evidence", 1),
            encoding="utf-8",
        )
        expect_failure(
            tmp_root,
            "note:## Current enforcement evidence",
            "missing_current_enforcement_heading",
        )

        write_fixture_tree(tmp_root)
        note_path.write_text(
            original_note.replace("make -C zigux phase15-validate", "make -C zigux phase15-check", 1),
            encoding="utf-8",
        )
        expect_failure(
            tmp_root,
            "note_current_enforcement:make -C zigux phase15-validate",
            "missing_current_enforcement_validate_route",
        )

    print("PHASE15_REVIEW_PROCESS_HANDOFF_SELF_TEST=pass")
    print("PHASE15_REVIEW_PROCESS_HANDOFF_SELF_TEST_CASE_COUNT=9")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the Phase 15 Architecture Council review-process handoff inventory."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=ROOT,
        help="Repository root to validate. Defaults to the current directory.",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run the fixture-backed self-test.",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = validate(args.root)
    if failures:
        print("PHASE15_REVIEW_PROCESS_HANDOFF=fail")
        print("PHASE15_REVIEW_PROCESS_HANDOFF_FAILURES_START")
        for failure in failures:
            print(failure)
        print("PHASE15_REVIEW_PROCESS_HANDOFF_FAILURES_END")
        return 1

    print("PHASE15_REVIEW_PROCESS_HANDOFF=pass")
    print(
        "PHASE15_REVIEW_PROCESS_HANDOFF_MARKER_COUNT="
        + str(
            len(NOTE_MARKERS)
            + (len(HANDOFF_INVENTORY_MARKERS) * 2)
            + len(MANIFEST_ROUTE_MARKERS)
            + len(NOTE_LANE_ROUTE_MARKERS)
            + len(NOTE_HANDOFF_ROUTE_MARKERS)
            + len(CURRENT_ENFORCEMENT_MARKERS)
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
