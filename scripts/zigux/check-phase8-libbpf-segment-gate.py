#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import tempfile


SCRIPT_PATH = Path(__file__).resolve()
ROOT = SCRIPT_PATH.parents[2] if len(SCRIPT_PATH.parents) > 2 else SCRIPT_PATH.parent

MANIFEST_PATH = "tools/lib/bpf/zigux_segments/manifest.json"
SURVEY_PATH = "Documentation/zigux/phase8-libbpf-segment-survey.md"
BUILD_PATH = "zigux/tests/phase8_libbpf_segments_only_build.zig"
VERIFY_PATH = "tools/lib/bpf/zigux_segments/verify.zig"

REQUIRED_FILES = [
    ".github/workflows/zigux-bootstrap.yml",
    "Documentation/zigux/README.md",
    SURVEY_PATH,
    "scripts/zigux/README.md",
    "scripts/zigux/check-phase8-libbpf-segment-gate.py",
    "zigux/Makefile",
    "zigux/tests/README.md",
    BUILD_PATH,
    MANIFEST_PATH,
    VERIFY_PATH,
]

LANDED_SLUGS = [
    "logging-version-and-errno",
    "pin-path-helpers",
    "cpu-mask-parsing",
    "type-name-helpers",
    "fdinfo-map-info-helpers",
    "map-reuse-compatibility",
    "perf-buffer-poll-bookkeeping",
]

DEFERRED_SLUGS = [
    "file-path-and-handle-bridge",
    "perf-buffer-online-cpu-routing",
    "skeleton-population",
    "object-and-elf-loader",
    "btf-relocation-and-program-load",
]


def oxford_backtick_list(items: list[str]) -> str:
    wrapped = [f"`{item}`" for item in items]
    if len(wrapped) == 1:
        return wrapped[0]
    if len(wrapped) == 2:
        return " and ".join(wrapped)
    return ", ".join(wrapped[:-1]) + ", and " + wrapped[-1]


COUNT_WORDS = {
    0: "zero",
    1: "one",
    2: "two",
    3: "three",
    4: "four",
    5: "five",
    6: "six",
    7: "seven",
    8: "eight",
    9: "nine",
    10: "ten",
    11: "eleven",
    12: "twelve",
    13: "thirteen",
    14: "fourteen",
    15: "fifteen",
    16: "sixteen",
    17: "seventeen",
    18: "eighteen",
    19: "nineteen",
    20: "twenty",
}


def count_marker(count: int) -> str:
    word = COUNT_WORDS.get(count, str(count))
    noun = "segment" if count == 1 else "segments"
    return f"The manifest currently records {word} bounded {noun}"


SURVEY_MARKERS = (
    "The directly readable stable-output helper set therefore now keeps the aggregate verifier plus `cpu_mask.zig`, `logging.zig`, `pin_path.zig`, `type_names.zig`, `perf_buffer_poll.zig`, `perf_buffer_ready_window.zig`, `online_cpu_routing.zig`, `online_cpu_routing_verify.zig`, `ready_buffer_fd_verify.zig`, and `ready_buffer_window_verify.zig` explicit.",
    "Current repo-facing reminder surfaces already keep the bridge helper, the focused bridge build shard, the focused libbpf-segment shard, and the shared Phase 8 build replay explicit on `master`, while that same checker packet already keeps the landed `tools/lib/bpf/zigux_segments/online_cpu_routing.zig` helper-local evidence explicit.",
    "This survey should therefore keep the helper-first packet, the bridge-plus-build reminder packet, and the routing-helper evidence explicit together without promoting the still-deferred setup-side routing, reopen-flow, token-materialization, or object-model work.",
)

MAKEFILE_MARKERS = (
    "phase8-validate:",
    "scripts/zigux/check-phase8-libbpf-segment-gate.py --self-test",
    "scripts/zigux/check-phase8-libbpf-segment-gate.py",
    "phase8-libbpf-segments-test:",
    "zigux/tests/phase8_libbpf_segments_only_build.zig --summary all",
)

BUILD_MARKERS = (
    "../../tools/lib/bpf/zigux_segments/verify.zig",
    "phase8-libbpf-segment-verify-tests",
    "Run focused Phase 8 libbpf segment verify build",
)

VERIFY_MARKERS = (
    "resolveNextOnlineCpuRouteCpuIndexReturnAtIndex",
    "resolveNextOnlineCpuRouteBufferFdAtIndex",
    "resolveReadyBufferFdLookupReturnAtAttempt",
)


def read_text(root: Path, rel_path: str) -> str:
    return (root / rel_path).read_text(encoding="utf-8")


def collect_missing_files(root: Path) -> list[str]:
    return [rel_path for rel_path in REQUIRED_FILES if not (root / rel_path).exists()]


