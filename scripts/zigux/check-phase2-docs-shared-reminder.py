#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DOCS_README = ROOT / "Documentation" / "zigux" / "README.md"
REVIEW_CHECKLIST = ROOT / "Documentation" / "zigux" / "review-checklist.md"
SCRIPTS_README = ROOT / "scripts" / "zigux" / "README.md"

DOCS_README_MARKERS = (
    "Phase 2 notes",
    "- `Documentation/zigux/phase2-toolchain-bootstrap-notes.md`",
    "- `Documentation/zigux/phase2-closure.md`",
    "- `Documentation/zigux/review-checklist.md`",
    "- `scripts/zigux/README.md`",
    "- `scripts/zigux/validate-phase2.py`",
    "- `scripts/zigux/validate-phase2-closure.py`",
    "- `scripts/zigux/check-zig-toolchain.py`",
    "- `scripts/zigux/install-zig.py`",
    "- `scripts/zigux/check-phase2-kbuild-routes.py`",
    "- `scripts/zigux/check-phase2-kconfig-selftest-alignment.py`",
    "- `scripts/zigux/check-phase2-tests-readme-alignment.py`",
    "- `scripts/zigux/check-phase2-toolchain-pinning.py`",
    "- `scripts/zigux/check-phase2-cross-selftest-alignment.py`",
    "- `scripts/zigux/check-phase2-toolchain-pin-scope.py`",
    "- `scripts/zigux/check-phase2-docs-shared-reminder.py`",
    "- `scripts/zigux/check-phase2-required-make-routes.py`",
    "- `python3 scripts/zigux/check-zig-toolchain.py --self-test`",
    "- `python3 scripts/zigux/check-zig-toolchain.py --policy-only`",
    "- `python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing`",
    "- `python3 scripts/zigux/install-zig.py --self-test`",
    "- `python3 scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test`",
    "- `scripts/zigux/kconfig/conf_bridge.zig`",
    "- `scripts/zigux/kconfig/confdata_bridge.zig`",
    "- `scripts/zigux/zig-toolchain-policy.json`",
    "- `zigux/Makefile`",
    "- `zigux/tests/fixtures/phase2_tool_manifest.json`",
    "- `zigux/tests/fixtures/phase2_artifact_tools_manifest.json`",
    "- `zigux/tests/fixtures/kconfig_bridge/conf_manifest.json`",
    "- `zigux/tests/fixtures/kconfig_bridge/confdata_manifest.json`",
    "- `zigux/tests/fixtures/kconfig_bridge/cases.json`",
    "current directly readable Phase 2 toolchain-installer, closure-side, kbuild, kconfig bridge, make-wrapper, and artifact-support packet",
    "repeated authenticated reads on current `master` still return missing for `scripts/zigux/check-phase2-cross.py`, and `zigux/tests/fixtures/phase2_cross_targets.json`",
    "historical packet members until same-lane work rematerializes them on `master`",
    "keep the docs-root Phase 2 summary aligned to the shipped toolchain checker, the returned installer helper, the docs-shared-reminder checker, the required-make-route guard",
    "keep the pinned policy-only, installer self-test, and archive-integrity replays explicit without reviving missing direct cross-route proof text",
)

DOCS_README_FORBIDDEN_MARKERS = (
    "current directly readable Phase 2 toolchain, closure-side, kbuild, kconfig bridge, make-wrapper, and artifact-support packet",
    "repeated authenticated reads on current `master` still return missing for `scripts/zigux/install-zig.py`, `scripts/zigux/check-phase2-cross.py`, and `zigux/tests/fixtures/phase2_cross_targets.json`",
    "keep the pinned policy-only and archive-integrity replays explicit without reviving missing installer or direct cross-route proof text",
)

