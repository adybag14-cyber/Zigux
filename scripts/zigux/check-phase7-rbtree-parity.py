#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


SELF_PATH = Path(__file__).resolve()
ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) >= 3 else SELF_PATH.parent

REQUIRED_FILES = [
    ".github/workflows/zigux-bootstrap.yml",
    "Documentation/zigux/README.md",
    "Documentation/zigux/review-checklist.md",
    "Documentation/zigux/phase7-rbtree-slice.md",
    "Documentation/zigux/phase7-make-wrapper-selftest-alignment.md",
    "Documentation/zigux/phase7-helper-lane-sequencing.md",
    "samples/zigux/README.md",
    "scripts/zigux/README.md",
    "scripts/zigux/validate-phase7.py",
    "scripts/zigux/check-phase7-make-wrapper.py",
    "scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py",
    "scripts/zigux/check-phase7-build-wiring.py",
    "zigux/Makefile",
    "zigux/tests/README.md",
    "zigux/tests/phase7_build.zig",
    "zigux/tests/phase7_rbtree.zig",
    "zigux/tests/phase7_rbtree_survey.zig",
    "zigux/tests/phase7_rbtree_manifest.json",
    "zigux/tests/fixtures/phase7_rbtree.json",
    "zigux/tests/fixtures/phase7_rbtree_c_harness.c",
    "lib/rbtree.zig",
]

