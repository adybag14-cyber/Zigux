#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
import tempfile
from pathlib import Path

SNAPSHOT_PATH = Path("zigux/tests/fixtures/phase12_libbpf_snapshot.json")
NOTE_PATHS = [
    "Documentation/zigux/phase12-libbpf-segment-survey.md",
    "Documentation/zigux/phase12-libbpf-verify-shard-note.md",
    "Documentation/zigux/phase12-libbpf-heavy-consumer-lane-sequencing.md",
    "Documentation/zigux/phase12-release-coordination-matrix.md",
]
EXPECTED_ABSENT_BOUNDARIES = [
    "zigux/tests/phase12_libbpf_manifest.json",
    "zigux/tests/phase12_libbpf_segments.zig",
    "zigux/tests/phase12_libbpf_reviewability.zig",
    "tools/lib/bpf/zigux_segments/manifest.json",
    "tools/lib/bpf/zigux_segments/verify.zig",
]
EXPECTED_LANE_KEY = "P12-L16"
EXPECTED_PHASE = "Phase 12"
EXPECTED_SCOPE = "parked Phase 12 libbpf note packet on current master"
SELF_PATH = Path(__file__).resolve()


def infer_repo_root() -> Path:
    for candidate in [SELF_PATH.parent, *SELF_PATH.parents]:
        if (candidate / SNAPSHOT_PATH).exists() and (candidate / NOTE_PATHS[0]).exists():
            return candidate
    return SELF_PATH.parent


ROOT = infer_repo_root()


def git_blob_sha(data: bytes) -> str:
    header = f"blob {len(data)}\0".encode("utf-8")
    return hashlib.sha1(header + data).hexdigest()


def render_snapshot(root: Path, surveyed_commit: str) -> dict[str, object]:
    return {
        "lane_key": EXPECTED_LANE_KEY,
        "phase": EXPECTED_PHASE,
        "surveyed_commit": surveyed_commit,
        "snapshot_scope": EXPECTED_SCOPE,
        "tracked_file_count": len(NOTE_PATHS),
        "supporting_notes": NOTE_PATHS,
        "parked_absent_boundaries": EXPECTED_ABSENT_BOUNDARIES,
        "files": [
            {
                "path": rel_path,
                "blob_sha": git_blob_sha((root / rel_path).read_bytes()),
            }
            for rel_path in NOTE_PATHS
        ],
    }


