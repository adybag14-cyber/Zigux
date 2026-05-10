#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from pathlib import Path
import sys
import tempfile


SCRIPT_PATH = Path(__file__).resolve()
ROOT = SCRIPT_PATH.parents[2] if len(SCRIPT_PATH.parents) > 2 else SCRIPT_PATH.parent

REQUIRED_FILES = [
    ".github/workflows/zigux-bootstrap.yml",
    "Documentation/zigux/README.md",
    "Documentation/zigux/phase8-libbpf-segment-survey.md",
    "Documentation/zigux/phase8-tooling-lane-sequencing.md",
    "Documentation/zigux/review-checklist.md",
    "scripts/zigux/README.md",
    "zigux/Makefile",
    "zigux/tests/README.md",
    "zigux/tests/phase8_libbpf_segments.zig",
    "zigux/tests/phase8_libbpf_segments_only_build.zig",
    "tools/lib/bpf/zigux_segments/manifest.json",
]

REQUIRED_MARKERS = {
    ".github/workflows/zigux-bootstrap.yml": [
        "Validate Phase 8 tooling packet",
        "make -C zigux phase8-validate",
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
        "Documentation/zigux/phase8-libbpf-segment-survey.md",
        "zigux/tests/phase8_libbpf_segments.zig",
        "zigux/tests/phase8_libbpf_segments_only_build.zig",
        "make -C zigux phase8-libbpf-segments-test",
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
        "Documentation/zigux/phase8-tooling-lane-sequencing.md",
        "zigux/tests/phase8_libbpf_segments_only_build.zig",
        "make -C zigux phase8-libbpf-segments-test",
    ],
    "zigux/Makefile": [
        "phase8-validate:",
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
    ],
}

