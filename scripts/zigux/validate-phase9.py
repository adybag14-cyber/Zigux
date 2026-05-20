#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[2]

REQUIRED_FILES = [
    "Documentation/zigux/freeze-map.md",
    "scripts/zigux/validate-phase9.py",
    "scripts/zigux/README.md",
    "scripts/zigux/check-phase9-module-metadata-packet.py",
    "Documentation/zigux/README.md",
    "Documentation/zigux/review-checklist.md",
    "Documentation/zigux/phase9-runtime-loader-gap-survey.md",
    "Documentation/zigux/phase9-runtime-trace-events-survey.md",
    "Documentation/zigux/phase9-runtime-trace-events-module-slice.md",
    "Documentation/zigux/phase9-module-metadata-depmod-bridge-survey.md",
    "zigux/Makefile",
    "zigux/tests/README.md",
    "zigux/tests/phase9_build.zig",
    "zigux/tests/runtime_loader_gap_manifest.json",
    "zigux/tests/runtime_loader_gap_survey.zig",
    "zigux/tests/runtime_trace_events_manifest.json",
    "zigux/tests/runtime_trace_events_survey.zig",
    "zigux/tests/runtime_module_metadata_manifest.json",
    "zigux/tests/runtime_module_metadata_survey.zig",
    ".github/workflows/zigux-bootstrap.yml",
]

REQUIRED_MAKE_MARKERS = [
    "PHONY += phase9-validate phase9-test phase9",
    "phase9-validate:",
    "scripts/zigux/validate-phase9.py",
    "phase9-test:",
    "zigux/tests/phase9_build.zig",
    "phase9: phase9-validate phase9-test",
]

REQUIRED_WORKFLOW_MARKERS = [
    "Validate Phase 9 runtime gates",
    "make -C zigux phase9-validate",
    "Run Phase 9 runtime helper tests",
    "zigux/tests/phase9_build.zig",
]

REQUIRED_SCRIPT_README_MARKERS = [
    "validate-phase9.py",
    "Phase 9 flow",
    "make -C zigux phase9-validate",
    "phase9_build.zig",
    "phase9-runtime-loader-gap-survey.md",
    "phase9-module-metadata-depmod-bridge-survey.md",
    "check-phase9-module-metadata-packet.py",
    "review-checklist.md",
    "manifest-backed catalog and ownership map",
]

REQUIRED_TESTS_README_MARKERS = [
    "zigux/tests/phase9_build.zig",
    "zigux/tests/runtime_loader_gap_survey.zig",
    "zigux/tests/runtime_loader_gap_manifest.json",
    "zigux/tests/runtime_module_metadata_manifest.json",
    "zigux/tests/runtime_module_metadata_survey.zig",
    "scripts/zigux/check-phase9-module-metadata-packet.py",
    "scripts/zigux/validate-phase9.py",
    "manifest-backed catalog and ownership map",
]

REQUIRED_DOC_README_MARKERS = [
    "Phase 9 notes",
    "Documentation/zigux/phase9-runtime-loader-gap-survey.md",
    "Documentation/zigux/review-checklist.md",
    "the `Documentation/zigux/phase9-runtime-trace-events-{survey,module-slice}.md`, `zigux/tests/runtime_trace_events_manifest.json`, and `zigux/tests/runtime_trace_events_survey.zig` bundle now keeps the `Documentation/zigux/freeze-map.md` boundary explicit",
    "python3 scripts/zigux/validate-phase9.py",
    "make -C zigux phase9-validate",
    "zigux/tests/phase9_build.zig",
    "manifest-backed catalog and ownership map",
]

REQUIRED_FREEZE_MAP_MARKERS = [
    "## Study / Boundary Only",
    "`kernel/trace/ring_buffer.c`",
    "Architecture Council decision",
]

