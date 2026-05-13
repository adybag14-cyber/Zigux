#!/usr/bin/env python3
from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


SCRIPT_PATH = "scripts/zigux/check-phase8-tests-readme-alignment.py"
SEQUENCING_PATH = "Documentation/zigux/phase8-tooling-lane-sequencing.md"
SCRIPTS_README_PATH = "scripts/zigux/README.md"
TESTS_README_PATH = "zigux/tests/README.md"
REVIEW_CHECKLIST_PATH = "Documentation/zigux/review-checklist.md"
MAKEFILE_PATH = "zigux/Makefile"

REQUIRED_FILES = (
    SCRIPT_PATH,
    SEQUENCING_PATH,
    SCRIPTS_README_PATH,
    TESTS_README_PATH,
    REVIEW_CHECKLIST_PATH,
    MAKEFILE_PATH,
)

REQUIRED_MARKERS = {
    SEQUENCING_PATH: (
        "### 4. Shared wording lane",
        "Documentation/zigux/phase8-tooling-lane-sequencing.md",
        "make -C zigux phase8-cpu-mask-test",
        "make -C zigux phase8-file-path-handle-bridge-test",
        "make -C zigux phase8-libbpf-segments-test",
        "make -C zigux phase8-perf-buffer-poll-test",
    ),
    SCRIPTS_README_PATH: (
        "Phase 8 flow - the current shared Phase 8 review surface on `master` is",
        "`Documentation/zigux/phase8-tooling-lane-sequencing.md`",
        "`scripts/zigux/check-phase8-perf-buffer-poll-gate.py`",
        "`scripts/zigux/check-phase8-libbpf-segment-gate.py`",
        "`scripts/zigux/check-phase8-libbpf-shard-routes.py`",
        "`make -C zigux phase8-cpu-mask-test`",
        "`make -C zigux phase8-file-path-handle-bridge-test`",
        "`make -C zigux phase8-libbpf-segments-test`",
        "`make -C zigux phase8-perf-buffer-poll-test`",
    ),
    TESTS_README_PATH: (
        "`Documentation/zigux/phase8-tooling-lane-sequencing.md`",
        "`scripts/zigux/check-phase8-tests-readme-alignment.py`",
        "`scripts/zigux/check-phase8-help-kallsyms-packet.py`",
        "`scripts/zigux/check-phase8-perf-buffer-poll-gate.py`",
        "`zigux/tests/phase8_exec_cmd.zig`",
        "`zigux/tests/phase8_exec_cmd_only_build.zig`",
        "`zigux/tests/phase8_help.zig`",
        "`zigux/tests/phase8_help_only_build.zig`",
        "`zigux/tests/phase8_help_kallsyms_only_build.zig`",
        "`zigux/tests/phase8_kallsyms.zig`",
        "`zigux/tests/phase8_kallsyms_only_build.zig`",
        "`zigux/tests/phase8_cpu_mask.zig`",
        "`zigux/tests/phase8_cpu_mask_only_build.zig`",
        "`zigux/tests/phase8_logging.zig`",
        "`zigux/tests/phase8_pin_path.zig`",
        "`zigux/tests/phase8_bpf_type_names.zig`",
        "`zigux/tests/phase8_file_path_handle_bridge.zig`",
        "`zigux/tests/phase8_file_path_handle_bridge_only_build.zig`",
        "`zigux/tests/phase8_perf_buffer_poll.zig`",
        "`zigux/tests/phase8_perf_buffer_poll_only_build.zig`",
        "`zigux/tests/phase8_libbpf_segments.zig`",
        "`zigux/tests/phase8_libbpf_segments_only_build.zig`",
        "`make -C zigux phase8-validate`",
        "`make -C zigux phase8-exec-cmd-test`",
        "`make -C zigux phase8-help-test`",
        "`make -C zigux phase8-help-kallsyms-test`",
        "`make -C zigux phase8-kallsyms-test`",
        "`make -C zigux phase8-cpu-mask-test`",
        "`make -C zigux phase8-file-path-handle-bridge-test`",
        "`make -C zigux phase8-libbpf-segments-test`",
        "`make -C zigux phase8-perf-buffer-poll-test`",
        "`make -C zigux phase8-test`",
        "`make -C zigux phase8`",
    ),
    REVIEW_CHECKLIST_PATH: (
        "if the change touches the shared parked Phase 8 libbpf packet",
        "`Documentation/zigux/phase8-tooling-lane-sequencing.md`",
        "`scripts/zigux/check-phase8-perf-buffer-poll-gate.py`",
        "`make -C zigux phase8-cpu-mask-test`",
        "`make -C zigux phase8-file-path-handle-bridge-test`",
        "`make -C zigux phase8-libbpf-segments-test`",
        "`make -C zigux phase8-perf-buffer-poll-test`",
    ),
    MAKEFILE_PATH: (
        "phase8-validate:",
        "scripts/zigux/check-phase8-perf-buffer-poll-gate.py",
        "phase8-cpu-mask-test:",
        "phase8-file-path-handle-bridge-test:",
        "phase8-libbpf-segments-test:",
        "phase8-perf-buffer-poll-test:",
        "phase8: phase8-validate phase8-test phase8-cpu-mask-test",
    ),
}


