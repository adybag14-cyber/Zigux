#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import tempfile


SELF_PATH = Path(__file__).resolve()
ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) > 2 else SELF_PATH.parent

DOCS_README_PATH = "Documentation/zigux/README.md"
REVIEW_CHECKLIST_PATH = "Documentation/zigux/review-checklist.md"
NOTE_PATH = "Documentation/zigux/phase15-architecture-council-review-process.md"
MANIFEST_PATH = "zigux/tests/phase15_architecture_council_review_process_manifest.json"
SCRIPT_README_PATH = "scripts/zigux/README.md"
TESTS_README_PATH = "zigux/tests/README.md"
MAKEFILE_PATH = "zigux/Makefile"

SELF_REFERENCE_MARKER = "Documentation/zigux/phase15-architecture-council-review-process.md"
PRODUCT_BOUNDARY_MARKER = "product boundary:"
REQUIRED_NOTE_BOUNDARY_MARKERS = [
    "`Documentation/zigux/freeze-map.md`",
    "`Documentation/zigux/phase15-freeze-map-governance.md`",
    "`Documentation/zigux/phase15-architecture-council-review-process.md`",
    "`Documentation/zigux/phase15-parity-scorecard.md`",
    "`Documentation/zigux/phase15-indefinite-c-policy.md`",
    "`Documentation/zigux/review-checklist.md`",
    "`scripts/zigux/check-phase15-review-process-handoff.py`",
    "`zigux/tests/phase15_architecture_council_review_process_manifest.json`",
    "`zigux/tests/phase15_architecture_council_review_process.zig`",
    "`zigux/tests/phase15_build.zig`",
]
OPTIONAL_LANE_ROUTE_MARKERS = [
    "scripts-root validator path",
    "tests-root guidance path",
    "dedicated handoff-checker route",
]
REQUIRED_DOCS_README_MARKERS = [
    "Phase 15 notes",
    "Documentation/zigux/freeze-map.md",
    "Documentation/zigux/phase15-freeze-map-governance.md",
    "Documentation/zigux/phase15-architecture-council-review-process.md",
    "Documentation/zigux/phase15-parity-scorecard.md",
    "Documentation/zigux/phase15-indefinite-c-policy.md",
    "zigux/tests/phase15_build.zig",
    "make -C zigux phase15",
]
REQUIRED_SCRIPT_README_MARKERS = [
    "Phase 15 flow",
    "phase15-architecture-council-review-process.md",
    "check-phase15-review-process-handoff.py",
    "zigux/tests/phase15_architecture_council_review_process_manifest.json",
    "zigux/tests/phase15_architecture_council_review_process.zig",
    "phase15_build.zig",
    "make -C zigux phase15",
]
EXACT_ONCE_SCRIPT_README_MARKERS = [
    "Phase 15 flow",
    "check-phase15-review-process-handoff.py",
]
REQUIRED_REVIEW_CHECKLIST_MARKERS = [
    "if the change touches the shared Phase 15 governance packet",
    "Documentation/zigux/freeze-map.md",
    "Documentation/zigux/phase15-freeze-map-governance.md",
    "Documentation/zigux/phase15-architecture-council-review-process.md",
    "Documentation/zigux/phase15-parity-scorecard.md",
    "Documentation/zigux/phase15-indefinite-c-policy.md",
    "Documentation/zigux/review-checklist.md",
    "scripts/zigux/check-phase15-review-process-handoff.py",
    "zigux/tests/phase15_freeze_map_governance.zig",
    "zigux/tests/phase15_parity_scorecard.zig",
    "zigux/tests/phase15_architecture_council_review_process.zig",
    "zigux/tests/phase15_indefinite_c_policy.json",
    "zigux/tests/phase15_indefinite_c_policy.zig",
    "zigux/tests/phase15_build.zig",
    "make -C zigux phase15",
]
REQUIRED_TESTS_README_MARKERS = [
    "keep the parked Phase 15 governance packet explicit in the tests root too",
    "Documentation/zigux/freeze-map.md",
    "Documentation/zigux/phase15-freeze-map-governance.md",
    "Documentation/zigux/phase15-architecture-council-review-process.md",
    "Documentation/zigux/phase15-parity-scorecard.md",
    "Documentation/zigux/phase15-indefinite-c-policy.md",
    "Documentation/zigux/review-checklist.md",
    "scripts/zigux/check-phase15-review-process-handoff.py",
    "zigux/tests/phase15_build.zig",
    "zigux/tests/phase15_freeze_map_governance.zig",
    "zigux/tests/phase15_parity_scorecard.zig",
    "zigux/tests/phase15_architecture_council_review_process.zig",
    "zigux/tests/phase15_indefinite_c_policy.json",
    "zigux/tests/phase15_indefinite_c_policy.zig",
    "zigux/Makefile",
    "zig build test --build-file zigux/tests/phase15_build.zig",
    "make -C zigux phase15",
]
REQUIRED_MAKEFILE_MARKERS = [
    "PHONY += phase15-validate phase15-test phase15",
    "phase15-validate:",
    "scripts/zigux/check-phase15-review-process-handoff.py --self-test",
    "scripts/zigux/check-phase15-review-process-handoff.py",
    "phase15-test:",
    "zigux/tests/phase15_build.zig",
]
EXACT_ONCE_MAKEFILE_MARKERS = [
    "PHONY += phase15-validate phase15-test phase15",
    "phase15-validate:",
    "phase15-test:",
]