def load_manifest(root: Path) -> dict:
    try:
        return json.loads(read_text(root, MANIFEST_PATH))
    except json.JSONDecodeError as exc:
        raise ValueError(f"manifest:invalid_json:{exc.msg}") from exc


def validate(root: Path) -> tuple[list[str], list[str], list[str]]:
    missing_files = collect_missing_files(root)
    if missing_files:
        return missing_files, [], []

    missing_markers: list[str] = []
    consistency_errors: list[str] = []

    survey_text = read_text(root, SURVEY_PATH)
    for marker in SURVEY_MARKERS:
        if marker not in survey_text:
            missing_markers.append(f"{SURVEY_PATH}:{marker}")

    makefile_text = read_text(root, "zigux/Makefile")
    for marker in MAKEFILE_MARKERS:
        if marker not in makefile_text:
            missing_markers.append(f"zigux/Makefile:{marker}")

    build_text = read_text(root, BUILD_PATH)
    for marker in BUILD_MARKERS:
        if marker not in build_text:
            missing_markers.append(f"{BUILD_PATH}:{marker}")

    verify_text = read_text(root, VERIFY_PATH)
    for marker in VERIFY_MARKERS:
        if marker not in verify_text:
            missing_markers.append(f"{VERIFY_PATH}:{marker}")

    try:
        manifest = load_manifest(root)
    except ValueError as exc:
        consistency_errors.append(str(exc))
        return [], missing_markers, consistency_errors

    if manifest.get("anchor") != "tools/lib/bpf/libbpf.c":
        consistency_errors.append("manifest:unexpected_anchor")

    segments = manifest.get("segments")
    if not isinstance(segments, list):
        consistency_errors.append("manifest:missing_or_invalid_segments")
        return [], missing_markers, consistency_errors

    segment_count = len(segments)
    expected_count_marker = count_marker(segment_count)
    if expected_count_marker not in survey_text:
        missing_markers.append(f"{SURVEY_PATH}:{expected_count_marker}")

    landed = [segment.get("slug") for segment in segments if segment.get("status") == "starter_landed"]
    deferred = [
        segment.get("slug")
        for segment in segments
        if segment.get("status") in {"deferred_high_risk", "blocked_on_object_model"}
    ]

    if landed != LANDED_SLUGS:
        consistency_errors.append(
            "manifest:unexpected_landed_slugs:" + ",".join([slug or "<missing>" for slug in landed])
        )
    if deferred != DEFERRED_SLUGS:
        consistency_errors.append(
            "manifest:unexpected_deferred_slugs:" + ",".join([slug or "<missing>" for slug in deferred])
        )

    landed_marker = f"The seven landed bounded slices are {oxford_backtick_list(LANDED_SLUGS)}."
    if landed_marker not in survey_text:
        missing_markers.append(f"{SURVEY_PATH}:{landed_marker}")

    return [], missing_markers, consistency_errors


FIXTURE_TEXT = {
    ".github/workflows/zigux-bootstrap.yml": "name: zigux-bootstrap\n- name: Validate Phase 8 tooling routes\n  run: make -C zigux phase8-validate\n",
    "Documentation/zigux/README.md": "# Zigux Documentation\n- `Documentation/zigux/phase8-libbpf-segment-survey.md`\n- `scripts/zigux/check-phase8-libbpf-segment-gate.py`\n",
    "scripts/zigux/README.md": "# scripts/zigux\n- check-phase8-libbpf-segment-gate.py\n- Documentation/zigux/phase8-libbpf-segment-survey.md\n",
    "zigux/tests/README.md": "# zigux/tests\n- `scripts/zigux/check-phase8-libbpf-segment-gate.py`\n- `zigux/tests/phase8_libbpf_segments_only_build.zig`\n",
    "zigux/Makefile": "\n".join(
        (
            "phase8-validate:",
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase8.py",
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase8-libbpf-segment-gate.py --self-test",
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase8-libbpf-segment-gate.py",
            "",
            "phase8-libbpf-segments-test:",
            "\tcd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/phase8_libbpf_segments_only_build.zig --summary all",
            "",
        )
    ),
    BUILD_PATH: "\n".join(
        (
            'const std = @import("std");',
            "",
            "pub fn build(b: *std.Build) void {",
            "    const target = b.standardTargetOptions(.{});",
            "    const optimize = b.standardOptimizeOption(.{});",
            "    const libbpf_segment_verify_module = b.createModule(.{",
            '        .root_source_file = b.path("../../tools/lib/bpf/zigux_segments/verify.zig"),',
            "        .target = target,",
            "        .optimize = optimize,",
            "    });",
            "    const libbpf_segment_verify_tests = b.addTest(.{",
            '        .name = "phase8-libbpf-segment-verify-tests",',
            "        .root_module = libbpf_segment_verify_module,",
            "    });",
            "    const run_libbpf_segment_verify_tests = b.addRunArtifact(libbpf_segment_verify_tests);",
            '    const test_step = b.step("test", "Run focused Phase 8 libbpf segment verify build");',
            "    test_step.dependOn(&run_libbpf_segment_verify_tests.step);",
            "}",
            "",
        )
    ),
    VERIFY_PATH: "\n".join(
        (
            "pub fn resolveNextOnlineCpuRouteCpuIndexReturnAtIndex() void {}",
            "pub fn resolveNextOnlineCpuRouteBufferFdAtIndex() void {}",
            "pub fn resolveReadyBufferFdLookupReturnAtAttempt() void {}",
            "",
        )
    ),
}


