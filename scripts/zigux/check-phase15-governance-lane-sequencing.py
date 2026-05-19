#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

SEQUENCING_NOTE = Path("Documentation/zigux/phase15-governance-lane-sequencing.md")
MANIFEST = Path("zigux/tests/phase15_governance_lane_sequencing_manifest.json")
REPLAY = Path("zigux/tests/phase15_governance_lane_sequencing.zig")
READINESS_MANIFEST = Path("zigux/tests/phase15_readiness_gate_manifest.json")

HANDOFF_MANIFEST = "zigux/tests/phase15_handoff_next_steps_manifest.json"
HANDOFF_CHECKER = "scripts/zigux/check-phase15-handoff-note-alignment.py"

DIRECT_PACKET_PATHS = [
    "Documentation/zigux/README.md",
    "Documentation/zigux/review-checklist.md",
    "Documentation/zigux/phase15-freeze-map-governance.md",
    "Documentation/zigux/phase15-parity-scorecard.md",
    "Documentation/zigux/phase15-architecture-council-review-process.md",
    "Documentation/zigux/phase15-indefinite-c-policy.md",
    "Documentation/zigux/phase15-readiness-gate-survey.md",
    "Documentation/zigux/phase15-handoff-next-steps-survey.md",
    "Documentation/zigux/phase15-study-only-anchor-accounting.md",
    "Documentation/zigux/phase15-shared-summary-gap.md",
    "scripts/zigux/README.md",
    "zigux/tests/README.md",
    "zigux/tests/phase15_governance_lane_sequencing_manifest.json",
    "zigux/tests/phase15_governance_lane_sequencing.zig",
    HANDOFF_MANIFEST,
    HANDOFF_CHECKER,
]

BROADER_GAP_PATHS = [
    "scripts/zigux/validate-phase15.py",
    "zigux/tests/phase15_handoff_next_steps.zig",
    "zigux/tests/phase15_build.zig",
    "zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig",
]

MAINTENANCE_REPLAY_COMMANDS = [
    "python3 scripts/zigux/check-phase15-docs-readme-alignment.py",
    "python3 scripts/zigux/check-phase15-scripts-readme-alignment.py",
    "python3 scripts/zigux/check-phase15-tests-readme-alignment.py",
    "python3 scripts/zigux/check-phase15-review-process-handoff.py",
    "python3 scripts/zigux/check-phase15-shared-summary-gap.py",
    "python3 scripts/zigux/check-phase15-handoff-note-alignment.py",
    "zig test zigux/tests/phase15_governance_lane_sequencing.zig",
]

REQUIRED_NOTE_MARKERS = [
    "PHASE15_STATUS=governance_lane_sequencing_packet_landed",
    "PHASE15_LANE_KEY=P15-Y06",
    "PHASE15_SLICE=architecture-council-governance-lane-boundaries",
    "current-master-readback-2026-05-19",
    "the dedicated handoff manifest plus focused handoff-note checker are now landed",
    "The shared reminder surfaces may say that:",
    "The shared reminder surfaces must not say that:",
    "a missing focused replay, dedicated build file, or other absent companion is already landed on current `master`",
]

REQUIRED_REPLAY_MARKERS = [
    'expectEqualStrings("P15-Y06", manifest.lane_key);',
    'expectEqualStrings("current-master-readback-2026-05-19", manifest.surveyed_commit);',
    'expectSliceContains(manifest.direct_packet_paths, "zigux/tests/phase15_handoff_next_steps_manifest.json");',
    'expectSliceContains(manifest.direct_packet_paths, "scripts/zigux/check-phase15-handoff-note-alignment.py");',
    'expectContains(sequencing_note, "The shared reminder surfaces may say that:");',
    'expectContains(sequencing_note, "The shared reminder surfaces must not say that:");',
]


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _read_json(path: Path) -> dict:
    return json.loads(_read_text(path))


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def collect_failures(root: Path) -> list[str]:
    failures: list[str] = []
    note_path = root / SEQUENCING_NOTE
    manifest_path = root / MANIFEST
    replay_path = root / REPLAY
    readiness_path = root / READINESS_MANIFEST

    for path in (note_path, manifest_path, replay_path, readiness_path):
        if not path.exists():
            failures.append(f"missing_file:{path.relative_to(root)}")
    if failures:
        return failures

    note = _read_text(note_path)
    manifest = _read_json(manifest_path)
    replay = _read_text(replay_path)
    readiness_manifest = _read_json(readiness_path)

    for marker in REQUIRED_NOTE_MARKERS:
        if marker not in note:
            failures.append(f"note:missing:{marker}")

    if manifest.get("lane_key") != "P15-Y06":
        failures.append("manifest:lane_key")
    if manifest.get("phase") != "Phase 15":
        failures.append("manifest:phase")
    if manifest.get("surveyed_commit") != "current-master-readback-2026-05-19":
        failures.append("manifest:surveyed_commit")
    if manifest.get("sequencing_note") != str(SEQUENCING_NOTE):
        failures.append("manifest:sequencing_note")
    if manifest.get("readiness_manifest") != str(READINESS_MANIFEST):
        failures.append("manifest:readiness_manifest")
    if manifest.get("shared_summary_gap_note") != "Documentation/zigux/phase15-shared-summary-gap.md":
        failures.append("manifest:shared_summary_gap_note")
    if manifest.get("direct_packet_paths") != DIRECT_PACKET_PATHS:
        failures.append("manifest:direct_packet_paths")
    if manifest.get("still_missing_broader_paths") != BROADER_GAP_PATHS:
        failures.append("manifest:still_missing_broader_paths")
    if manifest.get("maintenance_replay_commands") != MAINTENANCE_REPLAY_COMMANDS:
        failures.append("manifest:maintenance_replay_commands")

    for rel in DIRECT_PACKET_PATHS:
        if f"`{rel}`" not in note:
            failures.append(f"note:missing_direct_path:{rel}")
    for rel in BROADER_GAP_PATHS:
        if f"`{rel}`" not in note:
            failures.append(f"note:missing_gap_path:{rel}")
        if (root / rel).exists():
            failures.append(f"gap_returned:{rel}")

    readiness_direct = readiness_manifest.get("direct_packet_paths", [])
    for rel in (str(MANIFEST), str(REPLAY), HANDOFF_MANIFEST):
        if rel not in readiness_direct:
            failures.append(f"readiness_manifest:missing_direct_path:{rel}")

    for marker in REQUIRED_REPLAY_MARKERS:
        if marker not in replay:
            failures.append(f"replay:missing:{marker}")

    return failures


