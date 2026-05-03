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
FIXTURE_REL_PATH = "zigux/tests/fixtures/phase12_libbpf_snapshot.json"
ARTIFACT_DIFF_REL_PATH = "scripts/zigux/artifact_diff.py"
FIXTURE_PATH = ROOT / FIXTURE_REL_PATH
ARTIFACT_DIFF_PATH = ROOT / ARTIFACT_DIFF_REL_PATH
TRACKED_PATHS = [
    "zigux/tests/phase12_libbpf_manifest.json",
    "zigux/tests/phase12_libbpf_segments.zig",
    "zigux/tests/phase12_libbpf_reviewability.zig",
    "Documentation/zigux/phase12-libbpf-segment-survey.md",
    "tools/lib/bpf/zigux_segments/manifest.json",
]
MANIFEST_REL_PATH = TRACKED_PATHS[0]
SEGMENT_TEST_REL_PATH = TRACKED_PATHS[1]
REVIEWABILITY_TEST_REL_PATH = TRACKED_PATHS[2]
SURVEY_NOTE_REL_PATH = TRACKED_PATHS[3]
REQUIRED_PATHS = [*TRACKED_PATHS, FIXTURE_REL_PATH, ARTIFACT_DIFF_REL_PATH]
HEX40 = re.compile(r"^[0-9a-f]{40}$")
REVIEWABILITY_SNAPSHOT_TEST_NAME = (
    'test "phase12 libbpf reviewability gate pins the committed snapshot fixture packet"'
)
REVIEWABILITY_SNAPSHOT_MARKERS = [
    REVIEWABILITY_SNAPSHOT_TEST_NAME,
    "try std.testing.expectEqual(expected_paths.len, snapshot.tracked_file_count);",
    "try std.testing.expectEqual(expected_paths.len, snapshot.files.len);",
    "try std.testing.expectEqualStrings(expected_path, entry.path);",
    "zigux/tests/phase12_libbpf_manifest.json",
    "zigux/tests/phase12_libbpf_segments.zig",
    "zigux/tests/phase12_libbpf_reviewability.zig",
    "Documentation/zigux/phase12-libbpf-segment-survey.md",
    "tools/lib/bpf/zigux_segments/manifest.json",
]


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


def expected_lane_marker_text(lane_key: str) -> str:
    return f"PHASE12_LANE_KEY={lane_key}"


def validate_lane_marker_alignment(root: Path, manifest_packet: dict[str, str]) -> None:
    lane_marker = expected_lane_marker_text(manifest_packet["lane_key"])
    survey_note = (root / SURVEY_NOTE_REL_PATH).read_text(encoding="utf-8")
    if lane_marker not in survey_note:
        raise SystemExit("invalid Phase 12 libbpf survey note lane marker")
    segment_test = (root / SEGMENT_TEST_REL_PATH).read_text(encoding="utf-8")
    if lane_marker not in segment_test:
        raise SystemExit("invalid Phase 12 libbpf segment test lane marker")


def reviewability_snapshot_gate_source(reviewability_test: str) -> str:
    start = reviewability_test.find(REVIEWABILITY_SNAPSHOT_TEST_NAME)
    if start < 0:
        raise SystemExit("invalid Phase 12 libbpf reviewability snapshot markers")
    next_test = reviewability_test.find('\ntest "', start + len(REVIEWABILITY_SNAPSHOT_TEST_NAME))
    if next_test < 0:
        return reviewability_test[start:]
    return reviewability_test[start:next_test]


def validate_reviewability_snapshot_gate(root: Path) -> None:
    reviewability_test = (root / REVIEWABILITY_TEST_REL_PATH).read_text(encoding="utf-8")
    snapshot_gate = reviewability_snapshot_gate_source(reviewability_test)
    for marker in REVIEWABILITY_SNAPSHOT_MARKERS:
        if snapshot_gate.count(marker) != 1:
            raise SystemExit("invalid Phase 12 libbpf reviewability snapshot markers")


def file_digest(path: Path) -> dict[str, object]:
    data = path.read_bytes()
    return {
        "path": str(path.relative_to(ROOT)),
        "bytes": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
    }


