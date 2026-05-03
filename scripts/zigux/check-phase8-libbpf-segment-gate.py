#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from pathlib import Path
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[2]

REQUIRED_FILES = [
    ".github/workflows/zigux-bootstrap.yml",
    "Documentation/zigux/README.md",
    "Documentation/zigux/phase8-libbpf-segment-survey.md",
    "scripts/zigux/README.md",
    "scripts/zigux/check-phase8-libbpf-segment-gate.py",
    "zigux/Makefile",
    "zigux/tests/README.md",
    "zigux/tests/phase8_libbpf_segments.zig",
    "zigux/tests/phase8_libbpf_segments_only_build.zig",
    "tools/lib/bpf/zigux_segments/manifest.json",
]

REQUIRED_MARKERS = {
    ".github/workflows/zigux-bootstrap.yml": [
        "Validate Phase 8 tooling gates",
        "make -C zigux phase8-validate",
        "Run focused Phase 8 libbpf segment survey tests",
        "zigux/tests/phase8_libbpf_segments_only_build.zig",
    ],
    "Documentation/zigux/README.md": [
        "Documentation/zigux/phase8-libbpf-segment-survey.md",
        "scripts/zigux/check-phase8-libbpf-segment-gate.py",
        "tools/lib/bpf/zigux_segments/manifest.json",
        "make -C zigux phase8-libbpf-segments-test",
        "zigux/tests/phase8_libbpf_segments_only_build.zig",
    ],
    "Documentation/zigux/phase8-libbpf-segment-survey.md": [
        "The manifest currently records eleven bounded segments.",
        "tools/lib/bpf/zigux_segments/manifest.json",
        "scripts/zigux/check-phase8-libbpf-segment-gate.py",
        "make -C zigux phase8-libbpf-segments-test",
        "zigux/tests/phase8_libbpf_segments_only_build.zig",
        "six landed helper-first starter slices",
    ],
    "scripts/zigux/README.md": [
        "check-phase8-libbpf-segment-gate.py",
        "Documentation/zigux/phase8-libbpf-segment-survey.md",
        "tools/lib/bpf/zigux_segments/manifest.json",
        "make -C zigux phase8-libbpf-segments-test",
        "zigux/tests/phase8_libbpf_segments_only_build.zig",
    ],
    "scripts/zigux/check-phase8-libbpf-segment-gate.py": [
        "PHASE8_LIBBPF_SEGMENT_GATE=pass",
        "PHASE8_LIBBPF_SEGMENT_GATE_SELF_TEST=pass",
        "Run focused Phase 8 libbpf segment survey tests",
        "phase8-libbpf-segment-tests",
        "survey checkpoint: refreshed against inspected `master` head `",
    ],
    "zigux/Makefile": [
        "phase8-validate:",
        "scripts/zigux/check-phase8-libbpf-segment-gate.py --self-test",
        "scripts/zigux/check-phase8-libbpf-segment-gate.py",
        "phase8-libbpf-segments-test:",
        "zigux/tests/phase8_libbpf_segments_only_build.zig --summary all",
    ],
    "zigux/tests/README.md": [
        "zigux/tests/phase8_libbpf_segments_only_build.zig",
        "zigux/tests/phase8_libbpf_segments.zig",
        "make -C zigux phase8-libbpf-segments-test",
        "scripts/zigux/check-phase8-libbpf-segment-gate.py",
    ],
    "zigux/tests/phase8_libbpf_segments.zig": [
        "const current_surveyed_commit = ",
        "The manifest currently records eleven bounded segments",
        "phase8_libbpf_segments_only_build.zig",
        "survey checkpoint: refreshed against inspected `master` head `",
    ],
    "zigux/tests/phase8_libbpf_segments_only_build.zig": [
        "phase8_libbpf_segments.zig",
        "phase8-libbpf-segment-tests",
        "Run focused Phase 8 libbpf segment survey tests",
    ],
    "tools/lib/bpf/zigux_segments/manifest.json": [
        "\"lane_key\": \"P8-L15\"",
        "\"surveyed_commit\": ",
        "\"segments\": [",
        "\"logging-version-and-errno\"",
        "\"map-reuse-compatibility\"",
    ],
}


