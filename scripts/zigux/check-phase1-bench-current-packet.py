#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
import tempfile
from pathlib import Path


CHECKER_REL = Path("scripts/zigux/check-phase1-bench.py")

EXPECTED_SECTIONS = (
    {
        "first_line": '    status_mismatch_output = ok_output.replace(',
        "expected_lines": (
            '    status_mismatch_output = ok_output.replace(',
            '        "PHASE1_BENCH=pass",',
            '        "PHASE1_BENCH=fail",',
            "        1,",
            "    )",
            "    kind, payload = validate_output(expectations, status_mismatch_output)",
            '    assert kind == "status"',
            '    assert payload == ("pass", "fail")',
        ),
    },
    {
        "first_line": "    for key, value, expected_kind in (",
        "expected_lines": (
            "    for key, value, expected_kind in (",
            '        ("PHASE1_BENCH_STRING_CHECKSUM", "5", "missing_string_exact_checksums"),',
            '        ("PHASE1_BENCH_HWEIGHT_CHECKSUM", "6", "missing_hweight_exact_checksums"),',
            '        ("PHASE1_BENCH_LIST_SORT_CHECKSUM", "7", "missing_list_sort_exact_checksums"),',
            "    ):",
            '        missing_output = ok_output.replace(f"\\n{key}={value}", "")',
            "        kind, payload = validate_output(expectations, missing_output)",
            "        assert kind == expected_kind",
            "        assert payload == [key]",
        ),
    },
    {
        'first_line': '    if kind == "expectations_json_error":',
        "expected_lines": (
            '    if kind == "expectations_json_error":',
            "        exc = payload",
            "        assert isinstance(exc, json.JSONDecodeError)",
            '        print("PHASE1_BENCH_CHECK=fail")',
            '        print("EXPECTATIONS_JSON_ERROR={}".format(exc.msg))',
            '        print("EXPECTATIONS_JSON_LINE={}".format(exc.lineno))',
            '        print("EXPECTATIONS_JSON_COLUMN={}".format(exc.colno))',
            "        return 1",
        ),
    },
)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def extract_assert_section(text: str, first_line: str) -> tuple[str, object]:
    lines = text.splitlines()
    matches = [index for index, line in enumerate(lines) if line.strip() == first_line.strip()]
    if not matches:
        return ("missing_first_line", first_line)
    if len(matches) > 1:
        return ("duplicate_first_line", (first_line, len(matches)))

    start = matches[0]
    section: list[str] = []
    for line in lines[start:]:
        stripped = line.strip()
        if section and stripped == "":
            break
        if stripped:
            section.append(line.rstrip().strip())
    return ("pass", section)


def section_contains_expected_lines(
    section_lines: list[str], expected_lines: tuple[str, ...]
) -> bool:
    normalized_expected = [line.strip() for line in expected_lines]
    position = 0
    for line in section_lines:
        if line == normalized_expected[position]:
            position += 1
            if position == len(normalized_expected):
                return True
    return False


def collect_issues(text: str) -> list[str]:
    issues: list[str] = []
    for section_spec in EXPECTED_SECTIONS:
        first_line = section_spec["first_line"]
        expected_lines = section_spec["expected_lines"]
        kind, payload = extract_assert_section(text, first_line)
        if kind == "missing_first_line":
            issues.append(f"missing_first_line:{first_line}")
            continue
        if kind == "duplicate_first_line":
            _, count = payload
            issues.append(f"duplicate_first_line:{first_line}:{count}")
            continue

        actual_section = payload
        assert isinstance(actual_section, list)
        if not section_contains_expected_lines(actual_section, expected_lines):
            issues.append(f"assert_block:{first_line}:{actual_section!r}")
    return issues


def run_check(root: Path) -> tuple[str, object]:
    checker_path = root / CHECKER_REL
    if not checker_path.is_file():
        return ("missing_paths", [str(CHECKER_REL)])

    issues = collect_issues(read_text(checker_path))
    if issues:
        return ("assert_sections", issues)

    return (
        "pass",
        {
            "required_file_count": 1,
            "expected_section_count": len(EXPECTED_SECTIONS),
        },
    )


