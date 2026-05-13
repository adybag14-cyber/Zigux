#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) > 2 else Path.cwd()

MANIFEST_PATH = "zigux/tests/fixtures/phase12_virtio_scsi_manifest.json"
SLICE_PATH = "Documentation/zigux/phase12-virtio-scsi-slice.md"
REPLAY_PATH = "zigux/tests/phase12_virtio_scsi_packet.zig"
BUILD_PATH = "zigux/tests/phase12_build.zig"

SLICE_MARKER = "`PHASE12_SLICE=virtio-scsi-queue-lab-support`"


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def require_file(root: Path, rel: str, errors: list[str]) -> Path | None:
    path = root / rel
    if not path.is_file():
        errors.append(f"missing:{rel}")
        return None
    return path


def contains_manifest_expectation(source: str, key: str, value: str) -> bool:
    plain = f'"{key}": "{value}"'
    escaped = plain.replace('"', '\\"')
    return plain in source or escaped in source


def validate(root: Path) -> list[str]:
    errors: list[str] = []
    manifest_path = require_file(root, MANIFEST_PATH, errors)
    slice_path = require_file(root, SLICE_PATH, errors)
    replay_path = require_file(root, REPLAY_PATH, errors)
    build_path = require_file(root, BUILD_PATH, errors)
    if errors:
        return errors

    manifest_text = read_text(manifest_path)
    slice_text = read_text(slice_path)
    replay_text = read_text(replay_path)
    build_text = read_text(build_path)

    try:
        manifest = json.loads(manifest_text)
    except json.JSONDecodeError as exc:
        return [f"manifest:json_decode:{exc.msg}"]

    lane_key = manifest.get("lane_key")
    if not isinstance(lane_key, str) or not lane_key:
        errors.append("manifest:lane_key_missing")
    elif not contains_manifest_expectation(replay_text, "lane_key", lane_key):
        errors.append(f"replay:lane_key_mismatch:{lane_key}")
    elif f"lane: `{lane_key}`" not in slice_text:
        errors.append(f"slice:lane_key_mismatch:{lane_key}")

    surveyed_commit = manifest.get("surveyed_commit")
    if not isinstance(surveyed_commit, str) or not surveyed_commit:
        errors.append("manifest:surveyed_commit_missing")
    else:
        if not contains_manifest_expectation(replay_text, "surveyed_commit", surveyed_commit):
            errors.append(f"replay:surveyed_commit_mismatch:{surveyed_commit}")
        if f"reviewed against live `master` `{surveyed_commit}`" not in slice_text:
            errors.append(f"slice:surveyed_commit_mismatch:{surveyed_commit}")

    shipped_paths = manifest.get("shipped_paths")
    if not isinstance(shipped_paths, list) or not shipped_paths:
        errors.append("manifest:shipped_paths_missing")
    else:
        for rel in shipped_paths:
            if not isinstance(rel, str):
                errors.append("manifest:shipped_paths_non_string")
                continue
            if f'"{rel}"' not in manifest_text:
                errors.append(f"manifest:missing_shipped_path_literal:{rel}")

    gap_paths = manifest.get("repo_gaps")
    if not isinstance(gap_paths, list) or not gap_paths:
        errors.append("manifest:repo_gaps_missing")
    else:
        for rel in gap_paths:
            if not isinstance(rel, str):
                errors.append("manifest:repo_gaps_non_string")
                continue
            if f"`{rel}`" not in slice_text:
                errors.append(f"slice:missing_gap_marker:{rel}")

    if SLICE_MARKER not in slice_text:
        errors.append("slice:missing_slice_marker")

    if "phase12_virtio_scsi_packet.zig" not in build_text:
        errors.append("build:missing_packet_root")
    if "phase12-virtio-scsi-packet-tests" not in build_text:
        errors.append("build:missing_packet_test_name")
    if "run_packet_tests" not in build_text:
        errors.append("build:missing_packet_runner")
    if "smoke_step.dependOn(&run_packet_tests.step);" not in build_text:
        errors.append("build:missing_packet_smoke_dependency")
    if "test_step.dependOn(&run_packet_tests.step);" not in build_text:
        errors.append("build:missing_packet_test_dependency")

    return errors


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def seed_fixture_tree(root: Path) -> None:
    write_text(
        root / MANIFEST_PATH,
        json.dumps(
            {
                "lane_key": "complex-drivers-infra",
                "phase": "Phase 12",
                "surveyed_commit": "4b5b0667d4651364ccd4b388d84c3107b64fdd6a",
                "packet": "phase12-virtio-scsi-support",
                "status": "bounded infra prep",
                "anchor": "drivers/scsi/virtio_scsi.c",
                "shipped_paths": [
                    "drivers/scsi/virtio_scsi.zig",
                    "zigux/tests/phase12_virtio_scsi.zig",
                    "zigux/tests/phase12_virtio_scsi_syntax_lab.zig",
                    "zigux/tests/phase12_virtio_scsi_repeated_replan_gate.zig",
                    "zigux/tests/phase12_build.zig",
                    "zigux/tests/phase12_virtio_scsi_packet.zig",
                    "zigux/tests/fixtures/phase12_virtio_scsi_manifest.json",
                    "scripts/zigux/check-phase12-virtio-scsi-packet.py",
                    "Documentation/zigux/phase12-virtio-scsi-slice.md",
                ],
                "repo_gaps": [
                    "drivers/nvme/host/pci.zig",
                    "Documentation/zigux/phase12-closure.md",
                ],
                "validation": [
                    "zig test zigux/tests/phase12_virtio_scsi_packet.zig",
                    "python3 scripts/zigux/check-phase12-virtio-scsi-packet.py",
                ],
            },
            indent=2,
        )
        + "\n",
    )
    write_text(
        root / SLICE_PATH,
        "\n".join(
            [
                "# Phase 12 virtio_scsi Slice",
                "",
                "- `PHASE12_SLICE=virtio-scsi-queue-lab-support`",
                "- reviewed against live `master` `4b5b0667d4651364ccd4b388d84c3107b64fdd6a`",
                "- lane: `complex-drivers-infra`",
                "- anchor: `drivers/scsi/virtio_scsi.c`",
                "",
                "## Shipped packet",
                "",
                "- `drivers/scsi/virtio_scsi.zig` is the current complex-driver scaffold on `master`",
                "- `zigux/tests/phase12_virtio_scsi_packet.zig` is the manifest-backed packet replay for this bounded infra-prep slice",
                "- `scripts/zigux/check-phase12-virtio-scsi-packet.py` fails closed if the manifest, slice note, or build route drifts",
                "",
                "## Repo-reality gaps",
                "",
                "- `drivers/nvme/host/pci.zig` is still absent on the surveyed head",
                "- `Documentation/zigux/phase12-closure.md` is still absent on the surveyed head",
            ]
        )
        + "\n",
    )
    write_text(
        root / REPLAY_PATH,
        "\n".join(
            [
                "const std = @import(\"std\");",
                'test "phase12 packet replay" {',
                '    try std.testing.expect(std.mem.indexOf(u8, "\\\"lane_key\\\": \\\"complex-drivers-infra\\\"", "\\\"lane_key\\\": \\\"complex-drivers-infra\\\"") != null);',
                '    try std.testing.expect(std.mem.indexOf(u8, "\\\"surveyed_commit\\\": \\\"4b5b0667d4651364ccd4b388d84c3107b64fdd6a\\\"", "\\\"surveyed_commit\\\": \\\"4b5b0667d4651364ccd4b388d84c3107b64fdd6a\\\"") != null);',
                "}",
            ]
        )
        + "\n",
    )
    write_text(
        root / BUILD_PATH,
        "\n".join(
            [
                "const std = @import(\"std\");",
                "",
                "pub fn build(b: *std.Build) void {",
                "    const target = b.standardTargetOptions(.{});",
                "    const optimize = b.standardOptimizeOption(.{});",
                "",
                "    const packet_root_module = b.createModule(.{",
                '        .root_source_file = b.path("phase12_virtio_scsi_packet.zig"),',
                "        .target = target,",
                "        .optimize = optimize,",
                "    });",
                "",
                "    const packet_tests = b.addTest(.{",
                '        .name = "phase12-virtio-scsi-packet-tests",',
                "        .root_module = packet_root_module,",
                "    });",
                "    const run_packet_tests = b.addRunArtifact(packet_tests);",
                "",
                '    const smoke_step = b.step("smoke", "Run Phase 12 virtio-scsi syntax smoke");',
                "    smoke_step.dependOn(&run_packet_tests.step);",
                '    const test_step = b.step("test", "Run Phase 12 virtio-scsi packet tests");',
                "    test_step.dependOn(&run_packet_tests.step);",
                "}",
            ]
        )
        + "\n",
    )


