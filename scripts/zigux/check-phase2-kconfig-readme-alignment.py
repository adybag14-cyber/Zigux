#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
README = ROOT / "scripts" / "zigux" / "README.md"

PHASE2_FLOW_SENTENCE = (
    "- Phase 2 flow - the current scripts-root bridge packet stays reviewable through the live "
    "toolchain checker, installer helper, direct cross-route packet, `conf_bridge` and `confdata_bridge` "
    "helper surfaces, the restored closure-side validator packet, the manifest-backed kconfig fixture "
    "roster, the shipped make-wrapper packet, and the surviving Phase 2 alignment guards instead of "
    "replaying older missing-route assumptions inside that now-rematerialized toolchain packet"
)

CONF_BRIDGE_SENTENCE = (
    "- `scripts/zigux/kconfig/conf_bridge.zig` keeps the shipped sixteen-mode request-plan bridge "
    "explicit from the scripts root, including the `helpnewconfig` `silent` option handling and the "
    "same `randconfig`, `defconfig`, `savedefconfig`, and `syncconfig` argument surfaces that the "
    "Phase 2 wrapper-first roadmap tranche expects"
)

CONFDATA_PACKET_SENTENCE = (
    "- `scripts/zigux/kconfig/confdata_bridge.zig`, `zigux/tests/fixtures/kconfig_bridge/conf_manifest.json`, "
    "`zigux/tests/fixtures/kconfig_bridge/confdata_manifest.json`, and "
    "`zigux/tests/fixtures/kconfig_bridge/cases.json` keep the current conf-side and confdata-side bridge "
    "evidence packet explicit from the scripts root without pretending the broader closure packet is still "
    "directly readable"
)

GUARDS_SENTENCE = (
    "- `scripts/zigux/check-zig-toolchain.py`, `scripts/zigux/check-phase2-kbuild-routes.py`, "
    "`scripts/zigux/check-genksyms-bridge.py`, `scripts/zigux/check-phase2-docs-shared-reminder.py`, "
    "`scripts/zigux/check-phase2-kconfig-selftest-alignment.py`, "
    "`scripts/zigux/check-phase2-tests-readme-alignment.py`, `scripts/zigux/check-phase2-cross.py`, "
    "`scripts/zigux/check-phase2-cross-selftest-alignment.py`, "
    "`scripts/zigux/check-phase2-toolchain-pinning.py`, "
    "`scripts/zigux/check-phase2-toolchain-pin-scope.py`, `scripts/zigux/check-phase2-tool-manifest.py`, "
    "`scripts/zigux/check-phase2-artifact-tools-manifest.py`, `scripts/zigux/check-phase2-fixdep-gate.py`, "
    "`scripts/zigux/check-fixdep-diff.py`, and `scripts/zigux/check-phase2-required-make-routes.py` "
    "remain the shipped Phase 2 toolchain, reminder, alignment, artifact-support, fixdep, genksyms-bridge, "
    "and required-make-route guards that survive on current `master`"
)

TOOLCHAIN_REPLAY_SENTENCE = (
    "- `.github/workflows/zigux-bootstrap.yml`, `python3 scripts/zigux/check-zig-toolchain.py --self-test`, "
    "`python3 scripts/zigux/check-zig-toolchain.py --policy-only`, and "
    "`python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing` keep the shipped pinned "
    "Zig toolchain guard explicit in the live bootstrap action path before the surviving Phase 2 bridge "
    "and pinning checks"
)

CLOSURE_PACKET_SENTENCE = (
    "- `Documentation/zigux/phase2-closure.md`, `scripts/zigux/validate-phase2.py`, "
    "`scripts/zigux/validate-phase2-closure.py`, `zigux/Makefile`, `make -C zigux phase2-toolchain`, "
    "`make -C zigux phase2-tools`, `make -C zigux phase2-kconfig`, `make -C zigux phase2-cross`, "
    "`make -C zigux phase2-genksyms`, `make -C zigux phase2-fixdep`, `make -C zigux phase2-validate`, "
    "`make -C zigux phase2`, `zigux/tests/fixtures/phase2_tool_manifest.json`, and "
    "`zigux/tests/fixtures/phase2_artifact_tools_manifest.json` keep the shipped closure-side reminder, "
    "closure-validator, validator entrypoint, make-wrapper, and artifact-support packet explicit from the "
    "scripts root beside the surviving checker set"
)

