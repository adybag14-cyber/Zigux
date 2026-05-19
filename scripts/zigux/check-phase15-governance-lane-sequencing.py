#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

SEQUENCING_NOTE_PATH = Path("Documentation/zigux/phase15-governance-lane-sequencing.md")
MANIFEST_PATH = Path("zigux/tests/phase15_governance_lane_sequencing_manifest.json")
REPLAY_PATH = Path("zigux/tests/phase15_governance_lane_sequencing.zig")
READINESS_MANIFEST_PATH = Path("zigux/tests/phase15_readiness_gate_manifest.json")
DOCS_README_PATH = Path("Documentation/zigux/README.md")
REVIEW_CHECKLIST_PATH = Path("Documentation/zigux/review-checklist.md")
FREEZE_GOVERNANCE_PATH = Path("Documentation/zigux/phase15-freeze-map-governance.md")
PARITY_SCORECARD_PATH = Path("Documentation/zigux/phase15-parity-scorecard.md")
REVIEW_PROCESS_PATH = Path("Documentation/zigux/phase15-architecture-council-review-process.md")
INDEFINITE_C_POLICY_PATH = Path("Documentation/zigux/phase15-indefinite-c-policy.md")
READINESS_NOTE_PATH = Path("Documentation/zigux/phase15-readiness-gate-survey.md")
HANDOFF_NOTE_PATH = Path("Documentation/zigux/phase15-handoff-next-steps-survey.md")
STUDY_ONLY_PATH = Path("Documentation/zigux/phase15-study-only-anchor-accounting.md")
SHARED_GAP_PATH = Path("Documentation/zigux/phase15-shared-summary-gap.md")
SCRIPTS_README_PATH = Path("scripts/zigux/README.md")
TESTS_README_PATH = Path("zigux/tests/README.md")
HANDOFF_MANIFEST_PATH = Path("zigux/tests/phase15_handoff_next_steps_manifest.json")

DOCS_CHECKER = "scripts/zigux/check-phase15-docs-readme-alignment.py"
SCRIPTS_CHECKER = "scripts/zigux/check-phase15-scripts-readme-alignment.py"
TESTS_CHECKER = "scripts/zigux/check-phase15-tests-readme-alignment.py"
HANDOFF_CHECKER = "scripts/zigux/check-phase15-review-process-handoff.py"
SHARED_GAP_CHECKER = "scripts/zigux/check-phase15-shared-summary-gap.py"
HANDOFF_NOTE_CHECKER = "scripts/zigux/check-phase15-handoff-note-alignment.py"

DIRECT_PACKET_PATHS = (
    str(DOCS_README_PATH),
    str(REVIEW_CHECKLIST_PATH),
    str(FREEZE_GOVERNANCE_PATH),
    str(PARITY_SCORECARD_PATH),
    str(REVIEW_PROCESS_PATH),
    str(INDEFINITE_C_POLICY_PATH),
    str(READINESS_NOTE_PATH),
    str(HANDOFF_NOTE_PATH),
    str(STUDY_ONLY_PATH),
    str(SHARED_GAP_PATH),
    str(SCRIPTS_README_PATH),
    str(TESTS_README_PATH),
    str(MANIFEST_PATH),
    str(REPLAY_PATH),
    str(HANDOFF_MANIFEST_PATH),
    HANDOFF_NOTE_CHECKER,
)

BROADER_GAP_PATHS = (
    "scripts/zigux/validate-phase15.py",
    "zigux/tests/phase15_handoff_next_steps.zig",
    "zigux/tests/phase15_build.zig",
    "zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig",
)

MAINTENANCE_REPLAY_COMMANDS = (
    f"python3 {DOCS_CHECKER}",
    f"python3 {SCRIPTS_CHECKER}",
    f"python3 {TESTS_CHECKER}",
    f"python3 {HANDOFF_CHECKER}",
    f"python3 {SHARED_GAP_CHECKER}",
    f"python3 {HANDOFF_NOTE_CHECKER}",
    "zig test zigux/tests/phase15_governance_lane_sequencing.zig",
)