def build_fixture_manifest_text() -> str:
    segments = []
    for index, slug in enumerate(LANDED_SLUGS, start=1):
        segments.append(
            {
                "id": f"P8-L15-S{index:02d}",
                "slug": slug,
                "status": "starter_landed",
            }
        )
    for offset, slug in enumerate(DEFERRED_SLUGS, start=len(LANDED_SLUGS) + 1):
        status = "blocked_on_object_model" if slug == "skeleton-population" else "deferred_high_risk"
        segments.append(
            {
                "id": f"P8-L15-S{offset:02d}",
                "slug": slug,
                "status": status,
            }
        )
    return json.dumps(
        {
            "lane_key": "P8-L15",
            "phase": "Phase 8",
            "surveyed_commit": "089188c96b86c0da16088e916094a7c977d0cfc6",
            "anchor": "tools/lib/bpf/libbpf.c",
            "segments": segments,
        },
        indent=2,
    ) + "\n"


def build_fixture_survey_text() -> str:
    return "\n".join(
        (
            "# Phase 8 Libbpf Segment Survey",
            "",
            "- survey checkpoint: refreshed against inspected current `master` readback on 2026-05-20",
            f"- {count_marker(12)}: seven landed helper or helper-adjacent slices and five deferred or blocked follow-ons.",
            "",
            SURVEY_MARKERS[0],
            "",
            f"The seven landed bounded slices are {oxford_backtick_list(LANDED_SLUGS)}.",
            "",
            SURVEY_MARKERS[1],
            "",
            SURVEY_MARKERS[2],
            "",
        )
    )


def clone_fixture_root(destination_root: Path) -> None:
    for rel_path, text in FIXTURE_TEXT.items():
        target = destination_root / rel_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")

    (destination_root / SURVEY_PATH).parent.mkdir(parents=True, exist_ok=True)
    (destination_root / SURVEY_PATH).write_text(build_fixture_survey_text(), encoding="utf-8")

    (destination_root / MANIFEST_PATH).parent.mkdir(parents=True, exist_ok=True)
    (destination_root / MANIFEST_PATH).write_text(build_fixture_manifest_text(), encoding="utf-8")

    checker_path = destination_root / "scripts/zigux/check-phase8-libbpf-segment-gate.py"
    checker_path.parent.mkdir(parents=True, exist_ok=True)
    checker_path.write_text(Path(__file__).read_text(encoding="utf-8"), encoding="utf-8")


def expect_missing_marker(label: str, root: Path, expected_marker: str) -> None:
    missing_files, missing_markers, consistency_errors = validate(root)
    if missing_files:
        raise SystemExit(f"{label}:unexpected_missing_files:{','.join(missing_files)}")
    if consistency_errors:
        raise SystemExit(f"{label}:unexpected_consistency_errors:{','.join(consistency_errors)}")
    if expected_marker not in missing_markers:
        actual = ",".join(missing_markers) if missing_markers else "none"
        raise SystemExit(f"{label}:expected_missing_marker:{expected_marker}:actual:{actual}")


def expect_consistency_error(label: str, root: Path, expected_prefix: str) -> None:
    missing_files, missing_markers, consistency_errors = validate(root)
    if missing_files or missing_markers:
        raise SystemExit(
            f"{label}:unexpected_file_or_marker_failure:files={','.join(missing_files) if missing_files else 'none'}:markers={','.join(missing_markers) if missing_markers else 'none'}"
        )
    if not any(error.startswith(expected_prefix) for error in consistency_errors):
        actual = ",".join(consistency_errors) if consistency_errors else "none"
        raise SystemExit(f"{label}:expected_consistency_error:{expected_prefix}:actual:{actual}")


