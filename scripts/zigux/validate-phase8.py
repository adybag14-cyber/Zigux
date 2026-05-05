#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


SELF_PATH = Path(__file__).resolve()
ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) >= 3 else SELF_PATH.parent

REQUIRED_FILES = [
    "Documentation/zigux/phase8-bpf-type-names-slice.md",
    "Documentation/zigux/phase8-libbpf-segment-survey.md",
    "Documentation/zigux/phase8-perf-buffer-poll-slice.md",
    "scripts/zigux/validate-phase8.py",
    "zigux/Makefile",
    "zigux/tests/phase8_bpf_type_names.zig",
    "zigux/tests/phase8_build.zig",
    "zigux/tests/phase8_libbpf_segments.zig",
    "zigux/tests/phase8_libbpf_segments_only_build.zig",
    "zigux/tests/phase8_perf_buffer_poll.zig",
    "zigux/tests/phase8_perf_buffer_poll_only_build.zig",
    "tools/lib/bpf/zigux_segments/perf_buffer_poll.zig",
    "tools/lib/bpf/zigux_segments/type_names.zig",
]

REQUIRED_MARKERS = {
    "Documentation/zigux/phase8-bpf-type-names-slice.md": [
        "libbpf_bpf_{attach,link,map,prog}_type_str()",
        "dense table lookups with stable output behavior",
        "zigux/tests/phase8_bpf_type_names.zig",
    ],
    "Documentation/zigux/phase8-libbpf-segment-survey.md": [
        "perf-buffer-online-cpu-routing",
        "standalone timer or clockevent helper behavior",
        "make -C zigux phase8-libbpf-segments-test",
        "zig build test --build-file zigux/tests/phase8_libbpf_segments_only_build.zig --summary all",
        "make -C zigux phase8-perf-buffer-poll-test",
        "zig build test --build-file zigux/tests/phase8_perf_buffer_poll_only_build.zig --summary all",
        "make -C zigux phase8-test",
        "zig build test --build-file zigux/tests/phase8_build.zig --summary all",
    ],
    "Documentation/zigux/phase8-perf-buffer-poll-slice.md": [
        "perf_buffer__poll(timeout_ms)",
        "wait-result classification",
        "ready-buffer processing attempts cannot exceed observed ready events",
        "no standalone timer helper",
        "no standalone clockevent helper",
        "make -C zigux phase8-perf-buffer-poll-test",
        "make -C zigux phase8-test",
        "make -C zigux phase8",
    ],
    "zigux/Makefile": [
        "phase8-validate:",
        "scripts/zigux/validate-phase8.py --self-test",
        "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase8.py",
        "phase8-libbpf-segments-test:",
        "$(ZIG) build test --build-file zigux/tests/phase8_libbpf_segments_only_build.zig --summary all",
        "phase8-perf-buffer-poll-test:",
        "$(ZIG) build test --build-file zigux/tests/phase8_perf_buffer_poll_only_build.zig --summary all",
        "phase8-test:",
        "$(ZIG) build test --build-file zigux/tests/phase8_build.zig --summary all",
        "phase8: phase8-validate phase8-test",
    ],
    "zigux/tests/phase8_bpf_type_names.zig": [
        "phase 8 bpf type-name segment exposes libbpf string helpers",
        "trace_fsession",
        "map_type_names.len",
    ],
    "zigux/tests/phase8_build.zig": [
        "../../tools/lib/bpf/zigux_segments/perf_buffer_poll.zig",
        "\"phase8_perf_buffer_poll.zig\"",
        "phase8-perf-buffer-poll-tests",
        "../../tools/lib/bpf/zigux_segments/type_names.zig",
        "\"phase8_bpf_type_names.zig\"",
        "phase8-bpf-type-names-tests",
    ],
    "zigux/tests/phase8_libbpf_segments.zig": [
        "perf-buffer-online-cpu-routing",
        "standalone timer or clockevent helper behavior",
    ],
    "zigux/tests/phase8_libbpf_segments_only_build.zig": [
        "\"phase8_libbpf_segments.zig\"",
        "phase8-libbpf-segment-tests",
    ],
    "zigux/tests/phase8_perf_buffer_poll.zig": [
        "no standalone timer helper",
        "no standalone clockevent helper",
        "ready-buffer processing attempts cannot exceed observed ready events",
    ],
    "zigux/tests/phase8_perf_buffer_poll_only_build.zig": [
        "../../tools/lib/bpf/zigux_segments/perf_buffer_poll.zig",
        "\"phase8_perf_buffer_poll.zig\"",
        "phase8-perf-buffer-poll-tests",
    ],
    "tools/lib/bpf/zigux_segments/perf_buffer_poll.zig": [
        "summarizePollExecution",
        "ReadyBufferProcessingExceedsReadyCount",
        "ReadyBufferProcessingExceedsObservedEvents",
    ],
    "tools/lib/bpf/zigux_segments/type_names.zig": [
        "pub fn libbpfBpfAttachTypeStr",
        "pub fn libbpfBpfLinkTypeStr",
        "pub fn libbpfBpfMapTypeStr",
        "pub fn libbpfBpfProgTypeStr",
        "trace_fsession",
        "insn_array",
    ],
}

