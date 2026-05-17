#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

SELF_PATH = Path(__file__).resolve()
ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) >= 3 else SELF_PATH.parent

REQUIRED_FILES = [
    "scripts/zigux/fixdep.zig",
    "scripts/zigux/check-phase2-fixdep-gate.py",
    "zigux/tests/README.md",
    "zigux/tests/fixtures/fixdep/cases.json",
]

TESTS_README_MARKERS = [
    "scripts/zigux/check-phase2-fixdep-gate.py",
    "zig test scripts/zigux/fixdep.zig",
]

EXPECTED_CASES = {
    "sample": {
        "depfile": "sample.d",
        "target": "sample.o",
        "cmdline": "clang -Iinclude -DZIGUX_SAMPLE -c zigux/tests/fixtures/fixdep/sample.c -o sample.o",
        "expected": "sample_expected.txt",
        "expected_exit_code": 0,
    },
    "sample_multi_target": {
        "depfile": "sample_multi_target.d",
        "target": "module/sample2.o",
        "cmdline": "clang -Iinclude -DZIGUX_MULTI -c zigux/tests/fixtures/fixdep/sample2.c -o module/sample2.o",
        "expected": "sample_multi_target_expected.txt",
        "expected_exit_code": 0,
    },
    "sample_escaped_space": {
        "depfile": "sample_escaped_space.d",
        "target": "sample_escaped_space.o",
        "cmdline": "clang -c zigux/tests/fixtures/fixdep/sample_escaped_space_source.c -o sample_escaped_space.o",
        "expected": "sample_escaped_space_expected.txt",
        "expected_exit_code": 0,
    },
    "sample_escaped_colon": {
        "depfile": "sample_escaped_colon.d",
        "target": "sample_escaped_colon.o",
        "cmdline": "clang -c zigux/tests/fixtures/fixdep/sample_escaped_colon_source.c -o sample_escaped_colon.o",
        "expected": "sample_escaped_colon_expected.txt",
        "expected_exit_code": 0,
    },
    "sample_concatenated": {
        "depfile": "sample_concatenated.d",
        "target": "sample_concatenated.o",
        "cmdline": "clang -c zigux/tests/fixtures/fixdep/sample_concatenated_source.c -o sample_concatenated.o",
        "expected": "sample_concatenated_expected.txt",
        "expected_exit_code": 0,
    },
    "sample_dependency_continuation": {
        "depfile": "sample_dependency_continuation.d",
        "target": "sample_dependency_continuation.o",
        "cmdline": "clang -c zigux/tests/fixtures/fixdep/sample_dependency_continuation_source.c -o sample_dependency_continuation.o",
        "expected": "sample_dependency_continuation_expected.txt",
        "expected_exit_code": 0,
    },
    "sample_comment_continuation": {
        "depfile": "sample_comment_continuation.d",
        "target": "sample_comment_continuation.o",
        "cmdline": "clang -c zigux/tests/fixtures/fixdep/sample_comment_continuation_source.c -o sample_comment_continuation.o",
        "expected": "sample_comment_continuation_expected.txt",
        "expected_exit_code": 0,
    },
    "sample_comment_only": {
        "depfile": "sample_comment_only.d",
        "target": "sample_comment_only.o",
        "cmdline": "clang -Iinclude -DZIGUX_SAMPLE -c zigux/tests/fixtures/fixdep/sample.c -o sample_comment_only.o",
        "expected": "sample_comment_only_expected.txt",
        "expected_stderr": "sample_comment_only_expected.stderr.txt",
        "expected_exit_code": 1,
    },
    "sample_comment_only_stdout_full": {
        "depfile": "sample_comment_only.d",
        "target": "sample_comment_only_stdout_full.o",
        "cmdline": "clang -Iinclude -DZIGUX_SAMPLE -c zigux/tests/fixtures/fixdep/sample.c -o sample_comment_only_stdout_full.o",
        "expected": "sample_output_write_expected.txt",
        "expected_stderr": "sample_comment_only_expected.stderr.txt",
        "expected_exit_code": 1,
        "stdout_mode": "dev_full",
    },
    "sample_missing_dep": {
        "depfile": "sample_missing_dep.d",
        "target": "sample_missing_dep.o",
        "cmdline": "clang -c zigux/tests/fixtures/fixdep/sample_missing_dep_source.c -o sample_missing_dep.o",
        "expected": "sample_missing_dep_expected.txt",
        "expected_stderr": "sample_missing_dep_expected.stderr.txt",
        "expected_exit_code": 2,
    },
    "sample_missing_dep_stdout_full": {
        "depfile": "sample_missing_dep.d",
        "target": "sample_missing_dep_stdout_full.o",
        "cmdline": "clang -c zigux/tests/fixtures/fixdep/sample_missing_dep_source.c -o sample_missing_dep_stdout_full.o",
        "expected": "sample_output_write_expected.txt",
        "expected_stderr": "sample_missing_dep_expected.stderr.txt",
        "expected_exit_code": 2,
        "stdout_mode": "dev_full",
    },
    "sample_output_write": {
        "depfile": "sample.d",
        "target": "sample_output_write.o",
        "cmdline": "clang -Iinclude -DZIGUX_SAMPLE -c zigux/tests/fixtures/fixdep/sample.c -o sample_output_write.o",
        "expected": "sample_output_write_expected.txt",
        "expected_stderr": "sample_output_write_expected.stderr.txt",
        "expected_exit_code": 1,
        "stdout_mode": "dev_full",
    },
}

