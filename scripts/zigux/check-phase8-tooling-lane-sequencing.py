#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

SCRIPT_PATH = "scripts/zigux/check-phase8-tooling-lane-sequencing.py"
SEQUENCING_PATH = "Documentation/zigux/phase8-tooling-lane-sequencing.md"
SCRIPTS_README_PATH = "scripts/zigux/README.md"

REQUIRED_FILES = (
    SCRIPT_PATH,
    SEQUENCING_PATH,
    SCRIPTS_README_PATH,
)

REQUIRED_MARKERS = {
    SEQUENCING_PATH: (
        "current 2026-05-27 reread closes the earlier scripts-root perf-buffer-poll omission cue:",
        "`scripts/zigux/README.md` now explicitly carries `Documentation/zigux/phase8-perf-buffer-poll-slice.md`, `zigux/tests/phase8_perf_buffer_poll.zig`, `zigux/tests/phase8_perf_buffer_poll_only_build.zig`, `tools/lib/bpf/zigux_segments/perf_buffer_poll.zig`, and `make -C zigux phase8-perf-buffer-poll-test` beside the shared validator-first packet, so shared-wording follow-through no longer needs a scripts-root perf-buffer reminder repair.",
        "current 2026-05-27 reread also closes the older scripts-root symbol undercount cue:",
        "`scripts/zigux/README.md` now keeps `Documentation/zigux/phase8-kallsyms-slice.md`, `tools/lib/symbol/kallsyms.zig`, `zigux/tests/phase8_kallsyms.zig`, and `zigux/tests/phase8_kallsyms_only_build.zig` visible as broader public-tree-backed companions, so the shared wording lane no longer needs a scripts-root kallsyms reminder repair either.",
        "The smallest remaining shared-wording truthfulness task is therefore this sequencing note itself: it should stop pointing future runs at a scripts-root omission that current `master` no longer has.",
        "Keep the shared wording lane parked again after this note-local repair.",
        "If the lane reopens, start with a fresh reread of `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml` together before widening to any validator, helper, or bridge-packet follow-through.",
    ),
    SCRIPTS_README_PATH: (
        "`Documentation/zigux/phase8-perf-buffer-poll-slice.md`",
        "`zigux/tests/phase8_perf_buffer_poll.zig`",
        "`zigux/tests/phase8_perf_buffer_poll_only_build.zig`",
        "`tools/lib/bpf/zigux_segments/perf_buffer_poll.zig`",
        "`make -C zigux phase8-perf-buffer-poll-test`",
        "`Documentation/zigux/phase8-kallsyms-slice.md`",
        "`tools/lib/symbol/kallsyms.zig`",
        "`zigux/tests/phase8_kallsyms.zig`",
        "`zigux/tests/phase8_kallsyms_only_build.zig`",
    ),
}


def read_text(root: Path, rel_path: str) -> str:
    return (root / rel_path).read_text(encoding="utf-8")


def write_text(root: Path, rel_path: str, content: str) -> None:
    path = root / rel_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


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


def emit_result(problems: list[str]) -> int:
    if problems:
        print("PHASE8_TOOLING_LANE_SEQUENCING=fail")
        print("PHASE8_TOOLING_LANE_SEQUENCING_PROBLEMS_START")
        for problem in problems:
            print(problem)
        print("PHASE8_TOOLING_LANE_SEQUENCING_PROBLEMS_END")
        return 1

    print("PHASE8_TOOLING_LANE_SEQUENCING=pass")
    print(f"PHASE8_TOOLING_LANE_SEQUENCING_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(
        "PHASE8_TOOLING_LANE_SEQUENCING_REQUIRED_MARKER_COUNT="
        f"{sum(len(markers) for markers in REQUIRED_MARKERS.values())}"
    )
    return 0


def run_validator(root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(root / SCRIPT_PATH)],
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
    )


def make_fixture_root(root: Path) -> None:
    script_text = Path(__file__).read_text(encoding="utf-8")
    write_text(root, SCRIPT_PATH, script_text)
    for rel_path, markers in REQUIRED_MARKERS.items():
        write_text(root, rel_path, "\n".join(markers) + "\n")


def assert_missing_case(root: Path, rel_path: str, marker: str) -> None:
    text = read_text(root, rel_path)
    if marker not in text:
        raise SystemExit(f"self-test-fixture-missing:{rel_path}:{marker}")

    write_text(root, rel_path, text.replace(marker, ""))
    result = run_validator(root)
    expected = f"missing-marker:{rel_path}:{marker}"
    output = result.stdout.strip() or result.stderr.strip() or "no_output"
    if result.returncode == 0:
        raise SystemExit(f"self-test-unexpected-pass:{expected}")
    if "PHASE8_TOOLING_LANE_SEQUENCING=fail" not in output:
        raise SystemExit(f"self-test-missing-fail-banner:{output}")
    if "PHASE8_TOOLING_LANE_SEQUENCING_PROBLEMS_START" not in output:
        raise SystemExit(f"self-test-missing-problem-banner:{output}")
    if expected not in output:
        raise SystemExit(f"self-test-mismatch:{expected}:{output}")


def run_self_test() -> int:
    cases = 1
    with tempfile.TemporaryDirectory(prefix="zigux_phase8_tooling_lane_sequencing_") as tmp:
        baseline_root = Path(tmp) / "baseline"
        make_fixture_root(baseline_root)

        baseline = run_validator(baseline_root)
        baseline_output = baseline.stdout.strip() or baseline.stderr.strip() or "no_output"
        if baseline.returncode != 0:
            raise SystemExit(f"self-test-baseline-failed:{baseline_output}")
        if "PHASE8_TOOLING_LANE_SEQUENCING=pass" not in baseline_output:
            raise SystemExit(f"self-test-missing-pass-banner:{baseline_output}")

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
            if "PHASE8_TOOLING_LANE_SEQUENCING=fail" not in output:
                raise SystemExit(f"self-test-missing-fail-banner:{output}")
            if "PHASE8_TOOLING_LANE_SEQUENCING_PROBLEMS_START" not in output:
                raise SystemExit(f"self-test-missing-problem-banner:{output}")
            if expected not in output:
                raise SystemExit(f"self-test-mismatch:{expected}:{output}")
            cases += 1

    return cases


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    default_root = Path(__file__).resolve().parent
    if len(default_root.parents) >= 2:
        default_root = default_root.parents[1]
    parser.add_argument("--root", type=Path, default=default_root)
    parser.add_argument("--self-test", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    if args.self_test:
        cases = run_self_test()
        print("PHASE8_TOOLING_LANE_SEQUENCING_SELF_TEST=pass")
        print(f"PHASE8_TOOLING_LANE_SEQUENCING_SELF_TEST_CASE_COUNT={cases}")
        return 0

    return emit_result(validate(args.root))


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