REQUIRED_REVIEW_CHECKLIST_MARKERS = [
    "if the change is a Phase 9 runtime slice, do the module or sample note, the manifest-backed survey or loader-gap survey, and the shared `phase9_build.zig` entrypoint still agree on the same Linux anchor, bounded blocker posture, and replay scope?",
    "if the change touches the shared Phase 9 runtime-loader evidence packet, does the manifest-backed catalog and ownership map still keep the survey note, review checklist, shared request contract, sample-side loader plans, and shared `phase9_build.zig` entrypoint in one reviewable ownership packet?",
    "if the change touches the shared Phase 9 runtime-loader handoff, are allocator ownership, `requires_runtime_substrate`, handoff stage, and the still-blocked command-name, argv-policy, or environment-derived activation controls explicit rather than implied?",
    "if a Phase 9 runtime trace-events change touches the frozen trace-core boundary, do `Documentation/zigux/freeze-map.md`, the trace-events docs, `zigux/tests/runtime_trace_events_manifest.json`, and `zigux/tests/runtime_trace_events_survey.zig` still keep `kernel/trace/ring_buffer.c` as `Study / Boundary Only` and require an Architecture Council decision before any status change?",
    "does the change avoid hidden runtime services, implicit allocation, or unclear panic behavior?",
    "if unsafe code exists, is it narrow, visible, and review-owned?",
]

REQUIRED_LOADER_GAP_SURVEY_MARKERS = [
    "Documentation/zigux/review-checklist.md",
    "zigux/tests/runtime_loader_gap_manifest.json",
    "zigux/tests/runtime_loader_gap_survey.zig",
    "zigux/tests/phase9_build.zig",
    "zigux/kernel/runtime_loader.zig",
    "Delivery ownership map",
    "manifest-backed catalog",
    "bitmap loader-plan projection",
    "kretprobe loader-plan projection",
    "Phase 8",
    "Phase 9",
    "command or environment control surface",
    "allocator-handoff contract",
    "pre-execution",
]

REQUIRED_PHASE9_BUILD_MARKERS = [
    "runtime_loader_gap_survey.zig",
    "phase9-runtime-loader-gap-survey-tests",
    "phase9-runtime-loader-tests",
    "phase9-runtime-bitmap-loader-tests",
    "phase9-runtime-kretprobe-loader-tests",
]

REQUIRED_LOADER_GAP_SURVEY_TEST_MARKERS = [
    "runtime loader gap survey manifest keeps the roadmap boundary and shared request surface explicit",
    "runtime loader gap survey doc keeps the mixed roadmap phases and remaining control-surface gap explicit",
    "runtime loader gap survey keeps the review checklist runtime guardrails explicit",
    "Documentation/zigux/review-checklist.md",
    "zigux/tests/runtime_loader_gap_manifest.json",
]

REQUIRED_LOADER_GAP_MANIFEST_MARKERS = [
    '"delivery_evidence_catalog": [',
    '"id": "runtime-loader-gap-manifest"',
    '"path": "zigux/kernel/runtime_loader.zig"',
    '"ownership_map": [',
    '"surface": "zigux/tests/runtime_loader_gap_manifest.json"',
    '"surface": "samples/zigux/runtime_bitmap_loader.zig"',
    '"id": "runtime-loader-review-checklist"',
    '"zigux_destination": "Documentation/zigux/review-checklist.md"',
    '"id": "runtime-loader-gap-survey-gate"',
    '"zigux_destination": "zigux/tests/runtime_loader_gap_survey.zig"',
    '"id": "phase9-build-gate"',
    '"zigux_destination": "zigux/tests/phase9_build.zig"',
]

REQUIRED_TRACE_EVENTS_SURVEY_MARKERS = [
    "Documentation/zigux/freeze-map.md",
    "`kernel/trace/ring_buffer.c`",
    "Study / Boundary Only",
    "runtime task ownership",
    "polling and event-loop substrate",
    "ring-buffer parity",
    "Architecture Council",
]

REQUIRED_TRACE_EVENTS_MODULE_SLICE_MARKERS = [
    "Documentation/zigux/freeze-map.md",
    "`kernel/trace/ring_buffer.c`",
    "Study / Boundary Only",
    "runtime task ownership or event-loop substrate parity",
    "polling-backed wake or dispatch behavior",
    "ring-buffer parity",
    "Architecture Council",
]