def load_manifest_packet(root: Path = ROOT) -> dict[str, str]:
    manifest = json.loads((root / MANIFEST_REL_PATH).read_text(encoding="utf-8"))
    manifest_packet = validate_manifest_packet(manifest)
    validate_lane_marker_alignment(root, manifest_packet)
    validate_reviewability_snapshot_gate(root)
    return manifest_packet


def render_snapshot(root: Path = ROOT) -> dict[str, object]:
    manifest_packet = load_manifest_packet(root)
    files = [file_digest(root / rel_path) for rel_path in TRACKED_PATHS]
    return {
        "lane_key": manifest_packet["lane_key"],
        "phase": manifest_packet["phase"],
        "surveyed_commit": manifest_packet["surveyed_commit"],
        "tracked_file_count": len(files),
        "files": files,
    }


def compare_snapshot(
    snapshot: dict[str, object],
    fixture_path: Path = FIXTURE_PATH,
    artifact_diff_path: Path = ARTIFACT_DIFF_PATH,
) -> tuple[subprocess.CompletedProcess[str], str]:
    rendered = json.dumps(snapshot, indent=2) + "\n"
    with tempfile.TemporaryDirectory(prefix="zigux_phase12_libbpf_snapshot_") as tmp_dir_str:
        actual_path = Path(tmp_dir_str) / "phase12_libbpf_snapshot.json"
        actual_path.write_text(rendered, encoding="utf-8")
        result = subprocess.run(
            [
                sys.executable,
                str(artifact_diff_path),
                "--mode",
                "json",
                str(fixture_path),
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


def render_snapshot_result_lines(
    *,
    status: str,
    repeat_run: str,
    snapshot: dict[str, object] | None = None,
    rendered: str | None = None,
) -> list[str]:
    lines = [f"PHASE12_LIBBPF_SNAPSHOT={status}", f"PHASE12_LIBBPF_REPEAT_RUN={repeat_run}"]
    if snapshot is not None:
        lines.append(f"PHASE12_LIBBPF_TRACKED_FILE_COUNT={snapshot['tracked_file_count']}")
    if rendered is not None:
        lines.append(
            "PHASE12_LIBBPF_SNAPSHOT_SHA256="
            + hashlib.sha256(rendered.encode("utf-8")).hexdigest()
        )
    return lines


def run_snapshot_check() -> tuple[int, list[str]]:
    missing = missing_required_paths(ROOT)
    if missing:
        return 1, [
            "PHASE12_LIBBPF_SNAPSHOT=fail",
            "PHASE12_LIBBPF_SNAPSHOT_MISSING_START",
            *missing,
            "PHASE12_LIBBPF_SNAPSHOT_MISSING_END",
        ]

    first = render_snapshot()
    second = render_snapshot()
    if first != second:
        return 1, render_snapshot_result_lines(status="fail", repeat_run="drift")

    result, rendered = compare_snapshot(first)
    lines = result.stdout.splitlines()
    if result.returncode != 0:
        return result.returncode, [
            *lines,
            *render_snapshot_result_lines(status="fail", repeat_run="stable"),
        ]

    return 0, [
        *lines,
        *render_snapshot_result_lines(
            status="pass",
            repeat_run="stable",
            snapshot=first,
            rendered=rendered,
        ),
    ]


def copy_required_tree(root: Path) -> None:
    for rel_path in REQUIRED_PATHS:
        target_path = root / rel_path
        target_path.parent.mkdir(parents=True, exist_ok=True)
        target_path.write_bytes((ROOT / rel_path).read_bytes())


def run_self_test() -> int:
    live_manifest = json.loads((ROOT / MANIFEST_REL_PATH).read_text(encoding="utf-8"))
    manifest_packet = validate_manifest_packet(live_manifest)
    lane_marker = expected_lane_marker_text(manifest_packet["lane_key"])
    if manifest_packet["lane_key"] != live_manifest["lane_key"]:
        raise SystemExit("phase12-libbpf-snapshot:self-test:lane_key_round_trip")
    if manifest_packet["phase"] != "Phase 12":
        raise SystemExit("phase12-libbpf-snapshot:self-test:phase_round_trip")
    if manifest_packet["surveyed_commit"] != live_manifest["surveyed_commit"]:
        raise SystemExit("phase12-libbpf-snapshot:self-test:surveyed_commit_round_trip")
    validate_lane_marker_alignment(ROOT, manifest_packet)
    validate_reviewability_snapshot_gate(ROOT)

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

    with tempfile.TemporaryDirectory(prefix="zigux_phase12_libbpf_snapshot_required_") as tmp_dir_str:
        required_root = Path(tmp_dir_str)
        copy_required_tree(required_root)
        if missing_required_paths(required_root):
            raise SystemExit("phase12-libbpf-snapshot:self-test:required_tree_complete")

        (required_root / TRACKED_PATHS[2]).unlink()
        missing = missing_required_paths(required_root)
        if f"missing_file:{TRACKED_PATHS[2]}" not in missing:
            raise SystemExit("phase12-libbpf-snapshot:self-test:missing_tracked_file_detection")

    with tempfile.TemporaryDirectory(prefix="zigux_phase12_libbpf_snapshot_fixture_") as tmp_dir_str:
        fixture_root = Path(tmp_dir_str)
        copy_required_tree(fixture_root)
        (fixture_root / FIXTURE_REL_PATH).unlink()
        missing = missing_required_paths(fixture_root)
        if f"missing_file:{FIXTURE_REL_PATH}" not in missing:
            raise SystemExit("phase12-libbpf-snapshot:self-test:missing_fixture_detection")

    with tempfile.TemporaryDirectory(prefix="zigux_phase12_libbpf_snapshot_artifact_diff_") as tmp_dir_str:
        helper_root = Path(tmp_dir_str)
        copy_required_tree(helper_root)
        (helper_root / ARTIFACT_DIFF_REL_PATH).unlink()
        missing = missing_required_paths(helper_root)
        if f"missing_file:{ARTIFACT_DIFF_REL_PATH}" not in missing:
            raise SystemExit("phase12-libbpf-snapshot:self-test:missing_artifact_diff_detection")

    with tempfile.TemporaryDirectory(prefix="zigux_phase12_libbpf_snapshot_note_marker_") as tmp_dir_str:
        note_root = Path(tmp_dir_str)
        copy_required_tree(note_root)
        note_path = note_root / SURVEY_NOTE_REL_PATH
        note_path.write_text(
            note_path.read_text(encoding="utf-8").replace(f"{lane_marker}\n", ""),
            encoding="utf-8",
        )
        expect_system_exit(
            "invalid_survey_note_lane_marker",
            lambda: load_manifest_packet(note_root),
            "invalid Phase 12 libbpf survey note lane marker",
        )

    with tempfile.TemporaryDirectory(prefix="zigux_phase12_libbpf_snapshot_segment_marker_") as tmp_dir_str:
        segment_root = Path(tmp_dir_str)
        copy_required_tree(segment_root)
        segment_test_path = segment_root / SEGMENT_TEST_REL_PATH
        segment_test_path.write_text(
            segment_test_path.read_text(encoding="utf-8").replace(lane_marker, expected_lane_marker_text("P12-L99")),
            encoding="utf-8",
        )
        expect_system_exit(
            "invalid_segment_test_lane_marker",
            lambda: load_manifest_packet(segment_root),
            "invalid Phase 12 libbpf segment test lane marker",
        )

    with tempfile.TemporaryDirectory(prefix="zigux_phase12_libbpf_snapshot_reviewability_markers_") as tmp_dir_str:
        reviewability_root = Path(tmp_dir_str)
        copy_required_tree(reviewability_root)
        reviewability_test_path = reviewability_root / REVIEWABILITY_TEST_REL_PATH
        reviewability_test_path.write_text(
            reviewability_test_path.read_text(encoding="utf-8").replace(
                "try std.testing.expectEqual(expected_paths.len, snapshot.tracked_file_count);\n",
                "",
            ),
            encoding="utf-8",
        )
        expect_system_exit(
            "invalid_reviewability_snapshot_markers",
            lambda: load_manifest_packet(reviewability_root),
            "invalid Phase 12 libbpf reviewability snapshot markers",
        )

    with tempfile.TemporaryDirectory(prefix="zigux_phase12_libbpf_snapshot_reviewability_files_len_") as tmp_dir_str:
        reviewability_root = Path(tmp_dir_str)
        copy_required_tree(reviewability_root)
        reviewability_test_path = reviewability_root / REVIEWABILITY_TEST_REL_PATH
        reviewability_test_path.write_text(
            reviewability_test_path.read_text(encoding="utf-8").replace(
                "try std.testing.expectEqual(expected_paths.len, snapshot.files.len);\n",
                "",
            ),
            encoding="utf-8",
        )
        expect_system_exit(
            "invalid_reviewability_files_len_marker",
            lambda: load_manifest_packet(reviewability_root),
            "invalid Phase 12 libbpf reviewability snapshot markers",
        )

    with tempfile.TemporaryDirectory(prefix="zigux_phase12_libbpf_snapshot_reviewability_path_assertion_") as tmp_dir_str:
        reviewability_root = Path(tmp_dir_str)
        copy_required_tree(reviewability_root)
        reviewability_test_path = reviewability_root / REVIEWABILITY_TEST_REL_PATH
        reviewability_test_path.write_text(
            reviewability_test_path.read_text(encoding="utf-8").replace(
                "try std.testing.expectEqualStrings(expected_path, entry.path);\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_system_exit(
            "invalid_reviewability_path_assertion_marker",
            lambda: load_manifest_packet(reviewability_root),
            "invalid Phase 12 libbpf reviewability snapshot markers",
        )

    with tempfile.TemporaryDirectory(prefix="zigux_phase12_libbpf_snapshot_reviewability_tracked_path_") as tmp_dir_str:
        reviewability_root = Path(tmp_dir_str)
        copy_required_tree(reviewability_root)
        reviewability_test_path = reviewability_root / REVIEWABILITY_TEST_REL_PATH
        reviewability_test_path.write_text(
            reviewability_test_path.read_text(encoding="utf-8").replace(
                "zigux/tests/phase12_libbpf_manifest.json\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_system_exit(
            "invalid_reviewability_tracked_path_marker",
            lambda: load_manifest_packet(reviewability_root),
            "invalid Phase 12 libbpf reviewability snapshot markers",
        )

    with tempfile.TemporaryDirectory(prefix="zigux_phase12_libbpf_snapshot_reviewability_duplicate_path_") as tmp_dir_str:
        reviewability_root = Path(tmp_dir_str)
        copy_required_tree(reviewability_root)
        reviewability_test_path = reviewability_root / REVIEWABILITY_TEST_REL_PATH
        reviewability_test_path.write_text(
            reviewability_test_path.read_text(encoding="utf-8").replace(
                "zigux/tests/phase12_libbpf_manifest.json\n",
                "zigux/tests/phase12_libbpf_manifest.json\nzigux/tests/phase12_libbpf_manifest.json\n",
                1,
            ),
            encoding="utf-8",
        )
        expect_system_exit(
            "invalid_reviewability_duplicate_path_marker",
            lambda: load_manifest_packet(reviewability_root),
            "invalid Phase 12 libbpf reviewability snapshot markers",
        )

    with tempfile.TemporaryDirectory(prefix="zigux_phase12_libbpf_snapshot_reviewability_test_name_") as tmp_dir_str:
        reviewability_root = Path(tmp_dir_str)
        copy_required_tree(reviewability_root)
        reviewability_test_path = reviewability_root / REVIEWABILITY_TEST_REL_PATH
        reviewability_test_path.write_text(
            reviewability_test_path.read_text(encoding="utf-8").replace(
                'test "phase12 libbpf reviewability gate pins the committed snapshot fixture packet"\n',
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_system_exit(
            "invalid_reviewability_test_name_marker",
            lambda: load_manifest_packet(reviewability_root),
            "invalid Phase 12 libbpf reviewability snapshot markers",
        )

    first = render_snapshot()
    second = render_snapshot()
    if first != second:
        raise SystemExit("phase12-libbpf-snapshot:self-test:repeat_run_stability")

    original_render_snapshot = globals()["render_snapshot"]
    repeat_run_state = {"calls": 0}

    def unstable_render_snapshot(root: Path = ROOT) -> dict[str, object]:
        repeat_run_state["calls"] += 1
        snapshot = original_render_snapshot(root)
        if repeat_run_state["calls"] == 2:
            snapshot = dict(snapshot)
            snapshot["surveyed_commit"] = "0" * 40
        return snapshot

    try:
        globals()["render_snapshot"] = unstable_render_snapshot
        drift_exit_code, drift_lines = run_snapshot_check()
    finally:
        globals()["render_snapshot"] = original_render_snapshot

    if drift_exit_code != 1:
        raise SystemExit("phase12-libbpf-snapshot:self-test:repeat_run_drift_exit_code")
    expected_drift_lines = [
        "PHASE12_LIBBPF_SNAPSHOT=fail",
        "PHASE12_LIBBPF_REPEAT_RUN=drift",
    ]
    if drift_lines != expected_drift_lines:
        raise SystemExit("phase12-libbpf-snapshot:self-test:repeat_run_drift_lines")

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
    expected_pass_lines = [
        "ARTIFACT_DIFF=pass",
        "MODE=json",
        f"EXPECTED={FIXTURE_PATH}",
        "ACTUAL=",
        *render_snapshot_result_lines(
            status="pass",
            repeat_run="stable",
            snapshot=first,
            rendered=json.dumps(first, indent=2) + "\n",
        ),
    ]
    pass_exit_code, pass_lines = run_snapshot_check()
    if pass_exit_code != 0:
        raise SystemExit("phase12-libbpf-snapshot:self-test:pass_exit_code")
    if len(pass_lines) != len(expected_pass_lines):
        raise SystemExit("phase12-libbpf-snapshot:self-test:pass_line_count")
    if pass_lines[:2] != expected_pass_lines[:2]:
        raise SystemExit("phase12-libbpf-snapshot:self-test:pass_prefix")
    if pass_lines[2] != expected_pass_lines[2]:
        raise SystemExit("phase12-libbpf-snapshot:self-test:pass_expected_path")
    if not pass_lines[3].startswith("ACTUAL="):
        raise SystemExit("phase12-libbpf-snapshot:self-test:pass_actual_path")
    if pass_lines[4:] != expected_pass_lines[4:]:
        raise SystemExit("phase12-libbpf-snapshot:self-test:pass_snapshot_lines")

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

    with tempfile.TemporaryDirectory(prefix="zigux_phase12_libbpf_snapshot_missing_root_") as tmp_dir_str:
        missing_root = Path(tmp_dir_str)
        copy_required_tree(missing_root)
        (missing_root / TRACKED_PATHS[1]).unlink()
        original_root = globals()["ROOT"]
        original_fixture_path = globals()["FIXTURE_PATH"]
        original_artifact_diff_path = globals()["ARTIFACT_DIFF_PATH"]
        try:
            globals()["ROOT"] = missing_root
            globals()["FIXTURE_PATH"] = missing_root / FIXTURE_REL_PATH
            globals()["ARTIFACT_DIFF_PATH"] = missing_root / ARTIFACT_DIFF_REL_PATH
            missing_exit_code, missing_lines = run_snapshot_check()
        finally:
            globals()["ROOT"] = original_root
            globals()["FIXTURE_PATH"] = original_fixture_path
            globals()["ARTIFACT_DIFF_PATH"] = original_artifact_diff_path
        if missing_exit_code != 1:
            raise SystemExit("phase12-libbpf-snapshot:self-test:missing_exit_code")
        expected_missing_lines = [
            "PHASE12_LIBBPF_SNAPSHOT=fail",
            "PHASE12_LIBBPF_SNAPSHOT_MISSING_START",
            f"missing_file:{TRACKED_PATHS[1]}",
            "PHASE12_LIBBPF_SNAPSHOT_MISSING_END",
        ]
        if missing_lines != expected_missing_lines:
            raise SystemExit("phase12-libbpf-snapshot:self-test:missing_lines")

    print("PHASE12_LIBBPF_SNAPSHOT_SELF_TEST=pass")
    print("PHASE12_LIBBPF_SNAPSHOT_SELF_TEST_CASE_COUNT=42")
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

    exit_code, lines = run_snapshot_check()
    for line in lines:
        print(line)
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
