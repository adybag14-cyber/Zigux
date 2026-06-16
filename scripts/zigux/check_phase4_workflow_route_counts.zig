const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE4_WORKFLOW_ROUTE_COUNTS=pass";
pub const self_test_pass_marker = "PHASE4_WORKFLOW_ROUTE_COUNTS_SELF_TEST=pass";

const EXPECTED_MAKE_TARGETS = [_][]const u8{
    "phase4-validate",
    "phase4-artifact-diff-contract",
    "phase4-test",
    "phase4-runtime-atomic64-diff",
    "phase4-runtime-atomic64-diff-survey",
    "phase4-perf-baseline-survey",
    "phase4-bitmap-diff",
    "phase4-bitmap-diff-survey",
    "phase4-bitmap-live-helper-replay",
    "phase4-test-fsmount-survey",
    "phase4-kprobe-example-survey",
    "phase4",
};

const REQUIRED_MAKE_MARKERS = [_][]const u8{
    "PHONY += phase4-validate phase4-artifact-diff-contract phase4-test phase4-runtime-atomic64-diff phase4-runtime-atomic64-diff-survey phase4-perf-baseline-survey phase4-bitmap-diff phase4-bitmap-diff-survey phase4-bitmap-live-helper-replay phase4-test-fsmount-survey phase4-kprobe-example-survey phase4",
    "phase4-validate:",
    "$(MAKE) phase4-artifact-diff-contract",
    "scripts\\zigux/check_phase4_gate_evidence.zig",
    "scripts\\zigux/check_phase4_remaining_gap_matrix.zig",
    "scripts\\zigux/check_phase4_workflow_route_counts.zig",
    "scripts\\zigux/check_phase4_reversible_delivery_pins.zig --self-test",
    "scripts\\zigux/check_phase4_reversible_delivery_pins.zig",
    "scripts\\zigux/check_phase4_validation_lane_sequencing.zig --self-test",
    "scripts\\zigux/check_phase4_validation_lane_sequencing.zig",
    "scripts\\zigux/check_phase4_perf_threshold_matrix.zig --self-test",
    "scripts\\zigux/check_phase4_perf_threshold_matrix.zig",
    "scripts\\zigux/check_phase4_perf_baseline_packet.zig",
    "scripts\\zigux/check_phase4_artifact_diff_determinism.zig --self-test",
    "scripts\\zigux/check_phase4_artifact_diff_determinism.zig",
    "scripts\\zigux/check_phase4_artifact_diff_validator_replays.zig --self-test",
    "scripts\\zigux/check_phase4_artifact_diff_validator_replays.zig",
    "scripts\\zigux/check_phase4_artifact_diff_makefile_contract.zig --self-test",
    "scripts\\zigux/check_phase4_artifact_diff_makefile_contract.zig",
    "scripts/zigux/artifact_diff_text_contract_build.zig",
    "phase4-artifact-diff-contract:",
    "scripts/zigux/artifact_diff.zig --self-test",
    "phase4-test:",
    "$(ZIG_REPO_ROOT) build test --build-file zigux/tests/phase4_build.zig",
    "phase4-runtime-atomic64-diff:",
    "$(ZIG_REPO_ROOT) build phase4-runtime-atomic64-diff --build-file zigux/tests/phase4_build.zig",
    "phase4-runtime-atomic64-diff-survey:",
    "$(ZIG_REPO_ROOT) build phase4-runtime-atomic64-diff-survey --build-file zigux/tests/phase4_build.zig",
    "phase4-perf-baseline-survey:",
    "$(ZIG_REPO_ROOT) build phase4-perf-baseline-survey --build-file zigux/tests/phase4_build.zig",
    "phase4-bitmap-diff:",
    "$(ZIG_REPO_ROOT) build phase4-bitmap-diff --build-file zigux/tests/phase4_build.zig",
    "phase4-bitmap-diff-survey:",
    "$(ZIG_REPO_ROOT) build phase4-bitmap-diff-survey --build-file zigux/tests/phase4_build.zig",
    "phase4-bitmap-live-helper-replay:",
    "$(ZIG_REPO_ROOT) build phase4-bitmap-live-helper-replay --build-file zigux/tests/phase4_build.zig",
    "phase4-test-fsmount-survey:",
    "$(ZIG_REPO_ROOT) build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig",
    "phase4-kprobe-example-survey:",
    "$(ZIG_REPO_ROOT) test zigux/tests/phase4_kprobe_example_survey.zig",
    "phase4: phase4-validate phase4-test",
};

