#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


SELF_PATH = Path(__file__).resolve()
DEFAULT_ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) >= 3 else SELF_PATH.parent

SELF_CHECKER_REL = Path("scripts/zigux/check-phase1-bench-command-failure-reason-packet.py")
BENCH_CHECKER_REL = Path("scripts/zigux/check-phase1-bench.py")

REQUIRED_FILES = (
    SELF_CHECKER_REL,
    BENCH_CHECKER_REL,
)

REQUIRED_MARKERS = (
    "    if result.returncode != 0:",
    '        print("PHASE1_BENCH_CHECK=fail")',
    '        print("PHASE1_BENCH_CHECK_REASON=bench_command_failed")',
    '        print(f"BENCH_COMMAND_EXIT={result.returncode}")',
)


def repo_root(explicit_root: str | None) -> Path:
    return Path(explicit_root).resolve() if explicit_root else DEFAULT_ROOT


def read_text(root: Path, relative_path: Path) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def collect_missing_files(root: Path) -> list[str]:
    return [str(relative_path) for relative_path in REQUIRED_FILES if not (root / relative_path).is_file()]


def collect_missing_markers(root: Path) -> list[str]:
    text = read_text(root, BENCH_CHECKER_REL)
    return [marker for marker in REQUIRED_MARKERS if marker not in text]


def validate_marker_order(root: Path) -> tuple[str, object]:
    text = read_text(root, BENCH_CHECKER_REL)
    positions = {marker: text.find(marker) for marker in REQUIRED_MARKERS}
    missing = [marker for marker, position in positions.items() if position < 0]
    if missing:
        return ("missing_markers", missing)
    ordered_positions = [positions[marker] for marker in REQUIRED_MARKERS]
    if ordered_positions != sorted(ordered_positions):
        return ("marker_order", list(REQUIRED_MARKERS))
    return ("pass", None)


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def write_sample_root(root: Path) -> None:
    write_text(root / SELF_CHECKER_REL, "#!/usr/bin/env python3\nprint('fixture')\n")
    write_text(
        root / BENCH_CHECKER_REL,
        "\n".join(
            (
                "#!/usr/bin/env python3",
                "def main() -> int:",
                "    if result.returncode != 0:",
                '        print("PHASE1_BENCH_CHECK=fail")',
                '        print("PHASE1_BENCH_CHECK_REASON=bench_command_failed")',
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
    )


def run_self_test() -> None:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase1_bench_command_failure_reason_") as tmp_dir:
        root = Path(tmp_dir)
        write_sample_root(root)

        assert collect_missing_files(root) == []
        assert collect_missing_markers(root) == []
        assert validate_marker_order(root) == ("pass", None)
        case_count += 1

        bench_checker = root / BENCH_CHECKER_REL
        bench_checker.write_text(
            bench_checker.read_text(encoding="utf-8").replace(
                '        print("PHASE1_BENCH_CHECK_REASON=bench_command_failed")\n',
                "",
                1,
            ),
            encoding="utf-8",
        )
        assert collect_missing_markers(root) == ['        print("PHASE1_BENCH_CHECK_REASON=bench_command_failed")']
        assert validate_marker_order(root) == (
            "missing_markers",
            ['        print("PHASE1_BENCH_CHECK_REASON=bench_command_failed")'],
        )
        case_count += 1

        write_sample_root(root)
        bench_checker.write_text(
            bench_checker.read_text(encoding="utf-8").replace(
                '        print("PHASE1_BENCH_CHECK_REASON=bench_command_failed")\n'
                '        print(f"BENCH_COMMAND_EXIT={result.returncode}")\n',
                '        print(f"BENCH_COMMAND_EXIT={result.returncode}")\n'
                '        print("PHASE1_BENCH_CHECK_REASON=bench_command_failed")\n',
                1,
            ),
            encoding="utf-8",
        )
        assert collect_missing_markers(root) == []
        assert validate_marker_order(root) == ("marker_order", list(REQUIRED_MARKERS))
        case_count += 1

        write_sample_root(root)
        (root / BENCH_CHECKER_REL).unlink()
        assert collect_missing_files(root) == [str(BENCH_CHECKER_REL)]
        case_count += 1

    print("PHASE1_BENCH_COMMAND_FAILURE_REASON_PACKET_SELF_TEST=pass")
    print(f"PHASE1_BENCH_COMMAND_FAILURE_REASON_PACKET_SELF_TEST_CASE_COUNT={case_count}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the bounded Lane 16 bench command-failure reason-line packet."
    )
    parser.add_argument("--self-test", action="store_true", help="Run built-in checker self-tests.")
    parser.add_argument("--root", help="Validate an alternate Zigux tree root.")
    parser.add_argument("--write-sample-root", help="Write a minimal passing sample root and exit.")
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return 0

    if args.write_sample_root is not None:
        write_sample_root(Path(args.write_sample_root))
        print(f"PHASE1_BENCH_COMMAND_FAILURE_REASON_PACKET_SAMPLE_ROOT={Path(args.write_sample_root)}")
        return 0

    root = repo_root(args.root)
    missing_files = collect_missing_files(root)
    if missing_files:
        print("PHASE1_BENCH_COMMAND_FAILURE_REASON_PACKET=fail")
        print("MISSING_PHASE1_BENCH_COMMAND_FAILURE_REASON_PACKET_FILES_START")
        for item in missing_files:
            print(item)
        print("MISSING_PHASE1_BENCH_COMMAND_FAILURE_REASON_PACKET_FILES_END")
        return 1

    missing_markers = collect_missing_markers(root)
    if missing_markers:
        print("PHASE1_BENCH_COMMAND_FAILURE_REASON_PACKET=fail")
        print("MISSING_PHASE1_BENCH_COMMAND_FAILURE_REASON_PACKET_MARKERS_START")
        for item in missing_markers:
            print(item)
        print("MISSING_PHASE1_BENCH_COMMAND_FAILURE_REASON_PACKET_MARKERS_END")
        return 1

    order_kind, order_payload = validate_marker_order(root)
    if order_kind != "pass":
        print("PHASE1_BENCH_COMMAND_FAILURE_REASON_PACKET=fail")
        print(f"PHASE1_BENCH_COMMAND_FAILURE_REASON_PACKET_REASON={order_kind}")
        if isinstance(order_payload, list):
            for item in order_payload:
                print(item)
        else:
            print(order_payload)
        return 1

    print("PHASE1_BENCH_COMMAND_FAILURE_REASON_PACKET=pass")
    print(f"PHASE1_BENCH_COMMAND_FAILURE_REASON_PACKET_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(f"PHASE1_BENCH_COMMAND_FAILURE_REASON_PACKET_REQUIRED_MARKER_COUNT={len(REQUIRED_MARKERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
