#!/usr/bin/env python3
from __future__ import annotations

import argparse
import subprocess
import tempfile

from validate_phase3_core import ROOT, discover_phase3_slices, select_slices, validate_slices
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
)

BUILD_ROOT_DRIFT_SCRIPT = (
    "check-phase3-build-roots.py",
    "PHASE3_BUILD_ROOTS=fail",
    "build-roots-gate",
    "missing_root_source_file:../helpers/missing_plan.zig:zigux/helpers/missing_plan.zig",
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


def _run_survey_aggregation_self_test() -> int:
    cases = SURVEY_VALIDATION_SCRIPTS + (BUILD_ROOT_DRIFT_SCRIPT,)

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
        finally:
            globals()["ROOT"] = original_root

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
        result = _run_survey_aggregation_self_test()
        if result != 0:
            return result
        for script_name, _, _, _ in SURVEY_VALIDATION_SCRIPTS:
            result = _run_script_self_test(script_name)
            if result != 0:
                return result
        return _run_script_self_test(BUILD_ROOT_DRIFT_SCRIPT[0])

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
    for script_name, failure_banner, issue_prefix, _ in SURVEY_VALIDATION_SCRIPTS:
        issues.extend(
            _collect_script_validation_issues(
                script_name,
                failure_banner,
                issue_prefix,
            )
        )
    issues.extend(
        _collect_script_validation_issues(
            BUILD_ROOT_DRIFT_SCRIPT[0],
            BUILD_ROOT_DRIFT_SCRIPT[1],
            BUILD_ROOT_DRIFT_SCRIPT[2],
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