FIXTURE_TEXT = {
    ".github/workflows/zigux-bootstrap.yml": """name: zigux-bootstrap

- name: Validate Phase 8 tooling gates
  run: make -C zigux phase8-validate

- name: Run focused Phase 8 libbpf segment survey tests
  run: zig build test --build-file zigux/tests/phase8_libbpf_segments_only_build.zig --summary all
""",
    "Documentation/zigux/README.md": """# Zigux Documentation

- `Documentation/zigux/phase8-libbpf-segment-survey.md`
- `scripts/zigux/check-phase8-libbpf-segment-gate.py`
- `tools/lib/bpf/zigux_segments/manifest.json`
- `make -C zigux phase8-libbpf-segments-test`
- `zigux/tests/phase8_libbpf_segments_only_build.zig`
""",
    "Documentation/zigux/phase8-libbpf-segment-survey.md": """# Phase 8 Libbpf Segment Survey

- survey checkpoint: refreshed against inspected `master` head `0123456789abcdef0123456789abcdef01234567`
- The manifest currently records eleven bounded segments.
- tools/lib/bpf/zigux_segments/manifest.json
- scripts/zigux/check-phase8-libbpf-segment-gate.py
- make -C zigux phase8-libbpf-segments-test
- zigux/tests/phase8_libbpf_segments_only_build.zig
- six landed helper-first starter slices
""",
    "scripts/zigux/README.md": """# scripts/zigux

- check-phase8-libbpf-segment-gate.py
- Documentation/zigux/phase8-libbpf-segment-survey.md
- tools/lib/bpf/zigux_segments/manifest.json
- make -C zigux phase8-libbpf-segments-test
- zigux/tests/phase8_libbpf_segments_only_build.zig
""",
    "zigux/Makefile": """phase8-validate:
\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase8-libbpf-segment-gate.py --self-test
\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase8-libbpf-segment-gate.py

phase8-libbpf-segments-test:
\tcd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/phase8_libbpf_segments_only_build.zig --summary all
""",
    "zigux/tests/README.md": """# zigux/tests

- zigux/tests/phase8_libbpf_segments_only_build.zig
- zigux/tests/phase8_libbpf_segments.zig
- make -C zigux phase8-libbpf-segments-test
- scripts/zigux/check-phase8-libbpf-segment-gate.py
""",
    "zigux/tests/phase8_libbpf_segments.zig": """const current_surveyed_commit = \"0123456789abcdef0123456789abcdef01234567\";

test \"phase 8 libbpf survey stays wired\" {
    _ = \"The manifest currently records eleven bounded segments\";
    _ = \"phase8_libbpf_segments_only_build.zig\";
    _ = \"survey checkpoint: refreshed against inspected `master` head `0123456789abcdef0123456789abcdef01234567`\";
}
""",
    "zigux/tests/phase8_libbpf_segments_only_build.zig": """const root_module = b.createModule(.{
    .root_source_file = b.path(\"phase8_libbpf_segments.zig\"),
});
const libbpf_segments_tests = b.addTest(.{
    .name = \"phase8-libbpf-segment-tests\",
});
const test_step = b.step(\"test\", \"Run focused Phase 8 libbpf segment survey tests\");
""",
    "tools/lib/bpf/zigux_segments/manifest.json": """{
  \"lane_key\": \"P8-L15\",
  \"surveyed_commit\": \"0123456789abcdef0123456789abcdef01234567\",
  \"segments\": [
    {\"slug\": \"logging-version-and-errno\"},
    {\"slug\": \"map-reuse-compatibility\"}
  ]
}
""",
}


def read_text(root: Path, rel_path: str) -> str:
    return (root / rel_path).read_text(encoding="utf-8")


