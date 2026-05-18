#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NOTE_RELATIVE = Path("Documentation/zigux/phase2-scripts-surface-reconciliation.md")
README_RELATIVE = Path("scripts/zigux/README.md")

PRESENT_PATHS = (
    "scripts/zigux/README.md",
    "scripts/zigux/check-zig-toolchain.py",
    "scripts/zigux/check-phase2-kbuild-routes.py",
    "scripts/zigux/check-phase2-docs-shared-reminder.py",
    "scripts/zigux/check-phase2-kconfig-selftest-alignment.py",
    "scripts/zigux/check-phase2-tests-readme-alignment.py",
    "scripts/zigux/check-phase2-cross-selftest-alignment.py",
    "scripts/zigux/check-phase2-toolchain-pinning.py",
    "scripts/zigux/check-phase2-toolchain-pin-scope.py",
    "scripts/zigux/check-phase2-required-make-routes.py",
    "scripts/zigux/kconfig/conf_bridge.zig",
    "scripts/zigux/kconfig/confdata_bridge.zig",
    "Documentation/zigux/phase2-closure.md",
    "scripts/zigux/validate-phase2.py",
    "zigux/Makefile",
    "zigux/tests/fixtures/phase2_tool_manifest.json",
    "zigux/tests/fixtures/phase2_artifact_tools_manifest.json",
    "zigux/tests/fixtures/kconfig_bridge/conf_manifest.json",
    "zigux/tests/fixtures/kconfig_bridge/confdata_manifest.json",
    "zigux/tests/fixtures/kconfig_bridge/cases.json",
)

GAP_PATHS = (
    "scripts/zigux/validate-phase2-closure.py",
    "scripts/zigux/install-zig.py",
    "scripts/zigux/check-phase2-cross.py",
    "zigux/tests/fixtures/phase2_cross_targets.json",
)

NOTE_MARKERS = (
    "# Phase 2 Scripts Surface Reconciliation",
    "## Present scripts-root packet",
    "## Current repo-reality gaps",
    "## Shared reminder contract",
    "## Lane 25 boundary",
    "Treat those as the current directly readable Phase 2 scripts-root anchors on `master`.",
    "Treat those paths as active repo-reality gaps on current `master`, not as shipped scripts-root evidence.",
    "`Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, and `scripts/zigux/check-phase2-tests-readme-alignment.py` should keep the same narrowed packet visible from the docs root, checklist, tests root, and scripts root instead of rebuilding the older validator-first or installer-backed tranche.",
    "Keep the scripts-root reminder aligned with the live toolchain checker, the surviving kbuild and alignment guards, the kconfig bridge helper packet, the shipped closure-side validator entrypoint, and the required-make-route plus `zigux/Makefile` pair instead of reintroducing the missing closure-validator, installer, or direct cross-route packet as if it had already returned on `master`.",
    "Treat the adjacent bootstrap-note, shared-gap, and tests-root follow-up surfaces as separate same-lane review paths until they land, rather than folding those larger reminder packets back into this scripts-root sidecar.",
    "Lane 25 should use this note and its checker to keep the scripts-root Phase 2 reminder bounded to current-master truth while the remaining shared reminder surfaces land on their separate review paths.",
)

README_MARKERS = (
    "- Phase 2 flow - the current scripts-root bridge packet stays reviewable through the live `conf_bridge` and `confdata_bridge` helper surfaces, the manifest-backed kconfig fixture roster, the shipped make-wrapper packet, and the surviving Phase 2 alignment guards instead of rebuilding the older closure-side validator stack from paths that current `master` no longer serves",
    "- `scripts/zigux/check-zig-toolchain.py`, `scripts/zigux/check-phase2-kbuild-routes.py`, `scripts/zigux/check-phase2-docs-shared-reminder.py`, `scripts/zigux/check-phase2-kconfig-selftest-alignment.py`, `scripts/zigux/check-phase2-tests-readme-alignment.py`, `scripts/zigux/check-phase2-cross-selftest-alignment.py`, `scripts/zigux/check-phase2-toolchain-pinning.py`, `scripts/zigux/check-phase2-toolchain-pin-scope.py`, and `scripts/zigux/check-phase2-required-make-routes.py` remain the shipped Phase 2 toolchain, reminder, alignment, and required-make-route guards that survive on current `master`",
    "- `Documentation/zigux/phase2-closure.md`, `scripts/zigux/validate-phase2.py`, `zigux/Makefile`, `make -C zigux phase2-toolchain`, `make -C zigux phase2-tools`, `make -C zigux phase2-kconfig`, `make -C zigux phase2-cross`, `make -C zigux phase2-validate`, `make -C zigux phase2`, and `zigux/tests/fixtures/phase2_artifact_tools_manifest.json` keep the shipped closure-side reminder, validator entrypoint, make-wrapper, and artifact-support packet explicit from the scripts root beside the surviving checker set",
    "- repeated authenticated reads on current `master` still return missing for `scripts/zigux/validate-phase2-closure.py`, `scripts/zigux/install-zig.py`, `python3 scripts/zigux/install-zig.py --self-test`, `python3 scripts/zigux/check-phase2-cross.py --self-test`, `python3 scripts/zigux/check-phase2-cross.py`, and `zigux/tests/fixtures/phase2_cross_targets.json`, so treat those validator-first follow-through, installer, and direct cross-route names as historical packet members that need fresh re-materialization before they are reused here as direct current-`master` scripts-root evidence",
)

