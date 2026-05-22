#!/usr/bin/env python3
"""Check that the tests-root Phase 2 summary stays aligned with the shared closure packet."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent

TESTS_README_REL = Path("zigux/tests/README.md")
CLOSURE_NOTE_REL = Path("Documentation/zigux/phase2-closure.md")
SCRIPTS_README_REL = Path("scripts/zigux/README.md")
MAKEFILE_REL = Path("zigux/Makefile")

REQUIRED_FILES = (
    TESTS_README_REL,
    CLOSURE_NOTE_REL,
    SCRIPTS_README_REL,
    MAKEFILE_REL,
    Path("Documentation/zigux/phase2-toolchain-bootstrap-notes.md"),
    Path("Documentation/zigux/review-checklist.md"),
    Path("scripts/zigux/check-phase2-tests-readme-alignment.py"),
    Path("scripts/zigux/check-lane05-local-first-archive-workflow.py"),
    Path("scripts/zigux/check-lane05-local-archive-readme.py"),
    Path("scripts/zigux/check-phase2-cross.py"),
    Path("scripts/zigux/check-genksyms-bridge.py"),
    Path("scripts/zigux/check-phase2-fixdep-gate.py"),
    Path("scripts/zigux/check-fixdep-diff.py"),
    Path("scripts/zigux/install-zig.py"),
    Path("scripts/zigux/validate-phase2.py"),
    Path("scripts/zigux/validate-phase2-closure.py"),
    Path("scripts/zigux/fixdep.zig"),
    Path("scripts/zigux/genksyms.zig"),
    Path("third_party/README.md"),
    Path("third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz"),
    Path("zigux/tests/fixtures/phase2_tool_manifest.json"),
    Path("zigux/tests/fixtures/phase2_artifact_tools_manifest.json"),
    Path("zigux/tests/fixtures/phase2_cross_targets.json"),
    Path("zigux/tests/fixtures/fixdep/cases.json"),
    Path("zigux/tests/fixtures/genksyms_bridge/cases.json"),
)

TESTS_README_MARKERS = (
    "## Phase 2 review packet",
    "The current directly readable Phase 2 packet is the scripts-root kbuild, installer, direct cross-route, cross-selftest, docs-shared-reminder, tool-manifest, artifact-tools-manifest, required-make-route, toolchain reminder, kconfig bridge checker, genksyms bridge, and fixdep governance and parity set plus the live kconfig bridge helpers, the restored closure-side note, validator entrypoint, closure validator, the shipped `zigux/Makefile` wrappers, and their fixture roster",
    "Keep the rematerialized make-wrapper packet explicit through `make -C zigux phase2-toolchain`, `make -C zigux phase2-tools`, `make -C zigux phase2-kconfig`, `make -C zigux phase2-cross`, `make -C zigux phase2-genksyms`, `make -C zigux phase2-fixdep`, `make -C zigux phase2-validate`, and `make -C zigux phase2`.",
    "keep the repo-local pinned archive packet explicit through `third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz`, `python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz --archive-target x86_64-linux`, and the local-first `third_party`, mirror, then direct-download bootstrap order reused by `.github/workflows/zigux-bootstrap.yml` and the two Lane 05 archive checkers",
    "keep the local-first archive workflow replay surface explicit through `python3 scripts/zigux/check-lane05-local-first-archive-workflow.py --self-test`, `python3 scripts/zigux/check-lane05-local-first-archive-workflow.py`, `python3 scripts/zigux/check-lane05-local-archive-readme.py --self-test`, and `python3 scripts/zigux/check-lane05-local-archive-readme.py`.",
    "current `master` now directly materializes `scripts/zigux/install-zig.py`, `python3 scripts/zigux/install-zig.py --self-test`, `scripts/zigux/check-phase2-cross.py`, `python3 scripts/zigux/check-phase2-cross.py --self-test`, and `zigux/tests/fixtures/phase2_cross_targets.json`, so keep that returned installer, direct cross-route, and cross-target fixture packet explicit here instead of leaving it in the historical-gap bucket",
    "current `master` also directly materializes `scripts/zigux/check-genksyms-bridge.py`, `scripts/zigux/genksyms.zig`, `make -C zigux phase2-genksyms`, and the `zigux/tests/fixtures/genksyms_bridge/` packet, so keep that returned checker, bridge helper, wrapper, and fixture roster explicit here instead of leaving it outside the tests-root reminder",
    "current `master` also directly materializes `scripts/zigux/check-phase2-fixdep-gate.py`, `scripts/zigux/check-fixdep-diff.py`, `scripts/zigux/fixdep.zig`, `make -C zigux phase2-fixdep`, and `zigux/tests/fixtures/fixdep/cases.json`, so keep that returned fixdep governance, parity, helper, wrapper, and fixture packet explicit here instead of leaving it outside the tests-root reminder",
    "Tests-root reviewer prompt:",
    "- Does the bounded Phase 2 reminder keep the current direct-readback toolchain self-check, repo-local archive workflow, installer, direct cross-route, cross-selftest, docs-shared-reminder, tool-manifest, artifact-tools-manifest, required-make-route, validator, closure-validator, kconfig bridge, genksyms bridge, fixdep packet, make-wrapper, and fixture packet aligned without reviving older missing validator-first or wrapper-only proof?",
)

TESTS_README_EXACT_COUNT_MARKERS = (
    TESTS_README_MARKERS[2],
    TESTS_README_MARKERS[4],
    TESTS_README_MARKERS[6],
    TESTS_README_MARKERS[7],
    TESTS_README_MARKERS[9],
)

CLOSURE_NOTE_MARKERS = (
    "`zigux/tests/README.md`",
    "`scripts/zigux/check-phase2-tests-readme-alignment.py`",
    "`scripts/zigux/check-lane05-local-first-archive-workflow.py`",
    "`scripts/zigux/check-lane05-local-archive-readme.py`",
    "`scripts/zigux/check-phase2-cross.py`",
    "`scripts/zigux/check-genksyms-bridge.py`",
    "`scripts/zigux/check-phase2-fixdep-gate.py`",
    "`scripts/zigux/check-fixdep-diff.py`",
    "`make -C zigux phase2-cross`",
    "`make -C zigux phase2-genksyms`",
    "`make -C zigux phase2-fixdep`",
    "`PHASE2_SHARED_MAKE_ROUTES=make -C zigux phase2-toolchain,make -C zigux phase2-tools,make -C zigux phase2-kconfig,make -C zigux phase2-cross,make -C zigux phase2-genksyms,make -C zigux phase2-fixdep,make -C zigux phase2-validate,make -C zigux phase2`",
    "`PHASE2_NEXT_SAFE_STEP=keep the shared Phase 2 closure packet parked unless one shared reminder surface drifts again; if the shared backlog reopens first, start with one smallest truthfulness repair in Documentation/zigux/README.md, zigux/tests/README.md, or the directly coupled shared checker that proves the drift, and keep fixdep-, genksyms-, and kconfig-local follow-through in their dedicated lanes`",
)

SCRIPTS_README_MARKERS = (
    "## Phase 2",
    "- Phase 2 flow - the current scripts-root bridge packet stays reviewable through the live toolchain checker, installer helper, direct cross-route packet, `conf_bridge` and `confdata_bridge` helper surfaces, the restored closure-side validator packet, the manifest-backed kconfig fixture roster, the shipped make-wrapper packet, and the surviving Phase 2 alignment guards instead of replaying older missing-route assumptions inside that now-rematerialized toolchain packet",
    "`scripts/zigux/check-zig-toolchain.py`, `scripts/zigux/check-phase2-kbuild-routes.py`, `scripts/zigux/check-genksyms-bridge.py`, `scripts/zigux/check-phase2-docs-shared-reminder.py`, `scripts/zigux/check-phase2-kconfig-selftest-alignment.py`, `scripts/zigux/check-phase2-tests-readme-alignment.py`, `scripts/zigux/check-phase2-cross.py`, `scripts/zigux/check-phase2-cross-selftest-alignment.py`, `scripts/zigux/check-phase2-toolchain-pinning.py`, `scripts/zigux/check-phase2-toolchain-pin-scope.py`, `scripts/zigux/check-phase2-tool-manifest.py`, `scripts/zigux/check-phase2-artifact-tools-manifest.py`, `scripts/zigux/check-phase2-fixdep-gate.py`, `scripts/zigux/check-fixdep-diff.py`, and `scripts/zigux/check-phase2-required-make-routes.py` remain the shipped Phase 2 toolchain, reminder, alignment, artifact-support, fixdep, genksyms-bridge, and required-make-route guards that survive on current `master`",
    "`Documentation/zigux/phase2-closure.md`, `scripts/zigux/validate-phase2.py`, `scripts/zigux/validate-phase2-closure.py`, `zigux/Makefile`, `make -C zigux phase2-toolchain`, `make -C zigux phase2-tools`, `make -C zigux phase2-kconfig`, `make -C zigux phase2-cross`, `make -C zigux phase2-genksyms`, `make -C zigux phase2-fixdep`, `make -C zigux phase2-validate`, `make -C zigux phase2`, `zigux/tests/fixtures/phase2_tool_manifest.json`, and `zigux/tests/fixtures/phase2_artifact_tools_manifest.json` keep the shipped closure-side reminder, closure-validator, validator entrypoint, make-wrapper, and artifact-support packet explicit from the scripts root beside the surviving checker set",
    "`scripts/zigux/install-zig.py`, `python3 scripts/zigux/install-zig.py --self-test`, `python3 scripts/zigux/check-phase2-cross.py --self-test`, `python3 scripts/zigux/check-phase2-cross.py`, and `zigux/tests/fixtures/phase2_cross_targets.json` are directly readable on current `master`, so keep those installer and direct cross-route surfaces explicit beside the shipped toolchain and kbuild reminder packet instead of leaving them in repo-reality-gap wording",
    "- keep those installer, tool-manifest, artifact-support, direct cross-route, genksyms bridge, and fixdep surfaces explicit beside the shipped toolchain and kbuild reminder packet",
)

MAKEFILE_MARKERS = (
    "phase2-cross:",
    "phase2-genksyms:",
    "phase2-fixdep:",
    "phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep",
    "phase2: phase2-validate",
)

FORBIDDEN_TESTS_README_MARKERS = (
    "repeated authenticated reads on current `master` still return missing for `scripts/zigux/validate-phase2-closure.py`, `scripts/zigux/install-zig.py`",
    "the current directly readable Phase 2 packet is the scripts-root kbuild, installer, direct cross-route, cross-selftest, docs-shared-reminder, required-make-route, and toolchain reminder set plus the live kconfig bridge helpers, the restored closure-side note, validator entrypoint, and closure validator, the shipped `zigux/Makefile` wrappers, and their fixture roster",
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

    for rel_path in REQUIRED_FILES:
        if not (root / rel_path).is_file():
            issues.append(f"missing_file:{rel_path.as_posix()}")

    tests_readme_path = root / TESTS_README_REL
    closure_note_path = root / CLOSURE_NOTE_REL
    scripts_readme_path = root / SCRIPTS_README_REL
    makefile_path = root / MAKEFILE_REL
    if not tests_readme_path.is_file():
        return issues + [f"missing_file:{TESTS_README_REL.as_posix()}"]

    tests_readme_text = tests_readme_path.read_text(encoding="utf-8")
    closure_note_text = closure_note_path.read_text(encoding="utf-8") if closure_note_path.is_file() else ""
    scripts_readme_text = scripts_readme_path.read_text(encoding="utf-8") if scripts_readme_path.is_file() else ""
    makefile_text = makefile_path.read_text(encoding="utf-8") if makefile_path.is_file() else ""

    for marker in TESTS_README_MARKERS:
        if marker not in tests_readme_text:
            issues.append(f"missing_tests_readme_marker:{marker}")
    for marker in CLOSURE_NOTE_MARKERS:
        if marker not in closure_note_text:
            issues.append(f"missing_closure_note_marker:{marker}")
    for marker in SCRIPTS_README_MARKERS:
        if marker not in scripts_readme_text:
            issues.append(f"missing_scripts_readme_marker:{marker}")
    for marker in MAKEFILE_MARKERS:
        if marker not in makefile_text:
            issues.append(f"missing_makefile_marker:{marker}")
    for marker in FORBIDDEN_TESTS_README_MARKERS:
        count = tests_readme_text.count(marker)
        if count:
            issues.append(f"forbidden_tests_readme_marker:{marker}:count={count}:expected=0")

    issues.extend(
        collect_exact_count_issues(
            tests_readme_text,
            TESTS_README_EXACT_COUNT_MARKERS,
            "exact_count_tests_readme_marker",
        )
    )
    return issues


def build_good_tree(root: Path) -> None:
    write_text(root / TESTS_README_REL, "\n".join(TESTS_README_MARKERS) + "\n")
    write_text(root / CLOSURE_NOTE_REL, "\n".join(CLOSURE_NOTE_MARKERS) + "\n")
    write_text(root / SCRIPTS_README_REL, "\n".join(SCRIPTS_README_MARKERS) + "\n")
    write_text(root / MAKEFILE_REL, "\n".join(MAKEFILE_MARKERS) + "\n")
    for rel_path in REQUIRED_FILES:
        if rel_path in (TESTS_README_REL, CLOSURE_NOTE_REL, SCRIPTS_README_REL, MAKEFILE_REL):
            continue
        write_text(root / rel_path, "placeholder\n")


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="phase2_tests_root_summary_") as tmp_dir:
        root = Path(tmp_dir)

        build_good_tree(root)
        if collect_issues(root):
            raise SystemExit("phase2-tests-root-summary:self-test:good_tree")
        case_count += 1

        build_good_tree(root)
        (root / TESTS_README_REL).unlink()
        issues = collect_issues(root)
        if f"missing_file:{TESTS_README_REL.as_posix()}" not in issues:
            raise SystemExit("phase2-tests-root-summary:self-test:missing_tests_readme")
        case_count += 1

        build_good_tree(root)
        tests_readme_path = root / TESTS_README_REL
        tests_readme_path.write_text(
            tests_readme_path.read_text(encoding="utf-8").replace(TESTS_README_MARKERS[0], "", 1),
            encoding="utf-8",
        )
        issues = collect_issues(root)
        if f"missing_tests_readme_marker:{TESTS_README_MARKERS[0]}" not in issues:
            raise SystemExit("phase2-tests-root-summary:self-test:missing_tests_marker")
        case_count += 1

        build_good_tree(root)
        closure_note_path = root / CLOSURE_NOTE_REL
        closure_note_path.write_text(
            closure_note_path.read_text(encoding="utf-8").replace(CLOSURE_NOTE_MARKERS[0], "", 1),
            encoding="utf-8",
        )
        issues = collect_issues(root)
        if f"missing_closure_note_marker:{CLOSURE_NOTE_MARKERS[0]}" not in issues:
            raise SystemExit("phase2-tests-root-summary:self-test:missing_closure_marker")
        case_count += 1

        build_good_tree(root)
        scripts_readme_path = root / SCRIPTS_README_REL
        scripts_readme_path.write_text(
            scripts_readme_path.read_text(encoding="utf-8").replace(SCRIPTS_README_MARKERS[0], "", 1),
            encoding="utf-8",
        )
        issues = collect_issues(root)
        if f"missing_scripts_readme_marker:{SCRIPTS_README_MARKERS[0]}" not in issues:
            raise SystemExit("phase2-tests-root-summary:self-test:missing_scripts_marker")
        case_count += 1

        build_good_tree(root)
        makefile_path = root / MAKEFILE_REL
        makefile_path.write_text(
            makefile_path.read_text(encoding="utf-8").replace(MAKEFILE_MARKERS[0], "", 1),
            encoding="utf-8",
        )
        issues = collect_issues(root)
        if f"missing_makefile_marker:{MAKEFILE_MARKERS[0]}" not in issues:
            raise SystemExit("phase2-tests-root-summary:self-test:missing_makefile_marker")
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
            raise SystemExit("phase2-tests-root-summary:self-test:duplicate_tests_marker")
        case_count += 1

        build_good_tree(root)
        tests_readme_path = root / TESTS_README_REL
        tests_readme_path.write_text(
            tests_readme_path.read_text(encoding="utf-8") + FORBIDDEN_TESTS_README_MARKERS[0] + "\n",
            encoding="utf-8",
        )
        issues = collect_issues(root)
        expected = f"forbidden_tests_readme_marker:{FORBIDDEN_TESTS_README_MARKERS[0]}:count=1:expected=0"
        if expected not in issues:
            raise SystemExit("phase2-tests-root-summary:self-test:forbidden_tests_marker")
        case_count += 1

    print("PHASE2_TESTS_ROOT_SUMMARY_SELF_TEST=pass")
    print(f"PHASE2_TESTS_ROOT_SUMMARY_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def write_sample_root(root: Path) -> int:
    build_good_tree(root)
    print(f"PHASE2_TESTS_ROOT_SUMMARY_SAMPLE_ROOT={root}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the tests-root Phase 2 summary stays aligned with the shared closure packet."
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
        print("PHASE2_TESTS_ROOT_SUMMARY=fail")
        print("PHASE2_TESTS_ROOT_SUMMARY_ISSUES_START")
        for issue in issues:
            print(issue)
        print("PHASE2_TESTS_ROOT_SUMMARY_ISSUES_END")
        return 1

    print("PHASE2_TESTS_ROOT_SUMMARY=pass")
    print(f"PHASE2_TESTS_ROOT_SUMMARY_FILE_COUNT={len(REQUIRED_FILES)}")
    print(
        "PHASE2_TESTS_ROOT_SUMMARY_MARKER_COUNT="
        f"{len(TESTS_README_MARKERS) + len(CLOSURE_NOTE_MARKERS) + len(SCRIPTS_README_MARKERS) + len(MAKEFILE_MARKERS)}"
    )
    print(
        "PHASE2_TESTS_ROOT_SUMMARY_EXACT_COUNT_MARKER_COUNT="
        f"{len(TESTS_README_EXACT_COUNT_MARKERS)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