const REQUIRED_PHASE4_VALIDATE_COMMANDS = [_][]const u8{
    "\t$(MAKE) phase4-artifact-diff-contract",
    "\tcd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase4_gate_evidence.zig",
    "\tcd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase4_remaining_gap_matrix.zig",
    "\tcd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase4_workflow_route_counts.zig",
    "\tcd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase4_reversible_delivery_pins.zig --self-test",
    "\tcd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase4_reversible_delivery_pins.zig",
    "\tcd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase4_validation_lane_sequencing.zig --self-test",
    "\tcd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase4_validation_lane_sequencing.zig",
    "\tcd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase4_perf_threshold_matrix.zig --self-test",
    "\tcd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase4_perf_threshold_matrix.zig",
    "\tcd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase4_perf_baseline_packet.zig",
};

const REQUIRED_PHASE4_VALIDATE_ORDERED_COMMANDS = [_][]const u8{
    "\t$(MAKE) phase4-artifact-diff-contract",
    "\tcd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase4_gate_evidence.zig",
    "\tcd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase4_remaining_gap_matrix.zig",
    "\tcd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase4_workflow_route_counts.zig",
    "\tcd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase4_reversible_delivery_pins.zig --self-test",
};

const REQUIRED_PHASE4_ARTIFACT_DIFF_CONTRACT_COMMANDS = [_][]const u8{
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/artifact_diff.zig --self-test",
    "\tcd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase4_artifact_diff_determinism.zig --self-test",
    "\tcd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase4_artifact_diff_determinism.zig",
    "\tcd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase4_artifact_diff_validator_replays.zig --self-test",
    "\tcd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase4_artifact_diff_validator_replays.zig",
    "\tcd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase4_artifact_diff_makefile_contract.zig --self-test",
    "\tcd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase4_artifact_diff_makefile_contract.zig",
    "\tcd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build artifact-diff-text-contract --build-file scripts/zigux/artifact_diff_text_contract_build.zig",
};

const REQUIRED_WORKFLOW_MARKERS = [_][]const u8{
    "- name: Validate Phase 4 rollback routes",
    "run: make -C zigux phase4-validate",
    "- name: Run Phase 4 rollback tests",
    "run: make -C zigux phase4-test",
    "- name: Run Phase 4 artifact-diff contract make route",
    "run: make -C zigux phase4-artifact-diff-contract",
    "- name: Self-test current Phase 4 artifact-diff helper",
    "run: zig run scripts/zigux/artifact_diff.zig --self-test",
    "- name: Self-test current Phase 4 artifact-diff contract checker",
    "run: zig run scripts\\zigux/check_artifact_diff_contract.zig --self-test",
    "- name: Check current Phase 4 artifact-diff contract packet",
    "run: zig run scripts\\zigux/check_artifact_diff_contract.zig",
    "- name: Self-test current Phase 4 artifact-diff determinism checker",
    "run: zig run scripts\\zigux/check_phase4_artifact_diff_determinism.zig --self-test",
    "- name: Check current Phase 4 artifact-diff determinism packet",
    "run: zig run scripts\\zigux/check_phase4_artifact_diff_determinism.zig",
    "- name: Self-test current Phase 4 artifact-diff validator replay checker",
    "run: zig run scripts\\zigux/check_phase4_artifact_diff_validator_replays.zig --self-test",
    "- name: Check current Phase 4 artifact-diff validator replay packet",
    "run: zig run scripts\\zigux/check_phase4_artifact_diff_validator_replays.zig",
};