REQUIRED_NOTE_MARKERS = (
    "PHASE15_STATUS=governance_lane_sequencing_packet_landed",
    "PHASE15_LANE_KEY=P15-Y06",
    "PHASE15_SLICE=architecture-council-governance-lane-boundaries",
    "PHASE15_PROVENANCE_MODE=dated_master_readback",
    "the dedicated governance-lane sequencing manifest plus focused replay are now landed",
    "the dedicated handoff manifest plus focused handoff-note checker are now landed",
    "`Documentation/zigux/freeze-map.md` and `Documentation/zigux/phase15-freeze-map-governance.md` own the freeze anchor set",
    "`Documentation/zigux/phase15-parity-scorecard.md` owns blocked-posture accounting",
    "`Documentation/zigux/phase15-architecture-council-review-process.md` owns the Architecture Council request fields",
    "`Documentation/zigux/phase15-indefinite-c-policy.md` owns the stay-in-C policy vocabulary",
    "`Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md` are shared reminder surfaces",
    "`zigux/tests/phase15_governance_lane_sequencing_manifest.json` and `zigux/tests/phase15_governance_lane_sequencing.zig` keep this sequencing note's direct machine-readable inventory and focused replay explicit",
    "`zigux/tests/phase15_handoff_next_steps_manifest.json` and `scripts/zigux/check-phase15-handoff-note-alignment.py` keep the dedicated handoff companion packet explicit",
    "1. refresh repo reality for the freeze-map anchor set and blocker posture first",
    "5. refresh readiness, handoff, study-only-accounting, shared-summary, and other reminder surfaces only after the owning packet already says the same thing",
    "no Architecture Council approval is currently recorded for a freeze-map status change",
    "a deep-core status change has been approved",
    "a freeze-in-C anchor is ready for a direct Zigux bridge",
    "a missing focused replay, dedicated build file, or other absent companion is already landed on current `master`",
    "current lane posture: `maintenance_mode`",
    "a previously missing validator-first, focused handoff replay, lane-owner, or build companion lands on current `master`",
    "Keep this lane parked until either one of the remaining missing broader Phase 15 companions lands",
)