REVIEW_CHECKLIST_MARKERS = (
    "* if the change touches the shared Phase 2 toolchain packet, do `Documentation/zigux/README.md`",
    "`Documentation/zigux/phase2-toolchain-bootstrap-notes.md`",
    "`Documentation/zigux/review-checklist.md`",
    "`scripts/zigux/README.md`",
    "`scripts/zigux/check-zig-toolchain.py`",
    "`scripts/zigux/check-phase2-kbuild-routes.py`",
    "`scripts/zigux/check-phase2-kconfig-selftest-alignment.py`",
    "`scripts/zigux/check-phase2-tests-readme-alignment.py`",
    "`scripts/zigux/check-phase2-toolchain-pinning.py`",
    "`scripts/zigux/check-phase2-toolchain-pin-scope.py`",
    "`scripts/zigux/check-phase2-cross-selftest-alignment.py`",
    "`scripts/zigux/check-phase2-docs-shared-reminder.py`",
    "`scripts/zigux/check-phase2-required-make-routes.py`",
    "`scripts/zigux/kconfig/conf_bridge.zig`",
    "`scripts/zigux/kconfig/confdata_bridge.zig`",
    "`scripts/zigux/zig-toolchain-policy.json`",
    "`zigux/tests/fixtures/phase2_tool_manifest.json`",
    "`zigux/tests/fixtures/kconfig_bridge/conf_manifest.json`",
    "`zigux/tests/fixtures/kconfig_bridge/confdata_manifest.json`",
    "`zigux/tests/fixtures/kconfig_bridge/cases.json`",
    "current directly readable Phase 2 toolchain, kbuild, kconfig bridge, docs-shared-reminder, and required-make-route packet",
    "`Documentation/zigux/phase2-closure.md`",
    "`scripts/zigux/validate-phase2.py`",
    "`scripts/zigux/validate-phase2-closure.py`",
    "`zigux/Makefile`",
    "`scripts/zigux/install-zig.py`",
    "`zigux/tests/fixtures/phase2_artifact_tools_manifest.json`",
    "`python3 scripts/zigux/check-zig-toolchain.py --self-test`",
    "`python3 scripts/zigux/check-zig-toolchain.py --policy-only`",
    "`python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing`",
    "`python3 scripts/zigux/install-zig.py --self-test`",
    "`python3 scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test`",
    "`make -C zigux phase2-toolchain`",
    "`make -C zigux phase2-validate`",
    "`make -C zigux phase2-tools`",
    "`make -C zigux phase2-kconfig`",
    "`make -C zigux phase2-cross`",
    "`make -C zigux phase2`",
    "current rematerialized Phase 2 closure-side, closure-validator, validation, toolchain-installer, artifact-support, and make-wrapper packet",
    "`scripts/zigux/check-phase2-cross.py`, `python3 scripts/zigux/check-phase2-cross.py --self-test`, `python3 scripts/zigux/check-phase2-cross.py`, and `zigux/tests/fixtures/phase2_cross_targets.json` stay framed as historical packet members rather than shipped current-`master` evidence",
)

REVIEW_CHECKLIST_FORBIDDEN_MARKERS = (
    "`scripts/zigux/install-zig.py`, `python3 scripts/zigux/install-zig.py --self-test`, `scripts/zigux/check-phase2-cross.py`, `python3 scripts/zigux/check-phase2-cross.py --self-test`, `python3 scripts/zigux/check-phase2-cross.py`, and `zigux/tests/fixtures/phase2_cross_targets.json` stay framed as historical packet members rather than shipped current-`master` evidence",
    "current rematerialized Phase 2 closure-side, closure-validator, validation, artifact-support, and make-wrapper packet",
)

