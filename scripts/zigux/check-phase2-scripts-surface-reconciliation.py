#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
NOTE_RELATIVE = Path("Documentation/zigux/phase2-scripts-surface-reconciliation.md")
README_RELATIVE = Path("scripts/zigux/README.md")
BOOTSTRAP_NOTE_RELATIVE = Path("Documentation/zigux/phase2-toolchain-bootstrap-notes.md")
CLOSURE_NOTE_RELATIVE = Path("Documentation/zigux/phase2-closure.md")
MAKEFILE_RELATIVE = Path("zigux/Makefile")
MANIFEST_RELATIVE = Path("zigux/tests/fixtures/phase2_tool_manifest.json")

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
    "scripts/zigux/validate-phase2-closure.py",
    "zigux/Makefile",
    "zigux/tests/fixtures/phase2_tool_manifest.json",
    "zigux/tests/fixtures/phase2_artifact_tools_manifest.json",
    "zigux/tests/fixtures/kconfig_bridge/conf_manifest.json",
    "zigux/tests/fixtures/kconfig_bridge/confdata_manifest.json",
    "zigux/tests/fixtures/kconfig_bridge/cases.json",
)

GAP_PATHS = (
    "scripts/zigux/install-zig.py",
    "scripts/zigux/check-phase2-cross.py",
    "zigux/tests/fixtures/phase2_cross_targets.json",
)

NOTE_MARKERS = (
    "# Phase 2 Scripts Surface Reconciliation",
    "## Directly readable scripts-root anchors",
    "## Remaining repo-reality gaps",
    "## Current aligned packet",
    "## Lane 25 boundary",
    "Treat those as the current directly readable Phase 2 scripts-root anchors on `master`.",
    "Treat those paths as the remaining repo-reality gaps on current `master`, not as shipped Phase 2 scripts-root evidence.",
    "`scripts/zigux/README.md`, `Documentation/zigux/phase2-toolchain-bootstrap-notes.md`, `zigux/tests/fixtures/phase2_tool_manifest.json`, `Documentation/zigux/phase2-closure.md`, and `zigux/Makefile` now all keep `scripts/zigux/validate-phase2-closure.py` inside the present Phase 2 packet instead of classifying it as missing.",
    "The live reminder surfaces keep only `scripts/zigux/install-zig.py`, `scripts/zigux/check-phase2-cross.py`, and `zigux/tests/fixtures/phase2_cross_targets.json` in repo-reality-gap wording.",
    "Keep this scripts-surface sidecar focused on fail-closing that aligned scripts-root packet while the broader artifact-diff note and the other Lane 25 sidecars keep their separate surfaces.",
    "Do not treat the remaining installer or direct cross-route companions as returned until current `master` materializes them.",
    "Lane 25 should use this note and its checker to keep the present scripts-root, bootstrap-note, manifest, closure-side, and make-wrapper packet aligned around the restored closure validator without reopening the broader shared docs or artifact-diff surfaces.",
)

NOTE_FORBIDDEN_MARKERS = (
    "## Current reminder drift",
    "`scripts/zigux/README.md`, `Documentation/zigux/phase2-toolchain-bootstrap-notes.md`, and `zigux/tests/fixtures/phase2_tool_manifest.json` still classify `scripts/zigux/validate-phase2-closure.py` as a missing validator-first companion even though current `master` now directly serves that file.",
    "Keep this scripts-surface sidecar focused on that reopened reminder drift until the scripts-root, bootstrap-note, and manifest-root surfaces catch up to the restored closure validator.",
)

