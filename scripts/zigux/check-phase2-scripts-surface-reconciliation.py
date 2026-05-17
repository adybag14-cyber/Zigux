#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


NOTE_RELATIVE = Path("Documentation/zigux/phase2-scripts-surface-reconciliation.md")

PRESENT_PATHS = (
    "scripts/zigux/README.md",
    "scripts/zigux/check-zig-toolchain.py",
    "scripts/zigux/check-phase2-cross-selftest-alignment.py",
    "scripts/zigux/check-phase2-kconfig-selftest-alignment.py",
    "scripts/zigux/check-phase2-kbuild-routes.py",
    "scripts/zigux/check-phase2-tests-readme-alignment.py",
    "scripts/zigux/check-phase2-toolchain-pinning.py",
    "scripts/zigux/fixdep.zig",
    "scripts/zigux/kconfig/conf_bridge.zig",
    "scripts/zigux/kconfig/confdata_bridge.zig",
    "zigux/tests/fixtures/phase2_tool_manifest.json",
)

MISSING_PATHS = (
    "Documentation/zigux/phase2-toolchain-bootstrap-notes.md",
    "Documentation/zigux/phase2-closure.md",
    "scripts/zigux/validate-phase2.py",
    "scripts/zigux/validate-phase2-closure.py",
    "scripts/zigux/check-phase2-cross.py",
    "scripts/zigux/install-zig.py",
    "scripts/zigux/check-phase2-toolchain-pin-scope.py",
    "scripts/zigux/genksyms.zig",
    "scripts/zigux/genksyms_crc.zig",
    "scripts/zigux/mk_elfconfig.zig",
    "zigux/Makefile",
    "zigux/tests/fixtures/phase2_cross_targets.json",
    "zigux/tests/fixtures/phase2_artifact_tools_manifest.json",
)

REQUIRED_MARKERS = (
    "# Phase 2 Scripts Surface Reconciliation",
    "## Present scripts-root packet",
    "## Current repo-reality gaps",
    "## Shared reminder contract",
    "## Lane 25 boundary",
    "Treat those as the current directly readable Phase 2 scripts-root anchors on `master`.",
    "Treat those paths as active repo-reality gaps on current `master`, not as shipped scripts-root evidence.",
    "`Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, and `scripts/zigux/check-phase2-tests-readme-alignment.py` still need the same narrowing pass to match this present-versus-gap inventory, including `scripts/zigux/check-zig-toolchain.py` and `zigux/tests/fixtures/phase2_tool_manifest.json` as present anchors.",
    "`scripts/zigux/README.md` is already narrowed to the current direct packet on this branch and should stay aligned with `Documentation/zigux/phase2-scripts-surface-reconciliation.md` while the broader shared docs-root and tests-root reminder surfaces catch up.",
    "`Documentation/zigux/phase2-shared-reminder-gap.md` should stay explicit while `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, and `scripts/zigux/check-phase2-tests-readme-alignment.py` still encode the broader pre-narrowing Phase 2 packet.",
    "Keep the scripts-root reminder aligned with the live toolchain checker, the live kconfig bridge packet, and the surviving alignment guards instead of reintroducing the older closure-side validator stack before those direct paths return on `master`.",
    "Lane 25 should use this note to keep Phase 2 reminder work bounded to current-master truth until the remaining shared docs-root, review-checklist, tests-root, and checker surfaces are narrowed and the separate closure, cross-target, and tool-restoration lanes land.",
)


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def collect_issues(root: Path) -> list[tuple[str, str]]:
    note_text = read_text(root / NOTE_RELATIVE)
    issues: list[tuple[str, str]] = []

    for marker in REQUIRED_MARKERS:
        if marker not in note_text:
            issues.append(("MISSING_NOTE_MARKERS", marker))

    for relative in PRESENT_PATHS:
        if f"- `{relative}`\n" not in note_text:
            issues.append(("MISSING_PRESENT_NOTE_PATHS", relative))
        if not (root / relative).exists():
            issues.append(("MISSING_PRESENT_REPO_PATHS", relative))

    for relative in MISSING_PATHS:
        if f"- `{relative}`\n" not in note_text:
            issues.append(("MISSING_GAP_NOTE_PATHS", relative))
        if (root / relative).exists():
            issues.append(("UNEXPECTED_PRESENT_GAP_PATHS", relative))

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
    return """# Phase 2 Scripts Surface Reconciliation

This note records the current Phase 2 scripts-root packet that is directly readable on `master`.

## Present scripts-root packet

- `scripts/zigux/README.md`
- `scripts/zigux/check-zig-toolchain.py`
- `scripts/zigux/check-phase2-cross-selftest-alignment.py`
- `scripts/zigux/check-phase2-kconfig-selftest-alignment.py`
- `scripts/zigux/check-phase2-kbuild-routes.py`
- `scripts/zigux/check-phase2-tests-readme-alignment.py`
- `scripts/zigux/check-phase2-toolchain-pinning.py`
- `scripts/zigux/fixdep.zig`
- `scripts/zigux/kconfig/conf_bridge.zig`
- `scripts/zigux/kconfig/confdata_bridge.zig`
- `zigux/tests/fixtures/phase2_tool_manifest.json`

Treat those as the current directly readable Phase 2 scripts-root anchors on `master`.

## Current repo-reality gaps

- `Documentation/zigux/phase2-toolchain-bootstrap-notes.md`
- `Documentation/zigux/phase2-closure.md`
- `scripts/zigux/validate-phase2.py`
- `scripts/zigux/validate-phase2-closure.py`
- `scripts/zigux/check-phase2-cross.py`
- `scripts/zigux/install-zig.py`
- `scripts/zigux/check-phase2-toolchain-pin-scope.py`
- `scripts/zigux/genksyms.zig`
- `scripts/zigux/genksyms_crc.zig`
- `scripts/zigux/mk_elfconfig.zig`
- `zigux/Makefile`
- `zigux/tests/fixtures/phase2_cross_targets.json`
- `zigux/tests/fixtures/phase2_artifact_tools_manifest.json`

Treat those paths as active repo-reality gaps on current `master`, not as shipped scripts-root evidence.

## Shared reminder contract

- `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, and `scripts/zigux/check-phase2-tests-readme-alignment.py` still need the same narrowing pass to match this present-versus-gap inventory, including `scripts/zigux/check-zig-toolchain.py` and `zigux/tests/fixtures/phase2_tool_manifest.json` as present anchors.
- `scripts/zigux/README.md` is already narrowed to the current direct packet on this branch and should stay aligned with `Documentation/zigux/phase2-scripts-surface-reconciliation.md` while the broader shared docs-root and tests-root reminder surfaces catch up.
- `Documentation/zigux/phase2-shared-reminder-gap.md` should stay explicit while `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, and `scripts/zigux/check-phase2-tests-readme-alignment.py` still encode the broader pre-narrowing Phase 2 packet.
- Keep the scripts-root reminder aligned with the live toolchain checker, the live kconfig bridge packet, and the surviving alignment guards instead of reintroducing the older closure-side validator stack before those direct paths return on `master`.

## Lane 25 boundary

Lane 25 should use this note to keep Phase 2 reminder work bounded to current-master truth until the remaining shared docs-root, review-checklist, tests-root, and checker surfaces are narrowed and the separate closure, cross-target, and tool-restoration lanes land.
"""


