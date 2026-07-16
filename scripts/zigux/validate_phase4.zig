const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE4_VALIDATION=pass";
pub const self_test_pass_marker = "PHASE4_VALIDATE_SELF_TEST=pass";

const WORKFLOW_ROUTE_COUNTS_SELF_TEST_CASES = [_][]const u8{
    "baseline_round_trip,",
    "workflow_order_drift,",
    "missing_make_phase4_validate_artifact_diff_contract_selftest_command,",
    "phase4_validate_contract_selftest_order_drift,",
    "missing_make_artifact_diff_contract_selftest_command,",
    "missing_make_route_counts_command,",
    "missing_make_reversible_delivery_selftest_command,",
    "missing_make_reversible_delivery_command,",
    "missing_make_remaining_gap_command,",
    "missing_make_validator_replays_selftest_command,",
    "missing_make_validator_replays_command,",
    "missing_make_validation_lane_sequencing_selftest_command,",
    "missing_make_validation_lane_sequencing_command,",
    "missing_make_perf_baseline_command,",
    "missing_workflow_validate_route,",
    "missing_workflow_test_route,",
    "missing_workflow_artifact_diff_contract_make_route,",
    "missing_workflow_artifact_diff_helper_selftest,",
    "missing_workflow_artifact_diff_contract_selftest,",
    "missing_workflow_artifact_diff_contract_check,",
    "missing_workflow_artifact_diff_determinism_selftest,",
    "missing_workflow_artifact_diff_determinism_check,",
    "missing_workflow_artifact_diff_validator_replays_selftest,",
    "missing_workflow_artifact_diff_validator_replays_check,",
    "missing_matrix_remaining_gap_marker,",
    "missing_gate_evidence_bitmap_build_route,",
    "missing_gate_evidence_bitmap_wrapper,",
    "missing_build_test_fsmount_route,",
    "missing_build_bitmap_diff_route,",
    "missing_build_bitmap_diff_survey_route,",
    "missing_build_bitmap_live_helper_replay_route,",
    "forbidden_perf_baseline_dependency",
};

const ARTIFACT_DIFF_HELPER_SELF_TEST_CASES = [_][]const u8{
    "text_pass,",
    "text_mismatch,",
    "json_pass,",
    "json_mismatch,",
    "json_invalid_expected,",
    "json_invalid_actual,",
    "json_invalid_both,",
    "json_missing_expected,",
    "json_missing_actual,",
    "json_missing_both,",
    "bytes_pass,",
    "bytes_drift,",
    "text_missing_expected,",
    "text_missing_actual,",
    "text_missing_both,",
    "bytes_missing_expected,",
    "bytes_missing_actual,",
    "bytes_missing_both,",
    "legacy_sha256_alias,",
    "missing_mode_value_rejected,",
    "missing_positional_arguments_rejected,",
    "invalid_mode_rejected,",
    "extra_positional_rejected",
};

const PHASE4_TESTS_README_PACKET_SELF_TEST_CASES = [_][]const u8{
    "baseline_round_trip,",
    "missing_header,",
    "missing_intro,",
    "missing_phase4_heading,",
    "missing_phase4_note_reference,",
    "missing_phase4_gate_evidence_reference,",
    "missing_phase4_repo_reality_warning_reference,",
    "missing_phase4_tests_readme_checker_reference,",
    "missing_phase4_reversible_delivery_checker_reference,",
    "missing_phase4_perf_checker_reference,",
    "missing_phase4_validator_reference,",
    "missing_phase4_perf_manifest_reference,",
    "missing_phase4_perf_survey_reference,",
    "missing_phase4_build_reference,",
    "missing_phase4_bitmap_reference,",
    "missing_phase4_bitmap_replay_reference,",
    "missing_phase4_atomic64_reference,",
    "missing_phase4_runtime_atomic64_reference,",
    "missing_phase4_owner_split_reference",
};

