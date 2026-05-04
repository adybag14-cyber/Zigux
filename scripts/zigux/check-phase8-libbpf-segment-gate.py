#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]

MANIFEST_PATH = "tools/lib/bpf/zigux_segments/manifest.json"
SURVEY_PATH = "Documentation/zigux/phase8-libbpf-segment-survey.md"
TEST_PATH = "zigux/tests/phase8_libbpf_segments.zig"

EXPECTED_SLUGS = [
    "logging-version-and-errno",
    "pin-path-helpers",
    "cpu-mask-parsing",
    "type-name-helpers",
    "fdinfo-map-info-helpers",
    "map-reuse-compatibility",
    "file-path-and-handle-bridge",
    "perf-buffer-online-cpu-routing",
    "skeleton-population",
    "object-and-elf-loader",
    "btf-relocation-and-program-load",
]

EXPECTED_STATUSES = {
    "starter_landed": 6,
    "blocked_on_object_model": 1,
    "deferred_high_risk": 4,
}

EXPECTED_SEGMENT_DESTINATIONS = {
    "file-path-and-handle-bridge": "tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig",
    "perf-buffer-online-cpu-routing": "tools/lib/bpf/zigux_segments/cpu_mask.zig",
}

SURVEY_MARKERS = [
    "The manifest currently records eleven bounded segments.",
    "That eleven-segment catalog intentionally excludes the separate `perf_buffer_poll.zig` adjunct packet",
    "scope: segment manifest plus six landed helper-first starter slices",
    "active scheduled ownership and cleanup lane for this packet is `P8-L13`",
    "map-reuse-compatibility",
    "file-path-and-handle-bridge",
    "perf-buffer-online-cpu-routing",
]


def read_text(root: Path, rel_path: str) -> str:
    return (root / rel_path).read_text(encoding="utf-8")


def parse_current_surveyed_commit(test_text: str) -> str:
    match = re.search(r'const current_surveyed_commit = "([0-9a-f]{40})";', test_text)
    if match is None:
        raise ValueError("phase8_libbpf_segments_test:missing_current_surveyed_commit")
    return match.group(1)


def parse_destination_array(test_text: str) -> list[str]:
    match = re.search(
        r"const expected_segment_destinations = \[_\]\[\]const u8\{(.*?)\n\};",
        test_text,
        re.S,
    )
    if match is None:
        raise ValueError("phase8_libbpf_segments_test:missing_expected_segment_destinations")
    return re.findall(r'"([^"]+)"', match.group(1))


def validate(root: Path) -> tuple[list[str], list[str]]:
    failures: list[str] = []

    manifest = json.loads(read_text(root, MANIFEST_PATH))
    survey_text = read_text(root, SURVEY_PATH)
    test_text = read_text(root, TEST_PATH)

    note_commit_match = re.search(
        r"survey checkpoint: refreshed against inspected `master` head `([0-9a-f]{40})`",
        survey_text,
    )
    if note_commit_match is None:
        failures.append("survey:missing_surveyed_commit")
        note_commit = None
    else:
        note_commit = note_commit_match.group(1)

    test_commit = parse_current_surveyed_commit(test_text)
    manifest_commit = manifest.get("surveyed_commit")
    if note_commit and (note_commit != manifest_commit or note_commit != test_commit):
        failures.append(
            f"commit_sync:{note_commit}:{manifest_commit}:{test_commit}"
        )

    if manifest.get("lane_key") != "P8-L13":
        failures.append(f"manifest:lane_key:{manifest.get('lane_key')}")

    segments = manifest.get("segments", [])
    if len(segments) != 11:
        failures.append(f"manifest:segment_count:{len(segments)}")

    slugs = [segment.get("slug") for segment in segments]
    if slugs != EXPECTED_SLUGS:
        failures.append("manifest:slug_order")

    counts: dict[str, int] = {}
    for segment in segments:
        status = segment.get("status")
        counts[status] = counts.get(status, 0) + 1
    for status, expected_count in EXPECTED_STATUSES.items():
        if counts.get(status, 0) != expected_count:
            failures.append(f"manifest:status_count:{status}:{counts.get(status, 0)}")

    by_slug = {segment["slug"]: segment for segment in segments}
    for slug, expected_destination in EXPECTED_SEGMENT_DESTINATIONS.items():
        actual_destination = by_slug.get(slug, {}).get("zigux_destination")
        if actual_destination != expected_destination:
            failures.append(
                f"manifest:destination:{slug}:{actual_destination}"
            )

    for marker in SURVEY_MARKERS:
        if marker not in survey_text:
            failures.append(f"survey:marker:{marker}")

    destinations = parse_destination_array(test_text)
    if len(destinations) != len(EXPECTED_SLUGS):
        failures.append(f"test:destination_count:{len(destinations)}")
    else:
        if destinations[6] != EXPECTED_SEGMENT_DESTINATIONS["file-path-and-handle-bridge"]:
            failures.append(
                f"test:destination:file-path-and-handle-bridge:{destinations[6]}"
            )
        if destinations[7] != EXPECTED_SEGMENT_DESTINATIONS["perf-buffer-online-cpu-routing"]:
            failures.append(
                f"test:destination:perf-buffer-online-cpu-routing:{destinations[7]}"
            )

    return failures, [manifest_commit, note_commit or "", test_commit]


