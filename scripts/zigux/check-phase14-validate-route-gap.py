#!/usr/bin/env python3

from __future__ import annotations

import argparse
import ast
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
VALIDATOR_PATH = "scripts/zigux/validate-phase14.py"
MAKEFILE_PATH = "zigux/Makefile"
VALIDATE_TARGET_HEADER = "phase14-validate:"
VALIDATE_TARGET_LINE = "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase14.py"
PHASE14_WRAPPER_LINE = "phase14: phase14-validate phase14-smoke phase14-test"
TESTS_README_RERUN_LINES = [
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase14-tests-readme-smoke-summary.py --self-test",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase14-tests-readme-smoke-summary.py",
]


def read_text(root: Path, relative_path: str) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def load_make_exact_lines(validator_text: str) -> list[str]:
    module = ast.parse(validator_text, filename=VALIDATOR_PATH)
    for node in module.body:
        if not isinstance(node, ast.Assign):
            continue
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id == "MAKE_EXACT_LINES":
                if not isinstance(node.value, ast.List):
                    raise ValueError("MAKE_EXACT_LINES is not a list literal")
                values: list[str] = []
                for element in node.value.elts:
                    if not isinstance(element, ast.Constant) or not isinstance(element.value, str):
                        raise ValueError("MAKE_EXACT_LINES contains a non-string literal")
                    values.append(element.value)
                return values
    return []


def collect_errors(root: Path) -> list[str]:
    errors: list[str] = []

    validator_file = root / VALIDATOR_PATH
    makefile_file = root / MAKEFILE_PATH

    if not validator_file.exists():
        errors.append(f"missing file: {VALIDATOR_PATH}")
        validator_text = ""
        make_exact_lines: list[str] = []
    else:
        validator_text = read_text(root, VALIDATOR_PATH)
        try:
            make_exact_lines = load_make_exact_lines(validator_text)
        except ValueError as exc:
            errors.append(f"validator:invalid_make_exact_lines:{exc}")
            make_exact_lines = []

    if not makefile_file.exists():
        errors.append(f"missing file: {MAKEFILE_PATH}")
        return errors

    makefile_text = read_text(root, MAKEFILE_PATH)

    if f"{VALIDATE_TARGET_HEADER}\n" not in makefile_text:
        errors.append("makefile:missing_phase14_validate_target")
    if f"{VALIDATE_TARGET_LINE}\n" not in makefile_text:
        errors.append("makefile:missing_phase14_validate_command")
    if f"{PHASE14_WRAPPER_LINE}\n" not in makefile_text:
        errors.append("makefile:missing_phase14_wrapper_alignment")

    if validator_text and "PHASE14_VALIDATE_PACKET=shared_smoke" not in validator_text:
        errors.append("validator:missing_shared_smoke_marker")

    rerun_counts = [makefile_text.count(f"{line}\n") for line in TESTS_README_RERUN_LINES]
    if any(count not in (0, 1) for count in rerun_counts):
        for line, count in zip(TESTS_README_RERUN_LINES, rerun_counts):
            if count not in (0, 1):
                errors.append(f"makefile:unexpected_tests_readme_rerun_count:{line}:count={count}")

    if any(count == 1 for count in rerun_counts):
        for line, count in zip(TESTS_README_RERUN_LINES, rerun_counts):
            validator_count = make_exact_lines.count(line)
            if count == 1 and validator_count != 1:
                errors.append(
                    f"validator:make_exact_line:{line}:count={validator_count}"
                )

    return errors


def write_fixture(
    root: Path,
    *,
    validator_present: bool,
    validator_marker: bool,
    validator_exact_lines: list[str],
    makefile_lines: list[str],
) -> None:
    makefile_path = root / MAKEFILE_PATH
    makefile_path.parent.mkdir(parents=True, exist_ok=True)
    makefile_path.write_text("\n".join(makefile_lines) + "\n", encoding="utf-8")

    validator_path = root / VALIDATOR_PATH
    if validator_path.exists():
        validator_path.unlink()

    if not validator_present:
        return

    validator_path.parent.mkdir(parents=True, exist_ok=True)
    body = [
        "#!/usr/bin/env python3",
        '"""PHASE14_VALIDATE_PACKET=shared_smoke"""' if validator_marker else '"""PHASE14_VALIDATE_PACKET=missing"""',
        "",
        "MAKE_EXACT_LINES = [",
    ]
    for line in validator_exact_lines:
        body.append(f"    {line!r},")
    body.extend(["]", ""])
    validator_path.write_text("\n".join(body), encoding="utf-8")


