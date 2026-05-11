#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

SELF_PATH = Path(__file__).resolve()
ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) > 2 else SELF_PATH.parent

REQUIRED_FILES = [
    "Documentation/zigux/phase8-libbpf-segment-survey.md",
    "Documentation/zigux/phase8-tooling-lane-sequencing.md",
    "scripts/zigux/README.md",
    ".github/workflows/zigux-bootstrap.yml",
    "zigux/tests/README.md",
    "zigux/Makefile",
]

REQUIRED_MARKERS = {
    "Documentation/zigux/phase8-libbpf-segment-survey.md": [
        "make -C zigux phase8-file-path-handle-bridge-test",
        "make -C zigux phase8-libbpf-segments-test",
        "make -C zigux phase8-perf-buffer-poll-test",
        "zig build test --build-file zigux/tests/phase8_file_path_handle_bridge_only_build.zig --summary all",
        "zig build test --build-file zigux/tests/phase8_libbpf_segments_only_build.zig --summary all",
        "zig build test --build-file zigux/tests/phase8_perf_buffer_poll_only_build.zig --summary all",
    ],
    "Documentation/zigux/phase8-tooling-lane-sequencing.md": [
        "make -C zigux phase8-cpu-mask-test",
        "make -C zigux phase8-file-path-handle-bridge-test",
        "make -C zigux phase8-libbpf-segments-test",
        "make -C zigux phase8-perf-buffer-poll-test",
        "make -C zigux phase8",
    ],
    "scripts/zigux/README.md": [
        "Phase 8 flow",
        "make -C zigux phase8-help-test",
        "make -C zigux phase8-help-kallsyms-test",
        "make -C zigux phase8-kallsyms-test",
        "make -C zigux phase8-cpu-mask-test",
        "make -C zigux phase8-file-path-handle-bridge-test",
        "make -C zigux phase8-libbpf-segments-test",
        "make -C zigux phase8-perf-buffer-poll-test",
        "make -C zigux phase8",
    ],
    ".github/workflows/zigux-bootstrap.yml": [
        "Run focused Phase 8 libbpf shard tests",
        "make -C zigux phase8-file-path-handle-bridge-test",
        "make -C zigux phase8-libbpf-segments-test",
        "make -C zigux phase8-perf-buffer-poll-test",
    ],
    "zigux/tests/README.md": [
        "make -C zigux phase8-cpu-mask-test",
        "make -C zigux phase8-file-path-handle-bridge-test",
        "make -C zigux phase8-libbpf-segments-test",
        "make -C zigux phase8-perf-buffer-poll-test",
        "make -C zigux phase8",
    ],
    "zigux/Makefile": [
        "phase8-file-path-handle-bridge-test:",
        "phase8-libbpf-segments-test:",
        "phase8-perf-buffer-poll-test:",
        "phase8: phase8-validate phase8-test phase8-cpu-mask-test",
    ],
}


def collect_missing_files(root: Path) -> list[str]:
    return [rel for rel in REQUIRED_FILES if not (root / rel).exists()]


def collect_missing_markers(root: Path) -> list[str]:
    missing: list[str] = []
    for rel, markers in REQUIRED_MARKERS.items():
        path = root / rel
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        for marker in markers:
            if marker not in text:
                missing.append(f"{rel}: {marker}")
    return missing


def validate(root: Path) -> tuple[list[str], list[str]]:
    return collect_missing_files(root), collect_missing_markers(root)


def fixture_text(rel: str) -> str:
    markers = REQUIRED_MARKERS.get(rel)
    if markers is None:
        return "# fixture\n"
    return "\n".join(markers) + "\n"


def write_fixture_root(root: Path) -> None:
    for rel in REQUIRED_FILES:
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(fixture_text(rel), encoding="utf-8")


