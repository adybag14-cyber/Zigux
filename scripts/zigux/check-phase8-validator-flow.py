#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[2]

REQUIRED_FILES = [
    "scripts/zigux/validate-phase8.py",
    "scripts/zigux/check-phase8-tests-readme-alignment.py",
    "scripts/zigux/check-phase8-perf-buffer-poll-gate.py",
    "scripts/zigux/README.md",
    "zigux/Makefile",
    "zigux/tests/README.md",
    "Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md",
    "Documentation/zigux/phase8-perf-buffer-poll-slice.md",
    "Documentation/zigux/phase8-libbpf-segment-survey.md",
]

REQUIRED_MARKERS = {
    "scripts/zigux/validate-phase8.py": [
        "scripts/zigux/check-phase8-tests-readme-alignment.py",
        "scripts/zigux/check-phase8-perf-buffer-poll-gate.py",
        "zigux/tests/phase8_perf_buffer_poll_only_build.zig",
        "phase8-perf-buffer-poll-test:",
        "Run focused Phase 8 perf-buffer poll tests",
        "phase8-perf-buffer-poll-tests",
    ],
    "scripts/zigux/check-phase8-tests-readme-alignment.py": [
        '    "scripts/zigux/check-phase8-tests-readme-alignment.py",',
        '    "scripts/zigux/check-phase8-perf-buffer-poll-gate.py",',
        '"tests_readme:scripts/zigux/check-phase8-tests-readme-alignment.py",',
        '"tests_readme:scripts/zigux/check-phase8-perf-buffer-poll-gate.py",',
        "PHASE8_TESTS_README_ALIGNMENT_SELF_TEST_CASE_COUNT=",
    ],
    "scripts/zigux/check-phase8-perf-buffer-poll-gate.py": [
        '"Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md": [',
        '"ready-buffer counts",',
        '"no standalone timer helper",',
        '"no standalone clockevent helper",',
        "PHASE8_PERF_BUFFER_POLL_GATE_SELF_TEST_CASE_COUNT=",
    ],
    "scripts/zigux/README.md": [
        "`check-phase8-tests-readme-alignment.py`",
        "`check-phase8-perf-buffer-poll-gate.py`",
        "`make -C zigux phase8-validate`",
        "`Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md`",
    ],
    "zigux/Makefile": [
        "PHONY += phase8-validate phase8-exec-cmd-test phase8-help-test phase8-kallsyms-test phase8-libbpf-segments-test phase8-perf-buffer-poll-test phase8-test phase8",
        "scripts/zigux/check-phase8-tests-readme-alignment.py --self-test",
        "scripts/zigux/check-phase8-perf-buffer-poll-gate.py --self-test",
        "scripts/zigux/check-phase8-tests-readme-alignment.py",
        "scripts/zigux/check-phase8-perf-buffer-poll-gate.py",
        "phase8-perf-buffer-poll-test:",
        "phase8: phase8-validate phase8-exec-cmd-test phase8-help-test phase8-kallsyms-test phase8-libbpf-segments-test phase8-perf-buffer-poll-test phase8-test",
    ],
    "zigux/tests/README.md": [
        "`zigux/tests/phase8_libbpf_segments.zig`",
        "`zigux/tests/phase8_perf_buffer_poll_only_build.zig`",
        "`scripts/zigux/validate-phase8.py`",
        "`make -C zigux phase8-perf-buffer-poll-test`",
    ],
    "Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md": [
        "`python3 scripts/zigux/check-phase8-validator-flow.py --self-test`",
        "`python3 scripts/zigux/check-phase8-validator-flow.py`",
        "`python3 scripts/zigux/check-phase8-tests-readme-alignment.py --self-test`",
        "`python3 scripts/zigux/check-phase8-perf-buffer-poll-gate.py --self-test`",
        "`python3 scripts/zigux/check-phase8-tests-readme-alignment.py`",
        "`python3 scripts/zigux/check-phase8-perf-buffer-poll-gate.py`",
        "`make -C zigux phase8-perf-buffer-poll-test`",
    ],
    "Documentation/zigux/phase8-perf-buffer-poll-slice.md": [
        "`python3 scripts/zigux/check-phase8-validator-flow.py --self-test`",
        "`python3 scripts/zigux/check-phase8-validator-flow.py`",
        "PHASE8_VALIDATOR_FLOW_SELF_TEST_CASE_COUNT=15",
    ],
    "Documentation/zigux/phase8-libbpf-segment-survey.md": [
        "`python3 scripts/zigux/check-phase8-validator-flow.py --self-test`",
        "`python3 scripts/zigux/check-phase8-validator-flow.py`",
        "PHASE8_VALIDATOR_FLOW_SELF_TEST_CASE_COUNT=15",
    ],
}