REQUIRED_TRACE_EVENTS_MANIFEST_MARKERS = [
    '"id": "runtime-trace-events-freeze-map-boundary"',
    '"zigux_destination": "Documentation/zigux/phase9-runtime-trace-events-survey.md"',
    '"id": "runtime-trace-events-substrate-handoff"',
    '"zigux_destination": "samples/zigux/runtime_trace_events_loader.zig"',
    "`kernel/trace/ring_buffer.c`",
    "Architecture Council",
]

REQUIRED_TRACE_EVENTS_SURVEY_TEST_MARKERS = [
    'var saw_freeze_map_boundary = false;',
    'std.mem.eql(u8, gap.id, "runtime-trace-events-freeze-map-boundary")',
    'std.mem.indexOf(u8, gap.why_now, "`kernel/trace/ring_buffer.c`")',
    'std.mem.indexOf(u8, survey_doc, "Documentation/zigux/freeze-map.md")',
    'std.mem.indexOf(u8, survey_doc, "`kernel/trace/ring_buffer.c`")',
    'std.mem.indexOf(u8, module_doc, "`kernel/trace/ring_buffer.c`")',
]

REQUIRED_MODULE_METADATA_DOC_MARKERS = [
    "PHASE9_SLICE=module-metadata-depmod-bridge-survey",
    "zigux/tests/runtime_module_metadata_manifest.json",
    "zigux/tests/runtime_module_metadata_survey.zig",
    "scripts/zigux/check-phase9-module-metadata-packet.py",
]

REQUIRED_MODULE_METADATA_MANIFEST_MARKERS = [
    '"lane_key": "P9-L09"',
    '"runtime_sample_files": [',
    '"runtime_loader_files": [',
    '"absent_depmod_markers": [',
    '"trace_events_loader_present": false',
    '"depmod_bridge_present": false',
]

REQUIRED_MODULE_METADATA_SURVEY_MARKERS = [
    "Documentation/zigux/phase9-module-metadata-depmod-bridge-survey.md",
    "zigux/tests/runtime_module_metadata_manifest.json",
    "scripts/zigux/check-phase9-module-metadata-packet.py",
    "module metadata survey doc records the exact evidence and missing depmod bridge",
]

REQUIRED_MODULE_METADATA_CHECKER_MARKERS = [
    "PHASE9_MODULE_METADATA_PACKET=pass",
    "Documentation/zigux/phase9-module-metadata-depmod-bridge-survey.md",
    "zigux/tests/runtime_module_metadata_manifest.json",
    "zigux/tests/runtime_module_metadata_survey.zig",
]


def read_text(root: Path, rel_path: str) -> str:
    return (root / rel_path).read_text(encoding="utf-8")


def collect_missing_files(root: Path) -> list[str]:
    return [rel_path for rel_path in REQUIRED_FILES if not (root / rel_path).exists()]


def required_marker_count() -> int:
    return (
        len(REQUIRED_MAKE_MARKERS)
        + len(REQUIRED_WORKFLOW_MARKERS)
        + len(REQUIRED_SCRIPT_README_MARKERS)
        + len(REQUIRED_TESTS_README_MARKERS)
        + len(REQUIRED_DOC_README_MARKERS)
        + len(REQUIRED_FREEZE_MAP_MARKERS)
        + len(REQUIRED_REVIEW_CHECKLIST_MARKERS)
        + len(REQUIRED_LOADER_GAP_SURVEY_MARKERS)
        + len(REQUIRED_PHASE9_BUILD_MARKERS)
        + len(REQUIRED_LOADER_GAP_SURVEY_TEST_MARKERS)
        + len(REQUIRED_LOADER_GAP_MANIFEST_MARKERS)
        + len(REQUIRED_TRACE_EVENTS_SURVEY_MARKERS)
        + len(REQUIRED_TRACE_EVENTS_MODULE_SLICE_MARKERS)
        + len(REQUIRED_TRACE_EVENTS_MANIFEST_MARKERS)
        + len(REQUIRED_TRACE_EVENTS_SURVEY_TEST_MARKERS)
        + len(REQUIRED_MODULE_METADATA_DOC_MARKERS)
        + len(REQUIRED_MODULE_METADATA_MANIFEST_MARKERS)
        + len(REQUIRED_MODULE_METADATA_SURVEY_MARKERS)
        + len(REQUIRED_MODULE_METADATA_CHECKER_MARKERS)
    )


