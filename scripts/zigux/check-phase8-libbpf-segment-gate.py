#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
MANIFEST_PATH = "tools/lib/bpf/zigux_segments/manifest.json"
SURVEY_PATH = "Documentation/zigux/phase8-libbpf-segment-survey.md"
REVIEW_CHECKLIST_PATH = "Documentation/zigux/review-checklist.md"
VALIDATOR_PATH = "scripts/zigux/validate-phase8.py"
BUILD_PATH = "zigux/tests/phase8_libbpf_segments_only_build.zig"
VERIFY_PATH = "tools/lib/bpf/zigux_segments/verify.zig"
MAKEFILE_PATH = "zigux/Makefile"
BRIDGE_TEST_PATH = "zigux/tests/phase8_file_path_handle_bridge.zig"
BRIDGE_BUILD_PATH = "zigux/tests/phase8_file_path_handle_bridge_only_build.zig"
BRIDGE_HELPER_PATH = "tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig"

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
REQUIRED_FILES = [
    ".github/workflows/zigux-bootstrap.yml",
    "Documentation/zigux/README.md",
    REVIEW_CHECKLIST_PATH,
    SURVEY_PATH,
    "scripts/zigux/README.md",
    VALIDATOR_PATH,
    "scripts/zigux/check-phase8-libbpf-segment-gate.py",
    MAKEFILE_PATH,
    "zigux/tests/README.md",
    BUILD_PATH,
    BRIDGE_TEST_PATH,
    BRIDGE_BUILD_PATH,
    MANIFEST_PATH,
    VERIFY_PATH,
    BRIDGE_HELPER_PATH,
]
SURVEY_MARKERS = [
    "The directly readable stable-output helper set therefore now keeps the aggregate verifier plus `cpu_mask.zig`, `cpu_mask_verify.zig`, `logging.zig`, `logging_verify.zig`, `pin_path.zig`, `pin_path_verify.zig`, `type_names.zig`, `type_names_verify.zig`, `perf_buffer_poll.zig`, `perf_buffer_poll_verify.zig`, `perf_buffer_ready_window.zig`, `online_cpu_routing.zig`, `online_cpu_routing_verify.zig`, `ready_buffer_attempt_verify.zig`, `ready_buffer_fd_verify.zig`, and `ready_buffer_window_verify.zig` explicit.",
    "Current repo-facing reminder surfaces already keep the bridge helper, the focused bridge build shard, the focused libbpf-segment shard, and the shared Phase 8 build replay explicit on `master`, while that same checker packet already keeps the landed `tools/lib/bpf/zigux_segments/logging_verify.zig`, `tools/lib/bpf/zigux_segments/perf_buffer_poll_verify.zig`, `tools/lib/bpf/zigux_segments/pin_path_verify.zig`, `tools/lib/bpf/zigux_segments/online_cpu_routing.zig` helper-local evidence, `tools/lib/bpf/zigux_segments/ready_buffer_attempt_verify.zig`, and `tools/lib/bpf/zigux_segments/type_names_verify.zig` explicit.",
    "This survey should therefore keep the helper-first packet and the shared wrapper-route vocabulary explicit together without promoting the still-deferred setup-side routing, reopen-flow, token-materialization, object-model, or bridge-heavy work into direct authenticated helper proof.",
]
VALIDATOR_MARKERS = [
    'LIBBPF_SEGMENT_GATE_CHECKER = Path("scripts/zigux/check-phase8-libbpf-segment-gate.py")',
    "LIBBPF_SEGMENT_GATE_CHECKER,",
]
MAKEFILE_MARKERS = [
    "phase8-validate:",
    "phase8-libbpf-segments-test:",
    "zigux/tests/phase8_libbpf_segments_only_build.zig --summary all",
]
BUILD_MARKERS = [
    "../../tools/lib/bpf/zigux_segments/verify.zig",
    "phase8-libbpf-segment-verify-tests",
    "Run focused Phase 8 libbpf segment verify build",
]
VERIFY_MARKERS = [
    "resolveNextOnlineCpuRouteCpuIndexReturnAtIndex",
    "resolveNextOnlineCpuRouteBufferFdAtIndex",
    "resolveReadyBufferFdLookupReturnAtAttempt",
]
BRIDGE_TEST_MARKERS = [
    'test "phase 8 file-path handle bridge proof keeps the manifest-backed helper and deferred bridge split explicit" {',
    "planning-only `resolveReusePinnedMapAttempt()` gating",
    "planning-only `planTokenPreparation()` gating",
    'try std.testing.expect(std.mem.indexOf(u8, helper_source, "bpf_obj_get(") == null);',
]
BRIDGE_BUILD_MARKERS = [
    "../../tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig",
    "phase8_file_path_handle_bridge.zig",
    "phase8-file-path-handle-bridge-tests",
    "Run focused Phase 8 file-path-handle bridge tests",
]
BRIDGE_HELPER_MARKERS = [
    "pub fn resolveReusePinnedMapAttempt(",
    "pub fn planTokenPreparation(",
]