def validate(root: Path) -> list[str]:
    failures: list[str] = []
    snapshot_path = root / SNAPSHOT_PATH
    if not snapshot_path.exists():
        return [f"missing_file:{SNAPSHOT_PATH}"]

    try:
        snapshot = json.loads(snapshot_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [f"invalid_json:{SNAPSHOT_PATH}:{exc.msg}"]

    if snapshot.get("lane_key") != EXPECTED_LANE_KEY:
        failures.append(
            f"lane_key:expected={EXPECTED_LANE_KEY}:actual={snapshot.get('lane_key')!r}"
        )
    if snapshot.get("phase") != EXPECTED_PHASE:
        failures.append(
            f"phase:expected={EXPECTED_PHASE}:actual={snapshot.get('phase')!r}"
        )

    surveyed_commit = snapshot.get("surveyed_commit")
    if not isinstance(surveyed_commit, str) or len(surveyed_commit) != 40 or any(
        char not in "0123456789abcdef" for char in surveyed_commit
    ):
        failures.append(
            f"surveyed_commit:expected_40_char_hex:actual={surveyed_commit!r}"
        )
        surveyed_commit = "0" * 40

    if snapshot.get("snapshot_scope") != EXPECTED_SCOPE:
        failures.append(
            "snapshot_scope:expected="
            f"{EXPECTED_SCOPE!r}:actual={snapshot.get('snapshot_scope')!r}"
        )

    if snapshot.get("supporting_notes") != NOTE_PATHS:
        failures.append("supporting_notes")
    if snapshot.get("parked_absent_boundaries") != EXPECTED_ABSENT_BOUNDARIES:
        failures.append("parked_absent_boundaries")

    expected_tracked_file_count = len(NOTE_PATHS)
    actual_tracked_file_count = snapshot.get("tracked_file_count")
    if actual_tracked_file_count != expected_tracked_file_count:
        failures.append(
            "tracked_file_count:expected="
            f"{expected_tracked_file_count}:actual={actual_tracked_file_count!r}"
        )

    missing_notes = [rel_path for rel_path in NOTE_PATHS if not (root / rel_path).exists()]
    failures.extend(f"missing_note:{rel_path}" for rel_path in missing_notes)
    if missing_notes:
        return failures

    rendered = render_snapshot(root, surveyed_commit)
    files = snapshot.get("files")
    if not isinstance(files, list):
        failures.append(f"files:expected_list:actual={type(files).__name__}")
        files = []

    if len(files) != expected_tracked_file_count:
        failures.append(
            f"files_count:expected={expected_tracked_file_count}:actual={len(files)}"
        )

    if [entry.get("path") for entry in files if isinstance(entry, dict)] != NOTE_PATHS:
        failures.append("files_path_order")

    actual_files = {entry["path"]: entry["blob_sha"] for entry in rendered["files"]}
    actual_entries = {
        entry.get("path"): entry for entry in files if isinstance(entry, dict)
    }
    for rel_path in NOTE_PATHS:
        actual_entry = actual_entries.get(rel_path)
        if actual_entry is None:
            failures.append(f"missing_file_entry:{rel_path}")
            continue
        expected_blob_sha = actual_files[rel_path]
        actual_blob_sha = actual_entry.get("blob_sha")
        if actual_blob_sha != expected_blob_sha:
            failures.append(
                f"stale_blob:{rel_path}:expected={expected_blob_sha}:actual={actual_blob_sha!r}"
            )

    return failures


def write_fixture_tree(root: Path) -> None:
    note_texts = {
        NOTE_PATHS[0]: "# Phase 12 Libbpf Segment Survey\ncurrent survey note\n",
        NOTE_PATHS[1]: "# Phase 12 Libbpf Verify Shard Note\nparked verify note\n",
        NOTE_PATHS[2]: "# Phase 12 Libbpf Heavy-Consumer Lane Sequencing\nshared sequencing note\n",
        NOTE_PATHS[3]: "# Phase 12 Release Coordination Matrix\nshared matrix note\n",
    }
    for rel_path, text in note_texts.items():
        path = root / rel_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    snapshot_path = root / SNAPSHOT_PATH
    snapshot_path.parent.mkdir(parents=True, exist_ok=True)
    snapshot = render_snapshot(root, "db2badeb31e4d5411ee165dcc35f7297a200981a")
    snapshot_path.write_text(json.dumps(snapshot, indent=2) + "\n", encoding="utf-8")


def expect_failure(root: Path, expected: str) -> None:
    failures = validate(root)
    if failures != [expected]:
        raise SystemExit(
            f"expected failure not found: {expected}\nactual_failures={failures!r}"
        )


def run_self_test() -> int:
    base = Path(tempfile.mkdtemp(prefix="phase12-libbpf-note-snapshot-"))
    try:
        write_fixture_tree(base)
        failures = validate(base)
        if failures:
            raise SystemExit(f"fixture tree should pass but failed: {failures!r}")

        snapshot_path = base / SNAPSHOT_PATH

        snapshot = json.loads(snapshot_path.read_text(encoding="utf-8"))
        snapshot["files"][0]["blob_sha"] = "0" * 40
        snapshot_path.write_text(json.dumps(snapshot, indent=2) + "\n", encoding="utf-8")
        expect_failure(
            base,
            "stale_blob:Documentation/zigux/phase12-libbpf-segment-survey.md:expected="
            f"{git_blob_sha((base / NOTE_PATHS[0]).read_bytes())}:actual={'0' * 40}",
        )

        write_fixture_tree(base)
        (base / NOTE_PATHS[1]).unlink()
        expect_failure(base, f"missing_note:{NOTE_PATHS[1]}")

        write_fixture_tree(base)
        snapshot = json.loads(snapshot_path.read_text(encoding="utf-8"))
        snapshot["tracked_file_count"] = len(NOTE_PATHS) + 1
        snapshot_path.write_text(json.dumps(snapshot, indent=2) + "\n", encoding="utf-8")
        expect_failure(base, f"tracked_file_count:expected={len(NOTE_PATHS)}:actual={len(NOTE_PATHS) + 1}")

        write_fixture_tree(base)
        snapshot = json.loads(snapshot_path.read_text(encoding="utf-8"))
        snapshot["surveyed_commit"] = "deadbeef"
        snapshot_path.write_text(json.dumps(snapshot, indent=2) + "\n", encoding="utf-8")
        expect_failure(base, "surveyed_commit:expected_40_char_hex:actual='deadbeef'")

        write_fixture_tree(base)
        snapshot = json.loads(snapshot_path.read_text(encoding="utf-8"))
        snapshot["parked_absent_boundaries"][0] = "zigux/tests/unexpected.json"
        snapshot_path.write_text(json.dumps(snapshot, indent=2) + "\n", encoding="utf-8")
        expect_failure(base, "parked_absent_boundaries")

        write_fixture_tree(base)
        snapshot = json.loads(snapshot_path.read_text(encoding="utf-8"))
        snapshot["files"] = list(reversed(snapshot["files"]))
        snapshot_path.write_text(json.dumps(snapshot, indent=2) + "\n", encoding="utf-8")
        expect_failure(base, "files_path_order")

        print("PHASE12_LIBBPF_NOTE_SNAPSHOT_SELF_TEST=pass")
        print("PHASE12_LIBBPF_NOTE_SNAPSHOT_SELF_TEST_CASE_COUNT=6")
        return 0
    finally:
        shutil.rmtree(base, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Validate the parked Phase 12 libbpf note snapshot fixture against the "
            "current note packet blob IDs."
        )
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=ROOT,
        help="Repository root to validate. Defaults to the inferred repository root.",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run the fixture-backed self-test.",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = validate(args.root)
    if failures:
        print("PHASE12_LIBBPF_NOTE_SNAPSHOT=fail")
        print("PHASE12_LIBBPF_NOTE_SNAPSHOT_FAILURES_START")
        for failure in failures:
            print(failure)
        print("PHASE12_LIBBPF_NOTE_SNAPSHOT_FAILURES_END")
        return 1

    print("PHASE12_LIBBPF_NOTE_SNAPSHOT=pass")
    print(f"PHASE12_LIBBPF_NOTE_SNAPSHOT_TRACKED_FILE_COUNT={len(NOTE_PATHS)}")
    print(
        "PHASE12_LIBBPF_NOTE_SNAPSHOT_ABSENT_BOUNDARY_COUNT="
        f"{len(EXPECTED_ABSENT_BOUNDARIES)}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
