#!/usr/bin/env python3

from __future__ import annotations

import argparse
import ast
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
VALIDATOR_PATH = "scripts/zigux/validate-phase14.py"
MAKEFILE_PATH = "zigux/Makefile"
REQUIRED_LINES = [
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase14-tests-readme-smoke-summary.py --self-test",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase14-tests-readme-smoke-summary.py",
]


def text(root: Path, relative_path: str) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def load_make_exact_lines(validator_text: str) -> list[str]:
    module = ast.parse(validator_text, filename=VALIDATOR_PATH)
    for node in module.body:
        if not isinstance(node, ast.Assign):
            continue
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id == "MAKE_EXACT_LINES":
                values: list[str] = []
                if not isinstance(node.value, ast.List):
                    raise ValueError("MAKE_EXACT_LINES is not a list literal")
                for element in node.value.elts:
                    if not isinstance(element, ast.Constant) or not isinstance(element.value, str):
                        raise ValueError("MAKE_EXACT_LINES contains a non-string literal")
                    values.append(element.value)
                return values
    raise ValueError("MAKE_EXACT_LINES list not found")


def collect_missing(root: Path) -> list[str]:
    validator_text = text(root, VALIDATOR_PATH)
    makefile_text = text(root, MAKEFILE_PATH)
    make_exact_lines = load_make_exact_lines(validator_text)

    missing: list[str] = []
    for line in REQUIRED_LINES:
        validator_count = make_exact_lines.count(line)
        if validator_count != 1:
            missing.append(f"validator:make_exact_line:{line}:count={validator_count}")

        makefile_count = makefile_text.count(f"{line}\n")
        if makefile_count != 1:
            missing.append(f"makefile:phase14_validate_line:{line}:count={makefile_count}")

    return missing


def write_fixture(root: Path, validator_lines: list[str], makefile_lines: list[str]) -> None:
    validator_path = root / VALIDATOR_PATH
    validator_path.parent.mkdir(parents=True, exist_ok=True)
    validator_body = [
        "#!/usr/bin/env python3",
        "",
        "MAKE_EXACT_LINES = [",
    ]
    for line in validator_lines:
        validator_body.append(f"    {line!r},")
    validator_body += [
        "]",
        "",
    ]
    validator_path.write_text("\n".join(validator_body), encoding="utf-8")

    makefile_path = root / MAKEFILE_PATH
    makefile_path.parent.mkdir(parents=True, exist_ok=True)
    makefile_path.write_text("\n".join(makefile_lines) + "\n", encoding="utf-8")


def run_self_test() -> int:
    cases = [
        (
            "happy_path",
            REQUIRED_LINES,
            REQUIRED_LINES,
            [],
        ),
        (
            "validator_missing_selftest",
            [REQUIRED_LINES[1]],
            REQUIRED_LINES,
            [f"validator:make_exact_line:{REQUIRED_LINES[0]}:count=0"],
        ),
        (
            "validator_missing_live_route",
            [REQUIRED_LINES[0]],
            REQUIRED_LINES,
            [f"validator:make_exact_line:{REQUIRED_LINES[1]}:count=0"],
        ),
        (
            "makefile_missing_selftest",
            REQUIRED_LINES,
            [REQUIRED_LINES[1]],
            [f"makefile:phase14_validate_line:{REQUIRED_LINES[0]}:count=0"],
        ),
        (
            "validator_duplicate_live_route",
            [REQUIRED_LINES[0], REQUIRED_LINES[1], REQUIRED_LINES[1]],
            REQUIRED_LINES,
            [f"validator:make_exact_line:{REQUIRED_LINES[1]}:count=2"],
        ),
    ]

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_root = Path(tmpdir)
        for case_name, validator_lines, makefile_lines, expected_missing in cases:
            write_fixture(tmp_root, validator_lines, makefile_lines)
            actual_missing = collect_missing(tmp_root)
            if actual_missing != expected_missing:
                print("PHASE14_VALIDATOR_MAKEFILE_EXACTNESS_SELF_TEST=fail")
                print(f"SELF_TEST_CASE={case_name}")
                print("EXPECTED_START")
                for item in expected_missing:
                    print(item)
                print("EXPECTED_END")
                print("ACTUAL_START")
                for item in actual_missing:
                    print(item)
                print("ACTUAL_END")
                return 1

    print("PHASE14_VALIDATOR_MAKEFILE_EXACTNESS_SELF_TEST=pass")
    print(f"PHASE14_VALIDATOR_MAKEFILE_EXACTNESS_SELF_TEST_CASE_COUNT={len(cases)}")
    print(f"PHASE14_VALIDATOR_MAKEFILE_REQUIRED_LINE_MARKER={REQUIRED_LINES[0]}")
    print(f"PHASE14_VALIDATOR_MAKEFILE_REQUIRED_LINE_MARKER={REQUIRED_LINES[1]}")
    return 0


def run_check() -> int:
    missing = collect_missing(ROOT)
    if missing:
        print("PHASE14_VALIDATOR_MAKEFILE_EXACTNESS=fail")
        print("MISSING_PHASE14_VALIDATOR_MAKEFILE_EXACTNESS_START")
        for item in missing:
            print(item)
        print("MISSING_PHASE14_VALIDATOR_MAKEFILE_EXACTNESS_END")
        return 1

    print("PHASE14_VALIDATOR_MAKEFILE_EXACTNESS=pass")
    print(f"PHASE14_VALIDATOR_MAKEFILE_REQUIRED_LINE_COUNT={len(REQUIRED_LINES)}")
    print(f"PHASE14_VALIDATOR_MAKEFILE_REQUIRED_LINE_MARKER={REQUIRED_LINES[0]}")
    print(f"PHASE14_VALIDATOR_MAKEFILE_REQUIRED_LINE_MARKER={REQUIRED_LINES[1]}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Fail closed when Phase 14 validator Makefile exact-line coverage lags the tests-readme smoke checker reruns.",
    )
    parser.add_argument("--self-test", action="store_true", help="run the built-in checker self-test")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()
    return run_check()


if __name__ == "__main__":
    raise SystemExit(main())
