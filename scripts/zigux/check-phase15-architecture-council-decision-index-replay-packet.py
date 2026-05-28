#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

DECISION_INDEX_PATH = Path("Documentation/zigux/phase15-architecture-council-decision-index.md")
MANIFEST_PATH = Path("zigux/tests/phase15_architecture_council_decision_index_manifest.json")
REPLAY_PATH = Path("zigux/tests/phase15_architecture_council_decision_index.zig")

NOTE_REQUIRED_MARKERS = (
    "the dedicated decision-index manifest/checker/replay trio",
    "decision inventory, zero-decision posture, future record-link rules, and the dedicated decision-index manifest/checker/replay trio explicit",
    "`zigux/tests/phase15_architecture_council_decision_index_manifest.json`",
    "`zigux/tests/phase15_architecture_council_decision_index.zig`",
    "`scripts/zigux/check-phase15-architecture-council-decision-index.py`",
    "the dedicated decision-index manifest/checker/replay trio drifts away from this note",
)

REPLAY_REQUIRED_MARKERS = (
    "approved status-bucket changes recorded on current `master`: none",
    "stay-in-C closeout decision records recorded on current `master`: none",
    "next bounded step",
)

EXPECTED_MANIFEST = {
    "lane_key": "P15-L09",
    "phase": "Phase 15",
    "surveyed_commit": "current-master-readback-2026-05-27",
    "surveyed_commit_mode": "dated_master_readback",
    "decision_index_note": "Documentation/zigux/phase15-architecture-council-decision-index.md",
    "checker": "scripts/zigux/check-phase15-architecture-council-decision-index.py",
    "focused_replay": "zigux/tests/phase15_architecture_council_decision_index.zig",
}


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def collect_failures(root: Path) -> list[str]:
    failures: list[str] = []
    for rel in (DECISION_INDEX_PATH, MANIFEST_PATH, REPLAY_PATH):
        if not (root / rel).exists():
            failures.append(f"missing_file:{rel}")
    if failures:
        return failures

    note = _read(root / DECISION_INDEX_PATH)
    manifest_text = _read(root / MANIFEST_PATH)
    replay = _read(root / REPLAY_PATH)

    for marker in NOTE_REQUIRED_MARKERS:
        if marker not in note:
            failures.append(f"note:missing:{marker}")

    try:
        manifest = json.loads(manifest_text)
    except json.JSONDecodeError as exc:
        failures.append(f"manifest:invalid_json:{exc.msg}")
        return failures

    for key, value in EXPECTED_MANIFEST.items():
        if manifest.get(key) != value:
            failures.append(f"manifest:mismatch:{key}:{manifest.get(key)!r}")

    for marker in REPLAY_REQUIRED_MARKERS:
        if marker not in replay:
            failures.append(f"replay:missing:{marker}")

    return failures


def _seed(root: Path) -> None:
    _write(
        root / DECISION_INDEX_PATH,
        """# Phase 15 Architecture Council Decision Index

This note records the bounded Phase 15 index for Architecture Council decision records that affect freeze-map anchors.

## Status

- `PHASE15_STATUS=architecture_council_decision_index_landed`
- `PHASE15_LANE_KEY=P15-L09`

## Why this slice exists

This index closes that gap without widening Phase 15 into implementation work. It keeps decision inventory, zero-decision posture, future record-link rules, and the dedicated decision-index manifest/checker/replay trio explicit so later reminder surfaces do not have to infer them indirectly from the freeze map, the review-process note, or the parity scorecard.

## Related owner notes

- `zigux/tests/phase15_architecture_council_decision_index_manifest.json`
- `zigux/tests/phase15_architecture_council_decision_index.zig`
- `scripts/zigux/check-phase15-architecture-council-decision-index.py`

## Next bounded step

Keep this note parked unless the first reviewable Architecture Council decision record lands, a freeze-map anchor changes status bucket, or the dedicated decision-index manifest/checker/replay trio drifts away from this note.
""",
    )
    _write(root / MANIFEST_PATH, json.dumps(EXPECTED_MANIFEST, indent=2) + "\n")
    _write(
        root / REPLAY_PATH,
        """const std = @import(\"std\");

test \"phase15 decision index packet marker roster stays non-empty\" {
    const required_markers = [_][]const u8{
        \"approved status-bucket changes recorded on current `master`: none\",
        \"stay-in-C closeout decision records recorded on current `master`: none\",
        \"next bounded step\",
    };
    try std.testing.expect(required_markers.len == 3);
}
""",
    )


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase15_decision_index_replay_") as tmp_dir:
        root = Path(tmp_dir)

        good_root = root / "good"
        _seed(good_root)
        failures = collect_failures(good_root)
        if failures:
            raise AssertionError(f"good sample should pass: {failures}")
        case_count += 1

        bad_note_root = root / "bad_note"
        _seed(bad_note_root)
        _write(
            bad_note_root / DECISION_INDEX_PATH,
            _read(bad_note_root / DECISION_INDEX_PATH).replace(
                "- `zigux/tests/phase15_architecture_council_decision_index.zig`\n",
                "",
                1,
            ),
        )
        failures = collect_failures(bad_note_root)
        expected = ["note:missing:`zigux/tests/phase15_architecture_council_decision_index.zig`"]
        if failures != expected:
            raise AssertionError(f"unexpected note failure: {failures}")
        case_count += 1

        bad_manifest_root = root / "bad_manifest"
        _seed(bad_manifest_root)
        manifest = json.loads(_read(bad_manifest_root / MANIFEST_PATH))
        manifest["focused_replay"] = "zigux/tests/phase15_architecture_council_decision_index_missing.zig"
        _write(bad_manifest_root / MANIFEST_PATH, json.dumps(manifest, indent=2) + "\n")
        failures = collect_failures(bad_manifest_root)
        expected = [
            "manifest:mismatch:focused_replay:'zigux/tests/phase15_architecture_council_decision_index_missing.zig'"
        ]
        if failures != expected:
            raise AssertionError(f"unexpected manifest failure: {failures}")
        case_count += 1

        bad_replay_root = root / "bad_replay"
        _seed(bad_replay_root)
        _write(
            bad_replay_root / REPLAY_PATH,
            _read(bad_replay_root / REPLAY_PATH).replace(
                '        "next bounded step",\n',
                "",
                1,
            ),
        )
        failures = collect_failures(bad_replay_root)
        expected = ["replay:missing:next bounded step"]
        if failures != expected:
            raise AssertionError(f"unexpected replay failure: {failures}")
        case_count += 1

    print("PHASE15_ARCHITECTURE_COUNCIL_DECISION_INDEX_REPLAY_PACKET_SELF_TEST=pass")
    print(f"PHASE15_ARCHITECTURE_COUNCIL_DECISION_INDEX_REPLAY_PACKET_SELF_TEST_CASES={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify the Phase 15 Architecture Council decision-index note, manifest, and replay packet."
    )
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--write-sample-root", type=Path)
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root is not None:
        _seed(args.write_sample_root)
        print(
            "PHASE15_ARCHITECTURE_COUNCIL_DECISION_INDEX_REPLAY_PACKET_SAMPLE_ROOT="
            f"{args.write_sample_root}"
        )
        return 0

    failures = collect_failures(args.root)
    if failures:
        for failure in failures:
            print(f"ERROR: {failure}")
        return 1

    print("PHASE15_ARCHITECTURE_COUNCIL_DECISION_INDEX_REPLAY_PACKET=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