const REQUIRED_ARTIFACT_DOC_MARKERS = [_][]const u8{
    "Current Phase 4 use",
    "scripts/zigux/artifact_diff.zig",
    "scripts\\zigux/check_artifact_diff_contract.zig",
    "scripts\\zigux/check_phase4_artifact_diff_determinism.zig",
    "scripts\\zigux/check_phase4_artifact_diff_validator_replays.zig",
    "ARTIFACT_DIFF_SELF_TEST_CASE_COUNT=23",
    "ARTIFACT_DIFF_CONTRACT_SELF_TEST_CASE_COUNT=24",
    "ARTIFACT_DIFF_CONTRACT_CASE_COUNT=30",
    "PHASE4_ARTIFACT_DIFF_DETERMINISM_SELF_TEST_CASE_COUNT=13",
    "PHASE4_ARTIFACT_DIFF_VALIDATOR_REPLAYS_SELF_TEST_CASE_COUNT=14",
};

const REQUIRED_ARTIFACT_MATRIX_MARKERS = [_][]const u8{
    "scripts\\zigux/check_phase4_remaining_gap_matrix.zig",
    "Documentation/zigux/phase4-measurability-gap-survey.md",
    "zigux/tests/phase4_perf_baseline_manifest.json",
    "zigux/tests/phase4_perf_baseline_survey.zig",
    "zig build phase4-perf-baseline-survey --build-file zigux/tests/phase4_build.zig",
    "make -C zigux phase4-perf-baseline-survey",
};

const REQUIRED_MEASURABILITY_GAP_MARKERS = [_][]const u8{
    "# Phase 4 Measurability Gap Survey",
    "PHASE4_MEASURABILITY_GAP_REMAINING_PACKET_COUNT=3",
    "`Documentation/zigux/phase4-kprobe-example-gap-survey.md`, `zigux/tests/phase4_kprobe_example_manifest.json`, and `zigux/tests/phase4_kprobe_example_survey.zig`",
    "`Documentation/zigux/phase4-test-fsmount-gap-survey.md`, `zigux/tests/phase4_test_fsmount_manifest.json`, and `zigux/tests/phase4_test_fsmount_survey.zig`",
    "`zigux/tests/phase4_perf_baseline_manifest.json`, `zigux/tests/phase4_perf_baseline_survey.zig`, `scripts\\zigux/check_phase4_perf_baseline_packet.zig`, and `scripts\\zigux/check_phase4_perf_threshold_matrix.zig`",
    "`Documentation/zigux/phase4-validation-matrix.md`, `Documentation/zigux/phase4-gate-evidence.md`, `Documentation/zigux/phase4-reversible-delivery-evidence.md`, and `scripts\\zigux/validate_phase4.zig`",
};

const SAMPLE_PHASE4_VALIDATION_MATRIX_LINES = [_][]const u8{
    "# Phase 4 Validation Matrix",
    "scripts\\zigux/check_phase4_remaining_gap_matrix.zig",
    "Documentation/zigux/phase4-measurability-gap-survey.md",
    "zigux/tests/phase4_perf_baseline_manifest.json",
    "zigux/tests/phase4_perf_baseline_survey.zig",
    "zig build phase4-perf-baseline-survey --build-file zigux/tests/phase4_build.zig",
    "make -C zigux phase4-perf-baseline-survey",
};

const REQUIRED_RUNTIME_ATOMIC64_PACKET_MARKERS = [_][]const u8{
    "zigux/tests/atomic64_diff.zig",
    "zigux/tests/runtime_atomic64_diff.zig",
    "zigux/tests/phase4_runtime_atomic64_diff_manifest.json",
    "zigux/tests/phase4_runtime_atomic64_diff_survey.zig",
};

