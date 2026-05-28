#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
DOCS_README = ROOT / "Documentation" / "zigux" / "README.md"
PHASE2_NOTES = ROOT / "Documentation" / "zigux" / "phase2-toolchain-bootstrap-notes.md"
REVIEW_CHECKLIST = ROOT / "Documentation" / "zigux" / "review-checklist.md"
SCRIPTS_README = ROOT / "scripts" / "zigux" / "README.md"
TESTS_README = ROOT / "zigux" / "tests" / "README.md"
THIRD_PARTY_README = ROOT / "third_party" / "README.md"

DOCS_README_MARKERS = (
    "Phase 2 notes - `Documentation/zigux/phase2-closure.md` - `Documentation/zigux/phase2-toolchain-bootstrap-notes.md`",
    "`scripts/zigux/check-phase2-docs-shared-reminder.py`",
    "`scripts/zigux/check-phase2-tool-manifest.py` and `zigux/tests/fixtures/phase2_tool_manifest.json` keep the fixture-backed Phase 2 manifest packet explicit from the docs root beside the shipped reminder and make-wrapper surfaces.",
    "`scripts/zigux/check-phase2-artifact-tools-manifest.py` and `zigux/tests/fixtures/phase2_artifact_tools_manifest.json` keep the fixture-backed Phase 2 manifest packet explicit from the docs root beside the shipped reminder and make-wrapper surfaces.",
    "`third_party/README.md`, `scripts/zigux/check-lane05-local-first-archive-workflow.py`, and `scripts/zigux/check-lane05-local-archive-readme.py` are directly readable on current `master` again",
    "`scripts/zigux/install-zig.py`, `scripts/zigux/check-phase2-cross.py`, `scripts/zigux/check-phase2-cross-selftest-alignment.py`, and `zigux/tests/fixtures/phase2_cross_targets.json` are directly readable on current `master` again",
    "`scripts/zigux/check-phase2-fixdep-gate.py`, `scripts/zigux/check-fixdep-diff.py`, `scripts/zigux/fixdep.zig`, `zigux/tests/fixtures/fixdep/cases.json`, and `make -C zigux phase2-fixdep` are directly readable on current `master` again",
    "`python3 scripts/zigux/validate-phase2.py`, `python3 scripts/zigux/validate-phase2-closure.py`, `make -C zigux phase2-toolchain`, `make -C zigux phase2-tools`, `make -C zigux phase2-kconfig`, `make -C zigux phase2-cross`, `make -C zigux phase2-genksyms`, `make -C zigux phase2-fixdep`, `make -C zigux phase2-validate`, and `make -C zigux phase2` replay the bounded current Phase 2 closure-side, bounded genksyms bridge, and make-wrapper packet without widening it back into older missing-route assumptions.",
)

PHASE2_NOTES_MARKERS = (
    "# Phase 2 Toolchain Bootstrap Notes",
    "## Current direct packet",
    "`scripts/zigux/check-phase2-docs-shared-reminder.py`",
    "`scripts/zigux/check-phase2-bootstrap-workflow-routes.py`",
    "`scripts/zigux/check-phase2-kconfig-allconfig-helper-packet.py`",
    "`scripts/zigux/check-phase2-genksyms-selftest-alignment.py`",
    "`scripts/zigux/check-lane05-install-zig-archive-verification.py`",
    "`scripts/zigux/check-lane05-local-first-archive-workflow.py`",
    "`scripts/zigux/check-lane05-local-archive-readme.py`",
    "`scripts/zigux/stage-pinned-zig-archive.py`",
    "`scripts/zigux/check-lane05-stage-helper-contract.py`",
    "`scripts/zigux/check-lane05-stage-helper-selftest.py`",
    "`zigux/tests/fixtures/phase2_cross_targets.json` keeps the rematerialized direct cross-route packet explicit through the pinned `x86_64-linux` `archive_required` lane plus the `aarch64-linux` `route_contract_only` lane",
    "No current repo-reality gaps remain inside the bounded toolchain, installer, direct cross-route, local-first archive, returned archive-verification and staged-archive helper packet, or returned fixdep packet on current `master`.",
    "bootstrap workflow-route truthfulness",
    "dedicated kconfig allconfig helper guard",
    "aggregate `phase2` route replays",
)