def collect_missing_files(root: Path) -> list[str]:
    return [rel_path for rel_path in REQUIRED_FILES if not (root / rel_path).exists()]


def required_marker_count() -> int:
    return sum(len(markers) for markers in REQUIRED_MARKERS.values())


def require_match(pattern: str, text: str, label: str) -> str:
    match = re.search(pattern, text, re.MULTILINE)
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
        surveyed_commit_from_note = require_match(
            r"survey checkpoint: refreshed against inspected `master` head `([0-9a-f]{40})`",
            read_text(root, "Documentation/zigux/phase8-libbpf-segment-survey.md"),
            "survey_note:missing_or_invalid_surveyed_commit",
        )
        surveyed_commit_from_test = require_match(
            r'const current_surveyed_commit = "([0-9a-f]{40})";',
            read_text(root, "zigux/tests/phase8_libbpf_segments.zig"),
            "phase8_libbpf_segments_test:missing_or_invalid_current_surveyed_commit",
        )
        surveyed_commit_from_manifest = require_match(
            r'"surveyed_commit"\s*:\s*"([0-9a-f]{40})"',
            read_text(root, "tools/lib/bpf/zigux_segments/manifest.json"),
            "manifest:missing_or_invalid_surveyed_commit",
        )
    except ValueError as exc:
        commit_sync_errors.append(str(exc))
    else:
        if (
            surveyed_commit_from_note != surveyed_commit_from_test
            or surveyed_commit_from_note != surveyed_commit_from_manifest
        ):
            commit_sync_errors.extend(
                [
                    f"survey_note:{surveyed_commit_from_note}",
                    f"phase8_libbpf_segments_test:{surveyed_commit_from_test}",
                    f"manifest:{surveyed_commit_from_manifest}",
                ]
            )

    return [], missing_markers, commit_sync_errors


