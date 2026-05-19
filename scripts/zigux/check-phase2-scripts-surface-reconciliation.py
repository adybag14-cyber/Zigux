#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
NOTE_RELATIVE = Path("Documentation/zigux/phase2-scripts-surface-reconciliation.md")
README_RELATIVE = Path("scripts/zigux/README.md")
BOOTSTRAP_RELATIVE = Path("Documentation/zigux/phase2-toolchain-bootstrap-notes.md")
CLOSURE_RELATIVE = Path("Documentation/zigux/phase2-closure.md")
MAKEFILE_RELATIVE = Path("zigux/Makefile")
MANIFEST_RELATIVE = Path("zigux/tests/fixtures/phase2_tool_manifest.json")

DIRECT_PATHS = (
    "scripts/zigux/README.md",
    "scripts/zigux/check-zig-toolchain.py",
    "scripts/zigux/check-phase2-kbuild-routes.py",
    "scripts/zigux/check-phase2-docs-shared-reminder.py",
    "scripts/zigux/check-phase2-kconfig-selftest-alignment.py",
    "scripts/zigux/check-phase2-tests-readme-alignment.py",
    "scripts/zigux/check-phase2-cross.py",
    "scripts/zigux/check-phase2-cross-selftest-alignment.py",
    "scripts/zigux/check-phase2-toolchain-pinning.py",
    "scripts/zigux/check-phase2-toolchain-pin-scope.py",
    "scripts/zigux/check-phase2-required-make-routes.py",
    "scripts/zigux/install-zig.py",
    "scripts/zigux/kconfig/conf_bridge.zig",
    "scripts/zigux/kconfig/confdata_bridge.zig",
    "Documentation/zigux/phase2-closure.md",
    "Documentation/zigux/phase2-toolchain-bootstrap-notes.md",
    "scripts/zigux/validate-phase2.py",
    "scripts/zigux/validate-phase2-closure.py",
    "zigux/Makefile",
    "zigux/tests/fixtures/phase2_tool_manifest.json",
    "zigux/tests/fixtures/phase2_artifact_tools_manifest.json",
    "zigux/tests/fixtures/phase2_cross_targets.json",
    "zigux/tests/fixtures/kconfig_bridge/conf_manifest.json",
    "zigux/tests/fixtures/kconfig_bridge/confdata_manifest.json",
    "zigux/tests/fixtures/kconfig_bridge/cases.json",
)

NOTE_REQUIRED_MARKERS = (
    "# Phase 2 Scripts Surface Reconciliation",
    "## Directly readable scripts-root anchors",
    "## Current aligned packet",
    "## Current repo-reality gaps",
    "## Lane 25 boundary",
    "Treat those as the current directly readable Phase 2 scripts-root anchors on `master`.",
    "`scripts/zigux/README.md`, `Documentation/zigux/phase2-toolchain-bootstrap-notes.md`, `Documentation/zigux/phase2-closure.md`, `zigux/tests/fixtures/phase2_tool_manifest.json`, and `zigux/Makefile` now all keep `scripts/zigux/install-zig.py`, `scripts/zigux/check-phase2-cross.py`, `zigux/tests/fixtures/phase2_cross_targets.json`, and `scripts/zigux/validate-phase2-closure.py` inside the current packet instead of framing any of them as repo-reality gaps.",
    "The live reminder packet now stays aligned across the shipped toolchain checker, installer helper, direct cross-route checker, kconfig bridge helpers, closure-side validator pair, shipped make-wrapper routes, and fixture roster already visible on current `master`.",
    "Keep this scripts-surface sidecar focused on fail-closing that returned scripts-root packet while the shared docs, bootstrap-note, manifest-root, and artifact-diff lane packets keep their separate surfaces.",
    "No current repo-reality gaps remain inside the bounded scripts-root toolchain, installer, direct cross-route, closure-side, make-wrapper, and fixture packet on current `master`.",
    "Treat future drift here as a reminder-surface mismatch first, not as evidence that the returned installer or direct cross-route packet disappeared.",
    "Lane 25 should use this note and its checker to keep the present scripts-root, bootstrap-note, tests-root, manifest, closure-side, and make-wrapper packet aligned around the returned installer, direct cross-route, and closure-validator surfaces without reopening the broader shared docs or artifact-diff sidecars.",
)