PHASE2_NOTES_EXACT_COUNT_MARKERS = (
    "`scripts/zigux/check-lane05-local-first-archive-workflow.py`",
    "`scripts/zigux/check-lane05-local-archive-readme.py`",
)

PHASE2_NOTES_FORBIDDEN_MARKERS = (
    "historical packet members until same-lane work rematerializes them on `master`",
    "without reviving missing installer or direct cross-route proof text",
    "`zigux/Makefile` and `make -C zigux phase2-toolchain`, `make -C zigux phase2-tools`, `make -C zigux phase2-kconfig`, `make -C zigux phase2-cross`, `make -C zigux phase2-genksyms`, `make -C zigux phase2-validate`, and `make -C zigux phase2` stay framed as repo-reality gaps",
)

REVIEW_CHECKLIST_MARKERS = (
    "* if the change touches the shared Phase 2 toolchain packet, do `Documentation/zigux/README.md`",
    "`scripts/zigux/check-phase2-docs-shared-reminder.py`",
    "`scripts/zigux/check-phase2-required-make-routes.py`",
    "`scripts/zigux/check-phase2-fixdep-gate.py`",
    "`scripts/zigux/check-fixdep-diff.py`",
    "`scripts/zigux/check-lane05-local-first-archive-workflow.py`",
    "`scripts/zigux/check-lane05-local-archive-readme.py`",
    "`scripts/zigux/install-zig.py`",
    "`scripts/zigux/check-phase2-cross.py`",
    "`zigux/tests/fixtures/phase2_cross_targets.json`",
    "current directly readable Phase 2 local-first archive, toolchain, installer, direct cross-route, kbuild, kconfig bridge, docs-shared-reminder, tool-manifest, artifact-support, fixdep, genksyms-bridge, and required-make-route packet",
    "current rematerialized Phase 2 local-first archive, closure-side, closure-validator, validation, installer, direct cross-route, artifact-support, fixdep, toolchain self-check, and make-wrapper packet",
    "`python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz --archive-target x86_64-linux`",
)

REVIEW_CHECKLIST_EXACT_COUNT_MARKERS = (
    "`scripts/zigux/check-lane05-local-first-archive-workflow.py`",
    "`scripts/zigux/check-lane05-local-archive-readme.py`",
    "`python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz --archive-target x86_64-linux`",
)

REVIEW_CHECKLIST_FORBIDDEN_MARKERS = (
    "`scripts/zigux/install-zig.py`, `python3 scripts/zigux/install-zig.py --self-test`, `scripts/zigux/check-phase2-cross.py`, `python3 scripts/zigux/check-phase2-cross.py --self-test`, `python3 scripts/zigux/check-phase2-cross.py`, and `zigux/tests/fixtures/phase2_cross_targets.json` stay framed as historical packet members rather than shipped current-`master` evidence",
    "`zigux/Makefile`, `make -C zigux phase2-toolchain`, `make -C zigux phase2-tools`, `make -C zigux phase2-kconfig`, `make -C zigux phase2-cross`, `make -C zigux phase2-genksyms`, `make -C zigux phase2-validate`, and `make -C zigux phase2` stay framed as historical packet members rather than shipped current-`master` evidence",
)

