#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


SELF_PATH = Path(__file__).resolve()
ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) >= 3 else SELF_PATH.parent

REQUIRED_FILES = [
    ".github/workflows/zigux-bootstrap.yml",
    "Documentation/zigux/phase8-libbpf-segment-survey.md",
    "Documentation/zigux/phase8-perf-buffer-poll-slice.md",
    "Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md",
    "scripts/zigux/README.md",
    "scripts/zigux/check-phase8-perf-buffer-poll-gate.py",
    "tools/lib/bpf/zigux_segments/perf_buffer_poll.zig",
    "zigux/Makefile",
    "zigux/tests/README.md",
    "zigux/tests/phase8_build.zig",
    "zigux/tests/phase8_libbpf_segments.zig",
    "zigux/tests/phase8_perf_buffer_poll.zig",
    "zigux/tests/phase8_perf_buffer_poll_only_build.zig",
]

REQUIRED_MARKERS = {
    ".github/workflows/zigux-bootstrap.yml": [
        "Run focused Phase 8 libbpf shard tests",
        "make -C zigux phase8-perf-buffer-poll-test",
        "Run Phase 8 tooling tests",
        "zig build test --build-file zigux/tests/phase8_build.zig --summary all",
    ],
    "Documentation/zigux/phase8-libbpf-segment-survey.md": [
        "scripts/zigux/check-phase8-perf-buffer-poll-gate.py",
        "Documentation/zigux/phase8-perf-buffer-poll-slice.md",
        "make -C zigux phase8-perf-buffer-poll-test",
        "zig build test --build-file zigux/tests/phase8_perf_buffer_poll_only_build.zig --summary all",
        "make -C zigux phase8-test",
        "zig build test --build-file zigux/tests/phase8_build.zig --summary all",
    ],
    "Documentation/zigux/phase8-perf-buffer-poll-slice.md": [
        "perf_buffer__poll(timeout_ms)",
        "python3 scripts/zigux/check-phase8-perf-buffer-poll-gate.py",
        "make -C zigux phase8-perf-buffer-poll-test",
        "zig build test --build-file zigux/tests/phase8_perf_buffer_poll_only_build.zig --summary all",
        "no standalone timer helper",
        "no standalone clockevent helper",
        "broader perf-buffer-online-cpu-routing parity",
    ],
    "Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md": [
        "perf-buffer-online-cpu-routing",
        "make -C zigux phase8-perf-buffer-poll-test",
        "zig build test --build-file zigux/tests/phase8_perf_buffer_poll_only_build.zig --summary all",
        "standalone timer or clockevent helper behavior",
    ],
    "scripts/zigux/README.md": [
        "Phase 8 flow",
        "scripts/zigux/check-phase8-perf-buffer-poll-gate.py",
        "Documentation/zigux/phase8-perf-buffer-poll-slice.md",
        "zigux/tests/phase8_perf_buffer_poll.zig",
        "zigux/tests/phase8_perf_buffer_poll_only_build.zig",
        "make -C zigux phase8-perf-buffer-poll-test",
    ],
    "tools/lib/bpf/zigux_segments/perf_buffer_poll.zig": [
        "summarizePollExecution",
        "resolveReadyBufferIndexResultFromSlots",
        "ReadyBufferProcessingExceedsReadyCount",
        "NonReadyWaitHasProcessedRecords",
    ],
    "zigux/Makefile": [
        "phase8-validate:",
        "phase8-perf-buffer-poll-test:",
        "$(ZIG) build test --build-file zigux/tests/phase8_perf_buffer_poll_only_build.zig --summary all",
    ],
    "zigux/tests/README.md": [
        "zigux/tests/phase8_perf_buffer_poll.zig",
        "zigux/tests/phase8_perf_buffer_poll_only_build.zig",
        "make -C zigux phase8-perf-buffer-poll-test",
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
        "phase 8 perf-buffer poll gate checker keeps the dedicated review packet explicit",
        "scripts/zigux/check-phase8-perf-buffer-poll-gate.py",
        "no standalone timer helper",
        "no standalone clockevent helper",
        "ready-buffer processing attempts cannot exceed counted ready buffers before any broader observed-event budget mismatch",
        "phase 8 perf-buffer poll helper keeps the final return-path choice explicit",
        "phase 8 perf-buffer poll helper rejects successful ready waits that process fewer buffers than the observed wait result",
    ],
    "zigux/tests/phase8_perf_buffer_poll_only_build.zig": [
        "../../tools/lib/bpf/zigux_segments/perf_buffer_poll.zig",
        "\"phase8_perf_buffer_poll.zig\"",
        "phase8-perf-buffer-poll-tests",
    ],
}

