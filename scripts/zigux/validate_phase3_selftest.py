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
PHASE3_VALIDATOR_SELF_TEST_CASE_COUNT = 30


@dataclass(frozen=True)
class SelfTestTarget:
    relpath: str
    marker: str | None
    extra_markers: tuple[str, ...] = ()


SELF_TEST_TARGETS = (
    SelfTestTarget("scripts/zigux/validate-phase3.py", "PHASE3_VALIDATE_SELF_TEST=pass"),
    SelfTestTarget(
        "scripts/zigux/check-phase3-selftest-surface.py",
        "PHASE3_SELFTEST_SURFACE_SELF_TEST=pass",
        ("PHASE3_SELFTEST_SURFACE_SELF_TEST_CASE_COUNT=20",),
    ),
    SelfTestTarget(
        "scripts/zigux/check-phase3-readme-tooling-inventory.py",
        "PHASE3_README_TOOLING_INVENTORY_SELF_TEST=pass",
    ),
    SelfTestTarget(
        "scripts/zigux/check-phase3-abi-dump-gate.py",
        "PHASE3_ABI_DUMP_GATE_SELF_TEST=pass",
        ("PHASE3_ABI_DUMP_GATE_SELF_TEST_CASE_COUNT=4",),
    ),
    SelfTestTarget(
        "scripts/zigux/check-phase3-catalog-selftest.py",
        "PHASE3_CATALOG_SELF_TEST=pass",
        ("PHASE3_CATALOG_SELF_TEST_CASE_COUNT=6",),
    ),
    SelfTestTarget(
        "scripts/zigux/validate-phase3-abi-bindings-syntax.py",
        "PHASE3_ABI_BINDINGS_SYNTAX_SELF_TEST=pass",
    ),
    SelfTestTarget(
        "scripts/zigux/validate-phase3-policy-unsafe-survey.py",
        "PHASE3_POLICY_UNSAFE_SURVEY_SELF_TEST=pass",
    ),
    SelfTestTarget(
        "scripts/zigux/validate-phase3-low-level-wrapper-survey.py",
        "PHASE3_LOW_LEVEL_WRAPPER_SURVEY_SELF_TEST=pass",
    ),
    SelfTestTarget(
        "scripts/zigux/validate-phase3-export-uapi-survey.py",
        "PHASE3_EXPORT_UAPI_SURVEY_SELF_TEST=pass",
        ("PHASE3_EXPORT_UAPI_SURVEY_SELF_TEST_CASE_COUNT=5",),
    ),
    SelfTestTarget(
        "scripts/zigux/phase3_catalog.py",
        "PHASE3_CATALOG_SELF_TEST=pass",
        ("PHASE3_CATALOG_SELF_TEST_CASE_COUNT=6",),
    ),
    SelfTestTarget("scripts/zigux/phase3_check_lib.py", "PHASE3_CHECK_LIB_SELF_TEST=pass"),
    SelfTestTarget("scripts/zigux/run-phase3-checks.py", "PHASE3_RUNNER_SELF_TEST=pass"),
    SelfTestTarget(
        "scripts/zigux/generate-phase3-check-wrappers.py",
        "PHASE3_WRAPPER_SELF_TEST=pass",
    ),
)