DIRECT_CROSS_SENTENCE = (
    "- `scripts/zigux/install-zig.py`, `python3 scripts/zigux/install-zig.py --self-test`, "
    "`python3 scripts/zigux/check-phase2-cross.py --self-test`, `python3 scripts/zigux/check-phase2-cross.py`, "
    "and `zigux/tests/fixtures/phase2_cross_targets.json` are directly readable on current `master`, so keep "
    "those installer and direct cross-route surfaces explicit beside the shipped toolchain and kbuild reminder "
    "packet instead of leaving them in repo-reality-gap wording"
)

FOLLOWUP_SENTENCE = (
    "- if future work widens the installer or direct cross-route packet, update this reminder packet only "
    "after rereading those direct current-`master` surfaces together with the live toolchain policy, "
    "manifest-backed kconfig fixture roster, the fixture-backed Phase 2 tool packet, and shipped make-wrapper "
    "packet so the scripts-root summary stays aligned with the now-returned Phase 2 evidence"
)

LEGACY_FLOW_SENTENCE = (
    "- Phase 2 flow - the current scripts-root bridge packet stays reviewable through the live `conf_bridge` "
    "and `confdata_bridge` helper surfaces, the manifest-backed kconfig fixture roster, and the surviving "
    "Phase 2 alignment guards instead of rebuilding the older closure-side validator stack from paths that "
    "current `master` no longer serves"
)

LEGACY_GUARDS_SENTENCE = (
    "- `scripts/zigux/check-phase2-kbuild-routes.py`, `scripts/zigux/check-phase2-kconfig-selftest-alignment.py`, "
    "`scripts/zigux/check-phase2-tests-readme-alignment.py`, "
    "`scripts/zigux/check-phase2-cross-selftest-alignment.py`, and "
    "`scripts/zigux/check-phase2-toolchain-pinning.py` remain the shipped Phase 2 reminder and alignment guards "
    "that survive on current `master`"
)

LEGACY_MISSING_SENTENCE = (
    "- repeated authenticated reads on current `master` still return missing for "
    "`Documentation/zigux/phase2-closure.md`, `scripts/zigux/validate-phase2.py`, "
    "`scripts/zigux/validate-phase2-closure.py`, `zigux/Makefile`, "
    "`scripts/zigux/check-zig-toolchain.py`, `python3 scripts/zigux/install-zig.py --self-test`, "
    "`python3 scripts/zigux/check-zig-toolchain.py --self-test`, `python3 scripts/zigux/check-phase2-cross.py --self-test`, "
    "`python3 scripts/zigux/check-phase2-cross.py`, `make -C zigux phase2-validate`, and `make -C zigux phase2`, "
    "so treat those closure-side, validator-first, cross-matrix, toolchain-replay, and make-route names as "
    "historical packet members that need fresh re-materialization before they are reused here as direct current-`master` "
    "scripts-root evidence"
)

LEGACY_FOLLOWUP_SENTENCE = (
    "- if future work rematerializes the missing `phase2-closure`, validator-first routes, or make wrappers, "
    "update this reminder packet only after the direct paths return on current `master`, and keep any conf-side "
    "follow-up tied to the live `16-case` manifest and fixture roster rather than the older eight-case closure story"
)

REQUIRED_SNIPPETS = (
    PHASE2_FLOW_SENTENCE,
    CONF_BRIDGE_SENTENCE,
    CONFDATA_PACKET_SENTENCE,
    GUARDS_SENTENCE,
    TOOLCHAIN_REPLAY_SENTENCE,
    CLOSURE_PACKET_SENTENCE,
    DIRECT_CROSS_SENTENCE,
    FOLLOWUP_SENTENCE,
)

