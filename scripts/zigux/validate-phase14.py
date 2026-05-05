#!/usr/bin/env python3
"""PHASE14_VALIDATE_PACKET=shared_smoke

Fail-closed validator for the shared Phase 14 smoke packet.
"""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path

MARKER = "PHASE14_VALIDATE_PACKET=shared_smoke"

REQUIRED_COMMANDS = [
    "make -C zigux phase14-validate",
    "make -C zigux phase14-smoke",
    "zig build phase14-smoke --build-file zigux/tests/phase14_build.zig --summary all",
    "make -C zigux phase14-test",
    "make -C zigux phase14",
    "zig build test --build-file zigux/tests/phase14_build.zig --summary all",
]

REQUIRED_SURFACES = {
    "scripts/zigux/README.md": "make -C zigux phase14-validate",
    "scripts/zigux/validate-phase14.py": MARKER,
    ".github/workflows/zigux-bootstrap.yml": "Validate Phase 14 shared smoke packet",
}

REQUIRED_FILE_MARKERS = {
    "Documentation/zigux/phase14-end-to-end-smoke-survey.md": [
        "PHASE14_VALIDATE_ENTRYPOINT=make -C zigux phase14-validate",
        "PHASE14_VALIDATE_SCRIPT=python3 scripts/zigux/validate-phase14.py",
    ],
    "scripts/zigux/README.md": [
        "python3 scripts/zigux/validate-phase14.py",
        "make -C zigux phase14-validate",
    ],
    "scripts/zigux/validate-phase14.py": [MARKER],
    "zigux/tests/phase14_end_to_end_smoke_survey.zig": [
        "make -C zigux phase14-validate",
        "phase14: phase14-validate phase14-smoke phase14-test",
    ],
    "zigux/Makefile": [
        "phase14-validate:",
        "phase14: phase14-validate phase14-smoke phase14-test",
    ],
    ".github/workflows/zigux-bootstrap.yml": [
        "Validate Phase 14 shared smoke packet",
        "make -C zigux phase14-validate",
    ],
}


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def check(root: Path) -> list[str]:
    errors: list[str] = []

    manifest_path = root / "zigux/tests/phase14_end_to_end_smoke_manifest.json"
    if not manifest_path.exists():
        return [f"missing file: {manifest_path.as_posix()}"]

    try:
        manifest = json.loads(read_text(manifest_path))
    except json.JSONDecodeError as exc:
        return [f"invalid json in {manifest_path.as_posix()}: {exc}"]

    commands = manifest.get("commands")
    if commands != REQUIRED_COMMANDS:
        errors.append("phase14 manifest commands drifted from the shared validate/smoke/test packet")

    surfaces = {
        surface.get("path"): surface.get("required_marker")
        for surface in manifest.get("surfaces", [])
        if isinstance(surface, dict)
    }
    for path, marker in REQUIRED_SURFACES.items():
        if surfaces.get(path) != marker:
            errors.append(f"manifest surface drift for {path}")

    for rel_path, markers in REQUIRED_FILE_MARKERS.items():
        path = root / rel_path
        if not path.exists():
            errors.append(f"missing file: {rel_path}")
            continue
        text = read_text(path)
        for marker in markers:
            if marker not in text:
                errors.append(f"missing marker in {rel_path}: {marker}")

    return errors


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)

        manifest = {
            "lane_key": "core-adjacent",
            "phase": "Phase 14",
            "packet_name": "phase14_shared_smoke_packet",
            "focus": "study_only_shared_smoke_packet",
            "rollback_owner": "keep the freeze-map anchors in C and reopen only with stronger evidence",
            "commands": REQUIRED_COMMANDS,
            "surfaces": [
                {"path": path, "required_marker": marker}
                for path, marker in REQUIRED_SURFACES.items()
            ],
            "blocked_anchors": [
                "kernel/workqueue.c",
                "kernel/trace/ring_buffer.c",
                "kernel/rcu/tree.c",
                "net/core/skbuff.c",
            ],
        }
        write_text(
            root / "zigux/tests/phase14_end_to_end_smoke_manifest.json",
            json.dumps(manifest, indent=2) + "\n",
        )

        for rel_path, markers in REQUIRED_FILE_MARKERS.items():
            write_text(root / rel_path, "\n".join(markers) + "\n")

        errors = check(root)
        if errors:
            print("self-test expected success but failed:", file=sys.stderr)
            for error in errors:
                print(f"- {error}", file=sys.stderr)
            return 1

        broken_path = root / "Documentation/zigux/phase14-end-to-end-smoke-survey.md"
        broken_path.write_text("PHASE14_VALIDATE_ENTRYPOINT=absent_on_master\n", encoding="utf-8")
        errors = check(root)
        if not errors or not any("PHASE14_VALIDATE_SCRIPT=python3 scripts/zigux/validate-phase14.py" in error for error in errors):
            print("self-test expected failure when survey markers drifted", file=sys.stderr)
            return 1

    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true", help="run the built-in validator self-test")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    errors = check(repo_root())
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1

    print("phase14 shared smoke packet validated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
