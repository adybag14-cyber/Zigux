#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
import tempfile
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve()
ROOT = SCRIPT_PATH.parents[2] if len(SCRIPT_PATH.parents) > 2 else SCRIPT_PATH.parent

SHARED_REQUIRED_FILES = [
    ".github/workflows/zigux-bootstrap.yml",
    "Documentation/zigux/phase8-tooling-lane-sequencing.md",
    "Documentation/zigux/review-checklist.md",
    "scripts/zigux/README.md",
    "scripts/zigux/validate-phase8.py",
    "scripts/zigux/check-phase8-libbpf-shard-routes.py",
    "zigux/Makefile",
    "zigux/tests/README.md",
]

LEGACY_SEGMENT_PACKET_FILES = [
    "Documentation/zigux/phase8-libbpf-segment-survey.md",
    "zigux/tests/phase8_libbpf_segments.zig",
    "zigux/tests/phase8_libbpf_segments_only_build.zig",
    "tools/lib/bpf/zigux_segments/manifest.json",
]

SHARED_REQUIRED_MARKERS = {
    ".github/workflows/zigux-bootstrap.yml": [
        "Validate Phase 8 tooling packet",
        "make -C zigux phase8-validate",
    ],
    "Documentation/zigux/phase8-tooling-lane-sequencing.md": [
        "### 3. Libbpf helper lane",
        "### 4. Shared wording lane",
        "the current tree exposes `tools/lib/bpf/zigux_segments/manifest.json`",
        "`zigux/tests/phase8_cpu_mask.zig`",
        "`zigux/tests/phase8_libbpf_segments.zig`",
        "do not let older absent-file assumptions overrule current tree evidence",
    ],
    "Documentation/zigux/review-checklist.md": [
        "if the change touches the shared parked Phase 8 libbpf packet",
        "Documentation/zigux/phase8-tooling-lane-sequencing.md",
        "scripts/zigux/validate-phase8.py",
    ],
    "scripts/zigux/README.md": [
        "scripts/zigux/validate-phase8.py",
        "scripts/zigux/check-phase8-libbpf-shard-routes.py",
        "Documentation/zigux/phase8-tooling-lane-sequencing.md",
        "make -C zigux phase8-validate",
    ],
    "scripts/zigux/validate-phase8.py": [
        "Documentation/zigux/phase8-tooling-lane-sequencing.md",
        "scripts/zigux/check-phase8-libbpf-shard-routes.py",
        "zigux/Makefile",
        "zigux/tests/README.md",
    ],
    "scripts/zigux/check-phase8-libbpf-shard-routes.py": [
        "### 4. Shared wording lane",
        "Keep the shared wording lane parked until a fresh one-file reminder-surface drift appears.",
        "scripts/zigux/validate-phase8.py",
    ],
    "zigux/Makefile": [
        "phase8-validate:",
        "scripts/zigux/validate-phase8.py",
    ],
    "zigux/tests/README.md": [
        "scripts/zigux/validate-phase8.py",
        "make -C zigux phase8-validate",
    ],
}

LEGACY_PACKET_REQUIRED_MARKERS = {
    ".github/workflows/zigux-bootstrap.yml": [
        "Run focused Phase 8 libbpf shard tests",
        "make -C zigux phase8-libbpf-segments-test",
    ],
    "Documentation/zigux/README.md": [
        "Documentation/zigux/phase8-libbpf-segment-survey.md",
        "tools/lib/bpf/zigux_segments/manifest.json",
        "zigux/tests/phase8_libbpf_segments_only_build.zig",
        "zigux/tests/phase8_libbpf_segments.zig",
    ],
    "Documentation/zigux/phase8-libbpf-segment-survey.md": [
        "tools/lib/bpf/zigux_segments/manifest.json",
        "zigux/tests/phase8_libbpf_segments.zig",
        "zigux/tests/phase8_libbpf_segments_only_build.zig",
        "make -C zigux phase8-libbpf-segments-test",
    ],
    "Documentation/zigux/phase8-tooling-lane-sequencing.md": [
        "tools/lib/bpf/zigux_segments/manifest.json",
        "zigux/tests/phase8_libbpf_segments.zig",
    ],
    "Documentation/zigux/review-checklist.md": [
        "tools/lib/bpf/zigux_segments/manifest.json",
        "zigux/tests/phase8_libbpf_segments.zig",
        "zigux/tests/phase8_libbpf_segments_only_build.zig",
        "make -C zigux phase8-libbpf-segments-test",
    ],
    "scripts/zigux/README.md": [
        "zigux/tests/phase8_libbpf_segments_only_build.zig",
        "make -C zigux phase8-libbpf-segments-test",
    ],
    "zigux/Makefile": [
        "phase8-libbpf-segments-test:",
        "zigux/tests/phase8_libbpf_segments_only_build.zig --summary all",
    ],
    "zigux/tests/README.md": [
        "zigux/tests/phase8_libbpf_segments.zig",
        "zigux/tests/phase8_libbpf_segments_only_build.zig",
        "make -C zigux phase8-libbpf-segments-test",
    ],
    "zigux/tests/phase8_libbpf_segments_only_build.zig": [
        "phase8_libbpf_segments.zig",
    ],
    "tools/lib/bpf/zigux_segments/manifest.json": [
        "\"surveyed_commit\":",
        "\"segments\": [",
        "\"segmentation_notes\": [",
    ],
}

