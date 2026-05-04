#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys
import tempfile


ROOT = Path(__file__).resolve().parent
MANIFEST_REL_PATH = "zigux/tests/phase12_libbpf_manifest.json"
SNAPSHOT_REL_PATH = "zigux/tests/fixtures/phase12_libbpf_snapshot.json"
SURVEY_NOTE_REL_PATH = "Documentation/zigux/phase12-libbpf-segment-survey.md"
REQUIRED_PATHS = [MANIFEST_REL_PATH, SNAPSHOT_REL_PATH, SURVEY_NOTE_REL_PATH]
HEX40 = re.compile(r"^[0-9a-f]{40}$")


def missing_required_paths(root: Path) -> list[str]:
    missing: list[str] = []
    for rel_path in REQUIRED_PATHS:
        if not (root / rel_path).exists():
            missing.append(f"missing_file:{rel_path}")
    return missing


def validate_manifest_packet(manifest: dict[str, object]) -> dict[str, str]:
    lane_key = manifest.get("lane_key")
    phase = manifest.get("phase")
    surveyed_commit = manifest.get("surveyed_commit")
    if not isinstance(lane_key, str) or not lane_key:
        raise SystemExit("invalid Phase 12 libbpf lane_key")
    if not isinstance(phase, str) or phase != "Phase 12":
        raise SystemExit("invalid Phase 12 libbpf phase")
    if not isinstance(surveyed_commit, str) or not HEX40.fullmatch(surveyed_commit):
        raise SystemExit("invalid Phase 12 libbpf surveyed_commit")
    return {
        "lane_key": lane_key,
        "phase": phase,
        "surveyed_commit": surveyed_commit,
    }


def validate_snapshot_packet(snapshot: dict[str, object]) -> dict[str, str]:
    lane_key = snapshot.get("lane_key")
    phase = snapshot.get("phase")
    surveyed_commit = snapshot.get("surveyed_commit")
    if not isinstance(lane_key, str) or not lane_key:
        raise SystemExit("invalid Phase 12 libbpf snapshot lane_key")
    if not isinstance(phase, str) or phase != "Phase 12":
        raise SystemExit("invalid Phase 12 libbpf snapshot phase")
    if not isinstance(surveyed_commit, str) or not HEX40.fullmatch(surveyed_commit):
        raise SystemExit("invalid Phase 12 libbpf snapshot surveyed_commit")
    return {
        "lane_key": lane_key,
        "phase": phase,
        "surveyed_commit": surveyed_commit,
    }


def expected_surveyed_commit_note_text(surveyed_commit: str) -> str:
    return f"packet-local head `{surveyed_commit}`"


def load_alignment_packet(root: Path = ROOT) -> dict[str, str]:
    manifest_packet = validate_manifest_packet(
        json.loads((root / MANIFEST_REL_PATH).read_text(encoding="utf-8"))
    )
    snapshot_packet = validate_snapshot_packet(
        json.loads((root / SNAPSHOT_REL_PATH).read_text(encoding="utf-8"))
    )
    if manifest_packet["lane_key"] != snapshot_packet["lane_key"]:
        raise SystemExit("invalid Phase 12 libbpf snapshot lane_key alignment")
    if manifest_packet["phase"] != snapshot_packet["phase"]:
        raise SystemExit("invalid Phase 12 libbpf snapshot phase alignment")
    if manifest_packet["surveyed_commit"] != snapshot_packet["surveyed_commit"]:
        raise SystemExit("invalid Phase 12 libbpf snapshot surveyed_commit alignment")

    survey_note = (root / SURVEY_NOTE_REL_PATH).read_text(encoding="utf-8")
    expected_commit_text = expected_surveyed_commit_note_text(
        manifest_packet["surveyed_commit"]
    )
    if survey_note.count(expected_commit_text) != 1:
        raise SystemExit("invalid Phase 12 libbpf survey note surveyed commit")

    return manifest_packet


