#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


SELF_PATH = Path(__file__).resolve()
ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) >= 3 else SELF_PATH.parent

REQUIRED_FILES = [
    "Documentation/zigux/README.md",
    "Documentation/zigux/phase8-libbpf-segment-survey.md",
    "Documentation/zigux/phase8-tooling-lane-sequencing.md",
    "scripts/zigux/README.md",
    "zigux/Makefile",
    "zigux/tests/README.md",
    "zigux/tests/phase8_build.zig",
    "zigux/tests/phase8_cpu_mask.zig",
    "zigux/tests/phase8_cpu_mask_only_build.zig",
    "tools/lib/bpf/zigux_segments/cpu_mask.zig",
]

REQUIRED_MARKERS = {
    "Documentation/zigux/README.md": [
        "Phase 8 notes",
        "`zigux/tests/phase8_cpu_mask.zig`",
    ],
    "Documentation/zigux/phase8-libbpf-segment-survey.md": [
        "`zigux/tests/phase8_cpu_mask_only_build.zig`",
        "`make -C zigux phase8-cpu-mask-test`",
    ],
    "Documentation/zigux/phase8-tooling-lane-sequencing.md": [
        "`zigux/tests/phase8_cpu_mask_only_build.zig`",
        "`make -C zigux phase8-cpu-mask-test`",
    ],
    "scripts/zigux/README.md": [
        "Phase 8 flow",
        "`zigux/tests/phase8_cpu_mask.zig`",
        "`zigux/tests/phase8_cpu_mask_only_build.zig`",
        "`make -C zigux phase8-cpu-mask-test`",
    ],
    "zigux/Makefile": [
        "phase8-cpu-mask-test:",
        "$(ZIG) build test --build-file zigux/tests/phase8_cpu_mask_only_build.zig --summary all",
    ],
    "zigux/tests/README.md": [
        "keep the shared Phase 8 tooling packet wired through `zigux/tests/phase8_build.zig`",
        "`zigux/tests/phase8_cpu_mask.zig`",
    ],
    "zigux/tests/phase8_build.zig": [
        "../../tools/lib/bpf/zigux_segments/cpu_mask.zig",
        "\"phase8_cpu_mask.zig\"",
        "phase8-cpu-mask-tests",
    ],
    "zigux/tests/phase8_cpu_mask.zig": [
        "phase 8 cpu mask starter slice parses dense masks and counts possible CPUs",
        "countPossibleCpus(parsed.values)",
    ],
    "zigux/tests/phase8_cpu_mask_only_build.zig": [
        "../../tools/lib/bpf/zigux_segments/cpu_mask.zig",
        "\"phase8_cpu_mask.zig\"",
        "phase8-cpu-mask-tests",
    ],
    "tools/lib/bpf/zigux_segments/cpu_mask.zig": [
        "pub fn parseCpuMaskString",
        "pub fn parseCpuMaskFromReader",
        "pub fn countPossibleCpus",
    ],
}


def write_fixture_root(root: Path) -> None:
    for rel in REQUIRED_FILES:
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        text = "\n".join(REQUIRED_MARKERS.get(rel, ["# fixture"])) + "\n"
        path.write_text(text, encoding="utf-8")


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


def expect_missing_file(case: str, tmp_root: Path, rel: str) -> None:
    missing_files, missing_markers = validate(tmp_root)
    assert missing_files == [rel], case
    assert missing_markers == [], case


def expect_missing_marker(case: str, tmp_root: Path, expected: str) -> None:
    missing_files, missing_markers = validate(tmp_root)
    assert missing_files == [], case
    assert missing_markers == [expected], case


def mutate_file(tmp_root: Path, rel: str, old: str, new: str, case: str) -> None:
    path = tmp_root / rel
    original = path.read_text(encoding="utf-8")
    updated = original.replace(old, new, 1)
    assert updated != original, case
    path.write_text(updated, encoding="utf-8")