EXPECTED_CASE_ORDER = list(EXPECTED_CASES)

EXPECTED_FIXTURE_FILES = frozenset(
    {
        "cases.json",
        r"escaped\ space-config.h",
        "sample-config.h",
        "sample.c",
        "sample.d",
        "sample.h",
        "sample.rmeta",
        "sample2-config.h",
        "sample2.c",
        "sample2.so",
        "sample_comment_continuation.d",
        "sample_comment_continuation_dep.so",
        "sample_comment_continuation_expected.txt",
        "sample_comment_continuation_source.rmeta",
        "sample_comment_only.d",
        "sample_comment_only_expected.stderr.txt",
        "sample_comment_only_expected.txt",
        "sample_concatenated.d",
        "sample_concatenated_dep.h",
        "sample_concatenated_expected.txt",
        "sample_concatenated_source.c",
        "sample_concatenated_temp.c",
        "sample_concatenated_temp_dep.h",
        "sample_dependency_continuation.d",
        "sample_dependency_continuation_expected.txt",
        "sample_escaped_colon.d",
        "sample_escaped_colon_expected.txt",
        "sample_escaped_colon_source.c",
        "sample_escaped_space.d",
        "sample_escaped_space_expected.txt",
        "sample_escaped_space_source.c",
        "sample_expected.txt",
        "sample_missing_dep.d",
        "sample_missing_dep_expected.stderr.txt",
        "sample_missing_dep_expected.txt",
        "sample_missing_dep_source.c",
        "sample_multi_target.d",
        "sample_multi_target_expected.txt",
        "sample_output_write_expected.stderr.txt",
        "sample_output_write_expected.txt",
        "shared#config.h",
        "shared:config.h",
    }
)

EXACT_FILE_CONTENTS = {
    "zigux/tests/fixtures/fixdep/sample_comment_continuation_expected.txt": (
        "savedcmd_sample_comment_continuation.o := clang -c "
        "zigux/tests/fixtures/fixdep/sample_comment_continuation_source.c -o "
        "sample_comment_continuation.o\n\n"
        "source_sample_comment_continuation.o := "
        "zigux/tests/fixtures/fixdep/sample_comment_continuation_source.rmeta\n\n"
        "deps_sample_comment_continuation.o := \\\n"
        "  zigux/tests/fixtures/fixdep/sample_comment_continuation_dep.so \\\n\n"
        "sample_comment_continuation.o: $(deps_sample_comment_continuation.o)\n\n"
        "$(deps_sample_comment_continuation.o):\n"
    ),
    "zigux/tests/fixtures/fixdep/sample_dependency_continuation_expected.txt": (
        "savedcmd_sample_dependency_continuation.o := clang -c "
        "zigux/tests/fixtures/fixdep/sample_dependency_continuation_source.c -o "
        "sample_dependency_continuation.o\n\n"
        "source_sample_dependency_continuation.o := sample_dependency_continuation_source.rmeta\n\n"
        "deps_sample_dependency_continuation.o := \\\n"
        "  sample_dependency_continuation_dep_one.so \\\n"
        "  sample_dependency_continuation_dep_two.so \\\n"
        "  sample_dependency_continuation_dep_three.so \\\n\n"
        "sample_dependency_continuation.o: $(deps_sample_dependency_continuation.o)\n\n"
        "$(deps_sample_dependency_continuation.o):\n"
    ),
    "zigux/tests/fixtures/fixdep/sample_comment_only_expected.stderr.txt": (
        "fixdep: parse error; no targets found\n"
    ),
    "zigux/tests/fixtures/fixdep/sample_missing_dep_expected.stderr.txt": (
        "fixdep: error opening file: "
        "zigux/tests/fixtures/fixdep/sample_missing_dep.h: No such file or directory\n"
    ),
    "zigux/tests/fixtures/fixdep/sample_output_write_expected.stderr.txt": (
        "fixdep: not all data was written to the output\n"
    ),
}

