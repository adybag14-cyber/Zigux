#!/usr/bin/env python3
from __future__ import annotations

import argparse
import subprocess
import sys
import tempfile
from collections import Counter
from dataclasses import dataclass
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve()
ROOT = SCRIPT_PATH.parents[2] if len(SCRIPT_PATH.parents) > 2 else SCRIPT_PATH.parent


@dataclass(frozen=True)
class SelfTestTarget:
    relpath: str
    marker: str | None
    extra_markers: tuple[str, ...] = ()


SELF_TEST_TARGETS = (
    SelfTestTarget(
        "scripts/zigux/validate-phase3.py",
        "PHASE3_VALIDATE_SELF_TEST=pass",
        ("PHASE3_VALIDATE_SELF_TEST_CASE_COUNT=",),
    ),
    SelfTestTarget(
        "scripts/zigux/check-phase3-selftest-surface.py",
        "PHASE3_SELFTEST_SURFACE_SELF_TEST=pass",
        ("PHASE3_SELFTEST_SURFACE_SELF_TEST_CASE_COUNT=",),
    ),
    SelfTestTarget(
        "scripts/zigux/check-phase3-readme-tooling-inventory.py",
        "PHASE3_README_TOOLING_INVENTORY_SELF_TEST=pass",
        ("PHASE3_README_TOOLING_INVENTORY_SELF_TEST_CASE_COUNT=",),
    ),
    SelfTestTarget(
        "scripts/zigux/check-phase3-abi-dump-gate.py",
        "PHASE3_ABI_DUMP_GATE_SELF_TEST=pass",
        ("PHASE3_ABI_DUMP_GATE_SELF_TEST_CASE_COUNT=",),
    ),
    SelfTestTarget(
        "scripts/zigux/check-phase3-catalog-selftest.py",
        "PHASE3_CATALOG_SELF_TEST=pass",
        ("PHASE3_CATALOG_SELF_TEST_CASE_COUNT=",),
    ),
    SelfTestTarget(
        "scripts/zigux/validate-phase3-abi-bindings-syntax.py",
        "PHASE3_ABI_BINDINGS_SYNTAX_SELF_TEST=pass",
        ("PHASE3_ABI_BINDINGS_SYNTAX_SELF_TEST_CASE_COUNT=",),
    ),
    SelfTestTarget(
        "scripts/zigux/survey-phase3-abi-constant-parity.py",
        "PHASE3_ABI_CONSTANT_PARITY_SELF_TEST=pass",
        ("PHASE3_ABI_CONSTANT_PARITY_SELF_TEST_CASE_COUNT=",),
    ),
    SelfTestTarget(
        "scripts/zigux/validate-phase3-policy-unsafe-survey.py",
        "PHASE3_POLICY_UNSAFE_SURVEY_SELF_TEST=pass",
        ("PHASE3_POLICY_UNSAFE_SURVEY_SELF_TEST_CASE_COUNT=",),
    ),
    SelfTestTarget(
        "scripts/zigux/check-phase3-policy-byte-guards.py",
        "PHASE3_POLICY_BYTE_GUARDS_SELF_TEST=pass",
        ("PHASE3_POLICY_BYTE_GUARDS_SELF_TEST_CASE_COUNT=",),
    ),
    SelfTestTarget(
        "scripts/zigux/validate-phase3-low-level-wrapper-survey.py",
        "PHASE3_LOW_LEVEL_WRAPPER_SURVEY_SELF_TEST=pass",
        ("PHASE3_LOW_LEVEL_WRAPPER_SURVEY_SELF_TEST_CASE_COUNT=",),
    ),
    SelfTestTarget(
        "scripts/zigux/validate-phase3-export-uapi-survey.py",
        "PHASE3_EXPORT_UAPI_SURVEY_SELF_TEST=pass",
        ("PHASE3_EXPORT_UAPI_SURVEY_SELF_TEST_CASE_COUNT=",),
    ),
    SelfTestTarget(
        "scripts/zigux/phase3_catalog.py",
        "PHASE3_CATALOG_SELF_TEST=pass",
        ("PHASE3_CATALOG_SELF_TEST_CASE_COUNT=",),
    ),
    SelfTestTarget(
        "scripts/zigux/phase3_check_lib.py",
        "PHASE3_CHECK_LIB_SELF_TEST=pass",
        ("PHASE3_CHECK_LIB_SELF_TEST_CASE_COUNT=",),
    ),
    SelfTestTarget(
        "scripts/zigux/run-phase3-checks.py",
        "PHASE3_RUNNER_SELF_TEST=pass",
        ("PHASE3_RUNNER_SELF_TEST_CASE_COUNT=",),
    ),
    SelfTestTarget(
        "scripts/zigux/generate-phase3-check-wrappers.py",
        "PHASE3_WRAPPER_SELF_TEST=pass",
        ("PHASE3_WRAPPER_SELF_TEST_CASE_COUNT=",),
    ),
)


def exact_output_marker_count(output: str, marker: str) -> int:
    return Counter(output.splitlines()).get(marker, 0)


def prefix_output_marker_count(output: str, prefix: str) -> int:
    return sum(1 for line in output.splitlines() if line.startswith(prefix))


def run_targets(root: Path, targets: tuple[SelfTestTarget, ...] = SELF_TEST_TARGETS) -> list[str]:
    issues: list[str] = []
    for target in targets:
        script_path = root / target.relpath
        if not script_path.exists():
            issues.append(f"missing_script:{target.relpath}")
            continue

        completed = subprocess.run(
            [sys.executable, str(script_path), "--self-test"],
            cwd=str(root),
            capture_output=True,
            text=True,
        )
        if completed.returncode != 0:
            issues.append(f"self_test_failed:{target.relpath}:rc={completed.returncode}")
            stdout = completed.stdout.strip()
            stderr = completed.stderr.strip()
            if stdout:
                issues.append(f"self_test_stdout:{target.relpath}:{stdout}")
            if stderr:
                issues.append(f"self_test_stderr:{target.relpath}:{stderr}")
            continue

        if target.marker:
            marker_count = exact_output_marker_count(completed.stdout, target.marker)
            if marker_count == 0:
                issues.append(f"missing_pass_marker:{target.relpath}:{target.marker}")
            elif marker_count != 1:
                issues.append(f"duplicate_pass_marker:{target.relpath}:{marker_count}:{target.marker}")
        for marker in target.extra_markers:
            marker_count = (
                prefix_output_marker_count(completed.stdout, marker)
                if marker.endswith("=")
                else exact_output_marker_count(completed.stdout, marker)
            )
            if marker_count == 0:
                issues.append(f"missing_aux_marker:{target.relpath}:{marker}")
            elif marker_count != 1:
                issues.append(f"duplicate_aux_marker:{target.relpath}:{marker_count}:{marker}")

    return issues


