const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE4_PERF_BASELINE_PACKET_CHECK=pass";
pub const self_test_pass_marker = "PHASE4_PERF_BASELINE_PACKET_SELF_TEST=pass";

const FileContract = struct { rel: []const u8, markers: []const []const u8 };

const markers_0 = [_][]const u8{
    "ABI and Runtime Team",
    "Shared Subsystems Pod",
    "The dedicated perf-baseline survey keeps approved local benchmark commands and approved local-only acceptable limits explicit while shared CI perf promotion remains intentionally pending.",
    "reviewability_only_local_survey_wrappers_not_on_shared_phase4_test_or_bootstrap_workflow",
    "\"lane_key\": \"P4-L20\"",
    "\"phase\": \"Phase 4\"",
    "\"owner\": \"Validation and Perf Team\"",
    "\"rollback_owner\": \"Validation and Perf Team\"",
    "\"decision_owner\": \"Validation and Perf Team\"",
    "\"shared_ci_perf_promotion_status\": \"pending\"",
    "\"benchmark_command\": \"zig build phase4-runtime-atomic64-diff --build-file zigux/tests/phase4_build.zig\"",
    "\"benchmark_command\": \"zig build phase4-bitmap-diff --build-file zigux/tests/phase4_build.zig\"",
    "\"linux_style_wrapper\": \"make -C zigux phase4-perf-baseline-survey\"",
    "\"acceptable_limit_status\": \"approved_local_only\"",
    "\"acceptable_limit_metric\": \"median_elapsed_ns\"",
    "\"acceptable_limit_iterations\": 4",
    "\"acceptable_limit_sample_count\": 7",
    "\"acceptable_limit_max_elapsed_ns\": 8192",
    "\"acceptable_limit_max_elapsed_ns\": 12288",
    "\"sample_count_note\": \"seven monotonic samples\"",
    "\"status\": \"shared CI perf promotion pending\"",
    "\"gate_surfaces\": [",
    "\"surface\": \"zigux/tests/atomic64_diff.zig\"",
    "\"surface\": \"zigux/tests/bitmap_diff.zig\"",
    "\"kind\": \"legacy_threshold_replay_alias\"",
    "\"target_id\": \"phase4-perf-baseline-bitmap-command-evidence\"",
};

const markers_1 = [_][]const u8{
    "test \"phase4 perf baseline survey keeps exact local-only iteration, sample, and replay counts explicit\" {",
    "try requireMarkerCount(\"\\\"acceptable_limit_iterations\\\": 4\", 2);",
    "try requireMarkerCount(\"\\\"acceptable_limit_sample_count\\\": 7\", 2);",
    "try requireMarker(\"\\\"benchmark_command\\\": \\\"zig build phase4-runtime-atomic64-diff --build-file zigux/tests/phase4_build.zig\\\"\");",
    "try requireMarker(\"\\\"benchmark_command\\\": \\\"zig build phase4-bitmap-diff --build-file zigux/tests/phase4_build.zig\\\"\");",
    "try requireMarker(\"\\\"shared_ci_perf_promotion_status\\\": \\\"pending\\\"\");",
    "try requireMarker(\"\\\"coordination_owners\\\": [\");",
    "try requireMarker(\"\\\"rollback_owner\\\": \\\"Validation and Perf Team\\\"\");",
    "try requireMarker(\"\\\"decision_owner\\\": \\\"Validation and Perf Team\\\"\");",
    "try requireMarker(\"\\\"dedicated_local_survey_wrapper\\\": \\\"zig build phase4-perf-baseline-survey --build-file zigux/tests/phase4_build.zig\\\"\");",
    "try requireMarker(\"\\\"dedicated_linux_style_survey_wrapper\\\": \\\"make -C zigux phase4-perf-baseline-survey\\\"\");",
    "try requireMarker(\"\\\"validation_entrypoint\\\": \\\"zig build phase4-perf-baseline-survey --build-file zigux/tests/phase4_build.zig\\\"\");",
    "try requireMarker(\"\\\"bootstrap_ci_posture\\\": \\\"reviewability_only_local_survey_wrappers_not_on_shared_phase4_test_or_bootstrap_workflow\\\"\");",
    "try requireMarker(\"\\\"shared_lab_and_ci_matrix_anchor\\\": \\\"Documentation/zigux/phase4-validation-matrix.md#lab-and-ci-matrix\\\"\");",
    "try requireMarker(\"\\\"local_only_posture_note\\\": \\\"The dedicated perf-baseline survey keeps approved local benchmark commands and approved local-only acceptable limits explicit while shared CI perf promotion remains intentionally pending.\\\"\");",
};