ZERO_BYTE_FILES = [
    "zigux/tests/fixtures/fixdep/sample_comment_continuation_dep.so",
    "zigux/tests/fixtures/fixdep/sample_comment_continuation_source.rmeta",
]

EXPECTED_STDOUT_MODE_CASES = {
    "sample_comment_only_stdout_full",
    "sample_missing_dep_stdout_full",
    "sample_output_write",
}

EXPECTED_SELF_TEST_CASE_COUNT = 6


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def validate_required_files(root: Path) -> list[str]:
    return [path for path in REQUIRED_FILES if not (root / path).is_file()]


def validate_tests_readme(root: Path) -> list[str]:
    issues: list[str] = []
    text = read_text(root / "zigux/tests/README.md")
    for marker in TESTS_README_MARKERS:
        if marker not in text:
            issues.append(f"zigux/tests/README.md:missing_marker:{marker}")
    return issues


def validate_fixture_inventory(root: Path) -> list[str]:
    fixture_dir = root / "zigux/tests/fixtures/fixdep"
    actual = {path.name for path in fixture_dir.iterdir() if path.is_file()}
    missing = sorted(EXPECTED_FIXTURE_FILES - actual)
    unexpected = sorted(actual - EXPECTED_FIXTURE_FILES)
    issues: list[str] = []
    if missing:
        issues.append(
            "zigux/tests/fixtures/fixdep:missing_fixtures:" + ",".join(missing)
        )
    if unexpected:
        issues.append(
            "zigux/tests/fixtures/fixdep:unexpected_fixtures:" + ",".join(unexpected)
        )
    return issues


def validate_cases(root: Path) -> list[str]:
    issues: list[str] = []
    cases_path = root / "zigux/tests/fixtures/fixdep/cases.json"
    try:
        cases = json.loads(read_text(cases_path))
    except json.JSONDecodeError as exc:
        return [f"zigux/tests/fixtures/fixdep/cases.json:json:{exc.msg}"]

    if not isinstance(cases, list):
        return ["zigux/tests/fixtures/fixdep/cases.json:type"]

    names: list[str] = []
    for index, case in enumerate(cases):
        label = f"zigux/tests/fixtures/fixdep/cases.json:cases[{index}]"
        if not isinstance(case, dict):
            issues.append(f"{label}:type")
            continue
        name = case.get("name")
        if not isinstance(name, str):
            issues.append(f"{label}:missing_name")
            continue
        names.append(name)
        expected = EXPECTED_CASES.get(name)
        if expected is None:
            issues.append(f"{label}:unexpected_name:{name}")
            continue
        for key, expected_value in expected.items():
            if case.get(key) != expected_value:
                issues.append(
                    f"{label}:{name}:{key}:expected={expected_value!r}:got={case.get(key)!r}"
                )

        extra_keys = sorted(set(case) - set(expected) - {"name"})
        if extra_keys:
            issues.append(f"{label}:{name}:unexpected_keys:{','.join(extra_keys)}")

    if names != EXPECTED_CASE_ORDER:
        issues.append(
            "zigux/tests/fixtures/fixdep/cases.json:order:expected="
            + ",".join(EXPECTED_CASE_ORDER)
            + ":got="
            + ",".join(names)
        )

    stdout_mode_cases = {
        case["name"]
        for case in cases
        if isinstance(case, dict) and case.get("stdout_mode") == "dev_full"
    }
    if stdout_mode_cases != EXPECTED_STDOUT_MODE_CASES:
        issues.append(
            "zigux/tests/fixtures/fixdep/cases.json:stdout_mode_cases:expected="
            + ",".join(sorted(EXPECTED_STDOUT_MODE_CASES))
            + ":got="
            + ",".join(sorted(stdout_mode_cases))
        )

    return issues


def validate_exact_files(root: Path) -> list[str]:
    issues: list[str] = []
    for rel_path, expected in EXACT_FILE_CONTENTS.items():
        actual = read_text(root / rel_path)
        if actual != expected:
            issues.append(rel_path + ":content")
    return issues


def validate_zero_byte_files(root: Path) -> list[str]:
    issues: list[str] = []
    for rel_path in ZERO_BYTE_FILES:
        if (root / rel_path).stat().st_size != 0:
            issues.append(rel_path + ":expected_zero_bytes")
    return issues


def collect_issues(root: Path) -> list[str]:
    issues: list[str] = []
    missing_required = validate_required_files(root)
    if missing_required:
        return [f"missing_required:{path}" for path in missing_required]
    issues.extend(validate_tests_readme(root))
    issues.extend(validate_fixture_inventory(root))
    issues.extend(validate_cases(root))
    issues.extend(validate_exact_files(root))
    issues.extend(validate_zero_byte_files(root))
    return issues