def write_script(
    path: Path,
    marker: str,
    *,
    exit_code: int = 0,
    extra_markers: tuple[str, ...] = (),
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "#!/usr/bin/env python3",
        "from __future__ import annotations",
        "",
        "import sys",
        "",
        'if "--self-test" in sys.argv:',
        f'    print("{marker}")',
    ]
    for extra_marker in extra_markers:
        rendered_marker = f"{extra_marker}1" if extra_marker.endswith("=") else extra_marker
        lines.append(f'    print("{rendered_marker}")')
    lines.extend(
        [
            f"    raise SystemExit({exit_code})",
            "",
            'raise SystemExit("expected --self-test")',
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8", newline="\n")


def _populate_root(root: Path) -> None:
    for target in SELF_TEST_TARGETS:
        write_script(root / target.relpath, target.marker or "PASS", extra_markers=target.extra_markers)


def _require_target(
    relpath: str,
    marker: str,
    *,
    extra_markers: tuple[str, ...] = (),
    targets: tuple[SelfTestTarget, ...] = SELF_TEST_TARGETS,
) -> None:
    matches = [target for target in targets if target.relpath == relpath]
    assert len(matches) == 1, f"expected exactly one self-test target for {relpath}"
    target = matches[0]
    assert target.marker == marker, f"unexpected pass marker for {relpath}: {target.marker!r}"
    assert target.extra_markers == extra_markers, (
        f"unexpected aux markers for {relpath}: {target.extra_markers!r}"
    )


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase3_validator_selftest_runner_") as tmp_dir:
        tmp_root = Path(tmp_dir)

        _require_target(
            "scripts/zigux/validate-phase3.py",
            "PHASE3_VALIDATE_SELF_TEST=pass",
            extra_markers=("PHASE3_VALIDATE_SELF_TEST_CASE_COUNT=",),
        )
        case_count += 1
        _require_target(
            "scripts/zigux/check-phase3-selftest-surface.py",
            "PHASE3_SELFTEST_SURFACE_SELF_TEST=pass",
            extra_markers=("PHASE3_SELFTEST_SURFACE_SELF_TEST_CASE_COUNT=",),
        )
        case_count += 1
        _require_target(
            "scripts/zigux/check-phase3-readme-tooling-inventory.py",
            "PHASE3_README_TOOLING_INVENTORY_SELF_TEST=pass",
            extra_markers=("PHASE3_README_TOOLING_INVENTORY_SELF_TEST_CASE_COUNT=",),
        )
        case_count += 1
        _require_target(
            "scripts/zigux/check-phase3-abi-dump-gate.py",
            "PHASE3_ABI_DUMP_GATE_SELF_TEST=pass",
            extra_markers=("PHASE3_ABI_DUMP_GATE_SELF_TEST_CASE_COUNT=",),
        )
        case_count += 1
        _require_target(
            "scripts/zigux/check-phase3-catalog-selftest.py",
            "PHASE3_CATALOG_SELF_TEST=pass",
            extra_markers=("PHASE3_CATALOG_SELF_TEST_CASE_COUNT=",),
        )
        case_count += 1
        _require_target(
            "scripts/zigux/validate-phase3-abi-bindings-syntax.py",
            "PHASE3_ABI_BINDINGS_SYNTAX_SELF_TEST=pass",
            extra_markers=("PHASE3_ABI_BINDINGS_SYNTAX_SELF_TEST_CASE_COUNT=",),
        )
        case_count += 1
        _require_target(
            "scripts/zigux/survey-phase3-abi-constant-parity.py",
            "PHASE3_ABI_CONSTANT_PARITY_SELF_TEST=pass",
            extra_markers=("PHASE3_ABI_CONSTANT_PARITY_SELF_TEST_CASE_COUNT=",),
        )
        case_count += 1
        _require_target(
            "scripts/zigux/validate-phase3-policy-unsafe-survey.py",
            "PHASE3_POLICY_UNSAFE_SURVEY_SELF_TEST=pass",
            extra_markers=("PHASE3_POLICY_UNSAFE_SURVEY_SELF_TEST_CASE_COUNT=",),
        )
        case_count += 1
        _require_target(
            "scripts/zigux/check-phase3-policy-byte-guards.py",
            "PHASE3_POLICY_BYTE_GUARDS_SELF_TEST=pass",
            extra_markers=("PHASE3_POLICY_BYTE_GUARDS_SELF_TEST_CASE_COUNT=",),
        )
        case_count += 1
        _require_target(
            "scripts/zigux/validate-phase3-low-level-wrapper-survey.py",
            "PHASE3_LOW_LEVEL_WRAPPER_SURVEY_SELF_TEST=pass",
            extra_markers=("PHASE3_LOW_LEVEL_WRAPPER_SURVEY_SELF_TEST_CASE_COUNT=",),
        )
        case_count += 1
        _require_target(
            "scripts/zigux/validate-phase3-export-uapi-survey.py",
            "PHASE3_EXPORT_UAPI_SURVEY_SELF_TEST=pass",
            extra_markers=("PHASE3_EXPORT_UAPI_SURVEY_SELF_TEST_CASE_COUNT=",),
        )
        case_count += 1
        _require_target(
            "scripts/zigux/phase3_catalog.py",
            "PHASE3_CATALOG_SELF_TEST=pass",
            extra_markers=("PHASE3_CATALOG_SELF_TEST_CASE_COUNT=",),
        )
        case_count += 1
        _require_target(
            "scripts/zigux/phase3_check_lib.py",
            "PHASE3_CHECK_LIB_SELF_TEST=pass",
            extra_markers=("PHASE3_CHECK_LIB_SELF_TEST_CASE_COUNT=",),
        )
        case_count += 1
        _require_target(
            "scripts/zigux/run-phase3-checks.py",
            "PHASE3_RUNNER_SELF_TEST=pass",
            extra_markers=("PHASE3_RUNNER_SELF_TEST_CASE_COUNT=",),
        )
        case_count += 1
        _require_target(
            "scripts/zigux/generate-phase3-check-wrappers.py",
            "PHASE3_WRAPPER_SELF_TEST=pass",
            extra_markers=("PHASE3_WRAPPER_SELF_TEST_CASE_COUNT=",),
        )
        case_count += 1

        success_root = tmp_root / "success"
        _populate_root(success_root)
        assert run_targets(success_root) == []
        case_count += 1

        missing_validate_aux_root = tmp_root / "missing-validate-aux"
        _populate_root(missing_validate_aux_root)
        write_script(
            missing_validate_aux_root / "scripts/zigux/validate-phase3.py",
            "PHASE3_VALIDATE_SELF_TEST=pass",
        )
        assert run_targets(missing_validate_aux_root) == [
            "missing_aux_marker:scripts/zigux/validate-phase3.py:PHASE3_VALIDATE_SELF_TEST_CASE_COUNT="
        ]
        case_count += 1

        duplicate_validate_aux_root = tmp_root / "duplicate-validate-aux"
        _populate_root(duplicate_validate_aux_root)
        duplicate_validate_aux_path = duplicate_validate_aux_root / "scripts/zigux/validate-phase3.py"
        duplicate_validate_aux_path.write_text(
            "\n".join(
                [
                    "#!/usr/bin/env python3",
                    "from __future__ import annotations",
                    "",
                    "import sys",
                    "",
                    'if "--self-test" in sys.argv:',
                    '    print("PHASE3_VALIDATE_SELF_TEST=pass")',
                    '    print("PHASE3_VALIDATE_SELF_TEST_CASE_COUNT=9")',
                    '    print("PHASE3_VALIDATE_SELF_TEST_CASE_COUNT=10")',
                    "    raise SystemExit(0)",
                    "",
                    'raise SystemExit("expected --self-test")',
                    "",
                ]
            ),
            encoding="utf-8",
            newline="\n",
        )
        assert run_targets(duplicate_validate_aux_root) == [
            "duplicate_aux_marker:scripts/zigux/validate-phase3.py:2:PHASE3_VALIDATE_SELF_TEST_CASE_COUNT="
        ]
        case_count += 1

        missing_selftest_surface_aux_root = tmp_root / "missing-selftest-surface-aux"
        _populate_root(missing_selftest_surface_aux_root)
        write_script(
            missing_selftest_surface_aux_root / "scripts/zigux/check-phase3-selftest-surface.py",
            "PHASE3_SELFTEST_SURFACE_SELF_TEST=pass",
        )
        assert run_targets(missing_selftest_surface_aux_root) == [
            "missing_aux_marker:scripts/zigux/check-phase3-selftest-surface.py:PHASE3_SELFTEST_SURFACE_SELF_TEST_CASE_COUNT="
        ]
        case_count += 1

        wrong_selftest_surface_marker_root = tmp_root / "wrong-selftest-surface-marker"
        _populate_root(wrong_selftest_surface_marker_root)
        write_script(
            wrong_selftest_surface_marker_root / "scripts/zigux/check-phase3-selftest-surface.py",
            "WRONG_MARKER=pass",
        )
        assert run_targets(wrong_selftest_surface_marker_root) == [
            "missing_pass_marker:scripts/zigux/check-phase3-selftest-surface.py:PHASE3_SELFTEST_SURFACE_SELF_TEST=pass",
            "missing_aux_marker:scripts/zigux/check-phase3-selftest-surface.py:PHASE3_SELFTEST_SURFACE_SELF_TEST_CASE_COUNT=",
        ]
        case_count += 1

        duplicate_selftest_surface_aux_root = tmp_root / "duplicate-selftest-surface-aux"
        _populate_root(duplicate_selftest_surface_aux_root)
        duplicate_selftest_surface_aux_path = (
            duplicate_selftest_surface_aux_root / "scripts/zigux/check-phase3-selftest-surface.py"
        )
        duplicate_selftest_surface_aux_path.write_text(
            "\n".join(
                [
                    "#!/usr/bin/env python3",
                    "from __future__ import annotations",
                    "",
                    "import sys",
                    "",
                    'if "--self-test" in sys.argv:',
                    '    print("PHASE3_SELFTEST_SURFACE_SELF_TEST=pass")',
                    '    print("PHASE3_SELFTEST_SURFACE_SELF_TEST_CASE_COUNT=1")',
                    '    print("PHASE3_SELFTEST_SURFACE_SELF_TEST_CASE_COUNT=2")',
                    "    raise SystemExit(0)",
                    "",
                    'raise SystemExit("expected --self-test")',
                    "",
                ]
            ),
            encoding="utf-8",
            newline="\n",
        )
        assert run_targets(duplicate_selftest_surface_aux_root) == [
            "duplicate_aux_marker:scripts/zigux/check-phase3-selftest-surface.py:2:PHASE3_SELFTEST_SURFACE_SELF_TEST_CASE_COUNT="
        ]
        case_count += 1

        missing_readme_tooling_aux_root = tmp_root / "missing-readme-tooling-aux"
        _populate_root(missing_readme_tooling_aux_root)
        write_script(
            missing_readme_tooling_aux_root / "scripts/zigux/check-phase3-readme-tooling-inventory.py",
            "PHASE3_README_TOOLING_INVENTORY_SELF_TEST=pass",
        )
        assert run_targets(missing_readme_tooling_aux_root) == [
            "missing_aux_marker:scripts/zigux/check-phase3-readme-tooling-inventory.py:PHASE3_README_TOOLING_INVENTORY_SELF_TEST_CASE_COUNT="
        ]
        case_count += 1

        duplicate_readme_tooling_aux_root = tmp_root / "duplicate-readme-tooling-aux"
        _populate_root(duplicate_readme_tooling_aux_root)
        duplicate_readme_tooling_aux_path = (
            duplicate_readme_tooling_aux_root
            / "scripts/zigux/check-phase3-readme-tooling-inventory.py"
        )
        duplicate_readme_tooling_aux_path.write_text(
            "\n".join(
                [
                    "#!/usr/bin/env python3",
                    "from __future__ import annotations",
                    "",
                    "import sys",
                    "",
                    'if "--self-test" in sys.argv:',
                    '    print("PHASE3_README_TOOLING_INVENTORY_SELF_TEST=pass")',
                    '    print("PHASE3_README_TOOLING_INVENTORY_SELF_TEST_CASE_COUNT=1")',
                    '    print("PHASE3_README_TOOLING_INVENTORY_SELF_TEST_CASE_COUNT=2")',
                    "    raise SystemExit(0)",
                    "",
                    'raise SystemExit("expected --self-test")',
                    "",
                ]
            ),
            encoding="utf-8",
            newline="\n",
        )
        assert run_targets(duplicate_readme_tooling_aux_root) == [
            "duplicate_aux_marker:scripts/zigux/check-phase3-readme-tooling-inventory.py:2:PHASE3_README_TOOLING_INVENTORY_SELF_TEST_CASE_COUNT="
        ]
        case_count += 1

        missing_abi_dump_gate_aux_root = tmp_root / "missing-abi-dump-gate-aux"
        _populate_root(missing_abi_dump_gate_aux_root)
        write_script(
            missing_abi_dump_gate_aux_root / "scripts/zigux/check-phase3-abi-dump-gate.py",
            "PHASE3_ABI_DUMP_GATE_SELF_TEST=pass",
        )
        assert run_targets(missing_abi_dump_gate_aux_root) == [
            "missing_aux_marker:scripts/zigux/check-phase3-abi-dump-gate.py:PHASE3_ABI_DUMP_GATE_SELF_TEST_CASE_COUNT="
        ]
        case_count += 1

        duplicate_abi_dump_gate_aux_root = tmp_root / "duplicate-abi-dump-gate-aux"
        _populate_root(duplicate_abi_dump_gate_aux_root)
        duplicate_abi_dump_gate_aux_path = (
            duplicate_abi_dump_gate_aux_root / "scripts/zigux/check-phase3-abi-dump-gate.py"
        )
        duplicate_abi_dump_gate_aux_path.write_text(
            "\n".join(
                [
                    "#!/usr/bin/env python3",
                    "from __future__ import annotations",
                    "",
                    "import sys",
                    "",
                    'if "--self-test" in sys.argv:',
                    '    print("PHASE3_ABI_DUMP_GATE_SELF_TEST=pass")',
                    '    print("PHASE3_ABI_DUMP_GATE_SELF_TEST_CASE_COUNT=1")',
                    '    print("PHASE3_ABI_DUMP_GATE_SELF_TEST_CASE_COUNT=2")',
                    "    raise SystemExit(0)",
                    "",
                    'raise SystemExit("expected --self-test")',
                    "",
                ]
            ),
            encoding="utf-8",
            newline="\n",
        )
        assert run_targets(duplicate_abi_dump_gate_aux_root) == [
            "duplicate_aux_marker:scripts/zigux/check-phase3-abi-dump-gate.py:2:PHASE3_ABI_DUMP_GATE_SELF_TEST_CASE_COUNT="
        ]
        case_count += 1

        missing_catalog_selftest_aux_root = tmp_root / "missing-catalog-selftest-aux"
        _populate_root(missing_catalog_selftest_aux_root)
        write_script(
            missing_catalog_selftest_aux_root / "scripts/zigux/check-phase3-catalog-selftest.py",
            "PHASE3_CATALOG_SELF_TEST=pass",
        )
        assert run_targets(missing_catalog_selftest_aux_root) == [
            "missing_aux_marker:scripts/zigux/check-phase3-catalog-selftest.py:PHASE3_CATALOG_SELF_TEST_CASE_COUNT="
        ]
        case_count += 1

        duplicate_catalog_selftest_aux_root = tmp_root / "duplicate-catalog-selftest-aux"
        _populate_root(duplicate_catalog_selftest_aux_root)
        duplicate_catalog_selftest_aux_path = (
            duplicate_catalog_selftest_aux_root / "scripts/zigux/check-phase3-catalog-selftest.py"
        )
        duplicate_catalog_selftest_aux_path.write_text(
            "\n".join(
                [
                    "#!/usr/bin/env python3",
                    "from __future__ import annotations",
                    "",
                    "import sys",
                    "",
                    'if "--self-test" in sys.argv:',
                    '    print("PHASE3_CATALOG_SELF_TEST=pass")',
                    '    print("PHASE3_CATALOG_SELF_TEST_CASE_COUNT=1")',
                    '    print("PHASE3_CATALOG_SELF_TEST_CASE_COUNT=2")',
                    "    raise SystemExit(0)",
                    "",
                    'raise SystemExit("expected --self-test")',
                    "",
                ]
            ),
            encoding="utf-8",
            newline="\n",
        )
        assert run_targets(duplicate_catalog_selftest_aux_root) == [
            "duplicate_aux_marker:scripts/zigux/check-phase3-catalog-selftest.py:2:PHASE3_CATALOG_SELF_TEST_CASE_COUNT="
        ]
        case_count += 1

        missing_root = tmp_root / "missing"
        _populate_root(missing_root)
        (missing_root / "scripts/zigux/survey-phase3-abi-constant-parity.py").unlink()
        assert run_targets(missing_root) == [
            "missing_script:scripts/zigux/survey-phase3-abi-constant-parity.py"
        ]
        case_count += 1

        wrong_marker_root = tmp_root / "wrong-marker"
        _populate_root(wrong_marker_root)
        write_script(
            wrong_marker_root / "scripts/zigux/survey-phase3-abi-constant-parity.py",
            "WRONG_MARKER=pass",
        )
        assert run_targets(wrong_marker_root) == [
            "missing_pass_marker:scripts/zigux/survey-phase3-abi-constant-parity.py:PHASE3_ABI_CONSTANT_PARITY_SELF_TEST=pass",
            "missing_aux_marker:scripts/zigux/survey-phase3-abi-constant-parity.py:PHASE3_ABI_CONSTANT_PARITY_SELF_TEST_CASE_COUNT=",
        ]
        case_count += 1

        wrong_abi_bindings_marker_root = tmp_root / "wrong-abi-bindings-marker"
        _populate_root(wrong_abi_bindings_marker_root)
        write_script(
            wrong_abi_bindings_marker_root / "scripts/zigux/validate-phase3-abi-bindings-syntax.py",
            "WRONG_MARKER=pass",
        )
        assert run_targets(wrong_abi_bindings_marker_root) == [
            "missing_pass_marker:scripts/zigux/validate-phase3-abi-bindings-syntax.py:PHASE3_ABI_BINDINGS_SYNTAX_SELF_TEST=pass",
            "missing_aux_marker:scripts/zigux/validate-phase3-abi-bindings-syntax.py:PHASE3_ABI_BINDINGS_SYNTAX_SELF_TEST_CASE_COUNT=",
        ]
        case_count += 1

        missing_abi_bindings_aux_root = tmp_root / "missing-abi-bindings-aux"
        _populate_root(missing_abi_bindings_aux_root)
        write_script(
            missing_abi_bindings_aux_root / "scripts/zigux/validate-phase3-abi-bindings-syntax.py",
            "PHASE3_ABI_BINDINGS_SYNTAX_SELF_TEST=pass",
        )
        assert run_targets(missing_abi_bindings_aux_root) == [
            "missing_aux_marker:scripts/zigux/validate-phase3-abi-bindings-syntax.py:PHASE3_ABI_BINDINGS_SYNTAX_SELF_TEST_CASE_COUNT="
        ]
        case_count += 1

        duplicate_abi_bindings_aux_root = tmp_root / "duplicate-abi-bindings-aux"
        _populate_root(duplicate_abi_bindings_aux_root)
        duplicate_abi_bindings_aux_path = (
            duplicate_abi_bindings_aux_root / "scripts/zigux/validate-phase3-abi-bindings-syntax.py"
        )
        duplicate_abi_bindings_aux_path.write_text(
            "\n".join(
                [
                    "#!/usr/bin/env python3",
                    "from __future__ import annotations",
                    "",
                    "import sys",
                    "",
                    'if "--self-test" in sys.argv:',
                    '    print("PHASE3_ABI_BINDINGS_SYNTAX_SELF_TEST=pass")',
                    '    print("PHASE3_ABI_BINDINGS_SYNTAX_SELF_TEST_CASE_COUNT=1")',
                    '    print("PHASE3_ABI_BINDINGS_SYNTAX_SELF_TEST_CASE_COUNT=2")',
                    "    raise SystemExit(0)",
                    "",
                    'raise SystemExit("expected --self-test")',
                    "",
                ]
            ),
            encoding="utf-8",
            newline="\n",
        )
        assert run_targets(duplicate_abi_bindings_aux_root) == [
            "duplicate_aux_marker:scripts/zigux/validate-phase3-abi-bindings-syntax.py:2:PHASE3_ABI_BINDINGS_SYNTAX_SELF_TEST_CASE_COUNT="
        ]
        case_count += 1

        duplicate_marker_root = tmp_root / "duplicate-marker"
        _populate_root(duplicate_marker_root)
        duplicate_path = duplicate_marker_root / "scripts/zigux/survey-phase3-abi-constant-parity.py"
        duplicate_path.write_text(
            "\n".join(
                [
                    "#!/usr/bin/env python3",
                    "from __future__ import annotations",
                    "",
                    "import sys",
                    "",
                    'if "--self-test" in sys.argv:',
                    '    print("PHASE3_ABI_CONSTANT_PARITY_SELF_TEST=pass")',
                    '    print("PHASE3_ABI_CONSTANT_PARITY_SELF_TEST=pass")',
                    "    raise SystemExit(0)",
                    "",
                    'raise SystemExit("expected --self-test")',
                    "",
                ]
            ),
            encoding="utf-8",
            newline="\n",
        )
        assert run_targets(duplicate_marker_root) == [
            "duplicate_pass_marker:scripts/zigux/survey-phase3-abi-constant-parity.py:2:PHASE3_ABI_CONSTANT_PARITY_SELF_TEST=pass",
            "missing_aux_marker:scripts/zigux/survey-phase3-abi-constant-parity.py:PHASE3_ABI_CONSTANT_PARITY_SELF_TEST_CASE_COUNT=",
        ]
        case_count += 1

        failing_root = tmp_root / "failing"
        _populate_root(failing_root)
        write_script(
            failing_root / "scripts/zigux/survey-phase3-abi-constant-parity.py",
            "PHASE3_ABI_CONSTANT_PARITY_SELF_TEST=pass",
            exit_code=7,
        )
        assert run_targets(failing_root) == [
            "self_test_failed:scripts/zigux/survey-phase3-abi-constant-parity.py:rc=7",
            "self_test_stdout:scripts/zigux/survey-phase3-abi-constant-parity.py:PHASE3_ABI_CONSTANT_PARITY_SELF_TEST=pass",
        ]
        case_count += 1

        missing_constant_aux_root = tmp_root / "missing-constant-aux"
        _populate_root(missing_constant_aux_root)
        write_script(
            missing_constant_aux_root / "scripts/zigux/survey-phase3-abi-constant-parity.py",
            "PHASE3_ABI_CONSTANT_PARITY_SELF_TEST=pass",
        )
        assert run_targets(missing_constant_aux_root) == [
            "missing_aux_marker:scripts/zigux/survey-phase3-abi-constant-parity.py:PHASE3_ABI_CONSTANT_PARITY_SELF_TEST_CASE_COUNT="
        ]
        case_count += 1

        duplicate_constant_aux_root = tmp_root / "duplicate-constant-aux"
        _populate_root(duplicate_constant_aux_root)
        duplicate_constant_aux_path = (
            duplicate_constant_aux_root / "scripts/zigux/survey-phase3-abi-constant-parity.py"
        )
        duplicate_constant_aux_path.write_text(
            "\n".join(
                [
                    "#!/usr/bin/env python3",
                    "from __future__ import annotations",
                    "",
                    "import sys",
                    "",
                    'if "--self-test" in sys.argv:',
                    '    print("PHASE3_ABI_CONSTANT_PARITY_SELF_TEST=pass")',
                    '    print("PHASE3_ABI_CONSTANT_PARITY_SELF_TEST_CASE_COUNT=1")',
                    '    print("PHASE3_ABI_CONSTANT_PARITY_SELF_TEST_CASE_COUNT=2")',
                    "    raise SystemExit(0)",
                    "",
                    'raise SystemExit("expected --self-test")',
                    "",
                ]
            ),
            encoding="utf-8",
            newline="\n",
        )
        assert run_targets(duplicate_constant_aux_root) == [
            "duplicate_aux_marker:scripts/zigux/survey-phase3-abi-constant-parity.py:2:PHASE3_ABI_CONSTANT_PARITY_SELF_TEST_CASE_COUNT="
        ]
        case_count += 1

        missing_aux_root = tmp_root / "missing-aux"
        _populate_root(missing_aux_root)
        write_script(
            missing_aux_root / "scripts/zigux/validate-phase3-export-uapi-survey.py",
            "PHASE3_EXPORT_UAPI_SURVEY_SELF_TEST=pass",
        )
        assert run_targets(missing_aux_root) == [
            "missing_aux_marker:scripts/zigux/validate-phase3-export-uapi-survey.py:PHASE3_EXPORT_UAPI_SURVEY_SELF_TEST_CASE_COUNT="
        ]
        case_count += 1

        duplicate_aux_root = tmp_root / "duplicate-aux"
        _populate_root(duplicate_aux_root)
        duplicate_aux_path = tmp_root / "duplicate-aux" / "scripts/zigux/validate-phase3-export-uapi-survey.py"
        duplicate_aux_path.write_text(
            "\n".join(
                [
                    "#!/usr/bin/env python3",
                    "from __future__ import annotations",
                    "",
                    "import sys",
                    "",
                    'if "--self-test" in sys.argv:',
                    '    print("PHASE3_EXPORT_UAPI_SURVEY_SELF_TEST=pass")',
                    '    print("PHASE3_EXPORT_UAPI_SURVEY_SELF_TEST_CASE_COUNT=1")',
                    '    print("PHASE3_EXPORT_UAPI_SURVEY_SELF_TEST_CASE_COUNT=2")',
                    "    raise SystemExit(0)",
                    "",
                    'raise SystemExit("expected --self-test")',
                    "",
                ]
            ),
            encoding="utf-8",
            newline="\n",
        )
        assert run_targets(duplicate_aux_root) == [
            "duplicate_aux_marker:scripts/zigux/validate-phase3-export-uapi-survey.py:2:PHASE3_EXPORT_UAPI_SURVEY_SELF_TEST_CASE_COUNT="
        ]
        case_count += 1

        missing_policy_aux_root = tmp_root / "missing-policy-aux"
        _populate_root(missing_policy_aux_root)
        write_script(
            missing_policy_aux_root / "scripts/zigux/validate-phase3-policy-unsafe-survey.py",
            "PHASE3_POLICY_UNSAFE_SURVEY_SELF_TEST=pass",
        )
        assert run_targets(missing_policy_aux_root) == [
            "missing_aux_marker:scripts/zigux/validate-phase3-policy-unsafe-survey.py:PHASE3_POLICY_UNSAFE_SURVEY_SELF_TEST_CASE_COUNT="
        ]
        case_count += 1

        duplicate_policy_aux_root = tmp_root / "duplicate-policy-aux"
        _populate_root(duplicate_policy_aux_root)
        duplicate_policy_aux_path = (
            duplicate_policy_aux_root / "scripts/zigux/validate-phase3-policy-unsafe-survey.py"
        )
        duplicate_policy_aux_path.write_text(
            "\n".join(
                [
                    "#!/usr/bin/env python3",
                    "from __future__ import annotations",
                    "",
                    "import sys",
                    "",
                    'if "--self-test" in sys.argv:',
                    '    print("PHASE3_POLICY_UNSAFE_SURVEY_SELF_TEST=pass")',
                    '    print("PHASE3_POLICY_UNSAFE_SURVEY_SELF_TEST_CASE_COUNT=1")',
                    '    print("PHASE3_POLICY_UNSAFE_SURVEY_SELF_TEST_CASE_COUNT=2")',
                    "    raise SystemExit(0)",
                    "",
                    'raise SystemExit("expected --self-test")',
                    "",
                ]
            ),
            encoding="utf-8",
            newline="\n",
        )
        assert run_targets(duplicate_policy_aux_root) == [
            "duplicate_aux_marker:scripts/zigux/validate-phase3-policy-unsafe-survey.py:2:PHASE3_POLICY_UNSAFE_SURVEY_SELF_TEST_CASE_COUNT="
        ]
        case_count += 1

        missing_policy_byte_aux_root = tmp_root / "missing-policy-byte-aux"
        _populate_root(missing_policy_byte_aux_root)
        write_script(
            missing_policy_byte_aux_root / "scripts/zigux/check-phase3-policy-byte-guards.py",
            "PHASE3_POLICY_BYTE_GUARDS_SELF_TEST=pass",
        )
        assert run_targets(missing_policy_byte_aux_root) == [
            "missing_aux_marker:scripts/zigux/check-phase3-policy-byte-guards.py:PHASE3_POLICY_BYTE_GUARDS_SELF_TEST_CASE_COUNT="
        ]
        case_count += 1

        duplicate_policy_byte_aux_root = tmp_root / "duplicate-policy-byte-aux"
        _populate_root(duplicate_policy_byte_aux_root)
        duplicate_policy_byte_aux_path = (
            duplicate_policy_byte_aux_root / "scripts/zigux/check-phase3-policy-byte-guards.py"
        )
        duplicate_policy_byte_aux_path.write_text(
            "\n".join(
                [
                    "#!/usr/bin/env python3",
                    "from __future__ import annotations",
                    "",
                    "import sys",
                    "",
                    'if "--self-test" in sys.argv:',
                    '    print("PHASE3_POLICY_BYTE_GUARDS_SELF_TEST=pass")',
                    '    print("PHASE3_POLICY_BYTE_GUARDS_SELF_TEST_CASE_COUNT=1")',
                    '    print("PHASE3_POLICY_BYTE_GUARDS_SELF_TEST_CASE_COUNT=2")',
                    "    raise SystemExit(0)",
                    "",
                    'raise SystemExit("expected --self-test")',
                    "",
                ]
            ),
            encoding="utf-8",
            newline="\n",
        )
        assert run_targets(duplicate_policy_byte_aux_root) == [
            "duplicate_aux_marker:scripts/zigux/check-phase3-policy-byte-guards.py:2:PHASE3_POLICY_BYTE_GUARDS_SELF_TEST_CASE_COUNT="
        ]
        case_count += 1

        missing_low_level_aux_root = tmp_root / "missing-low-level-aux"
        _populate_root(missing_low_level_aux_root)
        write_script(
            missing_low_level_aux_root / "scripts/zigux/validate-phase3-low-level-wrapper-survey.py",
            "PHASE3_LOW_LEVEL_WRAPPER_SURVEY_SELF_TEST=pass",
        )
        assert run_targets(missing_low_level_aux_root) == [
            "missing_aux_marker:scripts/zigux/validate-phase3-low-level-wrapper-survey.py:PHASE3_LOW_LEVEL_WRAPPER_SURVEY_SELF_TEST_CASE_COUNT="
        ]
        case_count += 1

        duplicate_low_level_aux_root = tmp_root / "duplicate-low-level-aux"
        _populate_root(duplicate_low_level_aux_root)
        duplicate_low_level_aux_path = (
            duplicate_low_level_aux_root / "scripts/zigux/validate-phase3-low-level-wrapper-survey.py"
        )
        duplicate_low_level_aux_path.write_text(
            "\n".join(
                [
                    "#!/usr/bin/env python3",
                    "from __future__ import annotations",
                    "",
                    "import sys",
                    "",
                    'if "--self-test" in sys.argv:',
                    '    print("PHASE3_LOW_LEVEL_WRAPPER_SURVEY_SELF_TEST=pass")',
                    '    print("PHASE3_LOW_LEVEL_WRAPPER_SURVEY_SELF_TEST_CASE_COUNT=1")',
                    '    print("PHASE3_LOW_LEVEL_WRAPPER_SURVEY_SELF_TEST_CASE_COUNT=2")',
                    "    raise SystemExit(0)",
                    "",
                    'raise SystemExit("expected --self-test")',
                    "",
                ]
            ),
            encoding="utf-8",
            newline="\n",
        )
        assert run_targets(duplicate_low_level_aux_root) == [
            "duplicate_aux_marker:scripts/zigux/validate-phase3-low-level-wrapper-survey.py:2:PHASE3_LOW_LEVEL_WRAPPER_SURVEY_SELF_TEST_CASE_COUNT="
        ]
        case_count += 1

        missing_check_lib_aux_root = tmp_root / "missing-check-lib-aux"
        _populate_root(missing_check_lib_aux_root)
        write_script(
            missing_check_lib_aux_root / "scripts/zigux/phase3_check_lib.py",
            "PHASE3_CHECK_LIB_SELF_TEST=pass",
        )
        assert run_targets(missing_check_lib_aux_root) == [
            "missing_aux_marker:scripts/zigux/phase3_check_lib.py:PHASE3_CHECK_LIB_SELF_TEST_CASE_COUNT="
        ]
        case_count += 1

        duplicate_check_lib_aux_root = tmp_root / "duplicate-check-lib-aux"
        _populate_root(duplicate_check_lib_aux_root)
        duplicate_check_lib_aux_path = duplicate_check_lib_aux_root / "scripts/zigux/phase3_check_lib.py"
        duplicate_check_lib_aux_path.write_text(
            "\n".join(
                [
                    "#!/usr/bin/env python3",
                    "from __future__ import annotations",
                    "",
                    "import sys",
                    "",
                    'if "--self-test" in sys.argv:',
                    '    print("PHASE3_CHECK_LIB_SELF_TEST=pass")',
                    '    print("PHASE3_CHECK_LIB_SELF_TEST_CASE_COUNT=1")',
                    '    print("PHASE3_CHECK_LIB_SELF_TEST_CASE_COUNT=2")',
                    "    raise SystemExit(0)",
                    "",
                    'raise SystemExit("expected --self-test")',
                    "",
                ]
            ),
            encoding="utf-8",
            newline="\n",
        )
        assert run_targets(duplicate_check_lib_aux_root) == [
            "duplicate_aux_marker:scripts/zigux/phase3_check_lib.py:2:PHASE3_CHECK_LIB_SELF_TEST_CASE_COUNT="
        ]
        case_count += 1

        missing_runner_aux_root = tmp_root / "missing-runner-aux"
        _populate_root(missing_runner_aux_root)
        write_script(
            missing_runner_aux_root / "scripts/zigux/run-phase3-checks.py",
            "PHASE3_RUNNER_SELF_TEST=pass",
        )
        assert run_targets(missing_runner_aux_root) == [
            "missing_aux_marker:scripts/zigux/run-phase3-checks.py:PHASE3_RUNNER_SELF_TEST_CASE_COUNT="
        ]
        case_count += 1

        duplicate_runner_aux_root = tmp_root / "duplicate-runner-aux"
        _populate_root(duplicate_runner_aux_root)
        duplicate_runner_aux_path = duplicate_runner_aux_root / "scripts/zigux/run-phase3-checks.py"
        duplicate_runner_aux_path.write_text(
            "\n".join(
                [
                    "#!/usr/bin/env python3",
                    "from __future__ import annotations",
                    "",
                    "import sys",
                    "",
                    'if "--self-test" in sys.argv:',
                    '    print("PHASE3_RUNNER_SELF_TEST=pass")',
                    '    print("PHASE3_RUNNER_SELF_TEST_CASE_COUNT=1")',
                    '    print("PHASE3_RUNNER_SELF_TEST_CASE_COUNT=2")',
                    "    raise SystemExit(0)",
                    "",
                    'raise SystemExit("expected --self-test")',
                    "",
                ]
            ),
            encoding="utf-8",
            newline="\n",
        )
        assert run_targets(duplicate_runner_aux_root) == [
            "duplicate_aux_marker:scripts/zigux/run-phase3-checks.py:2:PHASE3_RUNNER_SELF_TEST_CASE_COUNT="
        ]
        case_count += 1

        missing_wrapper_aux_root = tmp_root / "missing-wrapper-aux"
        _populate_root(missing_wrapper_aux_root)
        write_script(
            missing_wrapper_aux_root / "scripts/zigux/generate-phase3-check-wrappers.py",
            "PHASE3_WRAPPER_SELF_TEST=pass",
        )
        assert run_targets(missing_wrapper_aux_root) == [
            "missing_aux_marker:scripts/zigux/generate-phase3-check-wrappers.py:PHASE3_WRAPPER_SELF_TEST_CASE_COUNT="
        ]
        case_count += 1

        duplicate_wrapper_aux_root = tmp_root / "duplicate-wrapper-aux"
        _populate_root(duplicate_wrapper_aux_root)
        duplicate_wrapper_aux_path = (
            duplicate_wrapper_aux_root / "scripts/zigux/generate-phase3-check-wrappers.py"
        )
        duplicate_wrapper_aux_path.write_text(
            "\n".join(
                [
                    "#!/usr/bin/env python3",
                    "from __future__ import annotations",
                    "",
                    "import sys",
                    "",
                    'if "--self-test" in sys.argv:',
                    '    print("PHASE3_WRAPPER_SELF_TEST=pass")',
                    '    print("PHASE3_WRAPPER_SELF_TEST_CASE_COUNT=1")',
                    '    print("PHASE3_WRAPPER_SELF_TEST_CASE_COUNT=2")',
                    "    raise SystemExit(0)",
                    "",
                    'raise SystemExit("expected --self-test")',
                    "",
                ]
            ),
            encoding="utf-8",
            newline="\n",
        )
        assert run_targets(duplicate_wrapper_aux_root) == [
            "duplicate_aux_marker:scripts/zigux/generate-phase3-check-wrappers.py:2:PHASE3_WRAPPER_SELF_TEST_CASE_COUNT="
        ]
        case_count += 1

        wrong_low_level_marker_root = tmp_root / "wrong-low-level-marker"
        _populate_root(wrong_low_level_marker_root)
        write_script(
            wrong_low_level_marker_root / "scripts/zigux/validate-phase3-low-level-wrapper-survey.py",
            "WRONG_MARKER=pass",
        )
        assert run_targets(wrong_low_level_marker_root) == [
            "missing_pass_marker:scripts/zigux/validate-phase3-low-level-wrapper-survey.py:PHASE3_LOW_LEVEL_WRAPPER_SURVEY_SELF_TEST=pass",
            "missing_aux_marker:scripts/zigux/validate-phase3-low-level-wrapper-survey.py:PHASE3_LOW_LEVEL_WRAPPER_SURVEY_SELF_TEST_CASE_COUNT=",
        ]
        case_count += 1

        stderr_root = tmp_root / "stderr"
        _populate_root(stderr_root)
        stderr_path = stderr_root / "scripts/zigux/survey-phase3-abi-constant-parity.py"
        stderr_path.write_text(
            "\n".join(
                [
                    "#!/usr/bin/env python3",
                    "from __future__ import annotations",
                    "",
                    "import sys",
                    "",
                    'if "--self-test" in sys.argv:',
                    '    print("PHASE3_ABI_CONSTANT_PARITY_SELF_TEST=pass")',
                    '    print("broken", file=sys.stderr)',
                    "    raise SystemExit(3)",
                    "",
                    'raise SystemExit("expected --self-test")',
                    "",
                ]
            ),
            encoding="utf-8",
            newline="\n",
        )
        assert run_targets(stderr_root) == [
            "self_test_failed:scripts/zigux/survey-phase3-abi-constant-parity.py:rc=3",
            "self_test_stdout:scripts/zigux/survey-phase3-abi-constant-parity.py:PHASE3_ABI_CONSTANT_PARITY_SELF_TEST=pass",
            "self_test_stderr:scripts/zigux/survey-phase3-abi-constant-parity.py:broken",
        ]
        case_count += 1

    print("PHASE3_VALIDATOR_SELF_TEST=pass")
    print(f"PHASE3_VALIDATOR_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run the current Phase 3 validator helper self-tests through one shared runner."
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run isolated coverage for the shared Phase 3 validator self-test runner.",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = run_targets(ROOT)
    if issues:
        print("PHASE3_VALIDATOR_SELF_TEST=fail")
        print("PHASE3_VALIDATOR_SELF_TEST_ISSUES_START")
        for issue in issues:
            print(issue)
        print("PHASE3_VALIDATOR_SELF_TEST_ISSUES_END")
        return 1

    print("PHASE3_VALIDATOR_SELF_TEST=pass")
    print(f"PHASE3_VALIDATOR_SELF_TEST_TARGET_COUNT={len(SELF_TEST_TARGETS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())