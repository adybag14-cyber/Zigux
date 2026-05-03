#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[2]

SURVEY_PATH = "Documentation/zigux/phase9-module-metadata-depmod-bridge-survey.md"
MANIFEST_PATH = "zigux/tests/runtime_module_metadata_manifest.json"
SURVEY_TEST_PATH = "zigux/tests/runtime_module_metadata_survey.zig"
ATOMIC64_SAMPLE_PATH = "samples/zigux/runtime_atomic64.zig"
BITMAP_SAMPLE_PATH = "samples/zigux/runtime_bitmap.zig"
KRETPROBE_SAMPLE_PATH = "samples/zigux/runtime_kretprobe.zig"
TRACE_EVENTS_SAMPLE_PATH = "samples/zigux/runtime_trace_events.zig"

REQUIRED_FILES = [
    SURVEY_PATH,
    MANIFEST_PATH,
    SURVEY_TEST_PATH,
    ATOMIC64_SAMPLE_PATH,
    BITMAP_SAMPLE_PATH,
    KRETPROBE_SAMPLE_PATH,
    TRACE_EVENTS_SAMPLE_PATH,
]

SURVEY_REQUIRED_MARKERS = [
    "`PHASE9_SLICE=runtime-module-metadata-depmod-bridge-survey`",
    "Each of those starters exposes a reviewable `ModuleDescriptor` with the same four metadata fields:",
    "- `name`",
    "- `anchor`",
    "- `requires_runtime_substrate`",
    "- `provides_selftest_hook`",
    "- `samples/zigux/runtime_atomic64.zig`",
    "- `samples/zigux/runtime_bitmap.zig`",
    "- `samples/zigux/runtime_kretprobe.zig`",
    "- `samples/zigux/runtime_trace_events.zig`",
    "The roadmap's Phase 9 goal is the first loadable Zigux runtime-module family with selftest hooks and bounded lifecycle parity under `zigux/tests/runtime_*` and `samples/zigux/runtime_*`.",
]

SURVEY_TEST_REQUIRED_MARKERS = [
    '"samples/zigux/runtime_atomic64.zig"',
    '"samples/zigux/runtime_bitmap.zig"',
    '"samples/zigux/runtime_kretprobe.zig"',
    '"samples/zigux/runtime_trace_events.zig"',
    '"runtime_atomic64"',
    '"runtime_bitmap"',
    '"runtime_kretprobe"',
    '"runtime_trace_events"',
    '"lib/atomic64_test.c"',
    '"lib/test_bitmap.c"',
    '"samples/kprobes/kretprobe_example.c"',
    '"samples/trace_events/trace-events-sample.c"',
    '"requires_runtime_substrate = true"',
    '"provides_selftest_hook = true"',
]

EXPECTED_DESCRIPTOR_SURFACES = [
    {
        "sample_path": ATOMIC64_SAMPLE_PATH,
        "module_name": "runtime_atomic64",
        "anchor": "lib/atomic64_test.c",
    },
    {
        "sample_path": BITMAP_SAMPLE_PATH,
        "module_name": "runtime_bitmap",
        "anchor": "lib/test_bitmap.c",
    },
    {
        "sample_path": KRETPROBE_SAMPLE_PATH,
        "module_name": "runtime_kretprobe",
        "anchor": "samples/kprobes/kretprobe_example.c",
    },
    {
        "sample_path": TRACE_EVENTS_SAMPLE_PATH,
        "module_name": "runtime_trace_events",
        "anchor": "samples/trace_events/trace-events-sample.c",
    },
]

