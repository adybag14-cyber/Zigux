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
    "Documentation/zigux/phase7-make-wrapper-selftest-alignment.md",
    "Documentation/zigux/phase7-helper-lane-sequencing.md",
    "Documentation/zigux/phase7-string-helpers-slice.md",
    "samples/zigux/README.md",
    "scripts/zigux/README.md",
    "scripts/zigux/validate-phase7.py",
    "scripts/zigux/check-phase7-make-wrapper.py",
    "scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py",
    "scripts/zigux/check-phase7-build-wiring.py",
    "scripts/zigux/check-phase7-argv-split-packet.py",
    "scripts/zigux/check-phase7-rbtree-parity.py",
    "zigux/Makefile",
    "zigux/tests/README.md",
    "zigux/tests/phase7_build.zig",
    "zigux/tests/phase7_string_helpers_manifest.json",
]

REQUIRED_MARKERS = {
    "Documentation/zigux/README.md": [
        "Documentation/zigux/phase7-make-wrapper-selftest-alignment.md",
        "scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py",
        "scripts/zigux/check-phase7-build-wiring.py",
        "make -C zigux phase7",
    ],
    "Documentation/zigux/review-checklist.md": [
        "Documentation/zigux/phase7-make-wrapper-selftest-alignment.md",
        "scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py",
        "scripts/zigux/check-phase7-build-wiring.py",
        "zigux/tests/fixtures/phase7_cmdline_next_arg_vectors.zig",
        "zigux/tests/fixtures/phase7_argv_split_vectors.zig",
    ],
    "Documentation/zigux/phase7-make-wrapper-selftest-alignment.md": [
        "`PHASE7_LANE_KEY=P7-Y05`",
        "python3 scripts/zigux/validate-phase7.py --self-test",
        "python3 scripts/zigux/validate-phase7.py",
        "python3 scripts/zigux/check-phase7-make-wrapper.py --self-test",
        "python3 scripts/zigux/check-phase7-make-wrapper.py",
        "python3 scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py --self-test",
        "python3 scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py",
        "python3 scripts/zigux/check-phase7-argv-split-packet.py --self-test",
        "python3 scripts/zigux/check-phase7-argv-split-packet.py",
        "python3 scripts/zigux/check-phase7-rbtree-parity.py --self-test",
        "python3 scripts/zigux/check-phase7-rbtree-parity.py",
        "python3 scripts/zigux/check-phase7-build-wiring.py --self-test",
        "python3 scripts/zigux/check-phase7-build-wiring.py",
        "make -C zigux phase7-validate",
        "make -C zigux phase7-string-helpers-survey",
        "make -C zigux phase7-string-helpers-sample-boundary",
        "make -C zigux phase7-cmdline-survey",
        "make -C zigux phase7-argv-split-survey",
        "make -C zigux phase7-rbtree-survey",
        "make -C zigux phase7-test",
        "make -C zigux phase7",
        "`zigux/tests/phase7_rbtree.zig` still fails direct current-path reads",
        "`lib/string_helpers.zig` and `zigux/tests/phase7_string_helpers.zig`",
        "are back on `master`",
        "The older string-helpers missing-pair reminder is no longer the live blocker",
        "`Documentation/zigux/phase7-helper-lane-sequencing.md` remains the dedicated",
        "`zigux/tests/README.md` is also a shared-control reminder surface owned by",
    ],
    "Documentation/zigux/phase7-helper-lane-sequencing.md": [
        "PHASE7_SHARED_CONTROL_LANE=P7-Y05",
        "PHASE7_HELPER_SEQUENCING_LANE=P7-Y06",
        "PHASE7_SHARED_DOCS_ROOT_LANE=P7-Y08",
        "`string_helpers` is parked as a landed helper-local packet",
        "`rbtree` is parked in a helper-local reminder posture",
        "`P7-Y05` owns only shared validator, make-wrapper, build-route, tests-root, and shared reminder truthfulness.",
    ],
    "Documentation/zigux/phase7-string-helpers-slice.md": [
        "PHASE7_STATUS=starter_landed",
        "restored starter packet",
        "current `master` now carries both `lib/string_helpers.zig` and `zigux/tests/phase7_string_helpers.zig`",
    ],
    "samples/zigux/README.md": [
        "scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py",
        "scripts/zigux/check-phase7-build-wiring.py",
    ],
    "scripts/zigux/README.md": [
        "Documentation/zigux/phase7-make-wrapper-selftest-alignment.md",
        "scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py",
        "scripts/zigux/check-phase7-build-wiring.py",
        "make -C zigux phase7-validate",
    ],
    "zigux/tests/README.md": [
        "zigux/tests/phase7_build.zig",
        "zigux/tests/phase7_string_helpers_sample_boundary.zig",
        "zigux/tests/phase7_rbtree.zig",
    ],
    "zigux/tests/phase7_string_helpers_manifest.json": [
        "\"current_master_state\": \"restored_starter_packet\"",
        "\"lib/string_helpers.zig\"",
        "\"zigux/tests/phase7_string_helpers.zig\"",
    ],
    "zigux/Makefile": [
        "scripts/zigux/check-phase7-make-wrapper.py --self-test",
        "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase7-make-wrapper.py",
        "scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py --self-test",
        "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py",
        "scripts/zigux/check-phase7-build-wiring.py --self-test",
        "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase7-build-wiring.py",
        "scripts/zigux/check-phase7-argv-split-packet.py --self-test",
        "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase7-argv-split-packet.py",
        "scripts/zigux/check-phase7-rbtree-parity.py --self-test",
        "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase7-rbtree-parity.py",
    ],
}