def validate(root: Path) -> tuple[list[str], list[str]]:
    missing_files = collect_missing_files(root)
    if missing_files:
        return missing_files, []

    makefile = read_text(root, "zigux/Makefile")
    workflow = read_text(root, ".github/workflows/zigux-bootstrap.yml")
    freeze_map = read_text(root, "Documentation/zigux/freeze-map.md")
    script_readme = read_text(root, "scripts/zigux/README.md")
    tests_readme = read_text(root, "zigux/tests/README.md")
    doc_readme = read_text(root, "Documentation/zigux/README.md")
    review_checklist = read_text(root, "Documentation/zigux/review-checklist.md")
    loader_gap_survey = read_text(root, "Documentation/zigux/phase9-runtime-loader-gap-survey.md")
    trace_events_survey = read_text(root, "Documentation/zigux/phase9-runtime-trace-events-survey.md")
    trace_events_module_slice = read_text(root, "Documentation/zigux/phase9-runtime-trace-events-module-slice.md")
    module_metadata_survey_doc = read_text(root, "Documentation/zigux/phase9-module-metadata-depmod-bridge-survey.md")
    phase9_build = read_text(root, "zigux/tests/phase9_build.zig")
    loader_gap_survey_test = read_text(root, "zigux/tests/runtime_loader_gap_survey.zig")
    loader_gap_manifest = read_text(root, "zigux/tests/runtime_loader_gap_manifest.json")
    trace_events_manifest = read_text(root, "zigux/tests/runtime_trace_events_manifest.json")
    trace_events_survey_test = read_text(root, "zigux/tests/runtime_trace_events_survey.zig")
    module_metadata_manifest = read_text(root, "zigux/tests/runtime_module_metadata_manifest.json")
    module_metadata_survey_test = read_text(root, "zigux/tests/runtime_module_metadata_survey.zig")
    module_metadata_checker = read_text(root, "scripts/zigux/check-phase9-module-metadata-packet.py")

    missing_markers: list[str] = []

    for marker in REQUIRED_MAKE_MARKERS:
        if marker not in makefile:
            missing_markers.append(f"make:{marker}")
    for marker in REQUIRED_WORKFLOW_MARKERS:
        if marker not in workflow:
            missing_markers.append(f"workflow:{marker}")
    for marker in REQUIRED_SCRIPT_README_MARKERS:
        if marker not in script_readme:
            missing_markers.append(f"script_readme:{marker}")
    for marker in REQUIRED_TESTS_README_MARKERS:
        if marker not in tests_readme:
            missing_markers.append(f"tests_readme:{marker}")
    for marker in REQUIRED_DOC_README_MARKERS:
        if marker not in doc_readme:
            missing_markers.append(f"doc_readme:{marker}")
    for marker in REQUIRED_FREEZE_MAP_MARKERS:
        if marker not in freeze_map:
            missing_markers.append(f"freeze_map:{marker}")
    for marker in REQUIRED_REVIEW_CHECKLIST_MARKERS:
        if marker not in review_checklist:
            missing_markers.append(f"review_checklist:{marker}")
    for marker in REQUIRED_LOADER_GAP_SURVEY_MARKERS:
        if marker not in loader_gap_survey:
            missing_markers.append(f"loader_gap_survey:{marker}")
    for marker in REQUIRED_PHASE9_BUILD_MARKERS:
        if marker not in phase9_build:
            missing_markers.append(f"phase9_build:{marker}")
    for marker in REQUIRED_LOADER_GAP_SURVEY_TEST_MARKERS:
        if marker not in loader_gap_survey_test:
            missing_markers.append(f"loader_gap_survey_test:{marker}")
    for marker in REQUIRED_LOADER_GAP_MANIFEST_MARKERS:
        if marker not in loader_gap_manifest:
            missing_markers.append(f"loader_gap_manifest:{marker}")
    for marker in REQUIRED_TRACE_EVENTS_SURVEY_MARKERS:
        if marker not in trace_events_survey:
            missing_markers.append(f"trace_events_survey:{marker}")
    for marker in REQUIRED_TRACE_EVENTS_MODULE_SLICE_MARKERS:
        if marker not in trace_events_module_slice:
            missing_markers.append(f"trace_events_module_slice:{marker}")
    for marker in REQUIRED_TRACE_EVENTS_MANIFEST_MARKERS:
        if marker not in trace_events_manifest:
            missing_markers.append(f"trace_events_manifest:{marker}")
    for marker in REQUIRED_TRACE_EVENTS_SURVEY_TEST_MARKERS:
        if marker not in trace_events_survey_test:
            missing_markers.append(f"trace_events_survey_test:{marker}")
    for marker in REQUIRED_MODULE_METADATA_DOC_MARKERS:
        if marker not in module_metadata_survey_doc:
            missing_markers.append(f"module_metadata_survey_doc:{marker}")
    for marker in REQUIRED_MODULE_METADATA_MANIFEST_MARKERS:
        if marker not in module_metadata_manifest:
            missing_markers.append(f"module_metadata_manifest:{marker}")
    for marker in REQUIRED_MODULE_METADATA_SURVEY_MARKERS:
        if marker not in module_metadata_survey_test:
            missing_markers.append(f"module_metadata_survey_test:{marker}")
    for marker in REQUIRED_MODULE_METADATA_CHECKER_MARKERS:
        if marker not in module_metadata_checker:
            missing_markers.append(f"module_metadata_checker:{marker}")

    return [], missing_markers