SAMPLE_REQUIRED_MARKERS = {
    ATOMIC64_SAMPLE_PATH: [
        "pub const ModuleDescriptor = struct",
        '.name = "runtime_atomic64"',
        '.anchor = "lib/atomic64_test.c"',
        ".requires_runtime_substrate = true",
        ".provides_selftest_hook = true",
    ],
    BITMAP_SAMPLE_PATH: [
        "pub const ModuleDescriptor = struct",
        '.name = "runtime_bitmap"',
        '.anchor = "lib/test_bitmap.c"',
        ".requires_runtime_substrate = true",
        ".provides_selftest_hook = true",
    ],
    KRETPROBE_SAMPLE_PATH: [
        "pub const ModuleDescriptor = struct",
        '.name = "runtime_kretprobe"',
        '.anchor = "samples/kprobes/kretprobe_example.c"',
        ".requires_runtime_substrate = true",
        ".provides_selftest_hook = true",
    ],
    TRACE_EVENTS_SAMPLE_PATH: [
        "pub const ModuleDescriptor = struct",
        '.name = "runtime_trace_events"',
        '.anchor = "samples/trace_events/trace-events-sample.c"',
        ".requires_runtime_substrate = true",
        ".provides_selftest_hook = true",
    ],
}

SAMPLE_FORBIDDEN_MARKERS = [
    "MODULE_INFO(",
    "MODULE_ALIAS(",
    ".modinfo",
    "modules.alias",
    "modules.order",
    "modules.builtin",
    "Module.symvers",
    "scripts/depmod.sh",
]


def read_text(root: Path, rel_path: str) -> str:
    return (root / rel_path).read_text(encoding="utf-8")


def collect_missing_files(root: Path) -> list[str]:
    return [rel_path for rel_path in REQUIRED_FILES if not (root / rel_path).exists()]


def validate_manifest(root: Path) -> list[str]:
    manifest_text = read_text(root, MANIFEST_PATH)
    failures: list[str] = []

    try:
        manifest = json.loads(manifest_text)
    except json.JSONDecodeError:
        return ["manifest:json_decode_failed"]

    descriptor_surfaces = manifest.get("descriptor_surfaces")
    if descriptor_surfaces != EXPECTED_DESCRIPTOR_SURFACES:
        failures.append("manifest:descriptor_surfaces_drift")

    summary = manifest.get("survey_summary")
    if not isinstance(summary, dict):
        failures.append("manifest:survey_summary_missing")
    else:
        if summary.get("runtime_descriptor_count") != 4:
            failures.append("manifest:runtime_descriptor_count_drift")
        if summary.get("depmod_gap_count") != 8:
            failures.append("manifest:depmod_gap_count_drift")

    return failures


def validate(root: Path) -> tuple[list[str], list[str]]:
    missing_files = collect_missing_files(root)
    if missing_files:
        return missing_files, []

    survey_text = read_text(root, SURVEY_PATH)
    manifest_failures = validate_manifest(root)
    survey_test_text = read_text(root, SURVEY_TEST_PATH)

    failures: list[str] = []

    for marker in SURVEY_REQUIRED_MARKERS:
        if marker not in survey_text:
            failures.append(f"survey:{marker}")

    for marker in SURVEY_TEST_REQUIRED_MARKERS:
        if marker not in survey_test_text:
            failures.append(f"survey_test:{marker}")

    for rel_path, markers in SAMPLE_REQUIRED_MARKERS.items():
        sample_text = read_text(root, rel_path)
        for marker in markers:
            if marker not in sample_text:
                failures.append(f"{rel_path}:{marker}")
        for marker in SAMPLE_FORBIDDEN_MARKERS:
            if marker in sample_text:
                failures.append(f"{rel_path}:forbidden:{marker}")

    failures.extend(manifest_failures)
    return [], failures