FORBIDDEN_SNIPPETS = (
    LEGACY_FLOW_SENTENCE,
    LEGACY_GUARDS_SENTENCE,
    LEGACY_MISSING_SENTENCE,
    LEGACY_FOLLOWUP_SENTENCE,
    "`scripts/zigux/check-phase2-kconfig-readme-alignment.py`",
)


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def collect_issues(readme_text: str) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    for snippet in REQUIRED_SNIPPETS:
        count = readme_text.count(snippet)
        if count != 1:
            issues.append(("REQUIRED_SNIPPET_COUNT_MISMATCH", f"{snippet}:actual={count}:expected=1"))
    for snippet in FORBIDDEN_SNIPPETS:
        count = readme_text.count(snippet)
        if count != 0:
            issues.append(("FORBIDDEN_SNIPPET_PRESENT", f"{snippet}:actual={count}:expected=0"))
    return issues


def emit_issues(issues: list[tuple[str, str]]) -> None:
    print("PHASE2_KCONFIG_README_ALIGNMENT=fail")
    for code, detail in issues:
        print(f"{code}={detail}")


def build_base_text() -> str:
    return "\n".join(
        (
            "# scripts/zigux",
            "",
            "This directory holds shipped Zigux validation helpers and compact reminder surfaces.",
            "",
            "## Phase 2",
            "",
            PHASE2_FLOW_SENTENCE,
            CONF_BRIDGE_SENTENCE,
            CONFDATA_PACKET_SENTENCE,
            GUARDS_SENTENCE,
            TOOLCHAIN_REPLAY_SENTENCE,
            CLOSURE_PACKET_SENTENCE,
            DIRECT_CROSS_SENTENCE,
            FOLLOWUP_SENTENCE,
            "",
        )
    )


def run_self_test() -> int:
    checks_run = 0
    base_text = build_base_text()

    assert collect_issues(base_text) == []
    checks_run += 1

    for snippet in REQUIRED_SNIPPETS:
        issues = collect_issues(base_text.replace(snippet, "", 1))
        assert ("REQUIRED_SNIPPET_COUNT_MISMATCH", f"{snippet}:actual=0:expected=1") in issues
        checks_run += 1

        issues = collect_issues(base_text.replace(snippet, snippet + "\n" + snippet, 1))
        assert ("REQUIRED_SNIPPET_COUNT_MISMATCH", f"{snippet}:actual=2:expected=1") in issues
        checks_run += 1

    for snippet in FORBIDDEN_SNIPPETS:
        issues = collect_issues(base_text + "\n" + snippet + "\n")
        assert ("FORBIDDEN_SNIPPET_PRESENT", f"{snippet}:actual=1:expected=0") in issues
        checks_run += 1

    with tempfile.TemporaryDirectory(prefix="zigux_phase2_kconfig_readme_alignment_") as tmp_dir:
        readme_path = Path(tmp_dir) / "README.md"
        readme_path.write_text(base_text, encoding="utf-8")
        assert collect_issues(read_text(readme_path)) == []
        checks_run += 1

    expected_case_count = 2 + (2 * len(REQUIRED_SNIPPETS)) + len(FORBIDDEN_SNIPPETS)
    if checks_run != expected_case_count:
        print("PHASE2_KCONFIG_README_ALIGNMENT_SELF_TEST=fail")
        print(f"PHASE2_KCONFIG_README_ALIGNMENT_SELF_TEST_CASE_COUNT_ACTUAL={checks_run}")
        print(f"PHASE2_KCONFIG_README_ALIGNMENT_SELF_TEST_CASE_COUNT_EXPECTED={expected_case_count}")
        return 1

    print("PHASE2_KCONFIG_README_ALIGNMENT_SELF_TEST=pass")
    print(f"PHASE2_KCONFIG_README_ALIGNMENT_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the Phase 2 scripts README stays aligned with the current shipped kconfig bridge packet."
    )
    parser.add_argument("--readme", type=Path, default=README, help="Override README path")
    parser.add_argument("--self-test", action="store_true", help="Run built-in checker coverage")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = collect_issues(read_text(args.readme))
    if issues:
        emit_issues(issues)
        return 1

    print("PHASE2_KCONFIG_README_ALIGNMENT=pass")
    print(f"README={args.readme}")
    print(f"PHASE2_KCONFIG_README_ALIGNMENT_REQUIRED_SNIPPET_COUNT={len(REQUIRED_SNIPPETS)}")
    print(f"PHASE2_KCONFIG_README_ALIGNMENT_FORBIDDEN_SNIPPET_COUNT={len(FORBIDDEN_SNIPPETS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