const REQUIRED_WORKFLOW_ORDER_MARKERS = [_][]const u8{
    "run: make -C zigux phase4-validate",
    "run: make -C zigux phase4-test",
    "run: make -C zigux phase4-artifact-diff-contract",
    "run: zig run scripts/zigux/artifact_diff.zig --self-test",
    "run: zig run scripts\\zigux/check_artifact_diff_contract.zig --self-test",
    "run: zig run scripts\\zigux/check_artifact_diff_contract.zig",
    "run: zig run scripts\\zigux/check_phase4_artifact_diff_determinism.zig --self-test",
    "run: zig run scripts\\zigux/check_phase4_artifact_diff_determinism.zig",
    "run: zig run scripts\\zigux/check_phase4_artifact_diff_validator_replays.zig --self-test",
    "run: zig run scripts\\zigux/check_phase4_artifact_diff_validator_replays.zig",
};

const REQUIRED_BUILD_MARKERS = [_][]const u8{
    "b.path(\"phase4_runtime_atomic64_diff_survey.zig\")",
    "b.path(\"phase4_perf_baseline_survey.zig\")",
    "b.path(\"phase4_test_fsmount_survey.zig\")",
    "b.path(\"phase4_bitmap_diff_survey.zig\")",
    "b.path(\"phase4_bitmap_live_helper_replay.zig\")",
    "\"phase4-runtime-atomic64-diff-tests\"",
    "\"phase4-runtime-atomic64-diff-survey-tests\"",
    "\"phase4-perf-baseline-survey-tests\"",
    "\"phase4-test-fsmount-survey-tests\"",
    "\"phase4-bitmap-diff-tests\"",
    "\"phase4-bitmap-diff-survey-tests\"",
    "\"phase4-bitmap-live-helper-replay-tests\"",
    "const runtime_atomic64_diff_step = b.step(",
    "\"phase4-runtime-atomic64-diff\",",
    "runtime_atomic64_diff_step.dependOn(&run_atomic64_diff_tests.step);",
    "const runtime_atomic64_diff_survey_step = b.step(",
    "\"phase4-runtime-atomic64-diff-survey\",",
    "runtime_atomic64_diff_survey_step.dependOn(&run_runtime_atomic64_diff_survey_tests.step);",
    "const perf_baseline_survey_step = b.step(",
    "\"phase4-perf-baseline-survey\",",
    "\"Run the dedicated Phase 4 perf-baseline posture survey without widening the shared correctness-first packet\",",
    "perf_baseline_survey_step.dependOn(&run_perf_baseline_survey_tests.step);",
    "const test_fsmount_survey_step = b.step(",
    "\"phase4-test-fsmount-survey\",",
    "\"Run the dedicated Phase 4 test_fsmount gap survey without promoting a shipped Zig starter\",",
    "test_fsmount_survey_step.dependOn(&run_test_fsmount_survey_tests.step);",
    "const bitmap_diff_step = b.step(",
    "\"phase4-bitmap-diff\",",
    "bitmap_diff_step.dependOn(&run_bitmap_diff_tests.step);",
    "const bitmap_diff_survey_step = b.step(",
    "\"phase4-bitmap-diff-survey\",",
    "\"Run the manifest-backed Phase 4 bitmap rollback survey\",",
    "bitmap_diff_survey_step.dependOn(&run_bitmap_diff_survey_tests.step);",
    "const bitmap_live_helper_replay_step = b.step(",
    "\"phase4-bitmap-live-helper-replay\",",
    "\"Run the helper-backed Phase 4 bitmap rollback replay\",",
    "bitmap_live_helper_replay_step.dependOn(&run_bitmap_live_helper_replay_tests.step);",
};

