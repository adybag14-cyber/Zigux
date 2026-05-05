#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


SELF_PATH = Path(__file__).resolve()
ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) >= 3 else SELF_PATH.parent

REQUIRED_FILES = [
    "Documentation/zigux/phase8-libbpf-segment-survey.md",
    "Documentation/zigux/phase8-perf-buffer-poll-slice.md",
    "scripts/zigux/validate-phase8.py",
    "zigux/Makefile",
    "zigux/tests/phase8_build.zig",
    "zigux/tests/phase8_libbpf_segments.zig",
    "zigux/tests/phase8_perf_buffer_poll.zig",
    "tools/lib/bpf/zigux_segments/perf_buffer_poll.zig",
]

REQUIRED_MARKERS = {
    "Documentation/zigux/phase8-libbpf-segment-survey.md": [
        "perf-buffer-online-cpu-routing",
        "standalone timer or clockevent helper behavior",
    ],
    "Documentation/zigux/phase8-perf-buffer-poll-slice.md": [
        "perf_buffer__poll(timeout_ms)",
        "wait-result classification",
        "ready-buffer processing attempts cannot exceed observed ready events",
        "no standalone timer helper",
        "no standalone clockevent helper",
    ],
    "zigux/Makefile": [
        "phase8-validate:",
        "scripts/zigux/validate-phase8.py --self-test",
        "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase8.py",
        "phase8-test:",
        "phase8: phase8-validate phase8-test",
    ],
    "zigux/tests/phase8_build.zig": [
        "../../tools/lib/bpf/zigux_segments/perf_buffer_poll.zig",
        "\"phase8_perf_buffer_poll.zig\"",
        "phase8-perf-buffer-poll-tests",
    ],
    "zigux/tests/phase8_libbpf_segments.zig": [
        "perf-buffer-online-cpu-routing",
        "standalone timer or clockevent helper behavior",
    ],
    "zigux/tests/phase8_perf_buffer_poll.zig": [
        "no standalone timer helper",
        "no standalone clockevent helper",
        "ready-buffer processing attempts cannot exceed observed ready events",
    ],
    "tools/lib/bpf/zigux_segments/perf_buffer_poll.zig": [
        "summarizePollExecution",
        "ReadyBufferProcessingExceedsReadyCount",
        "ReadyBufferProcessingExceedsObservedEvents",
    ],
}

FIXTURE_OVERRIDES = {
    "scripts/zigux/validate-phase8.py": "# fixture\n",
    "tools/lib/bpf/zigux_segments/perf_buffer_poll.zig": "\n".join(REQUIRED_MARKERS["tools/lib/bpf/zigux_segments/perf_buffer_poll.zig"]) + "\n",
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
    fixture_text.update(FIXTURE_OVERRIDES)
    for rel in REQUIRED_FILES:
        path = tmp_root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(fixture_text.get(rel, "// fixture\n"), encoding="utf-8")


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
        ("missing_validator", "scripts/zigux/validate-phase8.py"),
        ("missing_makefile", "zigux/Makefile"),
        ("missing_phase8_build", "zigux/tests/phase8_build.zig"),
        ("missing_phase8_perf_buffer_poll_note", "Documentation/zigux/phase8-perf-buffer-poll-slice.md"),
        ("missing_phase8_perf_buffer_poll_test", "zigux/tests/phase8_perf_buffer_poll.zig"),
        ("missing_perf_buffer_poll_helper", "tools/lib/bpf/zigux_segments/perf_buffer_poll.zig"),
    ]

    marker_cases = [
        ("makefile_validate_target", "zigux/Makefile", "phase8-validate:", "", "zigux/Makefile: phase8-validate:"),
        ("makefile_self_test_hook", "zigux/Makefile", "scripts/zigux/validate-phase8.py --self-test", "", "zigux/Makefile: scripts/zigux/validate-phase8.py --self-test"),
        ("makefile_phase8_wrapper", "zigux/Makefile", "phase8: phase8-validate phase8-test", "phase8: phase8-test", "zigux/Makefile: phase8: phase8-validate phase8-test"),
        ("survey_timer_boundary", "Documentation/zigux/phase8-libbpf-segment-survey.md", "standalone timer or clockevent helper behavior", "", "Documentation/zigux/phase8-libbpf-segment-survey.md: standalone timer or clockevent helper behavior"),
        ("perf_buffer_poll_note_boundary", "Documentation/zigux/phase8-perf-buffer-poll-slice.md", "ready-buffer processing attempts cannot exceed observed ready events", "", "Documentation/zigux/phase8-perf-buffer-poll-slice.md: ready-buffer processing attempts cannot exceed observed ready events"),
        ("segments_test_timer_boundary", "zigux/tests/phase8_libbpf_segments.zig", "standalone timer or clockevent helper behavior", "", "zigux/tests/phase8_libbpf_segments.zig: standalone timer or clockevent helper behavior"),
        ("phase8_build_perf_buffer_poll_source", "zigux/tests/phase8_build.zig", "\"phase8_perf_buffer_poll.zig\"", "\"phase8_perf_buffer_poll_drift.zig\"", "zigux/tests/phase8_build.zig: \"phase8_perf_buffer_poll.zig\""),
        ("phase8_build_perf_buffer_poll_test_name", "zigux/tests/phase8_build.zig", "phase8-perf-buffer-poll-tests", "phase8-perf-buffer-tests", "zigux/tests/phase8_build.zig: phase8-perf-buffer-poll-tests"),
        ("phase8_perf_buffer_poll_no_timer", "zigux/tests/phase8_perf_buffer_poll.zig", "no standalone timer helper", "", "zigux/tests/phase8_perf_buffer_poll.zig: no standalone timer helper"),
        ("phase8_perf_buffer_poll_no_clockevent", "zigux/tests/phase8_perf_buffer_poll.zig", "no standalone clockevent helper", "", "zigux/tests/phase8_perf_buffer_poll.zig: no standalone clockevent helper"),
        ("helper_ready_count_guard", "tools/lib/bpf/zigux_segments/perf_buffer_poll.zig", "ReadyBufferProcessingExceedsReadyCount", "ReadyBufferCountMismatch", "tools/lib/bpf/zigux_segments/perf_buffer_poll.zig: ReadyBufferProcessingExceedsReadyCount"),
    ]

    with tempfile.TemporaryDirectory(prefix="zigux_phase8_validator_") as tmp_dir_str:
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

    print("PHASE8_VALIDATOR_SELF_TEST=pass")
    print("PHASE8_VALIDATOR_SELF_TEST_CASE_COUNT=17")


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the current shared Phase 8 timer-adjacent tooling packet.")
    parser.add_argument("--self-test", action="store_true", help="Run validator self-test cases without reading repo files.")
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return 0

    missing_files, missing_markers = validate(ROOT)
    if missing_files:
        print("PHASE8_VALIDATION=fail")
        print("MISSING_PHASE8_FILES_START")
        for item in missing_files:
            print(item)
        print("MISSING_PHASE8_FILES_END")
        return 1

    if missing_markers:
        print("PHASE8_VALIDATION=fail")
        print("MISSING_PHASE8_MARKERS_START")
        for item in missing_markers:
            print(item)
        print("MISSING_PHASE8_MARKERS_END")
        return 1

    print("PHASE8_VALIDATION=pass")
    print(f"PHASE8_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(f"PHASE8_REQUIRED_MARKER_COUNT={sum(len(markers) for markers in REQUIRED_MARKERS.values())}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
