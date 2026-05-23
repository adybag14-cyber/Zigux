#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SURVEY = "Documentation/zigux/phase2-genksyms-dual-implementation-survey.md"
WORKFLOW = ".github/workflows/zigux-bootstrap.yml"
MAKEFILE = "zigux/Makefile"

REQUIRED_PATHS = (
    SURVEY,
    WORKFLOW,
    MAKEFILE,
    "Documentation/zigux/phase2-closure.md",
    "scripts/zigux/README.md",
    "scripts/zigux/validate-phase2.py",
    "scripts/zigux/validate-phase2-closure.py",
    "scripts/zigux/genksyms.zig",
    "scripts/zigux/check-genksyms-bridge.py",
    "scripts/zigux/check-phase2-genksyms-selftest-alignment.py",
    "scripts/zigux/check-phase2-genksyms-survey-alignment.py",
    "scripts/zigux/genksyms_version_before_invalid_long_option_test.zig",
    "zigux/tests/README.md",
    "zigux/tests/fixtures/phase2_tool_manifest.json",
    "zigux/tests/fixtures/genksyms_bridge/cases.json",
    "zigux/tests/fixtures/genksyms_bridge/manifest.json",
    "zigux/tests/fixtures/genksyms_bridge/help_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/minimal_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/debug_reference_types_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/long_options_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/abbreviated_long_options_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/quiet_overrides_warning_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/explicit_option_terminator_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/positional_passthrough_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/lone_dash_passthrough_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/abbreviated_version_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/ambiguous_long_option_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/invalid_option_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/missing_long_dump_types_argument_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/missing_long_reference_argument_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/missing_reference_argument_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/too_many_reference_files_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/unsupported_long_option_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/unexpected_long_help_argument_expected.json",
)

REQUIRED_SURVEY_SNIPPETS = (
    "The Phase 2 roadmap still keeps `scripts/genksyms/genksyms.c` inside the bounded toolchain and Kbuild enablement tranche",
    "Current `master` directly serves `scripts/zigux/genksyms.zig`, so the core dual-implementation helper is still present on head.",
    "Current `master` directly serves the bounded checker, invocation-fixture packet, dedicated manifest, help fixture, and restored process-output packet again:",
    "`Documentation/zigux/phase2-closure.md`, `scripts/zigux/validate-phase2.py`, `scripts/zigux/validate-phase2-closure.py`, `scripts/zigux/README.md`, `zigux/tests/README.md`, `zigux/Makefile`, `.github/workflows/zigux-bootstrap.yml`, and `zigux/tests/fixtures/phase2_tool_manifest.json`",
    "The narrower repo-reality gap that once lived at the checker layer is now closed on current `master`:",
    "Relative to the roadmap and ledger, the older inventory-shaped governance gap is no longer truthful on current `master`;",
    "Leave this survey parked unless a future reread finds another genksyms-local wording, inventory, or replay drift.",
)