REQUIRED_REPLAY_MARKERS = (
    'expectEqualStrings("P15-Y06", manifest.lane_key);',
    'expectEqualStrings("Phase 15", manifest.phase);',
    'expectEqualStrings("current-master-readback-2026-05-19", manifest.surveyed_commit);',
    'expectEqualStrings("Documentation/zigux/phase15-governance-lane-sequencing.md", manifest.sequencing_note);',
    'expectSliceContains(manifest.direct_packet_paths, "zigux/tests/phase15_governance_lane_sequencing_manifest.json");',
    'expectSliceContains(manifest.direct_packet_paths, "zigux/tests/phase15_governance_lane_sequencing.zig");',
    'expectSliceContains(manifest.direct_packet_paths, "zigux/tests/phase15_handoff_next_steps_manifest.json");',
    'expectSliceContains(manifest.direct_packet_paths, "scripts/zigux/check-phase15-handoff-note-alignment.py");',
    'expectSliceContains(manifest.direct_packet_paths, "Documentation/zigux/phase15-study-only-anchor-accounting.md");',
    'expectSliceContains(manifest.direct_packet_paths, "Documentation/zigux/phase15-shared-summary-gap.md");',
    'expectSliceContains(manifest.still_missing_broader_paths, "scripts/zigux/validate-phase15.py");',
    'expectSliceContains(manifest.maintenance_replay_commands, "zig test zigux/tests/phase15_governance_lane_sequencing.zig");',
    'expectSliceContains(manifest.maintenance_replay_commands, "python3 scripts/zigux/check-phase15-handoff-note-alignment.py");',
)


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _read_json(path: Path) -> dict:
    return json.loads(_read_text(path))


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def collect_failures(root: Path) -> list[str]:
    required_files = (
        SEQUENCING_NOTE_PATH,
        MANIFEST_PATH,
        REPLAY_PATH,
        READINESS_MANIFEST_PATH,
        DOCS_README_PATH,
        REVIEW_CHECKLIST_PATH,
        FREEZE_GOVERNANCE_PATH,
        PARITY_SCORECARD_PATH,
        REVIEW_PROCESS_PATH,
        INDEFINITE_C_POLICY_PATH,
        READINESS_NOTE_PATH,
        HANDOFF_NOTE_PATH,
        STUDY_ONLY_PATH,
        SHARED_GAP_PATH,
        SCRIPTS_README_PATH,
        TESTS_README_PATH,
        HANDOFF_MANIFEST_PATH,
    )
    failures: list[str] = []
    for path in required_files:
        if not (root / path).exists():
            failures.append(f"missing_file:{path}")
    if failures:
        return failures

    note = _read_text(root / SEQUENCING_NOTE_PATH)
    manifest = _read_json(root / MANIFEST_PATH)
    replay = _read_text(root / REPLAY_PATH)
    readiness_manifest = _read_json(root / READINESS_MANIFEST_PATH)

    for marker in REQUIRED_NOTE_MARKERS:
        if marker not in note:
            failures.append(f"sequencing_note:missing:{marker}")

    for command in MAINTENANCE_REPLAY_COMMANDS:
        if command not in note:
            failures.append(f"sequencing_note:missing_command:{command}")

    if manifest.get("lane_key") != "P15-Y06":
        failures.append("manifest:lane_key")
    if manifest.get("phase") != "Phase 15":
        failures.append("manifest:phase")
    if manifest.get("sequencing_note") != str(SEQUENCING_NOTE_PATH):
        failures.append("manifest:sequencing_note")
    if manifest.get("readiness_manifest") != str(READINESS_MANIFEST_PATH):
        failures.append("manifest:readiness_manifest")
    if manifest.get("shared_summary_gap_note") != str(SHARED_GAP_PATH):
        failures.append("manifest:shared_summary_gap_note")

    surveyed_commit = manifest.get("surveyed_commit")
    if not isinstance(surveyed_commit, str) or surveyed_commit not in note:
        failures.append("sequencing_note:missing_surveyed_commit")

    direct_packet_paths = manifest.get("direct_packet_paths")
    if direct_packet_paths != list(DIRECT_PACKET_PATHS):
        failures.append("manifest:direct_packet_paths")
    else:
        for rel in DIRECT_PACKET_PATHS:
            if f"`{rel}`" not in note:
                failures.append(f"sequencing_note:missing_direct_path:`{rel}`")
            if not (root / rel).exists():
                failures.append(f"repo:missing_direct_path:{rel}")

    still_missing_paths = manifest.get("still_missing_broader_paths")
    if still_missing_paths != list(BROADER_GAP_PATHS):
        failures.append("manifest:still_missing_broader_paths")
    else:
        for rel in BROADER_GAP_PATHS:
            if f"`{rel}`" not in note:
                failures.append(f"sequencing_note:missing_gap_path:`{rel}`")
            if (root / rel).exists():
                failures.append(f"repo:gap_path_returned:{rel}")

    if manifest.get("maintenance_replay_commands") != list(MAINTENANCE_REPLAY_COMMANDS):
        failures.append("manifest:maintenance_replay_commands")

    readiness_direct_paths = readiness_manifest.get("direct_packet_paths", [])
    for rel in (str(MANIFEST_PATH), str(REPLAY_PATH), str(HANDOFF_MANIFEST_PATH), HANDOFF_NOTE_CHECKER):
        if rel not in readiness_direct_paths:
            failures.append(f"readiness_manifest:missing_direct_path:{rel}")

    readiness_missing = readiness_manifest.get("still_missing_broader_paths")
    expected_readiness_missing = [
        "scripts/zigux/validate-phase15.py",
        "zigux/tests/phase15_build.zig",
        "zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig",
    ]
    if readiness_missing != expected_readiness_missing:
        failures.append("readiness_manifest:still_missing_broader_paths")

    for marker in REQUIRED_REPLAY_MARKERS:
        if marker not in replay:
            failures.append(f"replay:missing:{marker}")

    return failures


