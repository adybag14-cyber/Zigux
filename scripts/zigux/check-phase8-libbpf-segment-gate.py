#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import tempfile
from pathlib import Path


SELF_PATH = Path(__file__).resolve()
ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) >= 3 else SELF_PATH.parent

MANIFEST_PATH = "tools/lib/bpf/zigux_segments/manifest.json"
SURVEY_PATH = "Documentation/zigux/phase8-libbpf-segment-survey.md"
TEST_PATH = "zigux/tests/phase8_libbpf_segments.zig"

REQUIRED_FILES = [
    SURVEY_PATH,
    "Documentation/zigux/phase8-file-path-handle-bridge-slice.md",
    "Documentation/zigux/phase8-perf-buffer-poll-slice.md",
    "Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md",
    ".github/workflows/zigux-bootstrap.yml",
    "scripts/zigux/check-phase8-libbpf-segment-gate.py",
    "scripts/zigux/README.md",
    "zigux/Makefile",
    "zigux/tests/phase8_file_path_handle_bridge.zig",
    "zigux/tests/phase8_file_path_handle_bridge_only_build.zig",
    "zigux/tests/phase8_libbpf_segments.zig",
    "zigux/tests/phase8_libbpf_segments_only_build.zig",
    "zigux/tests/phase8_perf_buffer_poll.zig",
    "zigux/tests/phase8_perf_buffer_poll_only_build.zig",
    MANIFEST_PATH,
]

REQUIRED_MARKERS = {
    SURVEY_PATH: [
        "surveyed commit:",
        "tools/lib/bpf/zigux_segments/manifest.json",
        "tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig",
        "tools/lib/bpf/zigux_segments/perf_buffer_poll.zig",
        "zigux/tests/phase8_file_path_handle_bridge_only_build.zig",
        "zigux/tests/phase8_libbpf_segments_only_build.zig",
        "zigux/tests/phase8_perf_buffer_poll_only_build.zig",
        "helper-only reused-map name resolution",
        "perf-buffer-online-cpu-routing",
        "standalone timer or clockevent helper behavior",
        "make -C zigux phase8-libbpf-segments-test",
        "make -C zigux phase8-file-path-handle-bridge-test",
        "make -C zigux phase8-perf-buffer-poll-test",
    ],
    "Documentation/zigux/phase8-file-path-handle-bridge-slice.md": [
        "helper-only reused-map compatibility packet",
        "planning-only reopen-attempt disposition",
        "zigux/tests/phase8_file_path_handle_bridge_only_build.zig",
    ],
    "Documentation/zigux/phase8-perf-buffer-poll-slice.md": [
        "make -C zigux phase8-perf-buffer-poll-test",
        "zig build test --build-file zigux/tests/phase8_perf_buffer_poll_only_build.zig --summary all",
        "no standalone timer helper",
        "no standalone clockevent helper",
    ],
    "Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md": [
        "mapReuseObservationFromFdinfo()",
        "resolveReusePinnedMapAttempt()",
        "non-empty pinned path plus compatible fdinfo-derived map info",
        "fd close or ownership semantics",
    ],
    ".github/workflows/zigux-bootstrap.yml": [
        "Validate Phase 8 tooling packet",
        "Run focused Phase 8 libbpf shard tests",
        "make -C zigux phase8-file-path-handle-bridge-test",
        "make -C zigux phase8-libbpf-segments-test",
        "make -C zigux phase8-perf-buffer-poll-test",
    ],
    "scripts/zigux/README.md": [
        "Phase 8 flow",
        "Documentation/zigux/phase8-libbpf-segment-survey.md",
        "Documentation/zigux/phase8-file-path-handle-bridge-slice.md",
        "Documentation/zigux/phase8-perf-buffer-poll-slice.md",
        "zigux/tests/phase8_file_path_handle_bridge.zig",
        "zigux/tests/phase8_file_path_handle_bridge_only_build.zig",
        "zigux/tests/phase8_libbpf_segments.zig",
        "zigux/tests/phase8_libbpf_segments_only_build.zig",
        "zigux/tests/phase8_perf_buffer_poll.zig",
        "zigux/tests/phase8_perf_buffer_poll_only_build.zig",
        "make -C zigux phase8-file-path-handle-bridge-test",
        "make -C zigux phase8-libbpf-segments-test",
        "make -C zigux phase8-perf-buffer-poll-test",
    ],
    "zigux/Makefile": [
        "phase8-validate:",
        "phase8-file-path-handle-bridge-test:",
        "phase8-libbpf-segments-test:",
        "phase8-perf-buffer-poll-test:",
        "$(ZIG) build test --build-file zigux/tests/phase8_file_path_handle_bridge_only_build.zig --summary all",
        "$(ZIG) build test --build-file zigux/tests/phase8_libbpf_segments_only_build.zig --summary all",
        "$(ZIG) build test --build-file zigux/tests/phase8_perf_buffer_poll_only_build.zig --summary all",
    ],
    "zigux/tests/phase8_file_path_handle_bridge.zig": [
        "phase 8 file-path handle bridge helper keeps fdinfo observations reusable for planning-only compatibility",
        "phase 8 file-path handle bridge helper keeps planning-only reopen attempts explicit",
        "mapReuseObservationFromFdinfo",
    ],
    "zigux/tests/phase8_file_path_handle_bridge_only_build.zig": [
        "../../tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig",
        "\"phase8_file_path_handle_bridge.zig\"",
        "phase8-file-path-handle-bridge-tests",
    ],
    TEST_PATH: [
        "phase 8 libbpf segment manifest records the current helper-first catalog",
        "phase 8 libbpf survey note keeps segmented helper-first rollout explicit",
        "phase 8 libbpf survey note stays aligned with the landed helper packet and workflow shards",
        "perf-buffer-online-cpu-routing",
        "standalone timer or clockevent helper behavior",
    ],
    "zigux/tests/phase8_libbpf_segments_only_build.zig": [
        "\"phase8_libbpf_segments.zig\"",
        "phase8-libbpf-segment-tests",
        "Run focused Phase 8 libbpf segment survey tests",
    ],
    "zigux/tests/phase8_perf_buffer_poll.zig": [
        "ready-buffer processing attempts cannot exceed observed ready events",
        "ready-buffer processing attempts cannot exceed counted ready buffers before any broader observed-event budget mismatch",
        "non-ready wait observations cannot claim record processing",
    ],
    "zigux/tests/phase8_perf_buffer_poll_only_build.zig": [
        "../../tools/lib/bpf/zigux_segments/perf_buffer_poll.zig",
        "\"phase8_perf_buffer_poll.zig\"",
        "phase8-perf-buffer-poll-tests",
    ],
    MANIFEST_PATH: [
        "\"surveyed_commit\":",
        "\"fdinfo-map-info-helpers\"",
        "\"map-reuse-compatibility\"",
        "\"file-path-and-handle-bridge\"",
        "\"perf-buffer-online-cpu-routing\"",
        "\"perf-buffer-poll-bookkeeping\"",
    ],
}

