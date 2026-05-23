#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent

BENCH_CHECKER_REL = Path("scripts/zigux/check-phase1-bench.py")
WORKFLOW_REL = Path(".github/workflows/zigux-bootstrap.yml")

BENCH_COMMAND_MARKERS = (
    'zig = find_zig(args.zig)',
    '[zig, "build", "bench", "--build-file", "zigux/tests/build.zig", "-Doptimize=ReleaseSafe"]',
    "cwd=str(ROOT)",
    "capture_output=True",
    "text=True",
)

BENCH_FAILURE_MARKERS = (
    'print("PHASE1_BENCH_CHECK=fail")',
    'if result.returncode != 0:',
    'print(f"BENCH_COMMAND_EXIT={result.returncode}")',
    "if result.stdout:",
    'print(result.stdout.rstrip("\\n"))',
    "if result.stderr:",
    'print(result.stderr.rstrip("\\n"))',
    "return 1",
)

WORKFLOW_MARKERS = (
    "- name: Self-test current Phase 1 bench checker",
    "run: python3 scripts/zigux/check-phase1-bench.py --self-test",
)


def repo_root(override: str | None) -> Path:
    return Path(override).resolve() if override else ROOT


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def sample_bench_checker() -> str:
    failure_markers = "\n".join(f"        {marker}" for marker in BENCH_FAILURE_MARKERS)
    return (
        "def main() -> int:\n"
        "    parser = argparse.ArgumentParser(description=\"Run and validate the bounded Phase 1 benchmark smoke output.\")\n"
        "    parser.add_argument(\"--zig\", help=\"Path to Zig executable\")\n"
        "    parser.add_argument(\"--self-test\", action=\"store_true\", help=\"Run checker self-test cases without invoking Zig.\")\n"
        "    args = parser.parse_args()\n"
        "\n"
        '    zig = find_zig(args.zig)\n'
        "    result = subprocess.run(\n"
        "        [zig, \"build\", \"bench\", \"--build-file\", \"zigux/tests/build.zig\", \"-Doptimize=ReleaseSafe\"],\n"
        "        cwd=str(ROOT),\n"
        "        capture_output=True,\n"
        "        text=True,\n"
        "    )\n"
        "    if result.returncode != 0:\n"
        f"{failure_markers}\n"
        "\n"
        "    return 0\n"
    )


def sample_workflow() -> str:
    return (
        "jobs:\n"
        "  bootstrap:\n"
        "    steps:\n"
        "      - name: Self-test current Phase 1 bench checker\n"
        "        run: python3 scripts/zigux/check-phase1-bench.py --self-test\n"
    )


def write_sample_root(root: Path) -> None:
    write_text(root / BENCH_CHECKER_REL, sample_bench_checker())
    write_text(root / WORKFLOW_REL, sample_workflow())


def collect_missing_markers(text: str, markers: tuple[str, ...]) -> list[str]:
    return [marker for marker in markers if marker not in text]


def collect_failures(root: Path) -> list[str]:
    failures: list[str] = []
    bench_path = root / BENCH_CHECKER_REL
    workflow_path = root / WORKFLOW_REL

    if not bench_path.is_file():
        return [f"missing_file:{BENCH_CHECKER_REL.as_posix()}"]
    if not workflow_path.is_file():
        return [f"missing_file:{WORKFLOW_REL.as_posix()}"]

    bench_text = bench_path.read_text(encoding="utf-8")
    workflow_text = workflow_path.read_text(encoding="utf-8")

    missing_command_markers = collect_missing_markers(bench_text, BENCH_COMMAND_MARKERS)
    if missing_command_markers:
        failures.extend(
            f"missing_bench_command_marker:{marker}" for marker in missing_command_markers
        )

    missing_failure_markers = collect_missing_markers(bench_text, BENCH_FAILURE_MARKERS)
    if missing_failure_markers:
        failures.extend(
            f"missing_bench_failure_marker:{marker}" for marker in missing_failure_markers
        )

    missing_workflow_markers = collect_missing_markers(workflow_text, WORKFLOW_MARKERS)
    if missing_workflow_markers:
        failures.extend(
            f"missing_workflow_marker:{marker}" for marker in missing_workflow_markers
        )

    return failures


