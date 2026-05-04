#!/usr/bin/env python3
from __future__ import annotations

import ast
import os
from pathlib import Path
import subprocess
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[2]
VALIDATOR_PATH = ROOT / "scripts" / "zigux" / "validate-phase7.py"

EXPECTED_MAKE_EXPANSIONS = {
    "phase7-validate": [
        "python3 scripts/zigux/validate-phase7.py --self-test",
        "python3 scripts/zigux/validate-phase7.py",
        "python3 scripts/zigux/check-phase7-build-inventory.py --self-test",
        "python3 scripts/zigux/check-phase7-build-inventory.py",
        "python3 scripts/zigux/check-phase7-make-wrapper.py --self-test",
        "python3 scripts/zigux/check-phase7-make-wrapper.py",
        "python3 scripts/zigux/check-phase7-cmdline-parity.py --self-test",
        "python3 scripts/zigux/check-phase7-cmdline-parity.py",
        "python3 scripts/zigux/check-phase7-argv-split-packet.py --self-test",
        "python3 scripts/zigux/check-phase7-argv-split-packet.py",
        "python3 scripts/zigux/check-phase7-argv-split-parity.py --self-test",
        "python3 scripts/zigux/check-phase7-argv-split-parity.py",
        "python3 scripts/zigux/check-phase7-rbtree-parity.py --self-test",
        "python3 scripts/zigux/check-phase7-rbtree-parity.py",
    ],
    "phase7-test": [
        "zig build test --build-file zigux/tests/phase7_build.zig --summary all",
    ],
    "phase7": [
        "python3 scripts/zigux/validate-phase7.py --self-test",
        "python3 scripts/zigux/validate-phase7.py",
        "python3 scripts/zigux/check-phase7-build-inventory.py --self-test",
        "python3 scripts/zigux/check-phase7-build-inventory.py",
        "python3 scripts/zigux/check-phase7-make-wrapper.py --self-test",
        "python3 scripts/zigux/check-phase7-make-wrapper.py",
        "python3 scripts/zigux/check-phase7-cmdline-parity.py --self-test",
        "python3 scripts/zigux/check-phase7-cmdline-parity.py",
        "python3 scripts/zigux/check-phase7-argv-split-packet.py --self-test",
        "python3 scripts/zigux/check-phase7-argv-split-packet.py",
        "python3 scripts/zigux/check-phase7-argv-split-parity.py --self-test",
        "python3 scripts/zigux/check-phase7-argv-split-parity.py",
        "python3 scripts/zigux/check-phase7-rbtree-parity.py --self-test",
        "python3 scripts/zigux/check-phase7-rbtree-parity.py",
        "zig build test --build-file zigux/tests/phase7_build.zig --summary all",
    ],
}

UNEXPECTED_MAKE_EXPANSIONS = {
    "phase7-validate": [
        "zig build test --build-file zigux/tests/build.zig",
        "zig build test --build-file zigux/tests/phase7_build.zig --summary all",
    ],
    "phase7-test": [
        "python3 scripts/zigux/validate-phase7.py --self-test",
        "python3 scripts/zigux/validate-phase7.py",
        "python3 scripts/zigux/check-phase7-build-inventory.py --self-test",
        "python3 scripts/zigux/check-phase7-build-inventory.py",
        "python3 scripts/zigux/check-phase7-make-wrapper.py --self-test",
        "python3 scripts/zigux/check-phase7-make-wrapper.py",
        "python3 scripts/zigux/check-phase7-cmdline-parity.py --self-test",
        "python3 scripts/zigux/check-phase7-cmdline-parity.py",
        "python3 scripts/zigux/check-phase7-argv-split-packet.py --self-test",
        "python3 scripts/zigux/check-phase7-argv-split-packet.py",
        "python3 scripts/zigux/check-phase7-argv-split-parity.py --self-test",
        "python3 scripts/zigux/check-phase7-argv-split-parity.py",
        "python3 scripts/zigux/check-phase7-rbtree-parity.py --self-test",
        "python3 scripts/zigux/check-phase7-rbtree-parity.py",
        "zig build test --build-file zigux/tests/build.zig",
    ],
    "phase7": [
        "zig build test --build-file zigux/tests/build.zig",
    ],
}