def clone_fixture_root(source_root: Path, destination_root: Path) -> None:
    for rel_path in (MANIFEST_PATH, SURVEY_PATH, TEST_PATH):
        target = destination_root / rel_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(read_text(source_root, rel_path), encoding="utf-8")


def run_self_test() -> int:
    source_root = Path.cwd()
    with tempfile.TemporaryDirectory(prefix="phase8_libbpf_gate_") as tmp_dir:
        tmp_root = Path(tmp_dir)
        clone_fixture_root(source_root, tmp_root)

        baseline_failures, _ = validate(tmp_root)
        if baseline_failures:
            raise SystemExit(
                "phase8-libbpf-gate-self-test:baseline_failed:"
                + ",".join(baseline_failures)
            )

        test_path = tmp_root / TEST_PATH
        original_test = test_path.read_text(encoding="utf-8")
        test_path.write_text(
            original_test.replace(
                '"tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig",\n    "tools/lib/bpf/zigux_segments/cpu_mask.zig",',
                '"tools/lib/bpf/zigux_segments/cpu_mask.zig",\n    "tools/lib/bpf/zigux_segments/cpu_mask.zig",',
                1,
            ),
            encoding="utf-8",
        )
        failures, _ = validate(tmp_root)
        if not any(
            failure.startswith("test:destination:file-path-and-handle-bridge:")
            for failure in failures
        ):
            raise SystemExit(
                "phase8-libbpf-gate-self-test:missing_destination_drift_detection"
            )

        test_path.write_text(original_test, encoding="utf-8")
        survey_path = tmp_root / SURVEY_PATH
        original_survey = survey_path.read_text(encoding="utf-8")
        survey_path.write_text(
            original_survey.replace(
                "The manifest currently records eleven bounded segments.",
                "The manifest currently records ten bounded segments.",
                1,
            ),
            encoding="utf-8",
        )
        failures, _ = validate(tmp_root)
        if "survey:marker:The manifest currently records eleven bounded segments." not in failures:
            raise SystemExit(
                "phase8-libbpf-gate-self-test:missing_segment_count_marker_detection"
            )

    print("PHASE8_LIBBPF_SEGMENT_GATE_SELF_TEST=pass")
    print("PHASE8_LIBBPF_SEGMENT_GATE_SELF_TEST_CASE_COUNT=2")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the bounded Phase 8 libbpf segment survey packet."
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run built-in drift checks against a temporary three-file packet clone.",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures, commits = validate(ROOT)
    if failures:
        print("PHASE8_LIBBPF_SEGMENT_GATE=fail")
        print("PHASE8_LIBBPF_SEGMENT_GATE_FAILURES_START")
        for failure in failures:
            print(failure)
        print("PHASE8_LIBBPF_SEGMENT_GATE_FAILURES_END")
        return 1

    print("PHASE8_LIBBPF_SEGMENT_GATE=pass")
    print(f"PHASE8_LIBBPF_SEGMENT_GATE_COMMIT={commits[0]}")
    print(f"PHASE8_LIBBPF_SEGMENT_GATE_SEGMENT_COUNT={len(EXPECTED_SLUGS)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