def run_self_test() -> int:
    cases = [
        (
            "happy_path_without_tests_readme_reruns",
            {
                "validator_present": True,
                "validator_marker": True,
                "validator_exact_lines": [],
                "makefile_lines": [
                    VALIDATE_TARGET_HEADER,
                    VALIDATE_TARGET_LINE,
                    "phase14-smoke:",
                    "phase14-test:",
                    PHASE14_WRAPPER_LINE,
                ],
            },
            [],
        ),
        (
            "missing_validator_file",
            {
                "validator_present": False,
                "validator_marker": False,
                "validator_exact_lines": [],
                "makefile_lines": [
                    VALIDATE_TARGET_HEADER,
                    VALIDATE_TARGET_LINE,
                    PHASE14_WRAPPER_LINE,
                ],
            },
            [f"missing file: {VALIDATOR_PATH}"],
        ),
        (
            "missing_validate_target",
            {
                "validator_present": True,
                "validator_marker": True,
                "validator_exact_lines": [],
                "makefile_lines": [
                    VALIDATE_TARGET_LINE,
                    PHASE14_WRAPPER_LINE,
                ],
            },
            ["makefile:missing_phase14_validate_target"],
        ),
        (
            "missing_wrapper_alignment",
            {
                "validator_present": True,
                "validator_marker": True,
                "validator_exact_lines": [],
                "makefile_lines": [
                    VALIDATE_TARGET_HEADER,
                    VALIDATE_TARGET_LINE,
                    "phase14: phase14-smoke phase14-test",
                ],
            },
            ["makefile:missing_phase14_wrapper_alignment"],
        ),
        (
            "tests_readme_exactness_drift",
            {
                "validator_present": True,
                "validator_marker": True,
                "validator_exact_lines": [],
                "makefile_lines": [
                    VALIDATE_TARGET_HEADER,
                    VALIDATE_TARGET_LINE,
                    TESTS_README_RERUN_LINES[0],
                    TESTS_README_RERUN_LINES[1],
                    PHASE14_WRAPPER_LINE,
                ],
            },
            [
                f"validator:make_exact_line:{TESTS_README_RERUN_LINES[0]}:count=0",
                f"validator:make_exact_line:{TESTS_README_RERUN_LINES[1]}:count=0",
            ],
        ),
    ]

    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        for name, fixture, expected in cases:
            write_fixture(root, **fixture)
            actual = collect_errors(root)
            if actual != expected:
                print("PHASE14_VALIDATE_ROUTE_GAP_SELF_TEST=fail")
                print(f"SELF_TEST_CASE={name}")
                print("EXPECTED_START")
                for item in expected:
                    print(item)
                print("EXPECTED_END")
                print("ACTUAL_START")
                for item in actual:
                    print(item)
                print("ACTUAL_END")
                return 1

    print("PHASE14_VALIDATE_ROUTE_GAP_SELF_TEST=pass")
    print(f"PHASE14_VALIDATE_ROUTE_GAP_SELF_TEST_CASE_COUNT={len(cases)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Fail closed when the shared Phase 14 validate route is missing or when returned tests-readme reruns drift away from validator exactness.",
    )
    parser.add_argument("--self-test", action="store_true", help="run the built-in self-test")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    errors = collect_errors(ROOT)
    if errors:
        print("PHASE14_VALIDATE_ROUTE_GAP=fail")
        print("PHASE14_VALIDATE_ROUTE_GAP_ERRORS_START")
        for error in errors:
            print(error)
        print("PHASE14_VALIDATE_ROUTE_GAP_ERRORS_END")
        return 1

    print("PHASE14_VALIDATE_ROUTE_GAP=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
