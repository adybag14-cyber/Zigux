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
    "scripts/zigux/install-zig.py",
    "scripts/zigux/check-phase2-kbuild-routes.py",
    "scripts/zigux/check-phase2-docs-shared-reminder.py",
    "scripts/zigux/check-phase2-kconfig-selftest-alignment.py",
    "scripts/zigux/check-phase2-tests-readme-alignment.py",
    "scripts/zigux/check-phase2-cross.py",
    "scripts/zigux/check-phase2-cross-selftest-alignment.py",
    "scripts/zigux/check-phase2-toolchain-pinning.py",
    "scripts/zigux/check-phase2-toolchain-pin-scope.py",
    "scripts/zigux/check-phase2-required-make-routes.py",
    "scripts/zigux/check-phase2-tool-manifest.py",
    "scripts/zigux/check-phase2-artifact-tools-manifest.py",
    "scripts/zigux/check-genksyms-bridge.py",
    "scripts/zigux/kconfig/conf_bridge.zig",
    "scripts/zigux/kconfig/confdata_bridge.zig",
    "scripts/zigux/genksyms.zig",
    "Documentation/zigux/phase2-toolchain-bootstrap-notes.md",
    "Documentation/zigux/phase2-closure.md",
    "scripts/zigux/validate-phase2.py",
    "scripts/zigux/validate-phase2-closure.py",
    "zigux/Makefile",
    "zigux/tests/fixtures/phase2_tool_manifest.json",
    "zigux/tests/fixtures/phase2_artifact_tools_manifest.json",
    "zigux/tests/fixtures/phase2_cross_targets.json",
    "zigux/tests/fixtures/kconfig_bridge/conf_manifest.json",
    "zigux/tests/fixtures/kconfig_bridge/confdata_manifest.json",
    "zigux/tests/fixtures/kconfig_bridge/cases.json",
    "zigux/tests/fixtures/genksyms_bridge/cases.json",
    "zigux/tests/fixtures/genksyms_bridge/help_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/minimal_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/debug_reference_types_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/long_options_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/quiet_overrides_warning_expected.json",
)

NOTE_MARKERS = (
    "# Phase 2 Scripts Surface Reconciliation",
    "## Directly readable scripts-root anchors",
    "## Current repo-reality gaps",
    "## Current aligned packet",
    "## Lane 25 boundary",
    "Treat those as the current directly readable Phase 2 scripts-root anchors on `master`.",
    "- No current repo-reality gaps remain inside this bounded Phase 2 scripts-root packet on current `master`.",
    "- Treat older missing-installer, missing-direct-cross-route, or missing-closure-validator wording as stale lane history rather than current scripts-root evidence.",
    "- `scripts/zigux/README.md`, `Documentation/zigux/phase2-toolchain-bootstrap-notes.md`, `zigux/tests/fixtures/phase2_tool_manifest.json`, `Documentation/zigux/phase2-closure.md`, and `zigux/Makefile` now all keep `scripts/zigux/install-zig.py`, `scripts/zigux/check-phase2-cross.py`, `zigux/tests/fixtures/phase2_cross_targets.json`, `scripts/zigux/validate-phase2-closure.py`, the bounded genksyms bridge packet, and the rematerialized make-wrapper routes inside the present Phase 2 packet.",
    "- Keep this scripts-surface sidecar focused on fail-closing that current scripts-root packet while the shared-docs, bootstrap-note, review-checklist, and artifact-diff sidecars keep their separate surfaces.",
    "- Do not reopen older missing-route assumptions unless fresh exact current-`master` rereads prove those paths disappeared again.",
    "Lane 25 should use this note and its checker to keep the present scripts-root, bootstrap-note, manifest, closure-side, and make-wrapper packet aligned around the returned installer, direct cross-route, artifact-support, and bounded genksyms bridge surfaces without reopening the broader shared docs or artifact-diff surfaces.",
)

NOTE_FORBIDDEN_MARKERS = (
    "Treat those paths as the remaining repo-reality gaps on current `master`, not as shipped Phase 2 scripts-root evidence.",
    "- The live reminder surfaces keep only `scripts/zigux/install-zig.py`, `scripts/zigux/check-phase2-cross.py`, and `zigux/tests/fixtures/phase2_cross_targets.json` in repo-reality-gap wording.",
    "- Do not treat the remaining installer or direct cross-route companions as returned until current `master` materializes them.",
)

