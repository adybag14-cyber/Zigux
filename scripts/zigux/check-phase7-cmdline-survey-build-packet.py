#!/usr/bin/env python3
"""Guard the bounded Phase 7 cmdline survey-build helper-local packet."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

SEQUENCING_PATH = Path("Documentation/zigux/phase7-helper-lane-sequencing.md")
SLICE_PATH = Path("Documentation/zigux/phase7-cmdline-slice.md")
MANIFEST_PATH = Path("zigux/tests/phase7_cmdline_manifest.json")
SURVEY_BUILD_PATH = Path("zigux/tests/phase7_cmdline_survey_build.zig")
SAMPLES_README_PATH = Path("samples/zigux/README.md")

EXPECTED_REVIEW_SURFACE = "zigux/tests/phase7_cmdline_survey_build.zig"
EXPECTED_LANE_KEY = "P7-L08"
EXPECTED_PHASE = "Phase 7"
EXPECTED_ANCHOR = "lib/cmdline.c"
EXPECTED_STATE = "helper_slice_test_survey_manifest_checker_anchor"
EXPECTED_NEXT_STEP = (
    "Keep same-lane follow-through limited to the returned helper-local "
    "survey-manifest-checker truthfulness packet or one bounded parsing replay proof "
    "while shared-control routes stay parked outside this helper-local lane."
)

REQUIRED_FILES = [
    SEQUENCING_PATH,
    SLICE_PATH,
    MANIFEST_PATH,
    SURVEY_BUILD_PATH,
    SAMPLES_README_PATH,
]

REQUIRED_MARKERS = {
    SEQUENCING_PATH: [
        "- `zigux/tests/phase7_cmdline_survey.zig`",
        "- `zigux/tests/phase7_cmdline_manifest.json`",
        "- `scripts/zigux/check-phase7-cmdline-packet.py`",
        "cmdline-local review-noise, survey-checker-manifest drift, and no-sample-boundary upkeep should stay inside the returned cmdline packet",
    ],
    SLICE_PATH: [
        "`PHASE7_LANE_KEY=P7-L08`",
        "`zigux/tests/phase7_cmdline_survey_build.zig`",
        "`zig build phase7-cmdline-survey --build-file zigux/tests/phase7_cmdline_survey_build.zig`",
        "Keep same-lane follow-through limited to the returned helper-local survey-manifest-checker truthfulness packet or one bounded parsing replay proof.",
    ],
    SURVEY_BUILD_PATH: [
        '.root_source_file = b.path("phase7_cmdline_survey.zig")',
        '.name = "phase7-cmdline-survey"',
        '"phase7-cmdline-survey"',
        '"Run the Phase 7 cmdline survey anchor from the shared tests root"',
        "step.dependOn(&run.step);",
    ],
    SAMPLES_README_PATH: [
        "Current `master` still ships no standalone Phase 5 sample-root files here for:",
        "* `*cmdline*`",
    ],
}

COUNTED_MARKERS = {
    SURVEY_BUILD_PATH: [
        ('"phase7-cmdline-survey"', 2),
    ],
}

SELF_TEST_CASE_COUNT = 10


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def collect_missing_files(root: Path) -> list[str]:
    return [rel.as_posix() for rel in REQUIRED_FILES if not (root / rel).exists()]


def collect_missing_markers(root: Path) -> list[str]:
    missing: list[str] = []
    for rel, markers in REQUIRED_MARKERS.items():
        text = read_text(root / rel)
        for marker in markers:
            if marker not in text:
                missing.append(f"{rel.as_posix()}: {marker}")
    return missing


def collect_mismatched_counts(root: Path) -> list[str]:
    mismatches: list[str] = []
    for rel, markers in COUNTED_MARKERS.items():
        text = read_text(root / rel)
        for marker, expected in markers:
            actual = text.count(marker)
            if actual != expected:
                mismatches.append(
                    f"{rel.as_posix()}: expected {expected} occurrence(s) of {marker!r}, found {actual}"
                )
    return mismatches


def validate_manifest(root: Path) -> list[str]:
    manifest = json.loads(read_text(root / MANIFEST_PATH))
    issues: list[str] = []
    if manifest.get("lane_key") != EXPECTED_LANE_KEY:
        issues.append("zigux/tests/phase7_cmdline_manifest.json: lane_key")
    if manifest.get("phase") != EXPECTED_PHASE:
        issues.append("zigux/tests/phase7_cmdline_manifest.json: phase")
    if manifest.get("anchor") != EXPECTED_ANCHOR:
        issues.append("zigux/tests/phase7_cmdline_manifest.json: anchor")
    if manifest.get("current_master_state") != EXPECTED_STATE:
        issues.append("zigux/tests/phase7_cmdline_manifest.json: current_master_state")
    if manifest.get("next_bounded_step") != EXPECTED_NEXT_STEP:
        issues.append("zigux/tests/phase7_cmdline_manifest.json: next_bounded_step")
    review_surfaces = manifest.get("review_surfaces")
    if not isinstance(review_surfaces, list) or EXPECTED_REVIEW_SURFACE not in review_surfaces:
        issues.append("zigux/tests/phase7_cmdline_manifest.json: review_surfaces")
    if manifest.get("missing_paths") != []:
        issues.append("zigux/tests/phase7_cmdline_manifest.json: missing_paths")
    ownership_focus = manifest.get("ownership_focus")
    if not isinstance(ownership_focus, list) or not any(
        "zig build phase7-cmdline-survey --build-file zigux/tests/phase7_cmdline_survey_build.zig"
        in item
        for item in ownership_focus
    ):
        issues.append("zigux/tests/phase7_cmdline_manifest.json: ownership_focus")
    return issues


def validate(root: Path) -> tuple[list[str], list[str], list[str]]:
    missing_files = collect_missing_files(root)
    if missing_files:
        return missing_files, [], []
    manifest_issues = validate_manifest(root)
    missing_markers = collect_missing_markers(root)
    missing_markers.extend(manifest_issues)
    return missing_files, missing_markers, collect_mismatched_counts(root)


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def write_fixture_root(root: Path) -> None:
    write(
        root / SEQUENCING_PATH,
        "\n".join(REQUIRED_MARKERS[SEQUENCING_PATH]) + "\n",
    )
    write(
        root / SLICE_PATH,
        "\n".join(REQUIRED_MARKERS[SLICE_PATH]) + "\n",
    )
    write(
        root / MANIFEST_PATH,
        json.dumps(
            {
                "lane_key": EXPECTED_LANE_KEY,
                "phase": EXPECTED_PHASE,
                "verified_on_utc": "2026-05-27T18:35:01Z",
                "anchor": EXPECTED_ANCHOR,
                "current_master_state": EXPECTED_STATE,
                "review_surfaces": [
                    "Documentation/zigux/phase7-helper-lane-sequencing.md",
                    "Documentation/zigux/phase7-cmdline-slice.md",
                    "lib/cmdline.zig",
                    "zigux/tests/phase7_cmdline.zig",
                    "zigux/tests/phase7_cmdline_survey.zig",
                    "zigux/tests/phase7_cmdline_manifest.json",
                    EXPECTED_REVIEW_SURFACE,
                    "scripts/zigux/check-phase7-cmdline-packet.py",
                    "samples/zigux/README.md",
                ],
                "covered_helpers": [
                    "parseOptionStr",
                    "parse_option_str",
                    "getOption",
                    "get_option",
                    "getOptions",
                    "get_options",
                    "nextArg",
                    "next_arg",
                    "memparse",
                ],
                "missing_paths": [],
                "ownership_focus": [
                    "the dedicated `zig build phase7-cmdline-survey --build-file zigux/tests/phase7_cmdline_survey_build.zig` route keeps this helper-local survey replay runnable without widening into shared Phase 7 tests-root ownership",
                ],
                "next_bounded_step": EXPECTED_NEXT_STEP,
            },
            indent=2,
        )
        + "\n",
    )
    write(
        root / SURVEY_BUILD_PATH,
        "\n".join(REQUIRED_MARKERS[SURVEY_BUILD_PATH]) + "\n",
    )
    write(
        root / SAMPLES_README_PATH,
        "\n".join(REQUIRED_MARKERS[SAMPLES_README_PATH]) + "\n",
    )


def expect_missing_file(case: str, root: Path, rel: str) -> int:
    missing_files, missing_markers, mismatched_counts = validate(root)
    assert missing_markers == [], case
    assert mismatched_counts == [], case
    assert missing_files == [rel], case
    return 1


def expect_missing_marker(case: str, root: Path, marker: str) -> int:
    missing_files, missing_markers, mismatched_counts = validate(root)
    assert missing_files == [], case
    assert mismatched_counts == [], case
    assert missing_markers == [marker], case
    return 1


def expect_mismatched_count(case: str, root: Path, mismatch: str) -> int:
    missing_files, missing_markers, mismatched_counts = validate(root)
    assert missing_files == [], case
    assert missing_markers == [], case
    assert mismatched_counts == [mismatch], case
    return 1


def run_self_test() -> None:
    cases_run = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase7_cmdline_survey_build_") as tmp_dir:
        root = Path(tmp_dir)
        write_fixture_root(root)
        assert validate(root) == ([], [], [])

        (root / SURVEY_BUILD_PATH).unlink()
        cases_run += expect_missing_file(
            "missing_survey_build",
            root,
            "zigux/tests/phase7_cmdline_survey_build.zig",
        )

    with tempfile.TemporaryDirectory(prefix="zigux_phase7_cmdline_survey_build_") as tmp_dir:
        root = Path(tmp_dir)
        write_fixture_root(root)
        text = read_text(root / SLICE_PATH).replace(EXPECTED_REVIEW_SURFACE, "", 1)
        write(root / SLICE_PATH, text)
        cases_run += expect_missing_marker(
            "missing_slice_marker",
            root,
            "Documentation/zigux/phase7-cmdline-slice.md: `zigux/tests/phase7_cmdline_survey_build.zig`",
        )

    with tempfile.TemporaryDirectory(prefix="zigux_phase7_cmdline_survey_build_") as tmp_dir:
        root = Path(tmp_dir)
        write_fixture_root(root)
        manifest = json.loads(read_text(root / MANIFEST_PATH))
        manifest["review_surfaces"].remove(EXPECTED_REVIEW_SURFACE)
        write(root / MANIFEST_PATH, json.dumps(manifest, indent=2) + "\n")
        cases_run += expect_missing_marker(
            "missing_manifest_surface",
            root,
            "zigux/tests/phase7_cmdline_manifest.json: review_surfaces",
        )

    with tempfile.TemporaryDirectory(prefix="zigux_phase7_cmdline_survey_build_") as tmp_dir:
        root = Path(tmp_dir)
        write_fixture_root(root)
        text = read_text(root / SURVEY_BUILD_PATH).replace("step.dependOn(&run.step);", "", 1)
        write(root / SURVEY_BUILD_PATH, text)
        cases_run += expect_missing_marker(
            "missing_build_dependency",
            root,
            "zigux/tests/phase7_cmdline_survey_build.zig: step.dependOn(&run.step);",
        )

    with tempfile.TemporaryDirectory(prefix="zigux_phase7_cmdline_survey_build_") as tmp_dir:
        root = Path(tmp_dir)
        write_fixture_root(root)
        text = read_text(root / SURVEY_BUILD_PATH) + '"phase7-cmdline-survey"\n'
        write(root / SURVEY_BUILD_PATH, text)
        cases_run += expect_mismatched_count(
            "duplicate_step_name",
            root,
            "zigux/tests/phase7_cmdline_survey_build.zig: expected 2 occurrence(s) of '\"phase7-cmdline-survey\"', found 3",
        )

    with tempfile.TemporaryDirectory(prefix="zigux_phase7_cmdline_survey_build_") as tmp_dir:
        root = Path(tmp_dir)
        write_fixture_root(root)
        text = read_text(root / SAMPLES_README_PATH).replace("* `*cmdline*`", "* `cmdline*`", 1)
        write(root / SAMPLES_README_PATH, text)
        cases_run += expect_missing_marker(
            "missing_cmdline_boundary",
            root,
            "samples/zigux/README.md: * `*cmdline*`",
        )

    with tempfile.TemporaryDirectory(prefix="zigux_phase7_cmdline_survey_build_") as tmp_dir:
        root = Path(tmp_dir)
        write_fixture_root(root)
        manifest = json.loads(read_text(root / MANIFEST_PATH))
        manifest["ownership_focus"] = []
        write(root / MANIFEST_PATH, json.dumps(manifest, indent=2) + "\n")
        cases_run += expect_missing_marker(
            "missing_manifest_ownership_focus",
            root,
            "zigux/tests/phase7_cmdline_manifest.json: ownership_focus",
        )

    with tempfile.TemporaryDirectory(prefix="zigux_phase7_cmdline_survey_build_") as tmp_dir:
        root = Path(tmp_dir)
        write_fixture_root(root)
        manifest = json.loads(read_text(root / MANIFEST_PATH))
        manifest["next_bounded_step"] = "wrong"
        write(root / MANIFEST_PATH, json.dumps(manifest, indent=2) + "\n")
        cases_run += expect_missing_marker(
            "wrong_next_step",
            root,
            "zigux/tests/phase7_cmdline_manifest.json: next_bounded_step",
        )

    with tempfile.TemporaryDirectory(prefix="zigux_phase7_cmdline_survey_build_") as tmp_dir:
        root = Path(tmp_dir)
        write_fixture_root(root)
        text = read_text(root / SLICE_PATH).replace(
            "`zig build phase7-cmdline-survey --build-file zigux/tests/phase7_cmdline_survey_build.zig`",
            "",
            1,
        )
        write(root / SLICE_PATH, text)
        cases_run += expect_missing_marker(
            "missing_replay_route",
            root,
            "Documentation/zigux/phase7-cmdline-slice.md: `zig build phase7-cmdline-survey --build-file zigux/tests/phase7_cmdline_survey_build.zig`",
        )

    with tempfile.TemporaryDirectory(prefix="zigux_phase7_cmdline_survey_build_") as tmp_dir:
        root = Path(tmp_dir)
        write_fixture_root(root)
        manifest = json.loads(read_text(root / MANIFEST_PATH))
        manifest["missing_paths"] = ["zigux/tests/phase7_cmdline_survey_build.zig"]
        write(root / MANIFEST_PATH, json.dumps(manifest, indent=2) + "\n")
        cases_run += expect_missing_marker(
            "unexpected_missing_paths",
            root,
            "zigux/tests/phase7_cmdline_manifest.json: missing_paths",
        )

    assert cases_run == SELF_TEST_CASE_COUNT, (cases_run, SELF_TEST_CASE_COUNT)
    print("PHASE7_CMDLINE_SURVEY_BUILD_PACKET_SELF_TEST=pass")
    print(f"PHASE7_CMDLINE_SURVEY_BUILD_PACKET_SELF_TEST_CASE_COUNT={cases_run}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate the Phase 7 cmdline survey-build helper-local packet."
    )
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--write-sample-root", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.write_sample_root is not None:
        write_fixture_root(args.write_sample_root)
        return 0
    if args.self_test:
        run_self_test()
        return 0

    missing_files, missing_markers, mismatched_counts = validate(args.root)
    if missing_files or missing_markers or mismatched_counts:
        print("PHASE7_CMDLINE_SURVEY_BUILD_PACKET=fail")
        if missing_files:
            print("MISSING_PHASE7_CMDLINE_SURVEY_BUILD_FILES_START")
            for rel in missing_files:
                print(rel)
            print("MISSING_PHASE7_CMDLINE_SURVEY_BUILD_FILES_END")
        if missing_markers:
            print("MISSING_PHASE7_CMDLINE_SURVEY_BUILD_MARKERS_START")
            for marker in missing_markers:
                print(marker)
            print("MISSING_PHASE7_CMDLINE_SURVEY_BUILD_MARKERS_END")
        if mismatched_counts:
            print("MISMATCHED_PHASE7_CMDLINE_SURVEY_BUILD_COUNTS_START")
            for mismatch in mismatched_counts:
                print(mismatch)
            print("MISMATCHED_PHASE7_CMDLINE_SURVEY_BUILD_COUNTS_END")
        return 1

    print("PHASE7_CMDLINE_SURVEY_BUILD_PACKET=pass")
    print("PHASE7_CMDLINE_SURVEY_BUILD_REVIEW_SURFACE_COUNT=1")
    print("PHASE7_CMDLINE_SURVEY_BUILD_BOUNDARY_COUNT=1")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