def write_fixture_tree(root: Path) -> None:
    for rel_path in REQUIRED_FILES:
        target = root / rel_path
        target.parent.mkdir(parents=True, exist_ok=True)

    file_contents = {
        "Documentation/zigux/freeze-map.md": "\n".join(REQUIRED_FREEZE_MAP_MARKERS) + "\n",
        "scripts/zigux/validate-phase9.py": "validate-phase9 self fixture\n",
        "scripts/zigux/README.md": "\n".join(REQUIRED_SCRIPT_README_MARKERS) + "\n",
        "scripts/zigux/check-phase9-module-metadata-packet.py": "\n".join(REQUIRED_MODULE_METADATA_CHECKER_MARKERS) + "\n",
        "Documentation/zigux/README.md": "\n".join(REQUIRED_DOC_README_MARKERS) + "\n",
        "Documentation/zigux/review-checklist.md": "\n".join(REQUIRED_REVIEW_CHECKLIST_MARKERS) + "\n",
        "Documentation/zigux/phase9-runtime-loader-gap-survey.md": "\n".join(REQUIRED_LOADER_GAP_SURVEY_MARKERS) + "\n",
        "Documentation/zigux/phase9-runtime-trace-events-survey.md": "\n".join(REQUIRED_TRACE_EVENTS_SURVEY_MARKERS) + "\n",
        "Documentation/zigux/phase9-runtime-trace-events-module-slice.md": "\n".join(REQUIRED_TRACE_EVENTS_MODULE_SLICE_MARKERS) + "\n",
        "Documentation/zigux/phase9-module-metadata-depmod-bridge-survey.md": "\n".join(REQUIRED_MODULE_METADATA_DOC_MARKERS) + "\n",
        "zigux/Makefile": "\n".join(REQUIRED_MAKE_MARKERS) + "\n",
        "zigux/tests/README.md": "\n".join(REQUIRED_TESTS_README_MARKERS) + "\n",
        "zigux/tests/phase9_build.zig": "\n".join(REQUIRED_PHASE9_BUILD_MARKERS) + "\n",
        "zigux/tests/runtime_loader_gap_manifest.json": "\n".join(REQUIRED_LOADER_GAP_MANIFEST_MARKERS) + "\n",
        "zigux/tests/runtime_loader_gap_survey.zig": "\n".join(REQUIRED_LOADER_GAP_SURVEY_TEST_MARKERS) + "\n",
        "zigux/tests/runtime_trace_events_manifest.json": "\n".join(REQUIRED_TRACE_EVENTS_MANIFEST_MARKERS) + "\n",
        "zigux/tests/runtime_trace_events_survey.zig": "\n".join(REQUIRED_TRACE_EVENTS_SURVEY_TEST_MARKERS) + "\n",
        "zigux/tests/runtime_module_metadata_manifest.json": "\n".join(REQUIRED_MODULE_METADATA_MANIFEST_MARKERS) + "\n",
        "zigux/tests/runtime_module_metadata_survey.zig": "\n".join(REQUIRED_MODULE_METADATA_SURVEY_MARKERS) + "\n",
        ".github/workflows/zigux-bootstrap.yml": "\n".join(REQUIRED_WORKFLOW_MARKERS) + "\n",
    }

    for rel_path, text in file_contents.items():
        (root / rel_path).write_text(text, encoding="utf-8")