def read_text(root: Path, rel_path: str) -> str:
    return (root / rel_path).read_text(encoding="utf-8")


def validate(root: Path) -> tuple[list[str], list[str], list[str]]:
    missing_files = [rel for rel in REQUIRED_FILES if not (root / rel).exists()]
    if missing_files:
        return missing_files, [], []

    missing_markers: list[str] = []
    state_errors: list[str] = []

    survey_text = read_text(root, SURVEY_PATH)
    for marker in SURVEY_MARKERS:
        if marker not in survey_text:
            missing_markers.append(f"{SURVEY_PATH}:{marker}")

    for rel_path, markers in {
        VALIDATOR_PATH: VALIDATOR_MARKERS,
        MAKEFILE_PATH: MAKEFILE_MARKERS,
        BUILD_PATH: BUILD_MARKERS,
        VERIFY_PATH: VERIFY_MARKERS,
        BRIDGE_TEST_PATH: BRIDGE_TEST_MARKERS,
        BRIDGE_BUILD_PATH: BRIDGE_BUILD_MARKERS,
        BRIDGE_HELPER_PATH: BRIDGE_HELPER_MARKERS,
    }.items():
        text = read_text(root, rel_path)
        for marker in markers:
            if marker not in text:
                missing_markers.append(f"{rel_path}:{marker}")

    try:
        manifest = json.loads(read_text(root, MANIFEST_PATH))
    except json.JSONDecodeError as exc:
        return [], missing_markers, [f"manifest:invalid_json:{exc.msg}"]

    if manifest.get("anchor") != "tools/lib/bpf/libbpf.c":
        state_errors.append("manifest:unexpected_anchor")

    segments = manifest.get("segments")
    if not isinstance(segments, list):
        return [], missing_markers, ["manifest:missing_or_invalid_segments"]

    landed = [segment.get("slug") for segment in segments if segment.get("status") == "starter_landed"]
    deferred = [
        segment.get("slug")
        for segment in segments
        if segment.get("status") in {"deferred_high_risk", "blocked_on_object_model"}
    ]
    if landed != LANDED_SLUGS:
        state_errors.append("manifest:unexpected_landed_slugs:" + ",".join(str(x) for x in landed))
    if deferred != DEFERRED_SLUGS:
        state_errors.append("manifest:unexpected_deferred_slugs:" + ",".join(str(x) for x in deferred))

    return [], missing_markers, state_errors


def fixture_manifest() -> str:
    segments = []
    for idx, slug in enumerate(LANDED_SLUGS, start=1):
        segments.append({"id": f"P8-L15-S{idx:02d}", "slug": slug, "status": "starter_landed"})
    for idx, slug in enumerate(DEFERRED_SLUGS, start=len(LANDED_SLUGS) + 1):
        status = "blocked_on_object_model" if slug == "skeleton-population" else "deferred_high_risk"
        segments.append({"id": f"P8-L15-S{idx:02d}", "slug": slug, "status": status})
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