def run_check(root: Path = ROOT) -> tuple[int, list[str]]:
    missing = missing_required_paths(root)
    if missing:
        return 1, [
            "PHASE12_LIBBPF_SURVEYED_COMMIT=fail",
            "PHASE12_LIBBPF_SURVEYED_COMMIT_MISSING_START",
            *missing,
            "PHASE12_LIBBPF_SURVEYED_COMMIT_MISSING_END",
        ]

    packet = load_alignment_packet(root)
    return 0, [
        "PHASE12_LIBBPF_SURVEYED_COMMIT=pass",
        f"PHASE12_LIBBPF_LANE_KEY={packet['lane_key']}",
        f"PHASE12_LIBBPF_PHASE={packet['phase']}",
        f"PHASE12_LIBBPF_SURVEYED_HEAD={packet['surveyed_commit']}",
    ]


def expect_system_exit(label: str, callback, expected_message: str) -> None:
    try:
        callback()
    except SystemExit as exc:
        actual_message = str(exc)
        if actual_message != expected_message:
            raise SystemExit(
                f"phase12-libbpf-surveyed-commit:self-test:{label}:"
                f"expected={expected_message!r}:actual={actual_message!r}"
            ) from exc
        return
    raise SystemExit(
        "phase12-libbpf-surveyed-commit:self-test:"
        f"{label}:missing_system_exit:{expected_message!r}"
    )


def copy_required_tree(root: Path) -> None:
    for rel_path in REQUIRED_PATHS:
        target_path = root / rel_path
        target_path.parent.mkdir(parents=True, exist_ok=True)
        target_path.write_bytes((ROOT / rel_path).read_bytes())