def clone_fixture_root(destination_root: Path) -> None:
    for rel_path, text in FIXTURE_TEXT.items():
        target = destination_root / rel_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")

    checker_path = destination_root / "scripts/zigux/check-phase8-libbpf-segment-gate.py"
    checker_path.write_text(Path(__file__).read_text(encoding="utf-8"), encoding="utf-8")


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

        docs_readme_path = tmp_root / "Documentation/zigux/README.md"
        original_docs_readme = docs_readme_path.read_text(encoding="utf-8")
        docs_readme_path.write_text(
            original_docs_readme.replace(
                "make -C zigux phase8-libbpf-segments-test",
                "make -C zigux phase8-libbpf-test",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "docs_readme_make_target",
            tmp_root,
            "Documentation/zigux/README.md:make -C zigux phase8-libbpf-segments-test",
        )
        docs_readme_path.write_text(original_docs_readme, encoding="utf-8")

        survey_path = tmp_root / "Documentation/zigux/phase8-libbpf-segment-survey.md"
        original_survey = survey_path.read_text(encoding="utf-8")
        survey_path.write_text(
            original_survey.replace(
                "The manifest currently records eleven bounded segments.",
                "The manifest currently records ten bounded segments.",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "survey_segment_count",
            tmp_root,
            "Documentation/zigux/phase8-libbpf-segment-survey.md:The manifest currently records eleven bounded segments.",
        )
        survey_path.write_text(original_survey, encoding="utf-8")

        scripts_readme_path = tmp_root / "scripts/zigux/README.md"
        original_scripts_readme = scripts_readme_path.read_text(encoding="utf-8")
        scripts_readme_path.write_text(
            original_scripts_readme.replace(
                "check-phase8-libbpf-segment-gate.py",
                "check-phase8-libbpf-gate.py",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "scripts_readme_checker_name",
            tmp_root,
            "scripts/zigux/README.md:check-phase8-libbpf-segment-gate.py",
        )
        scripts_readme_path.write_text(original_scripts_readme, encoding="utf-8")

        makefile_path = tmp_root / "zigux/Makefile"
        original_makefile = makefile_path.read_text(encoding="utf-8")
        makefile_path.write_text(
            original_makefile.replace(
                "scripts/zigux/check-phase8-libbpf-segment-gate.py --self-test",
                "scripts/zigux/check-phase8-libbpf-segment-self.py --self-test",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "makefile_self_test_hook",
            tmp_root,
            "zigux/Makefile:scripts/zigux/check-phase8-libbpf-segment-gate.py --self-test",
        )
        makefile_path.write_text(original_makefile, encoding="utf-8")

        workflow_path = tmp_root / ".github/workflows/zigux-bootstrap.yml"
        original_workflow = workflow_path.read_text(encoding="utf-8")
        workflow_path.write_text(
            original_workflow.replace(
                "Run focused Phase 8 libbpf segment survey tests",
                "Run focused Phase 8 libbpf survey tests",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "workflow_step_name",
            tmp_root,
            ".github/workflows/zigux-bootstrap.yml:Run focused Phase 8 libbpf segment survey tests",
        )
        workflow_path.write_text(original_workflow, encoding="utf-8")

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
            "tests_readme_focused_build",
            tmp_root,
            "zigux/tests/README.md:zigux/tests/phase8_libbpf_segments_only_build.zig",
        )
        tests_readme_path.write_text(original_tests_readme, encoding="utf-8")

        focused_build_path = tmp_root / "zigux/tests/phase8_libbpf_segments_only_build.zig"
        original_focused_build = focused_build_path.read_text(encoding="utf-8")
        focused_build_path.write_text(
            original_focused_build.replace(
                "phase8-libbpf-segment-tests",
                "phase8-libbpf-tests",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "focused_build_artifact_name",
            tmp_root,
            "zigux/tests/phase8_libbpf_segments_only_build.zig:phase8-libbpf-segment-tests",
        )
        focused_build_path.write_text(original_focused_build, encoding="utf-8")

        manifest_path = tmp_root / "tools/lib/bpf/zigux_segments/manifest.json"
        original_manifest = manifest_path.read_text(encoding="utf-8")
        manifest_path.write_text(
            original_manifest.replace(
                '"map-reuse-compatibility"',
                '"map-reuse-boundary"',
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "manifest_slug",
            tmp_root,
            'tools/lib/bpf/zigux_segments/manifest.json:"map-reuse-compatibility"',
        )
        manifest_path.write_text(original_manifest, encoding="utf-8")

        libbpf_segments_test_path = tmp_root / "zigux/tests/phase8_libbpf_segments.zig"
        original_libbpf_segments_test = libbpf_segments_test_path.read_text(encoding="utf-8")
        libbpf_segments_test_path.write_text(
            original_libbpf_segments_test.replace(
                "0123456789abcdef0123456789abcdef01234567",
                "fedcba9876543210fedcba9876543210fedcba98",
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
        if "phase8_libbpf_segments_test:" not in ",".join(commit_sync_errors):
            actual = ",".join(commit_sync_errors) if commit_sync_errors else "none"
            raise SystemExit(
                "phase8-libbpf-segment-gate-self-test:commit_sync_mismatch:"
                f"expected_phase8_libbpf_segments_test_marker:actual:{actual}"
            )

    print("PHASE8_LIBBPF_SEGMENT_GATE_SELF_TEST=pass")
    print("PHASE8_LIBBPF_SEGMENT_GATE_SELF_TEST_CASE_COUNT=8")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate that the focused Phase 8 libbpf segment survey shard stays wired into the shared review packet."
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
        if len(commit_sync_errors) == 1 and ":missing_or_invalid_" in commit_sync_errors[0]:
            print("MISSING_PHASE8_LIBBPF_SEGMENT_COMMIT_SYNC_START")
            print(commit_sync_errors[0])
            print("MISSING_PHASE8_LIBBPF_SEGMENT_COMMIT_SYNC_END")
        else:
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