def _sample_note() -> str:
    direct_paths = "\n".join(f"- `{rel}`" for rel in DIRECT_PACKET_PATHS)
    broader_paths = "\n".join(f"- `{rel}`" for rel in BROADER_GAP_PATHS)
    replay_commands = "\n".join(f"- `{command}`" for command in MAINTENANCE_REPLAY_COMMANDS)
    return f"""# Phase 15 Governance Lane Sequencing

## Status

- `PHASE15_STATUS=governance_lane_sequencing_packet_landed`
- `PHASE15_LANE_KEY=P15-Y06`
- `PHASE15_SLICE=architecture-council-governance-lane-boundaries`
- `PHASE15_PROVENANCE_MODE=dated_master_readback`
- surveyed against dated current-master readback marker `current-master-readback-2026-05-19`
- current repo reality: the core Phase 15 governance notes are landed, the dedicated review-process manifest is landed, the dedicated governance-lane sequencing manifest plus focused replay are now landed, the dedicated handoff manifest plus focused handoff-note checker are now landed, and the shared reminder surfaces already point at this sequencing note, but the broader validator-first, focused handoff replay, shared-build, and lane-owner companions still remain repo-reality gaps on current `master`

## Lane inventory

- `Documentation/zigux/freeze-map.md` and `Documentation/zigux/phase15-freeze-map-governance.md` own the freeze anchor set
- `Documentation/zigux/phase15-parity-scorecard.md` owns blocked-posture accounting
- `Documentation/zigux/phase15-architecture-council-review-process.md` owns the Architecture Council request fields
- `Documentation/zigux/phase15-indefinite-c-policy.md` owns the stay-in-C policy vocabulary
- `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md` are shared reminder surfaces
- `zigux/tests/phase15_governance_lane_sequencing_manifest.json` and `zigux/tests/phase15_governance_lane_sequencing.zig` keep this sequencing note's direct machine-readable inventory and focused replay explicit
- `zigux/tests/phase15_handoff_next_steps_manifest.json` and `scripts/zigux/check-phase15-handoff-note-alignment.py` keep the dedicated handoff companion packet explicit without changing ownership of the parked governance-lane packet

## Sequencing rules

1. refresh repo reality for the freeze-map anchor set and blocker posture first
2. refresh the parity scorecard only if a blocker posture, owner, approver set, or evidence path changed
3. refresh the Architecture Council review-process packet only if the request-field inventory, stay-in-C closeout rule, or reopen-evidence rule changed
4. refresh the indefinite-C policy packet only if the stay-in-C vocabulary or reopen-trigger catalog changed
5. refresh readiness, handoff, study-only-accounting, shared-summary, and other reminder surfaces only after the owning packet already says the same thing

## Shared-surface boundaries

- no Architecture Council approval is currently recorded for a freeze-map status change
- a deep-core status change has been approved
- a freeze-in-C anchor is ready for a direct Zigux bridge
- a missing focused replay, dedicated build file, or other absent companion is already landed on current `master`

## Current repo-reality gaps

{broader_paths}

## Maintenance-mode handoff

- current lane posture: `maintenance_mode`
- replay only when one of these packet-local conditions becomes true:
{replay_commands}
- reopen only when one of these packet-local conditions becomes true:
  - a previously missing validator-first, focused handoff replay, lane-owner, or build companion lands on current `master`

## Direct packet

{direct_paths}

## Next bounded step

Keep this lane parked until either one of the remaining missing broader Phase 15 companions lands or one of the owner packets changes enough that the shared reminder boundaries need another truthfulness refresh.
"""


def _sample_manifest() -> str:
    return json.dumps(
        {
            "lane_key": "P15-Y06",
            "phase": "Phase 15",
            "surveyed_commit": "current-master-readback-2026-05-19",
            "sequencing_note": str(SEQUENCING_NOTE_PATH),
            "readiness_manifest": str(READINESS_MANIFEST_PATH),
            "shared_summary_gap_note": str(SHARED_GAP_PATH),
            "direct_packet_paths": list(DIRECT_PACKET_PATHS),
            "still_missing_broader_paths": list(BROADER_GAP_PATHS),
            "maintenance_replay_commands": list(MAINTENANCE_REPLAY_COMMANDS),
        },
        indent=2,
    ) + "\n"


