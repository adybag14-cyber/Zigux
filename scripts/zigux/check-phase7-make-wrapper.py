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
    'ROOT / "zigux" / "tests" / "fixtures" / "phase7_build_inventory.json"',
]

VALIDATOR_ALIGNMENT_LINES = {
    "phase7-validate": EXPECTED_MAKE_EXPANSIONS["phase7-validate"],
    "phase7-test": EXPECTED_MAKE_EXPANSIONS["phase7-test"],
    "phase7": EXPECTED_MAKE_EXPANSIONS["phase7"],
}


def display_path(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def load_validator_make_expansions(
    validator_path: Path,
) -> tuple[dict[str, list[str]] | None, list[str]]:
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

    for node in module.body:
        if not isinstance(node, ast.Assign):
            continue
        if not any(
            isinstance(target, ast.Name) and target.id == "expected_make_expansions"
            for target in node.targets
        ):
            continue
        try:
            value = ast.literal_eval(node.value)
        except (TypeError, ValueError) as exc:
            failures.append(f"validator expected_make_expansions literal drift: {exc}")
            return None, failures
        if not isinstance(value, dict):
            failures.append("validator expected_make_expansions is not a dict")
            return None, failures
        return value, failures

    failures.append("validator source missing expected_make_expansions")
    return None, failures


def check_validator_alignment(root: Path) -> list[str]:
    validator_path = root / "scripts" / "zigux" / "validate-phase7.py"
    expansions, failures = load_validator_make_expansions(validator_path)
    if expansions is None:
        return failures

    for target_name, expected_lines in VALIDATOR_ALIGNMENT_LINES.items():
        actual_lines = expansions.get(target_name)
        if not isinstance(actual_lines, list):
            failures.append(
                f"validator {target_name} expansion missing or not a list"
            )
            continue

        for line in expected_lines:
            actual_count = actual_lines.count(line)
            if actual_count == 0:
                failures.append(
                    f"validator {target_name} expansion missing: {line}"
                )
                continue
            if actual_count != 1:
                failures.append(
                    f"validator {target_name} expansion count drift: {line} ({actual_count} != 1)"
                )

        for line in UNEXPECTED_MAKE_EXPANSIONS.get(target_name, []):
            if line in actual_lines:
                failures.append(
                    f"validator {target_name} expansion unexpectedly includes: {line}"
                )

        expected_positions = {
            line: actual_lines.index(line)
            for line in expected_lines
            if line in actual_lines
        }
        for earlier, later in zip(expected_lines, expected_lines[1:]):
            earlier_pos = expected_positions.get(earlier)
            later_pos = expected_positions.get(later)
            if earlier_pos is None or later_pos is None:
                continue
            if earlier_pos >= later_pos:
                failures.append(
                    f"validator {target_name} expansion order drift: "
                    f"expected {earlier!r} before {later!r}"
                )
                break

    return failures


def check_root(root: Path, env: dict[str, str] | None = None) -> tuple[bool, list[str]]:
    failures = check_validator_alignment(root)

    for target_name, expected_lines in EXPECTED_MAKE_EXPANSIONS.items():
        result = subprocess.run(
            ["make", "-n", "-C", str(root / "zigux"), target_name],
            check=False,
            capture_output=True,
            text=True,
            env=env,
        )
        if result.returncode != 0:
            failures.append(
                f"{target_name}: make -n failed with returncode {result.returncode}"
            )
            stderr = result.stderr.strip()
            if stderr:
                failures.append(stderr)
            continue

        wrapper_lines = [line.strip() for line in result.stdout.splitlines() if line.strip()]
        for line in expected_lines:
            actual_count = wrapper_lines.count(line)
            if actual_count == 0:
                failures.append(
                    f"{target_name}: missing expected wrapper expansion: {line}"
                )
                continue
            if actual_count != 1:
                failures.append(
                    f"{target_name}: expected wrapper expansion count drift: {line} ({actual_count} != 1)"
                )

        for line in UNEXPECTED_MAKE_EXPANSIONS.get(target_name, []):
            if line in wrapper_lines:
                failures.append(
                    f"{target_name}: unexpected wrapper expansion: {line}"
                )

        expected_positions = {
            line: wrapper_lines.index(line)
            for line in expected_lines
            if line in wrapper_lines
        }
        for earlier, later in zip(expected_lines, expected_lines[1:]):
            earlier_pos = expected_positions.get(earlier)
            later_pos = expected_positions.get(later)
            if earlier_pos is None or later_pos is None:
                continue
            if earlier_pos >= later_pos:
                failures.append(
                    f"{target_name}: wrapper expansion order drift: "
                    f"expected {earlier!r} before {later!r}"
                )
                break

    return (len(failures) == 0, failures)


def make_fake_make(fake_make_path: Path, outputs: dict[str, list[str]]) -> None:
    lines = [
        "#!/usr/bin/env python3",
        "import sys",
        "",
        "target = sys.argv[-1]",
        "outputs = {",
    ]
    for target, values in outputs.items():
        lines.append(f"    {target!r}: [")
        for value in values:
            lines.append(f"        {value!r},")
        lines.append("    ],")
    lines.extend(
        [
            "}",
            "for line in outputs.get(target, []):",
            "    print(line)",
        ]
    )
    fake_make_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    fake_make_path.chmod(0o755)


def write_validator_fixture(
    validator_path: Path,
    expected_make_expansions: dict[str, list[str]],
    include_required_markers: bool = True,
) -> None:
    validator_path.parent.mkdir(parents=True, exist_ok=True)
    required_entries = []
    if include_required_markers:
        required_entries = [
            '    ROOT / "scripts" / "zigux" / "check-phase7-build-inventory.py",',
            '    ROOT / "zigux" / "tests" / "fixtures" / "phase7_build_inventory.json",',
        ]
    validator_path.write_text(
        "#!/usr/bin/env python3\n"
        "ROOT = None\n"
        "required_files = [\n"
        + ("\n".join(required_entries) + ("\n" if required_entries else ""))
        + "]\n"
        + f"expected_make_expansions = {expected_make_expansions!r}\n",
        encoding="utf-8",
    )


def expect_failure(
    label: str, root: Path, env: dict[str, str], expected_message: str
) -> None:
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
        fake_make_env = os.environ.copy()
        fake_make_env["PATH"] = f"{fake_make_dir}:{fake_make_env['PATH']}"

        make_fake_make(fake_make_path, EXPECTED_MAKE_EXPANSIONS)
        write_validator_fixture(validator_path, EXPECTED_MAKE_EXPANSIONS)
        ok, failures = check_root(tmp_root, env=fake_make_env)
        if not ok:
            raise SystemExit(
                "phase7-make-wrapper-selftest:baseline_failed:"
                + (" | ".join(failures) or "no_output")
            )

        write_validator_fixture(
            validator_path,
            EXPECTED_MAKE_EXPANSIONS,
            include_required_markers=False,
        )
        expect_failure(
            "missing_validator_required_markers",
            tmp_root,
            fake_make_env,
            'validator source missing marker: ROOT / "scripts" / "zigux" / "check-phase7-build-inventory.py"',
        )

        validator_path.write_text(
            "#!/usr/bin/env python3\n"
            "ROOT = None\n"
            "required_files = [\n"
            '    ROOT / "scripts" / "zigux" / "check-phase7-build-inventory.py",\n'
            '    ROOT / "zigux" / "tests" / "fixtures" / "phase7_build_inventory.json",\n'
            "]\n"
            "expected_make_expansions = {\n",
            encoding="utf-8",
        )
        expect_failure(
            "validator_parse_failure",
            tmp_root,
            fake_make_env,
            "validator source parse failure:",
        )

        write_validator_fixture(
            validator_path,
            {
                **EXPECTED_MAKE_EXPANSIONS,
                "phase7-validate": [
                    line
                    for line in EXPECTED_MAKE_EXPANSIONS["phase7-validate"]
                    if line
                    != "python3 scripts/zigux/check-phase7-build-inventory.py --self-test"
                ],
            },
        )
        expect_failure(
            "missing_validator_build_inventory_selftest",
            tmp_root,
            fake_make_env,
            "validator phase7-validate expansion missing: python3 scripts/zigux/check-phase7-build-inventory.py --self-test",
        )

        write_validator_fixture(
            validator_path,
            {
                **EXPECTED_MAKE_EXPANSIONS,
                "phase7-validate": [
                    line
                    for line in EXPECTED_MAKE_EXPANSIONS["phase7-validate"]
                    if line != "python3 scripts/zigux/check-phase7-build-inventory.py"
                ],
            },
        )
        expect_failure(
            "missing_validator_build_inventory_live",
            tmp_root,
            fake_make_env,
            "validator phase7-validate expansion missing: python3 scripts/zigux/check-phase7-build-inventory.py",
        )

        write_validator_fixture(
            validator_path,
            {
                **EXPECTED_MAKE_EXPANSIONS,
                "phase7-validate": [
                    line
                    for line in EXPECTED_MAKE_EXPANSIONS["phase7-validate"]
                    if line != "python3 scripts/zigux/check-phase7-cmdline-parity.py"
                ],
            },
        )
        expect_failure(
            "missing_validator_cmdline_live",
            tmp_root,
            fake_make_env,
            "validator phase7-validate expansion missing: python3 scripts/zigux/check-phase7-cmdline-parity.py",
        )

        write_validator_fixture(
            validator_path,
            {
                **EXPECTED_MAKE_EXPANSIONS,
                "phase7-validate": [
                    line
                    for line in EXPECTED_MAKE_EXPANSIONS["phase7-validate"]
                    if line != "python3 scripts/zigux/check-phase7-argv-split-packet.py"
                ],
            },
        )
        expect_failure(
            "missing_validator_argv_split_packet_live",
            tmp_root,
            fake_make_env,
            "validator phase7-validate expansion missing: python3 scripts/zigux/check-phase7-argv-split-packet.py",
        )

        write_validator_fixture(
            validator_path,
            {
                **EXPECTED_MAKE_EXPANSIONS,
                "phase7-validate": [
                    line
                    for line in EXPECTED_MAKE_EXPANSIONS["phase7-validate"]
                    if line != "python3 scripts/zigux/check-phase7-rbtree-parity.py"
                ],
            },
        )
        expect_failure(
            "missing_validator_rbtree_live",
            tmp_root,
            fake_make_env,
            "validator phase7-validate expansion missing: python3 scripts/zigux/check-phase7-rbtree-parity.py",
        )

        write_validator_fixture(
            validator_path,
            {
                **EXPECTED_MAKE_EXPANSIONS,
                "phase7-test": [
                    "zig build test --build-file zigux/tests/build.zig",
                    *EXPECTED_MAKE_EXPANSIONS["phase7-test"],
                ],
            },
        )
        expect_failure(
            "validator_phase7_test_unexpected_stale_build",
            tmp_root,
            fake_make_env,
            "validator phase7-test expansion unexpectedly includes: zig build test --build-file zigux/tests/build.zig",
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
            fake_make_env,
            "validator phase7-test expansion count drift: zig build test --build-file zigux/tests/phase7_build.zig --summary all (2 != 1)",
        )

        write_validator_fixture(
            validator_path,
            {
                **EXPECTED_MAKE_EXPANSIONS,
                "phase7": [
                    line
                    for line in EXPECTED_MAKE_EXPANSIONS["phase7"]
                    if line
                    != "python3 scripts/zigux/check-phase7-build-inventory.py --self-test"
                ],
            },
        )
        expect_failure(
            "missing_validator_build_inventory_selftest_in_bundle",
            tmp_root,
            fake_make_env,
            "validator phase7 expansion missing: python3 scripts/zigux/check-phase7-build-inventory.py --self-test",
        )

        write_validator_fixture(
            validator_path,
            {
                **EXPECTED_MAKE_EXPANSIONS,
                "phase7": [
                    line
                    for line in EXPECTED_MAKE_EXPANSIONS["phase7"]
                    if line != "python3 scripts/zigux/check-phase7-build-inventory.py"
                ],
            },
        )
        expect_failure(
            "missing_validator_build_inventory_live_in_bundle",
            tmp_root,
            fake_make_env,
            "validator phase7 expansion missing: python3 scripts/zigux/check-phase7-build-inventory.py",
        )

        write_validator_fixture(
            validator_path,
            {
                **EXPECTED_MAKE_EXPANSIONS,
                "phase7": [
                    line
                    for line in EXPECTED_MAKE_EXPANSIONS["phase7"]
                    if line != "python3 scripts/zigux/check-phase7-cmdline-parity.py"
                ],
            },
        )
        expect_failure(
            "missing_validator_cmdline_live_in_bundle",
            tmp_root,
            fake_make_env,
            "validator phase7 expansion missing: python3 scripts/zigux/check-phase7-cmdline-parity.py",
        )

        write_validator_fixture(
            validator_path,
            {
                **EXPECTED_MAKE_EXPANSIONS,
                "phase7": [
                    line
                    for line in EXPECTED_MAKE_EXPANSIONS["phase7"]
                    if line != "python3 scripts/zigux/check-phase7-argv-split-packet.py"
                ],
            },
        )
        expect_failure(
            "missing_validator_argv_split_packet_live_in_bundle",
            tmp_root,
            fake_make_env,
            "validator phase7 expansion missing: python3 scripts/zigux/check-phase7-argv-split-packet.py",
        )

        write_validator_fixture(
            validator_path,
            {
                **EXPECTED_MAKE_EXPANSIONS,
                "phase7": [
                    line
                    for line in EXPECTED_MAKE_EXPANSIONS["phase7"]
                    if line != "python3 scripts/zigux/check-phase7-rbtree-parity.py"
                ],
            },
        )
        expect_failure(
            "missing_validator_rbtree_live_in_bundle",
            tmp_root,
            fake_make_env,
            "validator phase7 expansion missing: python3 scripts/zigux/check-phase7-rbtree-parity.py",
        )

        write_validator_fixture(
            validator_path,
            {
                **EXPECTED_MAKE_EXPANSIONS,
                "phase7-validate": [
                    "python3 scripts/zigux/validate-phase7.py --self-test",
                    "python3 scripts/zigux/validate-phase7.py",
                    "python3 scripts/zigux/check-phase7-build-inventory.py",
                    "python3 scripts/zigux/check-phase7-build-inventory.py --self-test",
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
            },
        )
        expect_failure(
            "validator_order_drift",
            tmp_root,
            fake_make_env,
            "validator phase7-validate expansion order drift: expected 'python3 scripts/zigux/check-phase7-build-inventory.py --self-test' before 'python3 scripts/zigux/check-phase7-build-inventory.py'",
        )

        write_validator_fixture(validator_path, EXPECTED_MAKE_EXPANSIONS)
        make_fake_make(
            fake_make_path,
            {
                **EXPECTED_MAKE_EXPANSIONS,
                "phase7-validate": [
                    line
                    for line in EXPECTED_MAKE_EXPANSIONS["phase7-validate"]
                    if line
                    != "python3 scripts/zigux/check-phase7-build-inventory.py --self-test"
                ],
            },
        )
        expect_failure(
            "missing_build_inventory_selftest",
            tmp_root,
            fake_make_env,
            "phase7-validate: missing expected wrapper expansion: python3 scripts/zigux/check-phase7-build-inventory.py --self-test",
        )

        make_fake_make(
            fake_make_path,
            {
                **EXPECTED_MAKE_EXPANSIONS,
                "phase7-validate": [
                    line
                    for line in EXPECTED_MAKE_EXPANSIONS["phase7-validate"]
                    if line
                    != "python3 scripts/zigux/check-phase7-argv-split-packet.py --self-test"
                ],
            },
        )
        expect_failure(
            "missing_argv_split_packet_selftest",
            tmp_root,
            fake_make_env,
            "phase7-validate: missing expected wrapper expansion: python3 scripts/zigux/check-phase7-argv-split-packet.py --self-test",
        )

        make_fake_make(
            fake_make_path,
            {
                **EXPECTED_MAKE_EXPANSIONS,
                "phase7-validate": [
                    line
                    for line in EXPECTED_MAKE_EXPANSIONS["phase7-validate"]
                    if line
                    != "python3 scripts/zigux/check-phase7-argv-split-parity.py --self-test"
                ],
            },
        )
        expect_failure(
            "missing_argv_split_selftest",
            tmp_root,
            fake_make_env,
            "phase7-validate: missing expected wrapper expansion: python3 scripts/zigux/check-phase7-argv-split-parity.py --self-test",
        )

        make_fake_make(
            fake_make_path,
            {
                **EXPECTED_MAKE_EXPANSIONS,
                "phase7-validate": [
                    line
                    for line in EXPECTED_MAKE_EXPANSIONS["phase7-validate"]
                    if line
                    != "python3 scripts/zigux/check-phase7-rbtree-parity.py --self-test"
                ],
            },
        )
        expect_failure(
            "missing_rbtree_selftest",
            tmp_root,
            fake_make_env,
            "phase7-validate: missing expected wrapper expansion: python3 scripts/zigux/check-phase7-rbtree-parity.py --self-test",
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
            fake_make_env,
            "phase7-test: expected wrapper expansion count drift: zig build test --build-file zigux/tests/phase7_build.zig --summary all (2 != 1)",
        )

        make_fake_make(
            fake_make_path,
            {
                **EXPECTED_MAKE_EXPANSIONS,
                "phase7": [
                    line
                    for line in EXPECTED_MAKE_EXPANSIONS["phase7"]
                    if line
                    != "python3 scripts/zigux/check-phase7-argv-split-packet.py"
                ],
            },
        )
        expect_failure(
            "missing_argv_split_packet_live_in_bundle",
            tmp_root,
            fake_make_env,
            "phase7: missing expected wrapper expansion: python3 scripts/zigux/check-phase7-argv-split-packet.py",
        )

        make_fake_make(
            fake_make_path,
            {
                **EXPECTED_MAKE_EXPANSIONS,
                "phase7": [
                    line
                    for line in EXPECTED_MAKE_EXPANSIONS["phase7"]
                    if line
                    != "python3 scripts/zigux/check-phase7-argv-split-parity.py"
                ],
            },
        )
        expect_failure(
            "missing_argv_split_live_in_bundle",
            tmp_root,
            fake_make_env,
            "phase7: missing expected wrapper expansion: python3 scripts/zigux/check-phase7-argv-split-parity.py",
        )

        make_fake_make(
            fake_make_path,
            {
                **EXPECTED_MAKE_EXPANSIONS,
                "phase7": [
                    line
                    for line in EXPECTED_MAKE_EXPANSIONS["phase7"]
                    if line
                    != "python3 scripts/zigux/check-phase7-rbtree-parity.py"
                ],
            },
        )
        expect_failure(
            "missing_rbtree_live_in_bundle",
            tmp_root,
            fake_make_env,
            "phase7: missing expected wrapper expansion: python3 scripts/zigux/check-phase7-rbtree-parity.py",
        )

        make_fake_make(
            fake_make_path,
            {
                **EXPECTED_MAKE_EXPANSIONS,
                "phase7": [
                    *EXPECTED_MAKE_EXPANSIONS["phase7"],
                    "zig build test --build-file zigux/tests/build.zig",
                ],
            },
        )
        expect_failure(
            "stale_build_in_phase7_bundle",
            tmp_root,
            fake_make_env,
            "phase7: unexpected wrapper expansion: zig build test --build-file zigux/tests/build.zig",
        )

    print("PHASE7_MAKE_WRAPPER_SELF_TEST=pass")
    print("PHASE7_MAKE_WRAPPER_SELF_TEST_CASE_COUNT=24")
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