def read_text(root: Path, rel_path: str) -> str:
    return (root / rel_path).read_text(encoding="utf-8")


def validate(root: Path) -> list[str]:
    problems: list[str] = []
    for rel_path in REQUIRED_FILES:
        if not (root / rel_path).exists():
            problems.append(f"missing-file:{rel_path}")
    if problems:
        return problems

    for rel_path, markers in REQUIRED_MARKERS.items():
        text = read_text(root, rel_path)
        for marker in markers:
            if marker not in text:
                problems.append(f"missing-marker:{rel_path}:{marker}")
    return problems


def run_validator(root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(root / SCRIPT_PATH)],
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
    )


def write_text(root: Path, rel_path: str, content: str) -> None:
    path = root / rel_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def make_fixture_root(root: Path) -> None:
    script_text = Path(__file__).read_text(encoding="utf-8")
    write_text(root, SCRIPT_PATH, script_text)
    for rel_path, markers in REQUIRED_MARKERS.items():
        write_text(root, rel_path, "\n".join(markers) + "\n")


def assert_missing_case(root: Path, rel_path: str, marker: str) -> None:
    text = read_text(root, rel_path)
    if marker not in text:
        raise SystemExit(f"self-test-fixture-missing:{rel_path}:{marker}")
    (root / rel_path).write_text(text.replace(marker, "", 1), encoding="utf-8")
    result = run_validator(root)
    expected = f"missing-marker:{rel_path}:{marker}"
    output = result.stdout.strip() or result.stderr.strip() or "no_output"
    if result.returncode == 0:
        raise SystemExit(f"self-test-unexpected-pass:{rel_path}:{marker}")
    if expected not in output:
        raise SystemExit(f"self-test-mismatch:{expected}:{output}")