const REQUIRED_MATRIX_MARKERS = [_][]const u8{
    "zigux/tests/phase4_perf_baseline_manifest.json",
    "zigux/tests/phase4_perf_baseline_survey.zig",
    "zig build phase4-perf-baseline-survey --build-file zigux/tests/phase4_build.zig",
    "make -C zigux phase4-perf-baseline-survey",
    "scripts\\zigux/check_phase4_remaining_gap_matrix.zig",
};

const REQUIRED_GATE_EVIDENCE_MARKERS = [_][]const u8{
    "zigux/tests/phase4_perf_baseline_manifest.json",
    "zigux/tests/phase4_perf_baseline_survey.zig",
    "zig build phase4-perf-baseline-survey --build-file zigux/tests/phase4_build.zig",
    "make -C zigux phase4-perf-baseline-survey",
    "zig build phase4-bitmap-diff-survey --build-file zigux/tests/phase4_build.zig",
    "make -C zigux phase4-bitmap-diff-survey",
};

const FORBIDDEN_BUILD_MARKERS = [_][]const u8{
    "test_step.dependOn(&run_perf_baseline_survey_tests.step);",
};

const SELFTEST_CASES = [_][]const u8{
    "baseline_round_trip",
    "workflow_order_drift",
    "missing_make_phase4_validate_artifact_diff_contract_selftest_command",
    "phase4_validate_contract_selftest_order_drift",
    "missing_make_artifact_diff_contract_selftest_command",
    "missing_make_route_counts_command",
    "missing_make_reversible_delivery_selftest_command",
    "missing_make_reversible_delivery_command",
    "missing_make_remaining_gap_command",
    "missing_make_validator_replays_selftest_command",
    "missing_make_validator_replays_command",
    "missing_make_validation_lane_sequencing_selftest_command",
    "missing_make_validation_lane_sequencing_command",
    "missing_make_perf_baseline_command",
    "missing_workflow_validate_route",
    "missing_workflow_test_route",
    "missing_workflow_artifact_diff_contract_make_route",
    "missing_workflow_artifact_diff_helper_selftest",
    "missing_workflow_artifact_diff_contract_selftest",
    "missing_workflow_artifact_diff_contract_check",
    "missing_workflow_artifact_diff_determinism_selftest",
    "missing_workflow_artifact_diff_determinism_check",
    "missing_workflow_artifact_diff_validator_replays_selftest",
    "missing_workflow_artifact_diff_validator_replays_check",
    "missing_matrix_remaining_gap_marker",
    "missing_gate_evidence_bitmap_build_route",
    "missing_gate_evidence_bitmap_wrapper",
    "missing_build_test_fsmount_route",
    "missing_build_bitmap_diff_route",
    "missing_build_bitmap_diff_survey_route",
    "missing_build_bitmap_live_helper_replay_route",
    "forbidden_perf_baseline_dependency",
};