def read_text(root: Path, rel: str) -> str:
    path = root / rel
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def write_text(root: Path, rel: str, content: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def replace_once(text: str, old: str, new: str) -> str:
    if old not in text:
        raise AssertionError(f"marker not found: {old}")
    return text.replace(old, new, 1)


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []

    for rel in REQUIRED_PATHS:
        if not (root / rel).exists():
            issues.append(("MISSING_REQUIRED_PATH", rel))

    if issues:
        return issues

    survey_text = read_text(root, SURVEY)
    read_text(root, WORKFLOW)
    read_text(root, MAKEFILE)

    for snippet in REQUIRED_SURVEY_SNIPPETS:
        if snippet not in survey_text:
            issues.append(("MISSING_SURVEY_SNIPPET", snippet))

    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)

    print("PHASE2_GENKSYMS_SURVEY_ALIGNMENT=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def build_self_test_root(root: Path) -> None:
    survey_text = """# Phase 2 genksyms dual-implementation survey

Lane: `P2-L07`

## Roadmap and ledger anchor

- The Phase 2 roadmap still keeps `scripts/genksyms/genksyms.c` inside the bounded toolchain and Kbuild enablement tranche, with `scripts/zigux/genksyms.zig` as the Zigux destination.
- The bootstrap ledger still records a bounded genksyms wrapper lane around `scripts/zigux/genksyms.zig` together with a dedicated checker and fixture-backed expected-output packet, so this family remains real product infrastructure rather than wrapper churn.

## Current repo evidence

- Current `master` directly serves `scripts/zigux/genksyms.zig`, so the core dual-implementation helper is still present on head.
- Current `master` directly serves the bounded checker, invocation-fixture packet, dedicated manifest, help fixture, and restored process-output packet again: `scripts/zigux/check-genksyms-bridge.py`, `zigux/tests/fixtures/genksyms_bridge/cases.json`, `zigux/tests/fixtures/genksyms_bridge/manifest.json`, `zigux/tests/fixtures/genksyms_bridge/help_expected.json`, `zigux/tests/fixtures/genksyms_bridge/minimal_expected.json`, `zigux/tests/fixtures/genksyms_bridge/debug_reference_types_expected.json`, `zigux/tests/fixtures/genksyms_bridge/long_options_expected.json`, `zigux/tests/fixtures/genksyms_bridge/abbreviated_long_options_expected.json`, `zigux/tests/fixtures/genksyms_bridge/quiet_overrides_warning_expected.json`, `zigux/tests/fixtures/genksyms_bridge/explicit_option_terminator_expected.json`, `zigux/tests/fixtures/genksyms_bridge/positional_passthrough_expected.json`, `zigux/tests/fixtures/genksyms_bridge/lone_dash_passthrough_expected.json`, `zigux/tests/fixtures/genksyms_bridge/abbreviated_version_expected.json`, `zigux/tests/fixtures/genksyms_bridge/ambiguous_long_option_expected.json`, `zigux/tests/fixtures/genksyms_bridge/invalid_option_expected.json`, `zigux/tests/fixtures/genksyms_bridge/missing_long_dump_types_argument_expected.json`, `zigux/tests/fixtures/genksyms_bridge/missing_long_reference_argument_expected.json`, `zigux/tests/fixtures/genksyms_bridge/missing_reference_argument_expected.json`, `zigux/tests/fixtures/genksyms_bridge/too_many_reference_files_expected.json`, `zigux/tests/fixtures/genksyms_bridge/unsupported_long_option_expected.json`, and `zigux/tests/fixtures/genksyms_bridge/unexpected_long_help_argument_expected.json` are all readable on head.
- Current shared Phase 2 reminder surfaces also keep the genksyms packet explicit: `Documentation/zigux/phase2-closure.md`, `scripts/zigux/validate-phase2.py`, `scripts/zigux/validate-phase2-closure.py`, `scripts/zigux/README.md`, `zigux/tests/README.md`, `zigux/Makefile`, `.github/workflows/zigux-bootstrap.yml`, and `zigux/tests/fixtures/phase2_tool_manifest.json` all still name the checker, fixture roster, or `phase2-genksyms` replay route.
- The narrower repo-reality gap that once lived at the checker layer is now closed on current `master`: the dedicated checker directly validates the manifest-backed bridge packet, the restored process-output fixtures, the help fixture, and the standalone invalid-long-option version-side-effect proof, while `scripts/zigux/check-phase2-genksyms-selftest-alignment.py` keeps that checker-owned packet tied back to the workflow and Makefile hooks.

## Survey result

- Relative to the roadmap and ledger, the older inventory-shaped governance gap is no longer truthful on current `master`; the live work is a bounded wrapper-first dual-implementation packet whose expected-output governance is already checker-owned, so the remaining same-family posture is to keep this survey parked unless another directly coupled reminder surface drifts.

## Next bounded same-family step

1. Leave this survey parked unless a future reread finds another genksyms-local wording, inventory, or replay drift.
2. If the family reopens for governance rather than implementation, keep the next move to one directly coupled reminder-surface refresh in the survey note, closure note, tests README, or validator wording that mismatches the already checker-owned manifest and process-output packet.
"""
    write_text(root, SURVEY, survey_text)
    write_text(
        root,
        WORKFLOW,
        "\n".join(
            (
                "name: zigux-bootstrap",
                "run: python3 scripts/zigux/check-genksyms-bridge.py --self-test",
                "run: python3 scripts/zigux/check-genksyms-bridge.py",
                "run: zig test scripts/zigux/genksyms.zig",
            )
        )
        + "\n",
    )
    write_text(
        root,
        MAKEFILE,
        "\n".join(
            (
                ".PHONY: phase2-genksyms",
                "phase2-genksyms:",
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-genksyms-bridge.py --self-test",
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-genksyms-bridge.py",
                "\tcd $(ZIGUX_ROOT) && $(ZIG) test scripts/zigux/genksyms.zig",
            )
        )
        + "\n",
    )

    placeholder_paths = {
        "Documentation/zigux/phase2-closure.md",
        "scripts/zigux/README.md",
        "scripts/zigux/validate-phase2.py",
        "scripts/zigux/validate-phase2-closure.py",
        "scripts/zigux/genksyms.zig",
        "scripts/zigux/check-genksyms-bridge.py",
        "scripts/zigux/check-phase2-genksyms-selftest-alignment.py",
        "scripts/zigux/check-phase2-genksyms-survey-alignment.py",
        "scripts/zigux/genksyms_version_before_invalid_long_option_test.zig",
        "zigux/tests/README.md",
        "zigux/tests/fixtures/phase2_tool_manifest.json",
    }
    for rel in placeholder_paths:
        write_text(root, rel, "present\n")

    for rel in REQUIRED_PATHS:
        if rel in {
            SURVEY,
            WORKFLOW,
            MAKEFILE,
            *placeholder_paths,
        }:
            continue
        write_text(root, rel, "present\n")



def run_self_test() -> int:
    checks = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_genksyms_survey_") as tmp_dir:
        root = Path(tmp_dir)
        build_self_test_root(root)
        assert collect_issues(root) == []
        checks += 1

        for rel in REQUIRED_PATHS:
            build_self_test_root(root)
            (root / rel).unlink()
            issues = collect_issues(root)
            assert ("MISSING_REQUIRED_PATH", rel) in issues
            checks += 1

        for snippet in REQUIRED_SURVEY_SNIPPETS:
            build_self_test_root(root)
            survey_text = read_text(root, SURVEY)
            write_text(root, SURVEY, replace_once(survey_text, snippet, "snippet removed"))
            issues = collect_issues(root)
            assert ("MISSING_SURVEY_SNIPPET", snippet) in issues
            checks += 1

    print("PHASE2_GENKSYMS_SURVEY_ALIGNMENT_SELF_TEST=pass")
    print(f"PHASE2_GENKSYMS_SURVEY_ALIGNMENT_SELF_TEST_CASE_COUNT={checks}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Fail closed when the Phase 2 genksyms survey drifts from the live dual-implementation packet."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("PHASE2_GENKSYMS_SURVEY_ALIGNMENT=pass")
    print(f"PHASE2_GENKSYMS_SURVEY_ALIGNMENT_REQUIRED_PATH_COUNT={len(REQUIRED_PATHS)}")
    print(f"PHASE2_GENKSYMS_SURVEY_ALIGNMENT_SURVEY_SNIPPET_COUNT={len(REQUIRED_SURVEY_SNIPPETS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
