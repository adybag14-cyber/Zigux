#!/usr/bin/env python3
"""Check that the scripts-root Phase 2 summary stays aligned with the shared closure packet."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent

SCRIPTS_README_REL = Path("scripts/zigux/README.md")
CLOSURE_NOTE_REL = Path("Documentation/zigux/phase2-closure.md")
TESTS_README_REL = Path("zigux/tests/README.md")

REQUIRED_FILES = (
    Path(".github/workflows/zigux-bootstrap.yml"),
    Path("Documentation/zigux/README.md"),
    Path("Documentation/zigux/review-checklist.md"),
    CLOSURE_NOTE_REL,
    Path("Documentation/zigux/phase2-genksyms-dual-implementation-survey.md"),
    Path("Documentation/zigux/phase2-toolchain-bootstrap-notes.md"),
    SCRIPTS_README_REL,
    Path("scripts/zigux/install-zig.py"),
    Path("scripts/zigux/check-zig-toolchain.py"),
    Path("scripts/zigux/check-lane05-local-first-archive-workflow.py"),
    Path("scripts/zigux/check-lane05-local-archive-readme.py"),
    Path("scripts/zigux/check-phase2-kbuild-routes.py"),
    Path("scripts/zigux/check-kconfig-bridge.py"),
    Path("scripts/zigux/check-phase2-kconfig-selftest-alignment.py"),
    Path("scripts/zigux/check-phase2-tests-readme-alignment.py"),
    Path("scripts/zigux/check-phase2-cross.py"),
    Path("scripts/zigux/check-phase2-cross-selftest-alignment.py"),
    Path("scripts/zigux/check-phase2-docs-shared-reminder.py"),
    Path("scripts/zigux/check-phase2-toolchain-pinning.py"),
    Path("scripts/zigux/check-phase2-toolchain-pin-scope.py"),
    Path("scripts/zigux/check-phase2-tool-manifest.py"),
    Path("scripts/zigux/check-phase2-artifact-tools-manifest.py"),
    Path("scripts/zigux/check-phase2-required-make-routes.py"),
    Path("scripts/zigux/check-genksyms-bridge.py"),
    Path("scripts/zigux/check-phase2-genksyms-selftest-alignment.py"),
    Path("scripts/zigux/check-phase2-fixdep-gate.py"),
    Path("scripts/zigux/check-fixdep-diff.py"),
    Path("scripts/zigux/validate-phase2.py"),
    Path("scripts/zigux/validate-phase2-closure.py"),
    Path("scripts/zigux/zig-toolchain-policy.json"),
    Path("scripts/zigux/kconfig/conf_bridge.zig"),
    Path("scripts/zigux/kconfig/confdata_bridge.zig"),
    Path("scripts/zigux/genksyms.zig"),
    Path("scripts/zigux/genksyms_version_before_invalid_long_option_test.zig"),
    Path("scripts/zigux/fixdep.zig"),
    Path("third_party/README.md"),
    Path("third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz"),
    Path("zigux/Makefile"),
    TESTS_README_REL,
    Path("zigux/tests/fixtures/phase2_tool_manifest.json"),
    Path("zigux/tests/fixtures/phase2_artifact_tools_manifest.json"),
    Path("zigux/tests/fixtures/phase2_cross_targets.json"),
    Path("zigux/tests/fixtures/fixdep/cases.json"),
    Path("zigux/tests/fixtures/kconfig_bridge/conf_manifest.json"),
    Path("zigux/tests/fixtures/kconfig_bridge/confdata_manifest.json"),
    Path("zigux/tests/fixtures/kconfig_bridge/cases.json"),
    Path("zigux/tests/fixtures/genksyms_bridge/cases.json"),
    Path("zigux/tests/fixtures/genksyms_bridge/manifest.json"),
    Path("zigux/tests/fixtures/genksyms_bridge/help_expected.json"),
    Path("zigux/tests/fixtures/genksyms_bridge/minimal_expected.json"),
    Path("zigux/tests/fixtures/genksyms_bridge/debug_reference_types_expected.json"),
    Path("zigux/tests/fixtures/genksyms_bridge/long_options_expected.json"),
    Path("zigux/tests/fixtures/genksyms_bridge/abbreviated_long_options_expected.json"),
    Path("zigux/tests/fixtures/genksyms_bridge/quiet_overrides_warning_expected.json"),
    Path("zigux/tests/fixtures/genksyms_bridge/explicit_option_terminator_expected.json"),
    Path("zigux/tests/fixtures/genksyms_bridge/positional_passthrough_expected.json"),
    Path("zigux/tests/fixtures/genksyms_bridge/lone_dash_passthrough_expected.json"),
    Path("zigux/tests/fixtures/genksyms_bridge/abbreviated_version_expected.json"),
    Path("zigux/tests/fixtures/genksyms_bridge/ambiguous_long_option_expected.json"),
    Path("zigux/tests/fixtures/genksyms_bridge/invalid_option_expected.json"),
    Path("zigux/tests/fixtures/genksyms_bridge/missing_long_dump_types_argument_expected.json"),
    Path("zigux/tests/fixtures/genksyms_bridge/missing_long_reference_argument_expected.json"),
    Path("zigux/tests/fixtures/genksyms_bridge/missing_reference_argument_expected.json"),
    Path("zigux/tests/fixtures/genksyms_bridge/too_many_reference_files_expected.json"),
    Path("zigux/tests/fixtures/genksyms_bridge/unsupported_long_option_expected.json"),
    Path("zigux/tests/fixtures/genksyms_bridge/unexpected_long_help_argument_expected.json"),
)

SCRIPTS_README_MARKERS = (
    "## Phase 2",
    "the current scripts-root bridge packet stays reviewable through the live toolchain checker, installer helper, direct cross-route packet",
    "`scripts/zigux/kconfig/conf_bridge.zig` keeps the shipped sixteen-mode request-plan bridge explicit from the scripts root, including the `helpnewconfig` `silent` option handling and the same `randconfig`, `defconfig`, `savedefconfig`, and `syncconfig` argument surfaces that the Phase 2 wrapper-first roadmap tranche expects",
    "`scripts/zigux/kconfig/confdata_bridge.zig`, `zigux/tests/fixtures/kconfig_bridge/conf_manifest.json`, `zigux/tests/fixtures/kconfig_bridge/confdata_manifest.json`, and `zigux/tests/fixtures/kconfig_bridge/cases.json` keep the current conf-side and confdata-side bridge evidence packet explicit from the scripts root without pretending the broader closure packet is still directly readable",
    "`scripts/zigux/check-zig-toolchain.py`, `scripts/zigux/check-phase2-kbuild-routes.py`, `scripts/zigux/check-genksyms-bridge.py`, `scripts/zigux/check-phase2-docs-shared-reminder.py`, `scripts/zigux/check-phase2-kconfig-selftest-alignment.py`, `scripts/zigux/check-phase2-tests-readme-alignment.py`, `scripts/zigux/check-phase2-cross.py`, `scripts/zigux/check-phase2-cross-selftest-alignment.py`, `scripts/zigux/check-phase2-toolchain-pinning.py`, `scripts/zigux/check-phase2-toolchain-pin-scope.py`, `scripts/zigux/check-phase2-tool-manifest.py`, `scripts/zigux/check-phase2-artifact-tools-manifest.py`, `scripts/zigux/check-phase2-fixdep-gate.py`, `scripts/zigux/check-fixdep-diff.py`, and `scripts/zigux/check-phase2-required-make-routes.py` remain the shipped Phase 2 toolchain, reminder, alignment, artifact-support, fixdep, genksyms-bridge, and required-make-route guards that survive on current `master`",
    "`.github/workflows/zigux-bootstrap.yml`, `python3 scripts/zigux/check-zig-toolchain.py --self-test`, `python3 scripts/zigux/check-zig-toolchain.py --policy-only`, and `python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing` keep the shipped pinned Zig toolchain guard explicit",
    "`Documentation/zigux/phase2-closure.md`, `scripts/zigux/validate-phase2.py`, `scripts/zigux/validate-phase2-closure.py`, `zigux/Makefile`, `make -C zigux phase2-toolchain`, `make -C zigux phase2-tools`, `make -C zigux phase2-kconfig`, `make -C zigux phase2-cross`, `make -C zigux phase2-genksyms`, `make -C zigux phase2-fixdep`, `make -C zigux phase2-validate`, `make -C zigux phase2`, `zigux/tests/fixtures/phase2_tool_manifest.json`, and `zigux/tests/fixtures/phase2_artifact_tools_manifest.json` keep the shipped closure-side reminder, closure-validator, validator entrypoint, make-wrapper, and artifact-support packet explicit from the scripts root beside the surviving checker set",
    "`scripts/zigux/check-phase2-tool-manifest.py` and `zigux/tests/fixtures/phase2_tool_manifest.json` keep the fixture-backed current Phase 2 tool packet explicit from the scripts root beside the closure-side validator packet and the surviving alignment guards",
    "`scripts/zigux/check-phase2-artifact-tools-manifest.py`, `zigux/tests/fixtures/phase2_artifact_tools_manifest.json`, `scripts/zigux/check-phase2-fixdep-gate.py`, `scripts/zigux/check-fixdep-diff.py`, `scripts/zigux/fixdep.zig`, `zigux/tests/fixtures/fixdep/cases.json`, and `make -C zigux phase2-fixdep` keep the shipped artifact-support and fixdep packet explicit from the scripts root beside the closure-side validator packet and the surviving alignment guards",
    "`scripts/zigux/install-zig.py`, `python3 scripts/zigux/install-zig.py --self-test`, `python3 scripts/zigux/check-phase2-cross.py --self-test`, `python3 scripts/zigux/check-phase2-cross.py`, and `zigux/tests/fixtures/phase2_cross_targets.json` are directly readable on current `master`, so keep those installer and direct cross-route surfaces explicit beside the shipped toolchain and kbuild reminder packet instead of leaving them in repo-reality-gap wording",
    "keep those installer, tool-manifest, artifact-support, direct cross-route, genksyms bridge, and fixdep surfaces explicit beside the shipped toolchain and kbuild reminder packet",
)

SCRIPTS_README_EXACT_COUNT_MARKERS = (
    "keep those installer, tool-manifest, artifact-support, direct cross-route, genksyms bridge, and fixdep surfaces explicit beside the shipped toolchain and kbuild reminder packet",
)

CLOSURE_NOTE_MARKERS = (
    "`scripts/zigux/README.md`",
    "`scripts/zigux/check-lane05-local-first-archive-workflow.py`",
    "`scripts/zigux/check-lane05-local-archive-readme.py`",
    "`scripts/zigux/check-kconfig-bridge.py`",
    "`scripts/zigux/check-phase2-tests-readme-alignment.py`",
    "`scripts/zigux/check-phase2-toolchain-pinning.py`",
    "`scripts/zigux/check-phase2-toolchain-pin-scope.py`",
    "`scripts/zigux/validate-phase2.py`",
    "`scripts/zigux/validate-phase2-closure.py`",
    "`scripts/zigux/install-zig.py`",
    "`scripts/zigux/check-phase2-cross.py`",
    "`scripts/zigux/check-phase2-tool-manifest.py`",
    "`scripts/zigux/check-phase2-artifact-tools-manifest.py`",
    "`scripts/zigux/check-phase2-genksyms-selftest-alignment.py`",
    "`scripts/zigux/check-phase2-fixdep-gate.py`",
    "`scripts/zigux/check-fixdep-diff.py`",
    "`scripts/zigux/genksyms_version_before_invalid_long_option_test.zig`",
    "`scripts/zigux/fixdep.zig`",
    "`scripts/zigux/zig-toolchain-policy.json`",
    "`zigux/Makefile`",
    "`make -C zigux phase2-fixdep`",
    "`make -C zigux phase2`",
    "`zigux/tests/fixtures/kconfig_bridge/conf_manifest.json`",
    "`zigux/tests/fixtures/kconfig_bridge/confdata_manifest.json`",
    "`zigux/tests/fixtures/kconfig_bridge/cases.json`",
    "`zigux/tests/fixtures/genksyms_bridge/manifest.json`",
    "`zigux/tests/fixtures/genksyms_bridge/abbreviated_version_expected.json`",
)

TESTS_README_MARKERS = (
    "## Phase 2 review packet",
    "`scripts/zigux/README.md`",
    "`scripts/zigux/check-kconfig-bridge.py`",
    "`scripts/zigux/check-phase2-tests-readme-alignment.py`",
    "`scripts/zigux/check-phase2-cross.py`",
    "`scripts/zigux/check-phase2-cross-selftest-alignment.py`",
    "`scripts/zigux/check-phase2-toolchain-pinning.py`",
    "`scripts/zigux/check-phase2-toolchain-pin-scope.py`",
    "`scripts/zigux/check-phase2-tool-manifest.py`",
    "`scripts/zigux/check-phase2-artifact-tools-manifest.py`",
    "`scripts/zigux/check-phase2-fixdep-gate.py`",
    "`scripts/zigux/check-fixdep-diff.py`",
    "`scripts/zigux/install-zig.py`",
    "`zigux/Makefile`",
    "`zigux/tests/fixtures/kconfig_bridge/conf_manifest.json`",
    "`zigux/tests/fixtures/kconfig_bridge/confdata_manifest.json`",
    "`zigux/tests/fixtures/kconfig_bridge/cases.json`",
    "`scripts/zigux/check-lane05-local-first-archive-workflow.py`",
    "`scripts/zigux/check-lane05-local-archive-readme.py`",
    "`third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz`",
    "the `zigux/tests/fixtures/genksyms_bridge/` packet",
    "Keep the rematerialized make-wrapper packet explicit through `make -C zigux phase2-toolchain`, `make -C zigux phase2-tools`, `make -C zigux phase2-kconfig`, `make -C zigux phase2-cross`, `make -C zigux phase2-genksyms`, `make -C zigux phase2-fixdep`, `make -C zigux phase2-validate`, and `make -C zigux phase2`.",
    "keep the repo-local pinned archive packet explicit through `third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz`, `python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz --archive-target x86_64-linux`, and the local-first `third_party`, mirror, then direct-download bootstrap order reused by `.github/workflows/zigux-bootstrap.yml` and the two Lane 05 archive checkers",
    "keep the local-first archive workflow replay surface explicit through `python3 scripts/zigux/check-lane05-local-first-archive-workflow.py --self-test`, `python3 scripts/zigux/check-lane05-local-first-archive-workflow.py`, `python3 scripts/zigux/check-lane05-local-archive-readme.py --self-test`, and `python3 scripts/zigux/check-lane05-local-archive-readme.py`.",
    "current `master` also directly materializes `scripts/zigux/check-genksyms-bridge.py`, `scripts/zigux/genksyms.zig`, `make -C zigux phase2-genksyms`, and the `zigux/tests/fixtures/genksyms_bridge/` packet, so keep that returned checker, bridge helper, wrapper, and fixture roster explicit here instead of leaving it outside the tests-root reminder",
    "current `master` also directly materializes `scripts/zigux/check-phase2-fixdep-gate.py`, `scripts/zigux/check-fixdep-diff.py`, `scripts/zigux/fixdep.zig`, `make -C zigux phase2-fixdep`, and `zigux/tests/fixtures/fixdep/cases.json`, so keep that returned fixdep governance, parity, helper, wrapper, and fixture packet explicit here instead of leaving it outside the tests-root reminder",
)

TESTS_README_EXACT_COUNT_MARKERS = (
    "Keep the rematerialized make-wrapper packet explicit through `make -C zigux phase2-toolchain`, `make -C zigux phase2-tools`, `make -C zigux phase2-kconfig`, `make -C zigux phase2-cross`, `make -C zigux phase2-genksyms`, `make -C zigux phase2-fixdep`, `make -C zigux phase2-validate`, and `make -C zigux phase2`.",
    "keep the local-first archive workflow replay surface explicit through `python3 scripts/zigux/check-lane05-local-first-archive-workflow.py --self-test`, `python3 scripts/zigux/check-lane05-local-first-archive-workflow.py`, `python3 scripts/zigux/check-lane05-local-archive-readme.py --self-test`, and `python3 scripts/zigux/check-lane05-local-archive-readme.py`.",
    "current `master` also directly materializes `scripts/zigux/check-genksyms-bridge.py`, `scripts/zigux/genksyms.zig`, `make -C zigux phase2-genksyms`, and the `zigux/tests/fixtures/genksyms_bridge/` packet, so keep that returned checker, bridge helper, wrapper, and fixture roster explicit here instead of leaving it outside the tests-root reminder",
    "current `master` also directly materializes `scripts/zigux/check-phase2-fixdep-gate.py`, `scripts/zigux/check-fixdep-diff.py`, `scripts/zigux/fixdep.zig`, `make -C zigux phase2-fixdep`, and `zigux/tests/fixtures/fixdep/cases.json`, so keep that returned fixdep governance, parity, helper, wrapper, and fixture packet explicit here instead of leaving it outside the tests-root reminder",
)

FORBIDDEN_SCRIPTS_README_MARKERS = (
    "repeated authenticated reads on current `master` still return missing for `scripts/zigux/install-zig.py`",
    "`zigux/Makefile`, `make -C zigux phase2-toolchain`, `make -C zigux phase2-tools`, `make -C zigux phase2-kconfig`, `make -C zigux phase2-cross`, `make -C zigux phase2-genksyms`, `make -C zigux phase2-fixdep`, `make -C zigux phase2-validate`, and `make -C zigux phase2` stay framed as repo-reality gaps",
)


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def collect_exact_count_issues(text: str, markers: tuple[str, ...], prefix: str) -> list[str]:
    issues: list[str] = []
    for marker in markers:
        count = text.count(marker)
        if count != 1:
            issues.append(f"{prefix}:{count}:{marker}")
    return issues


def collect_issues(root: Path) -> list[str]:
    issues: list[str] = []

    scripts_readme_path = root / SCRIPTS_README_REL
    closure_note_path = root / CLOSURE_NOTE_REL
    tests_readme_path = root / TESTS_README_REL

    for rel_path in REQUIRED_FILES:
        if not (root / rel_path).is_file():
            issues.append(f"missing_file:{rel_path.as_posix()}")

    if not scripts_readme_path.is_file():
        return issues + [f"missing_file:{SCRIPTS_README_REL.as_posix()}"]

    scripts_readme_text = scripts_readme_path.read_text(encoding="utf-8")
    closure_note_text = closure_note_path.read_text(encoding="utf-8") if closure_note_path.is_file() else ""
    tests_readme_text = tests_readme_path.read_text(encoding="utf-8") if tests_readme_path.is_file() else ""

    for marker in SCRIPTS_README_MARKERS:
        if marker not in scripts_readme_text:
            issues.append(f"missing_scripts_readme_marker:{marker}")

    for marker in CLOSURE_NOTE_MARKERS:
        if marker not in closure_note_text:
            issues.append(f"missing_closure_note_marker:{marker}")

    for marker in TESTS_README_MARKERS:
        if marker not in tests_readme_text:
            issues.append(f"missing_tests_readme_marker:{marker}")

    issues.extend(
        collect_exact_count_issues(
            scripts_readme_text,
            SCRIPTS_README_EXACT_COUNT_MARKERS,
            "exact_count_scripts_readme_marker",
        )
    )
    issues.extend(
        collect_exact_count_issues(
            tests_readme_text,
            TESTS_README_EXACT_COUNT_MARKERS,
            "exact_count_tests_readme_marker",
        )
    )

    for marker in FORBIDDEN_SCRIPTS_README_MARKERS:
        count = scripts_readme_text.count(marker)
        if count:
            issues.append(f"forbidden_scripts_readme_marker:{marker}:count={count}:expected=0")

    return issues


def build_good_tree(root: Path) -> None:
    write_text(root / SCRIPTS_README_REL, "\n".join(SCRIPTS_README_MARKERS) + "\n")
    write_text(root / CLOSURE_NOTE_REL, "\n".join(CLOSURE_NOTE_MARKERS) + "\n")
    write_text(root / TESTS_README_REL, "\n".join(TESTS_README_MARKERS) + "\n")
    for rel_path in REQUIRED_FILES:
        if rel_path in (SCRIPTS_README_REL, CLOSURE_NOTE_REL, TESTS_README_REL):
            continue
        write_text(root / rel_path, "placeholder\n")


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="phase2_scripts_root_summary_") as tmp_dir:
        root = Path(tmp_dir)

        build_good_tree(root)
        if collect_issues(root):
            raise SystemExit("phase2-scripts-root-summary:self-test:good_tree")
        case_count += 1

        build_good_tree(root)
        (root / SCRIPTS_README_REL).unlink()
        issues = collect_issues(root)
        if f"missing_file:{SCRIPTS_README_REL.as_posix()}" not in issues:
            raise SystemExit("phase2-scripts-root-summary:self-test:missing_scripts_readme")
        case_count += 1

        build_good_tree(root)
        scripts_readme_path = root / SCRIPTS_README_REL
        scripts_readme_path.write_text(
            scripts_readme_path.read_text(encoding="utf-8").replace(SCRIPTS_README_MARKERS[0], "", 1),
            encoding="utf-8",
        )
        issues = collect_issues(root)
        if f"missing_scripts_readme_marker:{SCRIPTS_README_MARKERS[0]}" not in issues:
            raise SystemExit("phase2-scripts-root-summary:self-test:missing_scripts_marker")
        case_count += 1

        build_good_tree(root)
        closure_note_path = root / CLOSURE_NOTE_REL
        closure_note_path.write_text(
            closure_note_path.read_text(encoding="utf-8").replace(CLOSURE_NOTE_MARKERS[0], "", 1),
            encoding="utf-8",
        )
        issues = collect_issues(root)
        if f"missing_closure_note_marker:{CLOSURE_NOTE_MARKERS[0]}" not in issues:
            raise SystemExit("phase2-scripts-root-summary:self-test:missing_closure_marker")
        case_count += 1

        build_good_tree(root)
        tests_readme_path = root / TESTS_README_REL
        tests_readme_path.writeText = None
        tests_readme_path.write_text(
            tests_readme_path.read_text(encoding="utf-8").replace(TESTS_README_MARKERS[1], "", 1),
            encoding="utf-8",
        )
        issues = collect_issues(root)
        if f"missing_tests_readme_marker:{TESTS_README_MARKERS[1]}" not in issues:
            raise SystemExit("phase2-scripts-root-summary:self-test:missing_tests_marker")
        case_count += 1

        build_good_tree(root)
        tests_readme_path = root / TESTS_README_REL
        tests_readme_path.write_text(
            tests_readme_path.read_text(encoding="utf-8") + TESTS_README_EXACT_COUNT_MARKERS[0] + "\n",
            encoding="utf-8",
        )
        issues = collect_issues(root)
        expected = f"exact_count_tests_readme_marker:2:{TESTS_README_EXACT_COUNT_MARKERS[0]}"
        if expected not in issues:
            raise SystemExit("phase2-scripts-root-summary:self-test:duplicate_tests_marker")
        case_count += 1

        build_good_tree(root)
        scripts_readme_path = root / SCRIPTS_README_REL
        scripts_readme_path.write_text(
            scripts_readme_path.read_text(encoding="utf-8") + FORBIDDEN_SCRIPTS_README_MARKERS[0] + "\n",
            encoding="utf-8",
        )
        issues = collect_issues(root)
        expected = f"forbidden_scripts_readme_marker:{FORBIDDEN_SCRIPTS_README_MARKERS[0]}:count=1:expected=0"
        if expected not in issues:
            raise SystemExit("phase2-scripts-root-summary:self-test:forbidden_scripts_marker")
        case_count += 1

    print("PHASE2_SCRIPTS_ROOT_SUMMARY_SELF_TEST=pass")
    print(f"PHASE2_SCRIPTS_ROOT_SUMMARY_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def write_sample_root(root: Path) -> int:
    build_good_tree(root)
    print(f"PHASE2_SCRIPTS_ROOT_SUMMARY_SAMPLE_ROOT={root}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the scripts-root Phase 2 summary stays aligned with the shared closure packet."
    )
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in checker coverage")
    parser.add_argument(
        "--write-sample-root",
        type=Path,
        help="Write a minimal passing sample tree for replay coverage",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root is not None:
        return write_sample_root(args.write_sample_root)

    issues = collect_issues(args.root)
    if issues:
        print("PHASE2_SCRIPTS_ROOT_SUMMARY=fail")
        print("PHASE2_SCRIPTS_ROOT_SUMMARY_ISSUES_START")
        for issue in issues:
            print(issue)
        print("PHASE2_SCRIPTS_ROOT_SUMMARY_ISSUES_END")
        return 1

    print("PHASE2_SCRIPTS_ROOT_SUMMARY=pass")
    print(f"PHASE2_SCRIPTS_ROOT_SUMMARY_FILE_COUNT={len(REQUIRED_FILES)}")
    print(
        "PHASE2_SCRIPTS_ROOT_SUMMARY_MARKER_COUNT="
        f"{len(SCRIPTS_README_MARKERS) + len(CLOSURE_NOTE_MARKERS) + len(TESTS_README_MARKERS)}"
    )
    print(
        "PHASE2_SCRIPTS_ROOT_SUMMARY_EXACT_COUNT_MARKER_COUNT="
        f"{len(SCRIPTS_README_EXACT_COUNT_MARKERS) + len(TESTS_README_EXACT_COUNT_MARKERS)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
