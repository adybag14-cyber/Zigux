#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


SELF_PATH = Path(__file__).resolve()
ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) >= 3 else SELF_PATH.parent

REQUIRED_FILES = [
    "Documentation/zigux/phase8-libbpf-segment-survey.md",
    "Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md",
    "Documentation/zigux/phase8-perf-buffer-poll-slice.md",
    "zigux/tests/phase8_libbpf_segments.zig",
]

REQUIRED_MARKERS = {
    "Documentation/zigux/phase8-libbpf-segment-survey.md": [
        "perf-buffer-online-cpu-routing",
        "standalone timer or clockevent helper behavior",
    ],
    "Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md": [
        "perf_buffer__poll(timeout_ms)",
        "standalone timer or clockevent helper behavior",
        "poll-loop ownership beyond the already-landed bounded `perf_buffer__poll(timeout_ms)` helper packet",
    ],
    "Documentation/zigux/phase8-perf-buffer-poll-slice.md": [
        "no standalone timer helper",
        "no standalone clockevent helper",
        "broader perf-buffer-online-cpu-routing parity",
    ],
    "zigux/tests/phase8_libbpf_segments.zig": [
        "phase 8 libbpf survey note stays aligned with the landed helper packet",
        "tools/lib/bpf/zigux_segments/perf_buffer_poll.zig",
        "Documentation/zigux/phase8-perf-buffer-poll-slice.md",
        "standalone timer or clockevent helper behavior",
    ],
}

UNEXPECTED_FILES = [
    "tools/lib/bpf/zigux_segments/timer.zig",
    "tools/lib/bpf/zigux_segments/clockevent.zig",
    "zigux/tests/phase8_timer.zig",
    "zigux/tests/phase8_clockevent.zig",
    "Documentation/zigux/phase8-timer-slice.md",
    "Documentation/zigux/phase8-clockevent-slice.md",
]


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


def collect_unexpected_files(root: Path) -> list[str]:
    return [rel for rel in UNEXPECTED_FILES if (root / rel).exists()]


def validate(root: Path) -> tuple[list[str], list[str], list[str]]:
    missing_files = collect_missing_files(root)
    if missing_files:
        return missing_files, [], []

    missing_markers = collect_missing_markers(root)
    if missing_markers:
        return [], missing_markers, []

    return [], [], collect_unexpected_files(root)


def write_fixture_root(tmp_root: Path) -> None:
    fixture_text = {rel: "\n".join(markers) + "\n" for rel, markers in REQUIRED_MARKERS.items()}
    for rel in REQUIRED_FILES:
        path = tmp_root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(fixture_text[rel], encoding="utf-8")


def expect_missing_file(case: str, tmp_root: Path, rel: str) -> None:
    missing_files, missing_markers, unexpected_files = validate(tmp_root)
    assert missing_markers == [], case
    assert unexpected_files == [], case
    assert missing_files == [rel], case


def expect_missing_marker(case: str, tmp_root: Path, expected: str) -> None:
    missing_files, missing_markers, unexpected_files = validate(tmp_root)
    assert missing_files == [], case
    assert unexpected_files == [], case
    assert missing_markers == [expected], case


def expect_unexpected_file(case: str, tmp_root: Path, rel: str) -> None:
    missing_files, missing_markers, unexpected_files = validate(tmp_root)
    assert missing_files == [], case
    assert missing_markers == [], case
    assert unexpected_files == [rel], case


def mutate_file(tmp_root: Path, rel: str, old: str, new: str, case: str) -> None:
    path = tmp_root / rel
    original = path.read_text(encoding="utf-8")
    updated = original.replace(old, new, 1)
    assert updated != original, case
    path.write_text(updated, encoding="utf-8")


