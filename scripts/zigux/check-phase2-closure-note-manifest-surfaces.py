#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CLOSURE_NOTE = Path("Documentation/zigux/phase2-closure.md")
MANIFEST = Path("zigux/tests/fixtures/phase2_tool_manifest.json")

SURFACE_EXPECTATIONS: dict[str, tuple[str, ...]] = {
    "artifact_support": (
        "scripts/zigux/check-phase2-artifact-tools-manifest.py",
        "scripts/zigux/artifact_diff.py",
        "zigux/tests/fixtures/phase2_artifact_tools_manifest.json",
    ),
    "cross_route_support": (
        "scripts/zigux/check-phase2-cross.py",
        "zigux/tests/fixtures/phase2_cross_targets.json",
    ),
    "fixdep_support": (
        "scripts/zigux/check-phase2-fixdep-gate.py",
        "scripts/zigux/check-fixdep-diff.py",
        "scripts/zigux/fixdep.zig",
        "zigux/tests/fixtures/fixdep/cases.json",
    ),
    "make_wrappers": (
        "make -C zigux phase2-toolchain",
        "make -C zigux phase2-tools",
        "make -C zigux phase2-kconfig",
        "make -C zigux phase2-cross",
        "make -C zigux phase2-genksyms",
        "make -C zigux phase2-fixdep",
        "make -C zigux phase2-validate",
        "make -C zigux phase2",
    ),
    "policy": ("scripts/zigux/zig-toolchain-policy.json",),
}

NOTE_MARKERS: dict[str, tuple[str, ...]] = {
    "artifact_support": (
        "`scripts/zigux/check-phase2-artifact-tools-manifest.py`",
        "`scripts/zigux/artifact_diff.py`",
        "`zigux/tests/fixtures/phase2_artifact_tools_manifest.json`",
    ),
    "cross_route_support": (
        "`scripts/zigux/check-phase2-cross.py`",
        "`zigux/tests/fixtures/phase2_cross_targets.json`",
    ),
    "fixdep_support": (
        "`scripts/zigux/check-phase2-fixdep-gate.py`",
        "`scripts/zigux/check-fixdep-diff.py`",
        "`scripts/zigux/fixdep.zig`",
        "`zigux/tests/fixtures/fixdep/cases.json`",
    ),
    "make_wrappers": (
        "`make -C zigux phase2-toolchain`",
        "`make -C zigux phase2-tools`",
        "`make -C zigux phase2-kconfig`",
        "`make -C zigux phase2-cross`",
        "`make -C zigux phase2-genksyms`",
        "`make -C zigux phase2-fixdep`",
        "`make -C zigux phase2-validate`",
        "`make -C zigux phase2`",
    ),
    "policy": ("`scripts/zigux/zig-toolchain-policy.json`",),
}


def read_text(root: Path, rel: Path) -> str:
    path = root / rel
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def write_text(root: Path, rel: Path, content: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def read_manifest(root: Path) -> dict[str, object]:
    path = root / MANIFEST
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid json in required file: {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise SystemExit(f"invalid manifest root: {path}")
    return data


def require_surface_list(
    issues: list[tuple[str, str]],
    present_surfaces: object,
    surface: str,
) -> list[str] | None:
    if not isinstance(present_surfaces, dict):
        issues.append(("INVALID_MANIFEST_SHAPE", "present_surfaces"))
        return None
    value = present_surfaces.get(surface)
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        issues.append(("INVALID_MANIFEST_SHAPE", surface))
        return None
    return value


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    note_text = read_text(root, CLOSURE_NOTE)
    manifest = read_manifest(root)
    present_surfaces = manifest.get("present_surfaces")

    for surface, manifest_members in SURFACE_EXPECTATIONS.items():
        actual_members = require_surface_list(issues, present_surfaces, surface)
        if actual_members is not None:
            for member in manifest_members:
                if member not in actual_members:
                    issues.append(("MISSING_MANIFEST_SURFACE_MEMBER", f"{surface}:{member}"))
        for marker in NOTE_MARKERS[surface]:
            if marker not in note_text:
                issues.append(("MISSING_CLOSURE_NOTE_MARKER", f"{surface}:{marker}"))

    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)

    print("PHASE2_CLOSURE_NOTE_MANIFEST_SURFACES=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def build_sample_root(root: Path) -> None:
    manifest = {
        "phase": "Phase 2",
        "status": "active",
        "repo_reality_gaps": [],
        "present_surfaces": {
            surface: list(expectations)
            for surface, expectations in SURFACE_EXPECTATIONS.items()
        },
    }
    note_lines = [
        "# Phase 2 Closure",
        "",
        "## Surface Coverage",
        "",
    ]
    for surface in SURFACE_EXPECTATIONS:
        note_lines.append(f"### {surface}")
        note_lines.extend(f"- {marker}" for marker in NOTE_MARKERS[surface])
        note_lines.append("")

    write_text(root, CLOSURE_NOTE, "\n".join(note_lines))
    write_text(root, MANIFEST, json.dumps(manifest, indent=2) + "\n")


def write_sample_root(root: Path) -> int:
    build_sample_root(root)
    print(f"PHASE2_CLOSURE_NOTE_MANIFEST_SURFACES_SAMPLE_ROOT={root}")
    return 0


def run_self_test() -> int:
    checks = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_closure_note_surfaces_") as tmp_dir:
        root = Path(tmp_dir)

        build_sample_root(root)
        assert collect_issues(root) == []
        checks += 1

        for surface, markers in NOTE_MARKERS.items():
            for marker in markers:
                build_sample_root(root)
                note_path = root / CLOSURE_NOTE
                note_path.write_text(note_path.read_text(encoding="utf-8").replace(marker, "", 1), encoding="utf-8")
                assert ("MISSING_CLOSURE_NOTE_MARKER", f"{surface}:{marker}") in collect_issues(root)
                checks += 1

        for surface, members in SURFACE_EXPECTATIONS.items():
            for member in members:
                build_sample_root(root)
                manifest_path = root / MANIFEST
                payload = json.loads(manifest_path.read_text(encoding="utf-8"))
                payload["present_surfaces"][surface].remove(member)
                manifest_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
                assert ("MISSING_MANIFEST_SURFACE_MEMBER", f"{surface}:{member}") in collect_issues(root)
                checks += 1

        build_sample_root(root)
        manifest_path = root / MANIFEST
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
        payload["present_surfaces"]["policy"] = "scripts/zigux/zig-toolchain-policy.json"
        manifest_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert ("INVALID_MANIFEST_SHAPE", "policy") in collect_issues(root)
        checks += 1

        build_sample_root(root)
        manifest_path = root / MANIFEST
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
        payload["present_surfaces"] = []
        manifest_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert ("INVALID_MANIFEST_SHAPE", "present_surfaces") in collect_issues(root)
        checks += 1

    print("PHASE2_CLOSURE_NOTE_MANIFEST_SURFACES_SELF_TEST=pass")
    print(f"PHASE2_CLOSURE_NOTE_MANIFEST_SURFACES_SELF_TEST_CASE_COUNT={checks}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Fail closed when the Phase 2 closure note stops naming the refreshed manifest-surface packet."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    parser.add_argument("--write-sample-root", type=Path, help="Write a passing sample root")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root is not None:
        return write_sample_root(args.write_sample_root.resolve())

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("PHASE2_CLOSURE_NOTE_MANIFEST_SURFACES=pass")
    print(f"PHASE2_CLOSURE_NOTE_MANIFEST_SURFACE_COUNT={len(SURFACE_EXPECTATIONS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