def expect_missing_marker(label: str, root: Path, expected_marker: str) -> None:
    missing_files, missing_markers = validate(root)
    if missing_files:
        joined = ",".join(missing_files)
        raise SystemExit(f"phase9-self-test:{label}:unexpected_missing_files:{joined}")
    if expected_marker not in missing_markers:
        actual = ",".join(missing_markers) if missing_markers else "none"
        raise SystemExit(
            f"phase9-self-test:{label}:expected_missing_marker:{expected_marker}:actual:{actual}"
        )


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase9_validator_") as tmp_dir:
        tmp_root = Path(tmp_dir)
        write_fixture_tree(tmp_root)

        missing_files, missing_markers = validate(tmp_root)
        if missing_files or missing_markers:
            raise SystemExit(
                "phase9-self-test:baseline_failed:"
                f"files={','.join(missing_files) if missing_files else 'none'}:"
                f"markers={','.join(missing_markers) if missing_markers else 'none'}"
            )

        survey_doc_path = tmp_root / "Documentation/zigux/phase9-module-metadata-depmod-bridge-survey.md"
        original_survey_doc = survey_doc_path.read_text(encoding="utf-8")
        survey_doc_path.write_text(
            original_survey_doc.replace(
                "scripts/zigux/check-phase9-module-metadata-packet.py",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "module_metadata_survey_doc_checker_marker",
            tmp_root,
            "module_metadata_survey_doc:scripts/zigux/check-phase9-module-metadata-packet.py",
        )
        survey_doc_path.write_text(original_survey_doc, encoding="utf-8")

        checker_path = tmp_root / "scripts/zigux/check-phase9-module-metadata-packet.py"
        original_checker = checker_path.read_text(encoding="utf-8")
        checker_path.write_text(
            original_checker.replace("PHASE9_MODULE_METADATA_PACKET=pass", "", 1),
            encoding="utf-8",
        )
        expect_missing_marker(
            "module_metadata_checker_pass_marker",
            tmp_root,
            "module_metadata_checker:PHASE9_MODULE_METADATA_PACKET=pass",
        )
        checker_path.write_text(original_checker, encoding="utf-8")

    print("PHASE9_VALIDATOR_SELF_TEST=pass")
    print("PHASE9_VALIDATOR_SELF_TEST_CASE_COUNT=2")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the shared Phase 9 runtime evidence packet."
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run built-in drift checks against a temporary Phase 9 fixture tree.",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    missing_files, missing_markers = validate(ROOT)
    if missing_files:
        print("PHASE9_VALIDATION=fail")
        print("MISSING_PHASE9_FILES_START")
        for item in missing_files:
            print(item)
        print("MISSING_PHASE9_FILES_END")
        return 1
    if missing_markers:
        print("PHASE9_VALIDATION=fail")
        print("MISSING_PHASE9_MARKERS_START")
        for marker in missing_markers:
            print(marker)
        print("MISSING_PHASE9_MARKERS_END")
        return 1

    print("PHASE9_VALIDATION=pass")
    print(f"PHASE9_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(f"PHASE9_REQUIRED_MARKER_COUNT={required_marker_count()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())