SURVEYED_COMMIT_NOTE_RE = re.compile(
    r"survey checkpoint: refreshed against inspected `master` head `([0-9a-f]{40})`"
)
SURVEYED_COMMIT_TEST_RE = re.compile(
    r'const current_surveyed_commit = "([0-9a-f]{40})";'
)
SURVEYED_COMMIT_MANIFEST_RE = re.compile(
    r'"surveyed_commit"\s*:\s*"([0-9a-f]{40})"'
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

- survey checkpoint: refreshed against inspected `master` head `0123456789abcdef0123456789abcdef01234567`
- tools/lib/bpf/zigux_segments/manifest.json
- zigux/tests/phase8_libbpf_segments.zig
- zigux/tests/phase8_libbpf_segments_only_build.zig
- make -C zigux phase8-libbpf-segments-test
""",
    "Documentation/zigux/phase8-tooling-lane-sequencing.md": """# Phase 8 Tooling Lane Sequencing

- Documentation/zigux/phase8-libbpf-segment-survey.md
- zigux/tests/phase8_libbpf_segments.zig
- zigux/tests/phase8_libbpf_segments_only_build.zig
- make -C zigux phase8-libbpf-segments-test
""",
    "Documentation/zigux/review-checklist.md": """# Zigux Review Checklist

- Documentation/zigux/phase8-libbpf-segment-survey.md
- tools/lib/bpf/zigux_segments/manifest.json
- zigux/tests/phase8_libbpf_segments.zig
- zigux/tests/phase8_libbpf_segments_only_build.zig
- make -C zigux phase8-libbpf-segments-test
""",
    "scripts/zigux/README.md": """# scripts/zigux

- Documentation/zigux/phase8-libbpf-segment-survey.md
- Documentation/zigux/phase8-tooling-lane-sequencing.md
- zigux/tests/phase8_libbpf_segments_only_build.zig
- make -C zigux phase8-libbpf-segments-test
""",
    "zigux/Makefile": """phase8-validate:
\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase8.py

phase8-libbpf-segments-test:
\tcd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/phase8_libbpf_segments_only_build.zig --summary all
""",
    "zigux/tests/README.md": """# zigux/tests

- zigux/tests/phase8_libbpf_segments.zig
- zigux/tests/phase8_libbpf_segments_only_build.zig
- make -C zigux phase8-libbpf-segments-test
""",
    "zigux/tests/phase8_libbpf_segments.zig": """const current_surveyed_commit = \"0123456789abcdef0123456789abcdef01234567\";
""",
    "zigux/tests/phase8_libbpf_segments_only_build.zig": """const root_module = b.createModule(.{
    .root_source_file = b.path(\"phase8_libbpf_segments.zig\"),
});
""",
    "tools/lib/bpf/zigux_segments/manifest.json": """{
  \"surveyed_commit\": \"0123456789abcdef0123456789abcdef01234567\",
  \"segments\": []
}
""",
}


def read_text(root: Path, rel_path: str) -> str:
    return (root / rel_path).read_text(encoding="utf-8")


def collect_missing_files(root: Path) -> list[str]:
    return [rel_path for rel_path in REQUIRED_FILES if not (root / rel_path).exists()]


def required_marker_count() -> int:
    return sum(len(markers) for markers in REQUIRED_MARKERS.values())


def find_required_commit(text: str, pattern: re.Pattern[str], label: str) -> str:
    match = pattern.search(text)
    if match is None:
        raise ValueError(label)
    return match.group(1)


def validate(root: Path) -> tuple[list[str], list[str], list[str]]:
    missing_files = collect_missing_files(root)
    if missing_files:
        return missing_files, [], []

    missing_markers: list[str] = []
    for rel_path, markers in REQUIRED_MARKERS.items():
        text = read_text(root, rel_path)
        for marker in markers:
            if marker not in text:
                missing_markers.append(f"{rel_path}:{marker}")

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
            "phase8_libbpf_segments.zig:missing_or_invalid_current_surveyed_commit",
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

    return [], missing_markers, commit_sync_errors


def clone_fixture_root(destination_root: Path) -> None:
    for rel_path, text in FIXTURE_TEXT.items():
        target = destination_root / rel_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")


def expect_missing_marker(label: str, root: Path, expected_marker: str) -> None:
    missing_files, missing_markers, commit_sync_errors = validate(root)
    if missing_files:
        raise SystemExit(
            f"phase8-libbpf-segment-gate-self-test:{label}:unexpected_missing_files:{','.join(missing_files)}"
        )
    if commit_sync_errors:
        raise SystemExit(
            f"phase8-libbpf-segment-gate-self-test:{label}:unexpected_commit_sync:{','.join(commit_sync_errors)}"
        )
    if expected_marker not in missing_markers:
        actual = ",".join(missing_markers) if missing_markers else "none"
        raise SystemExit(
            f"phase8-libbpf-segment-gate-self-test:{label}:expected_missing_marker:{expected_marker}:actual:{actual}"
        )


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase8_libbpf_segment_gate_") as tmp_dir:
        tmp_root = Path(tmp_dir)
        clone_fixture_root(tmp_root)

        missing_files, missing_markers, commit_sync_errors = validate(tmp_root)
        if missing_files or missing_markers or commit_sync_errors:
            raise SystemExit(
                "phase8-libbpf-segment-gate-self-test:baseline_failed:"
                f"files={','.join(missing_files) if missing_files else 'none'}:"
                f"markers={','.join(missing_markers) if missing_markers else 'none'}:"
                f"commit_sync={','.join(commit_sync_errors) if commit_sync_errors else 'none'}"
            )

        workflow_path = tmp_root / ".github/workflows/zigux-bootstrap.yml"
        original_workflow = workflow_path.read_text(encoding="utf-8")
        workflow_path.write_text(
            original_workflow.replace(
                "make -C zigux phase8-libbpf-segments-test",
                "make -C zigux phase8-libbpf-test",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "workflow_route",
            tmp_root,
            ".github/workflows/zigux-bootstrap.yml:make -C zigux phase8-libbpf-segments-test",
        )
        workflow_path.write_text(original_workflow, encoding="utf-8")

        review_path = tmp_root / "Documentation/zigux/review-checklist.md"
        original_review = review_path.read_text(encoding="utf-8")
        review_path.write_text(
            original_review.replace(
                "tools/lib/bpf/zigux_segments/manifest.json",
                "tools/lib/bpf/zigux_segments/segments.json",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "review_manifest",
            tmp_root,
            "Documentation/zigux/review-checklist.md:tools/lib/bpf/zigux_segments/manifest.json",
        )
        review_path.write_text(original_review, encoding="utf-8")

        scripts_readme_path = tmp_root / "scripts/zigux/README.md"
        original_scripts_readme = scripts_readme_path.read_text(encoding="utf-8")
        scripts_readme_path.write_text(
            original_scripts_readme.replace(
                "Documentation/zigux/phase8-tooling-lane-sequencing.md",
                "Documentation/zigux/phase8-tooling-sequencing.md",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "scripts_lane_note",
            tmp_root,
            "scripts/zigux/README.md:Documentation/zigux/phase8-tooling-lane-sequencing.md",
        )
        scripts_readme_path.write_text(original_scripts_readme, encoding="utf-8")

        tests_readme_path = tmp_root / "zigux/tests/README.md"
        original_tests_readme = tests_readme_path.read_text(encoding="utf-8")
        tests_readme_path.write_text(
            original_tests_readme.replace(
                "zigux/tests/phase8_libbpf_segments_only_build.zig",
                "zigux/tests/phase8_libbpf_segment_build.zig",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "tests_focused_build",
            tmp_root,
            "zigux/tests/README.md:zigux/tests/phase8_libbpf_segments_only_build.zig",
        )
        tests_readme_path.write_text(original_tests_readme, encoding="utf-8")

        build_path = tmp_root / "zigux/tests/phase8_libbpf_segments_only_build.zig"
        original_build = build_path.read_text(encoding="utf-8")
        build_path.write_text(
            original_build.replace(
                "phase8_libbpf_segments.zig",
                "phase8_segments.zig",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "focused_root_module",
            tmp_root,
            "zigux/tests/phase8_libbpf_segments_only_build.zig:phase8_libbpf_segments.zig",
        )
        build_path.write_text(original_build, encoding="utf-8")

        survey_path = tmp_root / "Documentation/zigux/phase8-libbpf-segment-survey.md"
        original_survey = survey_path.read_text(encoding="utf-8")
        survey_path.write_text(
            original_survey.replace(
                "make -C zigux phase8-libbpf-segments-test",
                "make -C zigux phase8-libbpf-test",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "survey_make_route",
            tmp_root,
            "Documentation/zigux/phase8-libbpf-segment-survey.md:make -C zigux phase8-libbpf-segments-test",
        )
        survey_path.write_text(original_survey, encoding="utf-8")

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
        missing_files, missing_markers, commit_sync_errors = validate(tmp_root)
        if missing_files or missing_markers:
            raise SystemExit(
                "phase8-libbpf-segment-gate-self-test:commit_sync_mismatch:unexpected_file_or_marker_failure:"
                f"files={','.join(missing_files) if missing_files else 'none'}:"
                f"markers={','.join(missing_markers) if missing_markers else 'none'}"
            )
        if "tools/lib/bpf/zigux_segments/manifest.json:" not in ",".join(commit_sync_errors):
            actual = ",".join(commit_sync_errors) if commit_sync_errors else "none"
            raise SystemExit(
                "phase8-libbpf-segment-gate-self-test:commit_sync_mismatch:"
                f"expected_manifest_mismatch:actual:{actual}"
            )

    print("PHASE8_LIBBPF_SEGMENT_GATE_SELF_TEST=pass")
    print("PHASE8_LIBBPF_SEGMENT_GATE_SELF_TEST_CASE_COUNT=6")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the focused Phase 8 libbpf segment survey packet across its shared reminder surfaces."
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run built-in drift checks against a compact synthetic Phase 8 fixture tree.",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    missing_files, missing_markers, commit_sync_errors = validate(ROOT)
    if missing_files:
        print("PHASE8_LIBBPF_SEGMENT_GATE=fail")
        print("MISSING_PHASE8_LIBBPF_SEGMENT_GATE_FILES_START")
        for item in missing_files:
            print(item)
        print("MISSING_PHASE8_LIBBPF_SEGMENT_GATE_FILES_END")
        return 1
    if missing_markers:
        print("PHASE8_LIBBPF_SEGMENT_GATE=fail")
        print("MISSING_PHASE8_LIBBPF_SEGMENT_GATE_MARKERS_START")
        for marker in missing_markers:
            print(marker)
        print("MISSING_PHASE8_LIBBPF_SEGMENT_GATE_MARKERS_END")
        return 1
    if commit_sync_errors:
        print("PHASE8_LIBBPF_SEGMENT_GATE=fail")
        print("MISMATCHED_PHASE8_LIBBPF_SEGMENT_COMMIT_SYNC_START")
        for item in commit_sync_errors:
            print(item)
        print("MISMATCHED_PHASE8_LIBBPF_SEGMENT_COMMIT_SYNC_END")
        return 1

    print("PHASE8_LIBBPF_SEGMENT_GATE=pass")
    print(f"PHASE8_LIBBPF_SEGMENT_GATE_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(f"PHASE8_LIBBPF_SEGMENT_GATE_REQUIRED_MARKER_COUNT={required_marker_count()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