def build_self_test_root(root: Path) -> None:
    write_text(root / NOTE_RELATIVE, build_note_text())
    for relative in PRESENT_PATHS:
        write_text(root / relative, "# present\n")


def replace_once(text: str, marker: str, replacement: str = "") -> str:
    if marker not in text:
        raise AssertionError(f"marker not found: {marker}")
    return text.replace(marker, replacement, 1)


def run_self_test() -> int:
    checks_run = 0
    expected_case_count = (
        1
        + len(REQUIRED_MARKERS)
        + len(PRESENT_PATHS)
        + len(PRESENT_PATHS)
        + len(MISSING_PATHS)
        + len(MISSING_PATHS)
        + 1
    )

    with tempfile.TemporaryDirectory(prefix="zigux_p2_scripts_surface_") as tmp_dir:
        root = Path(tmp_dir)

        build_self_test_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        for marker in REQUIRED_MARKERS:
            build_self_test_root(root)
            note_path = root / NOTE_RELATIVE
            note_path.write_text(
                replace_once(note_path.read_text(encoding="utf-8"), marker),
                encoding="utf-8",
            )
            issues = collect_issues(root)
            assert ("MISSING_NOTE_MARKERS", marker) in issues
            checks_run += 1

        for relative in PRESENT_PATHS:
            build_self_test_root(root)
            note_path = root / NOTE_RELATIVE
            note_path.write_text(
                replace_once(note_path.read_text(encoding="utf-8"), f"- `{relative}`\n"),
                encoding="utf-8",
            )
            issues = collect_issues(root)
            assert ("MISSING_PRESENT_NOTE_PATHS", relative) in issues
            checks_run += 1

        for relative in PRESENT_PATHS:
            if relative == NOTE_RELATIVE.as_posix():
                continue
            build_self_test_root(root)
            (root / relative).unlink()
            issues = collect_issues(root)
            assert ("MISSING_PRESENT_REPO_PATHS", relative) in issues
            checks_run += 1

        for relative in MISSING_PATHS:
            build_self_test_root(root)
            note_path = root / NOTE_RELATIVE
            note_path.write_text(
                replace_once(note_path.read_text(encoding="utf-8"), f"- `{relative}`\n"),
                encoding="utf-8",
            )
            issues = collect_issues(root)
            assert ("MISSING_GAP_NOTE_PATHS", relative) in issues
            checks_run += 1

        for relative in MISSING_PATHS:
            build_self_test_root(root)
            write_text(root / relative, "# should stay missing\n")
            issues = collect_issues(root)
            assert ("UNEXPECTED_PRESENT_GAP_PATHS", relative) in issues
            checks_run += 1

        build_self_test_root(root)
        (root / NOTE_RELATIVE).unlink()
        try:
            collect_issues(root)
        except SystemExit as exc:
            assert "required file missing" in str(exc)
            checks_run += 1
        else:
            raise AssertionError("missing note did not abort")

    assert checks_run == expected_case_count
    print("PHASE2_SCRIPTS_SURFACE_RECONCILIATION_SELF_TEST=pass")
    print(f"PHASE2_SCRIPTS_SURFACE_RECONCILIATION_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Keep the current-master Phase 2 scripts-surface reconciliation note honest."
    )
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="Repository root to inspect")
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
    print(f"PHASE2_SCRIPTS_SURFACE_MARKER_COUNT={len(REQUIRED_MARKERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
