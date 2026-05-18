#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import tempfile
from pathlib import Path


SELF_PATH = Path(__file__).resolve()
ROOT = SELF_PATH.parent.parent.parent if len(SELF_PATH.parents) >= 3 else SELF_PATH.parent

SNAPSHOT_PATH = Path("zigux/tests/fixtures/phase12_libbpf_snapshot.json")
EXPECTED_LANE_KEY = "P12-Y04"
EXPECTED_PHASE = "Phase 12"
EXPECTED_TRACKED_PATHS = [
    "Documentation/zigux/phase12-libbpf-segment-survey.md",
    "Documentation/zigux/phase12-libbpf-verify-shard-note.md",
    "Documentation/zigux/phase12-libbpf-heavy-consumer-lane-sequencing.md",
    "Documentation/zigux/phase12-release-coordination-matrix.md",
]


def load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def is_hex_sha(value: object) -> bool:
    if not isinstance(value, str) or len(value) != 40:
        return False
    return all(ch in "0123456789abcdef" for ch in value)


def git_blob_sha(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode("utf-8") + data).hexdigest()


def collect_missing(root: Path) -> list[str]:
    snapshot_file = root / SNAPSHOT_PATH
    if not snapshot_file.exists():
        return [f"missing_file:{SNAPSHOT_PATH.as_posix()}"]

    packet = load_json(snapshot_file)
    missing: list[str] = []

    if packet.get("lane_key") != EXPECTED_LANE_KEY:
        missing.append(f"snapshot:lane_key:{EXPECTED_LANE_KEY}")
    if packet.get("phase") != EXPECTED_PHASE:
        missing.append(f"snapshot:phase:{EXPECTED_PHASE}")
    if not is_hex_sha(packet.get("surveyed_commit")):
        missing.append("snapshot:surveyed_commit:sha1")

    tracked_file_count = packet.get("tracked_file_count")
    if tracked_file_count != len(EXPECTED_TRACKED_PATHS):
        missing.append(f"snapshot:tracked_file_count:{len(EXPECTED_TRACKED_PATHS)}")

    for field_name in ("tracked_paths", "supporting_notes"):
        field_value = packet.get(field_name)
        if field_value != EXPECTED_TRACKED_PATHS:
            missing.append(f"snapshot:{field_name}:exact_order")

    files = packet.get("files")
    if not isinstance(files, list):
        missing.append("snapshot:files:list")
        return missing

    if len(files) != len(EXPECTED_TRACKED_PATHS):
        missing.append(f"snapshot:files:length:{len(EXPECTED_TRACKED_PATHS)}")
        return missing

    seen_paths: set[str] = set()
    for index, expected_path in enumerate(EXPECTED_TRACKED_PATHS):
        entry = files[index]
        if not isinstance(entry, dict):
            missing.append(f"snapshot:files:{index}:shape")
            continue
        if entry.get("path") != expected_path:
            missing.append(f"snapshot:files:{index}:path:{expected_path}")
            continue

        blob_sha = entry.get("blob_sha")
        if not is_hex_sha(blob_sha):
            missing.append(f"snapshot:files:{index}:blob_sha")
        if entry.get("path") in seen_paths:
            missing.append(f"snapshot:files:{index}:duplicate_path")
        seen_paths.add(entry.get("path"))

        actual_path = root / expected_path
        if not actual_path.exists():
            missing.append(f"missing_file:{expected_path}")
            continue
        if is_hex_sha(blob_sha) and blob_sha != git_blob_sha(actual_path):
            missing.append(f"snapshot:files:{index}:blob_sha:mismatch")

    for rel_path in EXPECTED_TRACKED_PATHS:
        if not (root / rel_path).exists() and f"missing_file:{rel_path}" not in missing:
            missing.append(f"missing_file:{rel_path}")

    return missing


def build_fixture_tree(root: Path) -> None:
    (root / SNAPSHOT_PATH.parent).mkdir(parents=True, exist_ok=True)
    files = []
    for index, rel_path in enumerate(EXPECTED_TRACKED_PATHS):
        path = root / rel_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"# fixture {index}\n", encoding="utf-8")
        files.append({"path": rel_path, "blob_sha": git_blob_sha(path)})

    snapshot = {
        "lane_key": EXPECTED_LANE_KEY,
        "phase": EXPECTED_PHASE,
        "surveyed_commit": "9695696dae13fac53792eb77b7ff68ae2053ceea",
        "tracked_file_count": len(EXPECTED_TRACKED_PATHS),
        "tracked_paths": EXPECTED_TRACKED_PATHS,
        "supporting_notes": EXPECTED_TRACKED_PATHS,
        "files": files,
    }
    (root / SNAPSHOT_PATH).write_text(json.dumps(snapshot, indent=2) + "\n", encoding="utf-8")


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    updated = text.replace(old, new, 1)
    if updated == text:
        raise SystemExit(f"failed to mutate fixture: {path}:{old}")
    path.write_text(updated, encoding="utf-8")