PARKED_DRIFT_MARKERS = {
    ".github/workflows/zigux-bootstrap.yml": [
        "Run focused Phase 8 libbpf shard tests",
        "make -C zigux phase8-libbpf-segments-test",
    ],
    "Documentation/zigux/README.md": [
        "Documentation/zigux/phase8-libbpf-segment-survey.md",
        "tools/lib/bpf/zigux_segments/manifest.json",
        "zigux/tests/phase8_libbpf_segments_only_build.zig",
        "zigux/tests/phase8_libbpf_segments.zig",
    ],
    "Documentation/zigux/review-checklist.md": [
        "Documentation/zigux/phase8-libbpf-segment-survey.md",
        "tools/lib/bpf/zigux_segments/manifest.json",
        "zigux/tests/phase8_libbpf_segments.zig",
        "zigux/tests/phase8_libbpf_segments_only_build.zig",
        "make -C zigux phase8-libbpf-segments-test",
    ],
    "scripts/zigux/README.md": [
        "Documentation/zigux/phase8-libbpf-segment-survey.md",
        "zigux/tests/phase8_libbpf_segments_only_build.zig",
        "make -C zigux phase8-libbpf-segments-test",
    ],
    "zigux/tests/README.md": [
        "zigux/tests/phase8_libbpf_segments.zig",
        "zigux/tests/phase8_libbpf_segments_only_build.zig",
        "make -C zigux phase8-libbpf-segments-test",
    ],
    "zigux/Makefile": [
        "phase8-libbpf-segments-test:",
        "zigux/tests/phase8_libbpf_segments_only_build.zig --summary all",
    ],
}

SURVEYED_COMMIT_NOTE_RE = re.compile(
    r"(?:survey checkpoint: refreshed against inspected `master` head|surveyed commit:)\s*`?([0-9a-f]{40})`?"
)
SURVEYED_COMMIT_TEST_RE = re.compile(
    r'const (?:(?:current|expected)_)?surveyed_commit = "([0-9a-f]{40})";'
)
SURVEYED_COMMIT_MANIFEST_RE = re.compile(
    r'"surveyed_commit"\s*:\s*"([0-9a-f]{40})"'
)

EXPECTED_BRIDGE_SEGMENTS = {
    "fdinfo-map-info-helpers": {
        "status": "starter_landed",
        "kind": "helper_first",
        "zigux_destination": "tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig",
    },
    "map-reuse-compatibility": {
        "status": "starter_landed",
        "kind": "helper_first",
        "zigux_destination": "tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig",
    },
    "file-path-and-handle-bridge": {
        "status": "deferred_high_risk",
        "kind": "resource_boundary",
        "zigux_destination": "tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig",
    },
}