EXACT_ONCE_SECTION_MARKERS = {
    SURVEY_PATH: [
        {
            "start": "product boundary:\n",
            "end": "\n## Why this slice exists",
            "needle": "  - `zigux/tests/phase8_libbpf_segments_only_build.zig`\n",
        },
    ],
}


def collect_missing_files(root: Path) -> list[str]:
    return [rel for rel in REQUIRED_FILES if not (root / rel).exists()]


def collect_missing_markers(root: Path) -> list[str]:
    missing: list[str] = []
    for rel, markers in REQUIRED_MARKERS.items():
        path = root / rel
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        for marker in markers:
            if marker not in text:
                missing.append(f"{rel}: {marker}")
    return missing


def collect_exact_section_errors(root: Path) -> list[str]:
    errors: list[str] = []
    for rel, section_specs in EXACT_ONCE_SECTION_MARKERS.items():
        text = (root / rel).read_text(encoding="utf-8")
        for spec in section_specs:
            start = text.find(spec["start"])
            if start == -1:
                errors.append(f"{rel}: missing_section_start:{spec['start'].strip()}")
                continue

            section_start = start + len(spec["start"])
            end = text.find(spec["end"], section_start)
            if end == -1:
                errors.append(f"{rel}: missing_section_end:{spec['end'].strip()}")
                continue

            section = text[section_start:end]
            if section.count(spec["needle"]) != 1:
                errors.append(
                    f"{rel}: exact_once_section_marker:{spec['needle'].rstrip()}"
                )
    return errors


