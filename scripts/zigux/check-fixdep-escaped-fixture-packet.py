#!/usr/bin/env python3
"""Check the escaped-space and escaped-colon fixdep fixture packet."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent
FIXTURE_DIR = Path("zigux/tests/fixtures/fixdep")
CASES_PATH = FIXTURE_DIR / "cases.json"

EXPECTED_CASES = (
    {
        "name": "sample_escaped_space",
        "depfile": "sample_escaped_space.d",
        "target": "sample_escaped_space.o",
        "cmdline": "clang -c zigux/tests/fixtures/fixdep/sample_escaped_space_source.c -o sample_escaped_space.o",
        "expected": "sample_escaped_space_expected.txt",
        "expected_exit_code": 0,
    },
    {
        "name": "sample_escaped_colon",
        "depfile": "sample_escaped_colon.d",
        "target": "sample_escaped_colon.o",
        "cmdline": "clang -c zigux/tests/fixtures/fixdep/sample_escaped_colon_source.c -o sample_escaped_colon.o",
        "expected": "sample_escaped_colon_expected.txt",
        "expected_exit_code": 0,
    },
)

EXPECTED_FILES = {
    "dep\\ name.rmeta": "",
    "dep:colon.so": "",
    "sample_escaped_space_source.c": "",
    "sample_escaped_space_source.rmeta": "",
    "sample_escaped_colon_source.c": "",
    "sample_escaped_colon_source.rmeta": "",
    "sample_escaped_space.d": (
        "sample_escaped_space.o: zigux/tests/fixtures/fixdep/sample_escaped_space_source.rmeta \\\n"
        " zigux/tests/fixtures/fixdep/dep\\ name.rmeta\n"
    ),
    "sample_escaped_colon.d": (
        "sample_escaped_colon.o: zigux/tests/fixtures/fixdep/sample_escaped_colon_source.rmeta \\\n"
        " zigux/tests/fixtures/fixdep/dep\\:colon.so\n"
    ),
    "sample_escaped_space_expected.txt": (
        "savedcmd_sample_escaped_space.o := clang -c zigux/tests/fixtures/fixdep/sample_escaped_space_source.c -o sample_escaped_space.o\n\n"
        "source_sample_escaped_space.o := zigux/tests/fixtures/fixdep/sample_escaped_space_source.rmeta\n\n"
        "deps_sample_escaped_space.o := \\\n"
        "  zigux/tests/fixtures/fixdep/dep\\ name.rmeta \\\n\n"
        "sample_escaped_space.o: $(deps_sample_escaped_space.o)\n\n"
        "$(deps_sample_escaped_space.o):\n"
    ),
    "sample_escaped_colon_expected.txt": (
        "savedcmd_sample_escaped_colon.o := clang -c zigux/tests/fixtures/fixdep/sample_escaped_colon_source.c -o sample_escaped_colon.o\n\n"
        "source_sample_escaped_colon.o := zigux/tests/fixtures/fixdep/sample_escaped_colon_source.rmeta\n\n"
        "deps_sample_escaped_colon.o := \\\n"
        "  zigux/tests/fixtures/fixdep/dep:colon.so \\\n\n"
        "sample_escaped_colon.o: $(deps_sample_escaped_colon.o)\n\n"
        "$(deps_sample_escaped_colon.o):\n"
    ),
}

EXPECTED_SELF_TEST_CASE_COUNT = 7


def resolve(root: Path, rel: Path) -> Path:
    return root / rel


def load_cases(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_cases(root: Path) -> None:
    raw_cases = load_cases(resolve(root, CASES_PATH))
    if not isinstance(raw_cases, list):
        raise ValueError(f"{CASES_PATH}:expected_json_list")

    names = [case.get("name") for case in raw_cases if isinstance(case, dict)]
    for expected_case in EXPECTED_CASES:
        name = expected_case["name"]
        if name not in names:
            raise ValueError(f"{CASES_PATH}:missing_case:{name}")

        case = next(case for case in raw_cases if isinstance(case, dict) and case.get("name") == name)
        for key, expected_value in expected_case.items():
            actual_value = case.get(key, 0 if key == "expected_exit_code" else None)
            if actual_value != expected_value:
                raise ValueError(
                    f"{CASES_PATH}:{name}:{key}={actual_value!r},expected={expected_value!r}"
                )


def validate_files(root: Path) -> None:
    fixture_root = resolve(root, FIXTURE_DIR)
    for name, expected_text in EXPECTED_FILES.items():
        path = fixture_root / name
        if not path.exists():
            raise FileNotFoundError(f"{fixture_root}:missing_fixture:{name}")
        actual_text = path.read_text(encoding="utf-8")
        if actual_text != expected_text:
            raise ValueError(f"{path}:content_mismatch")


def collect_issues(root: Path) -> list[str]:
    issues: list[str] = []
    try:
        validate_cases(root)
    except (ValueError, json.JSONDecodeError) as exc:
        issues.append(str(exc))
    try:
        validate_files(root)
    except (ValueError, FileNotFoundError) as exc:
        issues.append(str(exc))
    return issues


def emit_issues(issues: list[str]) -> int:
    print("FIXDEP_ESCAPED_FIXTURE_PACKET=fail")
    for issue in issues:
        print(issue)
    return 1


def write_case_packet(root: Path) -> None:
    fixture_root = resolve(root, FIXTURE_DIR)
    fixture_root.mkdir(parents=True, exist_ok=True)
    for name, text in EXPECTED_FILES.items():
        (fixture_root / name).write_text(text, encoding="utf-8")

    unrelated_case = {
        "name": "sample",
        "depfile": "sample.d",
        "target": "sample.o",
        "cmdline": "clang -Iinclude -DZIGUX_SAMPLE -c zigux/tests/fixtures/fixdep/sample.c -o sample.o",
        "expected": "sample_expected.txt",
        "expected_exit_code": 0,
    }
    cases = [unrelated_case, *EXPECTED_CASES]
    resolve(root, CASES_PATH).write_text(json.dumps(cases, indent=2) + "\n", encoding="utf-8")


def expect_failure(label: str, callback, expected_message: str) -> None:
    try:
        callback()
    except (ValueError, FileNotFoundError, json.JSONDecodeError) as exc:
        actual_message = str(exc)
        if actual_message != expected_message:
            raise SystemExit(
                f"escaped-fixture:self-test:{label}:expected={expected_message!r}:actual={actual_message!r}"
            ) from exc
        return
    raise SystemExit(f"escaped-fixture:self-test:{label}:missing_failure:{expected_message!r}")


def run_self_test() -> int:
    checks_run = 0
    with tempfile.TemporaryDirectory(prefix="zigux_fixdep_escaped_fixture_") as tmp_dir:
        root = Path(tmp_dir)

        write_case_packet(root)
        assert collect_issues(root) == []
        checks_run += 1

        write_case_packet(root)
        path = resolve(root, CASES_PATH)
        cases = json.loads(path.read_text(encoding="utf-8"))
        cases[1]["expected"] = "wrong_expected.txt"
        path.write_text(json.dumps(cases, indent=2) + "\n", encoding="utf-8")
        expect_failure(
            "wrong_expected_name",
            lambda: validate_cases(root),
            f"{CASES_PATH}:sample_escaped_space:expected='wrong_expected.txt',expected='sample_escaped_space_expected.txt'",
        )
        checks_run += 1

        write_case_packet(root)
        path = resolve(root, FIXTURE_DIR / "sample_escaped_space_expected.txt")
        path.unlink()
        expect_failure(
            "missing_expected_output",
            lambda: validate_files(root),
            f"{resolve(root, FIXTURE_DIR)}:missing_fixture:sample_escaped_space_expected.txt",
        )
        checks_run += 1

        write_case_packet(root)
        path = resolve(root, FIXTURE_DIR / "sample_escaped_space_expected.txt")
        path.write_text("broken\n", encoding="utf-8")
        expect_failure(
            "space_expected_mismatch",
            lambda: validate_files(root),
            f"{path}:content_mismatch",
        )
        checks_run += 1

        write_case_packet(root)
        path = resolve(root, FIXTURE_DIR / "sample_escaped_colon_expected.txt")
        path.write_text("broken\n", encoding="utf-8")
        expect_failure(
            "colon_expected_mismatch",
            lambda: validate_files(root),
            f"{path}:content_mismatch",
        )
        checks_run += 1

        write_case_packet(root)
        path = resolve(root, FIXTURE_DIR / "sample_escaped_space.d")
        path.write_text("broken\n", encoding="utf-8")
        expect_failure(
            "space_depfile_mismatch",
            lambda: validate_files(root),
            f"{path}:content_mismatch",
        )
        checks_run += 1

        write_case_packet(root)
        path = resolve(root, CASES_PATH)
        path.write_text("{broken\n", encoding="utf-8")
        issues = collect_issues(root)
        assert any("Expecting property name enclosed in double quotes" in issue for issue in issues)
        checks_run += 1

    assert checks_run == EXPECTED_SELF_TEST_CASE_COUNT
    print("FIXDEP_ESCAPED_FIXTURE_PACKET_SELF_TEST=pass")
    print(f"FIXDEP_ESCAPED_FIXTURE_PACKET_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check the escaped-space and escaped-colon fixdep fixture packet."
    )
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("FIXDEP_ESCAPED_FIXTURE_PACKET=pass")
    print(f"FIXDEP_ESCAPED_FIXTURE_REQUIRED_CASE_COUNT={len(EXPECTED_CASES)}")
    print(f"FIXDEP_ESCAPED_FIXTURE_REQUIRED_FILE_COUNT={len(EXPECTED_FILES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())