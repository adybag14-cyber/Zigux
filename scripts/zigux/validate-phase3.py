#!/usr/bin/env python3
from __future__ import annotations

import argparse
import subprocess
import tempfile
from pathlib import Path

from validate_phase3_core import (
    ROOT,
    discover_phase3_slices,
    select_slices,
    validate_slices,
    validate_source_markers,
)
from validate_phase3_header_binding_markers import (
    run_self_test as run_header_binding_marker_self_test,
    validate_header_binding_markers,
)
from validate_phase3_selftest import run_self_test


SURVEY_VALIDATION_SCRIPTS = (
    (
        "validate-phase3-roadmap-gap-survey.py",
        "PHASE3_ROADMAP_GAP_SURVEY=fail",
        "roadmap-gap-survey-gate",
        "missing_roadmap_anchor",
    ),
    (
        "validate-phase3-rbtree-interop-survey.py",
        "PHASE3_RBTREE_INTEROP_SURVEY=fail",
        "rbtree-interop-survey-gate",
        "missing_rbtree_interop_anchor",
    ),
    (
        "check-phase3-rbtree-shared-lift-contract.py",
        "PHASE3_RBTREE_SHARED_LIFT_CONTRACT=fail",
        "rbtree-shared-lift-contract-gate",
        "missing_layout_contract_marker:PHASE3_RBTREE_SHARED_LAYOUT_CONTRACT=zigux_rbtree_root_view-reused-unchanged-in-shared-phase3-abi-packet",
    ),
    (
        "check-phase3-tests-root-companion.py",
        "PHASE3_TESTS_ROOT_COMPANION=fail",
        "tests-root-companion-gate",
        'manifest:"scripts/zigux/check-phase3-tests-root-companion.py"',
    ),
    (
        "validate-phase3-export-uapi-survey.py",
        "PHASE3_EXPORT_UAPI_SURVEY=fail",
        "export-uapi-survey-gate",
        "missing_export_uapi_anchor",
    ),
    (
        "validate-phase3-low-level-wrapper-survey.py",
        "PHASE3_LOW_LEVEL_WRAPPER_SURVEY=fail",
        "low-level-wrapper-survey-gate",
        "missing_low_level_anchor",
    ),
    (
        "validate-phase3-policy-unsafe-survey.py",
        "PHASE3_POLICY_UNSAFE_SURVEY=fail",
        "policy-unsafe-survey-gate",
        "missing_policy_unsafe_anchor",
    ),
    (
        "check-phase3-policy-unsafe-mmio-consumer.py",
        "PHASE3_POLICY_UNSAFE_MMIO_CONSUMER=fail",
        "policy-unsafe-mmio-consumer-gate",
        "missing_mmio_policy_consumer_anchor",
    ),
    (
        "check-phase3-abi-layout-packet.py",
        "PHASE3_ABI_LAYOUT_PACKET=fail",
        "abi-layout-packet-gate",
        "missing_expected_struct:zigux_cpumask_view",
    ),
    (
        "check-phase3-abi-binding-constants.py",
        "PHASE3_ABI_BINDING_CONSTANTS=fail",
        "abi-binding-constants-gate",
        "binding_missing_enum_member:Facility.kernel",
    ),
    (
        "check-phase3-tooling-packet.py",
        "PHASE3_TOOLING_PACKET=fail",
        "tooling-packet-gate",
        "missing_tooling_file:scripts/zigux/check-phase3-build-roots.py",
    ),
    (
        "check-phase3-readme-tooling-inventory.py",
        "PHASE3_README_TOOLING_INVENTORY=fail",
        "readme-tooling-inventory-gate",
        "missing_readme_entry:check-phase3-tooling-packet.py",
    ),
    (
        "check-phase3-validation-flow.py",
        "PHASE3_VALIDATION_FLOW=fail",
        "validation-flow-gate",
        "missing_makefile_snippet:\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase3-validation-flow.py",
    ),
)

BUILD_ROOT_DRIFT_SCRIPT = (
    "check-phase3-build-roots.py",
    "PHASE3_BUILD_ROOTS=fail",
    "build-roots-gate",
    "missing_root_source_file:../helpers/missing_plan.zig:zigux/helpers/missing_plan.zig",
)

