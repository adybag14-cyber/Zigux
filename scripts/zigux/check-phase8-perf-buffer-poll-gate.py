#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[2]

REQUIRED_FILES = [
    ".github/workflows/zigux-bootstrap.yml",
    "Documentation/zigux/README.md",
    "Documentation/zigux/phase8-perf-buffer-poll-slice.md",
    "Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md",
    "scripts/zigux/README.md",
    "scripts/zigux/check-phase8-perf-buffer-poll-gate.py",
    "scripts/zigux/validate-phase8.py",
    "tools/lib/bpf/zigux_segments/perf_buffer_poll.zig",
    "zigux/Makefile",
    "zigux/tests/README.md",
    "zigux/tests/phase8_build.zig",
    "zigux/tests/phase8_perf_buffer_poll.zig",
    "zigux/tests/phase8_perf_buffer_poll_only_build.zig",
]

REQUIRED_MARKERS = {
    ".github/workflows/zigux-bootstrap.yml": [
        "Validate Phase 8 tooling gates",
        "make -C zigux phase8-validate",
        "Run focused Phase 8 perf-buffer poll tests",
        "zigux/tests/phase8_perf_buffer_poll_only_build.zig",
    ],
    "Documentation/zigux/README.md": [
        "Documentation/zigux/phase8-perf-buffer-poll-slice.md",
        "tools/lib/bpf/zigux_segments/perf_buffer_poll.zig",
        "zigux/tests/phase8_perf_buffer_poll.zig",
        "make -C zigux phase8-validate",
    ],
    "Documentation/zigux/phase8-perf-buffer-poll-slice.md": [
        "PHASE8_SLICE=perf-buffer-poll-helper",
        "zigux/tests/phase8_perf_buffer_poll_only_build.zig",
        "make -C zigux phase8-perf-buffer-poll-test",
        "wait-result classification",
        "no standalone timer helper",
        "no standalone clockevent helper",
    ],
    "Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md": [
        "Documentation/zigux/phase8-perf-buffer-poll-slice.md",
        "tools/lib/bpf/zigux_segments/perf_buffer_poll.zig",
        "zigux/tests/phase8_perf_buffer_poll.zig",
        "zigux/tests/phase8_perf_buffer_poll_only_build.zig",
        "make -C zigux phase8-perf-buffer-poll-test",
        "ready-buffer counts",
        "no standalone timer helper",
        "no standalone clockevent helper",
    ],
    "scripts/zigux/README.md": [
        "Documentation/zigux/phase8-perf-buffer-poll-slice.md",
        "tools/lib/bpf/zigux_segments/perf_buffer_poll.zig",
        "zigux/tests/phase8_perf_buffer_poll.zig",
        "make -C zigux phase8-validate",
    ],
    "scripts/zigux/validate-phase8.py": [
        "zigux/tests/phase8_perf_buffer_poll_only_build.zig",
        "phase8-perf-buffer-poll-test:",
        "Run focused Phase 8 perf-buffer poll tests",
        "phase8-perf-buffer-poll-tests",
    ],
    "tools/lib/bpf/zigux_segments/perf_buffer_poll.zig": [
        "pub const WaitClass = enum {",
        "pub fn summarizeProcessRecords(",
        "test \"summarizeProcessRecords keeps perf_buffer__process_records fail-fast ordering and processed record totals explicit\"",
    ],
    "zigux/Makefile": [
        "PHONY += phase8-validate phase8-exec-cmd-test phase8-help-test phase8-kallsyms-test phase8-libbpf-segments-test phase8-perf-buffer-poll-test phase8-test phase8",
        "phase8-validate:",
        "scripts/zigux/check-phase8-perf-buffer-poll-gate.py --self-test",
        "scripts/zigux/check-phase8-perf-buffer-poll-gate.py",
        "phase8-perf-buffer-poll-test:",
        "zigux/tests/phase8_perf_buffer_poll_only_build.zig --summary all",
        "phase8: phase8-validate phase8-exec-cmd-test phase8-help-test phase8-kallsyms-test phase8-libbpf-segments-test phase8-perf-buffer-poll-test phase8-test",
    ],
    "zigux/tests/README.md": [
        "zigux/tests/phase8_perf_buffer_poll_only_build.zig",
        "zigux/tests/phase8_perf_buffer_poll.zig",
        "make -C zigux phase8-perf-buffer-poll-test",
    ],
    "zigux/tests/phase8_build.zig": [
        "../../tools/lib/bpf/zigux_segments/perf_buffer_poll.zig",
        "phase8_perf_buffer_poll.zig",
        "phase8-perf-buffer-poll-tests",
    ],
    "zigux/tests/phase8_perf_buffer_poll.zig": [
        "test \"phase 8 perf-buffer poll helper stays wired into focused and shared Phase 8 builds\"",
        "phase8_perf_buffer_poll_only_build.zig",
        "phase8-perf-buffer-poll-tests",
    ],
    "zigux/tests/phase8_perf_buffer_poll_only_build.zig": [
        "phase8_perf_buffer_poll.zig",
        "phase8-perf-buffer-poll-tests",
        "Run focused Phase 8 perf-buffer poll tests",
    ],
}