const CHECKS = [_][]const u8{
    "CheckSpecphase4-repo-reality-warning-self-testpythonscripts\\zigux/check_phase4_repo_reality_warning.zig--self-test",
    "CheckSpecphase4-repo-reality-warningpythonscripts\\zigux/check_phase4_repo_reality_warning.zig",
    "CheckSpecphase4-reversible-delivery-pins-self-testpythonscripts\\zigux/check_phase4_reversible_delivery_pins.zig--self-test",
    "CheckSpecphase4-reversible-delivery-pinspythonscripts\\zigux/check_phase4_reversible_delivery_pins.zig",
    "CheckSpecphase4-tests-readme-packet-self-testpythonscripts\\zigux/check_phase4_tests_readme_packet.zig--self-test",
    "CheckSpecphase4-tests-readme-packetpythonscripts\\zigux/check_phase4_tests_readme_packet.zig",
    "CheckSpecphase4-artifact-diff-helper-self-testpythonscripts/zigux/artifact_diff.zig--self-test",
    "CheckSpecphase4-artifact-diff-contract-self-testpythonscripts\\zigux/check_artifact_diff_contract.zig--self-test",
    "CheckSpecphase4-artifact-diff-contractpythonscripts\\zigux/check_artifact_diff_contract.zig",
    "CheckSpecphase4-artifact-diff-determinism-self-testpythonscripts\\zigux/check_phase4_artifact_diff_determinism.zig--self-test",
    "CheckSpecphase4-artifact-diff-determinismpythonscripts\\zigux/check_phase4_artifact_diff_determinism.zig",
    "CheckSpecphase4-artifact-diff-validator-replays-self-testpythonscripts\\zigux/check_phase4_artifact_diff_validator_replays.zig--self-test",
    "CheckSpecphase4-artifact-diff-validator-replayspythonscripts\\zigux/check_phase4_artifact_diff_validator_replays.zig",
    "CheckSpecphase4-gate-evidence-self-testpythonscripts\\zigux/check_phase4_gate_evidence.zig--self-test",
    "CheckSpecphase4-gate-evidencepythonscripts\\zigux/check_phase4_gate_evidence.zig",
    "run_phase4_runtime_atomic64_packet_check",
    "CheckSpecphase4-perf-baseline-packet-self-testpythonscripts\\zigux/check_phase4_perf_baseline_packet.zig--self-test",
    "CheckSpecphase4-perf-baseline-packetpythonscripts\\zigux/check_phase4_perf_baseline_packet.zig",
    "CheckSpecphase4-perf-threshold-matrix-self-testpythonscripts\\zigux/check_phase4_perf_threshold_matrix.zig--self-test",
    "CheckSpecphase4-perf-threshold-matrixpythonscripts\\zigux/check_phase4_perf_threshold_matrix.zig",
    "CheckSpecphase4-remaining-gap-matrix-self-testpythonscripts\\zigux/check_phase4_remaining_gap_matrix.zig--self-test",
    "CheckSpecphase4-remaining-gap-matrixpythonscripts\\zigux/check_phase4_remaining_gap_matrix.zig",
    "CheckSpecphase4-validation-lane-sequencing-self-testpythonscripts\\zigux/check_phase4_validation_lane_sequencing.zig--self-test",
    "CheckSpecphase4-validation-lane-sequencingpythonscripts\\zigux/check_phase4_validation_lane_sequencing.zig",
    "CheckSpecphase4-workflow-route-counts-self-testpythonscripts\\zigux/check_phase4_workflow_route_counts.zig--self-test",
    "CheckSpecphase4-workflow-route-countspythonscripts\\zigux/check_phase4_workflow_route_counts.zig",
    "CheckSpecphase4-build-testzigbuildtest--build-filezigux/tests/phase4_build.zig",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_workflow_route_counts_self_test_cases_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_workflow_route_counts_self_test_cases_path);
    const text_workflow_route_counts_self_test_cases = try guard.readUtf8File(io, allocator, text_workflow_route_counts_self_test_cases_path);
    defer allocator.free(text_workflow_route_counts_self_test_cases);
    for (WORKFLOW_ROUTE_COUNTS_SELF_TEST_CASES) |marker| try guard.requireMarker(text_workflow_route_counts_self_test_cases, marker);
    const text_artifact_diff_helper_self_test_cases_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_artifact_diff_helper_self_test_cases_path);
    const text_artifact_diff_helper_self_test_cases = try guard.readUtf8File(io, allocator, text_artifact_diff_helper_self_test_cases_path);
    defer allocator.free(text_artifact_diff_helper_self_test_cases);
    for (ARTIFACT_DIFF_HELPER_SELF_TEST_CASES) |marker| try guard.requireMarker(text_artifact_diff_helper_self_test_cases, marker);
    const text_phase4_tests_readme_packet_self_test_cases_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_phase4_tests_readme_packet_self_test_cases_path);
    const text_phase4_tests_readme_packet_self_test_cases = try guard.readUtf8File(io, allocator, text_phase4_tests_readme_packet_self_test_cases_path);
    defer allocator.free(text_phase4_tests_readme_packet_self_test_cases);
    for (PHASE4_TESTS_README_PACKET_SELF_TEST_CASES) |marker| try guard.requireMarker(text_phase4_tests_readme_packet_self_test_cases, marker);
    const text_required_artifact_doc_markers_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_required_artifact_doc_markers_path);
    const text_required_artifact_doc_markers = try guard.readUtf8File(io, allocator, text_required_artifact_doc_markers_path);
    defer allocator.free(text_required_artifact_doc_markers);
    for (REQUIRED_ARTIFACT_DOC_MARKERS) |marker| try guard.requireMarker(text_required_artifact_doc_markers, marker);
    const text_required_artifact_matrix_markers_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_required_artifact_matrix_markers_path);
    const text_required_artifact_matrix_markers = try guard.readUtf8File(io, allocator, text_required_artifact_matrix_markers_path);
    defer allocator.free(text_required_artifact_matrix_markers);
    for (REQUIRED_ARTIFACT_MATRIX_MARKERS) |marker| try guard.requireMarker(text_required_artifact_matrix_markers, marker);
    const text_required_measurability_gap_markers_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_required_measurability_gap_markers_path);
    const text_required_measurability_gap_markers = try guard.readUtf8File(io, allocator, text_required_measurability_gap_markers_path);
    defer allocator.free(text_required_measurability_gap_markers);
    for (REQUIRED_MEASURABILITY_GAP_MARKERS) |marker| try guard.requireMarker(text_required_measurability_gap_markers, marker);
    const text_sample_phase4_validation_matrix_lines_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_sample_phase4_validation_matrix_lines_path);
    const text_sample_phase4_validation_matrix_lines = try guard.readUtf8File(io, allocator, text_sample_phase4_validation_matrix_lines_path);
    defer allocator.free(text_sample_phase4_validation_matrix_lines);
    for (SAMPLE_PHASE4_VALIDATION_MATRIX_LINES) |marker| try guard.requireExactLineCount(text_sample_phase4_validation_matrix_lines, marker, 1);
    const text_runtime_atomic64_packet_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase4-validation-matrix.md");
    defer allocator.free(text_runtime_atomic64_packet_path);
    const text_runtime_atomic64_packet = try guard.readUtf8File(io, allocator, text_runtime_atomic64_packet_path);
    defer allocator.free(text_runtime_atomic64_packet);
    for (REQUIRED_RUNTIME_ATOMIC64_PACKET_MARKERS) |marker| try guard.requireMarker(text_runtime_atomic64_packet, marker);
    const text_checks_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_checks_path);
    const text_checks = try guard.readUtf8File(io, allocator, text_checks_path);
    defer allocator.free(text_checks);
    for (CHECKS) |marker| try guard.requireMarker(text_checks, marker);
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