README_MARKERS = (
    "- Phase 2 flow - the current scripts-root bridge packet stays reviewable through the live toolchain checker, installer helper, direct cross-route packet, `conf_bridge` and `confdata_bridge` helper surfaces, the restored closure-side validator packet, the manifest-backed kconfig fixture roster, the shipped make-wrapper packet, and the surviving Phase 2 alignment guards instead of replaying older missing-route assumptions inside that now-rematerialized toolchain packet",
    "- `scripts/zigux/check-zig-toolchain.py`, `scripts/zigux/check-phase2-kbuild-routes.py`, `scripts/zigux/check-genksyms-bridge.py`, `scripts/zigux/check-phase2-docs-shared-reminder.py`, `scripts/zigux/check-phase2-kconfig-selftest-alignment.py`, `scripts/zigux/check-phase2-tests-readme-alignment.py`, `scripts/zigux/check-phase2-cross.py`, `scripts/zigux/check-phase2-cross-selftest-alignment.py`, `scripts/zigux/check-phase2-toolchain-pinning.py`, `scripts/zigux/check-phase2-toolchain-pin-scope.py`, `scripts/zigux/check-phase2-tool-manifest.py`, and `scripts/zigux/check-phase2-required-make-routes.py` remain the shipped Phase 2 toolchain, reminder, alignment, genksyms-bridge, and required-make-route guards that survive on current `master`",
    "- `Documentation/zigux/phase2-closure.md`, `scripts/zigux/validate-phase2.py`, `scripts/zigux/validate-phase2-closure.py`, `zigux/Makefile`, `make -C zigux phase2-toolchain`, `make -C zigux phase2-tools`, `make -C zigux phase2-kconfig`, `make -C zigux phase2-cross`, `make -C zigux phase2-genksyms`, `make -C zigux phase2-validate`, `make -C zigux phase2`, `zigux/tests/fixtures/phase2_tool_manifest.json`, and `zigux/tests/fixtures/phase2_artifact_tools_manifest.json` keep the shipped closure-side reminder, closure-validator, validator entrypoint, make-wrapper, and artifact-support packet explicit from the scripts root beside the surviving checker set",
    "- `scripts/zigux/check-phase2-tool-manifest.py` and `zigux/tests/fixtures/phase2_tool_manifest.json` keep the fixture-backed current Phase 2 tool packet explicit from the scripts root beside the closure-side validator packet and the surviving alignment guards",
    "- `scripts/zigux/install-zig.py`, `python3 scripts/zigux/install-zig.py --self-test`, `python3 scripts/zigux/check-phase2-cross.py --self-test`, `python3 scripts/zigux/check-phase2-cross.py`, and `zigux/tests/fixtures/phase2_cross_targets.json` are directly readable on current `master`, so keep those installer and direct cross-route surfaces explicit beside the shipped toolchain and kbuild reminder packet instead of leaving them in repo-reality-gap wording",
    "- keep those installer, tool-manifest, direct cross-route, and genksyms bridge surfaces explicit beside the shipped toolchain and kbuild reminder packet",
)