def expect_missing_file(label: str, root: Path, expected_file: str) -> None:
    missing_files, missing_markers, consistency_errors = validate(root)
    if missing_markers or consistency_errors:
        raise SystemExit(
            f"{label}:unexpected_marker_or_consistency_failure:markers={','.join(missing_markers) if missing_markers else 'none'}:consistency={','.join(consistency_errors) if consistency_errors else 'none'}"
        )
    if expected_file not in missing_files:
        actual = ",".join(missing_files) if missing_files else "none"
        raise SystemExit(f"{label}:expected_missing_file:{expected_file}:actual:{actual}")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase8_libbpf_segment_gate_") as tmp_dir:
        tmp_root = Path(tmp_dir)
        clone_fixture_root(tmp_root)

        missing_files, missing_markers, consistency_errors = validate(tmp_root)
        if missing_files or missing_markers or consistency_errors:
            raise SystemExit(
                "phase8-libbpf-segment-gate-self-test:baseline_failed:"
                f"files={','.join(missing_files) if missing_files else 'none'}:"
                f"markers={','.join(missing_markers) if missing_markers else 'none'}:"
                f"consistency={','.join(consistency_errors) if consistency_errors else 'none'}"
            )

        survey_path = tmp_root / SURVEY_PATH
        original_survey = survey_path.read_text(encoding="utf-8")
        survey_path.writeText = None
        survey_path.write_text(original_survey.replace(count_marker(12), count_marker(11), 1), encoding="utf-8")
        expect_missing_marker("survey_count_marker", tmp_root, f"{SURVEY_PATH}:{count_marker(12)}")
        survey_path.write_text(original_survey, encoding="utf-8")

        landed_marker = f"The seven landed bounded slices are {oxford_backtick_list(LANDED_SLUGS)}."
        survey_path.write_text(original_survey.replace(landed_marker, "The landed slices remain reviewable.", 1), encoding="utf-8")
        expect_missing_marker("survey_landed_marker", tmp_root, f"{SURVEY_PATH}:{landed_marker}")
        survey_path.write_text(original_survey, encoding="utf-8")

        build_path = tmp_root / BUILD_PATH
        original_build = build_path.read_text(encoding="utf-8")
        build_path.write_text(original_build.replace("phase8-libbpf-segment-verify-tests", "phase8-libbpf-tests", 1), encoding="utf-8")
        expect_missing_marker(
            "build_verify_artifact_name",
            tmp_root,
            f"{BUILD_PATH}:phase8-libbpf-segment-verify-tests",
        )
        build_path.write_text(original_build, encoding="utf-8")

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
            "makefile_checker_self_test_hook",
            tmp_root,
            "zigux/Makefile:scripts/zigux/check-phase8-libbpf-segment-gate.py --self-test",
        )
        makefile_path.write_text(original_makefile, encoding="utf-8")

        verify_path = tmp_root / VERIFY_PATH
        original_verify = verify_path.read_text(encoding="utf-8")
        verify_path.write_text(
            original_verify.replace("resolveReadyBufferFdLookupReturnAtAttempt", "resolveReadyBufferLookupReturn", 1),
            encoding="utf-8",
        )
        expect_missing_marker(
            "verify_lookup_marker",
            tmp_root,
            f"{VERIFY_PATH}:resolveReadyBufferFdLookupReturnAtAttempt",
        )
        verify_path.write_text(original_verify, encoding="utf-8")

        manifest_path = tmp_root / MANIFEST_PATH
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["segments"][4]["status"] = "ready_next"
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        expect_consistency_error("manifest_landed_status", tmp_root, "manifest:unexpected_landed_slugs:")
        manifest_path.write_text(build_fixture_manifest_text(), encoding="utf-8")

        verify_path.unlink()
        expect_missing_file("verify_file_presence", tmp_root, VERIFY_PATH)
        verify_path.write_text(original_verify, encoding="utf-8")

    print("PHASE8_LIBBPF_SEGMENT_GATE_SELF_TEST=pass")
    print("PHASE8_LIBBPF_SEGMENT_GATE_SELF_TEST_CASE_COUNT=6")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate that the focused Phase 8 libbpf segment gate still matches the current helper-first verify packet."
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run built-in drift checks against a compact synthetic Phase 8 fixture tree.",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    missing_files, missing_markers, consistency_errors = validate(ROOT)
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
    if consistency_errors:
        print("PHASE8_LIBBPF_SEGMENT_GATE=fail")
        print("MISMATCHED_PHASE8_LIBBPF_SEGMENT_GATE_STATE_START")
        for item in consistency_errors:
            print(item)
        print("MISMATCHED_PHASE8_LIBBPF_SEGMENT_GATE_STATE_END")
        return 1

    print("PHASE8_LIBBPF_SEGMENT_GATE=pass")
    print(f"PHASE8_LIBBPF_SEGMENT_GATE_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(
        "PHASE8_LIBBPF_SEGMENT_GATE_REQUIRED_MARKER_COUNT="
        f"{len(SURVEY_MARKERS) + len(MAKEFILE_MARKERS) + len(BUILD_MARKERS) + len(VERIFY_MARKERS) + 2}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