REQUIRED_MARKERS = {
    ".github/workflows/zigux-bootstrap.yml": [
        "Validate Phase 7 runtime helper gates",
        "make -C zigux phase7-validate",
        "Run Phase 7 runtime helper tests",
        "make -C zigux phase7-test",
    ],
    # The shared make-wrapper note explicitly records the docs-root README as a
    # still-pending backlog sync, so only fail-close on the shorter Phase 7
    # shorthand that current master already lands there today.
    "Documentation/zigux/README.md": [
        "Documentation/zigux/phase7-rbtree-slice.md",
        "zigux/tests/phase7_build.zig",
        "make -C zigux phase7",
    ],
    "Documentation/zigux/review-checklist.md": [
        "Documentation/zigux/phase7-rbtree-slice.md",
        "Documentation/zigux/phase7-make-wrapper-selftest-alignment.md",
        "lib/rbtree.zig",
        "scripts/zigux/check-phase7-make-wrapper.py",
        "scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py",
        "scripts/zigux/check-phase7-build-wiring.py",
        "scripts/zigux/check-phase7-rbtree-parity.py",
        "zigux/tests/fixtures/phase7_rbtree.json",
        "zigux/tests/fixtures/phase7_rbtree_c_harness.c",
    ],
    "Documentation/zigux/phase7-rbtree-slice.md": [
        "Documentation/zigux/phase7-helper-lane-sequencing.md",
        "python3 scripts/zigux/check-phase7-rbtree-parity.py",
        "zig build test --build-file zigux/tests/phase7_build.zig",
        "this slice does not carry an open parity-fixture follow-up",
        "linked-node teardown keeps detached ownership state, neighbour relinking, and leftmost continuity reviewable inside the shared Phase 7 packet",
        "cached-leftmost handoff and final singleton `eraseCached()` state stay explicit in the shared tests instead of being hidden behind the helper implementation alone",
    ],
    "Documentation/zigux/phase7-helper-lane-sequencing.md": [
        "rbtree packet, lane `P7-L13`:",
        "Documentation/zigux/phase7-rbtree-slice.md",
        "zigux/tests/phase7_rbtree_manifest.json",
        "scripts/zigux/check-phase7-rbtree-parity.py",
        "PHASE7_RBTREE_LANE=P7-L13",
        "`P7-L13` owns only rbtree helper-local parity, traversal, manifest, fixture, checker, or reminder drift.",
    ],
    "samples/zigux/README.md": [
        "current `master` still ships no `samples/zigux/*rbtree*` Phase 5 reference sample;",
        "Documentation/zigux/phase7-rbtree-slice.md",
        "Documentation/zigux/phase7-make-wrapper-selftest-alignment.md",
        "lib/rbtree.zig",
        "scripts/zigux/check-phase7-make-wrapper.py",
        "scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py",
        "scripts/zigux/check-phase7-build-wiring.py",
        "scripts/zigux/check-phase7-rbtree-parity.py",
        "zigux/tests/phase7_build.zig",
    ],
    "scripts/zigux/README.md": [
        "scripts/zigux/check-phase7-make-wrapper.py",
        "scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py",
        "scripts/zigux/check-phase7-build-wiring.py",
        "scripts/zigux/check-phase7-rbtree-parity.py",
        "make -C zigux phase7-validate",
        "make -C zigux phase7",
    ],
    "scripts/zigux/validate-phase7.py": [
        '"scripts/zigux/check-phase7-rbtree-parity.py"',
        '"zigux/tests/phase7_rbtree.zig"',
        '"zigux/tests/phase7_rbtree_survey.zig"',
        '"zigux/tests/phase7_rbtree_manifest.json"',
        '"zigux/tests/fixtures/phase7_rbtree.json"',
        '"zigux/tests/fixtures/phase7_rbtree_c_harness.c"',
    ],
    "zigux/tests/README.md": [
        "scripts/zigux/check-phase7-rbtree-parity.py",
        "zigux/tests/phase7_rbtree.zig",
        "zigux/tests/phase7_rbtree_survey.zig",
        "zigux/tests/phase7_rbtree_manifest.json",
        "zigux/tests/fixtures/phase7_rbtree.json",
        "zigux/tests/fixtures/phase7_rbtree_c_harness.c",
        "make -C zigux phase7-validate",
        "make -C zigux phase7",
    ],
    "zigux/Makefile": [
        "phase7-validate:",
        "scripts/zigux/check-phase7-rbtree-parity.py --self-test",
        "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase7-rbtree-parity.py",
        "phase7-test:",
        "phase7: phase7-validate phase7-test",
    ],
    "zigux/tests/phase7_build.zig": [
        "phase7-rbtree-tests",
        '"phase7_rbtree_survey.zig"',
        "phase7-rbtree-survey-tests",
        'run_rbtree_survey_tests.setCwd(b.path("../.."));',
    ],
    "zigux/tests/phase7_rbtree.zig": [
        "phase 7 rbtree balancing helpers keep ordered insert erase traversal stable",
        "phase 7 rbtree cached helpers return leftmost handoff state",
        "phase 7 rbtree eraseInit detaches erased nodes and keeps traversal stable",
        "phase 7 rbtree detached nodes stay non-empty until callers clear them",
        "phase 7 rbtree eraseLinked clears detached linked ownership state and reconnects neighbours",
        "phase 7 rbtree postorder traversal matches committed parity fixture",
    ],
    "zigux/tests/phase7_rbtree_survey.zig": [
        "Documentation/zigux/phase7-helper-lane-sequencing.md",
        "scripts/zigux/validate-phase7.py",
        "scripts/zigux/check-phase7-rbtree-parity.py",
        "zigux/tests/phase7_rbtree.zig",
        "zigux/tests/phase7_rbtree_survey.zig",
        "zigux/tests/phase7_rbtree_manifest.json",
        "python3 scripts/zigux/check-phase7-rbtree-parity.py --self-test",
        "python3 scripts/zigux/check-phase7-rbtree-parity.py",
        "phase 7 rbtree cached helpers return leftmost handoff state",
        "phase 7 rbtree eraseLinked clears detached linked ownership state and reconnects neighbours",
        "phase 7 rbtree postorder traversal matches committed parity fixture",
    ],
}


def collect_missing_files(root: Path) -> list[str]:
    return [rel for rel in REQUIRED_FILES if not (root / rel).exists()]


def collect_missing_markers(root: Path) -> list[str]:
    missing: list[str] = []
    for rel, markers in REQUIRED_MARKERS.items():
        text = (root / rel).read_text(encoding="utf-8")
        for marker in markers:
            if marker not in text:
                missing.append(f"{rel}: {marker}")
    return missing


def validate(root: Path) -> tuple[list[str], list[str]]:
    missing_files = collect_missing_files(root)
    if missing_files:
        return missing_files, []
    return [], collect_missing_markers(root)