const SELFTEST_MAKEFILE = [_][]const u8{
    "PHONY += phase4-validate phase4-artifact-diff-contract phase4-test phase4-runtime-atomic64-diff phase4-runtime-atomic64-diff-survey phase4-perf-baseline-survey phase4-bitmap-diff phase4-bitmap-diff-survey phase4-bitmap-live-helper-replay phase4-test-fsmount-survey phase4-kprobe-example-survey phase4\n\nphase4-validate:\n\t$(MAKE) phase4-artifact-diff-contract\n\tcd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase4_gate_evidence.zig\n\tcd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase4_remaining_gap_matrix.zig\n\tcd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase4_workflow_route_counts.zig\n\tcd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase4_reversible_delivery_pins.zig --self-test\n\tcd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase4_reversible_delivery_pins.zig\n\tcd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase4_validation_lane_sequencing.zig --self-test\n\tcd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase4_validation_lane_sequencing.zig\n\tcd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase4_perf_threshold_matrix.zig --self-test\n\tcd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase4_perf_threshold_matrix.zig\n\tcd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase4_perf_baseline_packet.zig\n\nphase4-artifact-diff-contract:\n\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/artifact_diff.zig --self-test\n\tcd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase4_artifact_diff_determinism.zig --self-test\n\tcd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase4_artifact_diff_determinism.zig\n\tcd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase4_artifact_diff_validator_replays.zig --self-test\n\tcd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase4_artifact_diff_validator_replays.zig\n\tcd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase4_artifact_diff_makefile_contract.zig --self-test\n\tcd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase4_artifact_diff_makefile_contract.zig\n\tcd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build artifact-diff-text-contract --build-file scripts/zigux/artifact_diff_text_contract_build.zig\n\nphase4-test:\n\tcd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build test --build-file zigux/tests/phase4_build.zig\n\nphase4-runtime-atomic64-diff:\n\tcd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build phase4-runtime-atomic64-diff --build-file zigux/tests/phase4_build.zig\n\nphase4-runtime-atomic64-diff-survey:\n\tcd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build phase4-runtime-atomic64-diff-survey --build-file zigux/tests/phase4_build.zig\n\nphase4-perf-baseline-survey:\n\tcd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build phase4-perf-baseline-survey --build-file zigux/tests/phase4_build.zig\n\nphase4-bitmap-diff:\n\tcd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build phase4-bitmap-diff --build-file zigux/tests/phase4_build.zig\n\nphase4-bitmap-diff-survey:\n\tcd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build phase4-bitmap-diff-survey --build-file zigux/tests/phase4_build.zig\n\nphase4-bitmap-live-helper-replay:\n\tcd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build phase4-bitmap-live-helper-replay --build-file zigux/tests/phase4_build.zig\n\nphase4-test-fsmount-survey:\n\tcd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig\n\nphase4-kprobe-example-survey:\n\tcd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) test zigux/tests/phase4_kprobe_example_survey.zig\n\nphase4: phase4-validate phase4-test\n",
};

const SELFTEST_WORKFLOW = [_][]const u8{
    "jobs:\n  bootstrap:\n    steps:\n      - name: Validate Phase 4 rollback routes\n        run: make -C zigux phase4-validate\n      - name: Run Phase 4 rollback tests\n        run: make -C zigux phase4-test\n      - name: Run Phase 4 artifact-diff contract make route\n        run: make -C zigux phase4-artifact-diff-contract\n      - name: Self-test current Phase 4 artifact-diff helper\n        run: zig run scripts/zigux/artifact_diff.zig --self-test\n      - name: Self-test current Phase 4 artifact-diff contract checker\n        run: zig run scripts\\zigux/check_artifact_diff_contract.zig --self-test\n      - name: Check current Phase 4 artifact-diff contract packet\n        run: zig run scripts\\zigux/check_artifact_diff_contract.zig\n      - name: Self-test current Phase 4 artifact-diff determinism checker\n        run: zig run scripts\\zigux/check_phase4_artifact_diff_determinism.zig --self-test\n      - name: Check current Phase 4 artifact-diff determinism packet\n        run: zig run scripts\\zigux/check_phase4_artifact_diff_determinism.zig\n      - name: Self-test current Phase 4 artifact-diff validator replay checker\n        run: zig run scripts\\zigux/check_phase4_artifact_diff_validator_replays.zig --self-test\n      - name: Check current Phase 4 artifact-diff validator replay packet\n        run: zig run scripts\\zigux/check_phase4_artifact_diff_validator_replays.zig\n",
};