FIXTURE_TEXT = {
    ".github/workflows/zigux-bootstrap.yml": """name: zigux-bootstrap

- name: Validate Phase 8 tooling gates
  run: make -C zigux phase8-validate

- name: Run focused Phase 8 perf-buffer poll tests
  run: zig build test --build-file zigux/tests/phase8_perf_buffer_poll_only_build.zig --summary all
""",
    "Documentation/zigux/README.md": """# Zigux Documentation

- `Documentation/zigux/phase8-perf-buffer-poll-slice.md`
- `tools/lib/bpf/zigux_segments/perf_buffer_poll.zig`
- `zigux/tests/phase8_perf_buffer_poll.zig`
- `make -C zigux phase8-validate`
""",
    "Documentation/zigux/phase8-perf-buffer-poll-slice.md": """# Phase 8 Perf-Buffer Poll Slice

- `PHASE8_SLICE=perf-buffer-poll-helper`
- `zigux/tests/phase8_perf_buffer_poll_only_build.zig`
- `make -C zigux phase8-perf-buffer-poll-test`
- wait-result classification
- no standalone timer helper
- no standalone clockevent helper
""",
    "Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md": """# Phase 8 Bridge Boundary Survey

- `Documentation/zigux/phase8-perf-buffer-poll-slice.md`
- `tools/lib/bpf/zigux_segments/perf_buffer_poll.zig`
- `zigux/tests/phase8_perf_buffer_poll.zig`
- `zigux/tests/phase8_perf_buffer_poll_only_build.zig`
- `make -C zigux phase8-perf-buffer-poll-test`
- ready-buffer counts
- no standalone timer helper
- no standalone clockevent helper
""",
    "scripts/zigux/README.md": """# scripts/zigux

- `Documentation/zigux/phase8-perf-buffer-poll-slice.md`
- `tools/lib/bpf/zigux_segments/perf_buffer_poll.zig`
- `zigux/tests/phase8_perf_buffer_poll.zig`
- `make -C zigux phase8-validate`
""",
    "scripts/zigux/check-phase8-perf-buffer-poll-gate.py": """#!/usr/bin/env python3
print("fixture")
""",
    "scripts/zigux/validate-phase8.py": """REQUIRED_FILES = [
    "zigux/tests/phase8_perf_buffer_poll_only_build.zig",
]

required_make_markers = [
    "phase8-perf-buffer-poll-test:",
]

required_workflow_markers = [
    "Run focused Phase 8 perf-buffer poll tests",
]

required_phase8_perf_buffer_poll_markers = [
    "phase8-perf-buffer-poll-tests",
]
""",
    "tools/lib/bpf/zigux_segments/perf_buffer_poll.zig": """pub const WaitClass = enum {
    nonblocking,
};

pub fn summarizeProcessRecords() void {}

test "summarizeProcessRecords keeps perf_buffer__process_records fail-fast ordering and processed record totals explicit" {}
""",
    "zigux/Makefile": """PHONY += phase8-validate phase8-exec-cmd-test phase8-help-test phase8-kallsyms-test phase8-libbpf-segments-test phase8-perf-buffer-poll-test phase8-test phase8

phase8-validate:
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase8-perf-buffer-poll-gate.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase8-perf-buffer-poll-gate.py

phase8-perf-buffer-poll-test:
	cd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/phase8_perf_buffer_poll_only_build.zig --summary all

phase8: phase8-validate phase8-exec-cmd-test phase8-help-test phase8-kallsyms-test phase8-libbpf-segments-test phase8-perf-buffer-poll-test phase8-test
""",
    "zigux/tests/README.md": """# zigux/tests

- `zigux/tests/phase8_perf_buffer_poll_only_build.zig`
- `zigux/tests/phase8_perf_buffer_poll.zig`
- `make -C zigux phase8-perf-buffer-poll-test`
""",
    "zigux/tests/phase8_build.zig": """const perf_buffer_poll_module = b.createModule(.{
    .root_source_file = b.path("../../tools/lib/bpf/zigux_segments/perf_buffer_poll.zig"),
});
const perf_buffer_poll_root_module = b.createModule(.{
    .root_source_file = b.path("phase8_perf_buffer_poll.zig"),
});
const perf_buffer_poll_tests = b.addTest(.{
    .name = "phase8-perf-buffer-poll-tests",
});
""",
    "zigux/tests/phase8_perf_buffer_poll.zig": """test "phase 8 perf-buffer poll helper stays wired into focused and shared Phase 8 builds" {
    _ = "phase8_perf_buffer_poll_only_build.zig";
    _ = "phase8-perf-buffer-poll-tests";
}
""",
    "zigux/tests/phase8_perf_buffer_poll_only_build.zig": """const root_module = b.createModule(.{
    .root_source_file = b.path("phase8_perf_buffer_poll.zig"),
});
const perf_buffer_poll_tests = b.addTest(.{
    .name = "phase8-perf-buffer-poll-tests",
});
const test_step = b.step("test", "Run focused Phase 8 perf-buffer poll tests");
""",
}