def exact_output_marker_count(output: str, marker: str) -> int:
    return Counter(output.splitlines()).get(marker, 0)


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
            marker_count = exact_output_marker_count(completed.stdout, marker)
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
    lines.extend(f'    print("{extra_marker}")' for extra_marker in extra_markers)
    lines.extend(
        [
            f"    raise SystemExit({exit_code})",
            "",
            'raise SystemExit("expected --self-test")',
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8", newline="\n")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase3_validator_selftest_runner_") as tmp_dir:
        root = Path(tmp_dir)
        for target in SELF_TEST_TARGETS:
            write_script(
                root / target.relpath,
                target.marker or "PASS",
                extra_markers=target.extra_markers,
            )

        issues = run_targets(root)
        assert issues == [], issues

        missing_root = Path(tmp_dir) / "missing"
        for target in SELF_TEST_TARGETS[1:]:
            write_script(
                missing_root / target.relpath,
                target.marker or "PASS",
                extra_markers=target.extra_markers,
            )
        issues = run_targets(missing_root)
        assert issues == [f"missing_script:{SELF_TEST_TARGETS[0].relpath}"], issues

        missing_low_level_wrapper_root = Path(tmp_dir) / "missing-low-level-wrapper"
        for target in SELF_TEST_TARGETS:
            if target.relpath.endswith("validate-phase3-low-level-wrapper-survey.py"):
                continue
            write_script(
                missing_low_level_wrapper_root / target.relpath,
                target.marker or "PASS",
                extra_markers=target.extra_markers,
            )
        issues = run_targets(missing_low_level_wrapper_root)
        assert issues == [
            "missing_script:scripts/zigux/validate-phase3-low-level-wrapper-survey.py"
        ], issues

        failing_root = Path(tmp_dir) / "failing"
        for target in SELF_TEST_TARGETS:
            exit_code = 7 if target.relpath.endswith("run-phase3-checks.py") else 0
            write_script(
                failing_root / target.relpath,
                target.marker or "PASS",
                exit_code=exit_code,
                extra_markers=target.extra_markers,
            )
        issues = run_targets(failing_root)
        assert f"self_test_failed:scripts/zigux/run-phase3-checks.py:rc=7" in issues

        validate_marker_root = Path(tmp_dir) / "validate-marker"
        for target in SELF_TEST_TARGETS:
            marker = (
                "WRONG_MARKER=pass"
                if target.relpath.endswith("validate-phase3.py")
                else (target.marker or "PASS")
            )
            write_script(
                validate_marker_root / target.relpath,
                marker,
                extra_markers=target.extra_markers,
            )
        issues = run_targets(validate_marker_root)
        assert (
            "missing_pass_marker:scripts/zigux/validate-phase3.py:PHASE3_VALIDATE_SELF_TEST=pass"
            in issues
        )

        substring_marker_root = Path(tmp_dir) / "substring-marker"
        for target in SELF_TEST_TARGETS:
            path = substring_marker_root / target.relpath
            if target.relpath.endswith("validate-phase3.py"):
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(
                    "\n".join(
                        [
                            "#!/usr/bin/env python3",
                            "from __future__ import annotations",
                            "",
                            "import sys",
                            "",
                            'if "--self-test" in sys.argv:',
                            '    print("note: PHASE3_VALIDATE_SELF_TEST=pass appears here but is not a standalone marker")',
                            "    raise SystemExit(0)",
                            "",
                            'raise SystemExit("expected --self-test")',
                            "",
                        ]
                    ),
                    encoding="utf-8",
                    newline="\n",
                )
                continue
            write_script(path, target.marker or "PASS", extra_markers=target.extra_markers)
        issues = run_targets(substring_marker_root)
        assert (
            "missing_pass_marker:scripts/zigux/validate-phase3.py:PHASE3_VALIDATE_SELF_TEST=pass"
            in issues
        )

        marker_root = Path(tmp_dir) / "marker"
        for target in SELF_TEST_TARGETS:
            marker = (
                "WRONG_MARKER=pass"
                if target.relpath.endswith("phase3_check_lib.py")
                else (target.marker or "PASS")
            )
            write_script(
                marker_root / target.relpath,
                marker,
                extra_markers=target.extra_markers,
            )
        issues = run_targets(marker_root)
        assert (
            "missing_pass_marker:scripts/zigux/phase3_check_lib.py:PHASE3_CHECK_LIB_SELF_TEST=pass"
            in issues
        )

        surface_marker_root = Path(tmp_dir) / "surface-marker"
        for target in SELF_TEST_TARGETS:
            marker = (
                "WRONG_MARKER=pass"
                if target.relpath.endswith("check-phase3-selftest-surface.py")
                else (target.marker or "PASS")
            )
            write_script(
                surface_marker_root / target.relpath,
                marker,
                extra_markers=target.extra_markers,
            )
        issues = run_targets(surface_marker_root)
        assert (
            "missing_pass_marker:scripts/zigux/check-phase3-selftest-surface.py:"
            "PHASE3_SELFTEST_SURFACE_SELF_TEST=pass"
            in issues
        )

        surface_count_root = Path(tmp_dir) / "surface-count"
        for target in SELF_TEST_TARGETS:
            extra_markers = (
                ()
                if target.relpath.endswith("check-phase3-selftest-surface.py")
                else target.extra_markers
            )
            write_script(
                surface_count_root / target.relpath,
                target.marker or "PASS",
                extra_markers=extra_markers,
            )
        issues = run_targets(surface_count_root)
        assert (
            "missing_aux_marker:scripts/zigux/check-phase3-selftest-surface.py:"
            "PHASE3_SELFTEST_SURFACE_SELF_TEST_CASE_COUNT=20"
            in issues
        )

        surface_duplicate_count_root = Path(tmp_dir) / "surface-duplicate-count"
        for target in SELF_TEST_TARGETS:
            path = surface_duplicate_count_root / target.relpath
            if target.relpath.endswith("check-phase3-selftest-surface.py"):
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(
                    "\n".join(
                        [
                            "#!/usr/bin/env python3",
                            "from __future__ import annotations",
                            "",
                            "import sys",
                            "",
                            'if "--self-test" in sys.argv:',
                            '    print("PHASE3_SELFTEST_SURFACE_SELF_TEST=pass")',
                            '    print("PHASE3_SELFTEST_SURFACE_SELF_TEST_CASE_COUNT=20")',
                            '    print("PHASE3_SELFTEST_SURFACE_SELF_TEST_CASE_COUNT=20")',
                            "    raise SystemExit(0)",
                            "",
                            'raise SystemExit("expected --self-test")',
                            "",
                        ]
                    ),
                    encoding="utf-8",
                    newline="\n",
                )
                continue
            write_script(path, target.marker or "PASS", extra_markers=target.extra_markers)
        issues = run_targets(surface_duplicate_count_root)
        assert (
            "duplicate_aux_marker:scripts/zigux/check-phase3-selftest-surface.py:2:"
            "PHASE3_SELFTEST_SURFACE_SELF_TEST_CASE_COUNT=20"
            in issues
        )

        tooling_inventory_marker_root = Path(tmp_dir) / "tooling-inventory-marker"
        for target in SELF_TEST_TARGETS:
            marker = (
                "WRONG_MARKER=pass"
                if target.relpath.endswith("check-phase3-readme-tooling-inventory.py")
                else (target.marker or "PASS")
            )
            write_script(
                tooling_inventory_marker_root / target.relpath,
                marker,
                extra_markers=target.extra_markers,
            )
        issues = run_targets(tooling_inventory_marker_root)
        assert (
            "missing_pass_marker:scripts/zigux/check-phase3-readme-tooling-inventory.py:"
            "PHASE3_README_TOOLING_INVENTORY_SELF_TEST=pass"
            in issues
        )

        tooling_inventory_duplicate_marker_root = Path(tmp_dir) / "tooling-inventory-duplicate-marker"
        for target in SELF_TEST_TARGETS:
            path = tooling_inventory_duplicate_marker_root / target.relpath
            if target.relpath.endswith("check-phase3-readme-tooling-inventory.py"):
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(
                    "\n".join(
                        [
                            "#!/usr/bin/env python3",
                            "from __future__ import annotations",
                            "",
                            "import sys",
                            "",
                            'if "--self-test" in sys.argv:',
                            '    print("PHASE3_README_TOOLING_INVENTORY_SELF_TEST=pass")',
                            '    print("PHASE3_README_TOOLING_INVENTORY_SELF_TEST=pass")',
                            "    raise SystemExit(0)",
                            "",
                            'raise SystemExit("expected --self-test")',
                            "",
                        ]
                    ),
                    encoding="utf-8",
                    newline="\n",
                )
                continue
            write_script(path, target.marker or "PASS", extra_markers=target.extra_markers)
        issues = run_targets(tooling_inventory_duplicate_marker_root)
        assert (
            "duplicate_pass_marker:scripts/zigux/check-phase3-readme-tooling-inventory.py:2:"
            "PHASE3_README_TOOLING_INVENTORY_SELF_TEST=pass"
            in issues
        )

        abi_dump_gate_marker_root = Path(tmp_dir) / "abi-dump-gate-marker"
        for target in SELF_TEST_TARGETS:
            marker = (
                "WRONG_MARKER=pass"
                if target.relpath.endswith("check-phase3-abi-dump-gate.py")
                else (target.marker or "PASS")
            )
            write_script(
                abi_dump_gate_marker_root / target.relpath,
                marker,
                extra_markers=target.extra_markers,
            )
        issues = run_targets(abi_dump_gate_marker_root)
        assert (
            "missing_pass_marker:scripts/zigux/check-phase3-abi-dump-gate.py:"
            "PHASE3_ABI_DUMP_GATE_SELF_TEST=pass"
            in issues
        )

        abi_dump_gate_duplicate_marker_root = Path(tmp_dir) / "abi-dump-gate-duplicate-marker"
        for target in SELF_TEST_TARGETS:
            path = abi_dump_gate_duplicate_marker_root / target.relpath
            if target.relpath.endswith("check-phase3-abi-dump-gate.py"):
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(
                    "\n".join(
                        [
                            "#!/usr/bin/env python3",
                            "from __future__ import annotations",
                            "",
                            "import sys",
                            "",
                            'if "--self-test" in sys.argv:',
                            '    print("PHASE3_ABI_DUMP_GATE_SELF_TEST=pass")',
                            '    print("PHASE3_ABI_DUMP_GATE_SELF_TEST=pass")',
                            '    print("PHASE3_ABI_DUMP_GATE_SELF_TEST_CASE_COUNT=4")',
                            "    raise SystemExit(0)",
                            "",
                            'raise SystemExit("expected --self-test")',
                            "",
                        ]
                    ),
                    encoding="utf-8",
                    newline="\n",
                )
                continue
            write_script(path, target.marker or "PASS", extra_markers=target.extra_markers)
        issues = run_targets(abi_dump_gate_duplicate_marker_root)
        assert (
            "duplicate_pass_marker:scripts/zigux/check-phase3-abi-dump-gate.py:2:"
            "PHASE3_ABI_DUMP_GATE_SELF_TEST=pass"
            in issues
        )

        abi_dump_gate_count_root = Path(tmp_dir) / "abi-dump-gate-count"
        for target in SELF_TEST_TARGETS:
            extra_markers = (
                ()
                if target.relpath.endswith("check-phase3-abi-dump-gate.py")
                else target.extra_markers
            )
            write_script(
                abi_dump_gate_count_root / target.relpath,
                target.marker or "PASS",
                extra_markers=extra_markers,
            )
        issues = run_targets(abi_dump_gate_count_root)
        assert (
            "missing_aux_marker:scripts/zigux/check-phase3-abi-dump-gate.py:"
            "PHASE3_ABI_DUMP_GATE_SELF_TEST_CASE_COUNT=4"
            in issues
        )

        abi_dump_gate_duplicate_count_root = Path(tmp_dir) / "abi-dump-gate-duplicate-count"
        for target in SELF_TEST_TARGETS:
            path = abi_dump_gate_duplicate_count_root / target.relpath
            if target.relpath.endswith("check-phase3-abi-dump-gate.py"):
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(
                    "\n".join(
                        [
                            "#!/usr/bin/env python3",
                            "from __future__ import annotations",
                            "",
                            "import sys",
                            "",
                            'if "--self-test" in sys.argv:',
                            '    print("PHASE3_ABI_DUMP_GATE_SELF_TEST=pass")',
                            '    print("PHASE3_ABI_DUMP_GATE_SELF_TEST_CASE_COUNT=4")',
                            '    print("PHASE3_ABI_DUMP_GATE_SELF_TEST_CASE_COUNT=4")',
                            "    raise SystemExit(0)",
                            "",
                            'raise SystemExit("expected --self-test")',
                            "",
                        ]
                    ),
                    encoding="utf-8",
                    newline="\n",
                )
                continue
            write_script(path, target.marker or "PASS", extra_markers=target.extra_markers)
        issues = run_targets(abi_dump_gate_duplicate_count_root)
        assert (
            "duplicate_aux_marker:scripts/zigux/check-phase3-abi-dump-gate.py:2:"
            "PHASE3_ABI_DUMP_GATE_SELF_TEST_CASE_COUNT=4"
            in issues
        )

        catalog_selftest_marker_root = Path(tmp_dir) / "catalog-selftest-marker"
        for target in SELF_TEST_TARGETS:
            marker = (
                "WRONG_MARKER=pass"
                if target.relpath.endswith("check-phase3-catalog-selftest.py")
                else (target.marker or "PASS")
            )
            write_script(
                catalog_selftest_marker_root / target.relpath,
                marker,
                extra_markers=target.extra_markers,
            )
        issues = run_targets(catalog_selftest_marker_root)
        assert (
            "missing_pass_marker:scripts/zigux/check-phase3-catalog-selftest.py:"
            "PHASE3_CATALOG_SELF_TEST=pass"
            in issues
        )

        catalog_selftest_count_root = Path(tmp_dir) / "catalog-selftest-count"
        for target in SELF_TEST_TARGETS:
            extra_markers = (
                ()
                if target.relpath.endswith("check-phase3-catalog-selftest.py")
                else target.extra_markers
            )
            write_script(
                catalog_selftest_count_root / target.relpath,
                target.marker or "PASS",
                extra_markers=extra_markers,
            )
        issues = run_targets(catalog_selftest_count_root)
        assert (
            "missing_aux_marker:scripts/zigux/check-phase3-catalog-selftest.py:"
            "PHASE3_CATALOG_SELF_TEST_CASE_COUNT=6"
            in issues
        )

        catalog_selftest_count_substring_root = Path(tmp_dir) / "catalog-selftest-count-substring"
        for target in SELF_TEST_TARGETS:
            path = catalog_selftest_count_substring_root / target.relpath
            if target.relpath.endswith("check-phase3-catalog-selftest.py"):
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(
                    "\n".join(
                        [
                            "#!/usr/bin/env python3",
                            "from __future__ import annotations",
                            "",
                            "import sys",
                            "",
                            'if "--self-test" in sys.argv:',
                            '    print("PHASE3_CATALOG_SELF_TEST=pass")',
                            '    print("note: PHASE3_CATALOG_SELF_TEST_CASE_COUNT=6 is mentioned here but is not exact")',
                            "    raise SystemExit(0)",
                            "",
                            'raise SystemExit("expected --self-test")',
                            "",
                        ]
                    ),
                    encoding="utf-8",
                    newline="\n",
                )
                continue
            write_script(path, target.marker or "PASS", extra_markers=target.extra_markers)
        issues = run_targets(catalog_selftest_count_substring_root)
        assert (
            "missing_aux_marker:scripts/zigux/check-phase3-catalog-selftest.py:"
            "PHASE3_CATALOG_SELF_TEST_CASE_COUNT=6"
            in issues
        )

        catalog_marker_root = Path(tmp_dir) / "catalog-marker"
        for target in SELF_TEST_TARGETS:
            marker = (
                "WRONG_MARKER=pass"
                if target.relpath.endswith("phase3_catalog.py")
                else (target.marker or "PASS")
            )
            write_script(
                catalog_marker_root / target.relpath,
                marker,
                extra_markers=target.extra_markers,
            )
        issues = run_targets(catalog_marker_root)
        assert (
            "missing_pass_marker:scripts/zigux/phase3_catalog.py:"
            "PHASE3_CATALOG_SELF_TEST=pass"
            in issues
        )

        catalog_count_root = Path(tmp_dir) / "catalog-count"
        for target in SELF_TEST_TARGETS:
            extra_markers = (
                ()
                if target.relpath.endswith("phase3_catalog.py")
                else target.extra_markers
            )
            write_script(
                catalog_count_root / target.relpath,
                target.marker or "PASS",
                extra_markers=extra_markers,
            )
        issues = run_targets(catalog_count_root)
        assert (
            "missing_aux_marker:scripts/zigux/phase3_catalog.py:"
            "PHASE3_CATALOG_SELF_TEST_CASE_COUNT=6"
            in issues
        )

        policy_unsafe_marker_root = Path(tmp_dir) / "policy-unsafe-marker"
        for target in SELF_TEST_TARGETS:
            marker = (
                "WRONG_MARKER=pass"
                if target.relpath.endswith("validate-phase3-policy-unsafe-survey.py")
                else (target.marker or "PASS")
            )
            write_script(
                policy_unsafe_marker_root / target.relpath,
                marker,
                extra_markers=target.extra_markers,
            )
        issues = run_targets(policy_unsafe_marker_root)
        assert (
            "missing_pass_marker:scripts/zigux/validate-phase3-policy-unsafe-survey.py:"
            "PHASE3_POLICY_UNSAFE_SURVEY_SELF_TEST=pass"
            in issues
        )

        low_level_wrapper_marker_root = Path(tmp_dir) / "low-level-wrapper-marker"
        for target in SELF_TEST_TARGETS:
            marker = (
                "WRONG_MARKER=pass"
                if target.relpath.endswith("validate-phase3-low-level-wrapper-survey.py")
                else (target.marker or "PASS")
            )
            write_script(
                low_level_wrapper_marker_root / target.relpath,
                marker,
                extra_markers=target.extra_markers,
            )
        issues = run_targets(low_level_wrapper_marker_root)
        assert (
            "missing_pass_marker:scripts/zigux/validate-phase3-low-level-wrapper-survey.py:"
            "PHASE3_LOW_LEVEL_WRAPPER_SURVEY_SELF_TEST=pass"
            in issues
        )

        export_uapi_marker_root = Path(tmp_dir) / "export-uapi-marker"
        for target in SELF_TEST_TARGETS:
            marker = (
                "WRONG_MARKER=pass"
                if target.relpath.endswith("validate-phase3-export-uapi-survey.py")
                else (target.marker or "PASS")
            )
            write_script(
                export_uapi_marker_root / target.relpath,
                marker,
                extra_markers=target.extra_markers,
            )
        issues = run_targets(export_uapi_marker_root)
        assert (
            "missing_pass_marker:scripts/zigux/validate-phase3-export-uapi-survey.py:"
            "PHASE3_EXPORT_UAPI_SURVEY_SELF_TEST=pass"
            in issues
        )

        export_uapi_duplicate_marker_root = Path(tmp_dir) / "export-uapi-duplicate-marker"
        for target in SELF_TEST_TARGETS:
            path = export_uapi_duplicate_marker_root / target.relpath
            if target.relpath.endswith("validate-phase3-export-uapi-survey.py"):
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(
                    "\n".join(
                        [
                            "#!/usr/bin/env python3",
                            "from __future__ import annotations",
                            "",
                            "import sys",
                            "",
                            'if "--self-test" in sys.argv:',
                            '    print("PHASE3_EXPORT_UAPI_SURVEY_SELF_TEST=pass")',
                            '    print("PHASE3_EXPORT_UAPI_SURVEY_SELF_TEST=pass")',
                            '    print("PHASE3_EXPORT_UAPI_SURVEY_SELF_TEST_CASE_COUNT=5")',
                            "    raise SystemExit(0)",
                            "",
                            'raise SystemExit("expected --self-test")',
                            "",
                        ]
                    ),
                    encoding="utf-8",
                    newline="\n",
                )
                continue
            write_script(path, target.marker or "PASS", extra_markers=target.extra_markers)
        issues = run_targets(export_uapi_duplicate_marker_root)
        assert (
            "duplicate_pass_marker:scripts/zigux/validate-phase3-export-uapi-survey.py:2:"
            "PHASE3_EXPORT_UAPI_SURVEY_SELF_TEST=pass"
            in issues
        )

        export_uapi_count_root = Path(tmp_dir) / "export-uapi-count"
        for target in SELF_TEST_TARGETS:
            extra_markers = (
                ()
                if target.relpath.endswith("validate-phase3-export-uapi-survey.py")
                else target.extra_markers
            )
            write_script(
                export_uapi_count_root / target.relpath,
                target.marker or "PASS",
                extra_markers=extra_markers,
            )
        issues = run_targets(export_uapi_count_root)
        assert (
            "missing_aux_marker:scripts/zigux/validate-phase3-export-uapi-survey.py:"
            "PHASE3_EXPORT_UAPI_SURVEY_SELF_TEST_CASE_COUNT=5"
            in issues
        )

        export_uapi_duplicate_count_root = Path(tmp_dir) / "export-uapi-duplicate-count"
        for target in SELF_TEST_TARGETS:
            path = export_uapi_duplicate_count_root / target.relpath
            if target.relpath.endswith("validate-phase3-export-uapi-survey.py"):
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(
                    "\n".join(
                        [
                            "#!/usr/bin/env python3",
                            "from __future__ import annotations",
                            "",
                            "import sys",
                            "",
                            'if "--self-test" in sys.argv:',
                            '    print("PHASE3_EXPORT_UAPI_SURVEY_SELF_TEST=pass")',
                            '    print("PHASE3_EXPORT_UAPI_SURVEY_SELF_TEST_CASE_COUNT=5")',
                            '    print("PHASE3_EXPORT_UAPI_SURVEY_SELF_TEST_CASE_COUNT=5")',
                            "    raise SystemExit(0)",
                            "",
                            'raise SystemExit("expected --self-test")',
                            "",
                        ]
                    ),
                    encoding="utf-8",
                    newline="\n",
                )
                continue
            write_script(path, target.marker or "PASS", extra_markers=target.extra_markers)
        issues = run_targets(export_uapi_duplicate_count_root)
        assert (
            "duplicate_aux_marker:scripts/zigux/validate-phase3-export-uapi-survey.py:2:"
            "PHASE3_EXPORT_UAPI_SURVEY_SELF_TEST_CASE_COUNT=5"
            in issues
        )

        runner_marker_root = Path(tmp_dir) / "runner-marker"
        for target in SELF_TEST_TARGETS:
            marker = (
                "WRONG_MARKER=pass"
                if target.relpath.endswith("run-phase3-checks.py")
                else (target.marker or "PASS")
            )
            write_script(
                runner_marker_root / target.relpath,
                marker,
                extra_markers=target.extra_markers,
            )
        issues = run_targets(runner_marker_root)
        assert (
            "missing_pass_marker:scripts/zigux/run-phase3-checks.py:PHASE3_RUNNER_SELF_TEST=pass"
            in issues
        )

        wrapper_marker_root = Path(tmp_dir) / "wrapper-marker"
        for target in SELF_TEST_TARGETS:
            marker = (
                "WRONG_MARKER=pass"
                if target.relpath.endswith("generate-phase3-check-wrappers.py")
                else (target.marker or "PASS")
            )
            write_script(
                wrapper_marker_root / target.relpath,
                marker,
                extra_markers=target.extra_markers,
            )
        issues = run_targets(wrapper_marker_root)
        assert (
            "missing_pass_marker:scripts/zigux/generate-phase3-check-wrappers.py:"
            "PHASE3_WRAPPER_SELF_TEST=pass"
            in issues
        )

        stderr_root = Path(tmp_dir) / "stderr"
        for target in SELF_TEST_TARGETS:
            if target.relpath.endswith("validate-phase3.py"):
                path = stderr_root / target.relpath
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(
                    "\n".join(
                        [
                            "#!/usr/bin/env python3",
                            "from __future__ import annotations",
                            "",
                            "import sys",
                            "",
                            'if "--self-test" in sys.argv:',
                            '    print("PHASE3_VALIDATE_SELF_TEST=pass")',
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
            else:
                write_script(
                    stderr_root / target.relpath,
                    target.marker or "PASS",
                    extra_markers=target.extra_markers,
                )
        issues = run_targets(stderr_root)
        assert "self_test_failed:scripts/zigux/validate-phase3.py:rc=3" in issues
        assert "self_test_stderr:scripts/zigux/validate-phase3.py:broken" in issues

    print("PHASE3_VALIDATOR_SELF_TEST=pass")
    print(f"PHASE3_VALIDATOR_SELF_TEST_CASE_COUNT={PHASE3_VALIDATOR_SELF_TEST_CASE_COUNT}")
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