EXPECTED_BRIDGE_LANDED_SCOPE = [
    "buildProcFdinfoPath() bounded /proc//fdinfo/ pathname shaping",
    "parseFdinfoLine() field splitting and trimming",
    "applyFdinfoMapInfoLine() numeric field decoding for map_type/key_size/value_size/max_entries/map_flags/map_extra",
    "parseFdinfoMapInfo() line-by-line fdinfo map metadata parsing",
    "summarizeFdinfoMapInfo() bounded completion reporting for the parsed map info packet",
    "mapReuseObservationFromFdinfo() helper-only conversion from parsed fdinfo metadata into a reusable comparison observation",
    "resolveReusedMapName() object-name retention for truncated reused-map names",
    "normalizeObservedReuseMapFlags() devmap readonly-prog normalization for reuse comparison",
    "summarizeMapReuseCompatibility() mismatch reporting for helper-only reused-map compatibility checks",
    "isMapReuseCompatible() helper-only reused-map compatibility comparison",
    "resolveReusePinnedMapAttempt() helper-only pinned-map reuse planning without procfs, bpffs, or fd side effects",
]

EXPECTED_BRIDGE_QUEUED_SCOPE = [
    "direct procfs reads and descriptor ownership flow",
    "token creation, bpffs reopen flow, and other fd-handle bridge side effects",
]

EXPECTED_BRIDGE_WHY_NOW = (
    "The shared file-path bridge destination now records the fdinfo parsing foundation, "
    "helper-only observation shaping, reused-map compatibility summaries, and pinned-map reuse "
    "planning packet as a reviewable landed helper slice, so future surveys can keep promoting "
    "bounded bridge behavior without crossing into live descriptor or reopen side effects."
)

FIXTURE_TEXT = {
    ".github/workflows/zigux-bootstrap.yml": """name: zigux-bootstrap

- name: Validate Phase 8 tooling packet
  run: make -C zigux phase8-validate

- name: Run focused Phase 8 libbpf shard tests
  run: make -C zigux phase8-libbpf-segments-test
""",
    "Documentation/zigux/README.md": """# Zigux Documentation

- `Documentation/zigux/phase8-libbpf-segment-survey.md`
- `tools/lib/bpf/zigux_segments/manifest.json`
- `zigux/tests/phase8_libbpf_segments_only_build.zig`
- `zigux/tests/phase8_libbpf_segments.zig`
""",
    "Documentation/zigux/phase8-libbpf-segment-survey.md": """# Phase 8 Libbpf Segment Survey

- surveyed commit: `0123456789abcdef0123456789abcdef01234567`
- tools/lib/bpf/zigux_segments/manifest.json
- zigux/tests/phase8_libbpf_segments.zig
- zigux/tests/phase8_libbpf_segments_only_build.zig
- make -C zigux phase8-libbpf-segments-test
""",
    "Documentation/zigux/phase8-tooling-lane-sequencing.md": """# Phase 8 Tooling Lane Sequencing

### 3. Libbpf helper lane
- the current tree exposes `tools/lib/bpf/zigux_segments/manifest.json`
- the current Phase 8 test packet includes `zigux/tests/phase8_cpu_mask.zig`, `zigux/tests/phase8_logging.zig`, `zigux/tests/phase8_pin_path.zig`, `zigux/tests/phase8_bpf_type_names.zig`, `zigux/tests/phase8_file_path_handle_bridge.zig`, `zigux/tests/phase8_perf_buffer_poll.zig`, and `zigux/tests/phase8_libbpf_segments.zig`

### 4. Shared wording lane
- Keep follow-up inside the shared wording lane
- do not let older absent-file assumptions overrule current tree evidence
""",
    "Documentation/zigux/review-checklist.md": """# Zigux Review Checklist

- if the change touches the shared parked Phase 8 libbpf packet
- Documentation/zigux/phase8-tooling-lane-sequencing.md
- scripts/zigux/validate-phase8.py
- Documentation/zigux/phase8-libbpf-segment-survey.md
- tools/lib/bpf/zigux_segments/manifest.json
- zigux/tests/phase8_libbpf_segments.zig
- zigux/tests/phase8_libbpf_segments_only_build.zig
- make -C zigux phase8-libbpf-segments-test
""",
    "scripts/zigux/README.md": """# scripts/zigux

- scripts/zigux/validate-phase8.py
- scripts/zigux/check-phase8-libbpf-shard-routes.py
- Documentation/zigux/phase8-tooling-lane-sequencing.md
- make -C zigux phase8-validate
- Documentation/zigux/phase8-libbpf-segment-survey.md
- zigux/tests/phase8_libbpf_segments_only_build.zig
- make -C zigux phase8-libbpf-segments-test
""",
    "scripts/zigux/validate-phase8.py": """# fixture
Documentation/zigux/phase8-tooling-lane-sequencing.md
scripts/zigux/check-phase8-libbpf-shard-routes.py
zigux/Makefile
zigux/tests/README.md
""",
    "scripts/zigux/check-phase8-libbpf-shard-routes.py": """# fixture
### 4. Shared wording lane
Keep the shared wording lane parked until a fresh one-file reminder-surface drift appears.
scripts/zigux/validate-phase8.py
""",
    "zigux/Makefile": """phase8-validate:
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase8.py

phase8-libbpf-segments-test:
	cd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/phase8_libbpf_segments_only_build.zig --summary all
""",
    "zigux/tests/README.md": """# zigux/tests

- scripts/zigux/validate-phase8.py
- make -C zigux phase8-validate
- zigux/tests/phase8_libbpf_segments.zig
- zigux/tests/phase8_libbpf_segments_only_build.zig
- make -C zigux phase8-libbpf-segments-test
""",
    "zigux/tests/phase8_libbpf_segments.zig": """const expected_surveyed_commit = \"0123456789abcdef0123456789abcdef01234567\";
""",
    "zigux/tests/phase8_libbpf_segments_only_build.zig": """const root_module = b.createModule(.{
    .root_source_file = b.path(\"phase8_libbpf_segments.zig\"),
});
""",
    "tools/lib/bpf/zigux_segments/manifest.json": json.dumps(
        {
            "surveyed_commit": "0123456789abcdef0123456789abcdef01234567",
            "segments": [
                {
                    "slug": "fdinfo-map-info-helpers",
                    "status": "starter_landed",
                    "kind": "helper_first",
                    "zigux_destination": "tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig",
                },
                {
                    "slug": "map-reuse-compatibility",
                    "status": "starter_landed",
                    "kind": "helper_first",
                    "zigux_destination": "tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig",
                },
                {
                    "slug": "file-path-and-handle-bridge",
                    "status": "deferred_high_risk",
                    "kind": "resource_boundary",
                    "zigux_destination": "tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig",
                },
            ],
            "segmentation_notes": [
                {
                    "destination": "tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig",
                    "landed_scope": EXPECTED_BRIDGE_LANDED_SCOPE,
                    "queued_scope": EXPECTED_BRIDGE_QUEUED_SCOPE,
                    "why_now": EXPECTED_BRIDGE_WHY_NOW,
                }
            ],
        },
        indent=2,
    )
    + "\n",
}


