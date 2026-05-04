#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve()
ROOT = SCRIPT_PATH.parents[2] if len(SCRIPT_PATH.parents) > 2 else SCRIPT_PATH.parent
SELF_TEST_CASE_COUNT = 22

DOCS_ROOT_PATH = Path("Documentation/zigux/README.md")
SCRIPTS_README_PATH = Path("scripts/zigux/README.md")
TESTS_README_PATH = Path("zigux/tests/README.md")
MANIFEST_PATH = Path("zigux/tests/phase6_helper_parity_manifest.json")
MAKEFILE_PATH = Path("zigux/Makefile")
REQUIRED_REVIEW_HELPER_PATHS = [
    Path("scripts/zigux/check-phase6-docs-root-external-parity.py"),
    Path("scripts/zigux/check-phase6-base64-catalog-evidence.py"),
]
REQUIRED_SCRIPT_PATHS = [
    Path("scripts/zigux/check-phase6-base64-c-parity.py"),
    Path("scripts/zigux/check-phase6-bsearch-c-parity.py"),
    Path("scripts/zigux/check-phase6-checksum-c-parity.py"),
    Path("scripts/zigux/check-phase6-hexdump-c-parity.py"),
]

EXTERNAL_PARITY_LINE = (
    "`python3 scripts/zigux/check-phase6-base64-c-parity.py`, "
    "`python3 scripts/zigux/check-phase6-bsearch-c-parity.py`, "
    "`python3 scripts/zigux/check-phase6-checksum-c-parity.py`, and "
    "`python3 scripts/zigux/check-phase6-hexdump-c-parity.py` are the shipped "
    "external C-vs-Zig review hooks for the bounded base64, bsearch, checksum, "
    "and hexdump portability surfaces."
)
DOCS_ROOT_VALIDATOR_LINE = (
    "`python3 scripts/zigux/validate-phase6.py`, `make -C zigux phase6-validate`, "
    "and `make -C zigux phase6` are the published validator-first shared replay "
    "path for the current Phase 6 helper tranche."
)
REQUIRED_SCRIPTS_README_LINES = [
    "- `check-phase6-docs-root-external-parity.py`",
    "- `check-phase6-base64-catalog-evidence.py`",
]
SCRIPTS_README_SELF_TEST_LINE = (
    "`validate-phase6.py --self-test` exercises the shared Phase 6 marker walk "
    "in a compact synthetic tree and fails if catalog-head provenance, "
    "script-README wording, perf-survey markers, shared-gates inventory, "
    "manifest `surveyed_commit`, or helper-local determinism evidence drifts."
)
REQUIRED_TESTS_README_LINES = [
    "- `scripts/zigux/check-phase6-docs-root-external-parity.py`",
    "- `scripts/zigux/check-phase6-base64-catalog-evidence.py`",
    "- `zigux/tests/phase6_base64_c_parity.zig`",
    "- `zigux/tests/phase6_base64_c_casegen.zig`",
    "- `zigux/tests/fixtures/phase6_base64_c_harness.c`",
    "- `zigux/tests/phase6_bsearch_c_parity.zig`",
    "- `zigux/tests/fixtures/phase6_bsearch_c_harness.c`",
    "- `zigux/tests/phase6_checksum_c_parity.zig`",
    "- `zigux/tests/fixtures/phase6_checksum_c_harness.c`",
    "- `zigux/tests/phase6_hexdump_c_parity.zig`",
    "- `zigux/tests/fixtures/phase6_hexdump_c_harness.c`",
]
REQUIRED_MANIFEST_EXACT_CHECKS = [
    "python3 scripts/zigux/check-phase6-docs-root-external-parity.py --self-test",
    "python3 scripts/zigux/check-phase6-docs-root-external-parity.py",
    "python3 scripts/zigux/check-phase6-base64-catalog-evidence.py --self-test",
    "python3 scripts/zigux/check-phase6-base64-catalog-evidence.py",
]
REQUIRED_MAKEFILE_LINES = [
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase6-docs-root-external-parity.py --self-test",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase6-docs-root-external-parity.py",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase6-base64-catalog-evidence.py --self-test",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase6-base64-catalog-evidence.py",
]
REQUIRED_FILE_COUNT = (
    5 + len(REQUIRED_REVIEW_HELPER_PATHS) + len(REQUIRED_SCRIPT_PATHS)
)
REQUIRED_LINE_COUNT = (
    2
    + len(REQUIRED_SCRIPTS_README_LINES)
    + 1
    + len(REQUIRED_TESTS_README_LINES)
    + len(REQUIRED_MANIFEST_EXACT_CHECKS)
    + len(REQUIRED_MAKEFILE_LINES)
)