def run_self_test() -> None:
    missing_file_cases = [
        ("missing_libbpf_survey", "Documentation/zigux/phase8-libbpf-segment-survey.md"),
        ("missing_bridge_survey", "Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md"),
        ("missing_poll_note", "Documentation/zigux/phase8-perf-buffer-poll-slice.md"),
        ("missing_focused_test", "zigux/tests/phase8_libbpf_segments.zig"),
    ]

    marker_cases = [
        (
            "missing_survey_no_timer_marker",
            "Documentation/zigux/phase8-libbpf-segment-survey.md",
            "standalone timer or clockevent helper behavior",
            "standalone deferred helper behavior",
            "Documentation/zigux/phase8-libbpf-segment-survey.md: standalone timer or clockevent helper behavior",
        ),
        (
            "missing_bridge_no_timer_marker",
            "Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md",
            "standalone timer or clockevent helper behavior",
            "standalone deferred helper behavior",
            "Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md: standalone timer or clockevent helper behavior",
        ),
        (
            "missing_poll_timer_marker",
            "Documentation/zigux/phase8-perf-buffer-poll-slice.md",
            "no standalone timer helper",
            "no standalone deferred helper",
            "Documentation/zigux/phase8-perf-buffer-poll-slice.md: no standalone timer helper",
        ),
        (
            "missing_focused_test_marker",
            "zigux/tests/phase8_libbpf_segments.zig",
            "Documentation/zigux/phase8-perf-buffer-poll-slice.md",
            "Documentation/zigux/phase8-poll-slice.md",
            "zigux/tests/phase8_libbpf_segments.zig: Documentation/zigux/phase8-perf-buffer-poll-slice.md",
        ),
    ]

    unexpected_file_cases = [
        ("unexpected_timer_helper", "tools/lib/bpf/zigux_segments/timer.zig"),
        ("unexpected_clockevent_test", "zigux/tests/phase8_clockevent.zig"),
    ]

    with tempfile.TemporaryDirectory(prefix="zigux_phase8_no_timer_") as tmp_dir_str:
        tmp_root = Path(tmp_dir_str)
        write_fixture_root(tmp_root)
        assert validate(tmp_root) == ([], [], [])

        for case, rel in missing_file_cases:
            (tmp_root / rel).unlink()
            expect_missing_file(case, tmp_root, rel)
            write_fixture_root(tmp_root)

        for case, rel, old, new, expected in marker_cases:
            mutate_file(tmp_root, rel, old, new, case)
            expect_missing_marker(case, tmp_root, expected)
            write_fixture_root(tmp_root)

        for case, rel in unexpected_file_cases:
            path = tmp_root / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("// unexpected\n", encoding="utf-8")
            expect_unexpected_file(case, tmp_root, rel)
            path.unlink()

    print("PHASE8_LIBBPF_NO_TIMER_SELF_TEST=pass")
    print(
        "PHASE8_LIBBPF_NO_TIMER_SELF_TEST_CASE_COUNT="
        f"{len(missing_file_cases) + len(marker_cases) + len(unexpected_file_cases)}"
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Fail closed if the current Phase 8 libbpf packet stops proving its no-timer boundary."
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run isolated checker coverage without reading repo files.",
    )
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return 0

    missing_files, missing_markers, unexpected_files = validate(ROOT)
    if missing_files:
        print("PHASE8_LIBBPF_NO_TIMER_BOUNDARY=fail")
        print("PHASE8_LIBBPF_NO_TIMER_MISSING_FILES_START")
        for item in missing_files:
            print(item)
        print("PHASE8_LIBBPF_NO_TIMER_MISSING_FILES_END")
        return 1

    if missing_markers:
        print("PHASE8_LIBBPF_NO_TIMER_BOUNDARY=fail")
        print("PHASE8_LIBBPF_NO_TIMER_MISSING_MARKERS_START")
        for item in missing_markers:
            print(item)
        print("PHASE8_LIBBPF_NO_TIMER_MISSING_MARKERS_END")
        return 1

    if unexpected_files:
        print("PHASE8_LIBBPF_NO_TIMER_BOUNDARY=fail")
        print("PHASE8_LIBBPF_NO_TIMER_UNEXPECTED_FILES_START")
        for item in unexpected_files:
            print(item)
        print("PHASE8_LIBBPF_NO_TIMER_UNEXPECTED_FILES_END")
        return 1

    print("PHASE8_LIBBPF_NO_TIMER_BOUNDARY=pass")
    print(f"PHASE8_LIBBPF_NO_TIMER_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(f"PHASE8_LIBBPF_NO_TIMER_REQUIRED_MARKER_COUNT={sum(len(markers) for markers in REQUIRED_MARKERS.values())}")
    print(f"PHASE8_LIBBPF_NO_TIMER_UNEXPECTED_FILE_COUNT={len(UNEXPECTED_FILES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