def _sample_note() -> str:
    direct_paths = "\n".join(f"- `{rel}`" for rel in DIRECT_PACKET_PATHS)
    broader_paths = "\n".join(f"- `{rel}`" for rel in BROADER_GAP_PATHS)
    replay_commands = "\n".join(f"  - `{command}`" for command in MAINTENANCE_REPLAY_COMMANDS)
    return f"""# Phase 15 Governance Lane Sequencing

- `PHASE15_STATUS=governance_lane_sequencing_packet_landed`
- `PHASE15_LANE_KEY=P15-Y06`
- `PHASE15_SLICE=architecture-council-governance-lane-boundaries`
- surveyed against dated current-master readback marker `current-master-readback-2026-05-19`
- the dedicated handoff manifest plus focused handoff-note checker are now landed

The shared reminder surfaces may say that:

- no Architecture Council approval is currently recorded for a freeze-map status change

The shared reminder surfaces must not say that:

- a deep-core status change has been approved
- a freeze-in-C anchor is ready for a direct Zigux bridge
- a missing focused replay, dedicated build file, or other absent companion is already landed on current `master`

## Current Repo-Reality Gaps

{broader_paths}

## Direct Packet

{direct_paths}

## Maintenance-Mode Handoff

{replay_commands}
"""


def _sample_manifest() -> str:
    return json.dumps(
        {
            "lane_key": "P15-Y06",
            "phase": "Phase 15",
            "surveyed_commit": "current-master-readback-2026-05-19",
            "sequencing_note": str(SEQUENCING_NOTE),
            "readiness_manifest": str(READINESS_MANIFEST),
            "shared_summary_gap_note": "Documentation/zigux/phase15-shared-summary-gap.md",
            "direct_packet_paths": DIRECT_PACKET_PATHS,
            "still_missing_broader_paths": BROADER_GAP_PATHS,
            "maintenance_replay_commands": MAINTENANCE_REPLAY_COMMANDS,
        },
        indent=2,
    ) + "\n"