def run_self_test() -> None:
    missing_file_cases = [
        ("missing_docs_root_readme", "Documentation/zigux/README.md"),
        (
            "missing_libbpf_segment_survey",
            "Documentation/zigux/phase8-libbpf-segment-survey.md",
        ),
        (
            "missing_lane_sequencing_note",
            "Documentation/zigux/phase8-tooling-lane-sequencing.md",
        ),
        ("missing_scripts_root_readme", "scripts/zigux/README.md"),
        ("missing_makefile", "zigux/Makefile"),
        ("missing_tests_root_readme", "zigux/tests/README.md"),
        ("missing_cpu_mask_only_build", "zigux/tests/phase8_cpu_mask_only_build.zig"),
        ("missing_cpu_mask_helper", "tools/lib/bpf/zigux_segments/cpu_mask.zig"),
    ]

    marker_cases = [
        (
            "scripts_root_cpu_mask_route",
            "scripts/zigux/README.md",
            "`make -C zigux phase8-cpu-mask-test`",
            "`make -C zigux phase8-cpu-mask-smoke`",
            "scripts/zigux/README.md: `make -C zigux phase8-cpu-mask-test`",
        ),
        (
            "survey_cpu_mask_route",
            "Documentation/zigux/phase8-libbpf-segment-survey.md",
            "`make -C zigux phase8-cpu-mask-test`",
            "`make -C zigux phase8-cpu-mask-smoke`",
            "Documentation/zigux/phase8-libbpf-segment-survey.md: `make -C zigux phase8-cpu-mask-test`",
        ),
        (
            "lane_note_cpu_mask_route",
            "Documentation/zigux/phase8-tooling-lane-sequencing.md",
            "`make -C zigux phase8-cpu-mask-test`",
            "`make -C zigux phase8-cpu-mask-smoke`",
            "Documentation/zigux/phase8-tooling-lane-sequencing.md: `make -C zigux phase8-cpu-mask-test`",
        ),
        (
            "makefile_cpu_mask_target",
            "zigux/Makefile",
            "phase8-cpu-mask-test:",
            "phase8-cpu-mask-smoke:",
            "zigux/Makefile: phase8-cpu-mask-test:",
        ),
        (
            "build_shard_cpu_mask_module",
            "zigux/tests/phase8_cpu_mask_only_build.zig",
            "../../tools/lib/bpf/zigux_segments/cpu_mask.zig",
            "../../tools/lib/bpf/zigux_segments/cpu_mask_missing.zig",
            "zigux/tests/phase8_cpu_mask_only_build.zig: ../../tools/lib/bpf/zigux_segments/cpu_mask.zig",
        ),
        (
            "shared_build_cpu_mask_step",
            "zigux/tests/phase8_build.zig",
            "phase8-cpu-mask-tests",
            "phase8-cpu-mask-smoke",
            "zigux/tests/phase8_build.zig: phase8-cpu-mask-tests",
        ),
        (
            "cpu_mask_helper_entrypoint",
            "tools/lib/bpf/zigux_segments/cpu_mask.zig",
            "pub fn parseCpuMaskString",
            "fn parseCpuMaskString",
            "tools/lib/bpf/zigux_segments/cpu_mask.zig: pub fn parseCpuMaskString",
        ),
    ]

    with tempfile.TemporaryDirectory(prefix="zigux_phase8_cpu_mask_checker_") as tmp_dir_str:
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

    print("PHASE8_CPU_MASK_SHARD_READBACK_SELF_TEST=pass")
    print(
        "PHASE8_CPU_MASK_SHARD_READBACK_SELF_TEST_CASE_COUNT="
        f"{len(missing_file_cases) + len(marker_cases)}"
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the focused Phase 8 cpu-mask shard across shared tooling surfaces."
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run built-in checker coverage without reading repo files.",
    )
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return 0

    missing_files, missing_markers = validate(ROOT)

    if missing_files:
        print("PHASE8_CPU_MASK_SHARD_READBACK=fail")
        print("MISSING_PHASE8_CPU_MASK_FILES_START")
        for item in missing_files:
            print(item)
        print("MISSING_PHASE8_CPU_MASK_FILES_END")
        return 1

    if missing_markers:
        print("PHASE8_CPU_MASK_SHARD_READBACK=fail")
        print("MISSING_PHASE8_CPU_MASK_MARKERS_START")
        for item in missing_markers:
            print(item)
        print("MISSING_PHASE8_CPU_MASK_MARKERS_END")
        return 1

    print("PHASE8_CPU_MASK_SHARD_READBACK=pass")
    print(f"PHASE8_CPU_MASK_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(
        "PHASE8_CPU_MASK_REQUIRED_MARKER_COUNT="
        f"{sum(len(markers) for markers in REQUIRED_MARKERS.values())}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