def read_text(root: Path, rel_path: str) -> str:
    return (root / rel_path).read_text(encoding="utf-8")


def collect_missing_files(root: Path, rel_paths: list[str]) -> list[str]:
    return [rel_path for rel_path in rel_paths if not (root / rel_path).exists()]


def collect_missing_markers(root: Path, markers_by_file: dict[str, list[str]]) -> list[str]:
    missing: list[str] = []
    for rel_path, markers in markers_by_file.items():
        path = root / rel_path
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        for marker in markers:
            if marker not in text:
                missing.append(f"{rel_path}:{marker}")
    return missing


def collect_present_markers(root: Path, markers_by_file: dict[str, list[str]]) -> list[str]:
    present: list[str] = []
    for rel_path, markers in markers_by_file.items():
        path = root / rel_path
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        for marker in markers:
            if marker in text:
                present.append(f"{rel_path}:{marker}")
    return present


def required_marker_count() -> int:
    return sum(len(markers) for markers in SHARED_REQUIRED_MARKERS.values())


def find_required_commit(text: str, pattern: re.Pattern[str], label: str) -> str:
    match = pattern.search(text)
    if match is None:
        raise ValueError(label)
    return match.group(1)


def parked_wording_mode(root: Path) -> bool:
    lane_note = root / "Documentation/zigux/phase8-tooling-lane-sequencing.md"
    if not lane_note.exists():
        return False
    text = lane_note.read_text(encoding="utf-8")
    required = [
        "### 4. Shared wording lane",
        "the current tree exposes `tools/lib/bpf/zigux_segments/manifest.json`",
        "do not let older absent-file assumptions overrule current tree evidence",
    ]
    return all(marker in text for marker in required)


