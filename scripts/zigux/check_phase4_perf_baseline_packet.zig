const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE4_PERF_BASELINE_PACKET_CHECK=pass";
pub const self_test_pass_marker = "PHASE4_PERF_BASELINE_PACKET_SELF_TEST=pass";

const EXPECTED_COORDINATION_OWNERS = [_][]const u8{
    "ABI and Runtime Team",
    "Shared Subsystems Pod",
};

const EXPECTED_LOCAL_ONLY_POSTURE_NOTE = [_][]const u8{
    "The dedicated perf-baseline survey keeps approved local benchmark commands and approved local-only acceptable limits explicit while shared CI perf promotion remains intentionally pending.",
};

const EXPECTED_BOOTSTRAP_CI_POSTURE = [_][]const u8{
    "reviewability_only_local_survey_wrappers_not_on_shared_phase4_test_or_bootstrap_workflow",
};

const MANIFEST_MARKERS = [_][]const u8{
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

const SURVEY_MARKERS = [_][]const u8{
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

const MATRIX_MARKERS = [_][]const u8{
    "local-only benchmark commands and acceptable limits are approved today",
    "the dedicated perf-baseline survey may keep the approved local benchmark commands and the approved local-only acceptable limits for both landed rollback gates machine-checked",
    "must stay outside the shared `phase4-test` entrypoint until any shared CI perf promotion is intentionally approved",
    "any future shared CI perf-promotion claim must name the Validation and Perf Team as the decision owner and the ABI and Runtime Team plus Shared Subsystems Pod as coordination owners",
    "current replay path: `zig build phase4-perf-baseline-survey --build-file zigux/tests/phase4_build.zig` and `make -C zigux phase4-perf-baseline-survey`",
};

const REVIEW_CHECKLIST_MARKERS = [_][]const u8{
    "keep the directly readable local-only perf packet explicit",
    "keep the Validation and Perf Team as the decision owner for any broader shared-CI perf promotion",
    "keep the ABI and Runtime Team plus Shared Subsystems Pod as coordination owners for that policy call",
    "keep the pending shared-CI perf-promotion posture explicit instead of implying shared CI perf approval",
};

const NOTE_MARKERS = [_][]const u8{
    "Current direct readback in this run confirmed this note, `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, `scripts/zigux/README.md`, `scripts\\zigux/check_phase4_repo_reality_warning.zig`, `scripts\\zigux/check_phase4_tests_readme_packet.zig`, `scripts\\zigux/check_phase4_reversible_delivery_pins.zig`, `scripts\\zigux/check_phase4_perf_baseline_packet.zig`, `scripts\\zigux/check_phase4_perf_threshold_matrix.zig`, `zigux/tests/phase4_perf_baseline_manifest.json`, and `zigux/tests/phase4_perf_baseline_survey.zig` on current `master`.",
    "Current direct-readback dedicated local-only perf checkers: `scripts\\zigux/check_phase4_perf_baseline_packet.zig` and `scripts\\zigux/check_phase4_perf_threshold_matrix.zig`.",
    "Current direct-readback dedicated local-only perf companion members:",
    "  * `zigux/tests/phase4_perf_baseline_manifest.json`",
    "  * `zigux/tests/phase4_perf_baseline_survey.zig`",
    "The direct checker pair now publishes `PHASE4_REPO_REALITY_WARNING_SELF_TEST_CASES=32` and `PHASE4_REVERSIBLE_DELIVERY_PIN_SELF_TEST_CASE_COUNT=20` here",
};

const SCRIPTS_README_MARKERS = [_][]const u8{
    "`scripts\\zigux/check_artifact_diff_contract.zig`, `scripts\\zigux/check_phase4_artifact_diff_determinism.zig`, `scripts\\zigux/check_phase4_artifact_diff_validator_replays.zig`, `scripts\\zigux/check_phase4_repo_reality_warning.zig`, `scripts\\zigux/check_phase4_reversible_delivery_pins.zig`, `scripts\\zigux/check_phase4_perf_baseline_packet.zig`, `scripts\\zigux/check_phase4_perf_threshold_matrix.zig`, `scripts\\zigux/check_phase4_remaining_gap_matrix.zig`, and `scripts\\zigux/check_phase4_workflow_route_counts.zig` keep the current helper-contract, validator-replay, shared rollback-owner reminder, local-only perf-governance, recovered remaining-gap, and route-inventory packet explicit on current `master`",
    "`Documentation/zigux/phase4-reversible-delivery-evidence.md`, `Documentation/zigux/phase4-gate-evidence.md`, `Documentation/zigux/phase4-validation-matrix.md`, `Documentation/zigux/phase4-validation-lane-sequencing.md`, `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, `zigux/tests/atomic64_diff.zig`, `zigux/tests/runtime_atomic64_diff.zig`, `scripts\\zigux/check_phase4_perf_threshold_matrix.zig`, `zigux/tests/phase4_perf_baseline_manifest.json`, and `zigux/tests/phase4_perf_baseline_survey.zig` remain the current reminder-surface companions for that active Phase 4 rollback-readiness and perf-governance packet",
    "keep the current governance split explicit here too: the direct-readback shared handoff stays narrower than the broader recovered note companions, the Validation and Perf Team remains the decision owner for any broader shared-CI perf promotion, the ABI and Runtime Team plus Shared Subsystems Pod remain the coordination owners for that policy call, and the dedicated perf-baseline survey must stay local-only until a later bounded lane intentionally widens that posture",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_expected_coordination_owners_path = try guard.joinPath(allocator, root, "zigux/tests/phase4_perf_baseline_manifest.json");
    defer allocator.free(text_expected_coordination_owners_path);
    const text_expected_coordination_owners = try guard.readUtf8File(io, allocator, text_expected_coordination_owners_path);
    defer allocator.free(text_expected_coordination_owners);
    for (EXPECTED_COORDINATION_OWNERS) |marker| try guard.requireMarker(text_expected_coordination_owners, marker);
    const text_expected_local_only_posture_note_path = try guard.joinPath(allocator, root, "zigux/tests/phase4_perf_baseline_manifest.json");
    defer allocator.free(text_expected_local_only_posture_note_path);
    const text_expected_local_only_posture_note = try guard.readUtf8File(io, allocator, text_expected_local_only_posture_note_path);
    defer allocator.free(text_expected_local_only_posture_note);
    for (EXPECTED_LOCAL_ONLY_POSTURE_NOTE) |marker| try guard.requireMarker(text_expected_local_only_posture_note, marker);
    const text_expected_bootstrap_ci_posture_path = try guard.joinPath(allocator, root, "zigux/tests/phase4_perf_baseline_manifest.json");
    defer allocator.free(text_expected_bootstrap_ci_posture_path);
    const text_expected_bootstrap_ci_posture = try guard.readUtf8File(io, allocator, text_expected_bootstrap_ci_posture_path);
    defer allocator.free(text_expected_bootstrap_ci_posture);
    for (EXPECTED_BOOTSTRAP_CI_POSTURE) |marker| try guard.requireMarker(text_expected_bootstrap_ci_posture, marker);
    const text_manifest_markers_path = try guard.joinPath(allocator, root, "zigux/tests/phase4_perf_baseline_manifest.json");
    defer allocator.free(text_manifest_markers_path);
    const text_manifest_markers = try guard.readUtf8File(io, allocator, text_manifest_markers_path);
    defer allocator.free(text_manifest_markers);
    for (MANIFEST_MARKERS) |marker| try guard.requireMarker(text_manifest_markers, marker);
    const text_survey_markers_path = try guard.joinPath(allocator, root, "zigux/tests/phase4_perf_baseline_survey.zig");
    defer allocator.free(text_survey_markers_path);
    const text_survey_markers = try guard.readUtf8File(io, allocator, text_survey_markers_path);
    defer allocator.free(text_survey_markers);
    for (SURVEY_MARKERS) |marker| try guard.requireMarker(text_survey_markers, marker);
    const text_matrix_markers_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase4-validation-matrix.md");
    defer allocator.free(text_matrix_markers_path);
    const text_matrix_markers = try guard.readUtf8File(io, allocator, text_matrix_markers_path);
    defer allocator.free(text_matrix_markers);
    for (MATRIX_MARKERS) |marker| try guard.requireMarker(text_matrix_markers, marker);
    const text_review_checklist_markers_path = try guard.joinPath(allocator, root, "Documentation/zigux/review-checklist.md");
    defer allocator.free(text_review_checklist_markers_path);
    const text_review_checklist_markers = try guard.readUtf8File(io, allocator, text_review_checklist_markers_path);
    defer allocator.free(text_review_checklist_markers);
    for (REVIEW_CHECKLIST_MARKERS) |marker| try guard.requireMarker(text_review_checklist_markers, marker);
    const text_note_markers_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase4-reversible-delivery-evidence.md");
    defer allocator.free(text_note_markers_path);
    const text_note_markers = try guard.readUtf8File(io, allocator, text_note_markers_path);
    defer allocator.free(text_note_markers);
    for (NOTE_MARKERS) |marker| try guard.requireMarker(text_note_markers, marker);
    const text_scripts_readme_markers_path = try guard.joinPath(allocator, root, "scripts/zigux/README.md");
    defer allocator.free(text_scripts_readme_markers_path);
    const text_scripts_readme_markers = try guard.readUtf8File(io, allocator, text_scripts_readme_markers_path);
    defer allocator.free(text_scripts_readme_markers);
    for (SCRIPTS_README_MARKERS) |marker| try guard.requireMarker(text_scripts_readme_markers, marker);
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
