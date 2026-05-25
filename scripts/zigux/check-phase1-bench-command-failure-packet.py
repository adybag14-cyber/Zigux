#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
import tempfile
from pathlib import Path


CHECKER_REL = Path("scripts/zigux/check-phase1-bench.py")
WORKFLOW_REL = Path(".github/workflows/zigux-bootstrap.yml")

BENCH_COMMAND_MARKERS = (
    '        [zig, "build", "bench", "--build-file", "zigux/tests/build.zig", "-Doptimize=ReleaseSafe"],',
    "        cwd=str(root),",
    "        capture_output=True,",
    "        text=True,",
)

BENCH_FAILURE_MARKERS = (
    "    if result.returncode != 0:",
    '        print("PHASE1_BENCH_CHECK=fail")',
    '        print(f"BENCH_COMMAND_EXIT={result.returncode}")',
    "        if result.stdout:",
    '            print(result.stdout.rstrip("\\n"))',
    "        if result.stderr:",
    '            print(result.stderr.rstrip("\\n"))',
    "        return 1",
)

WORKFLOW_MARKERS = (
    "      - name: Self-test current Phase 1 bench checker",
    "        run: python3 scripts/zigux/check-phase1-bench.py --self-test",
)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def collect_missing_markers(text: str, markers: tuple[str, ...]) -> list[str]:
    return [marker for marker in markers if marker not in text]


def run_check(root: Path) -> tuple[str, object]:
    checker_path = root / CHECKER_REL
    workflow_path = root / WORKFLOW_REL

    missing_paths = [str(rel) for rel in (CHECKER_REL, WORKFLOW_REL) if not (root / rel).is_file()]
    if missing_paths:
        return ("missing_paths", missing_paths)

    checker_text = read_text(checker_path)
    workflow_text = read_text(workflow_path)

    command_missing = collect_missing_markers(checker_text, BENCH_COMMAND_MARKERS)
    if command_missing:
        return ("bench_command_markers", command_missing)

    failure_missing = collect_missing_markers(checker_text, BENCH_FAILURE_MARKERS)
    if failure_missing:
        return ("bench_failure_markers", failure_missing)

    workflow_missing = collect_missing_markers(workflow_text, WORKFLOW_MARKERS)
    if workflow_missing:
        return ("workflow_markers", workflow_missing)

    return (
        "pass",
        {
            "required_file_count": 2,
            "bench_command_marker_count": len(BENCH_COMMAND_MARKERS),
            "bench_failure_marker_count": len(BENCH_FAILURE_MARKERS),
            "workflow_marker_count": len(WORKFLOW_MARKERS),
        },
    )


def write_sample_root(root: Path) -> None:
    (root / CHECKER_REL.parent).mkdir(parents=True, exist_ok=True)
    (root / WORKFLOW_REL.parent).mkdir(parents=True, exist_ok=True)
    (root / CHECKER_REL).write_text(
        "\n".join(
            (
                "#!/usr/bin/env python3",
                "def main() -> int:",
                "    result = subprocess.run(",
                '        [zig, "build", "bench", "--build-file", "zigux/tests/build.zig", "-Doptimize=ReleaseSafe"],',
                "        cwd=str(root),",
                "        capture_output=True,",
                "        text=True,",
                "    )",
                "    if result.returncode != 0:",
                '        print("PHASE1_BENCH_CHECK=fail")',
                '        print(f"BENCH_COMMAND_EXIT={result.returncode}")',
                "        if result.stdout:",
                '            print(result.stdout.rstrip("\\n"))',
                "        if result.stderr:",
                '            print(result.stderr.rstrip("\\n"))',
                "        return 1",
                "    return 0",
                "",
            )
        ),
        encoding="utf-8",
    )
    (root / WORKFLOW_REL).write_text(
        "\n".join(
            (
                "jobs:",
                "  bootstrap:",
                "    steps:",
                "      - name: Self-test current Phase 1 bench checker",
                "        run: python3 scripts/zigux/check-phase1-bench.py --self-test",
                "",
            )
        ),
        encoding="utf-8",
    )