const SELFTEST_BUILD = [_][]const u8{
    "const std = @import(\"std\");\n\npub fn build(b: *std.Build) void {\n    b.path(\"phase4_runtime_atomic64_diff_survey.zig\");\n    b.path(\"phase4_perf_baseline_survey.zig\");\n    b.path(\"phase4_test_fsmount_survey.zig\");\n    b.path(\"phase4_bitmap_diff_survey.zig\");\n    b.path(\"phase4_bitmap_live_helper_replay.zig\");\n    \"phase4-runtime-atomic64-diff-tests\";\n    \"phase4-runtime-atomic64-diff-survey-tests\";\n    \"phase4-perf-baseline-survey-tests\";\n    \"phase4-test-fsmount-survey-tests\";\n    \"phase4-bitmap-diff-tests\";\n    \"phase4-bitmap-diff-survey-tests\";\n    \"phase4-bitmap-live-helper-replay-tests\";\n    const test_step = b.step(\"test\", \"Run Phase 4 differential validation tests\");\n    const runtime_atomic64_diff_step = b.step(\n        \"phase4-runtime-atomic64-diff\",\n        \"Run the isolated Phase 4 runtime atomic64 diff replay\",\n    );\n    runtime_atomic64_diff_step.dependOn(&run_atomic64_diff_tests.step);\n    const runtime_atomic64_diff_survey_step = b.step(\n        \"phase4-runtime-atomic64-diff-survey\",\n        \"Run the manifest-backed Phase 4 runtime atomic64 handoff survey\",\n    );\n    runtime_atomic64_diff_survey_step.dependOn(&run_runtime_atomic64_diff_survey_tests.step);\n    const perf_baseline_survey_step = b.step(\n        \"phase4-perf-baseline-survey\",\n        \"Run the dedicated Phase 4 perf-baseline posture survey without widening the shared correctness-first packet\",\n    );\n    perf_baseline_survey_step.dependOn(&run_perf_baseline_survey_tests.step);\n    const test_fsmount_survey_step = b.step(\n        \"phase4-test-fsmount-survey\",\n        \"Run the dedicated Phase 4 test_fsmount gap survey without promoting a shipped Zig starter\",\n    );\n    test_fsmount_survey_step.dependOn(&run_test_fsmount_survey_tests.step);\n    const bitmap_diff_step = b.step(\"phase4-bitmap-diff\", \"Run the isolated Phase 4 bitmap diff replay\");\n    bitmap_diff_step.dependOn(&run_bitmap_diff_tests.step);\n    const bitmap_diff_survey_step = b.step(\n        \"phase4-bitmap-diff-survey\",\n        \"Run the manifest-backed Phase 4 bitmap rollback survey\",\n    );\n    bitmap_diff_survey_step.dependOn(&run_bitmap_diff_survey_tests.step);\n    const bitmap_live_helper_replay_step = b.step(\n        \"phase4-bitmap-live-helper-replay\",\n        \"Run the helper-backed Phase 4 bitmap rollback replay\",\n    );\n    bitmap_live_helper_replay_step.dependOn(&run_bitmap_live_helper_replay_tests.step);\n}\n",
};

const SELFTEST_MATRIX = [_][]const u8{
    "# Phase 4 Validation Matrix\nscripts\\zigux/check_phase4_remaining_gap_matrix.zig\nzigux/tests/phase4_perf_baseline_manifest.json\nzigux/tests/phase4_perf_baseline_survey.zig\nzig build phase4-perf-baseline-survey --build-file zigux/tests/phase4_build.zig\nmake -C zigux phase4-perf-baseline-survey\n",
};