def run_self_test() -> int:
    manifest_packet = validate_manifest_packet(
        json.loads((ROOT / MANIFEST_REL_PATH).read_text(encoding="utf-8"))
    )
    snapshot_packet = validate_snapshot_packet(
        json.loads((ROOT / SNAPSHOT_REL_PATH).read_text(encoding="utf-8"))
    )
    if manifest_packet["lane_key"] != snapshot_packet["lane_key"]:
        raise SystemExit(
            "phase12-libbpf-surveyed-commit:self-test:live_lane_key_alignment"
        )
    if manifest_packet["phase"] != snapshot_packet["phase"]:
        raise SystemExit(
            "phase12-libbpf-surveyed-commit:self-test:live_phase_alignment"
        )
    if manifest_packet["surveyed_commit"] != snapshot_packet["surveyed_commit"]:
        raise SystemExit(
            "phase12-libbpf-surveyed-commit:self-test:live_surveyed_commit_alignment"
        )
    load_alignment_packet(ROOT)

    invalid_manifest = dict(manifest_packet)
    invalid_manifest["surveyed_commit"] = "deadbeef"
    expect_system_exit(
        "invalid_manifest_surveyed_commit",
        lambda: validate_manifest_packet(invalid_manifest),
        "invalid Phase 12 libbpf surveyed_commit",
    )

    invalid_snapshot = dict(snapshot_packet)
    invalid_snapshot["surveyed_commit"] = "deadbeef"
    expect_system_exit(
        "invalid_snapshot_surveyed_commit",
        lambda: validate_snapshot_packet(invalid_snapshot),
        "invalid Phase 12 libbpf snapshot surveyed_commit",
    )

    with tempfile.TemporaryDirectory(
        prefix="zigux_phase12_libbpf_surveyed_commit_missing_"
    ) as tmp_dir_str:
        missing_root = Path(tmp_dir_str)
        copy_required_tree(missing_root)
        (missing_root / SURVEY_NOTE_REL_PATH).unlink()
        missing_exit_code, missing_lines = run_check(missing_root)
        if missing_exit_code != 1:
            raise SystemExit(
                "phase12-libbpf-surveyed-commit:self-test:missing_exit_code"
            )
        expected_missing_lines = [
            "PHASE12_LIBBPF_SURVEYED_COMMIT=fail",
            "PHASE12_LIBBPF_SURVEYED_COMMIT_MISSING_START",
            f"missing_file:{SURVEY_NOTE_REL_PATH}",
            "PHASE12_LIBBPF_SURVEYED_COMMIT_MISSING_END",
        ]
        if missing_lines != expected_missing_lines:
            raise SystemExit(
                "phase12-libbpf-surveyed-commit:self-test:missing_lines"
            )

    with tempfile.TemporaryDirectory(
        prefix="zigux_phase12_libbpf_surveyed_commit_note_"
    ) as tmp_dir_str:
        note_root = Path(tmp_dir_str)
        copy_required_tree(note_root)
        note_path = note_root / SURVEY_NOTE_REL_PATH
        note_path.write_text(
            note_path.read_text(encoding="utf-8").replace(
                expected_surveyed_commit_note_text(manifest_packet["surveyed_commit"]),
                expected_surveyed_commit_note_text("0" * 40),
            ),
            encoding="utf-8",
        )
        expect_system_exit(
            "invalid_survey_note_surveyed_commit",
            lambda: load_alignment_packet(note_root),
            "invalid Phase 12 libbpf survey note surveyed commit",
        )

    with tempfile.TemporaryDirectory(
        prefix="zigux_phase12_libbpf_surveyed_commit_note_duplicate_"
    ) as tmp_dir_str:
        note_root = Path(tmp_dir_str)
        copy_required_tree(note_root)
        note_path = note_root / SURVEY_NOTE_REL_PATH
        expected_commit_text = expected_surveyed_commit_note_text(
            manifest_packet["surveyed_commit"]
        )
        note_path.write_text(
            note_path.read_text(encoding="utf-8").replace(
                expected_commit_text,
                expected_commit_text + " and " + expected_commit_text,
                1,
            ),
            encoding="utf-8",
        )
        expect_system_exit(
            "duplicate_survey_note_surveyed_commit",
            lambda: load_alignment_packet(note_root),
            "invalid Phase 12 libbpf survey note surveyed commit",
        )

    with tempfile.TemporaryDirectory(
        prefix="zigux_phase12_libbpf_surveyed_commit_snapshot_"
    ) as tmp_dir_str:
        snapshot_root = Path(tmp_dir_str)
        copy_required_tree(snapshot_root)
        snapshot = json.loads(
            (snapshot_root / SNAPSHOT_REL_PATH).read_text(encoding="utf-8")
        )
        snapshot["surveyed_commit"] = "0" * 40
        (snapshot_root / SNAPSHOT_REL_PATH).write_text(
            json.dumps(snapshot, indent=2) + "\n",
            encoding="utf-8",
        )
        expect_system_exit(
            "snapshot_surveyed_commit_alignment",
            lambda: load_alignment_packet(snapshot_root),
            "invalid Phase 12 libbpf snapshot surveyed_commit alignment",
        )

    with tempfile.TemporaryDirectory(
        prefix="zigux_phase12_libbpf_surveyed_commit_lane_"
    ) as tmp_dir_str:
        lane_root = Path(tmp_dir_str)
        copy_required_tree(lane_root)
        snapshot = json.loads((lane_root / SNAPSHOT_REL_PATH).read_text(encoding="utf-8"))
        snapshot["lane_key"] = "P12-L99"
        (lane_root / SNAPSHOT_REL_PATH).write_text(
            json.dumps(snapshot, indent=2) + "\n",
            encoding="utf-8",
        )
        expect_system_exit(
            "snapshot_lane_key_alignment",
            lambda: load_alignment_packet(lane_root),
            "invalid Phase 12 libbpf snapshot lane_key alignment",
        )

    print("PHASE12_LIBBPF_SURVEYED_COMMIT_SELF_TEST=pass")
    print("PHASE12_LIBBPF_SURVEYED_COMMIT_SELF_TEST_CASE_COUNT=7")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Verify that the bounded Phase 12 libbpf snapshot packet and survey note "
            "still agree on the recorded surveyed commit."
        )
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run built-in manifest, snapshot, and survey-note alignment checks",
    )
    args = parser.parse_args(argv)

    if args.self_test:
        return run_self_test()

    exit_code, lines = run_check()
    for line in lines:
        print(line)
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