def expect(kind: str, expected_kind: str, payload: object, expected_payload: object) -> None:
    assert kind == expected_kind, (kind, payload)
    assert payload == expected_payload, (kind, payload)


def run_self_test() -> None:
    case_count = 0

    with tempfile.TemporaryDirectory(prefix="lane16-bench-command-failure-") as tmp:
        root = Path(tmp)
        write_sample_root(root)

        kind, payload = run_check(root)
        assert kind == "pass", (kind, payload)
        assert payload == {
            "required_file_count": 2,
            "bench_command_marker_count": len(BENCH_COMMAND_MARKERS),
            "bench_failure_marker_count": len(BENCH_FAILURE_MARKERS),
            "workflow_marker_count": len(WORKFLOW_MARKERS),
        }
        case_count += 1

        (root / CHECKER_REL).unlink()
        kind, payload = run_check(root)
        expect(kind, "missing_paths", payload, [str(CHECKER_REL)])
        case_count += 1
        write_sample_root(root)

        checker_path = root / CHECKER_REL
        checker_path.write_text(
            read_text(checker_path).replace(BENCH_COMMAND_MARKERS[1] + "\n", "", 1),
            encoding="utf-8",
        )
        kind, payload = run_check(root)
        expect(kind, "bench_command_markers", payload, [BENCH_COMMAND_MARKERS[1]])
        case_count += 1
        write_sample_root(root)

        checker_path.write_text(
            read_text(checker_path).replace(BENCH_FAILURE_MARKERS[2] + "\n", "", 1),
            encoding="utf-8",
        )
        kind, payload = run_check(root)
        expect(kind, "bench_failure_markers", payload, [BENCH_FAILURE_MARKERS[2]])
        case_count += 1
        write_sample_root(root)

        workflow_path = root / WORKFLOW_REL
        workflow_path.write_text(
            read_text(workflow_path).replace(WORKFLOW_MARKERS[1] + "\n", "", 1),
            encoding="utf-8",
        )
        kind, payload = run_check(root)
        expect(kind, "workflow_markers", payload, [WORKFLOW_MARKERS[1]])
        case_count += 1

    print("PHASE1_BENCH_COMMAND_FAILURE_PACKET_SELF_TEST=pass")
    print(f"PHASE1_BENCH_COMMAND_FAILURE_PACKET_SELF_TEST_CASE_COUNT={case_count}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check the current Phase 1 bench command-failure packet."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path("."),
        help="Repository root to inspect.",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run checker self-tests without reading a repo tree.",
    )
    parser.add_argument(
        "--write-sample-root",
        type=Path,
        help="Write a minimal passing sample root and exit.",
    )
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return 0

    if args.write_sample_root is not None:
        if args.write_sample_root.exists():
            shutil.rmtree(args.write_sample_root)
        write_sample_root(args.write_sample_root)
        print(f"PHASE1_BENCH_COMMAND_FAILURE_PACKET_SAMPLE_ROOT={args.write_sample_root}")
        return 0

    kind, payload = run_check(args.root)
    if kind != "pass":
        print("PHASE1_BENCH_COMMAND_FAILURE_PACKET=fail")
        print(f"PHASE1_BENCH_COMMAND_FAILURE_PACKET_REASON={kind}")
        print(payload)
        return 1

    assert isinstance(payload, dict)
    print("PHASE1_BENCH_COMMAND_FAILURE_PACKET=pass")
    print(
        "PHASE1_BENCH_COMMAND_FAILURE_PACKET_REQUIRED_FILE_COUNT={}".format(
            payload["required_file_count"]
        )
    )
    print(
        "PHASE1_BENCH_COMMAND_FAILURE_PACKET_BENCH_COMMAND_MARKER_COUNT={}".format(
            payload["bench_command_marker_count"]
        )
    )
    print(
        "PHASE1_BENCH_COMMAND_FAILURE_PACKET_BENCH_FAILURE_MARKER_COUNT={}".format(
            payload["bench_failure_marker_count"]
        )
    )
    print(
        "PHASE1_BENCH_COMMAND_FAILURE_PACKET_WORKFLOW_MARKER_COUNT={}".format(
            payload["workflow_marker_count"]
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