def validate_bridge_segmentation_contract(root: Path) -> list[str]:
    manifest = json.loads(read_text(root, "tools/lib/bpf/zigux_segments/manifest.json"))
    problems: list[str] = []

    segments = manifest.get("segments")
    if not isinstance(segments, list):
        return ["tools/lib/bpf/zigux_segments/manifest.json:segments:not_a_list"]

    by_slug = {
        segment.get("slug"): segment
        for segment in segments
        if isinstance(segment, dict) and isinstance(segment.get("slug"), str)
    }

    for slug, expected in EXPECTED_BRIDGE_SEGMENTS.items():
        segment = by_slug.get(slug)
        if segment is None:
            problems.append(f"tools/lib/bpf/zigux_segments/manifest.json:missing_bridge_segment:{slug}")
            continue
        for field, expected_value in expected.items():
            if segment.get(field) != expected_value:
                problems.append(
                    "tools/lib/bpf/zigux_segments/manifest.json:"
                    f"bridge_segment:{slug}:{field}:{segment.get(field)}:{expected_value}"
                )

    notes = manifest.get("segmentation_notes")
    if not isinstance(notes, list):
        return problems + ["tools/lib/bpf/zigux_segments/manifest.json:segmentation_notes:not_a_list"]
    if len(notes) != 1:
        problems.append(
            f"tools/lib/bpf/zigux_segments/manifest.json:segmentation_notes:length:{len(notes)}:1"
        )
        return problems

    note = notes[0]
    if not isinstance(note, dict):
        return problems + ["tools/lib/bpf/zigux_segments/manifest.json:segmentation_notes:entry:not_an_object"]

    destination = note.get("destination")
    if destination != "tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig":
        problems.append(
            "tools/lib/bpf/zigux_segments/manifest.json:"
            f"segmentation_notes:destination:{destination}:tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig"
        )

    for field, expected in (
        ("landed_scope", EXPECTED_BRIDGE_LANDED_SCOPE),
        ("queued_scope", EXPECTED_BRIDGE_QUEUED_SCOPE),
    ):
        actual = note.get(field)
        if actual != expected:
            problems.append(
                "tools/lib/bpf/zigux_segments/manifest.json:"
                f"segmentation_notes:{field}:{actual!r}:{expected!r}"
            )

    if note.get("why_now") != EXPECTED_BRIDGE_WHY_NOW:
        problems.append("tools/lib/bpf/zigux_segments/manifest.json:segmentation_notes:why_now")

    return problems


def validate_legacy_segment_packet(root: Path) -> tuple[list[str], list[str]]:
    missing_markers = collect_missing_markers(root, LEGACY_PACKET_REQUIRED_MARKERS)
    missing_markers.extend(validate_bridge_segmentation_contract(root))
    commit_sync_errors: list[str] = []
    try:
        note_commit = find_required_commit(
            read_text(root, "Documentation/zigux/phase8-libbpf-segment-survey.md"),
            SURVEYED_COMMIT_NOTE_RE,
            "phase8-libbpf-segment-survey.md:missing_or_invalid_surveyed_commit",
        )
        test_commit = find_required_commit(
            read_text(root, "zigux/tests/phase8_libbpf_segments.zig"),
            SURVEYED_COMMIT_TEST_RE,
            "phase8_libbpf_segments.zig:missing_or_invalid_expected_surveyed_commit",
        )
        manifest_commit = find_required_commit(
            read_text(root, "tools/lib/bpf/zigux_segments/manifest.json"),
            SURVEYED_COMMIT_MANIFEST_RE,
            "tools/lib/bpf/zigux_segments/manifest.json:missing_or_invalid_surveyed_commit",
        )
    except ValueError as exc:
        commit_sync_errors.append(str(exc))
    else:
        if note_commit != test_commit or note_commit != manifest_commit:
            commit_sync_errors.extend(
                [
                    f"phase8-libbpf-segment-survey.md:{note_commit}",
                    f"phase8_libbpf_segments.zig:{test_commit}",
                    f"tools/lib/bpf/zigux_segments/manifest.json:{manifest_commit}",
                ]
            )
    return missing_markers, commit_sync_errors