def assert_case(condition: bool, name: str, payload: object = None) -> None:
    if not condition:
        raise AssertionError((name, payload))


def run_self_test() -> None:
    case_count = 0

    with tempfile.TemporaryDirectory(prefix="phase1-bench-command-failure-") as tmp:
        root = Path(tmp)
        write_sample_root(root)

        failures = collect_failures(root)
        assert_case(not failures, "baseline pass", failures)
        case_count += 1

        (root / BENCH_CHECKER_REL).unlink()
        failures = collect_failures(root)
        assert_case(
            failures == [f"missing_file:{BENCH_CHECKER_REL.as_posix()}"],
            "missing bench checker",
            failures,
        )
        case_count += 1

    with tempfile.TemporaryDirectory(prefix="phase1-bench-command-failure-") as tmp:
        root = Path(tmp)
        write_sample_root(root)
        write_text(
            root / BENCH_CHECKER_REL,
            sample_bench_checker().replace('print(f"BENCH_COMMAND_EXIT={result.returncode}")\n', "", 1),
        )
        failures = collect_failures(root)
        assert_case(
            failures
            == ['missing_bench_failure_marker:print(f"BENCH_COMMAND_EXIT={result.returncode}")'],
            "missing bench exit marker",
            failures,
        )
        case_count += 1

    with tempfile.TemporaryDirectory(prefix="phase1-bench-command-failure-") as tmp:
        root = Path(tmp)
        write_sample_root(root)
        write_text(
            root / BENCH_CHECKER_REL,
            sample_bench_checker().replace("capture_output=True,\n", "", 1),
        )
        failures = collect_failures(root)
        assert_case(
            failures == ["missing_bench_command_marker:capture_output=True"],
            "missing capture_output marker",
            failures,
        )
        case_count += 1

    with tempfile.TemporaryDirectory(prefix="phase1-bench-command-failure-") as tmp:
        root = Path(tmp)
        write_sample_root(root)
        write_text(
            root / WORKFLOW_REL,
            sample_workflow().replace(
                "run: python3 scripts/zigux/check-phase1-bench.py --self-test\n",
                "",
                1,
            ),
        )
        failures = collect_failures(root)
        assert_case(
            failures
            == [
                "missing_workflow_marker:run: python3 scripts/zigux/check-phase1-bench.py --self-test"
            ],
            "missing workflow marker",
            failures,
        )
        case_count += 1

    print("PHASE1_BENCH_COMMAND_FAILURE_PACKET_SELF_TEST=pass")
    print(f"PHASE1_BENCH_COMMAND_FAILURE_PACKET_SELF_TEST_CASE_COUNT={case_count}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check the bounded Lane 16 bench command-failure packet on current master."
    )
    parser.add_argument("--root", help="Override the repository root for validation.")
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run checker self-test cases without inspecting a repository.",
    )
    parser.add_argument(
        "--write-sample-root",
        help="Write a current-like sample root for focused packet validation.",
    )
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return 0

    if args.write_sample_root:
        write_sample_root(Path(args.write_sample_root).resolve())
        return 0

    root = repo_root(args.root)
    failures = collect_failures(root)
    if failures:
        print("PHASE1_BENCH_COMMAND_FAILURE_PACKET=fail")
        for failure in failures:
            print(failure)
        return 1

    print("PHASE1_BENCH_COMMAND_FAILURE_PACKET=pass")
    print("PHASE1_BENCH_COMMAND_FAILURE_PACKET_REQUIRED_FILE_COUNT=2")
    print(
        "PHASE1_BENCH_COMMAND_FAILURE_PACKET_BENCH_COMMAND_MARKER_COUNT="
        f"{len(BENCH_COMMAND_MARKERS)}"
    )
    print(
        "PHASE1_BENCH_COMMAND_FAILURE_PACKET_BENCH_FAILURE_MARKER_COUNT="
        f"{len(BENCH_FAILURE_MARKERS)}"
    )
    print(
        "PHASE1_BENCH_COMMAND_FAILURE_PACKET_WORKFLOW_MARKER_COUNT="
        f"{len(WORKFLOW_MARKERS)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