def fixture_survey() -> str:
    return "\n".join(
        [
            "# Phase 8 Libbpf Segment Survey",
            "",
            "- survey checkpoint: refreshed against inspected current `master` readback on 2026-05-21",
            "",
            SURVEY_MARKERS[0],
            "",
            SURVEY_MARKERS[1],
            "",
            SURVEY_MARKERS[2],
            "",
        ]
    )


def write(root: Path, rel_path: str, text: str) -> None:
    path = root / rel_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def clone_fixture(root: Path) -> None:
    write(root, ".github/workflows/zigux-bootstrap.yml", "name: zigux-bootstrap\n- name: Validate Phase 8 tooling routes\n  run: make -C zigux phase8-validate\n")
    write(root, "Documentation/zigux/README.md", "# Zigux Documentation\n- `Documentation/zigux/phase8-libbpf-segment-survey.md`\n- `scripts/zigux/check-phase8-libbpf-segment-gate.py`\n")
    write(root, REVIEW_CHECKLIST_PATH, "# Zigux Review Checklist\n- `scripts/zigux/check-phase8-libbpf-segment-gate.py`\n- `scripts/zigux/validate-phase8.py`\n")
    write(root, "scripts/zigux/README.md", "# scripts/zigux\n- check-phase8-libbpf-segment-gate.py\n- Documentation/zigux/phase8-libbpf-segment-survey.md\n")
    write(
        root,
        VALIDATOR_PATH,
        "\n".join(
            (
                "#!/usr/bin/env python3",
                "from pathlib import Path",
                "",
                'LIBBPF_SEGMENT_GATE_CHECKER = Path("scripts/zigux/check-phase8-libbpf-segment-gate.py")',
                "",
                "CHECKERS = (",
                "    LIBBPF_SEGMENT_GATE_CHECKER,",
                ")",
                "",
                'print("PHASE8_VALIDATION=pass")',
                "",
            )
        ),
    )
    write(root, "zigux/tests/README.md", "# zigux/tests\n- `scripts/zigux/check-phase8-libbpf-segment-gate.py`\n- `zigux/tests/phase8_libbpf_segments_only_build.zig`\n")
    write(root, MAKEFILE_PATH, "phase8-validate:\n\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase8.py\n\nphase8-libbpf-segments-test:\n\tcd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/phase8_libbpf_segments_only_build.zig --summary all\n")
    write(root, BUILD_PATH, 'const std = @import("std");\n\npub fn build(b: *std.Build) void {\n    const target = b.standardTargetOptions(.{});\n    const optimize = b.standardOptimizeOption(.{});\n    const libbpf_segment_verify_module = b.createModule(.{\n        .root_source_file = b.path("../../tools/lib/bpf/zigux_segments/verify.zig"),\n        .target = target,\n        .optimize = optimize,\n    });\n    const libbpf_segment_verify_tests = b.addTest(.{\n        .name = "phase8-libbpf-segment-verify-tests",\n        .root_module = libbpf_segment_verify_module,\n    });\n    const run_libbpf_segment_verify_tests = b.addRunArtifact(libbpf_segment_verify_tests);\n    const test_step = b.step("test", "Run focused Phase 8 libbpf segment verify build");\n    test_step.dependOn(&run_libbpf_segment_verify_tests.step);\n}\n')
    write(root, BRIDGE_TEST_PATH, "\n".join(BRIDGE_TEST_MARKERS) + "\n")
    write(root, BRIDGE_BUILD_PATH, 'const std = @import("std");\n\npub fn build(b: *std.Build) void {\n    const target = b.standardTargetOptions(.{});\n    const optimize = b.standardOptimizeOption(.{});\n    const file_path_handle_bridge_module = b.createModule(.{\n        .root_source_file = b.path("../../tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig"),\n        .target = target,\n        .optimize = optimize,\n    });\n    const file_path_handle_bridge_root_module = b.createModule(.{\n        .root_source_file = b.path("phase8_file_path_handle_bridge.zig"),\n        .target = target,\n        .optimize = optimize,\n    });\n    file_path_handle_bridge_root_module.addImport("file_path_handle_bridge", file_path_handle_bridge_module);\n    const file_path_handle_bridge_tests = b.addTest(.{\n        .name = "phase8-file-path-handle-bridge-tests",\n        .root_module = file_path_handle_bridge_root_module,\n    });\n    const run_file_path_handle_bridge_tests = b.addRunArtifact(file_path_handle_bridge_tests);\n    const test_step = b.step("test", "Run focused Phase 8 file-path-handle bridge tests");\n    test_step.dependOn(&run_file_path_handle_bridge_tests.step);\n}\n')
    write(root, VERIFY_PATH, 'pub fn resolveNextOnlineCpuRouteCpuIndexReturnAtIndex() void {}\npub fn resolveNextOnlineCpuRouteBufferFdAtIndex() void {}\npub fn resolveReadyBufferFdLookupReturnAtAttempt() void {}\n')
    write(root, BRIDGE_HELPER_PATH, "\n".join(BRIDGE_HELPER_MARKERS) + "\n")
    write(root, MANIFEST_PATH, fixture_manifest())
    write(root, SURVEY_PATH, fixture_survey())
    write(root, "scripts/zigux/check-phase8-libbpf-segment-gate.py", Path(__file__).read_text(encoding="utf-8"))


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase8_libbpf_segment_gate_") as tmp_dir:
        root = Path(tmp_dir)
        clone_fixture(root)
        missing_files, missing_markers, state_errors = validate(root)
        if missing_files or missing_markers or state_errors:
            raise SystemExit("phase8-libbpf-segment-gate-self-test:baseline_failed")

        survey_path = root / SURVEY_PATH
        original_survey = survey_path.read_text(encoding="utf-8")
        survey_path.write_text(original_survey.replace("ready_buffer_attempt_verify.zig", "ready_buffer_attempt_review.zig", 1), encoding="utf-8")
        if f"{SURVEY_PATH}:{SURVEY_MARKERS[0]}" not in validate(root)[1]:
            raise SystemExit("phase8-libbpf-segment-gate-self-test:survey_marker")
        survey_path.write_text(original_survey, encoding="utf-8")

        validator_path = root / VALIDATOR_PATH
        original_validator = validator_path.read_text(encoding="utf-8")
        validator_path.write_text(
            original_validator.replace(
                'LIBBPF_SEGMENT_GATE_CHECKER = Path("scripts/zigux/check-phase8-libbpf-segment-gate.py")',
                'LIBBPF_SEGMENT_PROOF_CHECKER = Path("scripts/zigux/check-phase8-libbpf-segment-gate.py")',
                1,
            ),
            encoding="utf-8",
        )
        if f"{VALIDATOR_PATH}:{VALIDATOR_MARKERS[0]}" not in validate(root)[1]:
            raise SystemExit("phase8-libbpf-segment-gate-self-test:validator_marker")
        validator_path.write_text(original_validator, encoding="utf-8")

        build_path = root / BUILD_PATH
        original_build = build_path.read_text(encoding="utf-8")
        build_path.write_text(original_build.replace("phase8-libbpf-segment-verify-tests", "phase8-libbpf-tests", 1), encoding="utf-8")
        if f"{BUILD_PATH}:phase8-libbpf-segment-verify-tests" not in validate(root)[1]:
            raise SystemExit("phase8-libbpf-segment-gate-self-test:build_marker")
        build_path.write_text(original_build, encoding="utf-8")

        makefile_path = root / MAKEFILE_PATH
        original_makefile = makefile_path.read_text(encoding="utf-8")
        makefile_path.write_text(original_makefile.replace("phase8-libbpf-segments-test:", "phase8-libbpf-test:", 1), encoding="utf-8")
        if f"{MAKEFILE_PATH}:phase8-libbpf-segments-test:" not in validate(root)[1]:
            raise SystemExit("phase8-libbpf-segment-gate-self-test:makefile_marker")
        makefile_path.write_text(original_makefile, encoding="utf-8")

        bridge_test_path = root / BRIDGE_TEST_PATH
        original_bridge_test = bridge_test_path.read_text(encoding="utf-8")
        bridge_test_path.write_text(
            original_bridge_test.replace(
                "planning-only `planTokenPreparation()` gating",
                "planning-only `planTokenScheduling()` gating",
                1,
            ),
            encoding="utf-8",
        )
        if f"{BRIDGE_TEST_PATH}:planning-only `planTokenPreparation()` gating" not in validate(root)[1]:
            raise SystemExit("phase8-libbpf-segment-gate-self-test:bridge_test_marker")
        bridge_test_path.write_text(original_bridge_test, encoding="utf-8")

        bridge_build_path = root / BRIDGE_BUILD_PATH
        original_bridge_build = bridge_build_path.read_text(encoding="utf-8")
        bridge_build_path.write_text(
            original_bridge_build.replace(
                "phase8-file-path-handle-bridge-tests",
                "phase8-file-path-handle-tests",
                1,
            ),
            encoding="utf-8",
        )
        if f"{BRIDGE_BUILD_PATH}:phase8-file-path-handle-bridge-tests" not in validate(root)[1]:
            raise SystemExit("phase8-libbpf-segment-gate-self-test:bridge_build_marker")
        bridge_build_path.write_text(original_bridge_build, encoding="utf-8")

        bridge_helper_path = root / BRIDGE_HELPER_PATH
        original_bridge_helper = bridge_helper_path.read_text(encoding="utf-8")
        bridge_helper_path.write_text(
            original_bridge_helper.replace(
                "pub fn planTokenPreparation(",
                "pub fn planTokenProvision(",
                1,
            ),
            encoding="utf-8",
        )
        if f"{BRIDGE_HELPER_PATH}:pub fn planTokenPreparation(" not in validate(root)[1]:
            raise SystemExit("phase8-libbpf-segment-gate-self-test:bridge_helper_marker")
        bridge_helper_path.write_text(original_bridge_helper, encoding="utf-8")

        manifest_path = root / MANIFEST_PATH
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["segments"][4]["status"] = "ready_next"
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        if not any(error.startswith("manifest:unexpected_landed_slugs:") for error in validate(root)[2]):
            raise SystemExit("phase8-libbpf-segment-gate-self-test:manifest_state")
        manifest_path.write_text(fixture_manifest(), encoding="utf-8")

    print("PHASE8_LIBBPF_SEGMENT_GATE_SELF_TEST=pass")
    print("PHASE8_LIBBPF_SEGMENT_GATE_SELF_TEST_CASE_COUNT=8")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate that the focused Phase 8 libbpf segment gate matches the current helper-first verify packet.")
    parser.add_argument("--self-test", action="store_true", help="Run built-in drift checks against a compact synthetic Phase 8 fixture tree.")
    args = parser.parse_args()
    if args.self_test:
        return run_self_test()
    missing_files, missing_markers, state_errors = validate(ROOT)
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
    if state_errors:
        print("PHASE8_LIBBPF_SEGMENT_GATE=fail")
        print("MISMATCHED_PHASE8_LIBBPF_SEGMENT_GATE_STATE_START")
        for item in state_errors:
            print(item)
        print("MISMATCHED_PHASE8_LIBBPF_SEGMENT_GATE_STATE_END")
        return 1
    print("PHASE8_LIBBPF_SEGMENT_GATE=pass")
    print(f"PHASE8_LIBBPF_SEGMENT_GATE_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(
        "PHASE8_LIBBPF_SEGMENT_GATE_REQUIRED_MARKER_COUNT="
        f"{len(SURVEY_MARKERS) + len(VALIDATOR_MARKERS) + len(MAKEFILE_MARKERS) + len(BUILD_MARKERS) + len(VERIFY_MARKERS) + len(BRIDGE_TEST_MARKERS) + len(BRIDGE_BUILD_MARKERS) + len(BRIDGE_HELPER_MARKERS)}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