def write_fixture_root(tmp_root: Path) -> None:
    fixture_text = {rel: "\n".join(markers) + "\n" for rel, markers in REQUIRED_MARKERS.items()}
    fixture_text.update(
        {
            "zigux/tests/phase7_rbtree_manifest.json": "{}\n",
            "zigux/tests/fixtures/phase7_rbtree.json": "{}\n",
            "zigux/tests/fixtures/phase7_rbtree_c_harness.c": "/* fixture */\n",
            "lib/rbtree.zig": "// fixture\n",
        }
    )
    for rel in REQUIRED_FILES:
        path = tmp_root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(fixture_text.get(rel, "# fixture\n"), encoding="utf-8")


def expect_missing_file(case: str, tmp_root: Path, rel: str) -> None:
    missing_files, missing_markers = validate(tmp_root)
    assert missing_markers == [], case
    assert missing_files == [rel], case


def expect_missing_marker(case: str, tmp_root: Path, marker: str) -> None:
    missing_files, missing_markers = validate(tmp_root)
    assert missing_files == [], case
    assert missing_markers == [marker], case


def mutate_file(tmp_root: Path, rel: str, old: str, new: str, case: str) -> None:
    path = tmp_root / rel
    original = path.read_text(encoding="utf-8")
    updated = original.replace(old, new, 1)
    assert updated != original, case
    path.write_text(updated, encoding="utf-8")