def validate(root: Path) -> tuple[list[str], list[str], list[str], list[str], str]:
    missing_shared_files = collect_missing_files(root, SHARED_REQUIRED_FILES)
    if missing_shared_files:
        return missing_shared_files, [], [], [], "missing_shared_files"

    missing_shared_markers = collect_missing_markers(root, SHARED_REQUIRED_MARKERS)
    if missing_shared_markers:
        return [], missing_shared_markers, [], [], "missing_shared_markers"

    missing_legacy_files = collect_missing_files(root, LEGACY_SEGMENT_PACKET_FILES)
    if not missing_legacy_files:
        legacy_missing_markers, commit_sync_errors = validate_legacy_segment_packet(root)
        return [], [], legacy_missing_markers, commit_sync_errors, "legacy_segment_packet"

    if parked_wording_mode(root):
        parked_surface_drift = collect_present_markers(root, PARKED_DRIFT_MARKERS)
        return [], [], parked_surface_drift, [], "parked_wording_packet"

    return missing_legacy_files, [], [], [], "missing_legacy_files"


def clone_fixture_root(destination_root: Path, include_legacy_packet: bool = True) -> None:
    for rel_path, text in FIXTURE_TEXT.items():
        if not include_legacy_packet and rel_path in LEGACY_SEGMENT_PACKET_FILES:
            continue
        target = destination_root / rel_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")


