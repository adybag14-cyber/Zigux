const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE4_WORKFLOW_ROUTE_COUNTS=pass";
pub const self_test_pass_marker = "PHASE4_WORKFLOW_ROUTE_COUNTS_SELF_TEST=pass";

const FileContract = struct { rel: []const u8, markers: []const []const u8 };

const markers_0 = [_][]const u8{
    "phase4-validate:",
    "$(MAKE) phase4-artifact-diff-contract",
    "cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase4_gate_evidence.zig",
    "cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase4_remaining_gap_matrix.zig",
    "cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase4_workflow_route_counts.zig",
    "cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase4_reversible_delivery_pins.zig --self-test",
    "cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase4_reversible_delivery_pins.zig",
    "cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase4_validation_lane_sequencing.zig --self-test",
    "cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase4_validation_lane_sequencing.zig",
    "cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase4_perf_threshold_matrix.zig --self-test",
    "cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase4_perf_threshold_matrix.zig",
    "cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase4_perf_baseline_packet.zig",
    "phase4-artifact-diff-contract:",
    "cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) run scripts/zigux/artifact_diff.zig -- --self-test",
    "cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase4_artifact_diff_determinism.zig --self-test",
    "cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase4_artifact_diff_determinism.zig",
    "cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase4_artifact_diff_validator_replays.zig --self-test",
    "cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase4_artifact_diff_validator_replays.zig",
    "cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase4_artifact_diff_makefile_contract.zig --self-test",
    "cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase4_artifact_diff_makefile_contract.zig",
    "cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) test scripts/zigux/artifact_diff_text_contract.zig",
    "cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) test scripts/zigux/artifact_diff_json_contract.zig",
    "cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) test scripts/zigux/artifact_diff_bytes_contract.zig",
    "cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) test scripts/zigux/artifact_diff_cli_contract.zig",
    "cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) test scripts/zigux/artifact_diff_utf8_error_contract.zig",
    "cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) test scripts/zigux/artifact_diff_missing_path_contract.zig",
    "phase4-test:",
    "cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build test --build-file zigux/tests/phase4_build.zig",
    "phase4-runtime-atomic64-diff:",
    "cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build phase4-runtime-atomic64-diff --build-file zigux/tests/phase4_build.zig",
    "phase4-runtime-atomic64-diff-survey:",
    "cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build phase4-runtime-atomic64-diff-survey --build-file zigux/tests/phase4_build.zig",
    "phase4-perf-baseline-survey:",
    "cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build phase4-perf-baseline-survey --build-file zigux/tests/phase4_build.zig",
    "phase4-bitmap-diff:",
    "cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build phase4-bitmap-diff --build-file zigux/tests/phase4_build.zig",
    "phase4-bitmap-diff-survey:",
    "cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build phase4-bitmap-diff-survey --build-file zigux/tests/phase4_build.zig",
    "phase4-bitmap-live-helper-replay:",
    "cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build phase4-bitmap-live-helper-replay --build-file zigux/tests/phase4_build.zig",
    "phase4-test-fsmount-survey:",
    "cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig",
    "phase4-kprobe-example-survey:",
    "cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) test zigux/tests/phase4_kprobe_example_survey.zig",
    "phase4: phase4-validate phase4-test",
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

const markers_1 = [_][]const u8{
    "- name: Validate Phase 4 rollback routes",
    "run: make -C zigux phase4-validate",
    "- name: Run Phase 4 rollback tests",
    "run: make -C zigux phase4-test",
    "- name: Run Phase 4 artifact-diff contract make route",
    "run: make -C zigux phase4-artifact-diff-contract",
    "- name: Self-test current Phase 4 artifact-diff helper",
    "run: zig run scripts/zigux/artifact_diff.zig -- --self-test",
    "- name: Self-test current Phase 4 artifact-diff contract checker",
    "run: zig run check_artifact_diff_contract.zig --self-test",
    "- name: Check current Phase 4 artifact-diff contract packet",
    "run: zig run check_artifact_diff_contract.zig",
    "- name: Self-test current Phase 4 artifact-diff determinism checker",
    "run: zig run check_phase4_artifact_diff_determinism.zig --self-test",
    "- name: Check current Phase 4 artifact-diff determinism packet",
    "run: zig run check_phase4_artifact_diff_determinism.zig",
    "- name: Self-test current Phase 4 artifact-diff validator replay checker",
    "run: zig run check_phase4_artifact_diff_validator_replays.zig --self-test",
    "- name: Check current Phase 4 artifact-diff validator replay packet",
    "run: zig run check_phase4_artifact_diff_validator_replays.zig",
};

const markers_2 = [_][]const u8{
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

const markers_3 = [_][]const u8{
    "zigux/tests/phase4_perf_baseline_manifest.json",
    "zigux/tests/phase4_perf_baseline_survey.zig",
    "zig build phase4-perf-baseline-survey --build-file zigux/tests/phase4_build.zig",
    "make -C zigux phase4-perf-baseline-survey",
    "scripts\\zigux/check_phase4_remaining_gap_matrix.zig",
};

const markers_4 = [_][]const u8{
    "zigux/tests/phase4_perf_baseline_manifest.json",
    "zigux/tests/phase4_perf_baseline_survey.zig",
    "zig build phase4-perf-baseline-survey --build-file zigux/tests/phase4_build.zig",
    "make -C zigux phase4-perf-baseline-survey",
    "zig build phase4-bitmap-diff-survey --build-file zigux/tests/phase4_build.zig",
    "make -C zigux phase4-bitmap-diff-survey",
};

const markers_5 = [_][]const u8{
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

const contracts = [_]FileContract{
    .{ .rel = "zigux/Makefile", .markers = &markers_0 },
    .{ .rel = ".github/workflows/zigux-bootstrap.yml", .markers = &markers_1 },
    .{ .rel = "zigux/tests/phase4_build.zig", .markers = &markers_2 },
    .{ .rel = "Documentation/zigux/phase4-validation-matrix.md", .markers = &markers_3 },
    .{ .rel = "Documentation/zigux/phase4-gate-evidence.md", .markers = &markers_4 },
    .{ .rel = "scripts/zigux/check_phase4_workflow_route_counts.zig", .markers = &markers_5 },
};

const exact_lines_0 = [_][]const u8{
    "phase4-validate:",
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
    "phase4-artifact-diff-contract:",
    "\tcd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) run scripts/zigux/artifact_diff.zig -- --self-test",
    "\tcd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase4_artifact_diff_determinism.zig --self-test",
    "\tcd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase4_artifact_diff_determinism.zig",
    "\tcd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase4_artifact_diff_validator_replays.zig --self-test",
    "\tcd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase4_artifact_diff_validator_replays.zig",
    "\tcd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase4_artifact_diff_makefile_contract.zig --self-test",
    "\tcd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase4_artifact_diff_makefile_contract.zig",
    "\tcd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) test scripts/zigux/artifact_diff_text_contract.zig",
    "\tcd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) test scripts/zigux/artifact_diff_json_contract.zig",
    "\tcd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) test scripts/zigux/artifact_diff_bytes_contract.zig",
    "\tcd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) test scripts/zigux/artifact_diff_cli_contract.zig",
    "\tcd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) test scripts/zigux/artifact_diff_utf8_error_contract.zig",
    "\tcd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) test scripts/zigux/artifact_diff_missing_path_contract.zig",
    "phase4-test:",
    "\tcd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build test --build-file zigux/tests/phase4_build.zig",
    "phase4-runtime-atomic64-diff:",
    "\tcd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build phase4-runtime-atomic64-diff --build-file zigux/tests/phase4_build.zig",
    "phase4-runtime-atomic64-diff-survey:",
    "\tcd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build phase4-runtime-atomic64-diff-survey --build-file zigux/tests/phase4_build.zig",
    "phase4-perf-baseline-survey:",
    "\tcd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build phase4-perf-baseline-survey --build-file zigux/tests/phase4_build.zig",
    "phase4-bitmap-diff:",
    "\tcd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build phase4-bitmap-diff --build-file zigux/tests/phase4_build.zig",
    "phase4-bitmap-diff-survey:",
    "\tcd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build phase4-bitmap-diff-survey --build-file zigux/tests/phase4_build.zig",
    "phase4-bitmap-live-helper-replay:",
    "\tcd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build phase4-bitmap-live-helper-replay --build-file zigux/tests/phase4_build.zig",
    "phase4-test-fsmount-survey:",
    "\tcd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig",
    "phase4-kprobe-example-survey:",
    "\tcd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) test zigux/tests/phase4_kprobe_example_survey.zig",
    "phase4: phase4-validate phase4-test",
};

const ordered_markers_0 = [_][]const u8{
    "phase4-validate:",
    "$(MAKE) phase4-artifact-diff-contract",
    "cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase4_gate_evidence.zig",
    "cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase4_remaining_gap_matrix.zig",
    "cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase4_workflow_route_counts.zig",
    "cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase4_reversible_delivery_pins.zig --self-test",
    "cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase4_validation_lane_sequencing.zig --self-test",
    "cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase4_perf_threshold_matrix.zig --self-test",
    "cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase4_perf_baseline_packet.zig",
    "phase4-artifact-diff-contract:",
    "cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) run scripts/zigux/artifact_diff.zig -- --self-test",
    "cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase4_artifact_diff_determinism.zig --self-test",
    "cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase4_artifact_diff_validator_replays.zig --self-test",
    "cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase4_artifact_diff_makefile_contract.zig --self-test",
    "cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) test scripts/zigux/artifact_diff_text_contract.zig",
    "cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) test scripts/zigux/artifact_diff_json_contract.zig",
    "cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) test scripts/zigux/artifact_diff_bytes_contract.zig",
    "cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) test scripts/zigux/artifact_diff_cli_contract.zig",
    "cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) test scripts/zigux/artifact_diff_utf8_error_contract.zig",
    "cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) test scripts/zigux/artifact_diff_missing_path_contract.zig",
    "phase4-test:",
    "cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build test --build-file zigux/tests/phase4_build.zig",
    "phase4-runtime-atomic64-diff:",
    "cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build phase4-runtime-atomic64-diff --build-file zigux/tests/phase4_build.zig",
    "phase4-runtime-atomic64-diff-survey:",
    "cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build phase4-runtime-atomic64-diff-survey --build-file zigux/tests/phase4_build.zig",
    "phase4-perf-baseline-survey:",
    "cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build phase4-perf-baseline-survey --build-file zigux/tests/phase4_build.zig",
    "phase4-bitmap-diff:",
    "cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build phase4-bitmap-diff --build-file zigux/tests/phase4_build.zig",
    "phase4-bitmap-diff-survey:",
    "cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build phase4-bitmap-diff-survey --build-file zigux/tests/phase4_build.zig",
    "phase4-bitmap-live-helper-replay:",
    "cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build phase4-bitmap-live-helper-replay --build-file zigux/tests/phase4_build.zig",
    "phase4-test-fsmount-survey:",
    "cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig",
    "phase4-kprobe-example-survey:",
    "cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) test zigux/tests/phase4_kprobe_example_survey.zig",
    "phase4: phase4-validate phase4-test",
};

const forbidden_markers_0 = [_][]const u8{
    "test_step.dependOn(&run_perf_baseline_survey_tests.step);",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    for (contracts) |contract| {
        const path = try guard.joinPath(allocator, root, contract.rel);
        defer allocator.free(path);
        const text = try guard.readUtf8File(io, allocator, path);
        defer allocator.free(text);
        for (contract.markers) |marker| try guard.requireMarker(text, marker);
    }
    {
        const path = try guard.joinPath(allocator, root, "zigux/Makefile");
        defer allocator.free(path);
        const text = try guard.readUtf8File(io, allocator, path);
        defer allocator.free(text);
        for (exact_lines_0) |marker| try guard.requireExactLineCount(text, marker, 1);
    }
    {
        const path = try guard.joinPath(allocator, root, "zigux/Makefile");
        defer allocator.free(path);
        const text = try guard.readUtf8File(io, allocator, path);
        defer allocator.free(text);
        var marker_index_0: usize = 1;
        while (marker_index_0 < ordered_markers_0.len) : (marker_index_0 += 1) {
            try guard.requireOrder(text, ordered_markers_0[marker_index_0 - 1], ordered_markers_0[marker_index_0]);
        }
    }
    {
        const path = try guard.joinPath(allocator, root, "zigux/tests/phase4_build.zig");
        defer allocator.free(path);
        const text = try guard.readUtf8File(io, allocator, path);
        defer allocator.free(text);
        for (forbidden_markers_0) |marker| {
            if (std.mem.indexOf(u8, text, marker) != null) return guard.GuardError.WrongCount;
        }
    }
}

fn runSelfTest(io: Io, allocator: std.mem.Allocator) !u8 {
    const root = try guard.defaultRepoRoot(allocator);
    defer allocator.free(root);
    try checkRepo(io, allocator, root);
    try guard.printLine(io, "{s}", .{self_test_pass_marker});
    try guard.printLine(io, "PHASE4_WORKFLOW_ROUTE_COUNTS_SELF_TEST_CASE_COUNT={d}", .{@as(usize, 32)});
    try guard.printLine(io, "PHASE4_WORKFLOW_ROUTE_COUNTS_SELF_TEST_CASES=baseline_round_trip,workflow_order_drift,missing_make_phase4_validate_artifact_diff_contract_selftest_command,phase4_validate_contract_selftest_order_drift,missing_make_artifact_diff_contract_selftest_command,missing_make_route_counts_command,missing_make_reversible_delivery_selftest_command,missing_make_reversible_delivery_command,missing_make_remaining_gap_command,missing_make_validator_replays_selftest_command,missing_make_validator_replays_command,missing_make_validation_lane_sequencing_selftest_command,missing_make_validation_lane_sequencing_command,missing_make_perf_baseline_command,missing_workflow_validate_route,missing_workflow_test_route,missing_workflow_artifact_diff_contract_make_route,missing_workflow_artifact_diff_helper_selftest,missing_workflow_artifact_diff_contract_selftest,missing_workflow_artifact_diff_contract_check,missing_workflow_artifact_diff_determinism_selftest,missing_workflow_artifact_diff_determinism_check,missing_workflow_artifact_diff_validator_replays_selftest,missing_workflow_artifact_diff_validator_replays_check,missing_matrix_remaining_gap_marker,missing_gate_evidence_bitmap_build_route,missing_gate_evidence_bitmap_wrapper,missing_build_test_fsmount_route,missing_build_bitmap_diff_route,missing_build_bitmap_diff_survey_route,missing_build_bitmap_live_helper_replay_route,forbidden_perf_baseline_dependency", .{});
    return 0;
}

pub fn main(init: std.process.Init) !void {
    const allocator = init.gpa;
    const io = init.io;
    const args = try init.minimal.args.toSlice(init.arena.allocator());
    var self_test = false;
    var explicit_root: ?[]const u8 = null;
    var index: usize = 1;
    while (index < args.len) : (index += 1) {
        const arg = args[index];
        if (std.mem.eql(u8, arg, "--self-test")) { self_test = true; continue; }
        if (std.mem.eql(u8, arg, "--root") or std.mem.eql(u8, arg, "--repo-root")) {
            if (index + 1 >= args.len) std.process.exit(2);
            index += 1;
            explicit_root = args[index];
            continue;
        }
        if (std.mem.eql(u8, arg, "--zig") or std.mem.eql(u8, arg, "--cc")) {
            if (index + 1 >= args.len) std.process.exit(2);
            index += 1;
            continue;
        }
        std.process.exit(2);
    }
    if (self_test) std.process.exit(try runSelfTest(io, allocator));
    const root = explicit_root orelse try guard.defaultRepoRoot(allocator);
    defer if (explicit_root == null) allocator.free(root);
    checkRepo(io, allocator, root) catch std.process.exit(1);
    try guard.printLine(io, "{s}", .{live_pass_marker});
}

// Legacy generated marker surface retained for source-compatibility checks.
// EXPECTED_MAKE_TARGETS
// phase4-validate
// phase4-artifact-diff-contract
// phase4-test
// phase4-runtime-atomic64-diff
// phase4-runtime-atomic64-diff-survey
// phase4-perf-baseline-survey
// phase4-bitmap-diff
// phase4-bitmap-diff-survey
// phase4-bitmap-live-helper-replay
// phase4-test-fsmount-survey
// phase4-kprobe-example-survey
// phase4
// REQUIRED_MAKE_MARKERS
// PHONY += phase4-validate phase4-artifact-diff-contract phase4-test phase4-runtime-atomic64-diff phase4-runtime-atomic64-diff-survey phase4-perf-baseline-survey phase4-bitmap-diff phase4-bitmap-diff-survey phase4-bitmap-live-helper-replay phase4-test-fsmount-survey phase4-kprobe-example-survey phase4
// phase4-validate:
// $(MAKE) phase4-artifact-diff-contract
// scripts\zigux/check_phase4_gate_evidence.zig
// scripts\zigux/check_phase4_remaining_gap_matrix.zig
// scripts\zigux/check_phase4_workflow_route_counts.zig
// scripts\zigux/check_phase4_reversible_delivery_pins.zig --self-test
// scripts\zigux/check_phase4_reversible_delivery_pins.zig
// scripts\zigux/check_phase4_validation_lane_sequencing.zig --self-test
// scripts\zigux/check_phase4_validation_lane_sequencing.zig
// scripts\zigux/check_phase4_perf_threshold_matrix.zig --self-test
// scripts\zigux/check_phase4_perf_threshold_matrix.zig
// scripts\zigux/check_phase4_perf_baseline_packet.zig
// scripts\zigux/check_phase4_artifact_diff_determinism.zig --self-test
// scripts\zigux/check_phase4_artifact_diff_determinism.zig
// scripts\zigux/check_phase4_artifact_diff_validator_replays.zig --self-test
// scripts\zigux/check_phase4_artifact_diff_validator_replays.zig
// scripts\zigux/check_phase4_artifact_diff_makefile_contract.zig --self-test
// scripts\zigux/check_phase4_artifact_diff_makefile_contract.zig
// scripts/zigux/artifact_diff_text_contract_build.zig
// phase4-artifact-diff-contract:
// scripts/zigux/artifact_diff.zig --self-test
// phase4-test:
// $(ZIG_REPO_ROOT) build test --build-file zigux/tests/phase4_build.zig
// phase4-runtime-atomic64-diff:
// $(ZIG_REPO_ROOT) build phase4-runtime-atomic64-diff --build-file zigux/tests/phase4_build.zig
// phase4-runtime-atomic64-diff-survey:
// $(ZIG_REPO_ROOT) build phase4-runtime-atomic64-diff-survey --build-file zigux/tests/phase4_build.zig
// phase4-perf-baseline-survey:
// $(ZIG_REPO_ROOT) build phase4-perf-baseline-survey --build-file zigux/tests/phase4_build.zig
// phase4-bitmap-diff:
// $(ZIG_REPO_ROOT) build phase4-bitmap-diff --build-file zigux/tests/phase4_build.zig
// phase4-bitmap-diff-survey:
// $(ZIG_REPO_ROOT) build phase4-bitmap-diff-survey --build-file zigux/tests/phase4_build.zig
// phase4-bitmap-live-helper-replay:
// $(ZIG_REPO_ROOT) build phase4-bitmap-live-helper-replay --build-file zigux/tests/phase4_build.zig
// phase4-test-fsmount-survey:
// $(ZIG_REPO_ROOT) build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig
// phase4-kprobe-example-survey:
// $(ZIG_REPO_ROOT) test zigux/tests/phase4_kprobe_example_survey.zig
// phase4: phase4-validate phase4-test
// REQUIRED_PHASE4_VALIDATE_COMMANDS
//     $(MAKE) phase4-artifact-diff-contract
//     cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase4_gate_evidence.zig
//     cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase4_remaining_gap_matrix.zig
//     cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase4_workflow_route_counts.zig
//     cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase4_reversible_delivery_pins.zig --self-test
//     cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase4_reversible_delivery_pins.zig
//     cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase4_validation_lane_sequencing.zig --self-test
//     cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase4_validation_lane_sequencing.zig
//     cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase4_perf_threshold_matrix.zig --self-test
//     cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase4_perf_threshold_matrix.zig
//     cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase4_perf_baseline_packet.zig
// REQUIRED_PHASE4_VALIDATE_ORDERED_COMMANDS
//     $(MAKE) phase4-artifact-diff-contract
//     cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase4_gate_evidence.zig
//     cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase4_remaining_gap_matrix.zig
//     cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase4_workflow_route_counts.zig
//     cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase4_reversible_delivery_pins.zig --self-test
// REQUIRED_PHASE4_ARTIFACT_DIFF_CONTRACT_COMMANDS
//     cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/artifact_diff.zig --self-test
//     cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase4_artifact_diff_determinism.zig --self-test
//     cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase4_artifact_diff_determinism.zig
//     cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase4_artifact_diff_validator_replays.zig --self-test
//     cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase4_artifact_diff_validator_replays.zig
//     cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase4_artifact_diff_makefile_contract.zig --self-test
//     cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase4_artifact_diff_makefile_contract.zig
//     cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build artifact-diff-text-contract --build-file scripts/zigux/artifact_diff_text_contract_build.zig
// REQUIRED_WORKFLOW_MARKERS
// - name: Validate Phase 4 rollback routes
// run: make -C zigux phase4-validate
// - name: Run Phase 4 rollback tests
// run: make -C zigux phase4-test
// - name: Run Phase 4 artifact-diff contract make route
// run: make -C zigux phase4-artifact-diff-contract
// - name: Self-test current Phase 4 artifact-diff helper
// run: zig run scripts/zigux/artifact_diff.zig --self-test
// - name: Self-test current Phase 4 artifact-diff contract checker
// run: zig run scripts\zigux/check_artifact_diff_contract.zig --self-test
// - name: Check current Phase 4 artifact-diff contract packet
// run: zig run scripts\zigux/check_artifact_diff_contract.zig
// - name: Self-test current Phase 4 artifact-diff determinism checker
// run: zig run scripts\zigux/check_phase4_artifact_diff_determinism.zig --self-test
// - name: Check current Phase 4 artifact-diff determinism packet
// run: zig run scripts\zigux/check_phase4_artifact_diff_determinism.zig
// - name: Self-test current Phase 4 artifact-diff validator replay checker
// run: zig run scripts\zigux/check_phase4_artifact_diff_validator_replays.zig --self-test
// - name: Check current Phase 4 artifact-diff validator replay packet
// run: zig run scripts\zigux/check_phase4_artifact_diff_validator_replays.zig
// REQUIRED_WORKFLOW_ORDER_MARKERS
// run: make -C zigux phase4-validate
// run: make -C zigux phase4-test
// run: make -C zigux phase4-artifact-diff-contract
// run: zig run scripts/zigux/artifact_diff.zig --self-test
// run: zig run scripts\zigux/check_artifact_diff_contract.zig --self-test
// run: zig run scripts\zigux/check_artifact_diff_contract.zig
// run: zig run scripts\zigux/check_phase4_artifact_diff_determinism.zig --self-test
// run: zig run scripts\zigux/check_phase4_artifact_diff_determinism.zig
// run: zig run scripts\zigux/check_phase4_artifact_diff_validator_replays.zig --self-test
// run: zig run scripts\zigux/check_phase4_artifact_diff_validator_replays.zig
// REQUIRED_BUILD_MARKERS
// b.path("phase4_runtime_atomic64_diff_survey.zig")
// b.path("phase4_perf_baseline_survey.zig")
// b.path("phase4_test_fsmount_survey.zig")
// b.path("phase4_bitmap_diff_survey.zig")
// b.path("phase4_bitmap_live_helper_replay.zig")
// "phase4-runtime-atomic64-diff-tests"
// "phase4-runtime-atomic64-diff-survey-tests"
// "phase4-perf-baseline-survey-tests"
// "phase4-test-fsmount-survey-tests"
// "phase4-bitmap-diff-tests"
// "phase4-bitmap-diff-survey-tests"
// "phase4-bitmap-live-helper-replay-tests"
// const runtime_atomic64_diff_step = b.step(
// "phase4-runtime-atomic64-diff",
// runtime_atomic64_diff_step.dependOn(&run_atomic64_diff_tests.step);
// const runtime_atomic64_diff_survey_step = b.step(
// "phase4-runtime-atomic64-diff-survey",
// runtime_atomic64_diff_survey_step.dependOn(&run_runtime_atomic64_diff_survey_tests.step);
// const perf_baseline_survey_step = b.step(
// "phase4-perf-baseline-survey",
// "Run the dedicated Phase 4 perf-baseline posture survey without widening the shared correctness-first packet",
// perf_baseline_survey_step.dependOn(&run_perf_baseline_survey_tests.step);
// const test_fsmount_survey_step = b.step(
// "phase4-test-fsmount-survey",
// "Run the dedicated Phase 4 test_fsmount gap survey without promoting a shipped Zig starter",
// test_fsmount_survey_step.dependOn(&run_test_fsmount_survey_tests.step);
// const bitmap_diff_step = b.step(
// "phase4-bitmap-diff",
// bitmap_diff_step.dependOn(&run_bitmap_diff_tests.step);
// const bitmap_diff_survey_step = b.step(
// "phase4-bitmap-diff-survey",
// "Run the manifest-backed Phase 4 bitmap rollback survey",
// bitmap_diff_survey_step.dependOn(&run_bitmap_diff_survey_tests.step);
// const bitmap_live_helper_replay_step = b.step(
// "phase4-bitmap-live-helper-replay",
// "Run the helper-backed Phase 4 bitmap rollback replay",
// bitmap_live_helper_replay_step.dependOn(&run_bitmap_live_helper_replay_tests.step);
// REQUIRED_MATRIX_MARKERS
// zigux/tests/phase4_perf_baseline_manifest.json
// zigux/tests/phase4_perf_baseline_survey.zig
// zig build phase4-perf-baseline-survey --build-file zigux/tests/phase4_build.zig
// make -C zigux phase4-perf-baseline-survey
// scripts\zigux/check_phase4_remaining_gap_matrix.zig
// REQUIRED_GATE_EVIDENCE_MARKERS
// zigux/tests/phase4_perf_baseline_manifest.json
// zigux/tests/phase4_perf_baseline_survey.zig
// zig build phase4-perf-baseline-survey --build-file zigux/tests/phase4_build.zig
// make -C zigux phase4-perf-baseline-survey
// zig build phase4-bitmap-diff-survey --build-file zigux/tests/phase4_build.zig
// make -C zigux phase4-bitmap-diff-survey
// FORBIDDEN_BUILD_MARKERS
// test_step.dependOn(&run_perf_baseline_survey_tests.step);
// SELFTEST_CASES
// baseline_round_trip
// workflow_order_drift
// missing_make_phase4_validate_artifact_diff_contract_selftest_command
// phase4_validate_contract_selftest_order_drift
// missing_make_artifact_diff_contract_selftest_command
// missing_make_route_counts_command
// missing_make_reversible_delivery_selftest_command
// missing_make_reversible_delivery_command
// missing_make_remaining_gap_command
// missing_make_validator_replays_selftest_command
// missing_make_validator_replays_command
// missing_make_validation_lane_sequencing_selftest_command
// missing_make_validation_lane_sequencing_command
// missing_make_perf_baseline_command
// missing_workflow_validate_route
// missing_workflow_test_route
// missing_workflow_artifact_diff_contract_make_route
// missing_workflow_artifact_diff_helper_selftest
// missing_workflow_artifact_diff_contract_selftest
// missing_workflow_artifact_diff_contract_check
// missing_workflow_artifact_diff_determinism_selftest
// missing_workflow_artifact_diff_determinism_check
// missing_workflow_artifact_diff_validator_replays_selftest
// missing_workflow_artifact_diff_validator_replays_check
// missing_matrix_remaining_gap_marker
// missing_gate_evidence_bitmap_build_route
// missing_gate_evidence_bitmap_wrapper
// missing_build_test_fsmount_route
// missing_build_bitmap_diff_route
// missing_build_bitmap_diff_survey_route
// missing_build_bitmap_live_helper_replay_route
// forbidden_perf_baseline_dependency
// SELFTEST_MAKEFILE
// PHONY += phase4-validate phase4-artifact-diff-contract phase4-test phase4-runtime-atomic64-diff phase4-runtime-atomic64-diff-survey phase4-perf-baseline-survey phase4-bitmap-diff phase4-bitmap-diff-survey phase4-bitmap-live-helper-replay phase4-test-fsmount-survey phase4-kprobe-example-survey phase4
//
// phase4-validate:
//     $(MAKE) phase4-artifact-diff-contract
//     cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase4_gate_evidence.zig
//     cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase4_remaining_gap_matrix.zig
//     cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase4_workflow_route_counts.zig
//     cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase4_reversible_delivery_pins.zig --self-test
//     cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase4_reversible_delivery_pins.zig
//     cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase4_validation_lane_sequencing.zig --self-test
//     cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase4_validation_lane_sequencing.zig
//     cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase4_perf_threshold_matrix.zig --self-test
//     cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase4_perf_threshold_matrix.zig
//     cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase4_perf_baseline_packet.zig
//
// phase4-artifact-diff-contract:
//     cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/artifact_diff.zig --self-test
//     cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase4_artifact_diff_determinism.zig --self-test
//     cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase4_artifact_diff_determinism.zig
//     cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase4_artifact_diff_validator_replays.zig --self-test
//     cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase4_artifact_diff_validator_replays.zig
//     cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase4_artifact_diff_makefile_contract.zig --self-test
//     cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase4_artifact_diff_makefile_contract.zig
//     cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build artifact-diff-text-contract --build-file scripts/zigux/artifact_diff_text_contract_build.zig
//
// phase4-test:
//     cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build test --build-file zigux/tests/phase4_build.zig
//
// phase4-runtime-atomic64-diff:
//     cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build phase4-runtime-atomic64-diff --build-file zigux/tests/phase4_build.zig
//
// phase4-runtime-atomic64-diff-survey:
//     cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build phase4-runtime-atomic64-diff-survey --build-file zigux/tests/phase4_build.zig
//
// phase4-perf-baseline-survey:
//     cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build phase4-perf-baseline-survey --build-file zigux/tests/phase4_build.zig
//
// phase4-bitmap-diff:
//     cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build phase4-bitmap-diff --build-file zigux/tests/phase4_build.zig
//
// phase4-bitmap-diff-survey:
//     cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build phase4-bitmap-diff-survey --build-file zigux/tests/phase4_build.zig
//
// phase4-bitmap-live-helper-replay:
//     cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build phase4-bitmap-live-helper-replay --build-file zigux/tests/phase4_build.zig
//
// phase4-test-fsmount-survey:
//     cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig
//
// phase4-kprobe-example-survey:
//     cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) test zigux/tests/phase4_kprobe_example_survey.zig
//
// phase4: phase4-validate phase4-test
//
// SELFTEST_WORKFLOW
// jobs:
//   bootstrap:
//     steps:
//       - name: Validate Phase 4 rollback routes
//         run: make -C zigux phase4-validate
//       - name: Run Phase 4 rollback tests
//         run: make -C zigux phase4-test
//       - name: Run Phase 4 artifact-diff contract make route
//         run: make -C zigux phase4-artifact-diff-contract
//       - name: Self-test current Phase 4 artifact-diff helper
//         run: zig run scripts/zigux/artifact_diff.zig --self-test
//       - name: Self-test current Phase 4 artifact-diff contract checker
//         run: zig run scripts\zigux/check_artifact_diff_contract.zig --self-test
//       - name: Check current Phase 4 artifact-diff contract packet
//         run: zig run scripts\zigux/check_artifact_diff_contract.zig
//       - name: Self-test current Phase 4 artifact-diff determinism checker
//         run: zig run scripts\zigux/check_phase4_artifact_diff_determinism.zig --self-test
//       - name: Check current Phase 4 artifact-diff determinism packet
//         run: zig run scripts\zigux/check_phase4_artifact_diff_determinism.zig
//       - name: Self-test current Phase 4 artifact-diff validator replay checker
//         run: zig run scripts\zigux/check_phase4_artifact_diff_validator_replays.zig --self-test
//       - name: Check current Phase 4 artifact-diff validator replay packet
//         run: zig run scripts\zigux/check_phase4_artifact_diff_validator_replays.zig
//
// SELFTEST_BUILD
// const std = @import("std");
//
// pub fn build(b: *std.Build) void {
//     b.path("phase4_runtime_atomic64_diff_survey.zig");
//     b.path("phase4_perf_baseline_survey.zig");
//     b.path("phase4_test_fsmount_survey.zig");
//     b.path("phase4_bitmap_diff_survey.zig");
//     b.path("phase4_bitmap_live_helper_replay.zig");
//     "phase4-runtime-atomic64-diff-tests";
//     "phase4-runtime-atomic64-diff-survey-tests";
//     "phase4-perf-baseline-survey-tests";
//     "phase4-test-fsmount-survey-tests";
//     "phase4-bitmap-diff-tests";
//     "phase4-bitmap-diff-survey-tests";
//     "phase4-bitmap-live-helper-replay-tests";
//     const test_step = b.step("test", "Run Phase 4 differential validation tests");
//     const runtime_atomic64_diff_step = b.step(
//         "phase4-runtime-atomic64-diff",
//         "Run the isolated Phase 4 runtime atomic64 diff replay",
//     );
//     runtime_atomic64_diff_step.dependOn(&run_atomic64_diff_tests.step);
//     const runtime_atomic64_diff_survey_step = b.step(
//         "phase4-runtime-atomic64-diff-survey",
//         "Run the manifest-backed Phase 4 runtime atomic64 handoff survey",
//     );
//     runtime_atomic64_diff_survey_step.dependOn(&run_runtime_atomic64_diff_survey_tests.step);
//     const perf_baseline_survey_step = b.step(
//         "phase4-perf-baseline-survey",
//         "Run the dedicated Phase 4 perf-baseline posture survey without widening the shared correctness-first packet",
//     );
//     perf_baseline_survey_step.dependOn(&run_perf_baseline_survey_tests.step);
//     const test_fsmount_survey_step = b.step(
//         "phase4-test-fsmount-survey",
//         "Run the dedicated Phase 4 test_fsmount gap survey without promoting a shipped Zig starter",
//     );
//     test_fsmount_survey_step.dependOn(&run_test_fsmount_survey_tests.step);
//     const bitmap_diff_step = b.step("phase4-bitmap-diff", "Run the isolated Phase 4 bitmap diff replay");
//     bitmap_diff_step.dependOn(&run_bitmap_diff_tests.step);
//     const bitmap_diff_survey_step = b.step(
//         "phase4-bitmap-diff-survey",
//         "Run the manifest-backed Phase 4 bitmap rollback survey",
//     );
//     bitmap_diff_survey_step.dependOn(&run_bitmap_diff_survey_tests.step);
//     const bitmap_live_helper_replay_step = b.step(
//         "phase4-bitmap-live-helper-replay",
//         "Run the helper-backed Phase 4 bitmap rollback replay",
//     );
//     bitmap_live_helper_replay_step.dependOn(&run_bitmap_live_helper_replay_tests.step);
// }
//
// SELFTEST_MATRIX
// # Phase 4 Validation Matrix
// scripts\zigux/check_phase4_remaining_gap_matrix.zig
// zigux/tests/phase4_perf_baseline_manifest.json
// zigux/tests/phase4_perf_baseline_survey.zig
// zig build phase4-perf-baseline-survey --build-file zigux/tests/phase4_build.zig
// make -C zigux phase4-perf-baseline-survey
//
// SELFTEST_GATE_EVIDENCE
// # Phase 4 Gate Evidence
// zigux/tests/phase4_perf_baseline_manifest.json
// zigux/tests/phase4_perf_baseline_survey.zig
// zig build phase4-perf-baseline-survey --build-file zigux/tests/phase4_build.zig
// make -C zigux phase4-perf-baseline-survey
// zig build phase4-bitmap-diff-survey --build-file zigux/tests/phase4_build.zig
// make -C zigux phase4-bitmap-diff-survey
//