def _sample_replay() -> str:
    return """const std = @import(\"std\");

fn expectSliceContains(haystack: []const []const u8, needle: []const u8) !void {
    for (haystack) |entry| {
        if (std.mem.eql(u8, entry, needle)) return;
    }
    return error.TestUnexpectedResult;
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

const SequencingManifest = struct {
    lane_key: []const u8,
    phase: []const u8,
    surveyed_commit: []const u8,
    sequencing_note: []const u8,
    direct_packet_paths: []const []const u8,
    still_missing_broader_paths: []const []const u8,
    maintenance_replay_commands: []const []const u8,
};

test \"phase 15 governance-lane sequencing manifest records the current direct packet and gaps\" {
    const manifest_json =
        \\\\{
        \\\\  \"lane_key\": \"P15-Y06\",
        \\\\  \"phase\": \"Phase 15\",
        \\\\  \"surveyed_commit\": \"current-master-readback-2026-05-19\",
        \\\\  \"sequencing_note\": \"Documentation/zigux/phase15-governance-lane-sequencing.md\",
        \\\\  \"direct_packet_paths\": [
        \\\\    \"zigux/tests/phase15_governance_lane_sequencing_manifest.json\",
        \\\\    \"zigux/tests/phase15_governance_lane_sequencing.zig\",
        \\\\    \"zigux/tests/phase15_handoff_next_steps_manifest.json\",
        \\\\    \"scripts/zigux/check-phase15-handoff-note-alignment.py\",
        \\\\    \"Documentation/zigux/phase15-study-only-anchor-accounting.md\",
        \\\\    \"Documentation/zigux/phase15-shared-summary-gap.md\"
        \\\\  ],
        \\\\  \"still_missing_broader_paths\": [
        \\\\    \"scripts/zigux/validate-phase15.py\"
        \\\\  ],
        \\\\  \"maintenance_replay_commands\": [
        \\\\    \"python3 scripts/zigux/check-phase15-handoff-note-alignment.py\",
        \\\\    \"zig test zigux/tests/phase15_governance_lane_sequencing.zig\"
        \\\\  ]
        \\\\}
    ;
    const parsed = try std.json.parseFromSlice(SequencingManifest, std.testing.allocator, manifest_json, .{
        .ignore_unknown_fields = true,
    });
    defer parsed.deinit();
    const manifest = parsed.value;

    try std.testing.expectEqualStrings(\"P15-Y06\", manifest.lane_key);
    try std.testing.expectEqualStrings(\"current-master-readback-2026-05-19\", manifest.surveyed_commit);
    try expectSliceContains(manifest.direct_packet_paths, \"zigux/tests/phase15_handoff_next_steps_manifest.json\");
    try expectSliceContains(manifest.direct_packet_paths, \"scripts/zigux/check-phase15-handoff-note-alignment.py\");
}

test \"phase 15 governance-lane sequencing note keeps explicit shared-surface boundaries\" {
    const sequencing_note =
        \\\\The shared reminder surfaces may say that:
        \\\\
        \\\\The shared reminder surfaces must not say that:
    ;
    try expectContains(sequencing_note, \"The shared reminder surfaces may say that:\");
    try expectContains(sequencing_note, \"The shared reminder surfaces must not say that:\");
}
"""


def _sample_readiness_manifest() -> str:
    return json.dumps(
        {
            "direct_packet_paths": [
                str(MANIFEST),
                str(REPLAY),
                HANDOFF_MANIFEST,
            ]
        },
        indent=2,
    ) + "\n"


def _seed_repo(root: Path) -> None:
    _write(root / SEQUENCING_NOTE, _sample_note())
    _write(root / MANIFEST, _sample_manifest())
    _write(root / REPLAY, _sample_replay())
    _write(root / READINESS_MANIFEST, _sample_readiness_manifest())
    for rel in DIRECT_PACKET_PATHS:
        if rel in {str(MANIFEST), str(REPLAY)}:
            continue
        _write(root / rel, "present\n")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="phase15_governance_lane_") as tmpdir:
        root = Path(tmpdir)
        _seed_repo(root)
        failures = collect_failures(root)
        if failures:
            raise AssertionError(f"baseline fixture should pass: {failures}")

        note_root = root / "note"
        _seed_repo(note_root)
        _write((note_root / SEQUENCING_NOTE), _sample_note().replace("The shared reminder surfaces may say that:\n\n", "", 1))
        failures = collect_failures(note_root)
        if failures != ["note:missing:The shared reminder surfaces may say that:"]:
            raise AssertionError(f"unexpected note failure: {failures}")

        gap_root = root / "gap"
        _seed_repo(gap_root)
        _write(gap_root / "scripts/zigux/validate-phase15.py", "present\n")
        failures = collect_failures(gap_root)
        if failures != ["gap_returned:scripts/zigux/validate-phase15.py"]:
            raise AssertionError(f"unexpected gap failure: {failures}")

        readiness_root = root / "readiness"
        _seed_repo(readiness_root)
        readiness = _read_json(readiness_root / READINESS_MANIFEST)
        readiness["direct_packet_paths"].remove(str(REPLAY))
        _write(readiness_root / READINESS_MANIFEST, json.dumps(readiness, indent=2) + "\n")
        failures = collect_failures(readiness_root)
        if failures != [f"readiness_manifest:missing_direct_path:{REPLAY}"]:
            raise AssertionError(f"unexpected readiness failure: {failures}")

        replay_root = root / "replay"
        _seed_repo(replay_root)
        _write(replay_root / REPLAY, _sample_replay().replace('expectContains(sequencing_note, \"The shared reminder surfaces must not say that:\");\n', "", 1))
        failures = collect_failures(replay_root)
        expected = ['replay:missing:expectContains(sequencing_note, "The shared reminder surfaces must not say that:");']
        if failures != expected:
            raise AssertionError(f"unexpected replay failure: {failures}")

    print("PHASE15_GOVERNANCE_LANE_SEQUENCING_SELF_TEST=pass")
    print("PHASE15_GOVERNANCE_LANE_SEQUENCING_SELF_TEST_CASES=4")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify that the Phase 15 governance-lane sequencing packet stays aligned with the landed Architecture Council source-of-truth surfaces."
    )
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = collect_failures(args.root)
    if failures:
        for failure in failures:
            print(failure)
        return 1

    print("PHASE15_GOVERNANCE_LANE_SEQUENCING=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
