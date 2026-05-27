#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import tempfile

def _default_root() -> Path:
    resolved = Path(__file__).resolve()
    if len(resolved.parents) >= 3:
        return resolved.parents[2]
    return resolved.parent


ROOT = _default_root()
MANIFEST_PATH = "tools/lib/bpf/zigux_segments/manifest.json"
SURVEY_PATH = "Documentation/zigux/phase8-libbpf-segment-survey.md"
REVIEW_CHECKLIST_PATH = "Documentation/zigux/review-checklist.md"
BRIDGE_SLICE_PATH = "Documentation/zigux/phase8-file-path-handle-bridge-slice.md"
BRIDGE_BOUNDARY_SURVEY_PATH = "Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md"
VALIDATOR_PATH = "scripts/zigux/validate-phase8.py"
BUILD_PATH = "zigux/tests/phase8_libbpf_segments_only_build.zig"
LIBBPF_SEGMENTS_TEST_PATH = "zigux/tests/phase8_libbpf_segments.zig"
VERIFY_PATH = "tools/lib/bpf/zigux_segments/verify.zig"
MAKEFILE_PATH = "zigux/Makefile"
BRIDGE_TEST_PATH = "zigux/tests/phase8_file_path_handle_bridge.zig"
BRIDGE_BUILD_PATH = "zigux/tests/phase8_file_path_handle_bridge_only_build.zig"
BRIDGE_BOUNDARY_GUARD_PATH = "zigux/tests/phase8_file_path_handle_boundary_guard.zig"
BRIDGE_MANIFEST_SYNC_PATH = "zigux/tests/phase8_file_path_handle_bridge_manifest_sync.zig"
BRIDGE_HELPER_PATH = "tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig"
EXPECTED_LANE_KEY = "P8-L13"
EXPECTED_PHASE = "Phase 8"

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
    BRIDGE_SLICE_PATH,
    BRIDGE_BOUNDARY_SURVEY_PATH,
    SURVEY_PATH,
    "scripts/zigux/README.md",
    VALIDATOR_PATH,
    "scripts/zigux/check-phase8-libbpf-segment-gate.py",
    MAKEFILE_PATH,
    "zigux/tests/README.md",
    BUILD_PATH,
    LIBBPF_SEGMENTS_TEST_PATH,
    BRIDGE_TEST_PATH,
    BRIDGE_BUILD_PATH,
    BRIDGE_BOUNDARY_GUARD_PATH,
    BRIDGE_MANIFEST_SYNC_PATH,
    MANIFEST_PATH,
    VERIFY_PATH,
    BRIDGE_HELPER_PATH,
]
SURVEY_MARKERS = [
    "The directly readable stable-output helper set therefore now keeps the aggregate verifier plus `cpu_mask.zig`, `cpu_mask_verify.zig`, `logging.zig`, `logging_verify.zig`, `pin_path.zig`, `pin_path_verify.zig`, `type_names.zig`, `type_names_verify.zig`, `perf_buffer_poll.zig`, `perf_buffer_wait_budget.zig`, `perf_buffer_poll_verify.zig`, `perf_buffer_ready_window.zig`, `online_cpu_routing.zig`, `online_cpu_routing_verify.zig`, `ready_buffer_attempt_verify.zig`, `ready_buffer_fd_verify.zig`, and `ready_buffer_window_verify.zig` explicit.",
    "Current repo-facing reminder surfaces already keep the bridge helper, the focused bridge build shard, the focused libbpf-segment shard, and the shared Phase 8 build replay explicit on `master`, while that same checker packet already keeps the landed `tools/lib/bpf/zigux_segments/logging_verify.zig`, `tools/lib/bpf/zigux_segments/perf_buffer_poll_verify.zig`, `tools/lib/bpf/zigux_segments/pin_path_verify.zig`, `tools/lib/bpf/zigux_segments/online_cpu_routing.zig` helper-local evidence, `tools/lib/bpf/zigux_segments/ready_buffer_attempt_verify.zig`, and `tools/lib/bpf/zigux_segments/type_names_verify.zig` explicit.",
    "The directly readable verifier packet now also keeps dedicated stable-output witnesses for cpu-mask parse, string-backed summary, reader-backed summary, auto-count, and fail-closed outputs, logging env/version/error outputs, perf-buffer wait-classification, poll-summary, execution-summary, and impossible-summary fail-closed outputs, pin-path map/program output and validation wrappers, online-CPU route CPU-index and buffer-FD wrappers, ready-buffer attempt wrappers, ready-buffer FD wrappers, ready-buffer window mapped-size and lookup-return wrappers, and type-name lookup plus formatter wrappers explicit beside the aggregate `verify.zig` replay surface.",
    "This survey should therefore keep the helper-first packet and the shared wrapper-route vocabulary explicit together without promoting the still-deferred setup-side routing, reopen-flow, token-materialization, object-model, or bridge-heavy work into direct authenticated helper proof.",
]
BRIDGE_SLICE_MARKERS = [
    "The shared file-path bridge destination already carries the bounded procfs path construction and fdinfo text parsing helpers, so this landed slice should stay explicitly smaller than direct file reads, descriptor ownership, or pinned-object reopen flow.",
    "The shared bridge surface now already carries the reused-map-name chooser and compatibility comparison as landed helper-only behavior, and it should stay reviewable without widening into FD duplication, close-on-replacement, or pinned-map reopen side effects.",
]
BRIDGE_BOUNDARY_SURVEY_MARKERS = [
    "Current `master` still keeps the mixed-source bridge packet reviewable, and authenticated contents readback now reaches the bridge-side helper and witness files directly again in this runtime.",
    "That narrower split is therefore packet role rather than fetchability: the bridge helper and witness stay on the boundary side of the Phase 8 packet so this survey does not overclaim delivered procfs, bpffs, token, or fd-ownership behavior.",
    "The timing-adjacent poll reminder also stays explicit through `Documentation/zigux/phase8-perf-buffer-poll-slice.md`, `python3 scripts/zigux/check-phase8-perf-buffer-poll-gate.py`, `make -C zigux phase8-perf-buffer-poll-test`, and the shared `phase8` routes; that dedicated packet keeps no standalone timer helper behavior, no standalone clockevent helper behavior, and no broader timeout-sensitive routing behavior explicit while the surrounding setup-side bridge remains deferred.",
]
VALIDATOR_MARKERS = [
    'LIBBPF_SEGMENT_GATE_CHECKER = Path("scripts/zigux/check-phase8-libbpf-segment-gate.py")',
    "LIBBPF_SEGMENT_GATE_CHECKER,",
]
MAKEFILE_MARKERS = [
    "phase8-validate:",
    "phase8-libbpf-segments-test:",
    "zigux/tests/phase8_libbpf_segments_only_build.zig --summary all",
    "phase8: phase8-validate phase8-exec-cmd-test phase8-help-test phase8-help-kallsyms-test phase8-kallsyms-test phase8-file-path-handle-bridge-test phase8-libbpf-segments-test phase8-perf-buffer-poll-test phase8-test",
]
BUILD_MARKERS = [
    "../../tools/lib/bpf/zigux_segments/verify.zig",
    "phase8-libbpf-segment-verify-tests",
    "Run focused Phase 8 libbpf segment verify build",
]
LIBBPF_SEGMENTS_TEST_MARKERS = [
    'test "phase 8 libbpf-segment compatibility witness keeps the focused verify-routing replay visible" {',
    'test "phase 8 libbpf-segment compatibility witness keeps the shared no-timer poll boundary explicit" {',
    'test "phase 8 libbpf-segment compatibility witness keeps the mixed-source bridge packet visible" {',
    'test "phase 8 libbpf-segment compatibility witness keeps stable-output verifier shards visible" {',
]
VERIFY_MARKERS = [
    "resolveNextOnlineCpuRouteCpuIndexReturnAtIndex",
    "resolveNextOnlineCpuRouteBufferFdAtIndex",
    "resolveNextOnlineCpuRouteBufferFdReturnAtIndex",
    "resolveReadyBufferFdAtAttempt",
    "resolveReadyBufferFdLookupReturnAtAttempt",
    "resolveReadyBufferWindowMappedSizeAtAttempt",
    "resolveReadyBufferWindowMappedSizeReturnAtAttempt",
    "resolveReadyBufferWindowLookupReturnAtAttempt",
    "formatLibbpfBpfLinkType",
]
BRIDGE_TEST_MARKERS = [
    'test "phase 8 file-path handle bridge proof keeps the manifest-backed helper and deferred bridge split explicit" {',
    'test "phase 8 file-path handle bridge helper stays wired into the Linux-style replay routes" {',
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
BRIDGE_BOUNDARY_GUARD_MARKERS = [
    'test "phase 8 file-path-handle boundary guard keeps landed helper slices distinct from the deferred bridge" {',
    '"slug": "fdinfo-map-info-helpers"',
    '"slug": "map-reuse-compatibility"',
    '"slug": "file-path-and-handle-bridge"',
    "planTokenPreparation",
]
BRIDGE_MANIFEST_SYNC_MARKERS = [
    'test "phase 8 file-path handle bridge manifest keeps the landed helper wording explicit" {',
    '"lane_key": "P8-L13"',
    '"id": "P8-L13-S07"',
    '"slug": "file-path-and-handle-bridge", "status": "deferred_high_risk", "kind": "resource_boundary"',
    "planning-only token-readiness gating as a reviewable landed helper slice",
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

    bridge_slice_text = read_text(root, BRIDGE_SLICE_PATH)
    for marker in BRIDGE_SLICE_MARKERS:
        if marker not in bridge_slice_text:
            missing_markers.append(f"{BRIDGE_SLICE_PATH}:{marker}")

    bridge_boundary_survey_text = read_text(root, BRIDGE_BOUNDARY_SURVEY_PATH)
    for marker in BRIDGE_BOUNDARY_SURVEY_MARKERS:
        if marker not in bridge_boundary_survey_text:
            missing_markers.append(f"{BRIDGE_BOUNDARY_SURVEY_PATH}:{marker}")

    for rel_path, markers in {
        VALIDATOR_PATH: VALIDATOR_MARKERS,
        MAKEFILE_PATH: MAKEFILE_MARKERS,
        BUILD_PATH: BUILD_MARKERS,
        LIBBPF_SEGMENTS_TEST_PATH: LIBBPF_SEGMENTS_TEST_MARKERS,
        VERIFY_PATH: VERIFY_MARKERS,
        BRIDGE_TEST_PATH: BRIDGE_TEST_MARKERS,
        BRIDGE_BUILD_PATH: BRIDGE_BUILD_MARKERS,
        BRIDGE_BOUNDARY_GUARD_PATH: BRIDGE_BOUNDARY_GUARD_MARKERS,
        BRIDGE_MANIFEST_SYNC_PATH: BRIDGE_MANIFEST_SYNC_MARKERS,
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

    if manifest.get("lane_key") != EXPECTED_LANE_KEY:
        state_errors.append(f"manifest:unexpected_lane_key:{manifest.get('lane_key')}")
    if manifest.get("phase") != EXPECTED_PHASE:
        state_errors.append(f"manifest:unexpected_phase:{manifest.get('phase')}")
    surveyed_commit = manifest.get("surveyed_commit")
    if not isinstance(surveyed_commit, str) or not surveyed_commit:
        state_errors.append("manifest:missing_or_invalid_surveyed_commit")
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
        segments.append({"id": f"P8-L13-S{idx:02d}", "slug": slug, "status": "starter_landed"})
    for idx, slug in enumerate(DEFERRED_SLUGS, start=len(LANDED_SLUGS) + 1):
        status = "blocked_on_object_model" if slug == "skeleton-population" else "deferred_high_risk"
        segments.append({"id": f"P8-L13-S{idx:02d}", "slug": slug, "status": status})
    return json.dumps(
        {
            "lane_key": EXPECTED_LANE_KEY,
            "phase": EXPECTED_PHASE,
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
            SURVEY_MARKERS[3],
            "",
        ]
    )

def fixture_bridge_slice() -> str:
    return "\n".join(
        [
            "# Phase 8 File-Path Handle Bridge Slice",
            "",
            BRIDGE_SLICE_MARKERS[0],
            "",
            BRIDGE_SLICE_MARKERS[1],
            "",
        ]
    )

def fixture_bridge_boundary_survey() -> str:
    return "\n".join(
        [
            "# Phase 8 Userspace-Kernel Bridge Boundary Survey",
            "",
            BRIDGE_BOUNDARY_SURVEY_MARKERS[0],
            "",
            BRIDGE_BOUNDARY_SURVEY_MARKERS[1],
            "",
            BRIDGE_BOUNDARY_SURVEY_MARKERS[2],
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
    write(root, BRIDGE_SLICE_PATH, fixture_bridge_slice())
    write(root, BRIDGE_BOUNDARY_SURVEY_PATH, fixture_bridge_boundary_survey())
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
    write(root, MAKEFILE_PATH, "phase8-validate:\n\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase8.py\n\nphase8-libbpf-segments-test:\n\tcd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/phase8_libbpf_segments_only_build.zig --summary all\n\nphase8: phase8-validate phase8-exec-cmd-test phase8-help-test phase8-help-kallsyms-test phase8-kallsyms-test phase8-file-path-handle-bridge-test phase8-libbpf-segments-test phase8-perf-buffer-poll-test phase8-test\n")
    write(root, BUILD_PATH, 'const std = @import("std");\n\npub fn build(b: *std.Build) void {\n    const target = b.standardTargetOptions(.{});\n    const optimize = b.standardOptimizeOption(.{});\n    const libbpf_segment_verify_module = b.createModule(.{\n        .root_source_file = b.path("../../tools/lib/bpf/zigux_segments/verify.zig"),\n        .target = target,\n        .optimize = optimize,\n    });\n    const libbpf_segment_verify_tests = b.addTest(.{\n        .name = "phase8-libbpf-segment-verify-tests",\n        .root_module = libbpf_segment_verify_module,\n    });\n    const run_libbpf_segment_verify_tests = b.addRunArtifact(libbpf_segment_verify_tests);\n    const test_step = b.step("test", "Run focused Phase 8 libbpf segment verify build");\n    test_step.dependOn(&run_libbpf_segment_verify_tests.step);\n}\n')
    write(root, LIBBPF_SEGMENTS_TEST_PATH, "\n".join(LIBBPF_SEGMENTS_TEST_MARKERS) + "\n")
    write(root, BRIDGE_TEST_PATH, "\n".join(BRIDGE_TEST_MARKERS) + "\n")
    write(root, BRIDGE_BUILD_PATH, 'const std = @import("std");\n\npub fn build(b: *std.Build) void {\n    const target = b.standardTargetOptions(.{});\n    const optimize = b.standardOptimizeOption(.{});\n    const file_path_handle_bridge_module = b.createModule(.{\n        .root_source_file = b.path("../../tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig"),\n        .target = target,\n        .optimize = optimize,\n    });\n    const file_path_handle_bridge_root_module = b.createModule(.{\n        .root_source_file = b.path("phase8_file_path_handle_bridge.zig"),\n        .target = target,\n        .optimize = optimize,\n    });\n    file_path_handle_bridge_root_module.addImport("file_path_handle_bridge", file_path_handle_bridge_module);\n    const file_path_handle_bridge_tests = b.addTest(.{\n        .name = "phase8-file-path-handle-bridge-tests",\n        .root_module = file_path_handle_bridge_root_module,\n    });\n    const run_file_path_handle_bridge_tests = b.addRunArtifact(file_path_handle_bridge_tests);\n    const test_step = b.step("test", "Run focused Phase 8 file-path-handle bridge tests");\n    test_step.dependOn(&run_file_path_handle_bridge_tests.step);\n}\n')
    write(root, BRIDGE_BOUNDARY_GUARD_PATH, "\n".join(BRIDGE_BOUNDARY_GUARD_MARKERS) + "\n")
    write(root, BRIDGE_MANIFEST_SYNC_PATH, "\n".join(BRIDGE_MANIFEST_SYNC_MARKERS) + "\n")
    write(root, VERIFY_PATH, 'pub fn resolveNextOnlineCpuRouteCpuIndexReturnAtIndex() void {}\npub fn resolveNextOnlineCpuRouteBufferFdAtIndex() void {}\npub fn resolveNextOnlineCpuRouteBufferFdReturnAtIndex() void {}\npub fn resolveReadyBufferFdAtAttempt() void {}\npub fn resolveReadyBufferFdLookupReturnAtAttempt() void {}\npub fn resolveReadyBufferWindowMappedSizeAtAttempt() void {}\npub fn resolveReadyBufferWindowMappedSizeReturnAtAttempt() void {}\npub fn resolveReadyBufferWindowLookupReturnAtAttempt() void {}\npub fn formatLibbpfBpfLinkType() void {}\n')
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

        manifest_path = root / MANIFEST_PATH
        original_manifest = manifest_path.read_text(encoding="utf-8")

        manifest = json.loads(original_manifest)
        manifest["lane_key"] = "P8-L15"
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        if "manifest:unexpected_lane_key:P8-L15" not in validate(root)[2]:
            raise SystemExit("phase8-libbpf-segment-gate-self-test:lane_key_state")
        manifest_path.write_text(original_manifest, encoding="utf-8")

        manifest = json.loads(original_manifest)
        manifest["phase"] = "Phase 12"
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        if "manifest:unexpected_phase:Phase 12" not in validate(root)[2]:
            raise SystemExit("phase8-libbpf-segment-gate-self-test:phase_state")
        manifest_path.write_text(original_manifest, encoding="utf-8")

        manifest = json.loads(original_manifest)
        manifest["surveyed_commit"] = ""
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        if "manifest:missing_or_invalid_surveyed_commit" not in validate(root)[2]:
            raise SystemExit("phase8-libbpf-segment-gate-self-test:surveyed_commit_state")
        manifest_path.write_text(original_manifest, encoding="utf-8")

        survey_path = root / SURVEY_PATH
        original_survey = survey_path.read_text(encoding="utf-8")
        survey_path.write_text(original_survey.replace("ready_buffer_attempt_verify.zig", "ready_buffer_attempt_review.zig", 1), encoding="utf-8")
        if f"{SURVEY_PATH}:{SURVEY_MARKERS[0]}" not in validate(root)[1]:
            raise SystemExit("phase8-libbpf-segment-gate-self-test:survey_marker")
        survey_path.write_text(original_survey, encoding="utf-8")

        survey_path.write_text(
            original_survey.replace(
                "focused libbpf-segment shard",
                "focused libbpf review shard",
                1,
            ),
            encoding="utf-8",
        )
        if f"{SURVEY_PATH}:{SURVEY_MARKERS[1]}" not in validate(root)[1]:
            raise SystemExit("phase8-libbpf-segment-gate-self-test:reminder_survey_marker")
        survey_path.write_text(original_survey, encoding="utf-8")

        survey_path.write_text(
            original_survey.replace(
                "ready-buffer FD wrappers",
                "ready-buffer handle wrappers",
                1,
            ),
            encoding="utf-8",
        )
        if f"{SURVEY_PATH}:{SURVEY_MARKERS[2]}" not in validate(root)[1]:
            raise SystemExit("phase8-libbpf-segment-gate-self-test:verifier_survey_marker")
        survey_path.write_text(original_survey, encoding="utf-8")

        bridge_slice_path = root / BRIDGE_SLICE_PATH
        original_bridge_slice = bridge_slice_path.read_text(encoding="utf-8")
        bridge_slice_path.write_text(
            original_bridge_slice.replace(
                "bounded procfs path construction and fdinfo text parsing helpers",
                "bounded procfs path shaping and fdinfo parsing helpers",
                1,
            ),
            encoding="utf-8",
        )
        if f"{BRIDGE_SLICE_PATH}:{BRIDGE_SLICE_MARKERS[0]}" not in validate(root)[1]:
            raise SystemExit("phase8-libbpf-segment-gate-self-test:bridge_slice_marker")
        bridge_slice_path.write_text(original_bridge_slice, encoding="utf-8")

        bridge_boundary_survey_path = root / BRIDGE_BOUNDARY_SURVEY_PATH
        original_bridge_boundary_survey = bridge_boundary_survey_path.read_text(encoding="utf-8")
        bridge_boundary_survey_path.write_text(
            original_bridge_boundary_survey.replace(
                "mixed-source bridge packet reviewable",
                "mixed-source bridge packet inspectable",
                1,
            ),
            encoding="utf-8",
        )
        if f"{BRIDGE_BOUNDARY_SURVEY_PATH}:{BRIDGE_BOUNDARY_SURVEY_MARKERS[0]}" not in validate(root)[1]:
            raise SystemExit("phase8-libbpf-segment-gate-self-test:bridge_boundary_survey_marker")
        bridge_boundary_survey_path.write_text(original_bridge_boundary_survey, encoding="utf-8")

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

        libbpf_segments_test_path = root / LIBBPF_SEGMENTS_TEST_PATH
        original_libbpf_segments_test = libbpf_segments_test_path.read_text(encoding="utf-8")
        libbpf_segments_test_path.write_text(
            original_libbpf_segments_test.replace(
                'test "phase 8 libbpf-segment compatibility witness keeps stable-output verifier shards visible" {',
                'test "phase 8 libbpf-segment compatibility witness keeps verifier shards visible" {',
                1,
            ),
            encoding="utf-8",
        )
        expected_libbpf_segments_test_marker = (
            f"{LIBBPF_SEGMENTS_TEST_PATH}:"
            'test "phase 8 libbpf-segment compatibility witness keeps stable-output verifier shards visible" {'
        )
        if expected_libbpf_segments_test_marker not in validate(root)[1]:
            raise SystemExit("phase8-libbpf-segment-gate-self-test:libbpf_segments_test_marker")
        libbpf_segments_test_path.write_text(original_libbpf_segments_test, encoding="utf-8")

        verify_path = root / VERIFY_PATH
        original_verify = verify_path.read_text(encoding="utf-8")
        verify_path.write_text(
            original_verify.replace(
                "resolveReadyBufferFdAtAttempt",
                "resolveReadyBufferFdAtIndex",
                1,
            ),
            encoding="utf-8",
        )
        if f"{VERIFY_PATH}:resolveReadyBufferFdAtAttempt" not in validate(root)[1]:
            raise SystemExit("phase8-libbpf-segment-gate-self-test:verify_fd_direct_marker")
        verify_path.write_text(original_verify, encoding="utf-8")

        verify_path.write_text(
            original_verify.replace(
                "resolveReadyBufferFdLookupReturnAtAttempt",
                "resolveReadyBufferFdLookupReturnAtIndex",
                1,
            ),
            encoding="utf-8",
        )
        if f"{VERIFY_PATH}:resolveReadyBufferFdLookupReturnAtAttempt" not in validate(root)[1]:
            raise SystemExit("phase8-libbpf-segment-gate-self-test:verify_fd_return_marker")
        verify_path.write_text(original_verify, encoding="utf-8")

        verify_path.write_text(
            original_verify.replace(
                "resolveReadyBufferWindowMappedSizeAtAttempt",
                "resolveReadyBufferWindowMappedSizeAtIndex",
                1,
            ),
            encoding="utf-8",
        )
        if f"{VERIFY_PATH}:resolveReadyBufferWindowMappedSizeAtAttempt" not in validate(root)[1]:
            raise SystemExit("phase8-libbpf-segment-gate-self-test:verify_window_size_direct_marker")
        verify_path.write_text(original_verify, encoding="utf-8")

        verify_path.write_text(
            original_verify.replace(
                "resolveReadyBufferWindowMappedSizeReturnAtAttempt",
                "resolveReadyBufferWindowMappedSizeReturnAtIndex",
                1,
            ),
            encoding="utf-8",
        )
        if f"{VERIFY_PATH}:resolveReadyBufferWindowMappedSizeReturnAtAttempt" not in validate(root)[1]:
            raise SystemExit("phase8-libbpf-segment-gate-self-test:verify_window_size_marker")
        verify_path.write_text(original_verify, encoding="utf-8")

        verify_path.write_text(
            original_verify.replace(
                "resolveReadyBufferWindowLookupReturnAtAttempt",
                "resolveReadyBufferWindowLookupReturnAtIndex",
                1,
            ),
            encoding="utf-8",
        )
        if f"{VERIFY_PATH}:resolveReadyBufferWindowLookupReturnAtAttempt" not in validate(root)[1]:
            raise SystemExit("phase8-libbpf-segment-gate-self-test:verify_window_lookup_marker")
        verify_path.write_text(original_verify, encoding="utf-8")

        verify_path.write_text(
            original_verify.replace(
                "formatLibbpfBpfLinkType",
                "formatLibbpfBpfLinkReview",
                1,
            ),
            encoding="utf-8",
        )
        if f"{VERIFY_PATH}:formatLibbpfBpfLinkType" not in validate(root)[1]:
            raise SystemExit("phase8-libbpf-segment-gate-self-test:verify_link_formatter_marker")
        verify_path.write_text(original_verify, encoding="utf-8")

        verify_path.write_text(
            original_verify.replace(
                "resolveNextOnlineCpuRouteBufferFdReturnAtIndex",
                "resolveNextOnlineCpuRouteBufferFdReturnMissing",
                1,
            ),
            encoding="utf-8",
        )
        if f"{VERIFY_PATH}:resolveNextOnlineCpuRouteBufferFdReturnAtIndex" not in validate(root)[1]:
            raise SystemExit("phase8-libbpf-segment-gate-self-test:verify_route_fd_return_marker")
        verify_path.write_text(original_verify, encoding="utf-8")

        makefile_path = root / MAKEFILE_PATH
        original_makefile = makefile_path.read_text(encoding="utf-8")
        makefile_path.write_text(original_makefile.replace("phase8-libbpf-segments-test:", "phase8-libbpf-test:", 1), encoding="utf-8")
        if f"{MAKEFILE_PATH}:phase8-libbpf-segments-test:" not in validate(root)[1]:
            raise SystemExit("phase8-libbpf-segment-gate-self-test:makefile_marker")
        makefile_path.write_text(original_makefile, encoding="utf-8")

        makefile_path.write_text(
            original_makefile.replace(
                "phase8: phase8-validate phase8-exec-cmd-test phase8-help-test phase8-help-kallsyms-test phase8-kallsyms-test phase8-file-path-handle-bridge-test phase8-libbpf-segments-test phase8-perf-buffer-poll-test phase8-test",
                "phase8: phase8-validate phase8-exec-cmd-test phase8-help-test phase8-help-kallsyms-test phase8-kallsyms-test phase8-file-path-handle-bridge-test phase8-libbpf-segments-test phase8-test",
                1,
            ),
            encoding="utf-8",
        )
        expected_phase8_aggregate_marker = (
            f"{MAKEFILE_PATH}:"
            "phase8: phase8-validate phase8-exec-cmd-test phase8-help-test phase8-help-kallsyms-test phase8-kallsyms-test phase8-file-path-handle-bridge-test phase8-libbpf-segments-test phase8-perf-buffer-poll-test phase8-test"
        )
        if expected_phase8_aggregate_marker not in validate(root)[1]:
            raise SystemExit("phase8-libbpf-segment-gate-self-test:phase8_aggregate_marker")
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

        bridge_test_path.write_text(
            original_bridge_test.replace(
                'test "phase 8 file-path handle bridge helper stays wired into the Linux-style replay routes" {',
                'test "phase 8 file-path handle bridge helper stays wired into the replay routes" {',
                1,
            ),
            encoding="utf-8",
        )
        expected_bridge_route_marker = (
            f"{BRIDGE_TEST_PATH}:"
            'test "phase 8 file-path handle bridge helper stays wired into the Linux-style replay routes" {'
        )
        if expected_bridge_route_marker not in validate(root)[1]:
            raise SystemExit("phase8-libbpf-segment-gate-self-test:bridge_route_marker")
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

        boundary_guard_path = root / BRIDGE_BOUNDARY_GUARD_PATH
        original_boundary_guard = boundary_guard_path.read_text(encoding="utf-8")
        boundary_guard_path.write_text(
            original_boundary_guard.replace(
                '"slug": "map-reuse-compatibility"',
                '"slug": "map-reuse-contract"',
                1,
            ),
            encoding="utf-8",
        )
        if f'{BRIDGE_BOUNDARY_GUARD_PATH}:"slug": "map-reuse-compatibility"' not in validate(root)[1]:
            raise SystemExit("phase8-libbpf-segment-gate-self-test:boundary_guard_marker")
        boundary_guard_path.write_text(original_boundary_guard, encoding="utf-8")

        manifest_sync_path = root / BRIDGE_MANIFEST_SYNC_PATH
        original_manifest_sync = manifest_sync_path.read_text(encoding="utf-8")
        manifest_sync_path.write_text(
            original_manifest_sync.replace(
                'test "phase 8 file-path handle bridge manifest keeps the landed helper wording explicit" {',
                'test "phase 8 file-path handle bridge manifest keeps the helper wording explicit" {',
                1,
            ),
            encoding="utf-8",
        )
        expected_manifest_sync_marker = (
            f"{BRIDGE_MANIFEST_SYNC_PATH}:"
            'test "phase 8 file-path handle bridge manifest keeps the landed helper wording explicit" {'
        )
        if expected_manifest_sync_marker not in validate(root)[1]:
            raise SystemExit("phase8-libbpf-segment-gate-self-test:manifest_sync_marker")
        manifest_sync_path.write_text(original_manifest_sync, encoding="utf-8")

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

        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["segments"][4]["status"] = "ready_next"
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        if not any(error.startswith("manifest:unexpected_landed_slugs:") for error in validate(root)[2]):
            raise SystemExit("phase8-libbpf-segment-gate-self-test:manifest_state")
        manifest_path.write_text(fixture_manifest(), encoding="utf-8")

    print("PHASE8_LIBBPF_SEGMENT_GATE_SELF_TEST=pass")
    print("PHASE8_LIBBPF_SEGMENT_GATE_SELF_TEST_CASE_COUNT=27")
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
        f"{len(SURVEY_MARKERS) + len(BRIDGE_SLICE_MARKERS) + len(BRIDGE_BOUNDARY_SURVEY_MARKERS) + len(VALIDATOR_MARKERS) + len(MAKEFILE_MARKERS) + len(BUILD_MARKERS) + len(LIBBPF_SEGMENTS_TEST_MARKERS) + len(VERIFY_MARKERS) + len(BRIDGE_TEST_MARKERS) + len(BRIDGE_BUILD_MARKERS) + len(BRIDGE_BOUNDARY_GUARD_MARKERS) + len(BRIDGE_MANIFEST_SYNC_MARKERS) + len(BRIDGE_HELPER_MARKERS)}"
    )
    return 0

if __name__ == "__main__":
    sys.exit(main())