EXACT_ONCE_SECTION_MARKERS = {
    "scripts/zigux/README.md": [
        {
            "start": "Phase 8 flow\n",
            "end": "\nPhase 9 flow\n",
            "needle": "make -C zigux phase8-perf-buffer-poll-test",
        },
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

def collect_exact_section_errors(root: Path) -> list[str]:
    errors: list[str] = []
    for rel, section_specs in EXACT_ONCE_SECTION_MARKERS.items():
        path = root / rel
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        for spec in section_specs:
            start = text.find(spec["start"])
            if start == -1:
                errors.append(f"{rel}: missing_section_start:{spec['start'].strip()}")
                continue
            section_start = start + len(spec["start"])
            end = text.find(spec["end"], section_start)
            if end == -1:
                errors.append(f"{rel}: missing_section_end:{spec['end'].strip()}")
                continue
            section = text[section_start:end]
            if section.count(spec["needle"]) != 1:
                errors.append(f"{rel}: exact_once_section_marker:{spec['needle']}")
    return errors

def validate(root: Path) -> tuple[list[str], list[str]]:
    missing_markers = collect_missing_markers(root)
    missing_markers.extend(collect_exact_section_errors(root))
    return collect_missing_files(root), missing_markers

def build_scripts_readme_fixture() -> str:
    phase8_markers = "\n".join(REQUIRED_MARKERS["scripts/zigux/README.md"])
    return "# scripts/zigux\n\nPhase 8 flow\n" + phase8_markers + "\n\nPhase 9 flow\n"

def fixture_text(rel: str) -> str:
    if rel == ".github/workflows/zigux-bootstrap.yml":
        return "\n".join(REQUIRED_MARKERS[rel]) + "\n"
    if rel == "scripts/zigux/check-phase8-perf-buffer-poll-gate.py":
        return "# fixture\n"
    if rel == "scripts/zigux/README.md":
        return build_scripts_readme_fixture()
    return "\n".join(REQUIRED_MARKERS.get(rel, ["# fixture"])) + "\n"

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
        ("missing_workflow", ".github/workflows/zigux-bootstrap.yml"),
        ("missing_checker", "scripts/zigux/check-phase8-perf-buffer-poll-gate.py"),
        ("missing_survey", "Documentation/zigux/phase8-libbpf-segment-survey.md"),
        ("missing_poll_note", "Documentation/zigux/phase8-perf-buffer-poll-slice.md"),
        ("missing_bridge_note", "Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md"),
        ("missing_scripts_readme", "scripts/zigux/README.md"),
        ("missing_makefile", "zigux/Makefile"),
        ("missing_tests_readme", "zigux/tests/README.md"),
        ("missing_phase8_build", "zigux/tests/phase8_build.zig"),
        ("missing_poll_test", "zigux/tests/phase8_perf_buffer_poll.zig"),
    ]
    marker_cases = [
        ("workflow_phase8_libbpf_shard_label", ".github/workflows/zigux-bootstrap.yml", "Run focused Phase 8 libbpf shard tests", "Run focused Phase 8 libbpf packet tests", ".github/workflows/zigux-bootstrap.yml: Run focused Phase 8 libbpf shard tests"),
        ("workflow_perf_buffer_poll_route", ".github/workflows/zigux-bootstrap.yml", "make -C zigux phase8-perf-buffer-poll-test", "make -C zigux phase8-poll-test", ".github/workflows/zigux-bootstrap.yml: make -C zigux phase8-perf-buffer-poll-test"),
        ("survey_checker_route", "Documentation/zigux/phase8-libbpf-segment-survey.md", "scripts/zigux/check-phase8-perf-buffer-poll-gate.py", "scripts/zigux/check-phase8-perf-buffer-poll-surface.py", "Documentation/zigux/phase8-libbpf-segment-survey.md: scripts/zigux/check-phase8-perf-buffer-poll-gate.py"),
        ("survey_shared_build_route", "Documentation/zigux/phase8-libbpf-segment-survey.md", "zig build test --build-file zigux/tests/phase8_build.zig --summary all", "zig build test --build-file zigux/tests/phase8_shared_build.zig --summary all", "Documentation/zigux/phase8-libbpf-segment-survey.md: zig build test --build-file zigux/tests/phase8_build.zig --summary all"),
        ("poll_note_checker_route", "Documentation/zigux/phase8-perf-buffer-poll-slice.md", "python3 scripts/zigux/check-phase8-perf-buffer-poll-gate.py", "python3 scripts/zigux/check-phase8-perf-buffer-poll-surface.py", "Documentation/zigux/phase8-perf-buffer-poll-slice.md: python3 scripts/zigux/check-phase8-perf-buffer-poll-gate.py"),
        ("poll_note_route", "Documentation/zigux/phase8-perf-buffer-poll-slice.md", "make -C zigux phase8-perf-buffer-poll-test", "make -C zigux phase8-poll-test", "Documentation/zigux/phase8-perf-buffer-poll-slice.md: make -C zigux phase8-perf-buffer-poll-test"),
        ("bridge_note_boundary", "Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md", "perf-buffer-online-cpu-routing", "perf-buffer-routing", "Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md: perf-buffer-online-cpu-routing"),
        ("scripts_readme_checker", "scripts/zigux/README.md", "scripts/zigux/check-phase8-perf-buffer-poll-gate.py", "scripts/zigux/check-phase8-perf-buffer-poll-surface.py", "scripts/zigux/README.md: scripts/zigux/check-phase8-perf-buffer-poll-gate.py"),
        ("tests_readme_route", "zigux/tests/README.md", "make -C zigux phase8-perf-buffer-poll-test", "make -C zigux phase8-poll-test", "zigux/tests/README.md: make -C zigux phase8-perf-buffer-poll-test"),
        ("phase8_build_perf_module", "zigux/tests/phase8_build.zig", "../../tools/lib/bpf/zigux_segments/perf_buffer_poll.zig", "../../tools/lib/bpf/zigux_segments/perf_buffer_poll_missing.zig", "zigux/tests/phase8_build.zig: ../../tools/lib/bpf/zigux_segments/perf_buffer_poll.zig"),
        ("poll_test_checker_surface", "zigux/tests/phase8_perf_buffer_poll.zig", "phase 8 perf-buffer poll gate checker keeps the dedicated review packet explicit", "phase 8 perf-buffer poll gate checker keeps the review packet explicit", "zigux/tests/phase8_perf_buffer_poll.zig: phase 8 perf-buffer poll gate checker keeps the dedicated review packet explicit"),
        ("poll_test_guard", "zigux/tests/phase8_perf_buffer_poll.zig", "ready-buffer processing attempts cannot exceed counted ready buffers before any broader observed-event budget mismatch", "ready-buffer processing attempts cannot exceed counted ready buffers", "zigux/tests/phase8_perf_buffer_poll.zig: ready-buffer processing attempts cannot exceed counted ready buffers before any broader observed-event budget mismatch"),
        ("poll_test_underprocessed_guard", "zigux/tests/phase8_perf_buffer_poll.zig", "phase 8 perf-buffer poll helper rejects successful ready waits that process fewer buffers than the observed wait result", "phase 8 perf-buffer poll helper rejects successful ready waits that process fewer buffers", "zigux/tests/phase8_perf_buffer_poll.zig: phase 8 perf-buffer poll helper rejects successful ready waits that process fewer buffers than the observed wait result"),
        ("scripts_readme_phase8_section_route_once", "scripts/zigux/README.md", "make -C zigux phase8-perf-buffer-poll-test", "make -C zigux phase8-perf-buffer-poll-test\nmake -C zigux phase8-perf-buffer-poll-test", "scripts/zigux/README.md: exact_once_section_marker:make -C zigux phase8-perf-buffer-poll-test"),
    ]
    with tempfile.TemporaryDirectory(prefix="zigux_phase8_perf_buffer_poll_") as tmp_dir_str:
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
    print("PHASE8_PERF_BUFFER_POLL_GATE_SELF_TEST=pass")
    print(
        "PHASE8_PERF_BUFFER_POLL_GATE_SELF_TEST_CASE_COUNT="
        f"{len(missing_file_cases) + len(marker_cases)}"
    )

def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the current Phase 8 perf-buffer poll review packet.")
    parser.add_argument("--self-test", action="store_true", help="Run checker self-test cases without reading repo files.")
    args = parser.parse_args()
    if args.self_test:
        run_self_test()
        return 0
    missing_files, missing_markers = validate(ROOT)
    if missing_files:
        print("PHASE8_PERF_BUFFER_POLL_GATE=fail")
        print("MISSING_PHASE8_PERF_BUFFER_POLL_FILES_START")
        for item in missing_files:
            print(item)
        print("MISSING_PHASE8_PERF_BUFFER_POLL_FILES_END")
        return 1
    if missing_markers:
        print("PHASE8_PERF_BUFFER_POLL_GATE=fail")
        print("MISSING_PHASE8_PERF_BUFFER_POLL_MARKERS_START")
        for item in missing_markers:
            print(item)
        print("MISSING_PHASE8_PERF_BUFFER_POLL_MARKERS_END")
        return 1
    print("PHASE8_PERF_BUFFER_POLL_GATE=pass")
    print(f"PHASE8_PERF_BUFFER_POLL_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(f"PHASE8_PERF_BUFFER_POLL_REQUIRED_MARKER_COUNT={sum(len(markers) for markers in REQUIRED_MARKERS.values())}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
