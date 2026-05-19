#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
MANIFEST = Path("zigux/tests/fixtures/phase2_tool_manifest.json")

REQUIRED_TOP_LEVEL = {
    "phase": "Phase 2",
    "status": "active",
    "scope": "current directly readable scripts-root toolchain, installer, direct cross-route, kbuild, kconfig, genksyms, make-wrapper, and tranche-closure reminder packet",
    "workflow": ".github/workflows/zigux-bootstrap.yml",
}

REQUIRED_PRESENT_SURFACES = {
    "review_surfaces": (
        "Documentation/zigux/README.md",
        "Documentation/zigux/phase2-closure.md",
        "Documentation/zigux/review-checklist.md",
        "zigux/tests/README.md",
    ),
    "closure_notes": (
        "Documentation/zigux/phase2-closure.md",
        "Documentation/zigux/phase2-toolchain-bootstrap-notes.md",
    ),
    "validators": (
        "scripts/zigux/validate-phase2.py",
        "scripts/zigux/validate-phase2-closure.py",
    ),
    "checkers": (
        "scripts/zigux/check-zig-toolchain.py",
        "scripts/zigux/check-kconfig-bridge.py",
        "scripts/zigux/check-phase2-kconfig-selftest-alignment.py",
        "scripts/zigux/check-phase2-kbuild-routes.py",
        "scripts/zigux/check-phase2-tests-readme-alignment.py",
        "scripts/zigux/check-phase2-cross.py",
        "scripts/zigux/check-phase2-cross-selftest-alignment.py",
        "scripts/zigux/check-phase2-toolchain-pinning.py",
        "scripts/zigux/check-phase2-toolchain-pin-scope.py",
        "scripts/zigux/check-phase2-required-make-routes.py",
        "scripts/zigux/check-phase2-docs-shared-reminder.py",
        "scripts/zigux/check-phase2-tool-manifest.py",
        "scripts/zigux/check-phase2-artifact-tools-manifest.py",
        "scripts/zigux/check-genksyms-bridge.py",
    ),
    "bootstrap_helpers": (
        "scripts/zigux/install-zig.py",
    ),
    "bridge_helpers": (
        "scripts/zigux/kconfig/conf_bridge.zig",
        "scripts/zigux/kconfig/confdata_bridge.zig",
        "scripts/zigux/genksyms.zig",
    ),
    "policy": (
        "scripts/zigux/zig-toolchain-policy.json",
    ),
    "make_wrappers": (
        "zigux/Makefile",
        "make -C zigux phase2-toolchain",
        "make -C zigux phase2-tools",
        "make -C zigux phase2-kconfig",
        "make -C zigux phase2-cross",
        "make -C zigux phase2-genksyms",
        "make -C zigux phase2-validate",
        "make -C zigux phase2",
    ),
    "cross_route_support": (
        "scripts/zigux/check-phase2-cross.py",
        "zigux/tests/fixtures/phase2_cross_targets.json",
    ),
    "artifact_support": (
        "scripts/zigux/check-phase2-artifact-tools-manifest.py",
        "zigux/tests/fixtures/phase2_artifact_tools_manifest.json",
    ),
    "fixture_roster": (
        "zigux/tests/fixtures/kconfig_bridge/cases.json",
        "zigux/tests/fixtures/kconfig_bridge/conf_manifest.json",
        "zigux/tests/fixtures/kconfig_bridge/confdata_manifest.json",
        "zigux/tests/fixtures/genksyms_bridge/cases.json",
        "zigux/tests/fixtures/genksyms_bridge/help_expected.json",
        "zigux/tests/fixtures/genksyms_bridge/minimal_expected.json",
        "zigux/tests/fixtures/genksyms_bridge/debug_reference_types_expected.json",
        "zigux/tests/fixtures/genksyms_bridge/long_options_expected.json",
        "zigux/tests/fixtures/genksyms_bridge/quiet_overrides_warning_expected.json",
    ),
}

REQUIRED_NOTE_MARKERS = (
    "Current Phase 2 repo-tooling evidence is anchored in the shipped toolchain checker, the shipped toolchain-pinning and pin-scope guards, the returned installer helper, direct cross-route checker, docs-shared-reminder checker, required make-route guard, kbuild routes checker, the live kconfig bridge checker and fixture roster, the bounded genksyms bridge checker and fixture packet, cross-selftest checker, and the restored tranche-closure note.",
    "Keep the directly readable validator pair explicit through scripts/zigux/validate-phase2.py and scripts/zigux/validate-phase2-closure.py instead of leaving the closure-side replay packet implied only in prose.",
    "Keep the shipped zigux/Makefile entrypoints explicit through the phase2-toolchain, phase2-tools, phase2-kconfig, phase2-cross, phase2-genksyms, phase2-validate, and phase2 make wrappers instead of treating them as repo-reality gaps.",
    "Keep the dedicated manifest guards explicit through scripts/zigux/check-phase2-tool-manifest.py and scripts/zigux/check-phase2-artifact-tools-manifest.py so Phase 2 packet drift fails closed beside the other reminder checkers.",
    "Keep the returned installer helper, direct cross-route checker, phase2_cross_targets fixture, bounded genksyms fixture packet, and artifact-support manifest checker explicit through the current Phase 2 tool packet instead of leaving them in the repo-reality-gap bucket.",
)