def ensure_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def ensure_zero_byte(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"")


def build_self_test_tree(root: Path) -> None:
    ensure_text(root / "scripts/zigux/fixdep.zig", "test lane11_fixdep_gate_placeholder {}\n")
    ensure_text(
        root / "zigux/tests/README.md",
        "Phase 2 review packet: scripts/zigux/check-phase2-fixdep-gate.py\n"
        "Direct replay: zig test scripts/zigux/fixdep.zig\n",
    )
    ensure_text(root / "scripts/zigux/check-phase2-fixdep-gate.py", "placeholder\n")

    fixture_root = root / "zigux/tests/fixtures/fixdep"
    for name in EXPECTED_FIXTURE_FILES:
        path = fixture_root / name
        if name == "cases.json":
            ensure_text(
                path,
                json.dumps(
                    [{"name": key, **value} for key, value in EXPECTED_CASES.items()],
                    indent=2,
                )
                + "\n",
            )
        elif name == "sample_comment_continuation_dep.so":
            ensure_zero_byte(path)
        elif name == "sample_comment_continuation_source.rmeta":
            ensure_zero_byte(path)
        elif f"zigux/tests/fixtures/fixdep/{name}" in EXACT_FILE_CONTENTS:
            ensure_text(path, EXACT_FILE_CONTENTS[f"zigux/tests/fixtures/fixdep/{name}"])
        else:
            ensure_text(path, f"{name}\n")


def run_self_test() -> None:
    with tempfile.TemporaryDirectory(prefix="phase2-fixdep-gate-") as tmp:
        root = Path(tmp)
        build_self_test_tree(root)

        issues = collect_issues(root)
        if issues:
            raise SystemExit("self-test valid tree failed:\n" + "\n".join(issues))

        broken_cases = json.loads(read_text(root / "zigux/tests/fixtures/fixdep/cases.json"))
        broken_cases[0]["target"] = "drifted.o"
        ensure_text(
            root / "zigux/tests/fixtures/fixdep/cases.json",
            json.dumps(broken_cases, indent=2) + "\n",
        )
        issues = collect_issues(root)
        if not any(":sample:target:" in issue for issue in issues):
            raise SystemExit("self-test expected target drift issue")

        build_self_test_tree(root)
        ensure_text(
            root / "zigux/tests/README.md",
            "Phase 2 review packet without the gate marker\n",
        )
        issues = collect_issues(root)
        if not any("zigux/tests/README.md:missing_marker:" in issue for issue in issues):
            raise SystemExit("self-test expected README marker issue")

        build_self_test_tree(root)
        ensure_text(
            root / "zigux/tests/fixtures/fixdep/sample_output_write_expected.stderr.txt",
            "wrong\n",
        )
        issues = collect_issues(root)
        if "zigux/tests/fixtures/fixdep/sample_output_write_expected.stderr.txt:content" not in issues:
            raise SystemExit("self-test expected exact-content issue")

        build_self_test_tree(root)
        ensure_text(
            root / "zigux/tests/fixtures/fixdep/sample_comment_continuation_dep.so",
            "not-empty\n",
        )
        issues = collect_issues(root)
        if (
            "zigux/tests/fixtures/fixdep/sample_comment_continuation_dep.so:expected_zero_bytes"
            not in issues
        ):
            raise SystemExit("self-test expected zero-byte issue")

        build_self_test_tree(root)
        (root / "zigux/tests/fixtures/fixdep/unexpected.txt").write_text(
            "unexpected\n",
            encoding="utf-8",
        )
        issues = collect_issues(root)
        if not any(":unexpected_fixtures:" in issue for issue in issues):
            raise SystemExit("self-test expected inventory issue")

    print("PHASE2_FIXDEP_GATE_SELF_TEST=pass")
    print(f"PHASE2_FIXDEP_GATE_SELF_TEST_CASE_COUNT={EXPECTED_SELF_TEST_CASE_COUNT}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Validate the bounded Lane 11 fixdep fixture packet against the current gate contract."
    )
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return

    issues = collect_issues(args.root)
    if issues:
        raise SystemExit("\n".join(issues))

    print("PHASE2_FIXDEP_GATE=pass")
    print(f"PHASE2_FIXDEP_CASE_COUNT={len(EXPECTED_CASE_ORDER)}")
    print(f"PHASE2_FIXDEP_FIXTURE_COUNT={len(EXPECTED_FIXTURE_FILES)}")


if __name__ == "__main__":
    main()