SCRIPTS_README_MARKERS = (
    "## Phase 2",
    "- Phase 2 flow - the current scripts-root bridge packet stays reviewable through the live `conf_bridge` and `confdata_bridge` helper surfaces, the restored closure-side validator packet, the manifest-backed kconfig fixture roster, the shipped make-wrapper packet, and the surviving Phase 2 alignment guards instead of rebuilding the older installer and direct cross-route stack from paths that current `master` no longer serves",
    "`scripts/zigux/check-phase2-docs-shared-reminder.py`",
    "`scripts/zigux/check-phase2-required-make-routes.py`",
    "`zigux/Makefile`",
    "`make -C zigux phase2-toolchain`",
    "`make -C zigux phase2-tools`",
    "`make -C zigux phase2-kconfig`",
    "`make -C zigux phase2-cross`",
    "`make -C zigux phase2-validate`",
    "`make -C zigux phase2`",
    "`zigux/tests/fixtures/phase2_artifact_tools_manifest.json`",
    "`scripts/zigux/validate-phase2-closure.py`",
    "keep the shipped closure-side reminder, closure-validator, validator entrypoint, make-wrapper, and artifact-support packet explicit from the scripts root beside the surviving checker set",
    "repeated authenticated reads on current `master` still return missing for `scripts/zigux/install-zig.py`, `python3 scripts/zigux/install-zig.py --self-test`, `python3 scripts/zigux/check-phase2-cross.py --self-test`, `python3 scripts/zigux/check-phase2-cross.py`, and `zigux/tests/fixtures/phase2_cross_targets.json`",
    "treat those installer and direct cross-route names as historical packet members that need fresh re-materialization before they are reused here as direct current-`master` scripts-root evidence",
)