def write_fixture_tree(root: Path) -> None:
    (root / "Documentation/zigux").mkdir(parents=True, exist_ok=True)
    (root / "zigux/tests").mkdir(parents=True, exist_ok=True)
    (root / "samples/zigux").mkdir(parents=True, exist_ok=True)

    (root / SURVEY_PATH).write_text(
        "\n".join(
            [
                "# Phase 9 Module Metadata and Depmod Bridge Survey",
                "",
                "- `PHASE9_SLICE=runtime-module-metadata-depmod-bridge-survey`",
                "The roadmap's Phase 9 goal is the first loadable Zigux runtime-module family with selftest hooks and bounded lifecycle parity under `zigux/tests/runtime_*` and `samples/zigux/runtime_*`.",
                "Each of those starters exposes a reviewable `ModuleDescriptor` with the same four metadata fields:",
                "- `name`",
                "- `anchor`",
                "- `requires_runtime_substrate`",
                "- `provides_selftest_hook`",
                "- `samples/zigux/runtime_atomic64.zig`",
                "- `samples/zigux/runtime_bitmap.zig`",
                "- `samples/zigux/runtime_kretprobe.zig`",
                "- `samples/zigux/runtime_trace_events.zig`",
                "",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    manifest = {
        "survey_summary": {
            "runtime_descriptor_count": 4,
            "depmod_gap_count": 8,
        },
        "descriptor_surfaces": EXPECTED_DESCRIPTOR_SURFACES,
    }
    (root / MANIFEST_PATH).write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    (root / SURVEY_TEST_PATH).write_text(
        "\n".join(
            [
                '"samples/zigux/runtime_atomic64.zig"',
                '"samples/zigux/runtime_bitmap.zig"',
                '"samples/zigux/runtime_kretprobe.zig"',
                '"samples/zigux/runtime_trace_events.zig"',
                '"runtime_atomic64"',
                '"runtime_bitmap"',
                '"runtime_kretprobe"',
                '"runtime_trace_events"',
                '"lib/atomic64_test.c"',
                '"lib/test_bitmap.c"',
                '"samples/kprobes/kretprobe_example.c"',
                '"samples/trace_events/trace-events-sample.c"',
                '"requires_runtime_substrate = true"',
                '"provides_selftest_hook = true"',
                "",
            ]
        ),
        encoding="utf-8",
    )

    sample_contents = {
        ATOMIC64_SAMPLE_PATH: "\n".join(
            [
                "pub const ModuleDescriptor = struct {};",
                'const descriptor = .{ .name = "runtime_atomic64", .anchor = "lib/atomic64_test.c", .requires_runtime_substrate = true, .provides_selftest_hook = true };',
                "",
            ]
        ),
        BITMAP_SAMPLE_PATH: "\n".join(
            [
                "pub const ModuleDescriptor = struct {};",
                'const descriptor = .{ .name = "runtime_bitmap", .anchor = "lib/test_bitmap.c", .requires_runtime_substrate = true, .provides_selftest_hook = true };',
                "",
            ]
        ),
        KRETPROBE_SAMPLE_PATH: "\n".join(
            [
                "pub const ModuleDescriptor = struct {};",
                'const descriptor = .{ .name = "runtime_kretprobe", .anchor = "samples/kprobes/kretprobe_example.c", .requires_runtime_substrate = true, .provides_selftest_hook = true };',
                "",
            ]
        ),
        TRACE_EVENTS_SAMPLE_PATH: "\n".join(
            [
                "pub const ModuleDescriptor = struct {};",
                'const descriptor = .{ .name = "runtime_trace_events", .anchor = "samples/trace_events/trace-events-sample.c", .requires_runtime_substrate = true, .provides_selftest_hook = true };',
                "",
            ]
        ),
    }
    for rel_path, content in sample_contents.items():
        (root / rel_path).write_text(content, encoding="utf-8")


def expect_failure(label: str, root: Path, expected_failure: str) -> None:
    missing_files, failures = validate(root)
    if missing_files:
        raise SystemExit(
            f"phase9-runtime-starter-descriptors-selftest:{label}:unexpected_missing_files:{','.join(missing_files)}"
        )
    if expected_failure not in failures:
        actual = ",".join(failures) if failures else "none"
        raise SystemExit(
            f"phase9-runtime-starter-descriptors-selftest:{label}:expected_failure:{expected_failure}:actual:{actual}"
        )


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase9_runtime_starters_") as tmp_dir:
        tmp_root = Path(tmp_dir)
        write_fixture_tree(tmp_root)

        missing_files, failures = validate(tmp_root)
        if missing_files or failures:
            raise SystemExit(
                "phase9-runtime-starter-descriptors-selftest:baseline_failed:"
                f"files={','.join(missing_files) if missing_files else 'none'}:"
                f"failures={','.join(failures) if failures else 'none'}"
            )

        atomic64_sample_path = tmp_root / ATOMIC64_SAMPLE_PATH
        original_atomic64 = atomic64_sample_path.read_text(encoding="utf-8")
        atomic64_sample_path.write_text(
            original_atomic64.replace('.name = "runtime_atomic64"', "", 1),
            encoding="utf-8",
        )
        expect_failure(
            "atomic64_descriptor_name",
            tmp_root,
            f'{ATOMIC64_SAMPLE_PATH}:.name = "runtime_atomic64"',
        )
        atomic64_sample_path.write_text(original_atomic64, encoding="utf-8")

        survey_test_path = tmp_root / SURVEY_TEST_PATH
        original_survey_test = survey_test_path.read_text(encoding="utf-8")
        survey_test_path.write_text(
            original_survey_test.replace('"samples/zigux/runtime_bitmap.zig"', "", 1),
            encoding="utf-8",
        )
        expect_failure(
            "survey_test_bitmap_path",
            tmp_root,
            'survey_test:"samples/zigux/runtime_bitmap.zig"',
        )
        survey_test_path.write_text(original_survey_test, encoding="utf-8")

        manifest_path = tmp_root / MANIFEST_PATH
        original_manifest = manifest_path.read_text(encoding="utf-8")
        manifest = json.loads(original_manifest)
        manifest["descriptor_surfaces"][2]["anchor"] = "samples/kprobes/kretprobe_wrong.c"
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        expect_failure(
            "manifest_descriptor_anchor",
            tmp_root,
            "manifest:descriptor_surfaces_drift",
        )
        manifest_path.write_text(original_manifest, encoding="utf-8")

        trace_events_sample_path = tmp_root / TRACE_EVENTS_SAMPLE_PATH
        original_trace_events = trace_events_sample_path.read_text(encoding="utf-8")
        trace_events_sample_path.write_text(
            original_trace_events + "MODULE_ALIAS(dummy)\n",
            encoding="utf-8",
        )
        expect_failure(
            "trace_events_forbidden_depmod_surface",
            tmp_root,
            f"{TRACE_EVENTS_SAMPLE_PATH}:forbidden:MODULE_ALIAS(",
        )
        trace_events_sample_path.write_text(original_trace_events, encoding="utf-8")

    print("PHASE9_RUNTIME_STARTER_DESCRIPTORS_SELF_TEST=pass")
    print("PHASE9_RUNTIME_STARTER_DESCRIPTORS_SELF_TEST_CASE_COUNT=4")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the direct Phase 9 runtime starter descriptor surface."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=ROOT,
        help="Repository root to validate. Defaults to the current directory.",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run the built-in starter-descriptor fixture checks.",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    missing_files, failures = validate(args.root)
    if missing_files:
        print("PHASE9_RUNTIME_STARTER_DESCRIPTORS=fail")
        print("MISSING_PHASE9_RUNTIME_STARTER_DESCRIPTOR_FILES_START")
        for item in missing_files:
            print(item)
        print("MISSING_PHASE9_RUNTIME_STARTER_DESCRIPTOR_FILES_END")
        return 1
    if failures:
        print("PHASE9_RUNTIME_STARTER_DESCRIPTORS=fail")
        print("PHASE9_RUNTIME_STARTER_DESCRIPTOR_FAILURES_START")
        for failure in failures:
            print(failure)
        print("PHASE9_RUNTIME_STARTER_DESCRIPTOR_FAILURES_END")
        return 1

    required_marker_count = (
        len(SURVEY_REQUIRED_MARKERS)
        + len(SURVEY_TEST_REQUIRED_MARKERS)
        + sum(len(markers) for markers in SAMPLE_REQUIRED_MARKERS.values())
        + (len(SAMPLE_FORBIDDEN_MARKERS) * len(SAMPLE_REQUIRED_MARKERS))
        + 3
    )
    print("PHASE9_RUNTIME_STARTER_DESCRIPTORS=pass")
    print(f"PHASE9_RUNTIME_STARTER_DESCRIPTOR_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(
        "PHASE9_RUNTIME_STARTER_DESCRIPTOR_REQUIRED_MARKER_COUNT="
        f"{required_marker_count}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