SCRIPTS_README_MARKERS = (
    "## Phase 2",
    "Phase 2 flow - the current fixdep packet stays reviewable through the dedicated governance guard, parity checker, and shipped `phase2-fixdep` wrapper instead of widening back into older shared reminder churn",
    "`scripts/zigux/check-phase2-fixdep-gate.py`, `scripts/zigux/check-fixdep-diff.py`, `scripts/zigux/fixdep.zig`, `zigux/tests/fixtures/fixdep/cases.json`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml` keep the current fixdep governance, determinism, helper, fixture, and CI packet explicit from the scripts root",
    "`python3 scripts/zigux/check-phase2-fixdep-gate.py --self-test`, `python3 scripts/zigux/check-phase2-fixdep-gate.py`, `python3 scripts/zigux/check-fixdep-diff.py --self-test`, `python3 scripts/zigux/check-fixdep-diff.py`, `zig test scripts/zigux/fixdep.zig`, and `make -C zigux phase2-fixdep` replay the shipped fixdep lane without widening into unrelated Phase 2 surfaces",
)

SCRIPTS_README_FORBIDDEN_MARKERS = (
    "repeated authenticated reads on current `master` still return missing for `scripts/zigux/install-zig.py`",
    "`zigux/Makefile`, `make -C zigux phase2-toolchain`, `make -C zigux phase2-tools`, `make -C zigux phase2-kconfig`, `make -C zigux phase2-cross`, `make -C zigux phase2-genksyms`, `make -C zigux phase2-validate`, and `make -C zigux phase2` stay framed as repo-reality gaps",
)

TESTS_README_MARKERS = (
    "## Phase 2 review packet",
    "`Documentation/zigux/phase2-toolchain-bootstrap-notes.md`",
    "`scripts/zigux/check-phase2-kconfig-allconfig-helper-packet.py`",
    "`scripts/zigux/check-kconfig-bridge.py`",
    "`scripts/zigux/check-phase2-genksyms-selftest-alignment.py`",
    "`scripts/zigux/check-genksyms-bridge.py`",
    "`scripts/zigux/genksyms_version_before_ambiguous_long_option_test.zig`",
    "`make -C zigux phase2-genksyms`",
    "`scripts/zigux/check-phase2-fixdep-gate.py`",
    "`scripts/zigux/check-fixdep-diff.py`",
    "`make -C zigux phase2-fixdep`",
    "current `master` now directly materializes `scripts/zigux/install-zig.py`, `python3 scripts/zigux/install-zig.py --self-test`, `scripts/zigux/check-phase2-cross.py`, `python3 scripts/zigux/check-phase2-cross.py --self-test`, and `zigux/tests/fixtures/phase2_cross_targets.json`",
    "keep the local-first archive workflow replay surface explicit through `python3 scripts/zigux/check-lane05-local-first-archive-workflow.py --self-test`, `python3 scripts/zigux/check-lane05-local-first-archive-workflow.py`, `python3 scripts/zigux/check-lane05-local-archive-readme.py --self-test`, and `python3 scripts/zigux/check-lane05-local-archive-readme.py`.",
)

TESTS_README_EXACT_COUNT_MARKERS = (
    "keep the local-first archive workflow replay surface explicit through `python3 scripts/zigux/check-lane05-local-first-archive-workflow.py --self-test`, `python3 scripts/zigux/check-lane05-local-first-archive-workflow.py`, `python3 scripts/zigux/check-lane05-local-archive-readme.py --self-test`, and `python3 scripts/zigux/check-lane05-local-archive-readme.py`.",
)

THIRD_PARTY_README_MARKERS = (
    "# Zigux third-party archives",
    "## Current pinned Zig archive contract",
    "- target: `x86_64-linux`",
    "- channel: `0.17.0-dev.87+9b177a7d2`",
    "- file: `third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz`",
    "- sha256: `313b231e76f3cc9b718044602dbc3c42b531693507203a6baf2fa892c9533e77`",
    "- size: `58159088` bytes",
    "- Lane 05 bootstrap first reuses and validates `third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz` when that pinned archive is present.",
    "- If the exact archive file is absent but `third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz.parts` is present, `.github/workflows/zigux-bootstrap.yml` stages the same pinned payload locally with `scripts/zigux/stage-pinned-zig-archive.py` before mirror or direct-download fallback.",
    "- `scripts/zigux/check-lane05-install-zig-archive-verification.py`, `scripts/zigux/check-lane05-stage-helper-contract.py`, and `scripts/zigux/check-lane05-stage-helper-selftest.py` keep the archive-verification, staged-helper contract, and staged-helper self-test packet explicit beside that same local-first archive path.",
    "- do not keep duplicate-suffix copies such as `zig-x86_64-linux-0.17.0-dev.87+9b177a7d2 (1).tar.xz` in this directory",
)

