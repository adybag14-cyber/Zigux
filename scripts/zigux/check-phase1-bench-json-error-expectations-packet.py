#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


SELF_PATH = Path(__file__).resolve()
DEFAULT_ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) >= 3 else SELF_PATH.parent

SELF_CHECKER_REL = Path("scripts/zigux/check-phase1-bench-json-error-expectations-packet.py")
BENCH_CHECKER_REL = Path("scripts/zigux/check-phase1-bench.py")

REQUIRED_FILES = (
    SELF_CHECKER_REL,
    BENCH_CHECKER_REL,
)

EXPECTED_JSON_ERROR_BLOCK = (
    'if kind == "expectations_json_error":',
    "exc = payload",
    "assert isinstance(exc, json.JSONDecodeError)",
    'print("PHASE1_BENCH_CHECK=fail")',
    'print(f"EXPECTATIONS_JSON_ERROR={exc.msg}")',
    'print(f"EXPECTATIONS_JSON_LINE={exc.lineno}")',
    'print(f"EXPECTATIONS_JSON_COLUMN={exc.colno}")',
    "return 1",
)

FORBIDDEN_JSON_ERROR_SECTION_FRAGMENTS = (
    'print(f"PHASE1_BENCH_EXPECTATIONS={EXPECTATIONS}")',
    'print(f"PHASE1_BENCH_EXPECTATIONS={expectations_file}")',
)


def repo_root(explicit_root: str | None) -> Path:
    return Path(explicit_root).resolve() if explicit_root else DEFAULT_ROOT


def read_text(root: Path, relative_path: Path) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def extract_section(text: str, first_line: str) -> list[str]:
    section: list[str] = []
    capturing = False
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not capturing:
            if line == first_line:
                capturing = True
                section.append(line)
            continue
        if not line:
            return section
        section.append(line)
    return section


def collect_missing_files(root: Path) -> list[str]:
    return [str(relative_path) for relative_path in REQUIRED_FILES if not (root / relative_path).is_file()]


def validate_json_error_section(root: Path) -> tuple[str, object]:
    text = read_text(root, BENCH_CHECKER_REL)
    first_line = EXPECTED_JSON_ERROR_BLOCK[0]
    section = extract_section(text, first_line)
    if not section:
        return ("missing_json_error_section", first_line)

    unexpected = [
        fragment
        for fragment in FORBIDDEN_JSON_ERROR_SECTION_FRAGMENTS
        if fragment in section
    ]
    if unexpected:
        return ("json_error_section_forbidden_fragments", unexpected)

    if section != list(EXPECTED_JSON_ERROR_BLOCK):
        return ("json_error_section_mismatch", section)

    return ("pass", None)


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def write_sample_root(root: Path, *, with_legacy_expectations_echo: bool = False) -> None:
    write_text(root / SELF_CHECKER_REL, "#!/usr/bin/env python3\nprint('fixture')\n")

    lines = [
        "#!/usr/bin/env python3",
        "import json",
        "",
        'if kind == "expectations_json_error":',
        "    exc = payload",
        "    assert isinstance(exc, json.JSONDecodeError)",
        '    print("PHASE1_BENCH_CHECK=fail")',
    ]
    if with_legacy_expectations_echo:
        lines.append('    print(f"PHASE1_BENCH_EXPECTATIONS={EXPECTATIONS}")')
    lines.extend(
        [
            '    print(f"EXPECTATIONS_JSON_ERROR={exc.msg}")',
            '    print(f"EXPECTATIONS_JSON_LINE={exc.lineno}")',
            '    print(f"EXPECTATIONS_JSON_COLUMN={exc.colno}")',
            "    return 1",
            "",
        ]
    )
    write_text(root / BENCH_CHECKER_REL, "\n".join(lines))


