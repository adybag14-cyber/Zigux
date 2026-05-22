#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


SELF_PATH = Path(__file__).resolve()
DEFAULT_ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) >= 3 else SELF_PATH.parent

REQUIRED_FILES = [
    "scripts/zigux/check-phase1-bench-json-error-packet.py",
    "scripts/zigux/check-phase1-bench.py",
]

REQUIRED_MARKERS = [
    'if kind == "expectations_json_error":',
    'print("PHASE1_BENCH_CHECK=fail")',
    'print("PHASE1_BENCH_CHECK_REASON=expectations_json_error")',
    'print("EXPECTATIONS_JSON_ERROR={}".format(exc.msg))',
    'print("EXPECTATIONS_JSON_LINE={}".format(exc.lineno))',
    'print("EXPECTATIONS_JSON_COLUMN={}".format(exc.colno))',
]


def repo_root(explicit_root: str | None) -> Path:
    return Path(explicit_root).resolve() if explicit_root else DEFAULT_ROOT


def read_text(root: Path, relative_path: str) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def collect_missing_files(root: Path) -> list[str]:
    return [relative_path for relative_path in REQUIRED_FILES if not (root / relative_path).is_file()]


def collect_missing_markers(root: Path) -> list[str]:
    text = read_text(root, "scripts/zigux/check-phase1-bench.py")
    return [marker for marker in REQUIRED_MARKERS if marker not in text]


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def make_fixture_root(root: Path) -> None:
    write_text(root / "scripts/zigux/check-phase1-bench-json-error-packet.py", "# fixture\n")
    write_text(
        root / "scripts/zigux/check-phase1-bench.py",
        "\n".join(REQUIRED_MARKERS) + "\n",
    )


def run_self_test() -> None:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase1_bench_json_error_packet_") as tmp_dir:
        root = Path(tmp_dir)
        make_fixture_root(root)
        assert collect_missing_files(root) == []
        assert collect_missing_markers(root) == []
        case_count += 1

        bench_checker = root / "scripts/zigux/check-phase1-bench.py"
        bench_checker.write_text(
            bench_checker.read_text(encoding="utf-8").replace(
                'print("PHASE1_BENCH_CHECK_REASON=expectations_json_error")\n',
                "",
                1,
            ),
            encoding="utf-8",
        )
        assert collect_missing_markers(root) == ['print("PHASE1_BENCH_CHECK_REASON=expectations_json_error")']
        case_count += 1
        make_fixture_root(root)

        (root / "scripts/zigux/check-phase1-bench.py").unlink()
        assert collect_missing_files(root) == ["scripts/zigux/check-phase1-bench.py"]
        case_count += 1

    print("PHASE1_BENCH_JSON_ERROR_PACKET_SELF_TEST=pass")
    print(f"PHASE1_BENCH_JSON_ERROR_PACKET_SELF_TEST_CASE_COUNT={case_count}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the bounded Lane 16 malformed-expectations JSON bench packet."
    )
    parser.add_argument("--self-test", action="store_true", help="Run built-in checker self-tests.")
    parser.add_argument("--root", help="Validate an alternate Zigux tree root.")
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return 0

    root = repo_root(args.root)
    missing_files = collect_missing_files(root)
    if missing_files:
        print("PHASE1_BENCH_JSON_ERROR_PACKET=fail")
        print("MISSING_PHASE1_BENCH_JSON_ERROR_PACKET_FILES_START")
        for item in missing_files:
            print(item)
        print("MISSING_PHASE1_BENCH_JSON_ERROR_PACKET_FILES_END")
        return 1

    missing_markers = collect_missing_markers(root)
    if missing_markers:
        print("PHASE1_BENCH_JSON_ERROR_PACKET=fail")
        print("MISSING_PHASE1_BENCH_JSON_ERROR_PACKET_MARKERS_START")
        for item in missing_markers:
            print(item)
        print("MISSING_PHASE1_BENCH_JSON_ERROR_PACKET_MARKERS_END")
        return 1

    print("PHASE1_BENCH_JSON_ERROR_PACKET=pass")
    print(f"PHASE1_BENCH_JSON_ERROR_PACKET_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(f"PHASE1_BENCH_JSON_ERROR_PACKET_REQUIRED_MARKER_COUNT={len(REQUIRED_MARKERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