def read_text(root: Path, rel_path: str) -> str:
    return (root / rel_path).read_text(encoding="utf-8")


def load_json(root: Path, rel_path: str) -> dict:
    return json.loads(read_text(root, rel_path))


def expect_exact_once(text: str, marker: str, label: str, failures: list[str]) -> None:
    count = text.count(marker)
    if count != 1:
        failures.append(f"{label}:{marker}:count={count}")


def validate(root: Path) -> list[str]:
    failures: list[str] = []

    docs_readme_path = root / DOCS_README_PATH
    review_checklist_path = root / REVIEW_CHECKLIST_PATH
    note_path = root / NOTE_PATH
    manifest_path = root / MANIFEST_PATH
    script_readme_path = root / SCRIPT_README_PATH
    tests_readme_path = root / TESTS_README_PATH
    makefile_path = root / MAKEFILE_PATH
    if not docs_readme_path.exists():
        failures.append(f"missing_file:{DOCS_README_PATH}")
        return failures
    if not review_checklist_path.exists():
        failures.append(f"missing_file:{REVIEW_CHECKLIST_PATH}")
        return failures
    if not note_path.exists():
        failures.append(f"missing_file:{NOTE_PATH}")
        return failures
    if not manifest_path.exists():
        failures.append(f"missing_file:{MANIFEST_PATH}")
        return failures
    if not script_readme_path.exists():
        failures.append(f"missing_file:{SCRIPT_README_PATH}")
        return failures
    if not tests_readme_path.exists():
        failures.append(f"missing_file:{TESTS_README_PATH}")
        return failures
    if not makefile_path.exists():
        failures.append(f"missing_file:{MAKEFILE_PATH}")
        return failures

    docs_readme = read_text(root, DOCS_README_PATH)
    review_checklist = read_text(root, REVIEW_CHECKLIST_PATH)
    note = read_text(root, NOTE_PATH)
    manifest = load_json(root, MANIFEST_PATH)
    script_readme = read_text(root, SCRIPT_README_PATH)
    tests_readme = read_text(root, TESTS_README_PATH)
    makefile = read_text(root, MAKEFILE_PATH)

    for marker in REQUIRED_DOCS_README_MARKERS:
        if marker not in docs_readme:
            failures.append(f"docs_readme:{marker}")

    expect_exact_once(note, SELF_REFERENCE_MARKER, "note_self_reference", failures)
    if PRODUCT_BOUNDARY_MARKER not in note:
        failures.append("note:product_boundary_section")
    for marker in REQUIRED_NOTE_BOUNDARY_MARKERS:
        if marker not in note:
            failures.append(f"note:{marker}")

    for marker in REQUIRED_SCRIPT_README_MARKERS:
        if marker not in script_readme:
            failures.append(f"script_readme:{marker}")
    for marker in EXACT_ONCE_SCRIPT_README_MARKERS:
        expect_exact_once(script_readme, marker, "script_readme_exact_once", failures)

    for marker in REQUIRED_REVIEW_CHECKLIST_MARKERS:
        if marker not in review_checklist:
            failures.append(f"review_checklist:{marker}")

    for marker in REQUIRED_TESTS_README_MARKERS:
        if marker not in tests_readme:
            failures.append(f"tests_readme:{marker}")

    for marker in REQUIRED_MAKEFILE_MARKERS:
        if marker not in makefile:
            failures.append(f"makefile:{marker}")
    for marker in EXACT_ONCE_MAKEFILE_MARKERS:
        expect_exact_once(makefile, marker, "makefile_exact_once", failures)

    handoff = manifest.get("handoff_evidence")
    if handoff is None:
        failures.append("manifest:handoff_evidence:missing")
        return failures
    if not isinstance(handoff, dict):
        failures.append("manifest:handoff_evidence:not_object")
        return failures

    current_repo_handoff = handoff.get("current_repo_handoff")
    if current_repo_handoff is None:
        failures.append("manifest:handoff_evidence.current_repo_handoff:missing")
    elif not isinstance(current_repo_handoff, str):
        failures.append("manifest:handoff_evidence.current_repo_handoff:not_string")
    else:
        expect_exact_once(
            current_repo_handoff,
            SELF_REFERENCE_MARKER,
            "manifest_self_reference",
            failures,
        )

    current_bounded_lane = handoff.get("current_bounded_lane")
    if current_bounded_lane is None:
        failures.append("manifest:handoff_evidence.current_bounded_lane:missing")
    elif not isinstance(current_bounded_lane, str):
        failures.append("manifest:handoff_evidence.current_bounded_lane:not_string")
    else:
        for marker in OPTIONAL_LANE_ROUTE_MARKERS:
            if marker not in current_bounded_lane:
                failures.append(f"manifest_lane:{marker}")

    return failures