def read_text(root: Path, relative_path: Path) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def normalized_lines(text: str) -> list[str]:
    return [line.strip() for line in text.splitlines()]


def count_exact_line(lines: list[str], expected: str) -> int:
    return sum(1 for line in lines if line == expected)


def validate(root: Path) -> list[str]:
    missing: list[str] = []

    required_paths = [
        DOCS_ROOT_PATH,
        SCRIPTS_README_PATH,
        TESTS_README_PATH,
        MANIFEST_PATH,
        MAKEFILE_PATH,
        *REQUIRED_REVIEW_HELPER_PATHS,
        *REQUIRED_SCRIPT_PATHS,
    ]
    for relative_path in required_paths:
        if not (root / relative_path).exists():
            missing.append(f"missing_file:{relative_path.as_posix()}")

    if missing:
        return missing

    docs_root_lines = normalized_lines(read_text(root, DOCS_ROOT_PATH))
    actual_count = count_exact_line(docs_root_lines, EXTERNAL_PARITY_LINE)
    if actual_count != 1:
        missing.append(
            "docs_root_external_parity_line:"
            f"expected=1:actual={actual_count}"
        )

    actual_count = count_exact_line(docs_root_lines, DOCS_ROOT_VALIDATOR_LINE)
    if actual_count != 1:
        missing.append(
            "docs_root_validator_line:"
            f"expected=1:actual={actual_count}"
        )

    scripts_readme_lines = normalized_lines(read_text(root, SCRIPTS_README_PATH))
    for line in REQUIRED_SCRIPTS_README_LINES:
        actual_count = count_exact_line(scripts_readme_lines, line)
        if actual_count != 1:
            missing.append(
                "scripts_readme_checker_line:"
                f"expected=1:actual={actual_count}:{line}"
            )

    actual_count = count_exact_line(
        scripts_readme_lines, SCRIPTS_README_SELF_TEST_LINE
    )
    if actual_count != 1:
        missing.append(
            "scripts_readme_self_test_line:"
            f"expected=1:actual={actual_count}:{SCRIPTS_README_SELF_TEST_LINE}"
        )

    tests_readme_lines = normalized_lines(read_text(root, TESTS_README_PATH))
    for line in REQUIRED_TESTS_README_LINES:
        actual_count = count_exact_line(tests_readme_lines, line)
        if actual_count != 1:
            missing.append(
                "tests_readme_external_portability_line:"
                f"expected=1:actual={actual_count}:{line}"
            )

    manifest = json.loads(read_text(root, MANIFEST_PATH))
    exact_checks = manifest.get("exact_checks")
    if not isinstance(exact_checks, list):
        missing.append("manifest_exact_checks:invalid")
    else:
        for command in REQUIRED_MANIFEST_EXACT_CHECKS:
            actual_count = sum(1 for item in exact_checks if item == command)
            if actual_count != 1:
                missing.append(
                    "manifest_exact_checks:"
                    f"expected=1:actual={actual_count}:{command}"
                )

    makefile_lines = normalized_lines(read_text(root, MAKEFILE_PATH))
    for line in REQUIRED_MAKEFILE_LINES:
        actual_count = count_exact_line(makefile_lines, line)
        if actual_count != 1:
            missing.append(
                "makefile_checker_line:"
                f"expected=1:actual={actual_count}:{line}"
            )

    return missing


def write(root: Path, relative_path: Path, content: str) -> None:
    target = root / relative_path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")