def expect_case(tmp_root: Path, expected_item: str, case_name: str) -> None:
    missing = collect_missing(tmp_root)
    if expected_item not in missing:
        raise SystemExit(f"phase12-libbpf-snapshot:self-test:{case_name}:{missing}")


def run_self_test() -> None:
    with tempfile.TemporaryDirectory(prefix="zigux_phase12_libbpf_snapshot_") as tmp_dir_str:
        tmp_root = Path(tmp_dir_str)
        build_fixture_tree(tmp_root)

        if collect_missing(tmp_root) != []:
            raise SystemExit("phase12-libbpf-snapshot:self-test:clean_fixture")

        replace_once(tmp_root / SNAPSHOT_PATH, EXPECTED_LANE_KEY, "P12-X99")
        expect_case(tmp_root, f"snapshot:lane_key:{EXPECTED_LANE_KEY}", "lane_key")
        build_fixture_tree(tmp_root)

        replace_once(tmp_root / SNAPSHOT_PATH, EXPECTED_PHASE, "Phase 99")
        expect_case(tmp_root, f"snapshot:phase:{EXPECTED_PHASE}", "phase")
        build_fixture_tree(tmp_root)

        replace_once(
            tmp_root / SNAPSHOT_PATH,
            "9695696dae13fac53792eb77b7ff68ae2053ceea",
            "not-a-sha",
        )
        expect_case(tmp_root, "snapshot:surveyed_commit:sha1", "surveyed_commit")
        build_fixture_tree(tmp_root)

        replace_once(
            tmp_root / SNAPSHOT_PATH,
            f"\"tracked_file_count\": {len(EXPECTED_TRACKED_PATHS)}",
            "\"tracked_file_count\": 3",
        )
        expect_case(
            tmp_root,
            f"snapshot:tracked_file_count:{len(EXPECTED_TRACKED_PATHS)}",
            "tracked_file_count",
        )
        build_fixture_tree(tmp_root)

        replace_once(
            tmp_root / SNAPSHOT_PATH,
            EXPECTED_TRACKED_PATHS[2],
            "Documentation/zigux/phase12-libbpf-heavy-consumer-missing.md",
        )
        expect_case(tmp_root, "snapshot:tracked_paths:exact_order", "tracked_paths")
        build_fixture_tree(tmp_root)

        snapshot = load_json(tmp_root / SNAPSHOT_PATH)
        supporting_notes = snapshot["supporting_notes"]
        if not isinstance(supporting_notes, list):
            raise SystemExit("phase12-libbpf-snapshot:self-test:fixture_supporting_notes_shape")
        supporting_notes[2] = "Documentation/zigux/phase12-libbpf-heavy-consumer-missing.md"
        (tmp_root / SNAPSHOT_PATH).write_text(json.dumps(snapshot, indent=2) + "\n", encoding="utf-8")
        expect_case(tmp_root, "snapshot:supporting_notes:exact_order", "supporting_notes")
        build_fixture_tree(tmp_root)

        first_blob_sha = git_blob_sha(tmp_root / EXPECTED_TRACKED_PATHS[0])
        replace_once(tmp_root / SNAPSHOT_PATH, first_blob_sha, f"{'0' * 40}")
        expect_case(tmp_root, "snapshot:files:0:blob_sha:mismatch", "blob_sha_mismatch")
        build_fixture_tree(tmp_root)

        first_blob_sha = git_blob_sha(tmp_root / EXPECTED_TRACKED_PATHS[0])
        replace_once(tmp_root / SNAPSHOT_PATH, first_blob_sha, "short-sha")
        expect_case(tmp_root, "snapshot:files:0:blob_sha", "blob_sha")
        build_fixture_tree(tmp_root)

        (tmp_root / EXPECTED_TRACKED_PATHS[-1]).unlink()
        expect_case(
            tmp_root,
            f"missing_file:{EXPECTED_TRACKED_PATHS[-1]}",
            "supporting_file_presence",
        )

    print("PHASE12_LIBBPF_SNAPSHOT_SELF_TEST=pass")
    print("PHASE12_LIBBPF_SNAPSHOT_SELF_TEST_CASE_COUNT=9")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Fail closed when the live Phase 12 libbpf snapshot anchor drifts."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect.")
    parser.add_argument("--self-test", action="store_true", help="Run built-in checker self-tests.")
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return 0

    missing = collect_missing(args.root)
    if missing:
        print("PHASE12_LIBBPF_SNAPSHOT=fail")
        print("PHASE12_LIBBPF_SNAPSHOT_MISSING_START")
        for item in missing:
            print(item)
        print("PHASE12_LIBBPF_SNAPSHOT_MISSING_END")
        return 1

    print("PHASE12_LIBBPF_SNAPSHOT=pass")
    print(f"PHASE12_LIBBPF_SNAPSHOT_TRACKED_FILE_COUNT={len(EXPECTED_TRACKED_PATHS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