FIXTURE_OVERRIDES = {
    "scripts/zigux/validate-phase8.py": "# fixture\n",
    "tools/lib/bpf/zigux_segments/perf_buffer_poll.zig": "\n".join(
        REQUIRED_MARKERS["tools/lib/bpf/zigux_segments/perf_buffer_poll.zig"]
    )
    + "\n",
    "tools/lib/bpf/zigux_segments/type_names.zig": "\n".join(
        REQUIRED_MARKERS["tools/lib/bpf/zigux_segments/type_names.zig"]
    )
    + "\n",
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
        ("missing_phase8_bpf_type_names_note", "Documentation/zigux/phase8-bpf-type-names-slice.md"),
        ("missing_phase8_perf_buffer_poll_note", "Documentation/zigux/phase8-perf-buffer-poll-slice.md"),
        ("missing_phase8_bpf_type_names_test", "zigux/tests/phase8_bpf_type_names.zig"),
        ("missing_phase8_libbpf_segments_only_build", "zigux/tests/phase8_libbpf_segments_only_build.zig"),
        ("missing_phase8_perf_buffer_poll_test", "zigux/tests/phase8_perf_buffer_poll.zig"),
        ("missing_phase8_perf_buffer_poll_only_build", "zigux/tests/phase8_perf_buffer_poll_only_build.zig"),
        ("missing_type_names_helper", "tools/lib/bpf/zigux_segments/type_names.zig"),
        ("missing_perf_buffer_poll_helper", "tools/lib/bpf/zigux_segments/perf_buffer_poll.zig"),
    ]

    marker_cases = [
        ("makefile_validate_target", "zigux/Makefile", "phase8-validate:", "", "zigux/Makefile: phase8-validate:"),
        ("makefile_self_test_hook", "zigux/Makefile", "scripts/zigux/validate-phase8.py --self-test", "", "zigux/Makefile: scripts/zigux/validate-phase8.py --self-test"),
        ("makefile_libbpf_wrapper_target", "zigux/Makefile", "phase8-libbpf-segments-test:", "", "zigux/Makefile: phase8-libbpf-segments-test:"),
        ("makefile_libbpf_wrapper_command", "zigux/Makefile", "$(ZIG) build test --build-file zigux/tests/phase8_libbpf_segments_only_build.zig --summary all", "$(ZIG) build test --build-file zigux/tests/phase8_libbpf_segments_build.zig --summary all", "zigux/Makefile: $(ZIG) build test --build-file zigux/tests/phase8_libbpf_segments_only_build.zig --summary all"),
        ("makefile_perf_buffer_wrapper_target", "zigux/Makefile", "phase8-perf-buffer-poll-test:", "", "zigux/Makefile: phase8-perf-buffer-poll-test:"),
        ("makefile_perf_buffer_wrapper_command", "zigux/Makefile", "$(ZIG) build test --build-file zigux/tests/phase8_perf_buffer_poll_only_build.zig --summary all", "$(ZIG) build test --build-file zigux/tests/phase8_perf_buffer_poll_build.zig --summary all", "zigux/Makefile: $(ZIG) build test --build-file zigux/tests/phase8_perf_buffer_poll_only_build.zig --summary all"),
        ("makefile_phase8_wrapper", "zigux/Makefile", "phase8: phase8-validate phase8-test", "phase8: phase8-test", "zigux/Makefile: phase8: phase8-validate phase8-test"),
        ("makefile_phase8_shared_summary", "zigux/Makefile", "$(ZIG) build test --build-file zigux/tests/phase8_build.zig --summary all", "$(ZIG) build test --build-file zigux/tests/phase8_build.zig", "zigux/Makefile: $(ZIG) build test --build-file zigux/tests/phase8_build.zig --summary all"),
        ("type_names_note_helper_surface", "Documentation/zigux/phase8-bpf-type-names-slice.md", "libbpf_bpf_{attach,link,map,prog}_type_str()", "", "Documentation/zigux/phase8-bpf-type-names-slice.md: libbpf_bpf_{attach,link,map,prog}_type_str()"),
        ("survey_timer_boundary", "Documentation/zigux/phase8-libbpf-segment-survey.md", "standalone timer or clockevent helper behavior", "", "Documentation/zigux/phase8-libbpf-segment-survey.md: standalone timer or clockevent helper behavior"),
        ("survey_libbpf_wrapper", "Documentation/zigux/phase8-libbpf-segment-survey.md", "make -C zigux phase8-libbpf-segments-test", "make -C zigux phase8-libbpf-survey-test", "Documentation/zigux/phase8-libbpf-segment-survey.md: make -C zigux phase8-libbpf-segments-test"),
        ("survey_perf_buffer_wrapper", "Documentation/zigux/phase8-libbpf-segment-survey.md", "make -C zigux phase8-perf-buffer-poll-test", "make -C zigux phase8-perf-buffer-test", "Documentation/zigux/phase8-libbpf-segment-survey.md: make -C zigux phase8-perf-buffer-poll-test"),
        ("survey_phase8_test_wrapper", "Documentation/zigux/phase8-libbpf-segment-survey.md", "make -C zigux phase8-test", "make -C zigux phase8-shared-test", "Documentation/zigux/phase8-libbpf-segment-survey.md: make -C zigux phase8-test"),
        ("perf_buffer_poll_note_boundary", "Documentation/zigux/phase8-perf-buffer-poll-slice.md", "ready-buffer processing attempts cannot exceed observed ready events", "", "Documentation/zigux/phase8-perf-buffer-poll-slice.md: ready-buffer processing attempts cannot exceed observed ready events"),
        ("perf_buffer_poll_note_focused_gate", "Documentation/zigux/phase8-perf-buffer-poll-slice.md", "make -C zigux phase8-perf-buffer-poll-test", "make -C zigux phase8-perf-buffer-test", "Documentation/zigux/phase8-perf-buffer-poll-slice.md: make -C zigux phase8-perf-buffer-poll-test"),
        ("phase8_bpf_type_names_helper_surface", "zigux/tests/phase8_bpf_type_names.zig", "phase 8 bpf type-name segment exposes libbpf string helpers", "", "zigux/tests/phase8_bpf_type_names.zig: phase 8 bpf type-name segment exposes libbpf string helpers"),
        ("phase8_bpf_type_names_dense_table_anchor", "zigux/tests/phase8_bpf_type_names.zig", "map_type_names.len", "", "zigux/tests/phase8_bpf_type_names.zig: map_type_names.len"),
        ("phase8_build_perf_buffer_poll_source", "zigux/tests/phase8_build.zig", "\"phase8_perf_buffer_poll.zig\"", "\"phase8_perf_buffer_poll_drift.zig\"", "zigux/tests/phase8_build.zig: \"phase8_perf_buffer_poll.zig\""),
        ("phase8_build_perf_buffer_poll_test_name", "zigux/tests/phase8_build.zig", "phase8-perf-buffer-poll-tests", "phase8-perf-buffer-tests", "zigux/tests/phase8_build.zig: phase8-perf-buffer-poll-tests"),
        ("phase8_build_type_names_source", "zigux/tests/phase8_build.zig", "\"phase8_bpf_type_names.zig\"", "\"phase8_bpf_type_names_drift.zig\"", "zigux/tests/phase8_build.zig: \"phase8_bpf_type_names.zig\""),
        ("phase8_build_type_names_test_name", "zigux/tests/phase8_build.zig", "phase8-bpf-type-names-tests", "phase8-bpf-types-tests", "zigux/tests/phase8_build.zig: phase8-bpf-type-names-tests"),
        ("phase8_libbpf_only_build_root_source", "zigux/tests/phase8_libbpf_segments_only_build.zig", "\"phase8_libbpf_segments.zig\"", "\"phase8_libbpf_segments_drift.zig\"", "zigux/tests/phase8_libbpf_segments_only_build.zig: \"phase8_libbpf_segments.zig\""),
        ("phase8_libbpf_only_build_test_name", "zigux/tests/phase8_libbpf_segments_only_build.zig", "phase8-libbpf-segment-tests", "phase8-libbpf-survey-tests", "zigux/tests/phase8_libbpf_segments_only_build.zig: phase8-libbpf-segment-tests"),
        ("phase8_perf_buffer_poll_no_timer", "zigux/tests/phase8_perf_buffer_poll.zig", "no standalone timer helper", "", "zigux/tests/phase8_perf_buffer_poll.zig: no standalone timer helper"),
        ("phase8_perf_buffer_poll_no_clockevent", "zigux/tests/phase8_perf_buffer_poll.zig", "no standalone clockevent helper", "", "zigux/tests/phase8_perf_buffer_poll.zig: no standalone clockevent helper"),
        ("phase8_perf_buffer_only_build_helper_source", "zigux/tests/phase8_perf_buffer_poll_only_build.zig", "../../tools/lib/bpf/zigux_segments/perf_buffer_poll.zig", "../../tools/lib/bpf/zigux_segments/perf_buffer_poll_drift.zig", "zigux/tests/phase8_perf_buffer_poll_only_build.zig: ../../tools/lib/bpf/zigux_segments/perf_buffer_poll.zig"),
        ("phase8_perf_buffer_only_build_root_source", "zigux/tests/phase8_perf_buffer_poll_only_build.zig", "\"phase8_perf_buffer_poll.zig\"", "\"phase8_perf_buffer_poll_drift.zig\"", "zigux/tests/phase8_perf_buffer_poll_only_build.zig: \"phase8_perf_buffer_poll.zig\""),
        ("phase8_perf_buffer_only_build_test_name", "zigux/tests/phase8_perf_buffer_poll_only_build.zig", "phase8-perf-buffer-poll-tests", "phase8-perf-buffer-tests", "zigux/tests/phase8_perf_buffer_poll_only_build.zig: phase8-perf-buffer-poll-tests"),
        ("helper_ready_count_guard", "tools/lib/bpf/zigux_segments/perf_buffer_poll.zig", "ReadyBufferProcessingExceedsReadyCount", "ReadyBufferCountMismatch", "tools/lib/bpf/zigux_segments/perf_buffer_poll.zig: ReadyBufferProcessingExceedsReadyCount"),
        ("type_names_attach_helper", "tools/lib/bpf/zigux_segments/type_names.zig", "pub fn libbpfBpfAttachTypeStr", "pub fn attachTypeStr", "tools/lib/bpf/zigux_segments/type_names.zig: pub fn libbpfBpfAttachTypeStr"),
        ("type_names_table_tail", "tools/lib/bpf/zigux_segments/type_names.zig", "trace_fsession", "trace_session_drift", "tools/lib/bpf/zigux_segments/type_names.zig: trace_fsession"),
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
    print(f"PHASE8_VALIDATOR_SELF_TEST_CASE_COUNT={len(missing_file_cases) + len(marker_cases)}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the current shared Phase 8 repo-hosted tooling packet.")
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