def run_self_test() -> None:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase1_bench_json_error_expectations_") as tmp_dir:
        root = Path(tmp_dir)

        write_sample_root(root)
        assert collect_missing_files(root) == []
        assert validate_json_error_section(root) == ("pass", None)
        case_count += 1

        write_sample_root(root)
        bench_checker = root / BENCH_CHECKER_REL
        bench_checker.write_text(
            bench_checker.read_text(encoding="utf-8").replace(
                "    assert isinstance(exc, json.JSONDecodeError)\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        kind, payload = validate_json_error_section(root)
        assert kind == "json_error_section_mismatch", (kind, payload)
        assert "assert isinstance(exc, json.JSONDecodeError)" not in payload
        case_count += 1

        write_sample_root(root)
        bench_checker.write_text(
            bench_checker.read_text(encoding="utf-8").replace(
                '    print(f"EXPECTATIONS_JSON_ERROR={exc.msg}")\n'
                '    print(f"EXPECTATIONS_JSON_LINE={exc.lineno}")\n',
                '    print(f"EXPECTATIONS_JSON_LINE={exc.lineno}")\n'
                '    print(f"EXPECTATIONS_JSON_ERROR={exc.msg}")\n',
                1,
            ),
            encoding="utf-8",
        )
        kind, payload = validate_json_error_section(root)
        assert kind == "json_error_section_mismatch", (kind, payload)
        case_count += 1

        write_sample_root(root, with_legacy_expectations_echo=True)
        kind, payload = validate_json_error_section(root)
        assert kind == "json_error_section_forbidden_fragments", (kind, payload)
        assert payload == ['print(f"PHASE1_BENCH_EXPECTATIONS={EXPECTATIONS}")']
        case_count += 1

        write_sample_root(root)
        (root / BENCH_CHECKER_REL).unlink()
        assert collect_missing_files(root) == [str(BENCH_CHECKER_REL)]
        case_count += 1

    print("PHASE1_BENCH_JSON_ERROR_EXPECTATIONS_PACKET_SELF_TEST=pass")
    print(f"PHASE1_BENCH_JSON_ERROR_EXPECTATIONS_PACKET_SELF_TEST_CASE_COUNT={case_count}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the bounded Lane 16 malformed-JSON bench packet on current master."
    )
    parser.add_argument("--self-test", action="store_true", help="Run built-in checker self-tests.")
    parser.add_argument("--root", help="Validate an alternate Zigux tree root.")
    parser.add_argument("--write-sample-root", help="Write a minimal sample root and exit.")
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return 0

    if args.write_sample_root is not None:
        write_sample_root(Path(args.write_sample_root))
        print(
            "PHASE1_BENCH_JSON_ERROR_EXPECTATIONS_PACKET_SAMPLE_ROOT="
            f"{Path(args.write_sample_root)}"
        )
        return 0

    root = repo_root(args.root)
    missing_files = collect_missing_files(root)
    if missing_files:
        print("PHASE1_BENCH_JSON_ERROR_EXPECTATIONS_PACKET=fail")
        print("MISSING_PHASE1_BENCH_JSON_ERROR_EXPECTATIONS_PACKET_FILES_START")
        for item in missing_files:
            print(item)
        print("MISSING_PHASE1_BENCH_JSON_ERROR_EXPECTATIONS_PACKET_FILES_END")
        return 1

    kind, payload = validate_json_error_section(root)
    if kind != "pass":
        print("PHASE1_BENCH_JSON_ERROR_EXPECTATIONS_PACKET=fail")
        print(f"PHASE1_BENCH_JSON_ERROR_EXPECTATIONS_PACKET_REASON={kind}")
        if isinstance(payload, list):
            for item in payload:
                print(item)
        else:
            print(payload)
        return 1

    print("PHASE1_BENCH_JSON_ERROR_EXPECTATIONS_PACKET=pass")
    print(f"PHASE1_BENCH_JSON_ERROR_EXPECTATIONS_PACKET_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(
        "PHASE1_BENCH_JSON_ERROR_EXPECTATIONS_PACKET_REQUIRED_SECTION_LINE_COUNT="
        f"{len(EXPECTED_JSON_ERROR_BLOCK)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
