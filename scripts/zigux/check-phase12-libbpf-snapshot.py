#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[2]
FIXTURE_PATH = ROOT / "zigux/tests/fixtures/phase12_libbpf_snapshot.json"
ARTIFACT_DIFF_PATH = ROOT / "scripts/zigux/artifact_diff.py"
TRACKED_PATHS = [
    "zigux/tests/phase12_libbpf_manifest.json",
    "zigux/tests/phase12_libbpf_segments.zig",
    "zigux/tests/phase12_libbpf_reviewability.zig",
    "Documentation/zigux/phase12-libbpf-segment-survey.md",
    "tools/lib/bpf/zigux_segments/manifest.json",
]
HEX40 = re.compile(r"^[0-9a-f]{40}$")


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


def file_digest(path: Path) -> dict[str, object]:
    data = path.read_bytes()
    return {
        "path": str(path.relative_to(ROOT)),
        "bytes": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
    }


def load_manifest_packet() -> dict[str, str]:
    manifest = json.loads((ROOT / TRACKED_PATHS[0]).read_text(encoding="utf-8"))
    return validate_manifest_packet(manifest)


def render_snapshot() -> dict[str, object]:
    manifest_packet = load_manifest_packet()
    files = [file_digest(ROOT / rel_path) for rel_path in TRACKED_PATHS]
    return {
        "lane_key": manifest_packet["lane_key"],
        "phase": manifest_packet["phase"],
        "surveyed_commit": manifest_packet["surveyed_commit"],
        "tracked_file_count": len(files),
        "files": files,
    }


def compare_snapshot(snapshot: dict[str, object]) -> tuple[subprocess.CompletedProcess[str], str]:
    rendered = json.dumps(snapshot, indent=2) + "\n"
    with tempfile.TemporaryDirectory(prefix="zigux_phase12_libbpf_snapshot_") as tmp_dir_str:
        actual_path = Path(tmp_dir_str) / "phase12_libbpf_snapshot.json"
        actual_path.write_text(rendered, encoding="utf-8")
        result = subprocess.run(
            [
                sys.executable,
                str(ARTIFACT_DIFF_PATH),
                "--mode",
                "json",
                str(FIXTURE_PATH),
                str(actual_path),
            ],
            check=False,
            text=True,
            capture_output=True,
        )
    return result, rendered


def expect_system_exit(label: str, callback, expected_message: str) -> None:
    try:
        callback()
    except SystemExit as exc:
        actual_message = str(exc)
        if actual_message != expected_message:
            raise SystemExit(
                f"phase12-libbpf-snapshot:self-test:{label}:expected={expected_message!r}:actual={actual_message!r}"
            ) from exc
        return
    raise SystemExit(
        f"phase12-libbpf-snapshot:self-test:{label}:missing_system_exit:{expected_message!r}"
    )


def expect_snapshot_mismatch(label: str, snapshot: dict[str, object]) -> None:
    mismatched_result, _ = compare_snapshot(snapshot)
    if mismatched_result.returncode == 0:
        raise SystemExit(f"phase12-libbpf-snapshot:self-test:{label}:fixture_drift_exit")
    if "ARTIFACT_DIFF=fail" not in mismatched_result.stdout:
        raise SystemExit(f"phase12-libbpf-snapshot:self-test:{label}:fixture_drift_stdout")