def load_manifest(root: Path) -> tuple[dict[str, object] | None, list[str]]:
    path = root / MANIFEST_PATH
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None, [f"{MANIFEST_PATH}: invalid_json"]

    if not isinstance(payload, dict):
        return None, [f"{MANIFEST_PATH}: manifest_not_object"]
    return payload, []


def collect_manifest_alignment_errors(root: Path) -> list[str]:
    payload, errors = load_manifest(root)
    if errors:
        return errors

    assert payload is not None
    surveyed_commit = payload.get("surveyed_commit")
    if not isinstance(surveyed_commit, str):
        return [f"{MANIFEST_PATH}: missing_surveyed_commit"]
    if re.fullmatch(r"[0-9a-f]{40}", surveyed_commit) is None:
        return [f"{MANIFEST_PATH}: invalid_surveyed_commit_shape:{surveyed_commit}"]

    survey_text = (root / SURVEY_PATH).read_text(encoding="utf-8")
    test_text = (root / TEST_PATH).read_text(encoding="utf-8")

    alignment_errors: list[str] = []
    if surveyed_commit not in survey_text:
        alignment_errors.append(f"{SURVEY_PATH}: missing_surveyed_commit:{surveyed_commit}")
    if surveyed_commit not in test_text:
        alignment_errors.append(f"{TEST_PATH}: missing_surveyed_commit:{surveyed_commit}")

    segments = payload.get("segments")
    if not isinstance(segments, list):
        alignment_errors.append(f"{MANIFEST_PATH}: segments_not_list")
        return alignment_errors

    status_by_slug: dict[str, str] = {}
    for item in segments:
        if not isinstance(item, dict):
            alignment_errors.append(f"{MANIFEST_PATH}: segment_not_object")
            return alignment_errors
        slug = item.get("slug")
        status = item.get("status")
        if isinstance(slug, str) and isinstance(status, str):
            status_by_slug[slug] = status

    expected_statuses = {
        "fdinfo-map-info-helpers": "starter_landed",
        "map-reuse-compatibility": "starter_landed",
        "file-path-and-handle-bridge": "deferred_high_risk",
        "perf-buffer-online-cpu-routing": "deferred_high_risk",
        "perf-buffer-poll-bookkeeping": "starter_landed",
    }
    for slug, expected_status in expected_statuses.items():
        observed_status = status_by_slug.get(slug)
        if observed_status is None:
            alignment_errors.append(f"{MANIFEST_PATH}: missing_slug:{slug}")
        elif observed_status != expected_status:
            alignment_errors.append(
                f"{MANIFEST_PATH}: wrong_status:{slug}:{expected_status}:{observed_status}"
            )

    return alignment_errors


def validate(root: Path) -> tuple[list[str], list[str], list[str]]:
    missing_files = collect_missing_files(root)
    if missing_files:
        return missing_files, [], []

    marker_errors = collect_missing_markers(root)
    marker_errors.extend(collect_exact_section_errors(root))
    alignment_errors = collect_manifest_alignment_errors(root)
    return [], marker_errors, alignment_errors


def fixture_text(rel: str) -> str:
    if rel == "scripts/zigux/check-phase8-libbpf-segment-gate.py":
        return "# fixture\n"
    if rel == MANIFEST_PATH:
        return json.dumps(
            {
                "surveyed_commit": "0e8ce03f80f631368bfa3c32452d615bb629e3db",
                "segments": [
                    {"slug": "fdinfo-map-info-helpers", "status": "starter_landed"},
                    {"slug": "map-reuse-compatibility", "status": "starter_landed"},
                    {"slug": "file-path-and-handle-bridge", "status": "deferred_high_risk"},
                    {"slug": "perf-buffer-online-cpu-routing", "status": "deferred_high_risk"},
                    {"slug": "perf-buffer-poll-bookkeeping", "status": "starter_landed"},
                ],
            },
            indent=2,
        ) + "\n"
    if rel == SURVEY_PATH:
        body = "\n".join(REQUIRED_MARKERS[rel])
        return (
            "product boundary:\n"
            "  - `zigux/tests/phase8_libbpf_segments_only_build.zig`\n\n"
            "## Why this slice exists\n"
            f"{body}\n"
            "surveyed commit: `0e8ce03f80f631368bfa3c32452d615bb629e3db`\n"
        )
    if rel == TEST_PATH:
        body = "\n".join(REQUIRED_MARKERS[rel])
        return (
            "const expected_surveyed_commit = "
            '"0e8ce03f80f631368bfa3c32452d615bb629e3db";\n'
            f"{body}\n"
        )
    return "\n".join(REQUIRED_MARKERS.get(rel, ["# fixture"])) + "\n"