SCRIPTS_README_FORBIDDEN_MARKERS = (
    "repeated authenticated reads on current `master` still return missing for `scripts/zigux/validate-phase2-closure.py`, `scripts/zigux/install-zig.py`, `python3 scripts/zigux/install-zig.py --self-test`, `python3 scripts/zigux/check-phase2-cross.py --self-test`, `python3 scripts/zigux/check-phase2-cross.py`, `zigux/tests/fixtures/phase2_cross_targets.json`, `zigux/Makefile`, `make -C zigux phase2-toolchain`, `make -C zigux phase2-tools`, `make -C zigux phase2-kconfig`, `make -C zigux phase2-cross`, `make -C zigux phase2-validate`, and `make -C zigux phase2`",
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


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    docs_readme_text = read_text(resolve_path(root, DOCS_README))
    review_checklist_text = read_text(resolve_path(root, REVIEW_CHECKLIST))
    scripts_readme_text = read_text(resolve_path(root, SCRIPTS_README))
    issues.extend(
        collect_missing_markers(
            docs_readme_text,
            DOCS_README_MARKERS,
            "MISSING_DOCS_README_MARKERS",
        )
    )
    issues.extend(
        collect_forbidden_markers(
            docs_readme_text,
            DOCS_README_FORBIDDEN_MARKERS,
            "FORBIDDEN_DOCS_README_MARKERS",
        )
    )
    issues.extend(
        collect_missing_markers(
            review_checklist_text,
            REVIEW_CHECKLIST_MARKERS,
            "MISSING_REVIEW_CHECKLIST_MARKERS",
        )
    )
    issues.extend(
        collect_forbidden_markers(
            review_checklist_text,
            REVIEW_CHECKLIST_FORBIDDEN_MARKERS,
            "FORBIDDEN_REVIEW_CHECKLIST_MARKERS",
        )
    )
    issues.extend(
        collect_missing_markers(
            scripts_readme_text,
            SCRIPTS_README_MARKERS,
            "MISSING_SCRIPTS_README_MARKERS",
        )
    )
    issues.extend(
        collect_forbidden_markers(
            scripts_readme_text,
            SCRIPTS_README_FORBIDDEN_MARKERS,
            "FORBIDDEN_SCRIPTS_README_MARKERS",
        )
    )
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
    write_text(resolve_path(root, REVIEW_CHECKLIST), "\n".join(REVIEW_CHECKLIST_MARKERS) + "\n")
    write_text(resolve_path(root, SCRIPTS_README), "\n".join(SCRIPTS_README_MARKERS) + "\n")


def replace_once(text: str, marker: str, replacement: str = "") -> str:
    if marker not in text:
        raise AssertionError(f"marker not found: {marker}")
    return text.replace(marker, replacement, 1)


def run_self_test() -> int:
    checks_run = 0
    expected_case_count = (
        1
        + len(DOCS_README_MARKERS)
        + len(DOCS_README_FORBIDDEN_MARKERS)
        + len(REVIEW_CHECKLIST_MARKERS)
        + len(REVIEW_CHECKLIST_FORBIDDEN_MARKERS)
        + len(SCRIPTS_README_MARKERS)
        + len(SCRIPTS_README_FORBIDDEN_MARKERS)
        + 3
    )
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_docs_shared_reminder_") as tmp_dir:
        root = Path(tmp_dir)
        build_self_test_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        for marker in DOCS_README_MARKERS:
            build_self_test_root(root)
            path = resolve_path(root, DOCS_README)
            path.write_text(replace_once(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            issues = collect_issues(root)
            assert ("MISSING_DOCS_README_MARKERS", marker) in issues
            checks_run += 1

        for marker in DOCS_README_FORBIDDEN_MARKERS:
            build_self_test_root(root)
            path = resolve_path(root, DOCS_README)
            path.write_text(path.read_text(encoding="utf-8") + marker + "\n", encoding="utf-8")
            issues = collect_issues(root)
            assert ("FORBIDDEN_DOCS_README_MARKERS", marker) in issues
            checks_run += 1

        for marker in REVIEW_CHECKLIST_MARKERS:
            build_self_test_root(root)
            path = resolve_path(root, REVIEW_CHECKLIST)
            path.write_text(replace_once(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            issues = collect_issues(root)
            assert ("MISSING_REVIEW_CHECKLIST_MARKERS", marker) in issues
            checks_run += 1

        for marker in REVIEW_CHECKLIST_FORBIDDEN_MARKERS:
            build_self_test_root(root)
            path = resolve_path(root, REVIEW_CHECKLIST)
            path.write_text(path.read_text(encoding="utf-8") + marker + "\n", encoding="utf-8")
            issues = collect_issues(root)
            assert ("FORBIDDEN_REVIEW_CHECKLIST_MARKERS", marker) in issues
            checks_run += 1

        for marker in SCRIPTS_README_MARKERS:
            build_self_test_root(root)
            path = resolve_path(root, SCRIPTS_README)
            path.write_text(replace_once(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            issues = collect_issues(root)
            assert ("MISSING_SCRIPTS_README_MARKERS", marker) in issues
            checks_run += 1

        for marker in SCRIPTS_README_FORBIDDEN_MARKERS:
            build_self_test_root(root)
            path = resolve_path(root, SCRIPTS_README)
            path.write_text(path.read_text(encoding="utf-8") + marker + "\n", encoding="utf-8")
            issues = collect_issues(root)
            assert ("FORBIDDEN_SCRIPTS_README_MARKERS", marker) in issues
            checks_run += 1

        for rel_path in (DOCS_README, REVIEW_CHECKLIST, SCRIPTS_README):
            build_self_test_root(root)
            resolve_path(root, rel_path).unlink()
            try:
                collect_issues(root)
            except SystemExit as exc:
                assert "required file missing" in str(exc)
                assert str(resolve_path(root, rel_path)) in str(exc)
                checks_run += 1
            else:
                raise AssertionError(f"missing file did not abort: {rel_path}")

    assert checks_run == expected_case_count
    print("PHASE2_DOCS_SHARED_REMINDER_SELF_TEST=pass")
    print(f"PHASE2_DOCS_SHARED_REMINDER_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Keep the shared Phase 2 docs-root, checklist, and scripts-root reminder packet aligned to current repo reality."
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
    print(f"PHASE2_DOCS_SHARED_REMINDER_MARKER_COUNT={len(DOCS_README_MARKERS) + len(REVIEW_CHECKLIST_MARKERS) + len(SCRIPTS_README_MARKERS)}")
    print(
        "PHASE2_DOCS_SHARED_REMINDER_FORBIDDEN_MARKER_COUNT="
        f"{len(DOCS_README_FORBIDDEN_MARKERS) + len(REVIEW_CHECKLIST_FORBIDDEN_MARKERS) + len(SCRIPTS_README_FORBIDDEN_MARKERS)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())