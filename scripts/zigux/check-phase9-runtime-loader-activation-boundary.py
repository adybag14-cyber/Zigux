#!/usr/bin/env python3
"""Validate the Phase 9 runtime-loader activation-boundary packet.

This checker stays narrowly focused on the shared runtime-loader control
surface: the runtime packet may preserve a shared ``command_name`` handoff,
but Phase 8 still owns argv-policy and environment-derived activation.
"""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path


REPO_REQUIRED_MARKERS: dict[str, tuple[str, ...]] = {
    "Documentation/zigux/phase9-runtime-loader-gap-survey.md": (
        "shared `command_name` field",
        "argv policy",
        "environment-derived activation cues",
        "tools/lib/subcmd/exec-cmd.zig",
        "tools/lib/subcmd/help.zig",
        "ExtractArgv0Result.command_name",
        "Config.exec_path_env",
        "PERF_EXEC_PATH",
        "PATH",
        "LINES",
        "COLUMNS",
    ),
    "Documentation/zigux/phase9-runtime-loader-substrate-plan.md": (
        "optional shared `command_name` handoff field",
        "Phase 8 owner",
        "ExtractArgv0Result.command_name",
        "Config.exec_path_env",
        "PERF_EXEC_PATH",
        "PATH",
    ),
    "zigux/tests/runtime_loader_gap_manifest.json": (
        "\"shared_runtime_loader_field\": \"shared command_name field\"",
        "\"id\": \"runtime-loader-command-environment-controls\"",
        "Phase 8 tooling",
        "argv-policy",
        "environment-derived activation handling",
    ),
    "zigux/kernel/runtime_loader.zig": (
        "command_name: ?[]const u8",
        "pub fn keepsCommandNameExplicit",
    ),
    "tools/lib/subcmd/exec-cmd.zig": (
        "pub const ExtractArgv0Result = struct",
        "command_name: []const u8",
        "exec_path_env: []const u8",
        "\"PERF_EXEC_PATH\"",
        "env.get(\"PATH\")",
    ),
    "tools/lib/subcmd/help.zig": (
        "env_lines",
        "env_columns",
        "writePrettyPrintStringListForTerminal",
    ),
    "samples/zigux/runtime_atomic64_loader.zig": (
        "command_name: ?[]const u8",
        "perf-runtime-atomic64",
        "request.keepsCommandNameExplicit()",
        "released.keepsCommandNameExplicit()",
    ),
    "samples/zigux/runtime_bitmap_loader.zig": (
        "command_name: ?[]const u8",
        "perf-runtime-bitmap",
        "request.keepsCommandNameExplicit()",
        "released.keepsCommandNameExplicit()",
    ),
    "samples/zigux/runtime_kretprobe_loader.zig": (
        "command_name: ?[]const u8",
        "perf-runtime-kretprobe",
        "request.keepsCommandNameExplicit()",
        "released.keepsCommandNameExplicit()",
    ),
}

REPO_FORBIDDEN_MARKERS: dict[str, tuple[str, ...]] = {
    "zigux/kernel/runtime_loader.zig": (
        "argv_policy",
        "activation_env",
        "\"PERF_EXEC_PATH\"",
        "\"PATH\"",
        "\"LINES\"",
        "\"COLUMNS\"",
    ),
}


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise AssertionError(f"missing required file: {path}") from exc


def _check_repo(root: Path) -> None:
    for rel_path, markers in REPO_REQUIRED_MARKERS.items():
        text = _read_text(root / rel_path)
        for marker in markers:
            if marker not in text:
                raise AssertionError(f"{rel_path} is missing marker: {marker}")

    for rel_path, markers in REPO_FORBIDDEN_MARKERS.items():
        text = _read_text(root / rel_path)
        for marker in markers:
            if marker in text:
                raise AssertionError(f"{rel_path} unexpectedly contains marker: {marker}")

    manifest_path = root / "zigux/tests/runtime_loader_gap_manifest.json"
    manifest = json.loads(_read_text(manifest_path))
    summary = manifest["survey_summary"]
    if summary["shared_command_environment_control_present"] is not False:
        raise AssertionError(
            "runtime_loader_gap_manifest.json should still mark shared_command_environment_control_present as false"
        )

    control_markers = manifest["phase8_control_surface_markers"]
    if control_markers["shared_runtime_loader_field"] != "shared command_name field":
        raise AssertionError("shared runtime-loader field marker drifted away from the command_name contract")

    command_env_gap = next(
        (gap for gap in manifest["gaps"] if gap["id"] == "runtime-loader-command-environment-controls"),
        None,
    )
    if command_env_gap is None:
        raise AssertionError("runtime_loader_gap_manifest.json is missing the runtime-loader-command-environment-controls gap")
    if command_env_gap["status"] != "blocked_on_runtime_substrate":
        raise AssertionError("runtime-loader-command-environment-controls must stay blocked_on_runtime_substrate")
    if command_env_gap["zigux_destination"] != "zigux/kernel/runtime_loader.zig":
        raise AssertionError("runtime-loader-command-environment-controls destination drifted away from zigux/kernel/runtime_loader.zig")


def _run_self_test() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        for rel_path, markers in REPO_REQUIRED_MARKERS.items():
            target = root / rel_path
            target.parent.mkdir(parents=True, exist_ok=True)
            payload = "\n".join(markers) + "\n"
            if rel_path == "zigux/tests/runtime_loader_gap_manifest.json":
                payload = json.dumps(
                    {
                        "survey_summary": {
                            "shared_command_environment_control_present": False,
                        },
                        "phase8_control_surface_markers": {
                            "shared_runtime_loader_field": "shared command_name field",
                        },
                        "gaps": [
                            {
                                "id": "runtime-loader-command-environment-controls",
                                "status": "blocked_on_runtime_substrate",
                                "zigux_destination": "zigux/kernel/runtime_loader.zig",
                                "why_now": "Phase 8 tooling still owns argv-policy and environment-derived activation handling.",
                            }
                        ],
                    },
                    indent=2,
                    sort_keys=True,
                )
            target.write_text(payload, encoding="utf-8")

        _check_repo(root)

        # Prove the checker actually fails when a key marker drifts away.
        bad_runtime_loader = root / "zigux/kernel/runtime_loader.zig"
        bad_runtime_loader.write_text(
            "command_name: ?[]const u8\npub fn keepsCommandNameExplicit\n\"PATH\"\n",
            encoding="utf-8",
        )
        try:
            _check_repo(root)
        except AssertionError as exc:
            if "unexpectedly contains marker" not in str(exc):
                raise
        else:
            raise AssertionError("self-test expected the forbidden PATH marker to fail")


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        description="Validate the Phase 9 runtime-loader activation-boundary packet."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path("."),
        help="Repository root to inspect (default: current directory).",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run the checker's built-in self-test instead of a repo inspection.",
    )
    args = parser.parse_args(argv)

    try:
        if args.self_test:
            _run_self_test()
        else:
            _check_repo(args.root.resolve())
    except AssertionError as exc:
        print(f"phase9_runtime_loader_activation_boundary=fail: {exc}", file=sys.stderr)
        return 1

    mode = "self_test" if args.self_test else "repo_check"
    print(f"phase9_runtime_loader_activation_boundary=pass mode={mode}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