def expect_missing_file(case: str, tmp_root: Path, rel: str) -> None:
    missing_files, missing_markers = validate(tmp_root)
    assert missing_markers == [], case
    assert missing_files == [rel], case


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
        ("missing_survey", "Documentation/zigux/phase8-libbpf-segment-survey.md"),
        ("missing_lane_note", "Documentation/zigux/phase8-tooling-lane-sequencing.md"),
        ("missing_scripts_readme", "scripts/zigux/README.md"),
        ("missing_workflow", ".github/workflows/zigux-bootstrap.yml"),
        ("missing_tests_readme", "zigux/tests/README.md"),
        ("missing_makefile", "zigux/Makefile"),
    ]
    marker_cases = [
        (
            "survey_route",
            "Documentation/zigux/phase8-libbpf-segment-survey.md",
            "make -C zigux phase8-libbpf-segments-test",
            "make -C zigux phase8-libbpf-survey-test",
            "Documentation/zigux/phase8-libbpf-segment-survey.md: make -C zigux phase8-libbpf-segments-test",
        ),
        (
            "lane_note_perf_route",
            "Documentation/zigux/phase8-tooling-lane-sequencing.md",
            "make -C zigux phase8-perf-buffer-poll-test",
            "make -C zigux phase8-poll-test",
            "Documentation/zigux/phase8-tooling-lane-sequencing.md: make -C zigux phase8-perf-buffer-poll-test",
        ),
        (
            "scripts_readme_segments_route",
            "scripts/zigux/README.md",
            "make -C zigux phase8-libbpf-segments-test",
            "make -C zigux phase8-libbpf-review-test",
            "scripts/zigux/README.md: make -C zigux phase8-libbpf-segments-test",
        ),
        (
            "workflow_libbpf_step",
            ".github/workflows/zigux-bootstrap.yml",
            "Run focused Phase 8 libbpf shard tests",
            "Run focused Phase 8 libbpf tests",
            ".github/workflows/zigux-bootstrap.yml: Run focused Phase 8 libbpf shard tests",
        ),
        (
            "tests_readme_bridge_route",
            "zigux/tests/README.md",
            "make -C zigux phase8-file-path-handle-bridge-test",
            "make -C zigux phase8-handle-bridge-test",
            "zigux/tests/README.md: make -C zigux phase8-file-path-handle-bridge-test",
        ),
        (
            "makefile_phase8_route",
            "zigux/Makefile",
            "phase8: phase8-validate phase8-test phase8-cpu-mask-test",
            "phase8: phase8-validate phase8-test",
            "zigux/Makefile: phase8: phase8-validate phase8-test phase8-cpu-mask-test",
        ),
    ]

    with tempfile.TemporaryDirectory(prefix="zigux_phase8_libbpf_routes_") as tmp_dir_str:
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

    print("PHASE8_LIBBPF_SHARD_ROUTES_SELF_TEST=pass")
    print(
        "PHASE8_LIBBPF_SHARD_ROUTES_SELF_TEST_CASE_COUNT="
        f"{len(missing_file_cases) + len(marker_cases)}"
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the current Phase 8 libbpf shard route packet."
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run checker self-test cases without reading repo files.",
    )
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return 0

    missing_files, missing_markers = validate(ROOT)
    if missing_files:
        print("PHASE8_LIBBPF_SHARD_ROUTES=fail")
        print("MISSING_PHASE8_LIBBPF_SHARD_ROUTE_FILES_START")
        for item in missing_files:
            print(item)
        print("MISSING_PHASE8_LIBBPF_SHARD_ROUTE_FILES_END")
        return 1
    if missing_markers:
        print("PHASE8_LIBBPF_SHARD_ROUTES=fail")
        print("MISSING_PHASE8_LIBBPF_SHARD_ROUTE_MARKERS_START")
        for item in missing_markers:
            print(item)
        print("MISSING_PHASE8_LIBBPF_SHARD_ROUTE_MARKERS_END")
        return 1

    print("PHASE8_LIBBPF_SHARD_ROUTES=pass")
    print(f"PHASE8_LIBBPF_SHARD_ROUTE_FILE_COUNT={len(REQUIRED_FILES)}")
    print(
        "PHASE8_LIBBPF_SHARD_ROUTE_MARKER_COUNT="
        f"{sum(len(markers) for markers in REQUIRED_MARKERS.values())}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