def write_fixture_root(root: Path) -> None:
    for rel in REQUIRED_FILES:
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(fixture_text(rel), encoding="utf-8")


def expect_missing_file(case: str, tmp_root: Path, rel: str) -> None:
    missing_files, marker_errors, alignment_errors = validate(tmp_root)
    assert marker_errors == [], case
    assert alignment_errors == [], case
    assert missing_files == [rel], case


def expect_marker_error(case: str, tmp_root: Path, expected: str) -> None:
    missing_files, marker_errors, alignment_errors = validate(tmp_root)
    assert missing_files == [], case
    assert alignment_errors == [], case
    assert marker_errors == [expected], case


def expect_alignment_error(case: str, tmp_root: Path, expected: str) -> None:
    missing_files, marker_errors, alignment_errors = validate(tmp_root)
    assert missing_files == [], case
    assert marker_errors == [], case
    assert alignment_errors == [expected], case


def mutate_file(tmp_root: Path, rel: str, old: str, new: str, case: str) -> None:
    path = tmp_root / rel
    original = path.read_text(encoding="utf-8")
    updated = original.replace(old, new, 1)
    assert updated != original, case
    path.write_text(updated, encoding="utf-8")


def run_self_test() -> None:
    missing_file_cases = [
        ("missing_checker", "scripts/zigux/check-phase8-libbpf-segment-gate.py"),
        ("missing_survey", SURVEY_PATH),
        ("missing_manifest", MANIFEST_PATH),
        ("missing_test", TEST_PATH),
        ("missing_makefile", "zigux/Makefile"),
    ]

    marker_cases = [
        (
            "survey_missing_bridge_route",
            SURVEY_PATH,
            "make -C zigux phase8-file-path-handle-bridge-test",
            "make -C zigux phase8-bridge-test",
            f"{SURVEY_PATH}: make -C zigux phase8-file-path-handle-bridge-test",
        ),
        (
            "survey_missing_perf_buffer_note",
            SURVEY_PATH,
            "standalone timer or clockevent helper behavior",
            "standalone timer helper behavior",
            f"{SURVEY_PATH}: standalone timer or clockevent helper behavior",
        ),
        (
            "survey_exact_once_duplicate",
            SURVEY_PATH,
            "  - `zigux/tests/phase8_libbpf_segments_only_build.zig`\n",
            "  - `zigux/tests/phase8_libbpf_segments_only_build.zig`\n"
            "  - `zigux/tests/phase8_libbpf_segments_only_build.zig`\n",
            f"{SURVEY_PATH}: exact_once_section_marker:  - `zigux/tests/phase8_libbpf_segments_only_build.zig`",
        ),
        (
            "scripts_readme_missing_perf_route",
            "scripts/zigux/README.md",
            "make -C zigux phase8-perf-buffer-poll-test",
            "make -C zigux phase8-perf-buffer-test",
            "scripts/zigux/README.md: make -C zigux phase8-perf-buffer-poll-test",
        ),
        (
            "workflow_missing_libbpf_step",
            ".github/workflows/zigux-bootstrap.yml",
            "make -C zigux phase8-libbpf-segments-test",
            "make -C zigux phase8-libbpf-test",
            ".github/workflows/zigux-bootstrap.yml: make -C zigux phase8-libbpf-segments-test",
        ),
        (
            "bridge_test_missing_fdinfo_observation_marker",
            "zigux/tests/phase8_file_path_handle_bridge.zig",
            "mapReuseObservationFromFdinfo",
            "mapReuseObservation",
            "zigux/tests/phase8_file_path_handle_bridge.zig: mapReuseObservationFromFdinfo",
        ),
        (
            "perf_poll_missing_guard",
            "zigux/tests/phase8_perf_buffer_poll.zig",
            "non-ready wait observations cannot claim record processing",
            "non-ready wait observations stay explicit",
            "zigux/tests/phase8_perf_buffer_poll.zig: non-ready wait observations cannot claim record processing",
        ),
    ]

    alignment_cases = [
        (
            "invalid_commit_shape",
            MANIFEST_PATH,
            '"0e8ce03f80f631368bfa3c32452d615bb629e3db"',
            '"not-a-commit"',
            f"{MANIFEST_PATH}: invalid_surveyed_commit_shape:not-a-commit",
        ),
        (
            "survey_commit_drift",
            SURVEY_PATH,
            "0e8ce03f80f631368bfa3c32452d615bb629e3db",
            "1111111111111111111111111111111111111111",
            f"{SURVEY_PATH}: missing_surveyed_commit:0e8ce03f80f631368bfa3c32452d615bb629e3db",
        ),
        (
            "test_commit_drift",
            TEST_PATH,
            "0e8ce03f80f631368bfa3c32452d615bb629e3db",
            "2222222222222222222222222222222222222222",
            f"{TEST_PATH}: missing_surveyed_commit:0e8ce03f80f631368bfa3c32452d615bb629e3db",
        ),
        (
            "segment_status_drift",
            MANIFEST_PATH,
            '"perf-buffer-poll-bookkeeping",\n      "status": "starter_landed"',
            '"perf-buffer-poll-bookkeeping",\n      "status": "deferred_high_risk"',
            f"{MANIFEST_PATH}: wrong_status:perf-buffer-poll-bookkeeping:starter_landed:deferred_high_risk",
        ),
    ]

    with tempfile.TemporaryDirectory(prefix="zigux_phase8_libbpf_gate_") as tmp_dir_str:
        tmp_root = Path(tmp_dir_str)
        write_fixture_root(tmp_root)
        assert validate(tmp_root) == ([], [], [])

        for case, rel in missing_file_cases:
            (tmp_root / rel).unlink()
            expect_missing_file(case, tmp_root, rel)
            write_fixture_root(tmp_root)

        for case, rel, old, new, expected in marker_cases:
            mutate_file(tmp_root, rel, old, new, case)
            expect_marker_error(case, tmp_root, expected)
            write_fixture_root(tmp_root)

        for case, rel, old, new, expected in alignment_cases:
            mutate_file(tmp_root, rel, old, new, case)
            expect_alignment_error(case, tmp_root, expected)
            write_fixture_root(tmp_root)

    print("PHASE8_LIBBPF_SEGMENT_GATE_SELF_TEST=pass")
    print(
        "PHASE8_LIBBPF_SEGMENT_GATE_SELF_TEST_CASE_COUNT="
        f"{len(missing_file_cases) + len(marker_cases) + len(alignment_cases)}"
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the focused Phase 8 libbpf segment survey packet."
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run checker self-test cases without reading repo files.",
    )
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return 0

    missing_files, marker_errors, alignment_errors = validate(ROOT)
    if missing_files:
        print("PHASE8_LIBBPF_SEGMENT_GATE=fail")
        print("MISSING_PHASE8_LIBBPF_SEGMENT_FILES_START")
        for item in missing_files:
            print(item)
        print("MISSING_PHASE8_LIBBPF_SEGMENT_FILES_END")
        return 1

    if marker_errors:
        print("PHASE8_LIBBPF_SEGMENT_GATE=fail")
        print("MISSING_PHASE8_LIBBPF_SEGMENT_MARKERS_START")
        for item in marker_errors:
            print(item)
        print("MISSING_PHASE8_LIBBPF_SEGMENT_MARKERS_END")
        return 1

    if alignment_errors:
        print("PHASE8_LIBBPF_SEGMENT_GATE=fail")
        print("PHASE8_LIBBPF_SEGMENT_ALIGNMENT_ERRORS_START")
        for item in alignment_errors:
            print(item)
        print("PHASE8_LIBBPF_SEGMENT_ALIGNMENT_ERRORS_END")
        return 1

    print("PHASE8_LIBBPF_SEGMENT_GATE=pass")
    print(f"PHASE8_LIBBPF_SEGMENT_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(
        "PHASE8_LIBBPF_SEGMENT_REQUIRED_MARKER_COUNT="
        f"{sum(len(markers) for markers in REQUIRED_MARKERS.values())}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
