#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
NOTE = ROOT / "Documentation" / "zigux" / "phase2-scripts-surface-reconciliation.md"

PRESENT_PATHS = (
    "scripts/zigux/README.md",
    "scripts/zigux/check-phase2-tests-readme-alignment.py",
    "scripts/zigux/check-phase2-cross-selftest-alignment.py",
    "scripts/zigux/check-phase2-kconfig-selftest-alignment.py",
    "scripts/zigux/check-phase2-kbuild-routes.py",
    "scripts/zigux/check-phase2-toolchain-pinning.py",
    "scripts/zigux/fixdep.zig",
    "scripts/zigux/kconfig/conf_bridge.zig",
)

MISSING_PATHS = (
    "Documentation/zigux/phase2-toolchain-bootstrap-notes.md",
    "Documentation/zigux/phase2-closure.md",
    "scripts/zigux/validate-phase2.py",
    "scripts/zigux/validate-phase2-closure.py",
    "scripts/zigux/check-phase2-cross.py",
    "scripts/zigux/check-zig-toolchain.py",
    "scripts/zigux/install-zig.py",
    "scripts/zigux/genksyms.zig",
    "scripts/zigux/genksyms_crc.zig",
    "scripts/zigux/mk_elfconfig.zig",
    "scripts/zigux/kconfig/confdata_bridge.zig",
    "zigux/Makefile",
    "zigux/tests/fixtures/phase2_cross_targets.json",
    "zigux/tests/fixtures/phase2_tool_manifest.json",
    "zigux/tests/fixtures/phase2_artifact_tools_manifest.json",
)

README_DRIFT_MARKERS = (
    "scripts/zigux/check-phase2-toolchain-pin-scope.py",
    "make -C zigux phase2-validate",
    "make -C zigux phase2-cross",
    "`make -C zigux phase2` routes as current Phase 2 scripts-root evidence",
)

REQUIRED_NOTE_MARKERS = (
    "# Phase 2 Scripts Surface Reconciliation",
    "## Present scripts-root packet",
    "## Current repo-reality gaps",
    "## Outstanding scripts-root README drift",
    "## Lane 25 boundary",
    "Treat those paths as active repo-reality gaps on current `master`, not as shipped scripts-root evidence.",
    "Keep that README drift framed as the next bounded Lane 25 follow-up instead of folding it back into this note as if the scripts-root summary were already reconciled.",
)

EXPECTED_SELF_TEST_CASE_COUNT = 59


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

    for marker in README_DRIFT_MARKERS:
        if marker not in note_text:
            issues.append(("MISSING_README_DRIFT_MARKERS", marker))

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
            "## Outstanding scripts-root README drift",
            "",
            "- `scripts/zigux/README.md` still presents `scripts/zigux/kconfig/confdata_bridge.zig`, `scripts/zigux/check-phase2-toolchain-pin-scope.py`, `scripts/zigux/validate-phase2.py`, `scripts/zigux/validate-phase2-closure.py`, `scripts/zigux/check-phase2-cross.py`, `zigux/Makefile`, and the Linux-style `make -C zigux phase2-validate`, `make -C zigux phase2-cross`, and `make -C zigux phase2` routes as current Phase 2 scripts-root evidence even though fresh current-master reads still miss those branch-local, closure-side, cross-matrix, and make-route surfaces.",
            "- Keep that README drift framed as the next bounded Lane 25 follow-up instead of folding it back into this note as if the scripts-root summary were already reconciled.",
            "",
            "## Lane 25 boundary",
            "",
            "Lane 25 should use this note to keep Phase 2 reminder work bounded to current-master truth until the separate closure, cross-target, tool-restoration, and scripts-root README reconciliation lanes land.",
            "",
        ]
    )
    return "\n".join(lines)


def build_self_test_root(root: Path) -> None:
    write_text(root / NOTE.relative_to(ROOT), build_note_text())
    for relative in PRESENT_PATHS:
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

        for marker in README_DRIFT_MARKERS:
            build_self_test_root(root)
            note_path = root / NOTE.relative_to(ROOT)
            note_path.write_text(
                replace_once(note_path.read_text(encoding="utf-8"), marker),
                encoding="utf-8",
            )
            issues = collect_issues(root)
            assert ("MISSING_README_DRIFT_MARKERS", marker) in issues
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
    print(f"PHASE2_SCRIPTS_SURFACE_README_DRIFT_COUNT={len(README_DRIFT_MARKERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