FIXTURE_TEXT = {
    "scripts/zigux/validate-phase8.py": "\n".join(
        [
            'REQUIRED_FILES = [',
            '    "zigux/tests/phase8_perf_buffer_poll_only_build.zig",',
            "]",
            "",
            "required_make_markers = [",
            '    "phase8-perf-buffer-poll-test:",',
            "]",
            "",
            "required_workflow_markers = [",
            '    "Run focused Phase 8 perf-buffer poll tests",',
            "]",
            "",
            "required_phase8_perf_buffer_poll_markers = [",
            '    "phase8-perf-buffer-poll-tests",',
            "]",
            "",
            '    "scripts/zigux/check-phase8-tests-readme-alignment.py",',
            '    "scripts/zigux/check-phase8-perf-buffer-poll-gate.py",',
            "",
        ]
    )
    + "\n",
    "scripts/zigux/check-phase8-tests-readme-alignment.py": "\n".join(
        [
            "TESTS_README_MARKERS = [",
            '    "scripts/zigux/validate-phase8.py",',
            '    "scripts/zigux/check-phase8-tests-readme-alignment.py",',
            '    "scripts/zigux/check-phase8-perf-buffer-poll-gate.py",',
            "]",
            "",
            '            "- scripts/zigux/check-phase8-tests-readme-alignment.py\\n",',
            '            "- scripts/zigux/check-phase8-perf-buffer-poll-gate.py\\n",',
            "",
            '        "tests_readme:scripts/zigux/check-phase8-tests-readme-alignment.py",',
            '        "tests_readme:scripts/zigux/check-phase8-perf-buffer-poll-gate.py",',
            "",
            'print("PHASE8_TESTS_README_ALIGNMENT_SELF_TEST_CASE_COUNT=38")',
            "",
        ]
    )
    + "\n",
    "scripts/zigux/check-phase8-perf-buffer-poll-gate.py": "\n".join(
        [
            "REQUIRED_MARKERS = {",
            '    "Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md": [',
            '        "ready-buffer counts",',
            '        "no standalone timer helper",',
            '        "no standalone clockevent helper",',
            "    ],",
            "}",
            "",
            'print("PHASE8_PERF_BUFFER_POLL_GATE_SELF_TEST_CASE_COUNT=21")',
            "",
        ]
    )
    + "\n",
    "scripts/zigux/README.md": "\n".join(
        [
            "# scripts/zigux",
            "",
            "- `check-phase8-tests-readme-alignment.py`",
            "- `check-phase8-perf-buffer-poll-gate.py`",
            "",
            "## Phase 8 flow",
            "- `make -C zigux phase8-validate`",
            "- `Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md`",
            "- `zigux/tests/phase8_bridge_boundary_survey.zig`",
            "- `zigux/tests/phase8_libbpf_segments_only_build.zig`",
            "- `zigux/tests/phase8_perf_buffer_poll.zig`",
            "- `zigux/tests/phase8_perf_buffer_poll_only_build.zig`",
            "",
        ]
    )
    + "\n",
    "zigux/Makefile": "\n".join(
        [
            "PHONY += phase8-validate phase8-exec-cmd-test phase8-help-test phase8-kallsyms-test phase8-libbpf-segments-test phase8-perf-buffer-poll-test phase8-test phase8",
            "phase8-validate:",
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase8-tests-readme-alignment.py --self-test",
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase8-perf-buffer-poll-gate.py --self-test",
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase8-tests-readme-alignment.py",
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase8-perf-buffer-poll-gate.py",
            "phase8-perf-buffer-poll-test:",
            "phase8: phase8-validate phase8-exec-cmd-test phase8-help-test phase8-kallsyms-test phase8-libbpf-segments-test phase8-perf-buffer-poll-test phase8-test",
            "",
        ]
    )
    + "\n",
    "zigux/tests/README.md": "\n".join(
        [
            "# zigux/tests",
            "",
            "- `zigux/tests/phase8_libbpf_segments.zig`",
            "- `zigux/tests/phase8_perf_buffer_poll_only_build.zig`",
            "- `scripts/zigux/validate-phase8.py`",
            "- `make -C zigux phase8-perf-buffer-poll-test`",
            "",
        ]
    )
    + "\n",
    "Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md": "\n".join(
        [
            "# Phase 8 Bridge Boundary Survey",
            "",
            "- `python3 scripts/zigux/check-phase8-validator-flow.py --self-test`",
            "- `python3 scripts/zigux/check-phase8-tests-readme-alignment.py --self-test`",
            "- `python3 scripts/zigux/check-phase8-perf-buffer-poll-gate.py --self-test`",
            "- `python3 scripts/zigux/check-phase8-validator-flow.py`",
            "- `python3 scripts/zigux/check-phase8-tests-readme-alignment.py`",
            "- `python3 scripts/zigux/check-phase8-perf-buffer-poll-gate.py`",
            "- `make -C zigux phase8-perf-buffer-poll-test`",
            "",
        ]
    )
    + "\n",
    "Documentation/zigux/phase8-perf-buffer-poll-slice.md": "\n".join(
        [
            "# Phase 8 Perf-Buffer Poll Slice",
            "",
            "- `python3 scripts/zigux/check-phase8-validator-flow.py --self-test`",
            "- `python3 scripts/zigux/check-phase8-validator-flow.py`",
            "- `PHASE8_VALIDATOR_FLOW_SELF_TEST_CASE_COUNT=15`",
            "",
        ]
    )
    + "\n",
    "Documentation/zigux/phase8-libbpf-segment-survey.md": "\n".join(
        [
            "# Phase 8 Libbpf Segment Survey",
            "",
            "- `python3 scripts/zigux/check-phase8-validator-flow.py --self-test`",
            "- `python3 scripts/zigux/check-phase8-validator-flow.py`",
            "- `PHASE8_VALIDATOR_FLOW_SELF_TEST_CASE_COUNT=15`",
            "",
        ]
    )
    + "\n",
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
            f"phase8-validator-flow-self-test:{label}:unexpected_missing_files:{','.join(missing_files)}"
        )
    if expected_marker not in missing_markers:
        actual = ",".join(missing_markers) if missing_markers else "none"
        raise SystemExit(
            f"phase8-validator-flow-self-test:{label}:expected_missing_marker:{expected_marker}:actual:{actual}"
        )


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase8_validator_flow_") as tmp_dir:
        tmp_root = Path(tmp_dir)
        clone_fixture_root(tmp_root)

        missing_files, missing_markers = validate(tmp_root)
        if missing_files or missing_markers:
            raise SystemExit(
                "phase8-validator-flow-self-test:baseline_failed:"
                f"files={','.join(missing_files) if missing_files else 'none'}:"
                f"markers={','.join(missing_markers) if missing_markers else 'none'}"
            )

        validator_path = tmp_root / "scripts/zigux/validate-phase8.py"
        original_validator = validator_path.read_text(encoding="utf-8")
        validator_path.write_text(
            original_validator.replace(
                '    "scripts/zigux/check-phase8-perf-buffer-poll-gate.py",\n',
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "validator_perf_gate_hook",
            tmp_root,
            "scripts/zigux/validate-phase8.py:scripts/zigux/check-phase8-perf-buffer-poll-gate.py",
        )
        validator_path.write_text(original_validator, encoding="utf-8")

        makefile_path = tmp_root / "zigux/Makefile"
        original_makefile = makefile_path.read_text(encoding="utf-8")
        makefile_path.write_text(
            original_makefile.replace(
                "phase8-perf-buffer-poll-test:\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "makefile_perf_buffer_poll_target",
            tmp_root,
            "zigux/Makefile:phase8-perf-buffer-poll-test:",
        )
        makefile_path.write_text(original_makefile, encoding="utf-8")

        makefile_path.write_text(
            original_makefile.replace(
                "PHONY += phase8-validate phase8-exec-cmd-test phase8-help-test phase8-kallsyms-test phase8-libbpf-segments-test phase8-perf-buffer-poll-test phase8-test phase8\n",
                "PHONY += phase8-validate phase8-exec-cmd-test phase8-help-test phase8-kallsyms-test phase8-libbpf-segments-test phase8-test phase8\n",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "makefile_phase8_phony_route",
            tmp_root,
            "zigux/Makefile:PHONY += phase8-validate phase8-exec-cmd-test phase8-help-test phase8-kallsyms-test phase8-libbpf-segments-test phase8-perf-buffer-poll-test phase8-test phase8",
        )
        makefile_path.write_text(original_makefile, encoding="utf-8")

        makefile_path.write_text(
            original_makefile.replace(
                "phase8: phase8-validate phase8-exec-cmd-test phase8-help-test phase8-kallsyms-test phase8-libbpf-segments-test phase8-perf-buffer-poll-test phase8-test\n",
                "phase8: phase8-validate phase8-exec-cmd-test phase8-help-test phase8-kallsyms-test phase8-libbpf-segments-test phase8-test\n",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "makefile_phase8_aggregate_route",
            tmp_root,
            "zigux/Makefile:phase8: phase8-validate phase8-exec-cmd-test phase8-help-test phase8-kallsyms-test phase8-libbpf-segments-test phase8-perf-buffer-poll-test phase8-test",
        )
        makefile_path.write_text(original_makefile, encoding="utf-8")

        tests_checker_path = tmp_root / "scripts/zigux/check-phase8-tests-readme-alignment.py"
        original_tests_checker = tests_checker_path.read_text(encoding="utf-8")
        tests_checker_path.write_text(
            original_tests_checker.replace(
                '    "scripts/zigux/check-phase8-tests-readme-alignment.py",\n',
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "tests_checker_marker",
            tmp_root,
            'scripts/zigux/check-phase8-tests-readme-alignment.py:    "scripts/zigux/check-phase8-tests-readme-alignment.py",',
        )
        tests_checker_path.write_text(original_tests_checker, encoding="utf-8")

        tests_readme_path = tmp_root / "zigux/tests/README.md"
        original_tests_readme = tests_readme_path.read_text(encoding="utf-8")
        tests_readme_path.write_text(
            original_tests_readme.replace(
                "- `zigux/tests/phase8_perf_buffer_poll_only_build.zig`\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "tests_readme_perf_buffer_poll_only_build",
            tmp_root,
            "zigux/tests/README.md:`zigux/tests/phase8_perf_buffer_poll_only_build.zig`",
        )
        tests_readme_path.write_text(original_tests_readme, encoding="utf-8")

        scripts_readme_path = tmp_root / "scripts/zigux/README.md"
        original_scripts_readme = scripts_readme_path.read_text(encoding="utf-8")
        scripts_readme_path.write_text(
            original_scripts_readme.replace(
                "- `check-phase8-perf-buffer-poll-gate.py`\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "scripts_readme_perf_buffer_poll_gate_checker",
            tmp_root,
            "scripts/zigux/README.md:`check-phase8-perf-buffer-poll-gate.py`",
        )
        scripts_readme_path.write_text(original_scripts_readme, encoding="utf-8")

        bridge_path = tmp_root / "Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md"
        original_bridge = bridge_path.read_text(encoding="utf-8")
        bridge_path.write_text(
            original_bridge.replace(
                "- `python3 scripts/zigux/check-phase8-validator-flow.py --self-test`\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "bridge_validator_flow_self_test_step",
            tmp_root,
            "Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md:`python3 scripts/zigux/check-phase8-validator-flow.py --self-test`",
        )
        bridge_path.write_text(original_bridge, encoding="utf-8")

        bridge_path.write_text(
            original_bridge.replace(
                "- `python3 scripts/zigux/check-phase8-validator-flow.py`\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "bridge_validator_flow_live_step",
            tmp_root,
            "Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md:`python3 scripts/zigux/check-phase8-validator-flow.py`",
        )
        bridge_path.write_text(original_bridge, encoding="utf-8")

        poll_note_path = tmp_root / "Documentation/zigux/phase8-perf-buffer-poll-slice.md"
        original_poll_note = poll_note_path.read_text(encoding="utf-8")
        poll_note_path.write_text(
            original_poll_note.replace(
                "- `python3 scripts/zigux/check-phase8-validator-flow.py --self-test`\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "poll_note_validator_flow_self_test_step",
            tmp_root,
            "Documentation/zigux/phase8-perf-buffer-poll-slice.md:`python3 scripts/zigux/check-phase8-validator-flow.py --self-test`",
        )
        poll_note_path.write_text(original_poll_note, encoding="utf-8")

        poll_note_path.write_text(
            original_poll_note.replace(
                "- `PHASE8_VALIDATOR_FLOW_SELF_TEST_CASE_COUNT=15`\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "poll_note_validator_flow_case_count",
            tmp_root,
            "Documentation/zigux/phase8-perf-buffer-poll-slice.md:PHASE8_VALIDATOR_FLOW_SELF_TEST_CASE_COUNT=15",
        )
        poll_note_path.write_text(original_poll_note, encoding="utf-8")

        libbpf_note_path = tmp_root / "Documentation/zigux/phase8-libbpf-segment-survey.md"
        original_libbpf_note = libbpf_note_path.read_text(encoding="utf-8")
        libbpf_note_path.write_text(
            original_libbpf_note.replace(
                "- `python3 scripts/zigux/check-phase8-validator-flow.py --self-test`\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "libbpf_note_validator_flow_self_test_step",
            tmp_root,
            "Documentation/zigux/phase8-libbpf-segment-survey.md:`python3 scripts/zigux/check-phase8-validator-flow.py --self-test`",
        )
        libbpf_note_path.write_text(original_libbpf_note, encoding="utf-8")

        libbpf_note_path.write_text(
            original_libbpf_note.replace(
                "- `PHASE8_VALIDATOR_FLOW_SELF_TEST_CASE_COUNT=15`\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "libbpf_note_validator_flow_case_count",
            tmp_root,
            "Documentation/zigux/phase8-libbpf-segment-survey.md:PHASE8_VALIDATOR_FLOW_SELF_TEST_CASE_COUNT=15",
        )
        libbpf_note_path.write_text(original_libbpf_note, encoding="utf-8")

        perf_gate_checker_path = tmp_root / "scripts/zigux/check-phase8-perf-buffer-poll-gate.py"
        original_perf_gate_checker = perf_gate_checker_path.read_text(encoding="utf-8")
        perf_gate_checker_path.write_text(
            original_perf_gate_checker.replace(
                "PHASE8_PERF_BUFFER_POLL_GATE_SELF_TEST_CASE_COUNT=21",
                "PHASE8_PERF_BUFFER_POLL_GATE_CASE_COUNT=21",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "perf_gate_checker_self_test_count",
            tmp_root,
            "scripts/zigux/check-phase8-perf-buffer-poll-gate.py:PHASE8_PERF_BUFFER_POLL_GATE_SELF_TEST_CASE_COUNT=",
        )

    print("PHASE8_VALIDATOR_FLOW_SELF_TEST=pass")
    print("PHASE8_VALIDATOR_FLOW_SELF_TEST_CASE_COUNT=15")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the published Phase 8 validator-first checker route."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=ROOT,
        help="Repository root to validate.",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run built-in drift checks against a compact synthetic Phase 8 fixture tree.",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    root = args.root.resolve()
    missing_files, missing_markers = validate(root)
    if missing_files:
        print("PHASE8_VALIDATOR_FLOW=fail")
        print("MISSING_PHASE8_VALIDATOR_FLOW_FILES_START")
        for item in missing_files:
            print(item)
        print("MISSING_PHASE8_VALIDATOR_FLOW_FILES_END")
        return 1
    if missing_markers:
        print("PHASE8_VALIDATOR_FLOW=fail")
        print("MISSING_PHASE8_VALIDATOR_FLOW_MARKERS_START")
        for marker in missing_markers:
            print(marker)
        print("MISSING_PHASE8_VALIDATOR_FLOW_MARKERS_END")
        return 1

    print("PHASE8_VALIDATOR_FLOW=pass")
    print(f"PHASE8_VALIDATOR_FLOW_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(f"PHASE8_VALIDATOR_FLOW_REQUIRED_MARKER_COUNT={required_marker_count()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())