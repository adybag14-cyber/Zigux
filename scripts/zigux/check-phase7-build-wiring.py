#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

SEQUENCING_PATH = Path("Documentation/zigux/phase7-helper-lane-sequencing.md")
MAKEFILE_PATH = Path("zigux/Makefile")

SEQUENCING_MARKERS = [
    "shared control-surface packet, lane `P7-Y05`:",
    "`samples/zigux/README.md`",
    "`scripts/zigux/README.md`",
    "`zigux/tests/README.md`",
    "`zigux/Makefile`",
    "`zigux/tests/phase7_build.zig`",
    "`scripts/zigux/validate-phase7.py`",
    "`P7-Y05` owns only shared validator, scripts-root, sample-root, tests-root, make-wrapper, and build-route truthfulness.",
    "`scripts/zigux/validate-phase7.py` and `zigux/tests/phase7_build.zig`, so `P7-Y05` should treat the shared wrapper stack as parked reminder vocabulary until those files rematerialize.",
]

FORBIDDEN_MAKEFILE_MARKERS = [
    "phase7-validate",
    "phase7-string-helpers-test",
    "phase7-string-helpers-survey",
    "phase7-string-helpers-sample-boundary",
    "phase7-cmdline-test",
    "phase7-cmdline-survey",
    "phase7-argv-split-test",
    "phase7-argv-split-survey",
    "phase7-rbtree-test",
    "phase7-rbtree-survey",
    "phase7-test",
    "phase7:",
]

REQUIRED_FILES = (SEQUENCING_PATH, MAKEFILE_PATH)
REQUIRED_PRESENT_MARKERS = {
    SEQUENCING_PATH: SEQUENCING_MARKERS,
}
FORBIDDEN_MARKERS = {
    MAKEFILE_PATH: FORBIDDEN_MAKEFILE_MARKERS,
}

FIXTURE_TEXTS = {
    SEQUENCING_PATH: "\n".join(SEQUENCING_MARKERS) + "\n",
    MAKEFILE_PATH: "\n".join(
        [
            "PYTHON ?= python3",
            "ZIG ?= zig",
            "PHASE2_SCRIPT_ROOT := ../scripts/zigux",
            "PHASE3_SCRIPT_ROOT := ../scripts/zigux",
            ".PHONY: phase2 phase3",
            "phase2:",
            "\t$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-zig-toolchain.py --policy-only",
            "phase3:",
            "\tcd .. && $(PYTHON) scripts/zigux/validate-phase3-low-level-wrapper-survey.py",
        ]
    )
    + "\n",
}


def _read_text(root: Path, rel: Path) -> str:
    return (root / rel).read_text(encoding="utf-8")


def validate(root: Path) -> tuple[list[str], list[str], list[str]]:
    missing_files: list[str] = []
    missing_markers: list[str] = []
    unexpected_markers: list[str] = []

    for rel in REQUIRED_FILES:
        if not (root / rel).is_file():
            missing_files.append(str(rel))

    if missing_files:
        return missing_files, missing_markers, unexpected_markers

    for rel, markers in REQUIRED_PRESENT_MARKERS.items():
        text = _read_text(root, rel)
        for marker in markers:
            if marker not in text:
                missing_markers.append(f"{rel}: {marker}")

    for rel, markers in FORBIDDEN_MARKERS.items():
        text = _read_text(root, rel)
        for marker in markers:
            if marker in text:
                unexpected_markers.append(f"{rel}: {marker}")

    return missing_files, missing_markers, unexpected_markers


def _write_fixture_root(root: Path) -> None:
    for rel, text in FIXTURE_TEXTS.items():
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")


def _mutate_text(root: Path, rel: Path, old: str, new: str, case: str) -> None:
    path = root / rel
    text = path.read_text(encoding="utf-8")
    updated = text.replace(old, new, 1)
    assert updated != text, case
    path.write_text(updated, encoding="utf-8")


def _append_text(root: Path, rel: Path, extra: str) -> None:
    path = root / rel
    path.write_text(path.read_text(encoding="utf-8") + extra, encoding="utf-8")


