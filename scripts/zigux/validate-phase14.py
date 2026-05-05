#!/usr/bin/env python3
"""PHASE14_VALIDATE_PACKET=shared_smoke

Fail-closed validator for the current shared Phase 14 smoke packet.
This packet is still a one-shard smoke-plus-full-bundle replay surface on master.
"""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path

MARKER = "PHASE14_VALIDATE_PACKET=shared_smoke"
REQUIRED_COMMANDS = [
    "make -C zigux phase14-smoke",
    "zig build phase14-smoke --build-file zigux/tests/phase14_build.zig --summary all",
    "make -C zigux phase14-test",
    "zig build test --build-file zigux/tests/phase14_build.zig --summary all",
    "make -C zigux phase14",
]
REQUIRED_SURFACES = [
    ("Documentation/zigux/README.md", "Phase 14 notes"),
    ("Documentation/zigux/phase14-end-to-end-smoke-survey.md", "PHASE14_VALIDATE_ENTRYPOINT=absent_on_master"),
    ("Documentation/zigux/phase14-release-boundary-survey.md", "PHASE14_RELEASE_BOUNDARY=present"),
    ("Documentation/zigux/freeze-map.md", "kernel/workqueue.c"),
    ("Documentation/zigux/review-checklist.md", "shared Phase 14 smoke packet"),
    ("zigux/tests/README.md", "keep the current Phase 14 smoke packet reviewable"),
    ("zigux/tests/phase14_build.zig", "phase14-smoke"),
    ("zigux/tests/phase14_workqueue_bridge.zig", "phase14 workqueue bridge manifest records the boundary-map foothold and remaining gap"),
    ("zigux/tests/phase14_skbuff_bridge.zig", "phase14 skbuff bridge manifest records the boundary-map foothold and frozen ownership gap"),
    ("zigux/tests/phase14_ring_buffer_survey.zig", "phase 14 ring-buffer survey manifest records the study-only gap without inventing a port"),
    ("zigux/tests/phase14_rcu_tree_survey.zig", "phase 14 rcu tree survey manifest records the freeze-boundary gap without inventing a bridge"),
    ("zigux/tests/phase14_end_to_end_smoke_survey.zig", "phase14 shared smoke survey confirms the current packet surfaces"),
    ("zigux/tests/phase14_end_to_end_smoke_manifest.json", "phase14_shared_smoke_packet"),
    ("zigux/Makefile", "phase14: phase14-smoke phase14-test"),
]
REQUIRED_FILE_MARKERS = {
    "Documentation/zigux/phase14-end-to-end-smoke-survey.md": [
        "PHASE14_VALIDATE_ENTRYPOINT=absent_on_master",
        "PHASE14_COMPILE_ARTIFACT_COUNT=5",
        "PHASE14_FOCUSED_SHARD_COUNT=1",
    ],
    "zigux/Makefile": [
        "phase14-smoke:",
        "phase14-test:",
        "phase14: phase14-smoke phase14-test",
    ],
    "zigux/tests/phase14_build.zig": [
        'b.step("phase14-smoke", "Run the focused Phase 14 end-to-end smoke survey")',
        "test_step.dependOn(&run_phase14_end_to_end_smoke_tests.step);",
    ],
    "zigux/tests/phase14_end_to_end_smoke_survey.zig": [
        "phase14 shared smoke survey confirms the current packet surfaces",
        'expectEqual(@as(usize, 5), manifest.commands.len);',
        'expectEqual(@as(usize, 14), manifest.surfaces.len);',
    ],
}
FORBIDDEN_MARKERS = {
    "Documentation/zigux/phase14-end-to-end-smoke-survey.md": [
        "PHASE14_VALIDATE_ENTRYPOINT=make -C zigux phase14-validate",
        "PHASE14_VALIDATE_SCRIPT=python3 scripts/zigux/validate-phase14.py",
    ],
    "zigux/Makefile": [
        "phase14-validate:",
        "phase14: phase14-validate phase14-smoke phase14-test",
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

    if manifest.get("commands") != REQUIRED_COMMANDS:
        errors.append("phase14 manifest commands drifted from the current smoke-plus-full-bundle packet")

    surfaces = manifest.get("surfaces")
    if not isinstance(surfaces, list) or len(surfaces) != len(REQUIRED_SURFACES):
        errors.append("phase14 manifest surfaces drifted from the current 14-surface smoke packet")
    else:
        for surface, (path, marker) in zip(surfaces, REQUIRED_SURFACES):
            if surface.get("path") != path:
                errors.append(f"manifest surface path drift for {path}")
            if surface.get("required_marker") != marker:
                errors.append(f"manifest surface marker drift for {path}")

    for rel_path, markers in REQUIRED_FILE_MARKERS.items():
        path = root / rel_path
        if not path.exists():
            errors.append(f"missing file: {rel_path}")
            continue
        text = read_text(path)
        for marker in markers:
            if marker not in text:
                errors.append(f"missing marker in {rel_path}: {marker}")

    for rel_path, markers in FORBIDDEN_MARKERS.items():
        path = root / rel_path
        if not path.exists():
            errors.append(f"missing file: {rel_path}")
            continue
        text = read_text(path)
        for marker in markers:
            if marker in text:
                errors.append(f"forbidden marker still present in {rel_path}: {marker}")

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
                for path, marker in REQUIRED_SURFACES
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
        for rel_path, marker in REQUIRED_SURFACES:
            path = root / rel_path
            if not path.exists():
                write_text(path, marker + "\n")
        for rel_path in FORBIDDEN_MARKERS:
            if rel_path not in REQUIRED_FILE_MARKERS:
                write_text(root / rel_path, "")

        errors = check(root)
        if errors:
            print("self-test expected success but failed:", file=sys.stderr)
            for error in errors:
                print(f"- {error}", file=sys.stderr)
            return 1

        broken_path = root / "Documentation/zigux/phase14-end-to-end-smoke-survey.md"
        broken_path.write_text("PHASE14_VALIDATE_ENTRYPOINT=make -C zigux phase14-validate\n", encoding="utf-8")
        errors = check(root)
        if not errors or not any("forbidden marker still present" in error or "missing marker" in error for error in errors):
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