EXACT_COUNT_MARKERS = {
    ".github/workflows/zigux-bootstrap.yml": {
        "make -C zigux phase7-validate": 1,
        "python3 scripts/zigux/check-phase7-make-wrapper.py": 0,
        "python3 scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py": 0,
        "python3 scripts/zigux/check-phase7-build-wiring.py": 0,
    },
    "zigux/Makefile": {
        "scripts/zigux/check-phase7-make-wrapper.py --self-test": 1,
        "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase7-make-wrapper.py": 1,
        "scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py --self-test": 1,
        "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py": 1,
        "scripts/zigux/check-phase7-build-wiring.py --self-test": 1,
        "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase7-build-wiring.py": 1,
    },
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


def collect_count_mismatches(root: Path) -> list[str]:
    mismatches: list[str] = []
    for rel, expected_counts in EXACT_COUNT_MARKERS.items():
        text = (root / rel).read_text(encoding="utf-8")
        for marker, expected in expected_counts.items():
            actual = text.count(marker)
            if actual != expected:
                mismatches.append(f"{rel}: expected {expected} occurrence(s) of {marker!r}, found {actual}")
    return mismatches


def validate(root: Path) -> tuple[list[str], list[str], list[str]]:
    missing_files = collect_missing_files(root)
    if missing_files:
        return missing_files, [], []
    return [], collect_missing_markers(root), collect_count_mismatches(root)


def write_fixture_root(tmp_root: Path) -> None:
    fixture_text = {rel: "\n".join(markers) + "\n" for rel, markers in REQUIRED_MARKERS.items()}
    for rel in REQUIRED_FILES:
        path = tmp_root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(fixture_text.get(rel, "# fixture\n"), encoding="utf-8")

    workflow_path = tmp_root / ".github/workflows/zigux-bootstrap.yml"
    workflow_path.write_text("make -C zigux phase7-validate\n", encoding="utf-8")


def expect_missing_marker(case: str, tmp_root: Path, marker: str) -> None:
    missing_files, missing_markers, count_mismatches = validate(tmp_root)
    assert missing_files == [], case
    assert count_mismatches == [], case
    assert missing_markers == [marker], case


def expect_missing_file(case: str, tmp_root: Path, rel: str) -> None:
    missing_files, missing_markers, count_mismatches = validate(tmp_root)
    assert missing_markers == [], case
    assert count_mismatches == [], case
    assert missing_files == [rel], case


def expect_count_mismatch(case: str, tmp_root: Path, mismatch: str) -> None:
    missing_files, missing_markers, count_mismatches = validate(tmp_root)
    assert missing_files == [], case
    assert missing_markers == [], case
    assert count_mismatches == [mismatch], case


def remove_marker(tmp_root: Path, rel: str, marker: str, case: str) -> None:
    path = tmp_root / rel
    text = path.read_text(encoding="utf-8")
    updated = text.replace(marker, "", 1)
    assert updated != text, case
    path.write_text(updated, encoding="utf-8")


def run_self_test() -> None:
    with tempfile.TemporaryDirectory(prefix="zigux_phase7_make_wrapper_alignment_") as tmp_dir_str:
        tmp_root = Path(tmp_dir_str)
        write_fixture_root(tmp_root)
        assert validate(tmp_root) == ([], [], [])

        (tmp_root / "scripts/zigux/check-phase7-build-wiring.py").unlink()
        expect_missing_file(
            "missing_build_wiring_checker",
            tmp_root,
            "scripts/zigux/check-phase7-build-wiring.py",
        )
        write_fixture_root(tmp_root)

        (tmp_root / "Documentation/zigux/phase7-helper-lane-sequencing.md").unlink()
        expect_missing_file(
            "missing_helper_lane_note",
            tmp_root,
            "Documentation/zigux/phase7-helper-lane-sequencing.md",
        )
        write_fixture_root(tmp_root)

        remove_marker(
            tmp_root,
            "Documentation/zigux/phase7-make-wrapper-selftest-alignment.md",
            "The older string-helpers missing-pair reminder is no longer the live blocker",
            "missing_live_blocker_note",
        )
        expect_missing_marker(
            "missing_live_blocker_note",
            tmp_root,
            "Documentation/zigux/phase7-make-wrapper-selftest-alignment.md: The older string-helpers missing-pair reminder is no longer the live blocker",
        )
        write_fixture_root(tmp_root)

        remove_marker(
            tmp_root,
            "Documentation/zigux/phase7-make-wrapper-selftest-alignment.md",
            "`zigux/tests/phase7_rbtree.zig` still fails direct current-path reads",
            "missing_rbtree_blocker_marker",
        )
        expect_missing_marker(
            "missing_rbtree_blocker_marker",
            tmp_root,
            "Documentation/zigux/phase7-make-wrapper-selftest-alignment.md: `zigux/tests/phase7_rbtree.zig` still fails direct current-path reads",
        )
        write_fixture_root(tmp_root)

        remove_marker(
            tmp_root,
            "Documentation/zigux/phase7-helper-lane-sequencing.md",
            "`string_helpers` is parked as a landed helper-local packet",
            "missing_string_helpers_lane_state",
        )
        expect_missing_marker(
            "missing_string_helpers_lane_state",
            tmp_root,
            "Documentation/zigux/phase7-helper-lane-sequencing.md: `string_helpers` is parked as a landed helper-local packet",
        )
        write_fixture_root(tmp_root)

        remove_marker(
            tmp_root,
            "Documentation/zigux/phase7-string-helpers-slice.md",
            "current `master` now carries both `lib/string_helpers.zig` and `zigux/tests/phase7_string_helpers.zig`",
            "missing_restored_pair_marker",
        )
        expect_missing_marker(
            "missing_restored_pair_marker",
            tmp_root,
            "Documentation/zigux/phase7-string-helpers-slice.md: current `master` now carries both `lib/string_helpers.zig` and `zigux/tests/phase7_string_helpers.zig`",
        )
        write_fixture_root(tmp_root)

        remove_marker(
            tmp_root,
            "zigux/tests/phase7_string_helpers_manifest.json",
            "\"current_master_state\": \"restored_starter_packet\"",
            "missing_manifest_state",
        )
        expect_missing_marker(
            "missing_manifest_state",
            tmp_root,
            "zigux/tests/phase7_string_helpers_manifest.json: \"current_master_state\": \"restored_starter_packet\"",
        )
        write_fixture_root(tmp_root)

        remove_marker(
            tmp_root,
            "scripts/zigux/README.md",
            "make -C zigux phase7-validate",
            "missing_scripts_phase7_validate_route",
        )
        expect_missing_marker(
            "missing_scripts_phase7_validate_route",
            tmp_root,
            "scripts/zigux/README.md: make -C zigux phase7-validate",
        )
        write_fixture_root(tmp_root)

        remove_marker(
            tmp_root,
            "zigux/Makefile",
            "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase7-build-wiring.py",
            "missing_makefile_build_wiring_hook",
        )
        assert validate(tmp_root) == (
            [],
            [
                "zigux/Makefile: cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase7-build-wiring.py",
            ],
            [
                "zigux/Makefile: expected 1 occurrence(s) of 'cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase7-build-wiring.py', found 0",
            ],
        ), "missing_makefile_build_wiring_hook"
        write_fixture_root(tmp_root)

        workflow_path = tmp_root / ".github/workflows/zigux-bootstrap.yml"
        workflow_path.write_text(
            workflow_path.read_text(encoding="utf-8") + "make -C zigux phase7-validate\n",
            encoding="utf-8",
        )
        expect_count_mismatch(
            "duplicate_workflow_phase7_validate",
            tmp_root,
            ".github/workflows/zigux-bootstrap.yml: expected 1 occurrence(s) of 'make -C zigux phase7-validate', found 2",
        )
        write_fixture_root(tmp_root)

        workflow_path = tmp_root / ".github/workflows/zigux-bootstrap.yml"
        workflow_path.write_text(
            workflow_path.read_text(encoding="utf-8") + "python3 scripts/zigux/check-phase7-build-wiring.py\n",
            encoding="utf-8",
        )
        expect_count_mismatch(
            "direct_workflow_build_wiring_hook",
            tmp_root,
            ".github/workflows/zigux-bootstrap.yml: expected 0 occurrence(s) of 'python3 scripts/zigux/check-phase7-build-wiring.py', found 1",
        )

    print("PHASE7_MAKE_WRAPPER_SELFTEST_ALIGNMENT=pass")
    print("PHASE7_MAKE_WRAPPER_SELFTEST_ALIGNMENT_CASE_COUNT=10")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the Phase 7 make-wrapper selftests still match the live shared-control packet."
    )
    parser.add_argument("--self-test", action="store_true", help="Run checker self-tests without reading repo files.")
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return 0

    missing_files, missing_markers, count_mismatches = validate(ROOT)
    if missing_files:
        print("PHASE7_MAKE_WRAPPER_SELFTEST_ALIGNMENT=fail")
        print("MISSING_PHASE7_MAKE_WRAPPER_SELFTEST_ALIGNMENT_FILES_START")
        for item in missing_files:
            print(item)
        print("MISSING_PHASE7_MAKE_WRAPPER_SELFTEST_ALIGNMENT_FILES_END")
        return 1

    if missing_markers:
        print("PHASE7_MAKE_WRAPPER_SELFTEST_ALIGNMENT=fail")
        print("MISSING_PHASE7_MAKE_WRAPPER_SELFTEST_ALIGNMENT_MARKERS_START")
        for item in missing_markers:
            print(item)
        print("MISSING_PHASE7_MAKE_WRAPPER_SELFTEST_ALIGNMENT_MARKERS_END")
        return 1

    if count_mismatches:
        print("PHASE7_MAKE_WRAPPER_SELFTEST_ALIGNMENT=fail")
        print("MISMATCHED_PHASE7_MAKE_WRAPPER_SELFTEST_ALIGNMENT_COUNTS_START")
        for item in count_mismatches:
            print(item)
        print("MISMATCHED_PHASE7_MAKE_WRAPPER_SELFTEST_ALIGNMENT_COUNTS_END")
        return 1

    print("PHASE7_MAKE_WRAPPER_SELFTEST_ALIGNMENT=pass")
    print(f"PHASE7_MAKE_WRAPPER_SELFTEST_ALIGNMENT_FILE_COUNT={len(REQUIRED_FILES)}")
    print(f"PHASE7_MAKE_WRAPPER_SELFTEST_ALIGNMENT_MARKER_COUNT={sum(len(markers) for markers in REQUIRED_MARKERS.values())}")
    print(
        "PHASE7_MAKE_WRAPPER_SELFTEST_ALIGNMENT_COUNT_RULE_COUNT="
        f"{sum(len(markers) for markers in EXACT_COUNT_MARKERS.values())}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