def build_fixture_tree(root: Path) -> None:
    write(
        root,
        DOCS_ROOT_PATH,
        "\n".join([EXTERNAL_PARITY_LINE, DOCS_ROOT_VALIDATOR_LINE]) + "\n",
    )
    write(
        root,
        SCRIPTS_README_PATH,
        "\n".join([*REQUIRED_SCRIPTS_README_LINES, SCRIPTS_README_SELF_TEST_LINE]) + "\n",
    )
    write(root, TESTS_README_PATH, "\n".join(REQUIRED_TESTS_README_LINES) + "\n")
    write(
        root,
        MANIFEST_PATH,
        json.dumps({"exact_checks": REQUIRED_MANIFEST_EXACT_CHECKS}, indent=2) + "\n",
    )
    write(root, MAKEFILE_PATH, "\n".join(REQUIRED_MAKEFILE_LINES) + "\n")
    for relative_path in [*REQUIRED_REVIEW_HELPER_PATHS, *REQUIRED_SCRIPT_PATHS]:
        write(root, relative_path, "# placeholder\n")


def expect_contains(items: list[str], needle: str) -> None:
    if needle not in items:
        raise AssertionError(f"missing expectation {needle}")


def run_self_test() -> int:
    try:
        with tempfile.TemporaryDirectory(prefix="phase6_docs_root_external_parity_") as temp_dir:
            root = Path(temp_dir)
            count = 0

            build_fixture_tree(root)
            if validate(root):
                raise AssertionError(validate(root))
            count += 1

            build_fixture_tree(root)
            docs_root = root / DOCS_ROOT_PATH
            docs_root.write_text("", encoding="utf-8")
            expect_contains(
                validate(root),
                "docs_root_external_parity_line:expected=1:actual=0",
            )
            count += 1

            build_fixture_tree(root)
            docs_root = root / DOCS_ROOT_PATH
            docs_root.write_text(
                f"{EXTERNAL_PARITY_LINE}\n{EXTERNAL_PARITY_LINE}\n{DOCS_ROOT_VALIDATOR_LINE}\n",
                encoding="utf-8",
            )
            expect_contains(
                validate(root),
                "docs_root_external_parity_line:expected=1:actual=2",
            )
            count += 1

            build_fixture_tree(root)
            docs_root = root / DOCS_ROOT_PATH
            docs_root.write_text(f"{EXTERNAL_PARITY_LINE}\n", encoding="utf-8")
            expect_contains(
                validate(root),
                "docs_root_validator_line:expected=1:actual=0",
            )
            count += 1

            build_fixture_tree(root)
            docs_root = root / DOCS_ROOT_PATH
            docs_root.write_text(
                "\n".join(
                    [
                        EXTERNAL_PARITY_LINE,
                        DOCS_ROOT_VALIDATOR_LINE,
                        DOCS_ROOT_VALIDATOR_LINE,
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            expect_contains(
                validate(root),
                "docs_root_validator_line:expected=1:actual=2",
            )
            count += 1

            build_fixture_tree(root)
            scripts_readme = root / SCRIPTS_README_PATH
            scripts_readme.write_text("", encoding="utf-8")
            expect_contains(
                validate(root),
                "scripts_readme_checker_line:expected=1:actual=0:- `check-phase6-docs-root-external-parity.py`",
            )
            count += 1

            build_fixture_tree(root)
            scripts_readme = root / SCRIPTS_README_PATH
            scripts_readme.write_text(
                "- `check-phase6-docs-root-external-parity.py`\n- `check-phase6-docs-root-external-parity.py`\n"
                f"- `check-phase6-base64-catalog-evidence.py`\n{SCRIPTS_README_SELF_TEST_LINE}\n",
                encoding="utf-8",
            )
            expect_contains(
                validate(root),
                "scripts_readme_checker_line:expected=1:actual=2:- `check-phase6-docs-root-external-parity.py`",
            )
            count += 1

            build_fixture_tree(root)
            scripts_readme = root / SCRIPTS_README_PATH
            scripts_readme.write_text(
                f"- `check-phase6-docs-root-external-parity.py`\n{SCRIPTS_README_SELF_TEST_LINE}\n",
                encoding="utf-8",
            )
            expect_contains(
                validate(root),
                "scripts_readme_checker_line:expected=1:actual=0:- `check-phase6-base64-catalog-evidence.py`",
            )
            count += 1

            build_fixture_tree(root)
            scripts_readme = root / SCRIPTS_README_PATH
            scripts_readme.write_text(
                "- `check-phase6-docs-root-external-parity.py`\n"
                "- `check-phase6-base64-catalog-evidence.py`\n"
                "- `check-phase6-base64-catalog-evidence.py`\n"
                f"{SCRIPTS_README_SELF_TEST_LINE}\n",
                encoding="utf-8",
            )
            expect_contains(
                validate(root),
                "scripts_readme_checker_line:expected=1:actual=2:- `check-phase6-base64-catalog-evidence.py`",
            )
            count += 1

            build_fixture_tree(root)
            scripts_readme = root / SCRIPTS_README_PATH
            scripts_readme.write_text(
                "\n".join(REQUIRED_SCRIPTS_README_LINES) + "\n",
                encoding="utf-8",
            )
            expect_contains(
                validate(root),
                f"scripts_readme_self_test_line:expected=1:actual=0:{SCRIPTS_README_SELF_TEST_LINE}",
            )
            count += 1

            build_fixture_tree(root)
            scripts_readme = root / SCRIPTS_README_PATH
            scripts_readme.write_text(
                "\n".join(
                    [
                        *REQUIRED_SCRIPTS_README_LINES,
                        SCRIPTS_README_SELF_TEST_LINE,
                        SCRIPTS_README_SELF_TEST_LINE,
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            expect_contains(
                validate(root),
                f"scripts_readme_self_test_line:expected=1:actual=2:{SCRIPTS_README_SELF_TEST_LINE}",
            )
            count += 1

            build_fixture_tree(root)
            tests_readme = root / TESTS_README_PATH
            tests_readme.write_text(
                "\n".join(REQUIRED_TESTS_README_LINES[1:]) + "\n",
                encoding="utf-8",
            )
            expect_contains(
                validate(root),
                "tests_readme_external_portability_line:expected=1:actual=0:- `scripts/zigux/check-phase6-docs-root-external-parity.py`",
            )
            count += 1

            build_fixture_tree(root)
            tests_readme = root / TESTS_README_PATH
            tests_readme.write_text(
                "\n".join(
                    [
                        REQUIRED_TESTS_README_LINES[0],
                        REQUIRED_TESTS_README_LINES[0],
                        *REQUIRED_TESTS_README_LINES[1:],
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            expect_contains(
                validate(root),
                "tests_readme_external_portability_line:expected=1:actual=2:- `scripts/zigux/check-phase6-docs-root-external-parity.py`",
            )
            count += 1

            build_fixture_tree(root)
            (root / REQUIRED_SCRIPT_PATHS[2]).unlink()
            expect_contains(
                validate(root),
                "missing_file:scripts/zigux/check-phase6-checksum-c-parity.py",
            )
            count += 1

            build_fixture_tree(root)
            (root / REQUIRED_REVIEW_HELPER_PATHS[1]).unlink()
            expect_contains(
                validate(root),
                "missing_file:scripts/zigux/check-phase6-base64-catalog-evidence.py",
            )
            count += 1

            build_fixture_tree(root)
            docs_root = root / DOCS_ROOT_PATH
            docs_root.write_text(
                docs_root.read_text(encoding="utf-8").replace(
                    "check-phase6-hexdump-c-parity.py",
                    "check-phase6-hexdump-c-parity.py --drift",
                    1,
                ),
                encoding="utf-8",
            )
            expect_contains(
                validate(root),
                "docs_root_external_parity_line:expected=1:actual=0",
            )
            count += 1

            build_fixture_tree(root)
            manifest_path = root / MANIFEST_PATH
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["exact_checks"] = manifest["exact_checks"][1:]
            manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
            expect_contains(
                validate(root),
                "manifest_exact_checks:expected=1:actual=0:python3 scripts/zigux/check-phase6-docs-root-external-parity.py --self-test",
            )
            count += 1

            build_fixture_tree(root)
            manifest_path = root / MANIFEST_PATH
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            kept_checks = [
                item
                for item in manifest["exact_checks"]
                if item != "python3 scripts/zigux/check-phase6-base64-catalog-evidence.py --self-test"
            ]
            manifest["exact_checks"] = kept_checks
            manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
            expect_contains(
                validate(root),
                "manifest_exact_checks:expected=1:actual=0:python3 scripts/zigux/check-phase6-base64-catalog-evidence.py --self-test",
            )
            count += 1

            build_fixture_tree(root)
            manifest_path = root / MANIFEST_PATH
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            kept_checks = [
                item
                for item in manifest["exact_checks"]
                if item != "python3 scripts/zigux/check-phase6-base64-catalog-evidence.py"
            ]
            manifest["exact_checks"] = kept_checks
            manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
            expect_contains(
                validate(root),
                "manifest_exact_checks:expected=1:actual=0:python3 scripts/zigux/check-phase6-base64-catalog-evidence.py",
            )
            count += 1

            build_fixture_tree(root)
            makefile = root / MAKEFILE_PATH
            kept_lines = [
                line
                for line in makefile.read_text(encoding="utf-8").splitlines()
                if line != REQUIRED_MAKEFILE_LINES[1]
            ]
            makefile.write_text("\n".join(kept_lines) + "\n", encoding="utf-8")
            expect_contains(
                validate(root),
                "makefile_checker_line:expected=1:actual=0:cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase6-docs-root-external-parity.py",
            )
            count += 1

            build_fixture_tree(root)
            makefile = root / MAKEFILE_PATH
            kept_lines = [
                line
                for line in makefile.read_text(encoding="utf-8").splitlines()
                if line != REQUIRED_MAKEFILE_LINES[2]
            ]
            makefile.write_text("\n".join(kept_lines) + "\n", encoding="utf-8")
            expect_contains(
                validate(root),
                "makefile_checker_line:expected=1:actual=0:cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase6-base64-catalog-evidence.py --self-test",
            )
            count += 1

            build_fixture_tree(root)
            makefile = root / MAKEFILE_PATH
            kept_lines = [
                line
                for line in makefile.read_text(encoding="utf-8").splitlines()
                if line != REQUIRED_MAKEFILE_LINES[3]
            ]
            makefile.write_text("\n".join(kept_lines) + "\n", encoding="utf-8")
            expect_contains(
                validate(root),
                "makefile_checker_line:expected=1:actual=0:cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase6-base64-catalog-evidence.py",
            )
            count += 1

            if count != SELF_TEST_CASE_COUNT:
                raise AssertionError(
                    f"expected {SELF_TEST_CASE_COUNT} self-test cases, got {count}"
                )
    except AssertionError as exc:
        print("PHASE6_DOCS_ROOT_EXTERNAL_PARITY_SELF_TEST=fail")
        print(f"PHASE6_DOCS_ROOT_EXTERNAL_PARITY_SELF_TEST_REASON={exc}")
        return 1

    print("PHASE6_DOCS_ROOT_EXTERNAL_PARITY_SELF_TEST=pass")
    print(f"PHASE6_DOCS_ROOT_EXTERNAL_PARITY_SELF_TEST_CASE_COUNT={SELF_TEST_CASE_COUNT}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Fail closed on the Phase 6 docs-root review inventory lines."
    )
    parser.add_argument("--self-test", action="store_true", help="Run built-in checks")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    missing = validate(ROOT)
    if missing:
        print("PHASE6_DOCS_ROOT_EXTERNAL_PARITY=fail")
        print("PHASE6_DOCS_ROOT_EXTERNAL_PARITY_MISSING_START")
        for item in missing:
            print(item)
        print("PHASE6_DOCS_ROOT_EXTERNAL_PARITY_MISSING_END")
        return 1

    print("PHASE6_DOCS_ROOT_EXTERNAL_PARITY=pass")
    print(f"PHASE6_DOCS_ROOT_EXTERNAL_PARITY_REQUIRED_FILE_COUNT={REQUIRED_FILE_COUNT}")
    print(f"PHASE6_DOCS_ROOT_EXTERNAL_PARITY_REQUIRED_LINE_COUNT={REQUIRED_LINE_COUNT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())