THIRD_PARTY_README_EXACT_COUNT_MARKERS = (
    "- Lane 05 bootstrap first reuses and validates `third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz` when that pinned archive is present.",
    "- If the exact archive file is absent but `third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz.parts` is present, `.github/workflows/zigux-bootstrap.yml` stages the same pinned payload locally with `scripts/zigux/stage-pinned-zig-archive.py` before mirror or direct-download fallback.",
)


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def resolve_path(root: Path, path: Path) -> Path:
    try:
        return root / path.relative_to(ROOT)
    except ValueError:
        return root / path


def collect_missing_markers(text: str, markers: tuple[str, ...], code: str) -> list[tuple[str, str]]:
    return [(code, marker) for marker in markers if marker not in text]


def collect_forbidden_markers(text: str, markers: tuple[str, ...], code: str) -> list[tuple[str, str]]:
    return [(code, marker) for marker in markers if marker in text]


def collect_exact_count_markers(text: str, markers: tuple[str, ...], code: str) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    for marker in markers:
        count = text.count(marker)
        if count != 1:
            issues.append((code, f"{count}::{marker}"))
    return issues


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    texts = {
        "docs": read_text(resolve_path(root, DOCS_README)),
        "notes": read_text(resolve_path(root, PHASE2_NOTES)),
        "checklist": read_text(resolve_path(root, REVIEW_CHECKLIST)),
        "scripts": read_text(resolve_path(root, SCRIPTS_README)),
        "tests": read_text(resolve_path(root, TESTS_README)),
        "third_party": read_text(resolve_path(root, THIRD_PARTY_README)),
    }
    issues.extend(collect_missing_markers(texts["docs"], DOCS_README_MARKERS, "MISSING_DOCS_README_MARKERS"))
    issues.extend(collect_missing_markers(texts["notes"], PHASE2_NOTES_MARKERS, "MISSING_PHASE2_NOTES_MARKERS"))
    issues.extend(collect_exact_count_markers(texts["notes"], PHASE2_NOTES_EXACT_COUNT_MARKERS, "EXACT_COUNT_PHASE2_NOTES_MARKERS"))
    issues.extend(collect_forbidden_markers(texts["notes"], PHASE2_NOTES_FORBIDDEN_MARKERS, "FORBIDDEN_PHASE2_NOTES_MARKERS"))
    issues.extend(collect_missing_markers(texts["checklist"], REVIEW_CHECKLIST_MARKERS, "MISSING_REVIEW_CHECKLIST_MARKERS"))
    issues.extend(collect_exact_count_markers(texts["checklist"], REVIEW_CHECKLIST_EXACT_COUNT_MARKERS, "EXACT_COUNT_REVIEW_CHECKLIST_MARKERS"))
    issues.extend(collect_forbidden_markers(texts["checklist"], REVIEW_CHECKLIST_FORBIDDEN_MARKERS, "FORBIDDEN_REVIEW_CHECKLIST_MARKERS"))
    issues.extend(collect_missing_markers(texts["scripts"], SCRIPTS_README_MARKERS, "MISSING_SCRIPTS_README_MARKERS"))
    issues.extend(collect_forbidden_markers(texts["scripts"], SCRIPTS_README_FORBIDDEN_MARKERS, "FORBIDDEN_SCRIPTS_README_MARKERS"))
    issues.extend(collect_missing_markers(texts["tests"], TESTS_README_MARKERS, "MISSING_TESTS_README_MARKERS"))
    issues.extend(collect_exact_count_markers(texts["tests"], TESTS_README_EXACT_COUNT_MARKERS, "EXACT_COUNT_TESTS_README_MARKERS"))
    issues.extend(collect_missing_markers(texts["third_party"], THIRD_PARTY_README_MARKERS, "MISSING_THIRD_PARTY_README_MARKERS"))
    issues.extend(collect_exact_count_markers(texts["third_party"], THIRD_PARTY_README_EXACT_COUNT_MARKERS, "EXACT_COUNT_THIRD_PARTY_README_MARKERS"))
    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)
    print("PHASE2_DOCS_SHARED_REMINDER=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_self_test_root(root: Path) -> None:
    write_text(resolve_path(root, DOCS_README), "\n".join(DOCS_README_MARKERS) + "\n")
    write_text(resolve_path(root, PHASE2_NOTES), "\n".join(PHASE2_NOTES_MARKERS) + "\n")
    write_text(resolve_path(root, REVIEW_CHECKLIST), "\n".join(REVIEW_CHECKLIST_MARKERS) + "\n")
    write_text(resolve_path(root, SCRIPTS_README), "\n".join(SCRIPTS_README_MARKERS) + "\n")
    write_text(resolve_path(root, TESTS_README), "\n".join(TESTS_README_MARKERS) + "\n")
    write_text(resolve_path(root, THIRD_PARTY_README), "\n".join(THIRD_PARTY_README_MARKERS) + "\n")


def replace_all(text: str, marker: str) -> str:
    if marker not in text:
        raise AssertionError(f"marker not found: {marker}")
    return text.replace(marker, "")


def run_self_test() -> int:
    checks_run = 0
    expected_case_count = (
        1
        + len(DOCS_README_MARKERS)
        + len(PHASE2_NOTES_MARKERS)
        + len(PHASE2_NOTES_EXACT_COUNT_MARKERS)
        + len(PHASE2_NOTES_FORBIDDEN_MARKERS)
        + len(REVIEW_CHECKLIST_MARKERS)
        + len(REVIEW_CHECKLIST_EXACT_COUNT_MARKERS)
        + len(REVIEW_CHECKLIST_FORBIDDEN_MARKERS)
        + len(SCRIPTS_README_MARKERS)
        + len(SCRIPTS_README_FORBIDDEN_MARKERS)
        + len(TESTS_README_MARKERS)
        + len(TESTS_README_EXACT_COUNT_MARKERS)
        + len(THIRD_PARTY_README_MARKERS)
        + len(THIRD_PARTY_README_EXACT_COUNT_MARKERS)
        + 6
    )
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_docs_shared_reminder_") as tmp_dir:
        root = Path(tmp_dir)
        build_self_test_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        suites = (
            (DOCS_README, DOCS_README_MARKERS, "MISSING_DOCS_README_MARKERS"),
            (PHASE2_NOTES, PHASE2_NOTES_MARKERS, "MISSING_PHASE2_NOTES_MARKERS"),
            (REVIEW_CHECKLIST, REVIEW_CHECKLIST_MARKERS, "MISSING_REVIEW_CHECKLIST_MARKERS"),
            (SCRIPTS_README, SCRIPTS_README_MARKERS, "MISSING_SCRIPTS_README_MARKERS"),
            (TESTS_README, TESTS_README_MARKERS, "MISSING_TESTS_README_MARKERS"),
            (THIRD_PARTY_README, THIRD_PARTY_README_MARKERS, "MISSING_THIRD_PARTY_README_MARKERS"),
        )
        for rel_path, markers, code in suites:
            for marker in markers:
                build_self_test_root(root)
                path = resolve_path(root, rel_path)
                path.write_text(replace_all(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
                issues = collect_issues(root)
                assert (code, marker) in issues
                checks_run += 1

        exact_suites = (
            (PHASE2_NOTES, PHASE2_NOTES_EXACT_COUNT_MARKERS, "EXACT_COUNT_PHASE2_NOTES_MARKERS"),
            (REVIEW_CHECKLIST, REVIEW_CHECKLIST_EXACT_COUNT_MARKERS, "EXACT_COUNT_REVIEW_CHECKLIST_MARKERS"),
            (TESTS_README, TESTS_README_EXACT_COUNT_MARKERS, "EXACT_COUNT_TESTS_README_MARKERS"),
            (THIRD_PARTY_README, THIRD_PARTY_README_EXACT_COUNT_MARKERS, "EXACT_COUNT_THIRD_PARTY_README_MARKERS"),
        )
        for rel_path, markers, code in exact_suites:
            for marker in markers:
                build_self_test_root(root)
                path = resolve_path(root, rel_path)
                path.write_text(path.read_text(encoding="utf-8") + marker + "\n", encoding="utf-8")
                issues = collect_issues(root)
                assert (code, f"2::{marker}") in issues
                checks_run += 1

        forbidden_suites = (
            (PHASE2_NOTES, PHASE2_NOTES_FORBIDDEN_MARKERS, "FORBIDDEN_PHASE2_NOTES_MARKERS"),
            (REVIEW_CHECKLIST, REVIEW_CHECKLIST_FORBIDDEN_MARKERS, "FORBIDDEN_REVIEW_CHECKLIST_MARKERS"),
            (SCRIPTS_README, SCRIPTS_README_FORBIDDEN_MARKERS, "FORBIDDEN_SCRIPTS_README_MARKERS"),
        )
        for rel_path, markers, code in forbidden_suites:
            for marker in markers:
                build_self_test_root(root)
                path = resolve_path(root, rel_path)
                path.write_text(path.read_text(encoding="utf-8") + marker + "\n", encoding="utf-8")
                issues = collect_issues(root)
                assert (code, marker) in issues
                checks_run += 1

        for rel_path in (DOCS_README, PHASE2_NOTES, REVIEW_CHECKLIST, SCRIPTS_README, TESTS_README, THIRD_PARTY_README):
            build_self_test_root(root)
            resolve_path(root, rel_path).unlink()
            try:
                collect_issues(root)
            except SystemExit as exc:
                assert "required file missing" in str(exc)
                checks_run += 1
            else:
                raise AssertionError(f"missing file did not abort: {rel_path}")

    assert checks_run == expected_case_count
    print("PHASE2_DOCS_SHARED_REMINDER_SELF_TEST=pass")
    print(f"PHASE2_DOCS_SHARED_REMINDER_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Keep the shared Phase 2 reminder packet aligned to current docs-root, notes, checklist, scripts-root, tests-root, and third-party surfaces."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run the built-in contract self-test")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("PHASE2_DOCS_SHARED_REMINDER=pass")
    print(
        "PHASE2_DOCS_SHARED_REMINDER_MARKER_COUNT="
        f"{len(DOCS_README_MARKERS) + len(PHASE2_NOTES_MARKERS) + len(REVIEW_CHECKLIST_MARKERS) + len(SCRIPTS_README_MARKERS) + len(TESTS_README_MARKERS) + len(THIRD_PARTY_README_MARKERS)}"
    )
    print(
        "PHASE2_DOCS_SHARED_REMINDER_EXACT_COUNT_MARKER_COUNT="
        f"{len(PHASE2_NOTES_EXACT_COUNT_MARKERS) + len(REVIEW_CHECKLIST_EXACT_COUNT_MARKERS) + len(TESTS_README_EXACT_COUNT_MARKERS) + len(THIRD_PARTY_README_EXACT_COUNT_MARKERS)}"
    )
    print(
        "PHASE2_DOCS_SHARED_REMINDER_FORBIDDEN_MARKER_COUNT="
        f"{len(PHASE2_NOTES_FORBIDDEN_MARKERS) + len(REVIEW_CHECKLIST_FORBIDDEN_MARKERS) + len(SCRIPTS_README_FORBIDDEN_MARKERS)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