CANONICAL_SURVEY_MANIFEST_SCRIPT = (
    "check-phase3-canonical-survey-manifest.py",
    "PHASE3_CANONICAL_SURVEY_MANIFEST=fail",
    "canonical-survey-manifest-gate",
    "missing_manifest_survey_script:scripts/zigux/validate-phase3-roadmap-gap-survey.py",
)

POLICY_UNSAFE_BUILD_WIRING_MARKERS = (
    'root_module.addImport("abi_bindings", abi_bindings_module);',
    'root_module.addImport("interop_policy", interop_policy_module);',
    'root_module.addImport("mmio", mmio_module);',
)

LOW_LEVEL_WRAPPER_BARRIER_ACQUIRE_RELEASE_MARKERS = {
    "Documentation/zigux/phase3-abi-slice.md": (
        "PHASE3_BARRIER_SCOPE=acquire-release-acquire-release-combined-full",
    ),
    "zigux/helpers/barrier.zig": (
        "pub fn acquireRelease() void {",
    ),
    "zigux/tests/phase3_low_level_wrappers.zig": (
        "barrier.acquireRelease();",
    ),
}

ABI_EXACT_ONCE_MAKEFILE_SNIPPETS = (
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase3-abi.py\n",
    "\tcd $(ZIGUX_ROOT) && $(ZIG) build phase3-dump --build-file zigux/tests/build.zig\n",
    "\tcd $(ZIGUX_ROOT) && $(ZIG) build phase3-export-uapi-test --build-file zigux/tests/phase3_export_uapi_build.zig\n",
    "\tcd $(ZIGUX_ROOT) && $(ZIG) build phase3-export-uapi-layout-test --build-file zigux/tests/phase3_export_uapi_layout_build.zig\n",
    "\tcd $(ZIGUX_ROOT) && $(ZIG) build phase3-low-level-wrappers-test --build-file zigux/tests/phase3_low_level_wrappers_build.zig\n",
    "\tcd $(ZIGUX_ROOT) && $(ZIG) build phase3-policy-unsafe-test --build-file zigux/tests/phase3_policy_unsafe_build.zig\n",
    "\tcd $(ZIGUX_ROOT) && $(ZIG) build phase3-test --build-file zigux/tests/build.zig\n",
)


def _run_script_self_test(script_name: str) -> int:
    script_path = ROOT / "scripts" / "zigux" / script_name
    result = subprocess.run(
        ["python3", str(script_path), "--self-test"],
        cwd=ROOT,
        text=True,
        check=False,
    )
    return result.returncode