def write_fixture_tree(root: Path) -> None:
    (root / "Documentation/zigux").mkdir(parents=True, exist_ok=True)
    (root / "zigux/tests").mkdir(parents=True, exist_ok=True)
    (root / "scripts/zigux").mkdir(parents=True, exist_ok=True)
    (root / "zigux").mkdir(parents=True, exist_ok=True)

    docs_readme = """# Zigux Documentation

Phase 15 notes
- `Documentation/zigux/freeze-map.md`
- `Documentation/zigux/phase15-freeze-map-governance.md`
- `Documentation/zigux/phase15-architecture-council-review-process.md`
- `Documentation/zigux/phase15-parity-scorecard.md`
- `Documentation/zigux/phase15-indefinite-c-policy.md`
- `zigux/tests/phase15_build.zig` and `make -C zigux phase15` keep the parked governance packet reviewable.
"""
    (root / DOCS_README_PATH).write_text(docs_readme, encoding="utf-8")

    review_checklist = """# Zigux Review Checklist

- if the change touches the shared Phase 15 governance packet, do `Documentation/zigux/freeze-map.md`, `Documentation/zigux/phase15-freeze-map-governance.md`, `Documentation/zigux/phase15-architecture-council-review-process.md`, `Documentation/zigux/phase15-parity-scorecard.md`, `Documentation/zigux/phase15-indefinite-c-policy.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/check-phase15-review-process-handoff.py`, `zigux/tests/phase15_freeze_map_governance.zig`, `zigux/tests/phase15_parity_scorecard.zig`, `zigux/tests/phase15_architecture_council_review_process.zig`, `zigux/tests/phase15_indefinite_c_policy.json`, `zigux/tests/phase15_indefinite_c_policy.zig`, `zigux/tests/phase15_build.zig`, and `make -C zigux phase15` still agree on the same parked governance packet?
"""
    (root / REVIEW_CHECKLIST_PATH).write_text(review_checklist, encoding="utf-8")

    note = """# Phase 15 Architecture Council Review Process Survey

## Status

- product boundary:
  - `Documentation/zigux/freeze-map.md`
  - `Documentation/zigux/phase15-freeze-map-governance.md`
  - `Documentation/zigux/phase15-architecture-council-review-process.md`
  - `Documentation/zigux/phase15-parity-scorecard.md`
  - `Documentation/zigux/phase15-indefinite-c-policy.md`
  - `Documentation/zigux/review-checklist.md`
  - `scripts/zigux/check-phase15-review-process-handoff.py`
  - `zigux/tests/phase15_architecture_council_review_process_manifest.json`
  - `zigux/tests/phase15_architecture_council_review_process.zig`
  - `zigux/tests/phase15_build.zig`
"""
    (root / NOTE_PATH).write_text(note, encoding="utf-8")

    manifest = {
        "lane_key": "P15-L14",
        "phase": "Phase 15",
        "handoff_evidence": {
            "current_repo_handoff": (
                "The current repo handoff explicitly names "
                "Documentation/zigux/phase15-architecture-council-review-process.md "
                "beside the neighboring governance packet."
            ),
            "current_bounded_lane": (
                "The parked Architecture Council packet stays aligned with its "
                "scripts-root validator path, its tests-root guidance path, and its "
                "dedicated handoff-checker route."
            ),
        },
    }
    (root / MANIFEST_PATH).parent.mkdir(parents=True, exist_ok=True)
    (root / MANIFEST_PATH).write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    script_readme = """# scripts/zigux

Phase 15 flow
- the current shared Phase 15 governance surface on `master` is `Documentation/zigux/phase15-architecture-council-review-process.md`, `scripts/zigux/check-phase15-review-process-handoff.py`, `zigux/tests/phase15_architecture_council_review_process_manifest.json`, `zigux/tests/phase15_architecture_council_review_process.zig`, `zigux/tests/phase15_build.zig`, and `make -C zigux phase15`.
"""
    (root / SCRIPT_README_PATH).write_text(script_readme, encoding="utf-8")

    tests_readme = """# zigux/tests

- keep the parked Phase 15 governance packet explicit in the tests root too: `Documentation/zigux/freeze-map.md`, `Documentation/zigux/phase15-freeze-map-governance.md`, `Documentation/zigux/phase15-architecture-council-review-process.md`, `Documentation/zigux/phase15-parity-scorecard.md`, `Documentation/zigux/phase15-indefinite-c-policy.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/check-phase15-review-process-handoff.py`, `zigux/tests/phase15_build.zig`, `zigux/tests/phase15_freeze_map_governance.zig`, `zigux/tests/phase15_parity_scorecard.zig`, `zigux/tests/phase15_architecture_council_review_process.zig`, `zigux/tests/phase15_indefinite_c_policy.json`, `zigux/tests/phase15_indefinite_c_policy.zig`, `zigux/Makefile`, `zig build test --build-file zigux/tests/phase15_build.zig`, and `make -C zigux phase15` should continue to keep the current freeze-map, review-process, parity-scorecard, and indefinite-C governance packet reviewable through one shared build-and-make route without implying any Architecture Council approval for a freeze-map status change.
"""
    (root / TESTS_README_PATH).write_text(tests_readme, encoding="utf-8")

    makefile = """PHONY += phase15-validate phase15-test phase15

phase15-validate:
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase15-review-process-handoff.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase15-review-process-handoff.py

phase15-test:
	cd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/phase15_build.zig

phase15: phase15-validate phase15-test
"""
    (root / MAKEFILE_PATH).write_text(makefile, encoding="utf-8")


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

        docs_readme_path = tmp_root / DOCS_README_PATH
        docs_readme = docs_readme_path.read_text(encoding="utf-8")
        docs_readme_path.write_text(
            docs_readme.replace("`Documentation/zigux/phase15-parity-scorecard.md`\n", "", 1),
            encoding="utf-8",
        )
        expect_failure(
            tmp_root,
            "docs_readme:Documentation/zigux/phase15-parity-scorecard.md",
            "missing_docs_readme_phase15_marker",
        )

        write_fixture_tree(tmp_root)
        note_path = tmp_root / NOTE_PATH
        original_note = note_path.read_text(encoding="utf-8")
        note_path.write_text(
            original_note.replace(
                "`Documentation/zigux/phase15-architecture-council-review-process.md`",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_failure(
            tmp_root,
            "note_self_reference:Documentation/zigux/phase15-architecture-council-review-process.md:count=0",
            "missing_note_self_reference",
        )
        note_path.write_text(original_note, encoding="utf-8")

        note_path.write_text(
            original_note.replace(
                "product boundary:",
                "governance packet:",
                1,
            ),
            encoding="utf-8",
        )
        expect_failure(
            tmp_root,
            "note:product_boundary_section",
            "missing_product_boundary_marker",
        )

        write_fixture_tree(tmp_root)
        note_path = tmp_root / NOTE_PATH
        note_path.write_text(
            note_path.read_text(encoding="utf-8").replace(
                "  - `zigux/tests/phase15_architecture_council_review_process_manifest.json`\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_failure(
            tmp_root,
            "note:`zigux/tests/phase15_architecture_council_review_process_manifest.json`",
            "missing_note_manifest_marker",
        )

        write_fixture_tree(tmp_root)
        manifest_path = tmp_root / MANIFEST_PATH
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        del manifest["handoff_evidence"]
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        expect_failure(
            tmp_root,
            "manifest:handoff_evidence:missing",
            "missing_manifest_handoff_block",
        )

        write_fixture_tree(tmp_root)
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["handoff_evidence"]["current_repo_handoff"] = manifest["handoff_evidence"][
            "current_repo_handoff"
        ].replace(SELF_REFERENCE_MARKER, "this review-process note", 1)
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        expect_failure(
            tmp_root,
            "manifest_self_reference:Documentation/zigux/phase15-architecture-council-review-process.md:count=0",
            "missing_manifest_self_reference",
        )

        write_fixture_tree(tmp_root)
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["handoff_evidence"]["current_bounded_lane"] = "The parked packet stays aligned."
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        expect_failure(
            tmp_root,
            "manifest_lane:scripts-root validator path",
            "missing_manifest_lane_route_marker",
        )

        write_fixture_tree(tmp_root)
        script_readme_path = tmp_root / SCRIPT_README_PATH
        script_readme = script_readme_path.read_text(encoding="utf-8")
        script_readme_path.write_text(
            script_readme.replace("check-phase15-review-process-handoff.py", "", 1),
            encoding="utf-8",
        )
        expect_failure(
            tmp_root,
            "script_readme:check-phase15-review-process-handoff.py",
            "missing_script_readme_checker_marker",
        )

        write_fixture_tree(tmp_root)
        script_readme = script_readme_path.read_text(encoding="utf-8")
        script_readme_path.write_text(
            script_readme.replace(
                "`zigux/tests/phase15_architecture_council_review_process_manifest.json`, ",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_failure(
            tmp_root,
            "script_readme:zigux/tests/phase15_architecture_council_review_process_manifest.json",
            "missing_script_readme_manifest_marker",
        )

        write_fixture_tree(tmp_root)
        review_checklist_path = tmp_root / REVIEW_CHECKLIST_PATH
        review_checklist = review_checklist_path.read_text(encoding="utf-8")
        review_checklist_path.write_text(
            review_checklist.replace(
                "`zigux/tests/phase15_architecture_council_review_process.zig`, ",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_failure(
            tmp_root,
            "review_checklist:zigux/tests/phase15_architecture_council_review_process.zig",
            "missing_review_checklist_review_process_test_marker",
        )

        write_fixture_tree(tmp_root)
        tests_readme_path = tmp_root / TESTS_README_PATH
        tests_readme = tests_readme_path.read_text(encoding="utf-8")
        tests_readme_path.write_text(
            tests_readme.replace("`zigux/tests/phase15_architecture_council_review_process.zig`, ", "", 1),
            encoding="utf-8",
        )
        expect_failure(
            tmp_root,
            "tests_readme:zigux/tests/phase15_architecture_council_review_process.zig",
            "missing_tests_readme_phase15_marker",
        )

        write_fixture_tree(tmp_root)
        makefile_path = tmp_root / MAKEFILE_PATH
        makefile = makefile_path.read_text(encoding="utf-8")
        makefile_path.write_text(
            makefile.replace(
                "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase15-review-process-handoff.py --self-test\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_failure(
            tmp_root,
            "makefile:scripts/zigux/check-phase15-review-process-handoff.py --self-test",
            "missing_makefile_self_test_marker",
        )

    print("PHASE15_REVIEW_PROCESS_HANDOFF_SELF_TEST=pass")
    print("PHASE15_REVIEW_PROCESS_HANDOFF_SELF_TEST_CASE_COUNT=13")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the Phase 15 Architecture Council review-process handoff surfaces."
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
        f"{2 + len(REQUIRED_NOTE_BOUNDARY_MARKERS) + len(OPTIONAL_LANE_ROUTE_MARKERS) + len(REQUIRED_DOCS_README_MARKERS) + len(REQUIRED_SCRIPT_README_MARKERS) + len(EXACT_ONCE_SCRIPT_README_MARKERS) + len(REQUIRED_REVIEW_CHECKLIST_MARKERS) + len(REQUIRED_TESTS_README_MARKERS) + len(REQUIRED_MAKEFILE_MARKERS) + len(EXACT_ONCE_MAKEFILE_MARKERS)}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