README_MARKERS = (
    "- Phase 2 flow - the current scripts-root bridge packet stays reviewable through the live `conf_bridge` and `confdata_bridge` helper surfaces, the restored closure-side validator packet, the manifest-backed kconfig fixture roster, the shipped make-wrapper packet, and the surviving Phase 2 alignment guards instead of rebuilding the older installer and direct cross-route stack from paths that current `master` no longer serves",
    "- `scripts/zigux/check-zig-toolchain.py`, `scripts/zigux/check-phase2-kbuild-routes.py`, `scripts/zigux/check-phase2-docs-shared-reminder.py`, `scripts/zigux/check-phase2-kconfig-selftest-alignment.py`, `scripts/zigux/check-phase2-tests-readme-alignment.py`, `scripts/zigux/check-phase2-cross-selftest-alignment.py`, `scripts/zigux/check-phase2-toolchain-pinning.py`, `scripts/zigux/check-phase2-toolchain-pin-scope.py`, and `scripts/zigux/check-phase2-required-make-routes.py` remain the shipped Phase 2 toolchain, reminder, alignment, and required-make-route guards that survive on current `master`",
    "- `Documentation/zigux/phase2-closure.md`, `scripts/zigux/validate-phase2.py`, `scripts/zigux/validate-phase2-closure.py`, `zigux/Makefile`, `make -C zigux phase2-toolchain`, `make -C zigux phase2-tools`, `make -C zigux phase2-kconfig`, `make -C zigux phase2-cross`, `make -C zigux phase2-validate`, `make -C zigux phase2`, and `zigux/tests/fixtures/phase2_artifact_tools_manifest.json` keep the shipped closure-side reminder, closure-validator, validator entrypoint, make-wrapper, and artifact-support packet explicit from the scripts root beside the surviving checker set",
    "- repeated authenticated reads on current `master` still return missing for `scripts/zigux/install-zig.py`, `python3 scripts/zigux/install-zig.py --self-test`, `python3 scripts/zigux/check-phase2-cross.py --self-test`, `python3 scripts/zigux/check-phase2-cross.py`, and `zigux/tests/fixtures/phase2_cross_targets.json`, so treat those installer and direct cross-route names as historical packet members that need fresh re-materialization before they are reused here as direct current-`master` scripts-root evidence",
)

README_FORBIDDEN_MARKERS = (
    "- `Documentation/zigux/phase2-closure.md`, `scripts/zigux/validate-phase2.py`, `zigux/Makefile`, `make -C zigux phase2-toolchain`, `make -C zigux phase2-tools`, `make -C zigux phase2-kconfig`, `make -C zigux phase2-cross`, `make -C zigux phase2-validate`, `make -C zigux phase2`, and `zigux/tests/fixtures/phase2_artifact_tools_manifest.json` keep the shipped closure-side reminder, validator entrypoint, make-wrapper, and artifact-support packet explicit from the scripts root beside the surviving checker set",
    "- repeated authenticated reads on current `master` still return missing for `scripts/zigux/validate-phase2-closure.py`, `scripts/zigux/install-zig.py`, `python3 scripts/zigux/install-zig.py --self-test`, `python3 scripts/zigux/check-phase2-cross.py --self-test`, `python3 scripts/zigux/check-phase2-cross.py`, and `zigux/tests/fixtures/phase2_cross_targets.json`, so treat those validator-first follow-through, installer, and direct cross-route names as historical packet members that need fresh re-materialization before they are reused here as direct current-`master` scripts-root evidence",
)

BOOTSTRAP_MARKERS = (
    "- `Documentation/zigux/phase2-closure.md`, `scripts/zigux/validate-phase2.py`, `scripts/zigux/validate-phase2-closure.py`, `zigux/Makefile`, `zigux/tests/README.md`, `scripts/zigux/kconfig/conf_bridge.zig`, `scripts/zigux/kconfig/confdata_bridge.zig`, `zigux/tests/fixtures/phase2_tool_manifest.json`, `zigux/tests/fixtures/phase2_artifact_tools_manifest.json`, and the `zigux/tests/fixtures/kconfig_bridge/` manifest roster keep the bounded closure-side, closure-validator, validator-entrypoint, tests-facing, toolchain, fixture-backed artifact-diff support, and bridge packet reviewable without widening back into older installer or direct cross-route claims.",
    "- Repeated authenticated reads on current `master` still return missing for `scripts/zigux/install-zig.py`, `scripts/zigux/check-phase2-cross.py`, and `zigux/tests/fixtures/phase2_cross_targets.json`.",
    "- Treat the absent installer and direct cross-route names as historical packet members until same-lane work rematerializes them on `master`.",
)