def read_manifest(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def collect_issues(root: Path) -> list[tuple[str, str]]:
    manifest = read_manifest(root / MANIFEST)
    issues: list[tuple[str, str]] = []
    for key, expected in REQUIRED_TOP_LEVEL.items():
        if manifest.get(key) != expected:
            issues.append(("TOP_LEVEL_MISMATCH", key))
    surfaces = manifest.get("present_surfaces")
    if not isinstance(surfaces, dict):
        issues.append(("MISSING_PRESENT_SURFACES", "present_surfaces"))
    else:
        for category, required_entries in REQUIRED_PRESENT_SURFACES.items():
            entries = surfaces.get(category)
            if not isinstance(entries, list):
                issues.append(("MISSING_SURFACE_CATEGORY", category))
                continue
            for entry in required_entries:
                if entry not in entries:
                    issues.append(("MISSING_SURFACE_ENTRY", f"{category}:{entry}"))
    if manifest.get("repo_reality_gaps") != []:
        issues.append(("NONEMPTY_REPO_REALITY_GAPS", "repo_reality_gaps"))
    notes = manifest.get("notes")
    if not isinstance(notes, list):
        issues.append(("MISSING_NOTES", "notes"))
    else:
        for marker in REQUIRED_NOTE_MARKERS:
            if marker not in notes:
                issues.append(("MISSING_NOTE_MARKER", marker))
    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)
    print("PHASE2_TOOL_MANIFEST=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def write_manifest(path: Path, manifest: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def build_self_test_manifest() -> dict:
    return {
        **REQUIRED_TOP_LEVEL,
        "present_surfaces": {
            category: list(entries)
            for category, entries in REQUIRED_PRESENT_SURFACES.items()
        },
        "repo_reality_gaps": [],
        "notes": list(REQUIRED_NOTE_MARKERS),
    }


def run_self_test() -> int:
    expected_case_count = (
        1
        + len(REQUIRED_TOP_LEVEL)
        + 1
        + len(REQUIRED_PRESENT_SURFACES)
        + sum(len(entries) for entries in REQUIRED_PRESENT_SURFACES.values())
        + 1
        + 1
        + len(REQUIRED_NOTE_MARKERS)
        + 1
    )
    checks_run = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_tool_manifest_") as tmp_dir:
        root = Path(tmp_dir)
        manifest_path = root / MANIFEST
        write_manifest(manifest_path, build_self_test_manifest())
        assert collect_issues(root) == []
        checks_run += 1

        for key in REQUIRED_TOP_LEVEL:
            manifest = build_self_test_manifest()
            manifest[key] = "broken"
            write_manifest(manifest_path, manifest)
            assert ("TOP_LEVEL_MISMATCH", key) in collect_issues(root)
            checks_run += 1

        manifest = build_self_test_manifest()
        manifest["present_surfaces"] = []
        write_manifest(manifest_path, manifest)
        assert ("MISSING_PRESENT_SURFACES", "present_surfaces") in collect_issues(root)
        checks_run += 1

        for category, entries in REQUIRED_PRESENT_SURFACES.items():
            manifest = build_self_test_manifest()
            del manifest["present_surfaces"][category]
            write_manifest(manifest_path, manifest)
            assert ("MISSING_SURFACE_CATEGORY", category) in collect_issues(root)
            checks_run += 1
            for entry in entries:
                manifest = build_self_test_manifest()
                manifest["present_surfaces"][category].remove(entry)
                write_manifest(manifest_path, manifest)
                assert ("MISSING_SURFACE_ENTRY", f"{category}:{entry}") in collect_issues(root)
                checks_run += 1

        manifest = build_self_test_manifest()
        manifest["repo_reality_gaps"] = ["unexpected-gap"]
        write_manifest(manifest_path, manifest)
        assert ("NONEMPTY_REPO_REALITY_GAPS", "repo_reality_gaps") in collect_issues(root)
        checks_run += 1

        manifest = build_self_test_manifest()
        manifest["notes"] = "broken"
        write_manifest(manifest_path, manifest)
        assert ("MISSING_NOTES", "notes") in collect_issues(root)
        checks_run += 1

        for marker in REQUIRED_NOTE_MARKERS:
            manifest = build_self_test_manifest()
            manifest["notes"].remove(marker)
            write_manifest(manifest_path, manifest)
            assert ("MISSING_NOTE_MARKER", marker) in collect_issues(root)
            checks_run += 1

        manifest_path.unlink()
        try:
            collect_issues(root)
        except SystemExit as exc:
            assert "required file missing" in str(exc)
            checks_run += 1
        else:
            raise AssertionError("missing manifest did not abort")

    assert checks_run == expected_case_count
    print("PHASE2_TOOL_MANIFEST_SELF_TEST=pass")
    print(f"PHASE2_TOOL_MANIFEST_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Keep the Phase 2 tool manifest aligned with the current repo-tooling packet."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run the built-in contract self-test")
    args = parser.parse_args()
    if args.self_test:
        return run_self_test()
    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)
    print("PHASE2_TOOL_MANIFEST=pass")
    print(f"PHASE2_TOOL_MANIFEST_REQUIRED_SURFACE_COUNT={sum(len(entries) for entries in REQUIRED_PRESENT_SURFACES.values())}")
    print(f"PHASE2_TOOL_MANIFEST_REQUIRED_NOTE_COUNT={len(REQUIRED_NOTE_MARKERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