NOTE_FORBIDDEN_MARKERS = (
    "## Remaining repo-reality gaps",
    "Treat those paths as the remaining repo-reality gaps on current `master`, not as shipped Phase 2 scripts-root evidence.",
    "Do not treat the remaining installer or direct cross-route companions as returned until current `master` materializes them.",
)

README_REQUIRED_MARKERS = (
    "- Phase 2 flow - the current scripts-root bridge packet stays reviewable through the live toolchain checker, installer helper, direct cross-route packet, `conf_bridge` and `confdata_bridge` helper surfaces, the restored closure-side validator packet, the manifest-backed kconfig fixture roster, the shipped make-wrapper packet, and the surviving Phase 2 alignment guards instead of replaying older missing-route assumptions inside that now-rematerialized toolchain packet",
    "- `scripts/zigux/check-zig-toolchain.py`, `scripts/zigux/check-phase2-kbuild-routes.py`, `scripts/zigux/check-phase2-docs-shared-reminder.py`, `scripts/zigux/check-phase2-kconfig-selftest-alignment.py`, `scripts/zigux/check-phase2-tests-readme-alignment.py`, `scripts/zigux/check-phase2-cross.py`, `scripts/zigux/check-phase2-cross-selftest-alignment.py`, `scripts/zigux/check-phase2-toolchain-pinning.py`, `scripts/zigux/check-phase2-toolchain-pin-scope.py`, and `scripts/zigux/check-phase2-required-make-routes.py` remain the shipped Phase 2 toolchain, reminder, alignment, and required-make-route guards that survive on current `master`",
    "- `Documentation/zigux/phase2-closure.md`, `scripts/zigux/validate-phase2.py`, `scripts/zigux/validate-phase2-closure.py`, `zigux/Makefile`, `make -C zigux phase2-toolchain`, `make -C zigux phase2-tools`, `make -C zigux phase2-kconfig`, `make -C zigux phase2-cross`, `make -C zigux phase2-validate`, `make -C zigux phase2`, and `zigux/tests/fixtures/phase2_artifact_tools_manifest.json` keep the shipped closure-side reminder, closure-validator, validator entrypoint, make-wrapper, and artifact-support packet explicit from the scripts root beside the surviving checker set",
    "- `scripts/zigux/install-zig.py`, `python3 scripts/zigux/install-zig.py --self-test`, `python3 scripts/zigux/check-phase2-cross.py --self-test`, `python3 scripts/zigux/check-phase2-cross.py`, and `zigux/tests/fixtures/phase2_cross_targets.json` are directly readable on current `master`, so keep those installer and direct cross-route surfaces explicit beside the shipped toolchain and kbuild reminder packet instead of leaving them in repo-reality-gap wording",
)

README_FORBIDDEN_MARKERS = (
    "- repeated authenticated reads on current `master` still return missing for `scripts/zigux/install-zig.py`, `python3 scripts/zigux/install-zig.py --self-test`, `python3 scripts/zigux/check-phase2-cross.py --self-test`, `python3 scripts/zigux/check-phase2-cross.py`, and `zigux/tests/fixtures/phase2_cross_targets.json`, so treat those installer and direct cross-route names as historical packet members that need fresh re-materialization before they are reused here as direct current-`master` scripts-root evidence",
)

BOOTSTRAP_REQUIRED_MARKERS = (
    "- `scripts/zigux/install-zig.py` is directly readable on current `master` and keeps the pinned-channel archive download, SHA-256 verification, and install-root replay path explicit beside the reminder guards.",
    "- `zigux/tests/fixtures/phase2_cross_targets.json` keeps the rematerialized direct cross-route packet explicit through the pinned `x86_64-linux` `archive_required` lane plus the `aarch64-linux` `route_contract_only` lane, so toolchain follow-through should treat the returned cross packet as present evidence instead of a repo-reality gap.",
    "- No current repo-reality gaps remain inside the bounded toolchain, installer, and direct cross-route packet on current `master`.",
)