BOOTSTRAP_FORBIDDEN_MARKERS = (
    "- `Documentation/zigux/phase2-closure.md`, `scripts/zigux/validate-phase2.py`, `zigux/Makefile`, `zigux/tests/README.md`, `scripts/zigux/kconfig/conf_bridge.zig`, `scripts/zigux/kconfig/confdata_bridge.zig`, `zigux/tests/fixtures/phase2_tool_manifest.json`, `zigux/tests/fixtures/phase2_artifact_tools_manifest.json`, and the `zigux/tests/fixtures/kconfig_bridge/` manifest roster keep the bounded closure-side, validator-entrypoint, tests-facing, toolchain, fixture-backed artifact-diff support, and bridge packet reviewable without widening back into older validator-first or direct cross-route claims.",
    "- Repeated authenticated reads on current `master` still return missing for `scripts/zigux/validate-phase2-closure.py`, `scripts/zigux/install-zig.py`, `scripts/zigux/check-phase2-cross.py`, and `zigux/tests/fixtures/phase2_cross_targets.json`.",
    "- Treat the absent validator-first, direct cross-route, and installer names as historical packet members until same-lane work rematerializes them on `master`.",
)

CLOSURE_MARKERS = (
    "`scripts/zigux/validate-phase2-closure.py`",
    "`python3 scripts/zigux/validate-phase2-closure.py --self-test`",
    "`python3 scripts/zigux/validate-phase2-closure.py`",
    "Restoring the dedicated closure validator closes one repo-reality gap inside the bounded tranche while keeping the remaining installer and direct cross-route companions explicitly parked.",
)

MAKEFILE_MARKERS = (
    "phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/validate-phase2-closure.py",
)

EXPECTED_MANIFEST_GAPS = [
    "scripts/zigux/install-zig.py",
    "scripts/zigux/check-phase2-cross.py",
    "zigux/tests/fixtures/phase2_cross_targets.json",
]

EXPECTED_MANIFEST_NOTES_MARKER = (
    "Keep scripts/zigux/validate-phase2-closure.py out of the repo-reality-gap list because the closure validator is directly readable on current master and the closure-side packet depends on it as a live validation surface."
)

MANIFEST_FORBIDDEN_GAP = "scripts/zigux/validate-phase2-closure.py"