def read_text(root: Path, rel_path: str) -> str:
    return (root / rel_path).read_text(encoding="utf-8")


def collect_missing_files(root: Path) -> list[str]:
    return [rel_path for rel_path in REQUIRED_FILES if not (root / rel_path).exists()]


def required_marker_count() -> int:
    return sum(len(markers) for markers in REQUIRED_MARKERS.values())


def validate(root: Path) -> tuple[list[str], list[str]]:
    missing_files = collect_missing_files(root)
    if missing_files:
        return missing_files, []

    missing_markers: list[str] = []
    for rel_path, markers in REQUIRED_MARKERS.items():
        text = read_text(root, rel_path)
        for marker in markers:
            if marker not in text:
                missing_markers.append(f"{rel_path}:{marker}")
    return [], missing_markers


def clone_fixture_root(destination_root: Path) -> None:
    for rel_path, text in FIXTURE_TEXT.items():
        target = destination_root / rel_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")


def expect_missing_marker(label: str, root: Path, expected_marker: str) -> None:
    missing_files, missing_markers = validate(root)
    if missing_files:
        raise SystemExit(
            f"phase8-perf-buffer-poll-gate-self-test:{label}:unexpected_missing_files:{','.join(missing_files)}"
        )
    if expected_marker not in missing_markers:
        actual = ",".join(missing_markers) if missing_markers else "none"
        raise SystemExit(
            f"phase8-perf-buffer-poll-gate-self-test:{label}:expected_missing_marker:{expected_marker}:actual:{actual}"
        )


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase8_perf_poll_gate_") as tmp_dir:
        tmp_root = Path(tmp_dir)
        clone_fixture_root(tmp_root)

        missing_files, missing_markers = validate(tmp_root)
        if missing_files or missing_markers:
            raise SystemExit(
                "phase8-perf-buffer-poll-gate-self-test:baseline_failed:"
                f"files={','.join(missing_files) if missing_files else 'none'}:"
                f"markers={','.join(missing_markers) if missing_markers else 'none'}"
            )

        makefile_path = tmp_root / "zigux/Makefile"
        original_makefile = makefile_path.read_text(encoding="utf-8")
        makefile_path.write_text(
            original_makefile.replace(
                "scripts/zigux/check-phase8-perf-buffer-poll-gate.py --self-test",
                "scripts/zigux/check-phase8-perf-buffer-poll-self.py --self-test",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "makefile_self_test_hook",
            tmp_root,
            "zigux/Makefile:scripts/zigux/check-phase8-perf-buffer-poll-gate.py --self-test",
        )
        makefile_path.write_text(original_makefile, encoding="utf-8")

        tests_readme_path = tmp_root / "zigux/tests/README.md"
        original_tests_readme = tests_readme_path.read_text(encoding="utf-8")
        tests_readme_path.write_text(
            original_tests_readme.replace(
                "zigux/tests/phase8_perf_buffer_poll_only_build.zig",
                "zigux/tests/phase8_perf_buffer_poll_build.zig",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "tests_readme_focused_build",
            tmp_root,
            "zigux/tests/README.md:zigux/tests/phase8_perf_buffer_poll_only_build.zig",
        )
        tests_readme_path.write_text(original_tests_readme, encoding="utf-8")

        note_path = tmp_root / "Documentation/zigux/phase8-perf-buffer-poll-slice.md"
        original_note = note_path.read_text(encoding="utf-8")
        note_path.write_text(
            original_note.replace(
                "no standalone timer helper",
                "no standalone timer boundary",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "note_timer_boundary",
            tmp_root,
            "Documentation/zigux/phase8-perf-buffer-poll-slice.md:no standalone timer helper",
        )
        note_path.write_text(original_note, encoding="utf-8")

        workflow_path = tmp_root / ".github/workflows/zigux-bootstrap.yml"
        original_workflow = workflow_path.read_text(encoding="utf-8")
        workflow_path.write_text(
            original_workflow.replace(
                "Run focused Phase 8 perf-buffer poll tests",
                "Run focused Phase 8 perf-buffer tests",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "workflow_poll_step",
            tmp_root,
            ".github/workflows/zigux-bootstrap.yml:Run focused Phase 8 perf-buffer poll tests",
        )
        workflow_path.write_text(original_workflow, encoding="utf-8")

        docs_readme_path = tmp_root / "Documentation/zigux/README.md"
        original_docs_readme = docs_readme_path.read_text(encoding="utf-8")
        docs_readme_path.write_text(
            original_docs_readme.replace(
                "zigux/tests/phase8_perf_buffer_poll.zig",
                "zigux/tests/phase8_perf_buffer_poll_only_build.zig",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "docs_readme_poll_test_surface",
            tmp_root,
            "Documentation/zigux/README.md:zigux/tests/phase8_perf_buffer_poll.zig",
        )
        docs_readme_path.write_text(original_docs_readme, encoding="utf-8")

        docs_readme_path.write_text(
            original_docs_readme.replace(
                "make -C zigux phase8-validate",
                "make -C zigux phase8-check",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "docs_readme_validate_hook",
            tmp_root,
            "Documentation/zigux/README.md:make -C zigux phase8-validate",
        )
        docs_readme_path.write_text(original_docs_readme, encoding="utf-8")

        scripts_readme_path = tmp_root / "scripts/zigux/README.md"
        original_scripts_readme = scripts_readme_path.read_text(encoding="utf-8")
        scripts_readme_path.write_text(
            original_scripts_readme.replace(
                "tools/lib/bpf/zigux_segments/perf_buffer_poll.zig",
                "tools/lib/bpf/zigux_segments/perf_buffer_poll_helper.zig",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "scripts_readme_helper_surface",
            tmp_root,
            "scripts/zigux/README.md:tools/lib/bpf/zigux_segments/perf_buffer_poll.zig",
        )
        scripts_readme_path.write_text(original_scripts_readme, encoding="utf-8")

        scripts_readme_path.write_text(
            original_scripts_readme.replace(
                "make -C zigux phase8-validate",
                "make -C zigux phase8-check",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "scripts_readme_validate_hook",
            tmp_root,
            "scripts/zigux/README.md:make -C zigux phase8-validate",
        )
        scripts_readme_path.write_text(original_scripts_readme, encoding="utf-8")

        scripts_readme_path.write_text(
            original_scripts_readme.replace(
                "Documentation/zigux/phase8-perf-buffer-poll-slice.md",
                "Documentation/zigux/phase8-perf-buffer-slice.md",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "scripts_readme_note_surface",
            tmp_root,
            "scripts/zigux/README.md:Documentation/zigux/phase8-perf-buffer-poll-slice.md",
        )
        scripts_readme_path.write_text(original_scripts_readme, encoding="utf-8")

        scripts_readme_path.write_text(
            original_scripts_readme.replace(
                "zigux/tests/phase8_perf_buffer_poll.zig",
                "zigux/tests/phase8_perf_buffer_wait.zig",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "scripts_readme_test_surface",
            tmp_root,
            "scripts/zigux/README.md:zigux/tests/phase8_perf_buffer_poll.zig",
        )
        scripts_readme_path.write_text(original_scripts_readme, encoding="utf-8")

        bridge_boundary_path = tmp_root / "Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md"
        original_bridge_boundary = bridge_boundary_path.read_text(encoding="utf-8")
        bridge_boundary_path.write_text(
            original_bridge_boundary.replace(
                "zigux/tests/phase8_perf_buffer_poll_only_build.zig",
                "zigux/tests/phase8_perf_buffer_poll_build.zig",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "bridge_boundary_focused_build",
            tmp_root,
            "Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md:zigux/tests/phase8_perf_buffer_poll_only_build.zig",
        )
        bridge_boundary_path.write_text(original_bridge_boundary, encoding="utf-8")

        bridge_boundary_path.write_text(
            original_bridge_boundary.replace(
                "ready-buffer counts",
                "ready-buffer summaries",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "bridge_boundary_ready_buffer_counts",
            tmp_root,
            "Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md:ready-buffer counts",
        )
        bridge_boundary_path.write_text(original_bridge_boundary, encoding="utf-8")

        helper_path = tmp_root / "tools/lib/bpf/zigux_segments/perf_buffer_poll.zig"
        original_helper = helper_path.read_text(encoding="utf-8")
        helper_path.write_text(
            original_helper.replace(
                "pub fn summarizeProcessRecords(",
                "pub fn summarizeProcessedRecords(",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "helper_process_records_surface",
            tmp_root,
            "tools/lib/bpf/zigux_segments/perf_buffer_poll.zig:pub fn summarizeProcessRecords(",
        )
        helper_path.write_text(original_helper, encoding="utf-8")

        helper_path.write_text(
            original_helper.replace(
                "pub const WaitClass = enum {",
                "pub const WaitGroup = enum {",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "helper_wait_class_surface",
            tmp_root,
            "tools/lib/bpf/zigux_segments/perf_buffer_poll.zig:pub const WaitClass = enum {",
        )
        helper_path.write_text(original_helper, encoding="utf-8")

        helper_path.write_text(
            original_helper.replace(
                'test "summarizeProcessRecords keeps perf_buffer__process_records fail-fast ordering and processed record totals explicit"',
                'test "summarizeProcessRecords keeps perf_buffer__process_records ordering explicit"',
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "helper_process_records_test_surface",
            tmp_root,
            'tools/lib/bpf/zigux_segments/perf_buffer_poll.zig:test "summarizeProcessRecords keeps perf_buffer__process_records fail-fast ordering and processed record totals explicit"',
        )
        helper_path.write_text(original_helper, encoding="utf-8")

        validator_path = tmp_root / "scripts/zigux/validate-phase8.py"
        original_validator = validator_path.read_text(encoding="utf-8")
        validator_path.write_text(
            original_validator.replace(
                '"zigux/tests/phase8_perf_buffer_poll_only_build.zig"',
                '"zigux/tests/phase8_perf_buffer_poll_build.zig"',
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "validator_focused_build_file",
            tmp_root,
            "scripts/zigux/validate-phase8.py:zigux/tests/phase8_perf_buffer_poll_only_build.zig",
        )
        validator_path.write_text(original_validator, encoding="utf-8")

        validator_path.write_text(
            original_validator.replace(
                "phase8-perf-buffer-poll-test:",
                "phase8-perf-buffer-test:",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "validator_make_target",
            tmp_root,
            "scripts/zigux/validate-phase8.py:phase8-perf-buffer-poll-test:",
        )
        validator_path.write_text(original_validator, encoding="utf-8")

        validator_path.write_text(
            original_validator.replace(
                "Run focused Phase 8 perf-buffer poll tests",
                "Run focused Phase 8 perf-buffer tests",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "validator_workflow_surface",
            tmp_root,
            "scripts/zigux/validate-phase8.py:Run focused Phase 8 perf-buffer poll tests",
        )
        validator_path.write_text(original_validator, encoding="utf-8")

        shared_build_path = tmp_root / "zigux/tests/phase8_build.zig"
        original_shared_build = shared_build_path.read_text(encoding="utf-8")
        shared_build_path.write_text(
            original_shared_build.replace(
                "phase8-perf-buffer-poll-tests",
                "phase8-perf-buffer-tests",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "shared_build_poll_artifact_name",
            tmp_root,
            "zigux/tests/phase8_build.zig:phase8-perf-buffer-poll-tests",
        )
        shared_build_path.write_text(original_shared_build, encoding="utf-8")

        poll_test_path = tmp_root / "zigux/tests/phase8_perf_buffer_poll.zig"
        original_poll_test = poll_test_path.read_text(encoding="utf-8")
        poll_test_path.write_text(
            original_poll_test.replace(
                "phase8_perf_buffer_poll_only_build.zig",
                "phase8_perf_buffer_poll_build.zig",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "poll_test_focused_build_surface",
            tmp_root,
            "zigux/tests/phase8_perf_buffer_poll.zig:phase8_perf_buffer_poll_only_build.zig",
        )
        poll_test_path.write_text(original_poll_test, encoding="utf-8")

        focused_build_path = tmp_root / "zigux/tests/phase8_perf_buffer_poll_only_build.zig"
        original_focused_build = focused_build_path.read_text(encoding="utf-8")
        focused_build_path.write_text(
            original_focused_build.replace(
                "phase8-perf-buffer-poll-tests",
                "phase8-perf-buffer-tests",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "focused_build_artifact_name",
            tmp_root,
            "zigux/tests/phase8_perf_buffer_poll_only_build.zig:phase8-perf-buffer-poll-tests",
        )

    print("PHASE8_PERF_BUFFER_POLL_GATE_SELF_TEST=pass")
    print("PHASE8_PERF_BUFFER_POLL_GATE_SELF_TEST_CASE_COUNT=21")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate that the focused Phase 8 perf-buffer poll shard stays inside the shared review gate."
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run built-in drift checks against a compact synthetic Phase 8 fixture tree.",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    missing_files, missing_markers = validate(ROOT)
    if missing_files:
        print("PHASE8_PERF_BUFFER_POLL_GATE=fail")
        print("MISSING_PHASE8_PERF_BUFFER_POLL_GATE_FILES_START")
        for item in missing_files:
            print(item)
        print("MISSING_PHASE8_PERF_BUFFER_POLL_GATE_FILES_END")
        return 1
    if missing_markers:
        print("PHASE8_PERF_BUFFER_POLL_GATE=fail")
        print("MISSING_PHASE8_PERF_BUFFER_POLL_GATE_MARKERS_START")
        for marker in missing_markers:
            print(marker)
        print("MISSING_PHASE8_PERF_BUFFER_POLL_GATE_MARKERS_END")
        return 1

    print("PHASE8_PERF_BUFFER_POLL_GATE=pass")
    print(f"PHASE8_PERF_BUFFER_POLL_GATE_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(f"PHASE8_PERF_BUFFER_POLL_GATE_REQUIRED_MARKER_COUNT={required_marker_count()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