def _collect_script_validation_issues(
    script_name: str,
    failure_banner: str,
    issue_prefix: str,
) -> list[str]:
    script_path = ROOT / "scripts" / "zigux" / script_name
    result = subprocess.run(
        ["python3", str(script_path)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode == 0:
        return []

    issues: list[str] = []
    for line in result.stdout.splitlines():
        stripped = line.strip()
        if not stripped or stripped == failure_banner:
            continue
        issues.append(f"{issue_prefix}: {stripped}")
    stderr = result.stderr.strip()
    if stderr:
        issues.append(f"{issue_prefix}: stderr: {stderr.splitlines()[-1]}")
    if not issues:
        issues.append(f"{issue_prefix}: {script_name} exited with status {result.returncode}")
    return issues


def _collect_phase3_abi_makefile_exactness_issues(root: Path) -> list[str]:
    makefile_path = root / "zigux" / "Makefile"
    try:
        makefile = makefile_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return ["abi-makefile-gate: missing_file:zigux/Makefile"]

    issues: list[str] = []
    for snippet in ABI_EXACT_ONCE_MAKEFILE_SNIPPETS:
        actual_count = makefile.count(snippet)
        if actual_count != 1:
            issues.append(
                "abi-makefile-gate: unexpected_makefile_snippet_count:"
                f"{actual_count}:{snippet.rstrip()}"
            )
    return issues


def _run_survey_aggregation_self_test() -> int:
    cases = SURVEY_VALIDATION_SCRIPTS + (
        BUILD_ROOT_DRIFT_SCRIPT,
        CANONICAL_SURVEY_MANIFEST_SCRIPT,
    )

    with tempfile.TemporaryDirectory(prefix="zigux_phase3_survey_aggregation_") as tmp_dir:
        root = type(ROOT)(tmp_dir)
        scripts_dir = root / "scripts" / "zigux"
        scripts_dir.mkdir(parents=True, exist_ok=True)

        for script_name, failure_banner, _, issue_line in cases:
            script_path = scripts_dir / script_name
            script_path.write_text(
                "\n".join(
                    (
                        "#!/usr/bin/env python3",
                        f"print({failure_banner!r})",
                        f"print({issue_line!r})",
                        "raise SystemExit(1)",
                    )
                )
                + "\n",
                encoding="utf-8",
            )

        original_root = globals()["ROOT"]
        globals()["ROOT"] = root
        try:
            aggregated: list[str] = []
            for script_name, failure_banner, issue_prefix, issue_line in cases:
                issues = _collect_script_validation_issues(script_name, failure_banner, issue_prefix)
                assert issues == [f"{issue_prefix}: {issue_line}"]
                aggregated.extend(issues)
            assert len(aggregated) == len(cases)

            stderr_only_script = "stderr-only-survey.py"
            (scripts_dir / stderr_only_script).write_text(
                "\n".join(
                    (
                        "#!/usr/bin/env python3",
                        "import sys",
                        "print('synthetic stderr drift', file=sys.stderr)",
                        "raise SystemExit(1)",
                    )
                )
                + "\n",
                encoding="utf-8",
            )
            issues = _collect_script_validation_issues(
                stderr_only_script,
                "PHASE3_STDERR_ONLY=fail",
                "stderr-only-gate",
            )
            assert issues == ["stderr-only-gate: stderr: synthetic stderr drift"]

            silent_script = "silent-nonzero-survey.py"
            (scripts_dir / silent_script).write_text(
                "\n".join(
                    (
                        "#!/usr/bin/env python3",
                        "raise SystemExit(7)",
                    )
                )
                + "\n",
                encoding="utf-8",
            )
            issues = _collect_script_validation_issues(
                silent_script,
                "PHASE3_SILENT_NONZERO=fail",
                "silent-nonzero-gate",
            )
            assert issues == [f"silent-nonzero-gate: {silent_script} exited with status 7"]
        finally:
            globals()["ROOT"] = original_root

    return 0


def _run_policy_unsafe_build_wiring_self_test() -> int:
    rel = "zigux/tests/phase3_policy_unsafe_build.zig"
    with tempfile.TemporaryDirectory(prefix="zigux_phase3_policy_unsafe_build_markers_") as tmp_dir:
        root = type(ROOT)(tmp_dir)
        build_path = root / rel
        build_path.parent.mkdir(parents=True, exist_ok=True)

        build_path.write_text(
            "\n".join(
                (
                    'root_module.addImport("panic_policy", panic_policy_module);',
                    'root_module.addImport("allocator_policy", allocator_policy_module);',
                    'root_module.addImport("layout_assert", layout_assert_module);',
                    'root_module.addImport("narrow_unsafe", narrow_unsafe_module);',
                    "",
                )
            ),
            encoding="utf-8",
            newline="\n",
        )
        issues = validate_source_markers(
            root,
            {rel: POLICY_UNSAFE_BUILD_WIRING_MARKERS},
        )
        assert issues == [
            'source-marker: zigux/tests/phase3_policy_unsafe_build.zig missing root_module.addImport("abi_bindings", abi_bindings_module);',
            'source-marker: zigux/tests/phase3_policy_unsafe_build.zig missing root_module.addImport("interop_policy", interop_policy_module);',
            'source-marker: zigux/tests/phase3_policy_unsafe_build.zig missing root_module.addImport("mmio", mmio_module);',
        ]

        build_path.write_text(
            "\n".join(
                (
                    'root_module.addImport("abi_bindings", abi_bindings_module);',
                    'root_module.addImport("panic_policy", panic_policy_module);',
                    'root_module.addImport("allocator_policy", allocator_policy_module);',
                    'root_module.addImport("interop_policy", interop_policy_module);',
                    'root_module.addImport("layout_assert", layout_assert_module);',
                    'root_module.addImport("mmio", mmio_module);',
                    'root_module.addImport("narrow_unsafe", narrow_unsafe_module);',
                    "",
                )
            ),
            encoding="utf-8",
            newline="\n",
        )
        assert validate_source_markers(
            root,
            {rel: POLICY_UNSAFE_BUILD_WIRING_MARKERS},
        ) == []

    return 0


def _run_low_level_wrapper_barrier_marker_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase3_low_level_barrier_markers_") as tmp_dir:
        root = type(ROOT)(tmp_dir)
        doc_path = root / "Documentation" / "zigux" / "phase3-abi-slice.md"
        barrier_path = root / "zigux" / "helpers" / "barrier.zig"
        wrappers_path = root / "zigux" / "tests" / "phase3_low_level_wrappers.zig"
        doc_path.parent.mkdir(parents=True, exist_ok=True)
        barrier_path.parent.mkdir(parents=True, exist_ok=True)
        wrappers_path.parent.mkdir(parents=True, exist_ok=True)

        doc_path.write_text(
            "PHASE3_BARRIER_SCOPE=acquire-release-full\n",
            encoding="utf-8",
            newline="\n",
        )
        barrier_path.write_text(
            "pub fn acquire() void {}\npub fn release() void {}\npub fn full() void {}\n",
            encoding="utf-8",
            newline="\n",
        )
        wrappers_path.write_text(
            "barrier.acquire();\nbarrier.release();\nbarrier.full();\n",
            encoding="utf-8",
            newline="\n",
        )
        issues = validate_source_markers(root, LOW_LEVEL_WRAPPER_BARRIER_ACQUIRE_RELEASE_MARKERS)
        assert issues == [
            "source-marker: Documentation/zigux/phase3-abi-slice.md missing PHASE3_BARRIER_SCOPE=acquire-release-acquire-release-combined-full",
            "source-marker: zigux/helpers/barrier.zig missing pub fn acquireRelease() void {",
            "source-marker: zigux/tests/phase3_low_level_wrappers.zig missing barrier.acquireRelease();",
        ]

        doc_path.write_text(
            "PHASE3_BARRIER_SCOPE=acquire-release-acquire-release-combined-full\n",
            encoding="utf-8",
            newline="\n",
        )
        barrier_path.write_text(
            "pub fn acquire() void {}\npub fn release() void {}\npub fn acquireRelease() void {}\npub fn full() void {}\n",
            encoding="utf-8",
            newline="\n",
        )
        wrappers_path.write_text(
            "barrier.acquire();\nbarrier.release();\nbarrier.acquireRelease();\nbarrier.full();\n",
            encoding="utf-8",
            newline="\n",
        )
        assert validate_source_markers(root, LOW_LEVEL_WRAPPER_BARRIER_ACQUIRE_RELEASE_MARKERS) == []

    return 0


def _run_phase3_abi_makefile_exactness_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase3_abi_makefile_exactness_") as tmp_dir:
        root = type(ROOT)(tmp_dir)
        makefile_path = root / "zigux" / "Makefile"
        makefile_path.parent.mkdir(parents=True, exist_ok=True)

        makefile_path.write_text(
            "phase3-abi:\n" + "".join(ABI_EXACT_ONCE_MAKEFILE_SNIPPETS),
            encoding="utf-8",
            newline="\n",
        )
        assert _collect_phase3_abi_makefile_exactness_issues(root) == []

        makefile_path.write_text(
            "phase3-abi:\n"
            + "".join(ABI_EXACT_ONCE_MAKEFILE_SNIPPETS)
            + ABI_EXACT_ONCE_MAKEFILE_SNIPPETS[0],
            encoding="utf-8",
            newline="\n",
        )
        assert _collect_phase3_abi_makefile_exactness_issues(root) == [
            "abi-makefile-gate: unexpected_makefile_snippet_count:2:\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase3-abi.py"
        ]

        makefile_path.write_text(
            "phase3-abi:\n" + "".join(ABI_EXACT_ONCE_MAKEFILE_SNIPPETS[:-1]),
            encoding="utf-8",
            newline="\n",
        )
        assert _collect_phase3_abi_makefile_exactness_issues(root) == [
            "abi-makefile-gate: unexpected_makefile_snippet_count:0:\tcd $(ZIGUX_ROOT) && $(ZIG) build phase3-test --build-file zigux/tests/build.zig"
        ]

    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the bounded Phase 3 slice catalog and metadata.")
    parser.add_argument("--slug", action="append", default=[], help="Only validate the named Phase 3 slug. Repeat to validate more than one.")
    parser.add_argument("--check-artifact-diff", action="store_true", help="Also validate the generated Current Phase 3 use section.")
    parser.add_argument("--check-build-smoke", action="store_true", help="Also run focused Zig build smoke checks for the selected Phase 3 slices.")
    parser.add_argument("--check-build-root-drift", action="store_true", help="Deprecated compatibility flag; build-root drift checks now run by default.")
    parser.add_argument("--check-slug-sanity", action="store_true", help="Also audit discovered Phase 3 slugs for naming drift.")
    parser.add_argument("--skip-obsolete-wrapper-check", action="store_true", help="Skip the stale wrapper-file scan.")
    parser.add_argument("--zig", help="Explicit zig executable path for --check-build-smoke runs.")
    parser.add_argument("--self-test", action="store_true", help="Run isolated validator checks.")
    args = parser.parse_args()

    if args.self_test:
        result = run_self_test()
        if result != 0:
            return result
        result = run_header_binding_marker_self_test()
        if result != 0:
            return result
        result = _run_policy_unsafe_build_wiring_self_test()
        if result != 0:
            return result
        result = _run_low_level_wrapper_barrier_marker_self_test()
        if result != 0:
            return result
        result = _run_phase3_abi_makefile_exactness_self_test()
        if result != 0:
            return result
        result = _run_survey_aggregation_self_test()
        if result != 0:
            return result
        for script_name, _, _, _ in SURVEY_VALIDATION_SCRIPTS:
            result = _run_script_self_test(script_name)
            if result != 0:
                return result
        for script_name, _, _, _ in (BUILD_ROOT_DRIFT_SCRIPT, CANONICAL_SURVEY_MANIFEST_SCRIPT):
            result = _run_script_self_test(script_name)
            if result != 0:
                return result
        return 0

    slices = select_slices(discover_phase3_slices(), args.slug)
    if not slices:
        raise SystemExit("no Phase 3 slugs discovered")

    issues = validate_header_binding_markers(ROOT)
    issues.extend(
        validate_slices(
            ROOT,
            slices,
            check_artifact_diff=args.check_artifact_diff,
            check_build_smoke=args.check_build_smoke,
            check_slug_sanity=args.check_slug_sanity,
            check_all_wrappers=not args.skip_obsolete_wrapper_check,
            zig_path=args.zig,
        )
    )
    if any(entry.slug == "abi" for entry in slices):
        issues.extend(
            validate_source_markers(
                ROOT,
                LOW_LEVEL_WRAPPER_BARRIER_ACQUIRE_RELEASE_MARKERS,
            )
        )
    policy_unsafe_build_path = ROOT / "zigux/tests/phase3_policy_unsafe_build.zig"
    if policy_unsafe_build_path.exists():
        issues.extend(
            validate_source_markers(
                ROOT,
                {
                    "zigux/tests/phase3_policy_unsafe_build.zig": POLICY_UNSAFE_BUILD_WIRING_MARKERS,
                },
            )
        )
    issues.extend(_collect_phase3_abi_makefile_exactness_issues(ROOT))
    for script_name, failure_banner, issue_prefix, _ in SURVEY_VALIDATION_SCRIPTS:
        issues.extend(
            _collect_script_validation_issues(
                script_name,
                failure_banner,
                issue_prefix,
            )
        )
    for script_name, failure_banner, issue_prefix, _ in (
        BUILD_ROOT_DRIFT_SCRIPT,
        CANONICAL_SURVEY_MANIFEST_SCRIPT,
    ):
        issues.extend(
            _collect_script_validation_issues(
                script_name,
                failure_banner,
                issue_prefix,
            )
        )
    if issues:
        print("PHASE3_VALIDATION=fail")
        for issue in issues:
            print(issue)
        return 1

    print("PHASE3_VALIDATION=pass")
    print("PHASE3_VALIDATED_SLUGS=" + ",".join(entry.slug for entry in slices))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