def write_sample_root(root: Path) -> None:
    (root / CHECKER_REL.parent).mkdir(parents=True, exist_ok=True)
    (root / CHECKER_REL).write_text(
        "\n".join(
            (
                "#!/usr/bin/env python3",
                "def run_self_test() -> None:",
                '    status_mismatch_output = ok_output.replace(',
                '        "PHASE1_BENCH=pass",',
                "        # harmless note between replace arguments",
                '        "PHASE1_BENCH=fail",',
                "        1,",
                "    )",
                "    kind, payload = validate_output(expectations, status_mismatch_output)",
                '    assert kind == "status"',
                '    assert payload == ("pass", "fail")',
                "",
                "    for key, value, expected_kind in (",
                '        ("PHASE1_BENCH_STRING_CHECKSUM", "5", "missing_string_exact_checksums"),',
                '        ("PHASE1_BENCH_SPARE_CHECKSUM", "55", "missing_spare_exact_checksums"),',
                '        ("PHASE1_BENCH_HWEIGHT_CHECKSUM", "6", "missing_hweight_exact_checksums"),',
                '        ("PHASE1_BENCH_LIST_SORT_CHECKSUM", "7", "missing_list_sort_exact_checksums"),',
                "    ):",
                '        missing_output = ok_output.replace(f"\\n{key}={value}", "")',
                "        kind, payload = validate_output(expectations, missing_output)",
                "        assert kind == expected_kind",
                "        assert payload == [key]",
                "",
                "def main() -> int:",
                '    if kind == "expectations_json_error":',
                "        exc = payload",
                "        assert isinstance(exc, json.JSONDecodeError)",
                '        print("PHASE1_BENCH_CHECK=fail")',
                '        print("EXPECTATIONS_JSON_ERROR={}".format(exc.msg))',
                '        print("EXPECTATIONS_JSON_LINE={}".format(exc.lineno))',
                '        print("EXPECTATIONS_JSON_COLUMN={}".format(exc.colno))',
                "        return 1",
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

    with tempfile.TemporaryDirectory(prefix="lane16-bench-current-packet-") as tmp:
        root = Path(tmp)
        write_sample_root(root)

        kind, payload = run_check(root)
        assert kind == "pass", (kind, payload)
        assert payload == {
            "required_file_count": 1,
            "expected_section_count": len(EXPECTED_SECTIONS),
        }
        case_count += 1

        (root / CHECKER_REL).unlink()
        kind, payload = run_check(root)
        expect(kind, "missing_paths", payload, [str(CHECKER_REL)])
        case_count += 1
        write_sample_root(root)

        checker_path = root / CHECKER_REL
        checker_path.write_text(
            read_text(checker_path).replace(
                '        ("PHASE1_BENCH_HWEIGHT_CHECKSUM", "6", "missing_hweight_exact_checksums"),\n',
                "",
                1,
            ),
            encoding="utf-8",
        )
        kind, payload = run_check(root)
        assert kind == "assert_sections", (kind, payload)
        assert any(
            issue.startswith("assert_block:    for key, value, expected_kind in (")
            for issue in payload
        ), payload
        case_count += 1
        write_sample_root(root)

        checker_path.write_text(
            read_text(checker_path)
            + '\n    if kind == "expectations_json_error":\n        return 1\n',
            encoding="utf-8",
        )
        kind, payload = run_check(root)
        assert kind == "assert_sections", (kind, payload)
        assert payload == ['duplicate_first_line:    if kind == "expectations_json_error"::2'], payload
        case_count += 1
        write_sample_root(root)

        checker_path.write_text(
            read_text(checker_path).replace(
                '        "PHASE1_BENCH=fail",\n',
                "",
                1,
            ),
            encoding="utf-8",
        )
        kind, payload = run_check(root)
        assert kind == "assert_sections", (kind, payload)
        assert any(
            issue.startswith("assert_block:    status_mismatch_output = ok_output.replace(")
            for issue in payload
        ), payload
        case_count += 1

    print("PHASE1_BENCH_CURRENT_PACKET_SELF_TEST=pass")
    print(f"PHASE1_BENCH_CURRENT_PACKET_SELF_TEST_CASE_COUNT={case_count}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check the current Phase 1 bench checker packet."
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
        help="Write a minimal sample root and exit.",
    )
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return 0

    if args.write_sample_root is not None:
        if args.write_sample_root.exists():
            shutil.rmtree(args.write_sample_root)
        write_sample_root(args.write_sample_root)
        print(f"PHASE1_BENCH_CURRENT_PACKET_SAMPLE_ROOT={args.write_sample_root}")
        return 0

    kind, payload = run_check(args.root)
    if kind != "pass":
        print("PHASE1_BENCH_CURRENT_PACKET=fail")
        print(f"PHASE1_BENCH_CURRENT_PACKET_REASON={kind}")
        print(payload)
        return 1

    assert isinstance(payload, dict)
    print("PHASE1_BENCH_CURRENT_PACKET=pass")
    print(
        "PHASE1_BENCH_CURRENT_PACKET_REQUIRED_FILE_COUNT={}".format(
            payload["required_file_count"]
        )
    )
    print(
        "PHASE1_BENCH_CURRENT_PACKET_EXPECTED_SECTION_COUNT={}".format(
            payload["expected_section_count"]
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
