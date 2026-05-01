#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
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


def validate_manifest_packet(manifest: dict[str, object]) -> dict[str, str]:
    lane_key = manifest.get("lane_key")
    phase = manifest.get("phase")
    surveyed_commit = manifest.get("surveyed_commit")
    if not isinstance(lane_key, str) or not lane_key:
        raise SystemExit("invalid Phase 12 libbpf lane_key")
    if not isinstance(phase, str) or phase != "Phase 12":
        raise SystemExit("invalid Phase 12 libbpf phase")
    if not isinstance(surveyed_commit, str) or len(surveyed_commit) != 40:
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

    first_digest = files[0]
    if first_digest.get("path") != TRACKED_PATHS[0]:
        raise SystemExit("phase12-libbpf-snapshot:self-test:first_digest_path")
    if first_digest.get("bytes") != len((ROOT / TRACKED_PATHS[0]).read_bytes()):
        raise SystemExit("phase12-libbpf-snapshot:self-test:first_digest_bytes")

    matched_result, _ = compare_snapshot(first)
    if matched_result.returncode != 0:
        raise SystemExit("phase12-libbpf-snapshot:self-test:fixture_match")
    if "ARTIFACT_DIFF=pass" not in matched_result.stdout:
        raise SystemExit("phase12-libbpf-snapshot:self-test:fixture_match_stdout")

    drifted = dict(first)
    drifted["lane_key"] = "P12-L99"
    mismatched_result, _ = compare_snapshot(drifted)
    if mismatched_result.returncode == 0:
        raise SystemExit("phase12-libbpf-snapshot:self-test:fixture_drift_exit")
    if "ARTIFACT_DIFF=fail" not in mismatched_result.stdout:
        raise SystemExit("phase12-libbpf-snapshot:self-test:fixture_drift_stdout")

    print("PHASE12_LIBBPF_SNAPSHOT_SELF_TEST=pass")
    print("PHASE12_LIBBPF_SNAPSHOT_SELF_TEST_CASE_COUNT=16")
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