NOTE_TEMPLATE = """# Phase 2 Scripts Surface Reconciliation

This note records the current Phase 2 scripts-root packet that Lane 25 keeps aligned on `master`.

## Directly readable scripts-root anchors

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
- `scripts/zigux/validate-phase2-closure.py`
- `zigux/Makefile`
- `zigux/tests/fixtures/phase2_tool_manifest.json`
- `zigux/tests/fixtures/phase2_artifact_tools_manifest.json`
- `zigux/tests/fixtures/kconfig_bridge/conf_manifest.json`
- `zigux/tests/fixtures/kconfig_bridge/confdata_manifest.json`
- `zigux/tests/fixtures/kconfig_bridge/cases.json`

Treat those as the current directly readable Phase 2 scripts-root anchors on `master`.

## Remaining repo-reality gaps

- `scripts/zigux/install-zig.py`
- `scripts/zigux/check-phase2-cross.py`
- `zigux/tests/fixtures/phase2_cross_targets.json`

Treat those paths as the remaining repo-reality gaps on current `master`, not as shipped Phase 2 scripts-root evidence.

## Current aligned packet

- `scripts/zigux/README.md`, `Documentation/zigux/phase2-toolchain-bootstrap-notes.md`, `zigux/tests/fixtures/phase2_tool_manifest.json`, `Documentation/zigux/phase2-closure.md`, and `zigux/Makefile` now all keep `scripts/zigux/validate-phase2-closure.py` inside the present Phase 2 packet instead of classifying it as missing.
- The live reminder surfaces keep only `scripts/zigux/install-zig.py`, `scripts/zigux/check-phase2-cross.py`, and `zigux/tests/fixtures/phase2_cross_targets.json` in repo-reality-gap wording.
- Keep this scripts-surface sidecar focused on fail-closing that aligned scripts-root packet while the broader artifact-diff note and the other Lane 25 sidecars keep their separate surfaces.
- Do not treat the remaining installer or direct cross-route companions as returned until current `master` materializes them.

## Lane 25 boundary

Lane 25 should use this note and its checker to keep the present scripts-root, bootstrap-note, manifest, closure-side, and make-wrapper packet aligned around the restored closure validator without reopening the broader shared docs or artifact-diff surfaces.
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


def collect_missing_markers(text: str, markers: tuple[str, ...], code: str) -> list[tuple[str, str]]:
    return [(code, marker) for marker in markers if marker not in text]


def collect_forbidden_markers(text: str, markers: tuple[str, ...], code: str) -> list[tuple[str, str]]:
    return [(code, marker) for marker in markers if marker in text]


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    note_text = read_text(resolve(root, NOTE_RELATIVE))
    readme_text = read_text(resolve(root, README_RELATIVE))
    bootstrap_text = read_text(resolve(root, BOOTSTRAP_NOTE_RELATIVE))
    closure_text = read_text(resolve(root, CLOSURE_NOTE_RELATIVE))
    makefile_text = read_text(resolve(root, MAKEFILE_RELATIVE))

    issues.extend(collect_missing_markers(note_text, NOTE_MARKERS, "MISSING_NOTE_MARKERS"))
    issues.extend(collect_forbidden_markers(note_text, NOTE_FORBIDDEN_MARKERS, "FORBIDDEN_NOTE_MARKERS"))
    issues.extend(collect_missing_markers(readme_text, README_MARKERS, "MISSING_README_MARKERS"))
    issues.extend(collect_forbidden_markers(readme_text, README_FORBIDDEN_MARKERS, "FORBIDDEN_README_MARKERS"))
    issues.extend(collect_missing_markers(bootstrap_text, BOOTSTRAP_MARKERS, "MISSING_BOOTSTRAP_MARKERS"))
    issues.extend(collect_forbidden_markers(bootstrap_text, BOOTSTRAP_FORBIDDEN_MARKERS, "FORBIDDEN_BOOTSTRAP_MARKERS"))
    issues.extend(collect_missing_markers(closure_text, CLOSURE_MARKERS, "MISSING_CLOSURE_MARKERS"))
    issues.extend(collect_missing_markers(makefile_text, MAKEFILE_MARKERS, "MISSING_MAKEFILE_MARKERS"))

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

    try:
        manifest = json.loads(read_text(resolve(root, MANIFEST_RELATIVE)))
    except json.JSONDecodeError as exc:
        issues.append(("INVALID_MANIFEST_JSON", exc.msg))
        return issues

    if not isinstance(manifest, dict):
        issues.append(("INVALID_MANIFEST_PAYLOAD", type(manifest).__name__))
        return issues

    gaps = manifest.get("repo_reality_gaps")
    if gaps != EXPECTED_MANIFEST_GAPS:
        issues.append(("MANIFEST_GAP_MISMATCH", f"actual={gaps!r}:expected={EXPECTED_MANIFEST_GAPS!r}"))
    elif MANIFEST_FORBIDDEN_GAP in gaps:
        issues.append(("FORBIDDEN_MANIFEST_GAP", MANIFEST_FORBIDDEN_GAP))

    notes = manifest.get("notes")
    if not isinstance(notes, list):
        issues.append(("INVALID_MANIFEST_NOTES", type(notes).__name__))
    else:
        if EXPECTED_MANIFEST_NOTES_MARKER not in notes:
            issues.append(("MISSING_MANIFEST_NOTES_MARKER", EXPECTED_MANIFEST_NOTES_MARKER))

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


def replace_once(text: str, marker: str, replacement: str = "") -> str:
    if marker not in text:
        raise AssertionError(marker)
    return text.replace(marker, replacement, 1)


def build_self_test_root(root: Path) -> None:
    write_text(resolve(root, NOTE_RELATIVE), NOTE_TEMPLATE)
    write_text(resolve(root, README_RELATIVE), "\n".join(README_MARKERS) + "\n")
    write_text(resolve(root, BOOTSTRAP_NOTE_RELATIVE), "\n".join(BOOTSTRAP_MARKERS) + "\n")
    write_text(resolve(root, CLOSURE_NOTE_RELATIVE), "\n".join(CLOSURE_MARKERS) + "\n")
    write_text(resolve(root, MAKEFILE_RELATIVE), "\n".join(MAKEFILE_MARKERS) + "\n")
    write_text(
        resolve(root, MANIFEST_RELATIVE),
        json.dumps(
            {
                "repo_reality_gaps": EXPECTED_MANIFEST_GAPS,
                "notes": [EXPECTED_MANIFEST_NOTES_MARKER],
            },
            indent=2,
        )
        + "\n",
    )

    for relative in PRESENT_PATHS:
        path = resolve(root, Path(relative))
        if path in (
            resolve(root, README_RELATIVE),
            resolve(root, BOOTSTRAP_NOTE_RELATIVE),
            resolve(root, CLOSURE_NOTE_RELATIVE),
            resolve(root, MAKEFILE_RELATIVE),
            resolve(root, MANIFEST_RELATIVE),
        ):
            continue
        write_text(path, "present\n")


def run_self_test() -> int:
    checks = 0
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

        for marker in NOTE_FORBIDDEN_MARKERS:
            build_self_test_root(root)
            path = resolve(root, NOTE_RELATIVE)
            write_text(path, read_text(path) + marker + "\n")
            assert ("FORBIDDEN_NOTE_MARKERS", marker) in collect_issues(root)
            checks += 1

        for marker in README_MARKERS:
            build_self_test_root(root)
            path = resolve(root, README_RELATIVE)
            write_text(path, replace_once(read_text(path), marker))
            assert ("MISSING_README_MARKERS", marker) in collect_issues(root)
            checks += 1

        for marker in README_FORBIDDEN_MARKERS:
            build_self_test_root(root)
            path = resolve(root, README_RELATIVE)
            write_text(path, read_text(path) + marker + "\n")
            assert ("FORBIDDEN_README_MARKERS", marker) in collect_issues(root)
            checks += 1

        for marker in BOOTSTRAP_MARKERS:
            build_self_test_root(root)
            path = resolve(root, BOOTSTRAP_NOTE_RELATIVE)
            write_text(path, replace_once(read_text(path), marker))
            assert ("MISSING_BOOTSTRAP_MARKERS", marker) in collect_issues(root)
            checks += 1

        for marker in BOOTSTRAP_FORBIDDEN_MARKERS:
            build_self_test_root(root)
            path = resolve(root, BOOTSTRAP_NOTE_RELATIVE)
            write_text(path, read_text(path) + marker + "\n")
            assert ("FORBIDDEN_BOOTSTRAP_MARKERS", marker) in collect_issues(root)
            checks += 1

        for marker in CLOSURE_MARKERS:
            build_self_test_root(root)
            path = resolve(root, CLOSURE_NOTE_RELATIVE)
            write_text(path, replace_once(read_text(path), marker))
            assert ("MISSING_CLOSURE_MARKERS", marker) in collect_issues(root)
            checks += 1

        for marker in MAKEFILE_MARKERS:
            build_self_test_root(root)
            path = resolve(root, MAKEFILE_RELATIVE)
            write_text(path, replace_once(read_text(path), marker))
            assert ("MISSING_MAKEFILE_MARKERS", marker) in collect_issues(root)
            checks += 1

        for relative in PRESENT_PATHS:
            build_self_test_root(root)
            path = resolve(root, NOTE_RELATIVE)
            write_text(path, replace_once(read_text(path), f"- `{relative}`\n"))
            assert ("MISSING_PRESENT_NOTE_PATHS", relative) in collect_issues(root)
            checks += 1

        for relative in PRESENT_PATHS:
            if relative in (
                README_RELATIVE.as_posix(),
                BOOTSTRAP_NOTE_RELATIVE.as_posix(),
                CLOSURE_NOTE_RELATIVE.as_posix(),
                MAKEFILE_RELATIVE.as_posix(),
                MANIFEST_RELATIVE.as_posix(),
            ):
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

        build_self_test_root(root)
        path = resolve(root, MANIFEST_RELATIVE)
        payload = json.loads(read_text(path))
        payload["repo_reality_gaps"] = [MANIFEST_FORBIDDEN_GAP] + EXPECTED_MANIFEST_GAPS[:-1]
        write_text(path, json.dumps(payload, indent=2) + "\n")
        assert any(code in {"MANIFEST_GAP_MISMATCH", "FORBIDDEN_MANIFEST_GAP"} for code, _ in collect_issues(root))
        checks += 1

        build_self_test_root(root)
        path = resolve(root, MANIFEST_RELATIVE)
        payload = json.loads(read_text(path))
        payload["notes"] = []
        write_text(path, json.dumps(payload, indent=2) + "\n")
        assert ("MISSING_MANIFEST_NOTES_MARKER", EXPECTED_MANIFEST_NOTES_MARKER) in collect_issues(root)
        checks += 1

        build_self_test_root(root)
        path = resolve(root, MANIFEST_RELATIVE)
        payload = json.loads(read_text(path))
        payload["notes"] = "broken"
        write_text(path, json.dumps(payload, indent=2) + "\n")
        assert ("INVALID_MANIFEST_NOTES", "str") in collect_issues(root)
        checks += 1

        build_self_test_root(root)
        path = resolve(root, MANIFEST_RELATIVE)
        write_text(path, "{not-json}\n")
        assert any(code == "INVALID_MANIFEST_JSON" for code, _ in collect_issues(root))
        checks += 1

        build_self_test_root(root)
        path = resolve(root, MANIFEST_RELATIVE)
        write_text(path, "[]\n")
        assert ("INVALID_MANIFEST_PAYLOAD", "list") in collect_issues(root)
        checks += 1

        for relative in (
            NOTE_RELATIVE,
            README_RELATIVE,
            BOOTSTRAP_NOTE_RELATIVE,
            CLOSURE_NOTE_RELATIVE,
            MAKEFILE_RELATIVE,
        ):
            build_self_test_root(root)
            resolve(root, relative).unlink()
            try:
                collect_issues(root)
            except SystemExit as exc:
                assert "required file missing" in str(exc)
                checks += 1
            else:
                raise AssertionError(relative)

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

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("PHASE2_SCRIPTS_SURFACE_RECONCILIATION=pass")
    print(f"PHASE2_SCRIPTS_SURFACE_PRESENT_COUNT={len(PRESENT_PATHS)}")
    print(f"PHASE2_SCRIPTS_SURFACE_GAP_COUNT={len(GAP_PATHS)}")
    print(
        "PHASE2_SCRIPTS_SURFACE_MARKER_COUNT="
        f"{len(NOTE_MARKERS) + len(NOTE_FORBIDDEN_MARKERS) + len(README_MARKERS) + len(README_FORBIDDEN_MARKERS) + len(BOOTSTRAP_MARKERS) + len(BOOTSTRAP_FORBIDDEN_MARKERS) + len(CLOSURE_MARKERS) + len(MAKEFILE_MARKERS)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
