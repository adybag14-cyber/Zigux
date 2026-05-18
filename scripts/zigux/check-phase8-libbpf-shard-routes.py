#!/usr/bin/env python3
from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

SCRIPT_PATH = "scripts/zigux/check-phase8-libbpf-shard-routes.py"
SURVEY_PATH = "Documentation/zigux/phase8-libbpf-segment-survey.md"
DOCS_README_PATH = "Documentation/zigux/README.md"
TESTS_README_PATH = "zigux/tests/README.md"
MAKEFILE_PATH = "zigux/Makefile"

REQUIRED_FILES = (
    SCRIPT_PATH,
    SURVEY_PATH,
    DOCS_README_PATH,
    TESTS_README_PATH,
    MAKEFILE_PATH,
)

REQUIRED_MARKERS = {
    SURVEY_PATH: (
        "Current exact readback",
        "`tools/lib/bpf/zigux_segments/verify.zig`",
        "`tools/lib/bpf/zigux_segments/type_names.zig`",
        "`tools/lib/bpf/zigux_segments/pin_path.zig`",
        "`tools/lib/bpf/zigux_segments/manifest.json`",
        "`tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig`",
        "`tools/lib/bpf/zigux_segments/online_cpu_routing.zig`",
        "`zigux/tests/phase8_build.zig`",
        "reminder-surface or verify-shard evidence",
    ),
    DOCS_README_PATH: (
        "Phase 8 notes",
        "`Documentation/zigux/phase8-libbpf-segment-survey.md`",
        "`Documentation/zigux/phase8-perf-buffer-poll-slice.md`",
        "`scripts/zigux/validate-phase8.py`",
        "`tools/lib/bpf/zigux_segments/verify.zig`",
        "`tools/lib/bpf/zigux_segments/online_cpu_routing.zig`",
        "`zigux/tests/phase8_libbpf_segments.zig`",
    ),
    TESTS_README_PATH: (
        "## Phase 8 review packet",
        "`Documentation/zigux/phase8-libbpf-segment-survey.md`",
        "`Documentation/zigux/phase8-perf-buffer-poll-slice.md`",
        "`tools/lib/bpf/zigux_segments/verify.zig`",
        "`tools/lib/bpf/zigux_segments/online_cpu_routing.zig`",
        "`zigux/tests/phase8_libbpf_segments.zig`",
        "`zigux/tests/phase8_libbpf_segments_only_build.zig`",
        "`make -C zigux phase8-libbpf-segments-test`",
        "`make -C zigux phase8-perf-buffer-poll-test`",
        "`make -C zigux phase8-test`",
    ),
    MAKEFILE_PATH: (
        "phase8-libbpf-segments-test:",
        "zigux/tests/phase8_libbpf_segments_only_build.zig --summary all",
        "phase8-perf-buffer-poll-test:",
        "zigux/tests/phase8_perf_buffer_poll_only_build.zig --summary all",
        "phase8-test:",
        "zigux/tests/phase8_build.zig --summary all",
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
        raise SystemExit(f"self-test-unexpected-pass:{expected}")
    if expected not in output:
        raise SystemExit(f"self-test-mismatch:{expected}:{output}")


def run_self_test() -> int:
    cases = 1
    with tempfile.TemporaryDirectory(prefix="zigux_phase8_libbpf_shard_routes_") as tmp:
        baseline_root = Path(tmp) / "baseline"
        make_fixture_root(baseline_root)
        baseline = run_validator(baseline_root)
        if baseline.returncode != 0:
            details = baseline.stdout.strip() or baseline.stderr.strip() or "no_output"
            raise SystemExit(f"self-test-baseline-failed:{details}")

        for rel_path, markers in REQUIRED_MARKERS.items():
            for marker in markers:
                case_root = Path(tmp) / f"case_{cases}"
                shutil.copytree(baseline_root, case_root)
                assert_missing_case(case_root, rel_path, marker)
                cases += 1

        for rel_path in REQUIRED_FILES[1:]:
            case_root = Path(tmp) / f"case_{cases}"
            shutil.copytree(baseline_root, case_root)
            (case_root / rel_path).unlink()
            result = run_validator(case_root)
            expected = f"missing-file:{rel_path}"
            output = result.stdout.strip() or result.stderr.strip() or "no_output"
            if result.returncode == 0:
                raise SystemExit(f"self-test-unexpected-pass:{expected}")
            if expected not in output:
                raise SystemExit(f"self-test-mismatch:{expected}:{output}")
            cases += 1

        missing_script_root = Path(tmp) / f"case_{cases}"
        shutil.copytree(baseline_root, missing_script_root)
        (missing_script_root / SCRIPT_PATH).unlink()
        missing_result = run_validator(missing_script_root)
        missing_output = (
            missing_result.stdout.strip() or missing_result.stderr.strip() or "no_output"
        )
        if missing_result.returncode == 0 or "can't open file" not in missing_output:
            raise SystemExit(f"self-test-missing-file-mismatch:{missing_output}")
        cases += 1

    print("PHASE8_LIBBPF_SHARD_ROUTES_SELF_TEST=pass")
    print(f"PHASE8_LIBBPF_SHARD_ROUTES_SELF_TEST_CASE_COUNT={cases}")
    return 0


def main(argv: list[str]) -> int:
    if "--self-test" in argv:
        return run_self_test()

    root = Path(__file__).resolve().parents[2]
    problems = validate(root)
    if problems:
        print("PHASE8_LIBBPF_SHARD_ROUTES=fail")
        print("PHASE8_LIBBPF_SHARD_ROUTES_PROBLEMS_START")
        for problem in problems:
            print(problem)
        print("PHASE8_LIBBPF_SHARD_ROUTES_PROBLEMS_END")
        return 1

    print("PHASE8_LIBBPF_SHARD_ROUTES=pass")
    print(f"PHASE8_LIBBPF_SHARD_ROUTES_ROOT={root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