NOTE_TEMPLATE = """# Phase 2 Scripts Surface Reconciliation

This note records the current Phase 2 scripts-root packet that is directly readable on `master`.

## Present scripts-root packet

- `scripts/zigux/README.md`
- `scripts/zigux/check-zig-toolchain.py`
- `scripts/zigux/check-phase2-kbuild-routes.py`
- `scripts/zigux/check-phase2-docs-shared-reminder.py`
- `scripts/zigux/check-phase2-kconfig-selftest-alignment.py`
- `scripts/zigux/check-phase2-tests-readme-alignment.py`
- `scripts/zigux/check-phase2-cross-selftest-alignment.py`
- `scripts/zigux/check-phase2-toolchain-pinning.py`
- `scripts/zigux/check-phase2-toolchain-pin-scope.py`
- `scripts/zigux/check-phase2-required-make-routes.py`
- `scripts/zigux/kconfig/conf_bridge.zig`
- `scripts/zigux/kconfig/confdata_bridge.zig`
- `Documentation/zigux/phase2-closure.md`
- `scripts/zigux/validate-phase2.py`
- `zigux/Makefile`
- `zigux/tests/fixtures/phase2_tool_manifest.json`
- `zigux/tests/fixtures/phase2_artifact_tools_manifest.json`
- `zigux/tests/fixtures/kconfig_bridge/conf_manifest.json`
- `zigux/tests/fixtures/kconfig_bridge/confdata_manifest.json`
- `zigux/tests/fixtures/kconfig_bridge/cases.json`

Treat those as the current directly readable Phase 2 scripts-root anchors on `master`.

## Current repo-reality gaps

- `scripts/zigux/validate-phase2-closure.py`
- `scripts/zigux/install-zig.py`
- `scripts/zigux/check-phase2-cross.py`
- `zigux/tests/fixtures/phase2_cross_targets.json`

Treat those paths as active repo-reality gaps on current `master`, not as shipped scripts-root evidence.

## Shared reminder contract

- `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, and `scripts/zigux/check-phase2-tests-readme-alignment.py` should keep the same narrowed packet visible from the docs root, checklist, tests root, and scripts root instead of rebuilding the older validator-first or installer-backed tranche.
- Keep the scripts-root reminder aligned with the live toolchain checker, the surviving kbuild and alignment guards, the kconfig bridge helper packet, the shipped closure-side validator entrypoint, and the required-make-route plus `zigux/Makefile` pair instead of reintroducing the missing closure-validator, installer, or direct cross-route packet as if it had already returned on `master`.
- Treat the adjacent bootstrap-note, shared-gap, and tests-root follow-up surfaces as separate same-lane review paths until they land, rather than folding those larger reminder packets back into this scripts-root sidecar.

## Lane 25 boundary

Lane 25 should use this note and its checker to keep the scripts-root Phase 2 reminder bounded to current-master truth while the remaining shared reminder surfaces land on their separate review paths.
"""


def resolve(root: Path, relative: Path) -> Path:
    return root / relative


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    note_text = read_text(resolve(root, NOTE_RELATIVE))
    readme_text = read_text(resolve(root, README_RELATIVE))

    for marker in NOTE_MARKERS:
        if marker not in note_text:
            issues.append(("MISSING_NOTE_MARKERS", marker))

    for marker in README_MARKERS:
        if marker not in readme_text:
            issues.append(("MISSING_README_MARKERS", marker))

    for relative in PRESENT_PATHS:
        if f"- `{relative}`\n" not in note_text:
            issues.append(("MISSING_PRESENT_NOTE_PATHS", relative))
        if not resolve(root, Path(relative)).exists():
            issues.append(("MISSING_PRESENT_REPO_PATHS", relative))

    for relative in GAP_PATHS:
        if f"- `{relative}`\n" not in note_text:
            issues.append(("MISSING_GAP_NOTE_PATHS", relative))
        if resolve(root, Path(relative)).exists():
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