def run_self_test() -> int:
    cases = 1
    with tempfile.TemporaryDirectory(prefix="zigux_phase8_tests_readme_alignment_") as tmp:
        baseline_root = Path(tmp) / "baseline"
        make_fixture_root(baseline_root)
        baseline = run_validator(baseline_root)
        if baseline.returncode != 0:
            details = baseline.stdout.strip() or baseline.stderr.strip() or "no_output"
            raise SystemExit(f"self-test-baseline-failed:{details}")

        mutations = (
            (TESTS_README_PATH, "`scripts/zigux/check-phase8-tests-readme-alignment.py`"),
            (TESTS_README_PATH, "`scripts/zigux/check-phase8-help-kallsyms-packet.py`"),
            (TESTS_README_PATH, "`zigux/tests/phase8_exec_cmd.zig`"),
            (TESTS_README_PATH, "`zigux/tests/phase8_exec_cmd_only_build.zig`"),
            (TESTS_README_PATH, "`zigux/tests/phase8_help.zig`"),
            (TESTS_README_PATH, "`zigux/tests/phase8_help_only_build.zig`"),
            (TESTS_README_PATH, "`zigux/tests/phase8_help_kallsyms_only_build.zig`"),
            (TESTS_README_PATH, "`zigux/tests/phase8_kallsyms.zig`"),
            (TESTS_README_PATH, "`zigux/tests/phase8_kallsyms_only_build.zig`"),
            (TESTS_README_PATH, "`zigux/tests/phase8_cpu_mask.zig`"),
            (TESTS_README_PATH, "`zigux/tests/phase8_cpu_mask_only_build.zig`"),
            (TESTS_README_PATH, "`zigux/tests/phase8_logging.zig`"),
            (TESTS_README_PATH, "`zigux/tests/phase8_pin_path.zig`"),
            (TESTS_README_PATH, "`zigux/tests/phase8_bpf_type_names.zig`"),
            (TESTS_README_PATH, "`zigux/tests/phase8_file_path_handle_bridge.zig`"),
            (TESTS_README_PATH, "`zigux/tests/phase8_perf_buffer_poll.zig`"),
            (TESTS_README_PATH, "`zigux/tests/phase8_perf_buffer_poll_only_build.zig`"),
            (TESTS_README_PATH, "`zigux/tests/phase8_libbpf_segments.zig`"),
            (TESTS_README_PATH, "`zigux/tests/phase8_libbpf_segments_only_build.zig`"),
            (TESTS_README_PATH, "`make -C zigux phase8-validate`"),
            (TESTS_README_PATH, "`make -C zigux phase8-exec-cmd-test`"),
            (TESTS_README_PATH, "`make -C zigux phase8-help-test`"),
            (TESTS_README_PATH, "`make -C zigux phase8-help-kallsyms-test`"),
            (TESTS_README_PATH, "`make -C zigux phase8-kallsyms-test`"),
            (TESTS_README_PATH, "`make -C zigux phase8-test`"),
            (TESTS_README_PATH, "`make -C zigux phase8`"),
            (SCRIPTS_README_PATH, "`make -C zigux phase8-libbpf-segments-test`"),
            (SCRIPTS_README_PATH, "`scripts/zigux/check-phase8-libbpf-segment-gate.py`"),
            (SCRIPTS_README_PATH, "`scripts/zigux/check-phase8-libbpf-shard-routes.py`"),
            (SEQUENCING_PATH, "make -C zigux phase8-perf-buffer-poll-test"),
            (REVIEW_CHECKLIST_PATH, "`scripts/zigux/check-phase8-perf-buffer-poll-gate.py`"),
            (MAKEFILE_PATH, "phase8-cpu-mask-test:"),
        )
        for rel_path, marker in mutations:
            case_root = Path(tmp) / f"case_{cases}"
            shutil.copytree(baseline_root, case_root)
            assert_missing_case(case_root, rel_path, marker)
            cases += 1

        missing_file_root = Path(tmp) / f"case_{cases}"
        shutil.copytree(baseline_root, missing_file_root)
        (missing_file_root / SCRIPT_PATH).unlink()
        missing_result = run_validator(missing_file_root)
        missing_output = missing_result.stdout.strip() or missing_result.stderr.strip() or "no_output"
        if missing_result.returncode == 0 or "can't open file" not in missing_output:
            raise SystemExit(f"self-test-missing-file-mismatch:{missing_output}")
        cases += 1

    print("PHASE8_TESTS_README_ALIGNMENT_SELF_TEST=pass")
    print(f"PHASE8_TESTS_README_ALIGNMENT_SELF_TEST_CASE_COUNT={cases}")
    return 0


def main(argv: list[str]) -> int:
    if "--self-test" in argv:
        return run_self_test()

    root = Path(__file__).resolve().parents[2]
    problems = validate(root)
    if problems:
        print("PHASE8_TESTS_README_ALIGNMENT=fail")
        print("PHASE8_TESTS_README_ALIGNMENT_PROBLEMS_START")
        for problem in problems:
            print(problem)
        print("PHASE8_TESTS_README_ALIGNMENT_PROBLEMS_END")
        return 1

    print("PHASE8_TESTS_README_ALIGNMENT=pass")
    print(f"PHASE8_TESTS_README_ALIGNMENT_ROOT={root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