const markers_2 = [_][]const u8{
    "local-only benchmark commands and acceptable limits are approved today",
    "the dedicated perf-baseline survey may keep the approved local benchmark commands and the approved local-only acceptable limits for both landed rollback gates machine-checked",
    "must stay outside the shared `phase4-test` entrypoint until any shared CI perf promotion is intentionally approved",
    "any future shared CI perf-promotion claim must name the Validation and Perf Team as the decision owner and the ABI and Runtime Team plus Shared Subsystems Pod as coordination owners",
    "current replay path: `zig build phase4-perf-baseline-survey --build-file zigux/tests/phase4_build.zig` and `make -C zigux phase4-perf-baseline-survey`",
};

const markers_3 = [_][]const u8{
    "keep the directly readable local-only perf packet explicit",
    "keep the Validation and Perf Team as the decision owner for any broader shared-CI perf promotion",
    "keep the ABI and Runtime Team plus Shared Subsystems Pod as coordination owners for that policy call",
    "keep the pending shared-CI perf-promotion posture explicit instead of implying shared CI perf approval",
};

const markers_4 = [_][]const u8{
    "Current direct readback in this run confirmed this note, `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, `scripts/zigux/README.md`, `scripts\\zigux/check_phase4_repo_reality_warning.zig`, `scripts\\zigux/check_phase4_tests_readme_packet.zig`, `scripts\\zigux/check_phase4_reversible_delivery_pins.zig`, `scripts\\zigux/check_phase4_perf_baseline_packet.zig`, `scripts\\zigux/check_phase4_perf_threshold_matrix.zig`, `zigux/tests/phase4_perf_baseline_manifest.json`, and `zigux/tests/phase4_perf_baseline_survey.zig` on current `master`.",
    "Current direct-readback dedicated local-only perf checkers: `scripts\\zigux/check_phase4_perf_baseline_packet.zig` and `scripts\\zigux/check_phase4_perf_threshold_matrix.zig`.",
    "Current direct-readback dedicated local-only perf companion members:",
    "  * `zigux/tests/phase4_perf_baseline_manifest.json`",
    "  * `zigux/tests/phase4_perf_baseline_survey.zig`",
    "The direct checker pair now publishes `PHASE4_REPO_REALITY_WARNING_SELF_TEST_CASES=32` and `PHASE4_REVERSIBLE_DELIVERY_PIN_SELF_TEST_CASE_COUNT=20` here",
};

const markers_5 = [_][]const u8{
    "`scripts\\zigux/check_artifact_diff_contract.zig`, `scripts\\zigux/check_phase4_artifact_diff_determinism.zig`, `scripts\\zigux/check_phase4_artifact_diff_validator_replays.zig`, `scripts\\zigux/check_phase4_repo_reality_warning.zig`, `scripts\\zigux/check_phase4_reversible_delivery_pins.zig`, `scripts\\zigux/check_phase4_perf_baseline_packet.zig`, `scripts\\zigux/check_phase4_perf_threshold_matrix.zig`, `scripts\\zigux/check_phase4_remaining_gap_matrix.zig`, and `scripts\\zigux/check_phase4_workflow_route_counts.zig` keep the current helper-contract, validator-replay, shared rollback-owner reminder, local-only perf-governance, recovered remaining-gap, and route-inventory packet explicit on current `master`",
    "`Documentation/zigux/phase4-reversible-delivery-evidence.md`, `Documentation/zigux/phase4-gate-evidence.md`, `Documentation/zigux/phase4-validation-matrix.md`, `Documentation/zigux/phase4-validation-lane-sequencing.md`, `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, `zigux/tests/atomic64_diff.zig`, `zigux/tests/runtime_atomic64_diff.zig`, `scripts\\zigux/check_phase4_perf_threshold_matrix.zig`, `zigux/tests/phase4_perf_baseline_manifest.json`, and `zigux/tests/phase4_perf_baseline_survey.zig` remain the current reminder-surface companions for that active Phase 4 rollback-readiness and perf-governance packet",
    "keep the current governance split explicit here too: the direct-readback shared handoff stays narrower than the broader recovered note companions, the Validation and Perf Team remains the decision owner for any broader shared-CI perf promotion, the ABI and Runtime Team plus Shared Subsystems Pod remain the coordination owners for that policy call, and the dedicated perf-baseline survey must stay local-only until a later bounded lane intentionally widens that posture",
};

