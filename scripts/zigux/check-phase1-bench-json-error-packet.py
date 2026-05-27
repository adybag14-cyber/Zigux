#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import tempfile


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent
BENCH_CHECKER_REL = Path("scripts/zigux/check-phase1-bench.py")

REQUIRED_MARKERS = (
    '    if kind == "expectations_json_error":',
    "        exc = payload",
    "        assert isinstance(exc, json.JSONDecodeError)",
    '        print("PHASE1_BENCH_CHECK=fail")',
    '        print(f"PHASE1_BENCH_CHECK_REASON={kind}")',
    '        print(f"PHASE1_BENCH_EXPECTATIONS={expectations_file}")',
    '        print(f"EXPECTATIONS_JSON_ERROR={exc.msg}")',
    '        print(f"EXPECTATIONS_JSON_LINE={exc.lineno}")',
    '        print(f"EXPECTATIONS_JSON_COLUMN={exc.colno}")',
    "        return 1",
)


def repo_root(root: str | None) -> Path:
    return Path(root).resolve() if root else DEFAULT_ROOT.resolve()


def bench_checker_path(root: Path) -> Path:
    return root / BENCH_CHECKER_REL


def ordered_marker_failures(text: str, markers: tuple[str, ...]) -> list[str]:
    failures: list[str] = []
    last_index = -1
    for marker in markers:
        count = text.count(marker)
        if count != 1:
            failures.append(
                f"required_marker_count:{marker}:expected=1:actual={count}"
            )
            continue
        index = text.index(marker)
        if index <= last_index:
            failures.append(f"required_marker_order:{marker}")
            continue
        last_index = index
    return failures


def collect_failures(root: Path) -> list[str]:
    checker_path = bench_checker_path(root)
    if not checker_path.is_file():
        return [f"missing_file:{BENCH_CHECKER_REL.as_posix()}"]

    text = checker_path.read_text(encoding="utf-8")
    return ordered_marker_failures(text, REQUIRED_MARKERS)


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def sample_checker_text() -> str:
    return (
        "import json\n\n"
        "def main(kind: str, payload: object, expectations_file: str) -> int:\n"
        '    if kind == "expectations_json_error":\n'
        "        exc = payload\n"
        "        assert isinstance(exc, json.JSONDecodeError)\n"
        '        print("PHASE1_BENCH_CHECK=fail")\n'
        '        print(f"PHASE1_BENCH_CHECK_REASON={kind}")\n'
        '        print(f"PHASE1_BENCH_EXPECTATIONS={expectations_file}")\n'
        '        print(f"EXPECTATIONS_JSON_ERROR={exc.msg}")\n'
        '        print(f"EXPECTATIONS_JSON_LINE={exc.lineno}")\n'
        '        print(f"EXPECTATIONS_JSON_COLUMN={exc.colno}")\n'
        "        return 1\n"
        "    return 0\n"
    )


def write_sample_root(root: Path) -> None:
    write_text(bench_checker_path(root), sample_checker_text())


def assert_case(condition: bool, name: str, payload: object = None) -> None:
    if not condition:
        raise AssertionError((name, payload))


def run_self_test() -> None:
    case_count = 0

    with tempfile.TemporaryDirectory(prefix="lane16-json-error-packet-") as tmp:
        root = Path(tmp)

        failures = collect_failures(root)
        assert_case(
            failures == [f"missing_file:{BENCH_CHECKER_REL.as_posix()}"],
            "missing file",
            failures,
        )
        case_count += 1

        write_sample_root(root)
        failures = collect_failures(root)
        assert_case(not failures, "baseline pass", failures)
        case_count += 1

        missing_reason_text = sample_checker_text().replace(
            '        print(f"PHASE1_BENCH_CHECK_REASON={kind}")\n', "", 1
        )
        write_text(bench_checker_path(root), missing_reason_text)
        failures = collect_failures(root)
        assert_case(
            failures
            == [
                'required_marker_count:        print(f"PHASE1_BENCH_CHECK_REASON={kind}"):expected=1:actual=0'
            ],
            "missing reason marker",
            failures,
        )
        case_count += 1

        missing_expectations_text = sample_checker_text().replace(
            '        print(f"PHASE1_BENCH_EXPECTATIONS={expectations_file}")\n', "", 1
        )
        write_text(bench_checker_path(root), missing_expectations_text)
        failures = collect_failures(root)
        assert_case(
            failures
            == [
                'required_marker_count:        print(f"PHASE1_BENCH_EXPECTATIONS={expectations_file}"):expected=1:actual=0'
            ],
            "missing expectations marker",
            failures,
        )
        case_count += 1

        reordered_text = sample_checker_text().replace(
            '        print(f"EXPECTATIONS_JSON_LINE={exc.lineno}")\n'
            '        print(f"EXPECTATIONS_JSON_COLUMN={exc.colno}")\n',
            '        print(f"EXPECTATIONS_JSON_COLUMN={exc.colno}")\n'
            '        print(f"EXPECTATIONS_JSON_LINE={exc.lineno}")\n',
            1,
        )
        write_text(bench_checker_path(root), reordered_text)
        failures = collect_failures(root)
        assert_case(
            failures
            == [
                'required_marker_order:        print(f"EXPECTATIONS_JSON_COLUMN={exc.colno}")'
            ],
            "marker order",
            failures,
        )
        case_count += 1

    print("PHASE1_BENCH_JSON_ERROR_PACKET_SELF_TEST=pass")
    print(f"PHASE1_BENCH_JSON_ERROR_PACKET_SELF_TEST_CASE_COUNT={case_count}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Fail-close on the current malformed Phase 1 bench expectations error packet."
    )
    parser.add_argument("--root", help="Override the repository root used for validation.")
    parser.add_argument(
        "--write-sample-root",
        help="Write a minimal passing sample root to the given path.",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run checker self-tests without reading a repository root.",
    )
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return 0

    if args.write_sample_root:
        write_sample_root(Path(args.write_sample_root).resolve())
        return 0

    failures = collect_failures(repo_root(args.root))
    if failures:
        print("PHASE1_BENCH_JSON_ERROR_PACKET=fail")
        for failure in failures:
            print(failure)
        return 1

    print("PHASE1_BENCH_JSON_ERROR_PACKET=pass")
    print(f"PHASE1_BENCH_JSON_ERROR_PACKET_FILE={BENCH_CHECKER_REL.as_posix()}")
    print(f"PHASE1_BENCH_JSON_ERROR_PACKET_MARKER_COUNT={len(REQUIRED_MARKERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