def run_self_test() -> None:
    missing_file_cases = [
        ("missing_review_checklist", "Documentation/zigux/review-checklist.md"),
        ("missing_alignment_note", "Documentation/zigux/phase7-make-wrapper-selftest-alignment.md"),
        ("missing_helper_lane_note", "Documentation/zigux/phase7-helper-lane-sequencing.md"),
        ("missing_make_wrapper_checker", "scripts/zigux/check-phase7-make-wrapper.py"),
        ("missing_make_wrapper_alignment_checker", "scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py"),
        ("missing_scripts_readme", "scripts/zigux/README.md"),
        ("missing_tests_readme", "zigux/tests/README.md"),
        ("missing_manifest", "zigux/tests/phase7_rbtree_manifest.json"),
        ("missing_json_fixture", "zigux/tests/fixtures/phase7_rbtree.json"),
        ("missing_c_harness", "zigux/tests/fixtures/phase7_rbtree_c_harness.c"),
    ]

    marker_cases = [
        (
            "docs_readme_shared_build_marker",
            "Documentation/zigux/README.md",
            "zigux/tests/phase7_build.zig",
            "",
            "Documentation/zigux/README.md: zigux/tests/phase7_build.zig",
        ),
        (
            "review_checklist_slice_marker",
            "Documentation/zigux/review-checklist.md",
            "Documentation/zigux/phase7-rbtree-slice.md",
            "",
            "Documentation/zigux/review-checklist.md: Documentation/zigux/phase7-rbtree-slice.md",
        ),
        (
            "review_checklist_alignment_marker",
            "Documentation/zigux/review-checklist.md",
            "Documentation/zigux/phase7-make-wrapper-selftest-alignment.md",
            "",
            "Documentation/zigux/review-checklist.md: Documentation/zigux/phase7-make-wrapper-selftest-alignment.md",
        ),
        (
            "review_checklist_build_wiring_marker",
            "Documentation/zigux/review-checklist.md",
            "scripts/zigux/check-phase7-build-wiring.py",
            "",
            "Documentation/zigux/review-checklist.md: scripts/zigux/check-phase7-build-wiring.py",
        ),
        (
            "slice_helper_lane_note_marker",
            "Documentation/zigux/phase7-rbtree-slice.md",
            "Documentation/zigux/phase7-helper-lane-sequencing.md",
            "",
            "Documentation/zigux/phase7-rbtree-slice.md: Documentation/zigux/phase7-helper-lane-sequencing.md",
        ),
        (
            "slice_checker_marker",
            "Documentation/zigux/phase7-rbtree-slice.md",
            "python3 scripts/zigux/check-phase7-rbtree-parity.py",
            "",
            "Documentation/zigux/phase7-rbtree-slice.md: python3 scripts/zigux/check-phase7-rbtree-parity.py",
        ),
        (
            "slice_followup_marker",
            "Documentation/zigux/phase7-rbtree-slice.md",
            "this slice does not carry an open parity-fixture follow-up",
            "",
            "Documentation/zigux/phase7-rbtree-slice.md: this slice does not carry an open parity-fixture follow-up",
        ),
        (
            "slice_linked_teardown_marker",
            "Documentation/zigux/phase7-rbtree-slice.md",
            "linked-node teardown keeps detached ownership state, neighbour relinking, and leftmost continuity reviewable inside the shared Phase 7 packet",
            "",
            "Documentation/zigux/phase7-rbtree-slice.md: linked-node teardown keeps detached ownership state, neighbour relinking, and leftmost continuity reviewable inside the shared Phase 7 packet",
        ),
        (
            "slice_cached_leftmost_marker",
            "Documentation/zigux/phase7-rbtree-slice.md",
            "cached-leftmost handoff and final singleton `eraseCached()` state stay explicit in the shared tests instead of being hidden behind the helper implementation alone",
            "",
            "Documentation/zigux/phase7-rbtree-slice.md: cached-leftmost handoff and final singleton `eraseCached()` state stay explicit in the shared tests instead of being hidden behind the helper implementation alone",
        ),
        (
            "helper_lane_note_packet_marker",
            "Documentation/zigux/phase7-helper-lane-sequencing.md",
            "rbtree packet, lane `P7-L13`:",
            "",
            "Documentation/zigux/phase7-helper-lane-sequencing.md: rbtree packet, lane `P7-L13`:",
        ),
        (
            "helper_lane_note_lane_constant_marker",
            "Documentation/zigux/phase7-helper-lane-sequencing.md",
            "PHASE7_RBTREE_LANE=P7-L13",
            "",
            "Documentation/zigux/phase7-helper-lane-sequencing.md: PHASE7_RBTREE_LANE=P7-L13",
        ),
        (
            "helper_lane_note_owner_rule_marker",
            "Documentation/zigux/phase7-helper-lane-sequencing.md",
            "`P7-L13` owns only rbtree helper-local parity, traversal, manifest, fixture, checker, or reminder drift.",
            "",
            "Documentation/zigux/phase7-helper-lane-sequencing.md: `P7-L13` owns only rbtree helper-local parity, traversal, manifest, fixture, checker, or reminder drift.",
        ),
        (
            "samples_make_wrapper_alignment_marker",
            "samples/zigux/README.md",
            "scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py",
            "",
            "samples/zigux/README.md: scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py",
        ),
        (
            "scripts_readme_checker_marker",
            "scripts/zigux/README.md",
            "scripts/zigux/check-phase7-rbtree-parity.py",
            "",
            "scripts/zigux/README.md: scripts/zigux/check-phase7-rbtree-parity.py",
        ),
        (
            "makefile_checker_selftest_marker",
            "zigux/Makefile",
            "scripts/zigux/check-phase7-rbtree-parity.py --self-test",
            "",
            "zigux/Makefile: scripts/zigux/check-phase7-rbtree-parity.py --self-test",
        ),
        (
            "build_survey_cwd_marker",
            "zigux/tests/phase7_build.zig",
            'run_rbtree_survey_tests.setCwd(b.path("../.."));',
            'run_rbtree_survey_tests.setCwd(b.path("."));',
            'zigux/tests/phase7_build.zig: run_rbtree_survey_tests.setCwd(b.path("../.."));',
        ),
        (
            "helper_cached_leftmost_marker",
            "zigux/tests/phase7_rbtree.zig",
            "phase 7 rbtree cached helpers return leftmost handoff state",
            "",
            "zigux/tests/phase7_rbtree.zig: phase 7 rbtree cached helpers return leftmost handoff state",
        ),
        (
            "helper_erase_init_marker",
            "zigux/tests/phase7_rbtree.zig",
            "phase 7 rbtree eraseInit detaches erased nodes and keeps traversal stable",
            "",
            "zigux/tests/phase7_rbtree.zig: phase 7 rbtree eraseInit detaches erased nodes and keeps traversal stable",
        ),
        (
            "helper_linked_teardown_marker",
            "zigux/tests/phase7_rbtree.zig",
            "phase 7 rbtree eraseLinked clears detached linked ownership state and reconnects neighbours",
            "",
            "zigux/tests/phase7_rbtree.zig: phase 7 rbtree eraseLinked clears detached linked ownership state and reconnects neighbours",
        ),
        (
            "helper_postorder_marker",
            "zigux/tests/phase7_rbtree.zig",
            "phase 7 rbtree postorder traversal matches committed parity fixture",
            "",
            "zigux/tests/phase7_rbtree.zig: phase 7 rbtree postorder traversal matches committed parity fixture",
        ),
        (
            "survey_helper_lane_note_marker",
            "zigux/tests/phase7_rbtree_survey.zig",
            "Documentation/zigux/phase7-helper-lane-sequencing.md",
            "",
            "zigux/tests/phase7_rbtree_survey.zig: Documentation/zigux/phase7-helper-lane-sequencing.md",
        ),
        (
            "survey_selftest_marker",
            "zigux/tests/phase7_rbtree_survey.zig",
            "python3 scripts/zigux/check-phase7-rbtree-parity.py --self-test",
            "",
            "zigux/tests/phase7_rbtree_survey.zig: python3 scripts/zigux/check-phase7-rbtree-parity.py --self-test",
        ),
        (
            "survey_cached_leftmost_marker",
            "zigux/tests/phase7_rbtree_survey.zig",
            "phase 7 rbtree cached helpers return leftmost handoff state",
            "",
            "zigux/tests/phase7_rbtree_survey.zig: phase 7 rbtree cached helpers return leftmost handoff state",
        ),
        (
            "survey_linked_teardown_marker",
            "zigux/tests/phase7_rbtree_survey.zig",
            "phase 7 rbtree eraseLinked clears detached linked ownership state and reconnects neighbours",
            "",
            "zigux/tests/phase7_rbtree_survey.zig: phase 7 rbtree eraseLinked clears detached linked ownership state and reconnects neighbours",
        ),
        (
            "survey_postorder_marker",
            "zigux/tests/phase7_rbtree_survey.zig",
            "phase 7 rbtree postorder traversal matches committed parity fixture",
            "",
            "zigux/tests/phase7_rbtree_survey.zig: phase 7 rbtree postorder traversal matches committed parity fixture",
        ),
    ]

    with tempfile.TemporaryDirectory(prefix="zigux_phase7_rbtree_parity_") as tmp_dir_str:
        tmp_root = Path(tmp_dir_str)
        write_fixture_root(tmp_root)
        assert validate(tmp_root) == ([], [])

        for case, rel in missing_file_cases:
            (tmp_root / rel).unlink()
            expect_missing_file(case, tmp_root, rel)
            write_fixture_root(tmp_root)

        for case, rel, old, new, expected in marker_cases:
            mutate_file(tmp_root, rel, old, new, case)
            expect_missing_marker(case, tmp_root, expected)
            write_fixture_root(tmp_root)

    case_count = len(missing_file_cases) + len(marker_cases)
    print("PHASE7_RBTREE_PARITY_SELF_TEST=pass")
    print(f"PHASE7_RBTREE_PARITY_SELF_TEST_CASE_COUNT={case_count}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Check that the Phase 7 rbtree parity packet stays aligned.")
    parser.add_argument("--self-test", action="store_true", help="Run checker self-tests without reading repo files.")
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return 0

    missing_files, missing_markers = validate(ROOT)
    if missing_files:
        print("PHASE7_RBTREE_PARITY=fail")
        print("MISSING_PHASE7_RBTREE_PARITY_FILES_START")
        for item in missing_files:
            print(item)
        print("MISSING_PHASE7_RBTREE_PARITY_FILES_END")
        return 1

    if missing_markers:
        print("PHASE7_RBTREE_PARITY=fail")
        print("MISSING_PHASE7_RBTREE_PARITY_MARKERS_START")
        for item in missing_markers:
            print(item)
        print("MISSING_PHASE7_RBTREE_PARITY_MARKERS_END")
        return 1

    print("PHASE7_RBTREE_PARITY=pass")
    print(f"PHASE7_RBTREE_PARITY_FILE_COUNT={len(REQUIRED_FILES)}")
    print(f"PHASE7_RBTREE_PARITY_MARKER_COUNT={sum(len(markers) for markers in REQUIRED_MARKERS.values())}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())