def assert_only(got: list[str], want: list[str], label: str) -> None:
    if got != want:
        got_text = ",".join(got) or "none"
        want_text = ",".join(want) or "none"
        raise SystemExit(f"phase12-virtio-scsi-packet-self-test:{label}:got={got_text}:want={want_text}")


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase12_virtio_scsi_packet_") as temp_dir:
        root = Path(temp_dir)

        seed_fixture_tree(root)
        assert_only(validate(root), [], "baseline_failed")
        case_count += 1

        seed_fixture_tree(root)
        write_text(root / SLICE_PATH, "# stale\n")
        assert_only(
            validate(root),
            [
                "slice:lane_key_mismatch:complex-drivers-infra",
                "slice:surveyed_commit_mismatch:4b5b0667d4651364ccd4b388d84c3107b64fdd6a",
                "slice:missing_gap_marker:drivers/nvme/host/pci.zig",
                "slice:missing_gap_marker:Documentation/zigux/phase12-closure.md",
                "slice:missing_slice_marker",
            ],
            "slice_drift_failed",
        )
        case_count += 1

        seed_fixture_tree(root)
        write_text(
            root / REPLAY_PATH,
            'const std = @import("std");\n'
            'test "phase12 packet replay" {\n'
            '    try std.testing.expect(std.mem.indexOf(u8, "\\"lane_key\\": \\"wrong-lane\\"", "\\"lane_key\\": \\"wrong-lane\\"") != null);\n'
            '    try std.testing.expect(std.mem.indexOf(u8, "\\"surveyed_commit\\": \\"4b5b0667d4651364ccd4b388d84c3107b64fdd6a\\"", "\\"surveyed_commit\\": \\"4b5b0667d4651364ccd4b388d84c3107b64fdd6a\\"") != null);\n'
            "}\n",
        )
        assert_only(
            validate(root),
            ["replay:lane_key_mismatch:complex-drivers-infra"],
            "lane_key_drift_failed",
        )
        case_count += 1

        seed_fixture_tree(root)
        write_text(root / BUILD_PATH, "const std = @import(\"std\");\n")
        assert_only(
            validate(root),
            [
                "build:missing_packet_root",
                "build:missing_packet_test_name",
                "build:missing_packet_runner",
                "build:missing_packet_smoke_dependency",
                "build:missing_packet_test_dependency",
            ],
            "build_drift_failed",
        )
        case_count += 1

    print(f"PHASE12_VIRTIO_SCSI_PACKET_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the Phase 12 virtio_scsi support packet stays aligned."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to validate.")
    parser.add_argument("--self-test", action="store_true", help="Run checker self-tests.")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    errors = validate(args.root)
    if errors:
        for error in errors:
            print(error)
        return 1

    print("PHASE12_VIRTIO_SCSI_PACKET=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