BOOTSTRAP_MARKERS = (
    "- `scripts/zigux/check-phase2-toolchain-pinning.py`, `scripts/zigux/check-phase2-toolchain-pin-scope.py`, `scripts/zigux/check-phase2-required-make-routes.py`, `scripts/zigux/check-phase2-kbuild-routes.py`, `scripts/zigux/check-phase2-docs-shared-reminder.py`, `scripts/zigux/check-phase2-kconfig-selftest-alignment.py`, `scripts/zigux/check-phase2-tests-readme-alignment.py`, `scripts/zigux/check-phase2-tool-manifest.py`, `scripts/zigux/check-phase2-cross.py`, and `scripts/zigux/check-phase2-cross-selftest-alignment.py` are the current shipped Phase 2 reminder and alignment guards visible on `master`.",
    "- `scripts/zigux/check-phase2-artifact-tools-manifest.py` is directly readable on current `master` and keeps the fixture-backed artifact-support packet explicit beside `scripts/zigux/check-phase2-tool-manifest.py` and `zigux/tests/fixtures/phase2_artifact_tools_manifest.json`.",
    "- `scripts/zigux/install-zig.py` is directly readable on current `master` and keeps the pinned-channel archive download, SHA-256 verification, and install-root replay path explicit beside the reminder guards.",
    "- `.github/workflows/zigux-bootstrap.yml` now runs `python3 scripts/zigux/check-zig-toolchain.py --self-test`, `python3 scripts/zigux/check-zig-toolchain.py --policy-only`, `python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing`, `python3 scripts/zigux/install-zig.py --self-test`, `python3 scripts/zigux/check-phase2-toolchain-pinning.py --self-test`, `python3 scripts/zigux/check-phase2-toolchain-pinning.py`, `python3 scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test`, `python3 scripts/zigux/check-phase2-toolchain-pin-scope.py`, and `make -C zigux phase2-toolchain`, so the live bootstrap packet exercises the pinned-channel, pinned-archive integrity, installer, toolchain-pinning, pin-scope, and make-wrapper-backed toolchain route replays instead of leaving the toolchain reminder checks or the returned Phase 2 toolchain wrapper implicit beside the shipped CI packet.",
    "- `Documentation/zigux/phase2-closure.md`, `scripts/zigux/validate-phase2.py`, `scripts/zigux/validate-phase2-closure.py`, `zigux/Makefile`, `zigux/tests/README.md`, `scripts/zigux/check-phase2-tool-manifest.py`, `scripts/zigux/kconfig/conf_bridge.zig`, `scripts/zigux/kconfig/confdata_bridge.zig`, `zigux/tests/fixtures/phase2_tool_manifest.json`, `zigux/tests/fixtures/phase2_artifact_tools_manifest.json`, and the `zigux/tests/fixtures/kconfig_bridge/` manifest roster keep the bounded closure-side, closure-validator, validator-entrypoint, tests-facing, tool-manifest, fixture-backed artifact-diff support, and bridge packet reviewable without widening back into older validator-first claims.",
    "- `zigux/tests/fixtures/phase2_cross_targets.json` keeps the rematerialized direct cross-route packet explicit through the pinned `x86_64-linux` `archive_required` lane plus the `aarch64-linux` `route_contract_only` lane, so toolchain follow-through should treat the returned cross packet as present evidence instead of a repo-reality gap.",
    "- `scripts/zigux/check-genksyms-bridge.py`, `scripts/zigux/genksyms.zig`, and the `zigux/tests/fixtures/genksyms_bridge/` fixture roster keep the bounded genksyms bridge helper packet explicit beside the reminder guards, and `make -C zigux phase2-genksyms` keeps its wrapper route inside the same returned make-wrapper packet.",
    "- The rematerialized make-wrapper packet is directly readable on current `master` through `make -C zigux phase2-toolchain`, `make -C zigux phase2-tools`, `make -C zigux phase2-kconfig`, `make -C zigux phase2-cross`, `make -C zigux phase2-genksyms`, `make -C zigux phase2-validate`, and `make -C zigux phase2`, so keep those routes in the present packet instead of the repo-reality-gap list.",
    "- No current repo-reality gaps remain inside the bounded toolchain, installer, and direct cross-route packet on current `master`.",
)

CLOSURE_MARKERS = (
    "- `scripts/zigux/install-zig.py`",
    "- `scripts/zigux/check-phase2-cross.py`",
    "- `zigux/tests/fixtures/phase2_cross_targets.json`",
    "Within the bounded Phase 2 closure packet, current `master` no longer leaves the installer hook, direct cross-route packet, or returned closure-validator companions in the repo-reality-gap bucket.",
    "- `PHASE2_CURRENT_GAP_PACKET=`",
    "- `python3 scripts/zigux/install-zig.py --self-test`",
    "- `python3 scripts/zigux/check-phase2-cross.py --self-test`",
    "- `python3 scripts/zigux/validate-phase2-closure.py --self-test`",
    "- `make -C zigux phase2-genksyms`",
)

