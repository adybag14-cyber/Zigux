#!/usr/bin/env python3
"""Fail-close the bounded Phase 2 scripts-root tooling inventory."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DOC_REL = Path("Documentation/zigux/phase2-scripts-root-tooling-inventory.md")
MANIFEST_REL = Path("zigux/tests/fixtures/phase2_scripts_root_tooling_inventory.json")


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def read_manifest(path: Path) -> dict[str, object]:
    try:
        payload = json.loads(read_text(path))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid json in {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise SystemExit(f"invalid manifest shape in {path}")
    return payload


def require_string_list(payload: dict[str, object], key: str) -> tuple[str, ...]:
    value = payload.get(key)
    if not isinstance(value, list) or not value or any(not isinstance(item, str) for item in value):
        raise SystemExit(f"manifest key {key!r} must be a non-empty string list")
    return tuple(value)


def validate(root: Path) -> None:
    doc_path = root / DOC_REL
    manifest_path = root / MANIFEST_REL
    doc_text = read_text(doc_path)
    payload = read_manifest(manifest_path)

    if payload.get("phase") != "Phase 2":
        raise SystemExit("manifest phase must be 'Phase 2'")
    if payload.get("status") != "active":
        raise SystemExit("manifest status must be 'active'")
    if payload.get("focus") != "scripts-root repo tooling inventory":
        raise SystemExit("manifest focus is out of sync")

    surfaces = require_string_list(payload, "surfaces")
    commands = require_string_list(payload, "commands")

    required_doc_markers = (
        "# Phase 2 Scripts-Root Tooling Inventory",
        "## Review Surfaces",
        "## Tooling Surfaces",
        "## Fixtures And Manifests",
        "## Replay Commands",
        "## Boundary",
        "scripts/zigux/README.md",
        "bounded Phase 2 checklist for toolchain pinning, local-first archive bootstrap, kbuild, kconfig, genksyms, fixdep, cross-route, manifest, and make-wrapper follow-through.",
    )
    missing_markers = [marker for marker in required_doc_markers if marker not in doc_text]
    if missing_markers:
        raise SystemExit(f"inventory note missing required markers: {missing_markers}")

    missing_surface_files = [surface for surface in surfaces if not (root / surface).exists()]
    if missing_surface_files:
        raise SystemExit(f"inventory manifest references missing surfaces: {missing_surface_files}")

    missing_surface_mentions = [surface for surface in surfaces if f"`{surface}`" not in doc_text]
    if missing_surface_mentions:
        raise SystemExit(f"inventory note missing surface mentions: {missing_surface_mentions}")

    missing_command_mentions = [command for command in commands if f"`{command}`" not in doc_text]
    if missing_command_mentions:
        raise SystemExit(f"inventory note missing command mentions: {missing_command_mentions}")



def run_self_test() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        manifest = {
            "phase": "Phase 2",
            "status": "active",
            "focus": "scripts-root repo tooling inventory",
            "surfaces": [
                "Documentation/zigux/phase2-closure.md",
                "Documentation/zigux/phase2-toolchain-bootstrap-notes.md",
                "Documentation/zigux/review-checklist.md",
                "scripts/zigux/README.md",
                "zigux/tests/README.md",
                "scripts/zigux/check-zig-toolchain.py",
                "scripts/zigux/check-phase2-kbuild-routes.py",
                "scripts/zigux/check-phase2-tool-manifest.py",
                "zigux/tests/fixtures/phase2_tool_manifest.json",
                "zigux/Makefile",
                "third_party/README.md",
                "third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz"
            ],
            "commands": [
                "python3 scripts/zigux/check-phase2-scripts-root-tooling-inventory.py --self-test",
                "python3 scripts/zigux/check-phase2-scripts-root-tooling-inventory.py",
                "make -C zigux phase2-toolchain",
                "make -C zigux phase2-validate",
                "make -C zigux phase2"
            ]
        }
        for surface in manifest["surfaces"]:
            target = root / surface
            target.parent.mkdir(parents=True, exist_ok=True)
            if str(surface).endswith(".json"):
                target.write_text("{}\n", encoding="utf-8")
            else:
                target.write_text("stub\n", encoding="utf-8")

        (root / MANIFEST_REL).parent.mkdir(parents=True, exist_ok=True)
        (root / MANIFEST_REL).write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        (root / DOC_REL).parent.mkdir(parents=True, exist_ok=True)
        (root / DOC_REL).write_text(
            """# Phase 2 Scripts-Root Tooling Inventory

This note keeps the current Phase 2 repo-tooling packet explicit from the scripts root.

## Review Surfaces

- `Documentation/zigux/phase2-closure.md`
- `Documentation/zigux/phase2-toolchain-bootstrap-notes.md`
- `Documentation/zigux/review-checklist.md`
- `scripts/zigux/README.md`
- `zigux/tests/README.md`

## Tooling Surfaces

- `scripts/zigux/check-zig-toolchain.py`
- `scripts/zigux/check-phase2-kbuild-routes.py`
- `scripts/zigux/check-phase2-tool-manifest.py`

## Fixtures And Manifests

- `zigux/tests/fixtures/phase2_tool_manifest.json`
- `third_party/README.md`
- `third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz`
- `zigux/Makefile`

## Replay Commands

- `python3 scripts/zigux/check-phase2-scripts-root-tooling-inventory.py --self-test`
- `python3 scripts/zigux/check-phase2-scripts-root-tooling-inventory.py`
- `make -C zigux phase2-toolchain`
- `make -C zigux phase2-validate`
- `make -C zigux phase2`

## Boundary

`scripts/zigux/README.md` remains the broader scripts-root reminder surface. This inventory is the bounded Phase 2 checklist for toolchain pinning, local-first archive bootstrap, kbuild, kconfig, genksyms, fixdep, cross-route, manifest, and make-wrapper follow-through.
""",
            encoding="utf-8",
        )
        validate(root)



def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--self-test", action="store_true")
    return parser.parse_args()



def main() -> None:
    args = parse_args()
    if args.self_test:
        run_self_test()
        return
    validate(args.root.resolve())


if __name__ == "__main__":
    main()