def run_self_test() -> None:
    missing_file_cases = [(f"missing_{rel.name}", rel) for rel in REQUIRED_FILES]
    marker_cases = [
        (
            "lane_heading_drift",
            SEQUENCING_PATH,
            "shared control-surface packet, lane `P7-Y05`:",
            "shared control-surface packet, lane `P7-Y06`:",
        ),
        (
            "shared_truthfulness_scope_drift",
            SEQUENCING_PATH,
            "`P7-Y05` owns only shared validator, scripts-root, sample-root, tests-root, make-wrapper, and build-route truthfulness.",
            "`P7-Y05` owns helper-local cmdline proof and shared build truthfulness.",
        ),
        (
            "missing_route_posture_drift",
            SEQUENCING_PATH,
            "`scripts/zigux/validate-phase7.py` and `zigux/tests/phase7_build.zig`, so `P7-Y05` should treat the shared wrapper stack as parked reminder vocabulary until those files rematerialize.",
            "`scripts/zigux/validate-phase7.py` and `zigux/tests/phase7_build.zig`, so `P7-Y05` can now treat the shared wrapper stack as landed build proof.",
        ),
    ]
    unexpected_marker_cases = [
        ("phase7_validate_route_returned", "phase7-validate:\n\tpython3 scripts/zigux/validate-phase7.py\n"),
        ("phase7_cmdline_route_returned", "phase7-cmdline-survey:\n\tzig test zigux/tests/phase7_cmdline_survey.zig\n"),
        ("phase7_bundle_route_returned", "phase7: phase7-validate phase7-test\n"),
    ]

    with tempfile.TemporaryDirectory(prefix="zigux_phase7_build_wiring_") as tmp_dir_str:
        root = Path(tmp_dir_str)
        _write_fixture_root(root)
        assert validate(root) == ([], [], [])

        for case, rel in missing_file_cases:
            (root / rel).unlink()
            assert validate(root) == ([str(rel)], [], []), case
            _write_fixture_root(root)

        for case, rel, old, new in marker_cases:
            _mutate_text(root, rel, old, new, case)
            assert validate(root) == ([], [f"{rel}: {old}"], []), case
            _write_fixture_root(root)

        for case, extra in unexpected_marker_cases:
            _append_text(root, MAKEFILE_PATH, extra)
            expected = []
            for marker in FORBIDDEN_MAKEFILE_MARKERS:
                if marker in extra:
                    expected.append(f"{MAKEFILE_PATH}: {marker}")
            assert validate(root) == ([], [], expected), case
            _write_fixture_root(root)

    print("PHASE7_BUILD_WIRING=pass")
    print(
        "PHASE7_BUILD_WIRING_CASE_COUNT=%d"
        % (len(missing_file_cases) + len(marker_cases) + len(unexpected_marker_cases))
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Check that the shipped Phase 7 shared control packet stays parked on "
            "current repo reality until Phase 7 build routes rematerialize."
        )
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run checker self-tests without reading repo files.",
    )
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return 0

    missing_files, missing_markers, unexpected_markers = validate(Path("."))
    if missing_files:
        print("PHASE7_BUILD_WIRING=fail")
        print("MISSING_PHASE7_BUILD_WIRING_FILES_START")
        for item in missing_files:
            print(item)
        print("MISSING_PHASE7_BUILD_WIRING_FILES_END")
        return 1

    if missing_markers:
        print("PHASE7_BUILD_WIRING=fail")
        print("MISSING_PHASE7_BUILD_WIRING_MARKERS_START")
        for item in missing_markers:
            print(item)
        print("MISSING_PHASE7_BUILD_WIRING_MARKERS_END")
        return 1

    if unexpected_markers:
        print("PHASE7_BUILD_WIRING=fail")
        print("UNEXPECTED_PHASE7_BUILD_WIRING_MARKERS_START")
        for item in unexpected_markers:
            print(item)
        print("UNEXPECTED_PHASE7_BUILD_WIRING_MARKERS_END")
        return 1

    print("PHASE7_BUILD_WIRING=pass")
    print(f"PHASE7_BUILD_WIRING_FILE_COUNT={len(REQUIRED_FILES)}")
    print(
        "PHASE7_BUILD_WIRING_PRESENT_MARKER_COUNT=%d"
        % sum(len(markers) for markers in REQUIRED_PRESENT_MARKERS.values())
    )
    print(
        "PHASE7_BUILD_WIRING_FORBIDDEN_MARKER_COUNT=%d"
        % sum(len(markers) for markers in FORBIDDEN_MARKERS.values())
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
