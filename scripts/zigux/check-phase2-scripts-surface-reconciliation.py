#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
NOTE = ROOT / "Documentation" / "zigux" / "phase2-scripts-surface-reconciliation.md"
README = ROOT / "scripts" / "zigux" / "README.md"

PRESENT_PATHS = (
    "scripts/zigux/README.md",
    "scripts/zigux/check-phase2-tests-readme-alignment.py",
    "scripts/zigux/check-phase2-cross-selftest-alignment.py",
    "scripts/zigux/check-phase2-kconfig-selftest-alignment.py",
    "scripts/zigux/check-phase2-kbuild-routes.py",
    "scripts/zigux/check-phase2-toolchain-pinning.py",
    "scripts/zigux/fixdep.zig",
    "scripts/zigux/kconfig/conf_bridge.zig",
    "scripts/zigux/kconfig/confdata_bridge.zig",
)

MISSING_PATHS = (
    "Documentation/zigux/phase2-toolchain-bootstrap-notes.md",
    "Documentation/zigux/phase2-closure.md",
    "scripts/zigux/validate-phase2.py",
    "scripts/zigux/validate-phase2-closure.py",
    "scripts/zigux/check-phase2-cross.py",
    "scripts/zigux/check-zig-toolchain.py",
    "scripts/zigux/install-zig.py",
    "scripts/zigux/check-phase2-toolchain-pin-scope.py",
    "scripts/zigux/genksyms.zig",
    "scripts/zigux/genksyms_crc.zig",
    "scripts/zigux/mk_elfconfig.zig",
    "zigux/Makefile",
    "zigux/tests/fixtures/phase2_cross_targets.json",
    "zigux/tests/fixtures/phase2_tool_manifest.json",
    "zigux/tests/fixtures/phase2_artifact_tools_manifest.json",
)

REQUIRED_NOTE_MARKERS = (
    "# Phase 2 Scripts Surface Reconciliation",
    "## Present scripts-root packet",
    "## Current repo-reality gaps",
    "## Shared reminder contract",
    "## Lane 25 boundary",
    "These are the current directly readable Phase 2 scripts-root anchors on `master`.",
    "Treat those paths as active repo-reality gaps on current `master`, not as shipped scripts-root evidence.",
    "`Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, and `scripts/zigux/README.md` should match the same present-versus-gap inventory tracked here, including `scripts/zigux/kconfig/confdata_bridge.zig` as a present anchor and the still-missing closure-side, cross-matrix, toolchain-helper, genksyms, and make-route surfaces as repo-reality gaps.",
    "`Documentation/zigux/README.md` and `Documentation/zigux/review-checklist.md` still need that same narrowing pass before Lane 25 is fully closed, so treat those two shared reminder surfaces as remaining same-lane drift instead of proof that the older closure-side, cross-matrix, or make-route packet has returned on `master`.",
)

REQUIRED_README_MARKERS = (
    "the current scripts-root bridge packet stays reviewable through the live `conf_bridge` and `confdata_bridge` helper surfaces",
    "`Documentation/zigux/phase2-scripts-surface-reconciliation.md`",
    "`scripts/zigux/check-phase2-tests-readme-alignment.py`",
    "`scripts/zigux/check-phase2-cross-selftest-alignment.py`",
    "`scripts/zigux/check-phase2-kconfig-selftest-alignment.py`",
    "`scripts/zigux/check-phase2-kbuild-routes.py`",
    "`scripts/zigux/check-phase2-toolchain-pinning.py`",
    "`scripts/zigux/fixdep.zig`",
    "`scripts/zigux/kconfig/conf_bridge.zig`",
    "`scripts/zigux/kconfig/confdata_bridge.zig`",
    "repeated authenticated reads on current `master` still return missing for",
    "`scripts/zigux/check-phase2-toolchain-pin-scope.py`",
    "`scripts/zigux/check-zig-toolchain.py`",
    "`scripts/zigux/install-zig.py`",
    "`scripts/zigux/genksyms.zig`",
    "`scripts/zigux/genksyms_crc.zig`",
    "`scripts/zigux/mk_elfconfig.zig`",
    "`zigux/Makefile`",
    "repo-reality gaps that need fresh re-materialization before they are reused here as direct current-`master` scripts-root evidence",
)