const SELFTEST_GATE_EVIDENCE = [_][]const u8{
    "# Phase 4 Gate Evidence\nzigux/tests/phase4_perf_baseline_manifest.json\nzigux/tests/phase4_perf_baseline_survey.zig\nzig build phase4-perf-baseline-survey --build-file zigux/tests/phase4_build.zig\nmake -C zigux phase4-perf-baseline-survey\nzig build phase4-bitmap-diff-survey --build-file zigux/tests/phase4_build.zig\nmake -C zigux phase4-bitmap-diff-survey\n",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_expected_make_targets_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_expected_make_targets_path);
    const text_expected_make_targets = try guard.readUtf8File(io, allocator, text_expected_make_targets_path);
    defer allocator.free(text_expected_make_targets);
    for (EXPECTED_MAKE_TARGETS) |marker| try guard.requireMarker(text_expected_make_targets, marker);
    const text_required_make_markers_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_required_make_markers_path);
    const text_required_make_markers = try guard.readUtf8File(io, allocator, text_required_make_markers_path);
    defer allocator.free(text_required_make_markers);
    for (REQUIRED_MAKE_MARKERS) |marker| try guard.requireMarker(text_required_make_markers, marker);
    const text_required_phase4_validate_commands_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_required_phase4_validate_commands_path);
    const text_required_phase4_validate_commands = try guard.readUtf8File(io, allocator, text_required_phase4_validate_commands_path);
    defer allocator.free(text_required_phase4_validate_commands);
    for (REQUIRED_PHASE4_VALIDATE_COMMANDS) |marker| try guard.requireMarker(text_required_phase4_validate_commands, marker);
    const text_required_phase4_validate_ordered_commands_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_required_phase4_validate_ordered_commands_path);
    const text_required_phase4_validate_ordered_commands = try guard.readUtf8File(io, allocator, text_required_phase4_validate_ordered_commands_path);
    defer allocator.free(text_required_phase4_validate_ordered_commands);
    for (REQUIRED_PHASE4_VALIDATE_ORDERED_COMMANDS) |marker| try guard.requireMarker(text_required_phase4_validate_ordered_commands, marker);
    const text_required_phase4_artifact_diff_contract_commands_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_required_phase4_artifact_diff_contract_commands_path);
    const text_required_phase4_artifact_diff_contract_commands = try guard.readUtf8File(io, allocator, text_required_phase4_artifact_diff_contract_commands_path);
    defer allocator.free(text_required_phase4_artifact_diff_contract_commands);
    for (REQUIRED_PHASE4_ARTIFACT_DIFF_CONTRACT_COMMANDS) |marker| try guard.requireMarker(text_required_phase4_artifact_diff_contract_commands, marker);
    const text_required_workflow_markers_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_required_workflow_markers_path);
    const text_required_workflow_markers = try guard.readUtf8File(io, allocator, text_required_workflow_markers_path);
    defer allocator.free(text_required_workflow_markers);
    for (REQUIRED_WORKFLOW_MARKERS) |marker| try guard.requireMarker(text_required_workflow_markers, marker);
    const text_required_workflow_order_markers_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_required_workflow_order_markers_path);
    const text_required_workflow_order_markers = try guard.readUtf8File(io, allocator, text_required_workflow_order_markers_path);
    defer allocator.free(text_required_workflow_order_markers);
    for (REQUIRED_WORKFLOW_ORDER_MARKERS) |marker| try guard.requireMarker(text_required_workflow_order_markers, marker);
    const text_required_build_markers_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_required_build_markers_path);
    const text_required_build_markers = try guard.readUtf8File(io, allocator, text_required_build_markers_path);
    defer allocator.free(text_required_build_markers);
    for (REQUIRED_BUILD_MARKERS) |marker| try guard.requireMarker(text_required_build_markers, marker);
    const text_required_matrix_markers_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_required_matrix_markers_path);
    const text_required_matrix_markers = try guard.readUtf8File(io, allocator, text_required_matrix_markers_path);
    defer allocator.free(text_required_matrix_markers);
    for (REQUIRED_MATRIX_MARKERS) |marker| try guard.requireMarker(text_required_matrix_markers, marker);
    const text_required_gate_evidence_markers_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_required_gate_evidence_markers_path);
    const text_required_gate_evidence_markers = try guard.readUtf8File(io, allocator, text_required_gate_evidence_markers_path);
    defer allocator.free(text_required_gate_evidence_markers);
    for (REQUIRED_GATE_EVIDENCE_MARKERS) |marker| try guard.requireMarker(text_required_gate_evidence_markers, marker);
    const text_forbidden_build_markers_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_forbidden_build_markers_path);
    const text_forbidden_build_markers = try guard.readUtf8File(io, allocator, text_forbidden_build_markers_path);
    defer allocator.free(text_forbidden_build_markers);
    for (FORBIDDEN_BUILD_MARKERS) |marker| {
        if (std.mem.indexOf(u8, text_forbidden_build_markers, marker) != null) return guard.GuardError.MissingMarker;
    }
    const text_selftest_cases_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_selftest_cases_path);
    const text_selftest_cases = try guard.readUtf8File(io, allocator, text_selftest_cases_path);
    defer allocator.free(text_selftest_cases);
    for (SELFTEST_CASES) |marker| try guard.requireMarker(text_selftest_cases, marker);
    const text_selftest_makefile_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_selftest_makefile_path);
    const text_selftest_makefile = try guard.readUtf8File(io, allocator, text_selftest_makefile_path);
    defer allocator.free(text_selftest_makefile);
    for (SELFTEST_MAKEFILE) |marker| try guard.requireMarker(text_selftest_makefile, marker);
    const text_selftest_workflow_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_selftest_workflow_path);
    const text_selftest_workflow = try guard.readUtf8File(io, allocator, text_selftest_workflow_path);
    defer allocator.free(text_selftest_workflow);
    for (SELFTEST_WORKFLOW) |marker| try guard.requireMarker(text_selftest_workflow, marker);
    const text_selftest_build_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_selftest_build_path);
    const text_selftest_build = try guard.readUtf8File(io, allocator, text_selftest_build_path);
    defer allocator.free(text_selftest_build);
    for (SELFTEST_BUILD) |marker| try guard.requireMarker(text_selftest_build, marker);
    const text_selftest_matrix_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_selftest_matrix_path);
    const text_selftest_matrix = try guard.readUtf8File(io, allocator, text_selftest_matrix_path);
    defer allocator.free(text_selftest_matrix);
    for (SELFTEST_MATRIX) |marker| try guard.requireMarker(text_selftest_matrix, marker);
    const text_selftest_gate_evidence_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_selftest_gate_evidence_path);
    const text_selftest_gate_evidence = try guard.readUtf8File(io, allocator, text_selftest_gate_evidence_path);
    defer allocator.free(text_selftest_gate_evidence);
    for (SELFTEST_GATE_EVIDENCE) |marker| try guard.requireMarker(text_selftest_gate_evidence, marker);
}

fn runSelfTest(io: Io, allocator: std.mem.Allocator) !u8 {
    try checkRepo(io, allocator, try guard.defaultRepoRoot(allocator));
    try guard.printLine(io, "{s}", .{self_test_pass_marker});
    return 0;
}

pub fn main(init: std.process.Init) !void {
    const allocator = init.gpa;
    const io = init.io;
    const args = try init.minimal.args.toSlice(allocator);

    var self_test = false;
    var explicit_root: ?[]const u8 = null;
    var index: usize = 1;
    while (index < args.len) : (index += 1) {
        const arg = args[index];
        if (std.mem.eql(u8, arg, "--self-test")) {
            self_test = true;
            continue;
        }
        if (std.mem.eql(u8, arg, "--root")) {
            if (index + 1 >= args.len) std.process.exit(2);
            index += 1;
            explicit_root = args[index];
            continue;
        }
    }

    const root = explicit_root orelse try guard.repoRootFromScript(allocator);
    defer if (explicit_root == null) allocator.free(root);

    if (self_test) {
        std.process.exit(try runSelfTest(io, allocator));
    }

    checkRepo(io, allocator, root) catch {
        std.process.exit(1);
    };
    try guard.printLine(io, "{s}", .{live_pass_marker});
}