def _sample_readiness_manifest() -> str:
    return json.dumps(
        {
            "surveyed_commit_mode": "dated_master_readback",
            "surveyed_commit": "current-master-readback-2026-05-19",
            "readiness_packet_checker": "scripts/zigux/check-phase15-readiness-gate-packet.py",
            "direct_packet_paths": [
                "Documentation/zigux/freeze-map.md",
                "Documentation/zigux/phase15-freeze-map-governance.md",
                "Documentation/zigux/phase15-governance-lane-sequencing.md",
                "Documentation/zigux/phase15-handoff-next-steps-survey.md",
                "Documentation/zigux/phase15-shared-summary-gap.md",
                "Documentation/zigux/review-checklist.md",
                DOCS_CHECKER,
                SCRIPTS_CHECKER,
                TESTS_CHECKER,
                HANDOFF_CHECKER,
                SHARED_GAP_CHECKER,
                HANDOFF_NOTE_CHECKER,
                "scripts/zigux/check-phase15-readiness-gate-packet.py",
                "zigux/tests/README.md",
                "zigux/tests/phase15_architecture_council_review_process_manifest.json",
                "zigux/tests/phase15_governance_lane_sequencing_manifest.json",
                "zigux/tests/phase15_governance_lane_sequencing.zig",
                "zigux/tests/phase15_handoff_next_steps_manifest.json",
                "zigux/tests/phase15_readiness_gate_manifest.json",
            ],
            "still_missing_broader_paths": [
                "scripts/zigux/validate-phase15.py",
                "zigux/tests/phase15_build.zig",
                "zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig",
            ],
        },
        indent=2,
    ) + "\n"


def _sample_replay() -> str:
    return """const std = @import(\"std\");

test \"phase 15 governance-lane sequencing manifest records the new direct replay packet\" {
    try std.testing.expectEqualStrings(\"P15-Y06\", manifest.lane_key);
    try std.testing.expectEqualStrings(\"Phase 15\", manifest.phase);
    try std.testing.expectEqualStrings(\"current-master-readback-2026-05-19\", manifest.surveyed_commit);
    try std.testing.expectEqualStrings(\"Documentation/zigux/phase15-governance-lane-sequencing.md\", manifest.sequencing_note);
    try expectSliceContains(manifest.direct_packet_paths, \"zigux/tests/phase15_governance_lane_sequencing_manifest.json\");
    try expectSliceContains(manifest.direct_packet_paths, \"zigux/tests/phase15_governance_lane_sequencing.zig\");
    try expectSliceContains(manifest.direct_packet_paths, \"zigux/tests/phase15_handoff_next_steps_manifest.json\");
    try expectSliceContains(manifest.direct_packet_paths, \"scripts/zigux/check-phase15-handoff-note-alignment.py\");
    try expectSliceContains(manifest.direct_packet_paths, \"Documentation/zigux/phase15-study-only-anchor-accounting.md\");
    try expectSliceContains(manifest.direct_packet_paths, \"Documentation/zigux/phase15-shared-summary-gap.md\");
    try expectSliceContains(manifest.still_missing_broader_paths, \"scripts/zigux/validate-phase15.py\");
    try expectSliceContains(manifest.maintenance_replay_commands, \"python3 scripts/zigux/check-phase15-handoff-note-alignment.py\");
    try expectSliceContains(manifest.maintenance_replay_commands, \"zig test zigux/tests/phase15_governance_lane_sequencing.zig\");
}
"""