REQUIRED_VALIDATOR_TEXT_MARKERS = [
    'ROOT / "scripts" / "zigux" / "check-phase7-build-inventory.py"',
    'ROOT / "scripts" / "zigux" / "check-phase7-make-wrapper.py"',
    'ROOT / "zigux" / "tests" / "fixtures" / "phase7_build_inventory.json"',
]

REQUIRED_VALIDATOR_LIST_MARKERS = {
    "required_tests_readme_markers": [
        "`scripts/zigux/check-phase7-make-wrapper.py --self-test`",
        "`scripts/zigux/check-phase7-make-wrapper.py`",
    ],
    "required_doc_readme_markers": [
        "`python3 scripts/zigux/check-phase7-make-wrapper.py --self-test`",
        "`python3 scripts/zigux/check-phase7-make-wrapper.py`",
    ],
}


def display_path(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def parse_validator_lists(validator_path: Path) -> tuple[dict[str, object] | None, list[str]]:
    if not validator_path.exists():
        return None, [f"missing validator source: {display_path(validator_path)}"]

    validator_text = validator_path.read_text(encoding="utf-8")
    failures = [
        f"validator source missing marker: {marker}"
        for marker in REQUIRED_VALIDATOR_TEXT_MARKERS
        if marker not in validator_text
    ]

    try:
        module = ast.parse(validator_text, filename=str(validator_path))
    except SyntaxError as exc:
        failures.append(
            "validator source parse failure: "
            f"{display_path(validator_path)}:{exc.lineno}:{exc.offset}: {exc.msg}"
        )
        return None, failures

    values: dict[str, object] = {}
    for node in module.body:
        if not isinstance(node, ast.Assign):
            continue
        for target in node.targets:
            if isinstance(target, ast.Name):
                try:
                    values[target.id] = ast.literal_eval(node.value)
                except (TypeError, ValueError):
                    continue
    return values, failures


def check_validator_alignment(root: Path) -> list[str]:
    validator_values, failures = parse_validator_lists(root / "scripts" / "zigux" / "validate-phase7.py")
    if validator_values is None:
        return failures

    expansions = validator_values.get("expected_make_expansions")
    if not isinstance(expansions, dict):
        failures.append("validator source missing expected_make_expansions")
        return failures

    for target_name, expected_lines in EXPECTED_MAKE_EXPANSIONS.items():
        actual_lines = expansions.get(target_name)
        if not isinstance(actual_lines, list):
            failures.append(f"validator {target_name} expansion missing or not a list")
            continue

        for line in expected_lines:
            actual_count = actual_lines.count(line)
            if actual_count == 0:
                failures.append(f"validator {target_name} expansion missing: {line}")
            elif actual_count != 1:
                failures.append(
                    f"validator {target_name} expansion count drift: {line} ({actual_count} != 1)"
                )

        for line in UNEXPECTED_MAKE_EXPANSIONS.get(target_name, []):
            if line in actual_lines:
                failures.append(
                    f"validator {target_name} expansion unexpectedly includes: {line}"
                )

        actual_positions = {line: actual_lines.index(line) for line in expected_lines if line in actual_lines}
        for earlier, later in zip(expected_lines, expected_lines[1:]):
            earlier_pos = actual_positions.get(earlier)
            later_pos = actual_positions.get(later)
            if earlier_pos is not None and later_pos is not None and earlier_pos >= later_pos:
                failures.append(
                    f"validator {target_name} expansion order drift: expected {earlier!r} before {later!r}"
                )
                break

    for list_name, markers in REQUIRED_VALIDATOR_LIST_MARKERS.items():
        actual_list = validator_values.get(list_name)
        if not isinstance(actual_list, list):
            failures.append(f"validator source missing {list_name}")
            continue
        for marker in markers:
            count = actual_list.count(marker)
            if count == 0:
                failures.append(f"validator {list_name} missing: {marker}")
            elif count != 1:
                failures.append(
                    f"validator {list_name} count drift: {marker} ({count} != 1)"
                )

    return failures


def check_make_output(root: Path, env: dict[str, str] | None = None) -> list[str]:
    failures: list[str] = []
    for target_name, expected_lines in EXPECTED_MAKE_EXPANSIONS.items():
        result = subprocess.run(
            ["make", "-n", "-C", str(root / "zigux"), target_name],
            check=False,
            capture_output=True,
            text=True,
            env=env,
        )
        if result.returncode != 0:
            failures.append(f"{target_name}: make -n failed with returncode {result.returncode}")
            stderr = result.stderr.strip()
            if stderr:
                failures.append(stderr)
            continue

        wrapper_lines = [line.strip() for line in result.stdout.splitlines() if line.strip()]
        for line in expected_lines:
            count = wrapper_lines.count(line)
            if count == 0:
                failures.append(f"{target_name}: missing expected wrapper expansion: {line}")
            elif count != 1:
                failures.append(
                    f"{target_name}: expected wrapper expansion count drift: {line} ({count} != 1)"
                )

        for line in UNEXPECTED_MAKE_EXPANSIONS.get(target_name, []):
            if line in wrapper_lines:
                failures.append(f"{target_name}: unexpected wrapper expansion: {line}")

        positions = {line: wrapper_lines.index(line) for line in expected_lines if line in wrapper_lines}
        for earlier, later in zip(expected_lines, expected_lines[1:]):
            earlier_pos = positions.get(earlier)
            later_pos = positions.get(later)
            if earlier_pos is not None and later_pos is not None and earlier_pos >= later_pos:
                failures.append(
                    f"{target_name}: wrapper expansion order drift: expected {earlier!r} before {later!r}"
                )
                break
    return failures


def check_root(root: Path, env: dict[str, str] | None = None) -> tuple[bool, list[str]]:
    failures = check_validator_alignment(root)
    failures.extend(check_make_output(root, env=env))
    return len(failures) == 0, failures


def make_fake_make(fake_make_path: Path, outputs: dict[str, list[str]]) -> None:
    lines = [
        "#!/usr/bin/env python3",
        "import sys",
        f"outputs = {outputs!r}",
        "for line in outputs.get(sys.argv[-1], []):",
        "    print(line)",
    ]
    fake_make_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    fake_make_path.chmod(0o755)


def write_validator_fixture(
    validator_path: Path,
    expected_make_expansions: dict[str, list[str]],
    *,
    tests_markers: list[str] | None = None,
    doc_markers: list[str] | None = None,
    include_required_text_markers: bool = True,
) -> None:
    validator_path.parent.mkdir(parents=True, exist_ok=True)
    text_markers = []
    if include_required_text_markers:
        text_markers = [
            '    ROOT / "scripts" / "zigux" / "check-phase7-build-inventory.py",',
            '    ROOT / "scripts" / "zigux" / "check-phase7-make-wrapper.py",',
            '    ROOT / "zigux" / "tests" / "fixtures" / "phase7_build_inventory.json",',
        ]
    tests_markers = tests_markers or REQUIRED_VALIDATOR_LIST_MARKERS["required_tests_readme_markers"]
    doc_markers = doc_markers or REQUIRED_VALIDATOR_LIST_MARKERS["required_doc_readme_markers"]
    body = [
        "#!/usr/bin/env python3",
        "ROOT = None",
        "required_files = [",
        *text_markers,
        "]",
        f"expected_make_expansions = {expected_make_expansions!r}",
        f"required_tests_readme_markers = {tests_markers!r}",
        f"required_doc_readme_markers = {doc_markers!r}",
    ]
    validator_path.write_text("\n".join(body) + "\n", encoding="utf-8")


def expect_failure(label: str, root: Path, env: dict[str, str], expected_message: str) -> None:
    ok, failures = check_root(root, env=env)
    if ok:
        raise SystemExit(f"phase7-make-wrapper-selftest:{label}:unexpected_pass")
    joined = "\n".join(failures)
    if expected_message not in joined:
        raise SystemExit(
            f"phase7-make-wrapper-selftest:{label}:expected:{expected_message}:actual:{joined}"
        )


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase7_make_wrapper_") as tmp_dir:
        tmp_root = Path(tmp_dir)
        (tmp_root / "zigux").mkdir()
        validator_path = tmp_root / "scripts" / "zigux" / "validate-phase7.py"
        fake_make_dir = tmp_root / "fake-bin"
        fake_make_dir.mkdir()
        fake_make_path = fake_make_dir / "make"
        env = os.environ.copy()
        env["PATH"] = f"{fake_make_dir}:{env['PATH']}"

        make_fake_make(fake_make_path, EXPECTED_MAKE_EXPANSIONS)
        write_validator_fixture(validator_path, EXPECTED_MAKE_EXPANSIONS)
        ok, failures = check_root(tmp_root, env=env)
        if not ok:
            raise SystemExit(
                "phase7-make-wrapper-selftest:baseline_failed:" + (" | ".join(failures) or "no_output")
            )

        write_validator_fixture(
            validator_path,
            EXPECTED_MAKE_EXPANSIONS,
            include_required_text_markers=False,
        )
        expect_failure(
            "missing_validator_required_markers",
            tmp_root,
            env,
            'validator source missing marker: ROOT / "scripts" / "zigux" / "check-phase7-build-inventory.py"',
        )

        write_validator_fixture(validator_path, EXPECTED_MAKE_EXPANSIONS)
        validator_text = validator_path.read_text(encoding="utf-8")
        validator_path.write_text(
            validator_text.replace(
                '    ROOT / "scripts" / "zigux" / "check-phase7-make-wrapper.py",\n',
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_failure(
            "missing_make_wrapper_required_marker",
            tmp_root,
            env,
            'validator source missing marker: ROOT / "scripts" / "zigux" / "check-phase7-make-wrapper.py"',
        )

        validator_path.write_text("#!/usr/bin/env python3\nexpected_make_expansions = {\n", encoding="utf-8")
        expect_failure("validator_parse_failure", tmp_root, env, "validator source parse failure:")

        write_validator_fixture(
            validator_path,
            EXPECTED_MAKE_EXPANSIONS,
            tests_markers=["`scripts/zigux/check-phase7-make-wrapper.py`"],
        )
        expect_failure(
            "missing_tests_marker",
            tmp_root,
            env,
            "validator required_tests_readme_markers missing: `scripts/zigux/check-phase7-make-wrapper.py --self-test`",
        )

        write_validator_fixture(
            validator_path,
            EXPECTED_MAKE_EXPANSIONS,
            doc_markers=["`python3 scripts/zigux/check-phase7-make-wrapper.py`"],
        )
        expect_failure(
            "missing_doc_marker",
            tmp_root,
            env,
            "validator required_doc_readme_markers missing: `python3 scripts/zigux/check-phase7-make-wrapper.py --self-test`",
        )

        write_validator_fixture(
            validator_path,
            EXPECTED_MAKE_EXPANSIONS,
            tests_markers=[
                *REQUIRED_VALIDATOR_LIST_MARKERS["required_tests_readme_markers"],
                REQUIRED_VALIDATOR_LIST_MARKERS["required_tests_readme_markers"][0],
            ],
        )
        expect_failure(
            "duplicate_tests_marker",
            tmp_root,
            env,
            "validator required_tests_readme_markers count drift: `scripts/zigux/check-phase7-make-wrapper.py --self-test` (2 != 1)",
        )

        write_validator_fixture(
            validator_path,
            EXPECTED_MAKE_EXPANSIONS,
            doc_markers=[
                *REQUIRED_VALIDATOR_LIST_MARKERS["required_doc_readme_markers"],
                REQUIRED_VALIDATOR_LIST_MARKERS["required_doc_readme_markers"][1],
            ],
        )
        expect_failure(
            "duplicate_doc_marker",
            tmp_root,
            env,
            "validator required_doc_readme_markers count drift: `python3 scripts/zigux/check-phase7-make-wrapper.py` (2 != 1)",
        )

        write_validator_fixture(
            validator_path,
            {
                **EXPECTED_MAKE_EXPANSIONS,
                "phase7-validate": [
                    line
                    for line in EXPECTED_MAKE_EXPANSIONS["phase7-validate"]
                    if line != "python3 scripts/zigux/check-phase7-build-inventory.py --self-test"
                ],
            },
        )
        expect_failure(
            "missing_validator_build_inventory_selftest",
            tmp_root,
            env,
            "validator phase7-validate expansion missing: python3 scripts/zigux/check-phase7-build-inventory.py --self-test",
        )

        write_validator_fixture(
            validator_path,
            {
                **EXPECTED_MAKE_EXPANSIONS,
                "phase7-test": [
                    *EXPECTED_MAKE_EXPANSIONS["phase7-test"],
                    EXPECTED_MAKE_EXPANSIONS["phase7-test"][0],
                ],
            },
        )
        expect_failure(
            "validator_phase7_test_duplicate_line",
            tmp_root,
            env,
            "validator phase7-test expansion count drift: zig build test --build-file zigux/tests/phase7_build.zig --summary all (2 != 1)",
        )

        write_validator_fixture(validator_path, EXPECTED_MAKE_EXPANSIONS)
        make_fake_make(
            fake_make_path,
            {
                **EXPECTED_MAKE_EXPANSIONS,
                "phase7-validate": [
                    line
                    for line in EXPECTED_MAKE_EXPANSIONS["phase7-validate"]
                    if line != "python3 scripts/zigux/check-phase7-make-wrapper.py --self-test"
                ],
            },
        )
        expect_failure(
            "missing_make_wrapper_selftest",
            tmp_root,
            env,
            "phase7-validate: missing expected wrapper expansion: python3 scripts/zigux/check-phase7-make-wrapper.py --self-test",
        )

        make_fake_make(
            fake_make_path,
            {
                **EXPECTED_MAKE_EXPANSIONS,
                "phase7": [
                    line
                    for line in EXPECTED_MAKE_EXPANSIONS["phase7"]
                    if line != "python3 scripts/zigux/check-phase7-make-wrapper.py"
                ],
            },
        )
        expect_failure(
            "missing_make_wrapper_live_in_bundle",
            tmp_root,
            env,
            "phase7: missing expected wrapper expansion: python3 scripts/zigux/check-phase7-make-wrapper.py",
        )

        make_fake_make(
            fake_make_path,
            {
                **EXPECTED_MAKE_EXPANSIONS,
                "phase7-test": [
                    *EXPECTED_MAKE_EXPANSIONS["phase7-test"],
                    EXPECTED_MAKE_EXPANSIONS["phase7-test"][0],
                ],
            },
        )
        expect_failure(
            "duplicate_phase7_test_wrapper_line",
            tmp_root,
            env,
            "phase7-test: expected wrapper expansion count drift: zig build test --build-file zigux/tests/phase7_build.zig --summary all (2 != 1)",
        )

        make_fake_make(
            fake_make_path,
            {
                **EXPECTED_MAKE_EXPANSIONS,
                "phase7": [*EXPECTED_MAKE_EXPANSIONS["phase7"], "zig build test --build-file zigux/tests/build.zig"],
            },
        )
        expect_failure(
            "stale_build_in_phase7_bundle",
            tmp_root,
            env,
            "phase7: unexpected wrapper expansion: zig build test --build-file zigux/tests/build.zig",
        )

    print("PHASE7_MAKE_WRAPPER_SELF_TEST=pass")
    print("PHASE7_MAKE_WRAPPER_SELF_TEST_CASE_COUNT=12")
    return 0


def main() -> int:
    if "--self-test" in sys.argv[1:]:
        return run_self_test()

    ok, failures = check_root(ROOT)
    if not ok:
        print("PHASE7_MAKE_WRAPPER=fail")
        print("PHASE7_MAKE_WRAPPER_FAILURES_START")
        for failure in failures:
            print(failure)
        print("PHASE7_MAKE_WRAPPER_FAILURES_END")
        return 1

    print("PHASE7_MAKE_WRAPPER=pass")
    print(f"PHASE7_MAKE_WRAPPER_TARGET_COUNT={len(EXPECTED_MAKE_EXPANSIONS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