const contracts = [_]FileContract{
    .{ .rel = "zigux/tests/phase4_perf_baseline_manifest.json", .markers = &markers_0 },
    .{ .rel = "zigux/tests/phase4_perf_baseline_survey.zig", .markers = &markers_1 },
    .{ .rel = "Documentation/zigux/phase4-validation-matrix.md", .markers = &markers_2 },
    .{ .rel = "Documentation/zigux/review-checklist.md", .markers = &markers_3 },
    .{ .rel = "Documentation/zigux/phase4-reversible-delivery-evidence.md", .markers = &markers_4 },
    .{ .rel = "scripts/zigux/README.md", .markers = &markers_5 },
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    for (contracts) |contract| {
        const path = try guard.joinPath(allocator, root, contract.rel);
        defer allocator.free(path);
        const text = try guard.readUtf8File(io, allocator, path);
        defer allocator.free(text);
        for (contract.markers) |marker| try guard.requireMarker(text, marker);
    }
}

fn runSelfTest(io: Io, allocator: std.mem.Allocator) !u8 {
    const root = try guard.defaultRepoRoot(allocator);
    defer allocator.free(root);
    try checkRepo(io, allocator, root);
    try guard.printLine(io, "{s}", .{self_test_pass_marker});
    try guard.printLine(io, "PHASE4_PERF_BASELINE_PACKET_SELF_TEST_CASE_COUNT={d}", .{@as(usize, 6)});
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
// EXPECTED_COORDINATION_OWNERS
// ABI and Runtime Team
// Shared Subsystems Pod
// EXPECTED_LOCAL_ONLY_POSTURE_NOTE
// The dedicated perf-baseline survey keeps approved local benchmark commands and approved local-only acceptable limits explicit while shared CI perf promotion remains intentionally pending.
// EXPECTED_BOOTSTRAP_CI_POSTURE
// reviewability_only_local_survey_wrappers_not_on_shared_phase4_test_or_bootstrap_workflow
// MANIFEST_MARKERS
// "lane_key": "P4-L20"
// "phase": "Phase 4"
// "owner": "Validation and Perf Team"
// "rollback_owner": "Validation and Perf Team"
// "decision_owner": "Validation and Perf Team"
// "shared_ci_perf_promotion_status": "pending"
// "benchmark_command": "zig build phase4-runtime-atomic64-diff --build-file zigux/tests/phase4_build.zig"
// "benchmark_command": "zig build phase4-bitmap-diff --build-file zigux/tests/phase4_build.zig"
// "linux_style_wrapper": "make -C zigux phase4-perf-baseline-survey"
// "acceptable_limit_status": "approved_local_only"
// "acceptable_limit_metric": "median_elapsed_ns"
// "acceptable_limit_iterations": 4
// "acceptable_limit_sample_count": 7
// "acceptable_limit_max_elapsed_ns": 8192
// "acceptable_limit_max_elapsed_ns": 12288
// "sample_count_note": "seven monotonic samples"
// "status": "shared CI perf promotion pending"
// "gate_surfaces": [
// "surface": "zigux/tests/atomic64_diff.zig"
// "surface": "zigux/tests/bitmap_diff.zig"
// "kind": "legacy_threshold_replay_alias"
// "target_id": "phase4-perf-baseline-bitmap-command-evidence"
// SURVEY_MARKERS
// test "phase4 perf baseline survey keeps exact local-only iteration, sample, and replay counts explicit" {
// try requireMarkerCount("\"acceptable_limit_iterations\": 4", 2);
// try requireMarkerCount("\"acceptable_limit_sample_count\": 7", 2);
// try requireMarker("\"benchmark_command\": \"zig build phase4-runtime-atomic64-diff --build-file zigux/tests/phase4_build.zig\"");
// try requireMarker("\"benchmark_command\": \"zig build phase4-bitmap-diff --build-file zigux/tests/phase4_build.zig\"");
// try requireMarker("\"shared_ci_perf_promotion_status\": \"pending\"");
// try requireMarker("\"coordination_owners\": [");
// try requireMarker("\"rollback_owner\": \"Validation and Perf Team\"");
// try requireMarker("\"decision_owner\": \"Validation and Perf Team\"");
// try requireMarker("\"dedicated_local_survey_wrapper\": \"zig build phase4-perf-baseline-survey --build-file zigux/tests/phase4_build.zig\"");
// try requireMarker("\"dedicated_linux_style_survey_wrapper\": \"make -C zigux phase4-perf-baseline-survey\"");
// try requireMarker("\"validation_entrypoint\": \"zig build phase4-perf-baseline-survey --build-file zigux/tests/phase4_build.zig\"");
// try requireMarker("\"bootstrap_ci_posture\": \"reviewability_only_local_survey_wrappers_not_on_shared_phase4_test_or_bootstrap_workflow\"");
// try requireMarker("\"shared_lab_and_ci_matrix_anchor\": \"Documentation/zigux/phase4-validation-matrix.md#lab-and-ci-matrix\"");
// try requireMarker("\"local_only_posture_note\": \"The dedicated perf-baseline survey keeps approved local benchmark commands and approved local-only acceptable limits explicit while shared CI perf promotion remains intentionally pending.\"");
// MATRIX_MARKERS
// local-only benchmark commands and acceptable limits are approved today
// the dedicated perf-baseline survey may keep the approved local benchmark commands and the approved local-only acceptable limits for both landed rollback gates machine-checked
// must stay outside the shared `phase4-test` entrypoint until any shared CI perf promotion is intentionally approved
// any future shared CI perf-promotion claim must name the Validation and Perf Team as the decision owner and the ABI and Runtime Team plus Shared Subsystems Pod as coordination owners
// current replay path: `zig build phase4-perf-baseline-survey --build-file zigux/tests/phase4_build.zig` and `make -C zigux phase4-perf-baseline-survey`
// REVIEW_CHECKLIST_MARKERS
// keep the directly readable local-only perf packet explicit
// keep the Validation and Perf Team as the decision owner for any broader shared-CI perf promotion
// keep the ABI and Runtime Team plus Shared Subsystems Pod as coordination owners for that policy call
// keep the pending shared-CI perf-promotion posture explicit instead of implying shared CI perf approval
// NOTE_MARKERS
// Current direct readback in this run confirmed this note, `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, `scripts/zigux/README.md`, `scripts\zigux/check_phase4_repo_reality_warning.zig`, `scripts\zigux/check_phase4_tests_readme_packet.zig`, `scripts\zigux/check_phase4_reversible_delivery_pins.zig`, `scripts\zigux/check_phase4_perf_baseline_packet.zig`, `scripts\zigux/check_phase4_perf_threshold_matrix.zig`, `zigux/tests/phase4_perf_baseline_manifest.json`, and `zigux/tests/phase4_perf_baseline_survey.zig` on current `master`.
// Current direct-readback dedicated local-only perf checkers: `scripts\zigux/check_phase4_perf_baseline_packet.zig` and `scripts\zigux/check_phase4_perf_threshold_matrix.zig`.
// Current direct-readback dedicated local-only perf companion members:
//   * `zigux/tests/phase4_perf_baseline_manifest.json`
//   * `zigux/tests/phase4_perf_baseline_survey.zig`
// The direct checker pair now publishes `PHASE4_REPO_REALITY_WARNING_SELF_TEST_CASES=32` and `PHASE4_REVERSIBLE_DELIVERY_PIN_SELF_TEST_CASE_COUNT=20` here
// SCRIPTS_README_MARKERS
// `scripts\zigux/check_artifact_diff_contract.zig`, `scripts\zigux/check_phase4_artifact_diff_determinism.zig`, `scripts\zigux/check_phase4_artifact_diff_validator_replays.zig`, `scripts\zigux/check_phase4_repo_reality_warning.zig`, `scripts\zigux/check_phase4_reversible_delivery_pins.zig`, `scripts\zigux/check_phase4_perf_baseline_packet.zig`, `scripts\zigux/check_phase4_perf_threshold_matrix.zig`, `scripts\zigux/check_phase4_remaining_gap_matrix.zig`, and `scripts\zigux/check_phase4_workflow_route_counts.zig` keep the current helper-contract, validator-replay, shared rollback-owner reminder, local-only perf-governance, recovered remaining-gap, and route-inventory packet explicit on current `master`
// `Documentation/zigux/phase4-reversible-delivery-evidence.md`, `Documentation/zigux/phase4-gate-evidence.md`, `Documentation/zigux/phase4-validation-matrix.md`, `Documentation/zigux/phase4-validation-lane-sequencing.md`, `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, `zigux/tests/atomic64_diff.zig`, `zigux/tests/runtime_atomic64_diff.zig`, `scripts\zigux/check_phase4_perf_threshold_matrix.zig`, `zigux/tests/phase4_perf_baseline_manifest.json`, and `zigux/tests/phase4_perf_baseline_survey.zig` remain the current reminder-surface companions for that active Phase 4 rollback-readiness and perf-governance packet
// keep the current governance split explicit here too: the direct-readback shared handoff stays narrower than the broader recovered note companions, the Validation and Perf Team remains the decision owner for any broader shared-CI perf promotion, the ABI and Runtime Team plus Shared Subsystems Pod remain the coordination owners for that policy call, and the dedicated perf-baseline survey must stay local-only until a later bounded lane intentionally widens that posture