BOOTSTRAP_FORBIDDEN_MARKERS = (
    "- Repeated authenticated reads on current `master` still return missing for `scripts/zigux/install-zig.py`, `scripts/zigux/check-phase2-cross.py`, and `zigux/tests/fixtures/phase2_cross_targets.json`.",
    "- Treat the absent installer and direct cross-route names as historical packet members until same-lane work rematerializes them on `master`.",
)

CLOSURE_REQUIRED_MARKERS = (
    "`scripts/zigux/install-zig.py`",
    "`scripts/zigux/check-phase2-cross.py`",
    "`zigux/tests/fixtures/phase2_cross_targets.json`",
    "Within the bounded Phase 2 closure packet, current `master` no longer leaves the installer hook, direct cross-route packet, or returned closure-validator companions in the repo-reality-gap bucket.",
)

MAKEFILE_REQUIRED_MARKERS = (
    "phase2-cross:",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/validate-phase2-closure.py",
)

EXPECTED_MANIFEST_GAPS: list[str] = []
EXPECTED_MANIFEST_NOTE = (
    "Keep the returned installer helper, direct cross-route checker, and phase2_cross_targets fixture explicit through the bounded toolchain packet instead of leaving them in the repo-reality-gap bucket."
)

NOTE_TEMPLATE = """# Phase 2 Scripts Surface Reconciliation

This note records the current Phase 2 scripts-root packet that Lane 25 keeps aligned on `master`.

## Directly readable scripts-root anchors

- `scripts/zigux/README.md`
- `scripts/zigux/check-zig-toolchain.py`
- `scripts/zigux/check-phase2-kbuild-routes.py`
- `scripts/zigux/check-phase2-docs-shared-reminder.py`
- `scripts/zigux/check-phase2-kconfig-selftest-alignment.py`
- `scripts/zigux/check-phase2-tests-readme-alignment.py`
- `scripts/zigux/check-phase2-cross.py`
- `scripts/zigux/check-phase2-cross-selftest-alignment.py`
- `scripts/zigux/check-phase2-toolchain-pinning.py`
- `scripts/zigux/check-phase2-toolchain-pin-scope.py`
- `scripts/zigux/check-phase2-required-make-routes.py`
- `scripts/zigux/install-zig.py`
- `scripts/zigux/kconfig/conf_bridge.zig`
- `scripts/zigux/kconfig/confdata_bridge.zig`
- `Documentation/zigux/phase2-closure.md`
- `Documentation/zigux/phase2-toolchain-bootstrap-notes.md`
- `scripts/zigux/validate-phase2.py`
- `scripts/zigux/validate-phase2-closure.py`
- `zigux/Makefile`
- `zigux/tests/fixtures/phase2_tool_manifest.json`
- `zigux/tests/fixtures/phase2_artifact_tools_manifest.json`
- `zigux/tests/fixtures/phase2_cross_targets.json`
- `zigux/tests/fixtures/kconfig_bridge/conf_manifest.json`
- `zigux/tests/fixtures/kconfig_bridge/confdata_manifest.json`
- `zigux/tests/fixtures/kconfig_bridge/cases.json`

Treat those as the current directly readable Phase 2 scripts-root anchors on `master`.

## Current aligned packet

- `scripts/zigux/README.md`, `Documentation/zigux/phase2-toolchain-bootstrap-notes.md`, `Documentation/zigux/phase2-closure.md`, `zigux/tests/fixtures/phase2_tool_manifest.json`, and `zigux/Makefile` now all keep `scripts/zigux/install-zig.py`, `scripts/zigux/check-phase2-cross.py`, `zigux/tests/fixtures/phase2_cross_targets.json`, and `scripts/zigux/validate-phase2-closure.py` inside the current packet instead of framing any of them as repo-reality gaps.
- The live reminder packet now stays aligned across the shipped toolchain checker, installer helper, direct cross-route checker, kconfig bridge helpers, closure-side validator pair, shipped make-wrapper routes, and fixture roster already visible on current `master`.
- Keep this scripts-surface sidecar focused on fail-closing that returned scripts-root packet while the shared docs, bootstrap-note, manifest-root, and artifact-diff lane packets keep their separate surfaces.

## Current repo-reality gaps

- No current repo-reality gaps remain inside the bounded scripts-root toolchain, installer, direct cross-route, closure-side, make-wrapper, and fixture packet on current `master`.
- Treat future drift here as a reminder-surface mismatch first, not as evidence that the returned installer or direct cross-route packet disappeared.

## Lane 25 boundary

Lane 25 should use this note and its checker to keep the present scripts-root, bootstrap-note, tests-root, manifest, closure-side, and make-wrapper packet aligned around the returned installer, direct cross-route, and closure-validator surfaces without reopening the broader shared docs or artifact-diff sidecars.
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
    bootstrap_text = read_text(resolve(root, BOOTSTRAP_RELATIVE))
    closure_text = read_text(resolve(root, CLOSURE_RELATIVE))
    makefile_text = read_text(resolve(root, MAKEFILE_RELATIVE))

    issues.extend(collect_missing_markers(note_text, NOTE_REQUIRED_MARKERS, "MISSING_NOTE_MARKERS"))
    issues.extend(collect_forbidden_markers(note_text, NOTE_FORBIDDEN_MARKERS, "FORBIDDEN_NOTE_MARKERS"))
    issues.extend(collect_missing_markers(readme_text, README_REQUIRED_MARKERS, "MISSING_README_MARKERS"))
    issues.extend(collect_forbidden_markers(readme_text, README_FORBIDDEN_MARKERS, "FORBIDDEN_README_MARKERS"))
    issues.extend(collect_missing_markers(bootstrap_text, BOOTSTRAP_REQUIRED_MARKERS, "MISSING_BOOTSTRAP_MARKERS"))
    issues.extend(collect_forbidden_markers(bootstrap_text, BOOTSTRAP_FORBIDDEN_MARKERS, "FORBIDDEN_BOOTSTRAP_MARKERS"))
    issues.extend(collect_missing_markers(closure_text, CLOSURE_REQUIRED_MARKERS, "MISSING_CLOSURE_MARKERS"))
    issues.extend(collect_missing_markers(makefile_text, MAKEFILE_REQUIRED_MARKERS, "MISSING_MAKEFILE_MARKERS"))

    for relative in DIRECT_PATHS:
        if f"- `{relative}`\n" not in note_text:
            issues.append(("MISSING_DIRECT_NOTE_PATHS", relative))
        if not resolve(root, Path(relative)).exists():
            issues.append(("MISSING_DIRECT_REPO_PATHS", relative))

    manifest = json.loads(read_text(resolve(root, MANIFEST_RELATIVE)))
    gaps = manifest.get("repo_reality_gaps")
    if gaps != EXPECTED_MANIFEST_GAPS:
        issues.append(("MANIFEST_GAP_MISMATCH", f"actual={gaps!r}:expected={EXPECTED_MANIFEST_GAPS!r}"))
    notes = manifest.get("notes")
    if not isinstance(notes, list):
        issues.append(("INVALID_MANIFEST_NOTES", type(notes).__name__))
    elif EXPECTED_MANIFEST_NOTE not in notes:
        issues.append(("MISSING_MANIFEST_NOTE", EXPECTED_MANIFEST_NOTE))

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


def replace_once(text: str, marker: str) -> str:
    if marker not in text:
        raise AssertionError(marker)
    return text.replace(marker, "", 1)


def build_self_test_root(root: Path) -> None:
    write_text(resolve(root, NOTE_RELATIVE), NOTE_TEMPLATE)
    write_text(resolve(root, README_RELATIVE), "\n".join(README_REQUIRED_MARKERS) + "\n")
    write_text(resolve(root, BOOTSTRAP_RELATIVE), "\n".join(BOOTSTRAP_REQUIRED_MARKERS) + "\n")
    write_text(resolve(root, CLOSURE_RELATIVE), "\n".join(CLOSURE_REQUIRED_MARKERS) + "\n")
    write_text(resolve(root, MAKEFILE_RELATIVE), "\n".join(MAKEFILE_REQUIRED_MARKERS) + "\n")
    write_text(
        resolve(root, MANIFEST_RELATIVE),
        json.dumps({"repo_reality_gaps": [], "notes": [EXPECTED_MANIFEST_NOTE]}, indent=2) + "\n",
    )
    for relative in DIRECT_PATHS:
        path = resolve(root, Path(relative))
        if path in (
            resolve(root, README_RELATIVE),
            resolve(root, BOOTSTRAP_RELATIVE),
            resolve(root, CLOSURE_RELATIVE),
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

        for marker in NOTE_REQUIRED_MARKERS:
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

        for marker in README_REQUIRED_MARKERS:
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

        for marker in BOOTSTRAP_REQUIRED_MARKERS:
            build_self_test_root(root)
            path = resolve(root, BOOTSTRAP_RELATIVE)
            write_text(path, replace_once(read_text(path), marker))
            assert ("MISSING_BOOTSTRAP_MARKERS", marker) in collect_issues(root)
            checks += 1

        for marker in BOOTSTRAP_FORBIDDEN_MARKERS:
            build_self_test_root(root)
            path = resolve(root, BOOTSTRAP_RELATIVE)
            write_text(path, read_text(path) + marker + "\n")
            assert ("FORBIDDEN_BOOTSTRAP_MARKERS", marker) in collect_issues(root)
            checks += 1

        for marker in CLOSURE_REQUIRED_MARKERS:
            build_self_test_root(root)
            path = resolve(root, CLOSURE_RELATIVE)
            write_text(path, replace_once(read_text(path), marker))
            assert ("MISSING_CLOSURE_MARKERS", marker) in collect_issues(root)
            checks += 1

        for marker in MAKEFILE_REQUIRED_MARKERS:
            build_self_test_root(root)
            path = resolve(root, MAKEFILE_RELATIVE)
            write_text(path, replace_once(read_text(path), marker))
            assert ("MISSING_MAKEFILE_MARKERS", marker) in collect_issues(root)
            checks += 1

        for relative in DIRECT_PATHS:
            build_self_test_root(root)
            path = resolve(root, NOTE_RELATIVE)
            write_text(path, replace_once(read_text(path), f"- `{relative}`\n"))
            assert ("MISSING_DIRECT_NOTE_PATHS", relative) in collect_issues(root)
            checks += 1

        for relative in DIRECT_PATHS:
            if relative in (
                README_RELATIVE.as_posix(),
                BOOTSTRAP_RELATIVE.as_posix(),
                CLOSURE_RELATIVE.as_posix(),
                MAKEFILE_RELATIVE.as_posix(),
                MANIFEST_RELATIVE.as_posix(),
            ):
                continue
            build_self_test_root(root)
            resolve(root, Path(relative)).unlink()
            assert ("MISSING_DIRECT_REPO_PATHS", relative) in collect_issues(root)
            checks += 1

        build_self_test_root(root)
        manifest_path = resolve(root, MANIFEST_RELATIVE)
        payload = json.loads(read_text(manifest_path))
        payload["repo_reality_gaps"] = ["scripts/zigux/install-zig.py"]
        write_text(manifest_path, json.dumps(payload, indent=2) + "\n")
        assert any(code == "MANIFEST_GAP_MISMATCH" for code, _ in collect_issues(root))
        checks += 1

        build_self_test_root(root)
        manifest_path = resolve(root, MANIFEST_RELATIVE)
        payload = json.loads(read_text(manifest_path))
        payload["notes"] = []
        write_text(manifest_path, json.dumps(payload, indent=2) + "\n")
        assert ("MISSING_MANIFEST_NOTE", EXPECTED_MANIFEST_NOTE) in collect_issues(root)
        checks += 1

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
    print(f"PHASE2_SCRIPTS_SURFACE_DIRECT_PATH_COUNT={len(DIRECT_PATHS)}")
    print(
        "PHASE2_SCRIPTS_SURFACE_MARKER_COUNT="
        f"{len(NOTE_REQUIRED_MARKERS) + len(NOTE_FORBIDDEN_MARKERS) + len(README_REQUIRED_MARKERS) + len(README_FORBIDDEN_MARKERS) + len(BOOTSTRAP_REQUIRED_MARKERS) + len(BOOTSTRAP_FORBIDDEN_MARKERS) + len(CLOSURE_REQUIRED_MARKERS) + len(MAKEFILE_REQUIRED_MARKERS)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