MAKEFILE_MARKERS = (
    "phase2-toolchain:",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-zig-toolchain.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-zig-toolchain.py --policy-only",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-zig-toolchain.py --archive-only --allow-missing",
    "phase2-cross:",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-selftest-alignment.py",
    "phase2-genksyms:",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-genksyms-bridge.py --self-test",
    "phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-tool-manifest.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/validate-phase2-closure.py",
)

EXPECTED_MANIFEST_GAPS: list[str] = []
EXPECTED_MANIFEST_NOTES_MARKER = (
    "Keep the returned installer helper, direct cross-route checker, phase2_cross_targets fixture, bounded genksyms fixture packet, and artifact-support manifest checker explicit through the current Phase 2 tool packet instead of leaving them in the repo-reality-gap bucket."
)

NOTE_TEMPLATE = """# Phase 2 Scripts Surface Reconciliation

This note records the current Phase 2 scripts-root packet that Lane 25 keeps aligned on `master`.

## Directly readable scripts-root anchors

- `scripts/zigux/README.md`
- `scripts/zigux/check-zig-toolchain.py`
- `scripts/zigux/install-zig.py`
- `scripts/zigux/check-phase2-kbuild-routes.py`
- `scripts/zigux/check-phase2-docs-shared-reminder.py`
- `scripts/zigux/check-phase2-kconfig-selftest-alignment.py`
- `scripts/zigux/check-phase2-tests-readme-alignment.py`
- `scripts/zigux/check-phase2-cross.py`
- `scripts/zigux/check-phase2-cross-selftest-alignment.py`
- `scripts/zigux/check-phase2-toolchain-pinning.py`
- `scripts/zigux/check-phase2-toolchain-pin-scope.py`
- `scripts/zigux/check-phase2-required-make-routes.py`
- `scripts/zigux/check-phase2-tool-manifest.py`
- `scripts/zigux/check-phase2-artifact-tools-manifest.py`
- `scripts/zigux/check-genksyms-bridge.py`
- `scripts/zigux/kconfig/conf_bridge.zig`
- `scripts/zigux/kconfig/confdata_bridge.zig`
- `scripts/zigux/genksyms.zig`
- `Documentation/zigux/phase2-toolchain-bootstrap-notes.md`
- `Documentation/zigux/phase2-closure.md`
- `scripts/zigux/validate-phase2.py`
- `scripts/zigux/validate-phase2-closure.py`
- `zigux/Makefile`
- `zigux/tests/fixtures/phase2_tool_manifest.json`
- `zigux/tests/fixtures/phase2_artifact_tools_manifest.json`
- `zigux/tests/fixtures/phase2_cross_targets.json`
- `zigux/tests/fixtures/kconfig_bridge/conf_manifest.json`
- `zigux/tests/fixtures/kconfig_bridge/confdata_manifest.json`
- `zigux/tests/fixtures/kconfig_bridge/cases.json`
- `zigux/tests/fixtures/genksyms_bridge/cases.json`
- `zigux/tests/fixtures/genksyms_bridge/help_expected.json`
- `zigux/tests/fixtures/genksyms_bridge/minimal_expected.json`
- `zigux/tests/fixtures/genksyms_bridge/debug_reference_types_expected.json`
- `zigux/tests/fixtures/genksyms_bridge/long_options_expected.json`
- `zigux/tests/fixtures/genksyms_bridge/quiet_overrides_warning_expected.json`

Treat those as the current directly readable Phase 2 scripts-root anchors on `master`.

## Current repo-reality gaps

- No current repo-reality gaps remain inside this bounded Phase 2 scripts-root packet on current `master`.
- Treat older missing-installer, missing-direct-cross-route, or missing-closure-validator wording as stale lane history rather than current scripts-root evidence.

## Current aligned packet

- `scripts/zigux/README.md`, `Documentation/zigux/phase2-toolchain-bootstrap-notes.md`, `zigux/tests/fixtures/phase2_tool_manifest.json`, `Documentation/zigux/phase2-closure.md`, and `zigux/Makefile` now all keep `scripts/zigux/install-zig.py`, `scripts/zigux/check-phase2-cross.py`, `zigux/tests/fixtures/phase2_cross_targets.json`, `scripts/zigux/validate-phase2-closure.py`, the bounded genksyms bridge packet, and the rematerialized make-wrapper routes inside the present Phase 2 packet.
- Keep this scripts-surface sidecar focused on fail-closing that current scripts-root packet while the shared-docs, bootstrap-note, review-checklist, and artifact-diff sidecars keep their separate surfaces.
- Do not reopen older missing-route assumptions unless fresh exact current-`master` rereads prove those paths disappeared again.

## Lane 25 boundary

Lane 25 should use this note and its checker to keep the present scripts-root, bootstrap-note, manifest, closure-side, and make-wrapper packet aligned around the returned installer, direct cross-route, artifact-support, and bounded genksyms bridge surfaces without reopening the broader shared docs or artifact-diff surfaces.
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
    issues.extend(collect_missing_markers(bootstrap_text, BOOTSTRAP_MARKERS, "MISSING_BOOTSTRAP_MARKERS"))
    issues.extend(collect_missing_markers(closure_text, CLOSURE_MARKERS, "MISSING_CLOSURE_MARKERS"))
    issues.extend(collect_missing_markers(makefile_text, MAKEFILE_MARKERS, "MISSING_MAKEFILE_MARKERS"))

    for relative in PRESENT_PATHS:
        note_entry = f"- `{relative}`"
        if note_entry not in note_text:
            issues.append(("MISSING_PRESENT_NOTE_PATHS", relative))
        if not resolve(root, Path(relative)).exists():
            issues.append(("MISSING_PRESENT_REPO_PATHS", relative))

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

    notes = manifest.get("notes")
    if not isinstance(notes, list):
        issues.append(("INVALID_MANIFEST_NOTES", type(notes).__name__))
    elif EXPECTED_MANIFEST_NOTES_MARKER not in notes:
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
            if marker.startswith("- `"):
                path.write_text(read_text(path) + marker + "\n", encoding="utf-8")
            else:
                path.write_text(read_text(path) + "\n" + marker + "\n", encoding="utf-8")
            assert ("FORBIDDEN_NOTE_MARKERS", marker) in collect_issues(root)
            checks += 1

        for marker in README_MARKERS:
            build_self_test_root(root)
            path = resolve(root, README_RELATIVE)
            write_text(path, replace_once(read_text(path), marker))
            assert ("MISSING_README_MARKERS", marker) in collect_issues(root)
            checks += 1

        for marker in BOOTSTRAP_MARKERS:
            build_self_test_root(root)
            path = resolve(root, BOOTSTRAP_NOTE_RELATIVE)
            write_text(path, replace_once(read_text(path), marker))
            assert ("MISSING_BOOTSTRAP_MARKERS", marker) in collect_issues(root)
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

        build_self_test_root(root)
        path = resolve(root, MANIFEST_RELATIVE)
        payload = json.loads(read_text(path))
        payload["repo_reality_gaps"] = ["scripts/zigux/install-zig.py"]
        write_text(path, json.dumps(payload, indent=2) + "\n")
        assert any(code == "MANIFEST_GAP_MISMATCH" for code, _ in collect_issues(root))
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
        write_text(path, "{not-json}\n")
        assert any(code == "INVALID_MANIFEST_JSON" for code, _ in collect_issues(root))
        checks += 1

        build_self_test_root(root)
        resolve(root, Path("scripts/zigux/install-zig.py")).unlink()
        assert ("MISSING_PRESENT_REPO_PATHS", "scripts/zigux/install-zig.py") in collect_issues(root)
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
    print(f"PHASE2_SCRIPTS_SURFACE_PRESENT_COUNT={len(PRESENT_PATHS)}")
    print(
        "PHASE2_SCRIPTS_SURFACE_MARKER_COUNT="
        f"{len(NOTE_MARKERS) + len(NOTE_FORBIDDEN_MARKERS) + len(README_MARKERS) + len(BOOTSTRAP_MARKERS) + len(CLOSURE_MARKERS) + len(MAKEFILE_MARKERS)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