EXPECTED_SELF_TEST_CASE_COUNT = 78


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def resolve(root: Path, relative: str) -> Path:
    return root / relative


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    note_text = read_text(root / NOTE.relative_to(ROOT))
    readme_text = read_text(root / README.relative_to(ROOT))

    for marker in REQUIRED_NOTE_MARKERS:
        if marker not in note_text:
            issues.append(("MISSING_NOTE_MARKERS", marker))

    for relative in PRESENT_PATHS:
        if f"- `{relative}`\n" not in note_text:
            issues.append(("MISSING_PRESENT_NOTE_PATHS", relative))
        if not resolve(root, relative).exists():
            issues.append(("MISSING_PRESENT_REPO_PATHS", relative))

    for relative in MISSING_PATHS:
        if f"- `{relative}`\n" not in note_text:
            issues.append(("MISSING_GAP_NOTE_PATHS", relative))
        if resolve(root, relative).exists():
            issues.append(("UNEXPECTED_PRESENT_GAP_PATHS", relative))

    for marker in REQUIRED_README_MARKERS:
        if marker not in readme_text:
            issues.append(("MISSING_README_MARKERS", marker))

    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)

    print("PHASE2_SCRIPTS_SURFACE_RECONCILIATION=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_note_text() -> str:
    lines = [
        "# Phase 2 Scripts Surface Reconciliation",
        "",
        "This note records the current scripts-root Phase 2 packet that is directly readable on `master`.",
        "",
        "## Present scripts-root packet",
        "",
    ]
    lines.extend(f"- `{path}`" for path in PRESENT_PATHS)
    lines.extend(
        [
            "",
            "These are the current directly readable Phase 2 scripts-root anchors on `master`.",
            "",
            "## Current repo-reality gaps",
            "",
        ]
    )
    lines.extend(f"- `{path}`" for path in MISSING_PATHS)
    lines.extend(
        [
            "",
            "Treat those paths as active repo-reality gaps on current `master`, not as shipped scripts-root evidence.",
            "",
            "## Shared reminder contract",
            "",
            "- `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, and `scripts/zigux/README.md` should match the same present-versus-gap inventory tracked here, including `scripts/zigux/kconfig/confdata_bridge.zig` as a present anchor and the still-missing closure-side, cross-matrix, toolchain-helper, genksyms, and make-route surfaces as repo-reality gaps.",
            "- Keep the scripts-root reminder aligned with the live kconfig bridge packet and the surviving alignment guards instead of reintroducing the older closure-side validator stack before those direct paths return on `master`.",
            "- `Documentation/zigux/README.md` and `Documentation/zigux/review-checklist.md` still need that same narrowing pass before Lane 25 is fully closed, so treat those two shared reminder surfaces as remaining same-lane drift instead of proof that the older closure-side, cross-matrix, or make-route packet has returned on `master`.",
            "",
            "## Lane 25 boundary",
            "",
            "Lane 25 should use this note to keep Phase 2 reminder work bounded to current-master truth, including the still-pending docs-root and review-checklist narrowing pass, until the separate closure, cross-target, and tool-restoration lanes land.",
            "",
        ]
    )
    return "\n".join(lines)


def build_readme_text() -> str:
    return "\n".join(
        [
            "# scripts/zigux",
            "",
            "## Phase 2",
            "",
            "- Phase 2 flow - the current scripts-root bridge packet stays reviewable through the live `conf_bridge` and `confdata_bridge` helper surfaces, the manifest-backed kconfig fixture roster, `Documentation/zigux/phase2-scripts-surface-reconciliation.md`, and the surviving Phase 2 alignment guards instead of rebuilding the older closure-side validator stack from paths that current `master` still does not serve",
            "- `scripts/zigux/fixdep.zig`, `scripts/zigux/kconfig/conf_bridge.zig`, `scripts/zigux/kconfig/confdata_bridge.zig`, `zigux/tests/fixtures/kconfig_bridge/conf_manifest.json`, `zigux/tests/fixtures/kconfig_bridge/confdata_manifest.json`, and `zigux/tests/fixtures/kconfig_bridge/cases.json` keep the current direct Zig tool anchor plus the conf-side and confdata-side bridge evidence packet explicit from the scripts root",
            "- `scripts/zigux/check-phase2-tests-readme-alignment.py`, `scripts/zigux/check-phase2-cross-selftest-alignment.py`, `scripts/zigux/check-phase2-kconfig-selftest-alignment.py`, `scripts/zigux/check-phase2-kbuild-routes.py`, and `scripts/zigux/check-phase2-toolchain-pinning.py` remain the shipped Phase 2 reminder and alignment guards that survive on current `master`",
            "- repeated authenticated reads on current `master` still return missing for `Documentation/zigux/phase2-toolchain-bootstrap-notes.md`, `Documentation/zigux/phase2-closure.md`, `scripts/zigux/validate-phase2.py`, `scripts/zigux/validate-phase2-closure.py`, `scripts/zigux/check-phase2-cross.py`, `scripts/zigux/check-zig-toolchain.py`, `scripts/zigux/install-zig.py`, `scripts/zigux/check-phase2-toolchain-pin-scope.py`, `scripts/zigux/genksyms.zig`, `scripts/zigux/genksyms_crc.zig`, `scripts/zigux/mk_elfconfig.zig`, `zigux/Makefile`, `zigux/tests/fixtures/phase2_cross_targets.json`, `zigux/tests/fixtures/phase2_tool_manifest.json`, and `zigux/tests/fixtures/phase2_artifact_tools_manifest.json`, so treat those closure-side, validator-first, cross-matrix, toolchain-helper, genksyms, and make-route names as repo-reality gaps that need fresh re-materialization before they are reused here as direct current-`master` scripts-root evidence",
            "- keep future scripts-root reminder updates keyed to `Documentation/zigux/phase2-scripts-surface-reconciliation.md` and the live kconfig bridge fixture roster rather than the older closure-side packet",
            "",
        ]
    )


def build_self_test_root(root: Path) -> None:
    write_text(root / NOTE.relative_to(ROOT), build_note_text())
    write_text(root / README.relative_to(ROOT), build_readme_text())
    for relative in PRESENT_PATHS:
        if relative == README.relative_to(ROOT).as_posix():
            continue
        write_text(resolve(root, relative), "# present\n")


def replace_once(text: str, marker: str, replacement: str = "") -> str:
    if marker not in text:
        raise AssertionError(f"marker not found: {marker}")
    return text.replace(marker, replacement, 1)


def run_self_test() -> int:
    checks_run = 0
    with tempfile.TemporaryDirectory(prefix="zigux_p2_scripts_surface_") as tmp_dir:
        root = Path(tmp_dir)

        build_self_test_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        for marker in REQUIRED_NOTE_MARKERS:
            build_self_test_root(root)
            note_path = root / NOTE.relative_to(ROOT)
            note_path.write_text(
                replace_once(note_path.read_text(encoding="utf-8"), marker),
                encoding="utf-8",
            )
            issues = collect_issues(root)
            assert ("MISSING_NOTE_MARKERS", marker) in issues
            checks_run += 1

        for relative in PRESENT_PATHS:
            build_self_test_root(root)
            note_path = root / NOTE.relative_to(ROOT)
            note_path.write_text(
                replace_once(note_path.read_text(encoding="utf-8"), f"- `{relative}`\n"),
                encoding="utf-8",
            )
            issues = collect_issues(root)
            assert ("MISSING_PRESENT_NOTE_PATHS", relative) in issues
            checks_run += 1

        for relative in PRESENT_PATHS:
            if relative == README.relative_to(ROOT).as_posix():
                continue
            build_self_test_root(root)
            resolve(root, relative).unlink()
            issues = collect_issues(root)
            assert ("MISSING_PRESENT_REPO_PATHS", relative) in issues
            checks_run += 1

        for relative in MISSING_PATHS:
            build_self_test_root(root)
            note_path = root / NOTE.relative_to(ROOT)
            note_path.write_text(
                replace_once(note_path.read_text(encoding="utf-8"), f"- `{relative}`\n"),
                encoding="utf-8",
            )
            issues = collect_issues(root)
            assert ("MISSING_GAP_NOTE_PATHS", relative) in issues
            checks_run += 1

        for relative in MISSING_PATHS:
            build_self_test_root(root)
            write_text(resolve(root, relative), "# should stay missing\n")
            issues = collect_issues(root)
            assert ("UNEXPECTED_PRESENT_GAP_PATHS", relative) in issues
            checks_run += 1

        for marker in REQUIRED_README_MARKERS:
            build_self_test_root(root)
            readme_path = root / README.relative_to(ROOT)
            readme_path.write_text(
                readme_path.read_text(encoding="utf-8").replace(marker, ""),
                encoding="utf-8",
            )
            issues = collect_issues(root)
            assert ("MISSING_README_MARKERS", marker) in issues
            checks_run += 1

        build_self_test_root(root)
        (root / NOTE.relative_to(ROOT)).unlink()
        try:
            collect_issues(root)
        except SystemExit as exc:
            assert "required file missing" in str(exc)
            checks_run += 1
        else:
            raise AssertionError("missing note did not abort")

        build_self_test_root(root)
        (root / README.relative_to(ROOT)).unlink()
        try:
            collect_issues(root)
        except SystemExit as exc:
            assert "required file missing" in str(exc)
            checks_run += 1
        else:
            raise AssertionError("missing readme did not abort")

    assert checks_run == EXPECTED_SELF_TEST_CASE_COUNT
    print("PHASE2_SCRIPTS_SURFACE_RECONCILIATION_SELF_TEST=pass")
    print(f"PHASE2_SCRIPTS_SURFACE_RECONCILIATION_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Keep the current-master-safe Phase 2 scripts-surface reconciliation note honest."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root)
    if issues:
        return emit_issues(issues)

    print("PHASE2_SCRIPTS_SURFACE_RECONCILIATION=pass")
    print(f"PHASE2_SCRIPTS_SURFACE_PRESENT_COUNT={len(PRESENT_PATHS)}")
    print(f"PHASE2_SCRIPTS_SURFACE_GAP_COUNT={len(MISSING_PATHS)}")
    print(f"PHASE2_SCRIPTS_SURFACE_README_MARKER_COUNT={len(REQUIRED_README_MARKERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