def build_self_test_root(root: Path) -> None:
    write_text(resolve(root, NOTE_RELATIVE), NOTE_TEMPLATE)
    write_text(resolve(root, README_RELATIVE), "\n".join(README_MARKERS) + "\n")

    for relative in PRESENT_PATHS:
        if relative in (NOTE_RELATIVE.as_posix(), README_RELATIVE.as_posix()):
            continue
        write_text(resolve(root, Path(relative)), "present\n")


def replace_once(text: str, marker: str, replacement: str = "") -> str:
    if marker not in text:
        raise AssertionError(marker)
    return text.replace(marker, replacement, 1)


def run_self_test() -> int:
    checks = 0
    expected = (
        1
        + len(NOTE_MARKERS)
        + len(README_MARKERS)
        + len(PRESENT_PATHS)
        + (len(PRESENT_PATHS) - 1)
        + len(GAP_PATHS)
        + len(GAP_PATHS)
        + 2
    )

    with tempfile.TemporaryDirectory(prefix="lane25_scripts_surface_") as tmp:
        root = Path(tmp)
        build_self_test_root(root)
        assert collect_issues(root) == []
        checks += 1

        for marker in NOTE_MARKERS:
            build_self_test_root(root)
            path = resolve(root, NOTE_RELATIVE)
            write_text(path, replace_once(read_text(path), marker))
            assert ("MISSING_NOTE_MARKERS", marker) in collect_issues(root)
            checks += 1

        for marker in README_MARKERS:
            build_self_test_root(root)
            path = resolve(root, README_RELATIVE)
            write_text(path, replace_once(read_text(path), marker))
            assert ("MISSING_README_MARKERS", marker) in collect_issues(root)
            checks += 1

        for relative in PRESENT_PATHS:
            build_self_test_root(root)
            path = resolve(root, NOTE_RELATIVE)
            write_text(path, replace_once(read_text(path), f"- `{relative}`\n"))
            assert ("MISSING_PRESENT_NOTE_PATHS", relative) in collect_issues(root)
            checks += 1

        for relative in PRESENT_PATHS:
            if relative in (NOTE_RELATIVE.as_posix(), README_RELATIVE.as_posix()):
                continue
            build_self_test_root(root)
            resolve(root, Path(relative)).unlink()
            assert ("MISSING_PRESENT_REPO_PATHS", relative) in collect_issues(root)
            checks += 1

        for relative in GAP_PATHS:
            build_self_test_root(root)
            path = resolve(root, NOTE_RELATIVE)
            write_text(path, replace_once(read_text(path), f"- `{relative}`\n"))
            assert ("MISSING_GAP_NOTE_PATHS", relative) in collect_issues(root)
            checks += 1

        for relative in GAP_PATHS:
            build_self_test_root(root)
            write_text(resolve(root, Path(relative)), "should stay missing\n")
            assert ("UNEXPECTED_PRESENT_GAP_PATHS", relative) in collect_issues(root)
            checks += 1

        for relative in (NOTE_RELATIVE, README_RELATIVE):
            build_self_test_root(root)
            resolve(root, relative).unlink()
            try:
                collect_issues(root)
            except SystemExit as exc:
                assert "required file missing" in str(exc)
                checks += 1
            else:
                raise AssertionError(relative)

    assert checks == expected, (checks, expected)
    print("PHASE2_SCRIPTS_SURFACE_RECONCILIATION_SELF_TEST=pass")
    print(f"PHASE2_SCRIPTS_SURFACE_RECONCILIATION_SELF_TEST_CASE_COUNT={checks}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Keep the current-master Phase 2 scripts-surface reconciliation note honest."
    )
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root)
    if issues:
        return emit_issues(issues)

    print("PHASE2_SCRIPTS_SURFACE_RECONCILIATION=pass")
    print(f"PHASE2_SCRIPTS_SURFACE_PRESENT_COUNT={len(PRESENT_PATHS)}")
    print(f"PHASE2_SCRIPTS_SURFACE_GAP_COUNT={len(GAP_PATHS)}")
    print(f"PHASE2_SCRIPTS_SURFACE_MARKER_COUNT={len(NOTE_MARKERS) + len(README_MARKERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