def expect_validation(
    case: str,
    root: Path,
    expected_files: list[str],
    expected_shared_markers: list[str],
    expected_legacy_markers: list[str],
    expected_commit_sync: list[str],
    expected_mode: str,
) -> None:
    actual = validate(root)
    expected = (
        expected_files,
        expected_shared_markers,
        expected_legacy_markers,
        expected_commit_sync,
        expected_mode,
    )
    assert actual == expected, f"{case}: {actual!r} != {expected!r}"


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase8_libbpf_segment_gate_") as tmp_dir:
        tmp_root = Path(tmp_dir)
        clone_fixture_root(tmp_root)

        expect_validation(
            "legacy_packet_baseline",
            tmp_root,
            [],
            [],
            [],
            [],
            "legacy_segment_packet",
        )

        workflow_path = tmp_root / ".github/workflows/zigux-bootstrap.yml"
        original_workflow = workflow_path.read_text(encoding="utf-8")
        workflow_path.unlink()
        expect_validation(
            "missing_shared_file",
            tmp_root,
            [".github/workflows/zigux-bootstrap.yml"],
            [],
            [],
            [],
            "missing_shared_files",
        )
        workflow_path.write_text(original_workflow, encoding="utf-8")

        lane_note_path = tmp_root / "Documentation/zigux/phase8-tooling-lane-sequencing.md"
        original_lane_note = lane_note_path.read_text(encoding="utf-8")
        lane_note_path.write_text(
            original_lane_note.replace(
                "### 4. Shared wording lane",
                "### 4. Shared wording packet",
                1,
            ),
            encoding="utf-8",
        )
        expect_validation(
            "missing_shared_marker",
            tmp_root,
            [],
            [
                "Documentation/zigux/phase8-tooling-lane-sequencing.md:### 4. Shared wording lane",
            ],
            [],
            [],
            "missing_shared_markers",
        )
        lane_note_path.write_text(original_lane_note, encoding="utf-8")

        manifest_path = tmp_root / "tools/lib/bpf/zigux_segments/manifest.json"
        original_manifest = manifest_path.read_text(encoding="utf-8")
        manifest_path.write_text(
            original_manifest.replace(
                '"surveyed_commit": "0123456789abcdef0123456789abcdef01234567"',
                '"surveyed_commit": "fedcba9876543210fedcba9876543210fedcba98"',
                1,
            ),
            encoding="utf-8",
        )
        expect_validation(
            "legacy_commit_sync_mismatch",
            tmp_root,
            [],
            [],
            [],
            [
                "phase8-libbpf-segment-survey.md:0123456789abcdef0123456789abcdef01234567",
                "phase8_libbpf_segments.zig:0123456789abcdef0123456789abcdef01234567",
                "tools/lib/bpf/zigux_segments/manifest.json:fedcba9876543210fedcba9876543210fedcba98",
            ],
            "legacy_segment_packet",
        )
        manifest_path.write_text(original_manifest, encoding="utf-8")

        bad_bridge_manifest = json.loads(original_manifest)
        bad_bridge_manifest["segmentation_notes"][0]["landed_scope"] = EXPECTED_BRIDGE_LANDED_SCOPE[:-1]
        manifest_path.write_text(json.dumps(bad_bridge_manifest, indent=2) + "\n", encoding="utf-8")
        bridge_errors = validate(tmp_root)[2]
        assert len(bridge_errors) == 1 and "segmentation_notes:landed_scope" in bridge_errors[0], bridge_errors
        manifest_path.write_text(original_manifest, encoding="utf-8")

        bad_segment_manifest = json.loads(original_manifest)
        for segment in bad_segment_manifest["segments"]:
            if segment["slug"] == "map-reuse-compatibility":
                segment["status"] = "ready_next"
                break
        manifest_path.write_text(json.dumps(bad_segment_manifest, indent=2) + "\n", encoding="utf-8")
        bridge_errors = validate(tmp_root)[2]
        assert len(bridge_errors) == 1 and "bridge_segment:map-reuse-compatibility:status" in bridge_errors[0], bridge_errors
        manifest_path.write_text(original_manifest, encoding="utf-8")

        parked_root = tmp_root / "parked"
        clone_fixture_root(parked_root, include_legacy_packet=False)
        expect_validation(
            "parked_packet_with_stale_surfaces",
            parked_root,
            [],
            [],
            [
                ".github/workflows/zigux-bootstrap.yml:Run focused Phase 8 libbpf shard tests",
                ".github/workflows/zigux-bootstrap.yml:make -C zigux phase8-libbpf-segments-test",
                "Documentation/zigux/README.md:Documentation/zigux/phase8-libbpf-segment-survey.md",
                "Documentation/zigux/README.md:tools/lib/bpf/zigux_segments/manifest.json",
                "Documentation/zigux/README.md:zigux/tests/phase8_libbpf_segments_only_build.zig",
                "Documentation/zigux/README.md:zigux/tests/phase8_libbpf_segments.zig",
                "Documentation/zigux/review-checklist.md:Documentation/zigux/phase8-libbpf-segment-survey.md",
                "Documentation/zigux/review-checklist.md:tools/lib/bpf/zigux_segments/manifest.json",
                "Documentation/zigux/review-checklist.md:zigux/tests/phase8_libbpf_segments.zig",
                "Documentation/zigux/review-checklist.md:zigux/tests/phase8_libbpf_segments_only_build.zig",
                "Documentation/zigux/review-checklist.md:make -C zigux phase8-libbpf-segments-test",
                "scripts/zigux/README.md:Documentation/zigux/phase8-libbpf-segment-survey.md",
                "scripts/zigux/README.md:zigux/tests/phase8_libbpf_segments_only_build.zig",
                "scripts/zigux/README.md:make -C zigux phase8-libbpf-segments-test",
                "zigux/tests/README.md:zigux/tests/phase8_libbpf_segments.zig",
                "zigux/tests/README.md:zigux/tests/phase8_libbpf_segments_only_build.zig",
                "zigux/tests/README.md:make -C zigux phase8-libbpf-segments-test",
                "zigux/Makefile:phase8-libbpf-segments-test:",
                "zigux/Makefile:zigux/tests/phase8_libbpf_segments_only_build.zig --summary all",
            ],
            [],
            "parked_wording_packet",
        )

        for rel_path, removals in {
            ".github/workflows/zigux-bootstrap.yml": [
                "- name: Run focused Phase 8 libbpf shard tests\n  run: make -C zigux phase8-libbpf-segments-test\n",
            ],
            "Documentation/zigux/README.md": [
                "- `Documentation/zigux/phase8-libbpf-segment-survey.md`\n",
                "- `tools/lib/bpf/zigux_segments/manifest.json`\n",
                "- `zigux/tests/phase8_libbpf_segments_only_build.zig`\n",
                "- `zigux/tests/phase8_libbpf_segments.zig`\n",
            ],
            "Documentation/zigux/review-checklist.md": [
                "- Documentation/zigux/phase8-libbpf-segment-survey.md\n",
                "- tools/lib/bpf/zigux_segments/manifest.json\n",
                "- zigux/tests/phase8_libbpf_segments.zig\n",
                "- zigux/tests/phase8_libbpf_segments_only_build.zig\n",
                "- make -C zigux phase8-libbpf-segments-test\n",
            ],
            "scripts/zigux/README.md": [
                "- Documentation/zigux/phase8-libbpf-segment-survey.md\n",
                "- zigux/tests/phase8_libbpf_segments_only_build.zig\n",
                "- make -C zigux phase8-libbpf-segments-test\n",
            ],
            "zigux/tests/README.md": [
                "- zigux/tests/phase8_libbpf_segments.zig\n",
                "- zigux/tests/phase8_libbpf_segments_only_build.zig\n",
                "- make -C zigux phase8-libbpf-segments-test\n",
            ],
            "zigux/Makefile": [
                "\nphase8-libbpf-segments-test:\n\tcd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/phase8_libbpf_segments_only_build.zig --summary all\n",
            ],
        }.items():
            path = parked_root / rel_path
            text = path.read_text(encoding="utf-8")
            for removal in removals:
                text = text.replace(removal, "")
            path.write_text(text, encoding="utf-8")

        expect_validation(
            "parked_packet_without_stale_surfaces",
            parked_root,
            [],
            [],
            [],
            [],
            "parked_wording_packet",
        )

    print("PHASE8_LIBBPF_SEGMENT_GATE_SELF_TEST=pass")
    print("PHASE8_LIBBPF_SEGMENT_GATE_SELF_TEST_CASE_COUNT=8")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Validate the Phase 8 libbpf packet when the legacy segment survey exists, "
            "or report stale shared-surface drift when the packet is parked on wording-only surfaces."
        )
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run built-in drift checks against compact synthetic Phase 8 fixture trees.",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    missing_files, missing_shared_markers, legacy_errors, commit_sync_errors, mode = validate(ROOT)
    if missing_files:
        print("PHASE8_LIBBPF_SEGMENT_GATE=fail")
        if mode == "missing_shared_files":
            print("MISSING_PHASE8_LIBBPF_SEGMENT_SHARED_FILES_START")
            for item in missing_files:
                print(item)
            print("MISSING_PHASE8_LIBBPF_SEGMENT_SHARED_FILES_END")
        else:
            print("MISSING_PHASE8_LIBBPF_SEGMENT_LEGACY_FILES_START")
            for item in missing_files:
                print(item)
            print("MISSING_PHASE8_LIBBPF_SEGMENT_LEGACY_FILES_END")
        return 1
    if missing_shared_markers:
        print("PHASE8_LIBBPF_SEGMENT_GATE=fail")
        print("MISSING_PHASE8_LIBBPF_SEGMENT_SHARED_MARKERS_START")
        for marker in missing_shared_markers:
            print(marker)
        print("MISSING_PHASE8_LIBBPF_SEGMENT_SHARED_MARKERS_END")
        return 1
    if legacy_errors:
        print("PHASE8_LIBBPF_SEGMENT_GATE=fail")
        if mode == "parked_wording_packet":
            print("STALE_PHASE8_LIBBPF_PARKED_SURFACES_START")
            for item in legacy_errors:
                print(item)
            print("STALE_PHASE8_LIBBPF_PARKED_SURFACES_END")
        else:
            print("MISSING_PHASE8_LIBBPF_SEGMENT_MARKERS_START")
            for marker in legacy_errors:
                print(marker)
            print("MISSING_PHASE8_LIBBPF_SEGMENT_MARKERS_END")
        return 1
    if commit_sync_errors:
        print("PHASE8_LIBBPF_SEGMENT_GATE=fail")
        print("MISMATCHED_PHASE8_LIBBPF_SEGMENT_COMMIT_SYNC_START")
        for item in commit_sync_errors:
            print(item)
        print("MISMATCHED_PHASE8_LIBBPF_SEGMENT_COMMIT_SYNC_END")
        return 1

    print("PHASE8_LIBBPF_SEGMENT_GATE=pass")
    print(f"PHASE8_LIBBPF_SEGMENT_GATE_MODE={mode}")
    print(f"PHASE8_LIBBPF_SEGMENT_GATE_SHARED_FILE_COUNT={len(SHARED_REQUIRED_FILES)}")
    if mode == "legacy_segment_packet":
        print(f"PHASE8_LIBBPF_SEGMENT_GATE_REQUIRED_MARKER_COUNT={required_marker_count()}")
    else:
        print("PHASE8_LIBBPF_SEGMENT_GATE_REQUIRED_MARKER_COUNT=parked-wording-lane")
    return 0


if __name__ == "__main__":
    sys.exit(main())