def _seed_repo(root: Path) -> None:
    _write(root / SEQUENCING_NOTE_PATH, _sample_note())
    _write(root / MANIFEST_PATH, _sample_manifest())
    _write(root / READINESS_MANIFEST_PATH, _sample_readiness_manifest())
    _write(root / REPLAY_PATH, _sample_replay())
    for path in (
        DOCS_README_PATH,
        REVIEW_CHECKLIST_PATH,
        FREEZE_GOVERNANCE_PATH,
        PARITY_SCORECARD_PATH,
        REVIEW_PROCESS_PATH,
        INDEFINITE_C_POLICY_PATH,
        READINESS_NOTE_PATH,
        HANDOFF_NOTE_PATH,
        STUDY_ONLY_PATH,
        SHARED_GAP_PATH,
        SCRIPTS_README_PATH,
        TESTS_README_PATH,
        HANDOFF_MANIFEST_PATH,
    ):
        _write(root / path, "present\n")
    _write(root / Path(HANDOFF_NOTE_CHECKER), "present\n")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="phase15_governance_lane_sequencing_") as tmpdir:
        root = Path(tmpdir)
        _seed_repo(root)

        failures = collect_failures(root)
        if failures:
            raise AssertionError(f"baseline fixture should pass: {failures}")

        missing_marker_root = root / "missing_marker"
        _seed_repo(missing_marker_root)
        _write(
            missing_marker_root / SEQUENCING_NOTE_PATH,
            _sample_note().replace(
                f"- `python3 {TESTS_CHECKER}`\n",
                "",
                1,
            ),
        )
        failures = collect_failures(missing_marker_root)
        expected = [f"sequencing_note:missing_command:python3 {TESTS_CHECKER}"]
        if failures != expected:
            raise AssertionError(f"unexpected missing-marker failure: {failures}")

        returned_gap_root = root / "returned_gap"
        _seed_repo(returned_gap_root)
        _write(returned_gap_root / "scripts/zigux/validate-phase15.py", "present\n")
        failures = collect_failures(returned_gap_root)
        expected = ["repo:gap_path_returned:scripts/zigux/validate-phase15.py"]
        if failures != expected:
            raise AssertionError(f"unexpected returned-gap failure: {failures}")

        manifest_root = root / "manifest_drift"
        _seed_repo(manifest_root)
        manifest = json.loads(_read_text(manifest_root / MANIFEST_PATH))
        manifest["maintenance_replay_commands"] = manifest["maintenance_replay_commands"][:-1]
        _write(manifest_root / MANIFEST_PATH, json.dumps(manifest, indent=2) + "\n")
        failures = collect_failures(manifest_root)
        expected = ["manifest:maintenance_replay_commands"]
        if failures != expected:
            raise AssertionError(f"unexpected manifest-drift failure: {failures}")

        readiness_root = root / "readiness_drift"
        _seed_repo(readiness_root)
        readiness_manifest = json.loads(_read_text(readiness_root / READINESS_MANIFEST_PATH))
        readiness_manifest["direct_packet_paths"].remove(str(REPLAY_PATH))
        _write(readiness_root / READINESS_MANIFEST_PATH, json.dumps(readiness_manifest, indent=2) + "\n")
        failures = collect_failures(readiness_root)
        expected = [f"readiness_manifest:missing_direct_path:{REPLAY_PATH}"]
        if failures != expected:
            raise AssertionError(f"unexpected readiness-drift failure: {failures}")

        replay_root = root / "replay_drift"
        _seed_repo(replay_root)
        _write(
            replay_root / REPLAY_PATH,
            _sample_replay().replace(
                'expectSliceContains(manifest.still_missing_broader_paths, "scripts/zigux/validate-phase15.py");\n',
                "",
                1,
            ),
        )
        failures = collect_failures(replay_root)
        expected = [
            'replay:missing:expectSliceContains(manifest.still_missing_broader_paths, "scripts/zigux/validate-phase15.py");'
        ]
        if failures != expected:
            raise AssertionError(f"unexpected replay-drift failure: {failures}")

    print("PHASE15_GOVERNANCE_LANE_SEQUENCING_SELF_TEST=pass")
    print("PHASE15_GOVERNANCE_LANE_SEQUENCING_SELF_TEST_CASES=5")
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