def run_self_test() -> int:
    live_manifest = json.loads((ROOT / TRACKED_PATHS[0]).read_text(encoding="utf-8"))
    manifest_packet = validate_manifest_packet(live_manifest)
    if manifest_packet["lane_key"] != "P12-L16":
        raise SystemExit("phase12-libbpf-snapshot:self-test:lane_key_round_trip")
    if manifest_packet["phase"] != "Phase 12":
        raise SystemExit("phase12-libbpf-snapshot:self-test:phase_round_trip")
    if manifest_packet["surveyed_commit"] != live_manifest["surveyed_commit"]:
        raise SystemExit("phase12-libbpf-snapshot:self-test:surveyed_commit_round_trip")

    invalid_lane_manifest = dict(live_manifest)
    invalid_lane_manifest["lane_key"] = ""
    expect_system_exit(
        "invalid_lane_key",
        lambda: validate_manifest_packet(invalid_lane_manifest),
        "invalid Phase 12 libbpf lane_key",
    )

    invalid_phase_manifest = dict(live_manifest)
    invalid_phase_manifest["phase"] = "Phase 11"
    expect_system_exit(
        "invalid_phase",
        lambda: validate_manifest_packet(invalid_phase_manifest),
        "invalid Phase 12 libbpf phase",
    )

    invalid_commit_manifest = dict(live_manifest)
    invalid_commit_manifest["surveyed_commit"] = "deadbeef"
    expect_system_exit(
        "invalid_surveyed_commit",
        lambda: validate_manifest_packet(invalid_commit_manifest),
        "invalid Phase 12 libbpf surveyed_commit",
    )

    invalid_nonhex_commit_manifest = dict(live_manifest)
    invalid_nonhex_commit_manifest["surveyed_commit"] = "g" * 40
    expect_system_exit(
        "invalid_nonhex_surveyed_commit",
        lambda: validate_manifest_packet(invalid_nonhex_commit_manifest),
        "invalid Phase 12 libbpf surveyed_commit",
    )

    invalid_uppercase_commit_manifest = dict(live_manifest)
    invalid_uppercase_commit_manifest["surveyed_commit"] = live_manifest["surveyed_commit"].upper()
    expect_system_exit(
        "invalid_uppercase_surveyed_commit",
        lambda: validate_manifest_packet(invalid_uppercase_commit_manifest),
        "invalid Phase 12 libbpf surveyed_commit",
    )

    first = render_snapshot()
    second = render_snapshot()
    if first != second:
        raise SystemExit("phase12-libbpf-snapshot:self-test:repeat_run_stability")
    if first["tracked_file_count"] != len(TRACKED_PATHS):
        raise SystemExit("phase12-libbpf-snapshot:self-test:tracked_file_count")

    files = first["files"]
    if not isinstance(files, list):
        raise SystemExit("phase12-libbpf-snapshot:self-test:files_list")
    actual_paths = [entry.get("path") for entry in files]
    if actual_paths != TRACKED_PATHS:
        raise SystemExit("phase12-libbpf-snapshot:self-test:tracked_path_order")

    for entry, expected_path in zip(files, TRACKED_PATHS):
        if entry.get("path") != expected_path:
            raise SystemExit("phase12-libbpf-snapshot:self-test:tracked_entry_path")
        expected_bytes = (ROOT / expected_path).read_bytes()
        if entry.get("bytes") != len(expected_bytes):
            raise SystemExit("phase12-libbpf-snapshot:self-test:tracked_entry_bytes")
        if entry.get("sha256") != hashlib.sha256(expected_bytes).hexdigest():
            raise SystemExit("phase12-libbpf-snapshot:self-test:tracked_entry_sha256")

    matched_result, _ = compare_snapshot(first)
    if matched_result.returncode != 0:
        raise SystemExit("phase12-libbpf-snapshot:self-test:fixture_match")
    if "ARTIFACT_DIFF=pass" not in matched_result.stdout:
        raise SystemExit("phase12-libbpf-snapshot:self-test:fixture_match_stdout")

    drifted = dict(first)
    drifted["lane_key"] = "P12-L99"
    expect_snapshot_mismatch("fixture_lane_key_drift", drifted)

    drifted_phase = dict(first)
    drifted_phase["phase"] = "Phase 11"
    expect_snapshot_mismatch("fixture_phase_drift", drifted_phase)

    drifted_commit = dict(first)
    drifted_commit["surveyed_commit"] = "0" * 40
    expect_snapshot_mismatch("fixture_surveyed_commit_drift", drifted_commit)

    drifted_track_count = dict(first)
    drifted_track_count["tracked_file_count"] = int(first["tracked_file_count"]) + 1
    expect_snapshot_mismatch("fixture_tracked_file_count_drift", drifted_track_count)

    drifted_path = json.loads(json.dumps(first))
    drifted_path["files"][0]["path"] = "zigux/tests/phase12_libbpf_manifest_drift.json"
    expect_snapshot_mismatch("fixture_tracked_path_drift", drifted_path)

    drifted_bytes = json.loads(json.dumps(first))
    drifted_bytes["files"][0]["bytes"] = int(first["files"][0]["bytes"]) + 1
    expect_snapshot_mismatch("fixture_byte_count_drift", drifted_bytes)

    drifted_sha = json.loads(json.dumps(first))
    drifted_sha["files"][0]["sha256"] = "0" * 64
    expect_snapshot_mismatch("fixture_sha256_drift", drifted_sha)

    last_index = len(files) - 1
    drifted_tail_path = json.loads(json.dumps(first))
    drifted_tail_path["files"][last_index]["path"] = "tools/lib/bpf/zigux_segments/manifest_drift.json"
    expect_snapshot_mismatch("fixture_tail_path_drift", drifted_tail_path)

    drifted_tail_bytes = json.loads(json.dumps(first))
    drifted_tail_bytes["files"][last_index]["bytes"] = int(first["files"][last_index]["bytes"]) + 1
    expect_snapshot_mismatch("fixture_tail_byte_count_drift", drifted_tail_bytes)

    drifted_tail_sha = json.loads(json.dumps(first))
    drifted_tail_sha["files"][last_index]["sha256"] = "f" * 64
    expect_snapshot_mismatch("fixture_tail_sha256_drift", drifted_tail_sha)

    drifted_order = json.loads(json.dumps(first))
    drifted_order["files"][0], drifted_order["files"][last_index] = drifted_order["files"][last_index], drifted_order["files"][0]
    expect_snapshot_mismatch("fixture_tracked_order_drift", drifted_order)

    print("PHASE12_LIBBPF_SNAPSHOT_SELF_TEST=pass")
    print("PHASE12_LIBBPF_SNAPSHOT_SELF_TEST_CASE_COUNT=28")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Rebuild and compare the bounded Phase 12 libbpf snapshot fixture."
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run built-in manifest, ordering, and repeat-run checks",
    )
    args = parser.parse_args(argv)

    if args.self_test:
        return run_self_test()

    first = render_snapshot()
    second = render_snapshot()
    if first != second:
        print("PHASE12_LIBBPF_SNAPSHOT=fail")
        print("PHASE12_LIBBPF_REPEAT_RUN=drift")
        return 1

    result, rendered = compare_snapshot(first)

    if result.stdout:
        sys.stdout.write(result.stdout)
    if result.stderr:
        sys.stderr.write(result.stderr)

    if result.returncode != 0:
        print("PHASE12_LIBBPF_SNAPSHOT=fail")
        print("PHASE12_LIBBPF_REPEAT_RUN=stable")
        return result.returncode

    print("PHASE12_LIBBPF_SNAPSHOT=pass")
    print("PHASE12_LIBBPF_REPEAT_RUN=stable")
    print(f"PHASE12_LIBBPF_TRACKED_FILE_COUNT={first['tracked_file_count']}")
    print(
        "PHASE12_LIBBPF_SNAPSHOT_SHA256="
        + hashlib.sha256(rendered.encode("utf-8")).hexdigest()
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
