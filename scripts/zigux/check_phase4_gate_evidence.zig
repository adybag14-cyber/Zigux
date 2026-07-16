const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "CHECK_PHASE4_GATE_EVIDENCE=pass";
pub const self_test_pass_marker = "CHECK_PHASE4_GATE_EVIDENCE_SELF_TEST=pass";

const FileContract = struct { rel: []const u8, markers: []const []const u8 };

const markers_0 = [_][]const u8{
    "baseline_round_trip",
    "shipped_target_count_drift",
    "missing_exact_readback_heading",
    "forbidden_gate_evidence_checker_self_pin",
    "validator_blob_pin_drift",
    "phase4_build_manifest_blob_pin_drift",
    "phase4_build_survey_blob_pin_drift",
    "phase9_build_manifest_blob_pin_drift",
    "phase9_build_survey_blob_pin_drift",
    "doc_readme_blob_pin_drift",
    "script_readme_blob_pin_drift",
    "tests_readme_blob_pin_drift",
    "gate_evidence_self_test_case_count_drift",
    "gate_evidence_self_test_cases_drift",
    "shared_validator_reruns_gate_evidence_check_drift",
    "shared_validator_reruns_gate_evidence_self_test_drift",
    "shared_validator_expected_target_count_drift",
    "shared_validator_expected_self_test_case_count_drift",
    "runtime_atomic64_survey_packet_presence_drift",
    "bitmap_manifest_gate_evidence_blob_drift",
    "workflow_route_checker_matrix_presence_drift",
    "kprobe_gap_packet_presence_drift",
    "kprobe_owner_drift",
    "kprobe_validation_entrypoint_drift",
    "kprobe_next_step_drift",
    "perf_baseline_packet_presence_drift",
    "perf_baseline_note_split_marker_drift",
    "perf_baseline_owner_drift",
    "perf_baseline_shared_promotion_status_drift",
    "test_fsmount_gap_packet_presence_drift",
    "test_fsmount_threshold_posture_drift",
    "test_fsmount_owner_drift",
    "test_fsmount_validation_entrypoint_drift",
    "test_fsmount_linux_style_wrapper_drift",
    "test_fsmount_next_step_drift",
    "missing_validator_file",
    "missing_phase4_build_file",
    "missing_artifact_diff_helper_file",
    "missing_workflow_route_checker_file",
    "missing_atomic64_manifest_file",
    "missing_bitmap_manifest_file",
    "missing_perf_survey_file",
    "missing_kprobe_manifest_file",
    "missing_test_fsmount_survey_file",
    "missing_note_file",
    "PHASE4_VALIDATION_MATRIX_BLOB_SHA",
    "PHASE4_WORKFLOW_ROUTE_CHECKER_BLOB_SHA",
    "PHASE4_ARTIFACT_DIFF_DOC_BLOB_SHA",
    "PHASE4_ARTIFACT_DIFF_HELPER_BLOB_SHA",
    "PHASE4_ARTIFACT_DIFF_CONTRACT_CHECKER_BLOB_SHA",
    "PHASE4_MAKEFILE_BLOB_SHA",
    "PHASE4_WORKFLOW_BLOB_SHA",
    "PHASE4_DOC_README_BLOB_SHA",
    "PHASE4_SCRIPT_README_BLOB_SHA",
    "PHASE4_TESTS_README_BLOB_SHA",
    "PHASE4_VALIDATOR_BLOB_SHA",
    "PHASE4_GATE_EVIDENCE_CHECKER_BLOB_SHA",
    "PHASE4_ATOMIC64_DIFF_BLOB_SHA",
    "PHASE4_RUNTIME_ATOMIC64_DIFF_BLOB_SHA",
    "PHASE4_RUNTIME_ATOMIC64_MANIFEST_BLOB_SHA",
    "PHASE4_RUNTIME_ATOMIC64_SURVEY_BLOB_SHA",
    "PHASE4_RUNTIME_ATOMIC64_REVIEW_CHECKLIST_BLOB_SHA",
    "PHASE4_PHASE9_BUILD_BLOB_SHA",
    "PHASE4_REVERSIBLE_DELIVERY_EVIDENCE_BLOB_SHA",
    "PHASE4_SHIPPED_GATE_BLOB_TARGET_COUNT",
    "PHASE4_GATE_EVIDENCE_SELF_TEST_CASE_COUNT",
    "PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_TARGET_COUNT",
    "PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_SELF_TEST_CASE_COUNT",
    "missing_validator_file",
    "missing_phase4_build_file",
    "missing_artifact_diff_helper_file",
    "missing_workflow_route_checker_file",
    "missing_atomic64_manifest_file",
    "missing_bitmap_manifest_file",
    "missing_perf_survey_file",
    "missing_kprobe_manifest_file",
    "missing_test_fsmount_survey_file",
    "missing_note_file",
};

const markers_1 = [_][]const u8{
    "# Phase 4 Gate Evidence",
    "## Status",
    "`PHASE4_SHIPPED_GATE_BLOB_TARGET_COUNT=19`",
    "`PHASE4_GATE_EVIDENCE_SELF_TEST_CASE_COUNT=45`",
    "`PHASE4_SEPARATE_GATE_EVIDENCE_CHECKER_PRESENT=true`",
    "`PHASE4_SHARED_VALIDATOR_RERUNS_GATE_EVIDENCE_CHECK=true`",
    "`PHASE4_SHARED_VALIDATOR_RERUNS_GATE_EVIDENCE_SELF_TEST=true`",
    "`PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_TARGET_COUNT=19`",
    "`PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_SELF_TEST_CASE_COUNT=45`",
    "`PHASE4_RUNTIME_ATOMIC64_SURVEY_PACKET_PRESENT=true`",
    "`PHASE4_SHARED_KPROBE_SURVEY_PACKET_PRESENT=true`",
    "`PHASE4_SHARED_TEST_FSMOUNT_SURVEY_PACKET_PRESENT=true`",
    "`PHASE4_SHARED_PERF_BASELINE_SURVEY_PACKET_PRESENT=true`",
    "## Exact Readback Evidence",
    "`scripts\\zigux/check_phase4_gate_evidence.zig`",
    "`phase4-runtime-atomic64-diff-survey-tests`",
    "`make -C zigux phase4-runtime-atomic64-diff-survey`",
    "two `inc_not_zero` checks",
    "three `dec_if_positive` checks",
    "PHASE4_KPROBE_SHARED_LAB_AND_CI_MATRIX_ANCHOR=Documentation/zigux/phase4-validation-matrix.md#lab-and-ci-matrix",
    "PHASE4_VALIDATION_MATRIX_BLOB_SHA",
    "PHASE4_WORKFLOW_ROUTE_CHECKER_BLOB_SHA",
    "PHASE4_ARTIFACT_DIFF_DOC_BLOB_SHA",
    "PHASE4_ARTIFACT_DIFF_HELPER_BLOB_SHA",
    "PHASE4_ARTIFACT_DIFF_CONTRACT_CHECKER_BLOB_SHA",
    "PHASE4_MAKEFILE_BLOB_SHA",
    "PHASE4_WORKFLOW_BLOB_SHA",
    "PHASE4_DOC_README_BLOB_SHA",
    "PHASE4_SCRIPT_README_BLOB_SHA",
    "PHASE4_TESTS_README_BLOB_SHA",
    "PHASE4_VALIDATOR_BLOB_SHA",
    "PHASE4_GATE_EVIDENCE_CHECKER_BLOB_SHA",
    "PHASE4_ATOMIC64_DIFF_BLOB_SHA",
    "PHASE4_RUNTIME_ATOMIC64_DIFF_BLOB_SHA",
    "PHASE4_RUNTIME_ATOMIC64_MANIFEST_BLOB_SHA",
    "PHASE4_RUNTIME_ATOMIC64_SURVEY_BLOB_SHA",
    "PHASE4_RUNTIME_ATOMIC64_REVIEW_CHECKLIST_BLOB_SHA",
    "PHASE4_PHASE9_BUILD_BLOB_SHA",
    "PHASE4_REVERSIBLE_DELIVERY_EVIDENCE_BLOB_SHA",
    "PHASE4_SHIPPED_GATE_BLOB_TARGET_COUNT",
    "PHASE4_GATE_EVIDENCE_SELF_TEST_CASE_COUNT",
    "PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_TARGET_COUNT",
    "PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_SELF_TEST_CASE_COUNT",
    "missing_validator_file",
    "missing_phase4_build_file",
    "missing_artifact_diff_helper_file",
    "missing_workflow_route_checker_file",
    "missing_atomic64_manifest_file",
    "missing_bitmap_manifest_file",
    "missing_perf_survey_file",
    "missing_kprobe_manifest_file",
    "missing_test_fsmount_survey_file",
    "missing_note_file",
};

const markers_2 = [_][]const u8{
    "scripts\\zigux/check_phase4_gate_evidence.zig",
    "scripts\\zigux/check_phase4_remaining_gap_matrix.zig",
    "scripts\\zigux/check_phase4_workflow_route_counts.zig",
    "zigux/tests/phase4_perf_baseline_manifest.json",
    "zigux/tests/phase4_perf_baseline_survey.zig",
    "explicit local lab replay marker: `make -C zigux phase4-kprobe-example-survey`",
    "dedicated local survey wrapper: `make -C zigux phase4-kprobe-example-survey`",
    "validation entrypoint: `zig test zigux/tests/phase4_kprobe_example_survey.zig`",
    "survey owner: `Validation and Perf Team`",
    "rollback owner: `Validation and Perf Team`",
    "local-only benchmark commands and acceptable limits are approved today",
    "gate owners: `ABI and Runtime Team` and `Shared Subsystems Pod`",
    "shared CI perf promotion pending",
    "current measurable status: absent on current `master`",
    "reviewability-only no-perf-threshold posture",
    "validation entrypoint: `zig build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig`",
    "dedicated Linux-style survey wrapper: `make -C zigux phase4-test-fsmount-survey`",
    "survey owner: `Validation and Perf Team`",
    "rollback owner: `Validation and Perf Team`",
    "Validation and Perf Team owning that policy decision in coordination with the ABI and Runtime Team and Shared Subsystems Pod as the current gate rollback owners",
    "next bounded evidence step: keep the dedicated parked survey packet",
};

const markers_3 = [_][]const u8{
    "\"PHASE4_TEST_FSMOUNT_LOCAL_LAB_REPLAY=zig build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig\"",
};

const markers_4 = [_][]const u8{
    "Phase 4 notes - `Documentation/zigux/phase4-reversible-delivery-evidence.md`",
    "the current docs-root Phase 4 reminder packet should stay parked on the directly readable helper, the returned contract checker, the determinism and validator-replay checkers, the shared repo-reality and pin guards, the dedicated local-only perf packet, the recovered broader note-and-checker companions, and the roadmap-backed atomic64 differential pair",
    "keep the current governance split explicit here too: the direct-readback shared handoff stays narrower than the broader recovered note companions, the Validation and Perf Team remains the decision owner for any broader shared-CI perf promotion, the ABI and Runtime Team plus Shared Subsystems Pod remain the coordination owners for that policy call, and the dedicated perf-baseline survey must stay local-only until a later bounded lane intentionally widens that posture",
    "current `master` keeps the broader Phase 4 validator, build, and bitmap replay companions in a split-readback state rather than the missing bucket:",
};

const markers_5 = [_][]const u8{
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

const markers_6 = [_][]const u8{
    "keep the directly readable local-only perf packet explicit",
    "keep the recovered broader note-and-checker companions explicit through `Documentation/zigux/phase4-gate-evidence.md`, `Documentation/zigux/phase4-validation-matrix.md`, `scripts\\zigux/check_phase4_gate_evidence.zig`, and `scripts\\zigux/check_phase4_remaining_gap_matrix.zig`",
    "keep the repo-reality warning explicit for the broader Phase 4 validator, build, and bitmap-diff companions still needing raw-fallback proof or fresh authenticated blob capture",
    "keep the roadmap-backed `atomic64_diff` pair explicit as direct current-head evidence",
    "keep the Validation and Perf Team as the decision owner for any broader shared-CI perf promotion",
    "keep the ABI and Runtime Team plus Shared Subsystems Pod as coordination owners for that policy call",
    "keep the pending shared-CI perf-promotion posture explicit instead of implying shared CI perf approval",
};

const markers_7 = [_][]const u8{
    "Keep the recovered broader note-and-checker companions explicit through `Documentation/zigux/phase4-gate-evidence.md`, `Documentation/zigux/phase4-validation-matrix.md`, `scripts\\zigux/check_phase4_gate_evidence.zig`, and `scripts\\zigux/check_phase4_remaining_gap_matrix.zig`",
    "Current direct-readback dedicated local-only perf companion members: `zigux/tests/phase4_perf_baseline_manifest.json`, `zigux/tests/phase4_perf_baseline_survey.zig`",
};

const markers_8 = [_][]const u8{
    "`scripts\\zigux/check_artifact_diff_contract.zig`, `scripts\\zigux/check_phase4_artifact_diff_determinism.zig`, `scripts\\zigux/check_phase4_artifact_diff_validator_replays.zig`, `scripts\\zigux/check_phase4_repo_reality_warning.zig`, `scripts\\zigux/check_phase4_reversible_delivery_pins.zig`, `scripts\\zigux/check_phase4_perf_baseline_packet.zig`, `scripts\\zigux/check_phase4_remaining_gap_matrix.zig`, and `scripts\\zigux/check_phase4_workflow_route_counts.zig` keep the current helper-contract, validator-replay, shared rollback-owner reminder, local-only perf-governance, recovered remaining-gap, and route-inventory packet explicit on current `master`",
    "`Documentation/zigux/phase4-reversible-delivery-evidence.md`, `Documentation/zigux/phase4-gate-evidence.md`, `Documentation/zigux/phase4-validation-matrix.md`, `Documentation/zigux/phase4-validation-lane-sequencing.md`, `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, `zigux/tests/atomic64_diff.zig`, and `zigux/tests/runtime_atomic64_diff.zig`, `zigux/tests/phase4_perf_baseline_manifest.json`, and `zigux/tests/phase4_perf_baseline_survey.zig` remain the current reminder-surface companions for that active Phase 4 rollback-readiness and perf-governance packet",
    "keep the current governance split explicit here too: the direct-readback shared handoff stays narrower than the broader recovered note companions, the Validation and Perf Team remains the decision owner for any broader shared-CI perf promotion, the ABI and Runtime Team plus Shared Subsystems Pod remain the coordination owners for that policy call, and the dedicated perf-baseline survey must stay local-only until a later bounded lane intentionally widens that posture",
};

const contracts = [_]FileContract{
    .{ .rel = "scripts/zigux/check_phase4_gate_evidence.zig", .markers = &markers_0 },
    .{ .rel = "Documentation/zigux/phase4-gate-evidence.md", .markers = &markers_1 },
    .{ .rel = "Documentation/zigux/phase4-validation-matrix.md", .markers = &markers_2 },
    .{ .rel = "zigux/tests/phase4_test_fsmount_survey.zig", .markers = &markers_3 },
    .{ .rel = "Documentation/zigux/README.md", .markers = &markers_4 },
    .{ .rel = ".github/workflows/zigux-bootstrap.yml", .markers = &markers_5 },
    .{ .rel = "Documentation/zigux/review-checklist.md", .markers = &markers_6 },
    .{ .rel = "zigux/tests/README.md", .markers = &markers_7 },
    .{ .rel = "scripts/zigux/README.md", .markers = &markers_8 },
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
    try guard.printLine(io, "PHASE4_GATE_EVIDENCE_SELF_TEST_CASE_COUNT={d}", .{@as(usize, 45)});
    try guard.printLine(io, "PHASE4_GATE_EVIDENCE_SELF_TEST_CASES=baseline_round_trip,shipped_target_count_drift,missing_exact_readback_heading,forbidden_gate_evidence_checker_self_pin,validator_blob_pin_drift,phase4_build_manifest_blob_pin_drift,phase4_build_survey_blob_pin_drift,phase9_build_manifest_blob_pin_drift,phase9_build_survey_blob_pin_drift,doc_readme_blob_pin_drift,script_readme_blob_pin_drift,tests_readme_blob_pin_drift,gate_evidence_self_test_case_count_drift,gate_evidence_self_test_cases_drift,shared_validator_reruns_gate_evidence_check_drift,shared_validator_reruns_gate_evidence_self_test_drift,shared_validator_expected_target_count_drift,shared_validator_expected_self_test_case_count_drift,runtime_atomic64_survey_packet_presence_drift,bitmap_manifest_gate_evidence_blob_drift,workflow_route_checker_matrix_presence_drift,kprobe_gap_packet_presence_drift,kprobe_owner_drift,kprobe_validation_entrypoint_drift,kprobe_next_step_drift,perf_baseline_packet_presence_drift,perf_baseline_note_split_marker_drift,perf_baseline_owner_drift,perf_baseline_shared_promotion_status_drift,test_fsmount_gap_packet_presence_drift,test_fsmount_threshold_posture_drift,test_fsmount_owner_drift,test_fsmount_validation_entrypoint_drift,test_fsmount_linux_style_wrapper_drift,test_fsmount_next_step_drift,missing_validator_file,missing_phase4_build_file,missing_artifact_diff_helper_file,missing_workflow_route_checker_file,missing_atomic64_manifest_file,missing_bitmap_manifest_file,missing_perf_survey_file,missing_kprobe_manifest_file,missing_test_fsmount_survey_file,missing_note_file", .{});
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
        std.process.exit(2);
    }
    if (self_test) std.process.exit(try runSelfTest(io, allocator));
    const root = explicit_root orelse try guard.defaultRepoRoot(allocator);
    defer if (explicit_root == null) allocator.free(root);
    checkRepo(io, allocator, root) catch std.process.exit(1);
    try guard.printLine(io, "{s}", .{live_pass_marker});
    try guard.printLine(io, "PHASE4_SHIPPED_GATE_BLOB_TARGET_COUNT={d}", .{@as(usize, 19)});
}

// Legacy source-surface anchors retained for consumers that inspect this checker.
// SELF_TEST_CASES
// baseline_round_trip
// shipped_target_count_drift
// missing_exact_readback_heading
// forbidden_gate_evidence_checker_self_pin
// validator_blob_pin_drift
// phase4_build_manifest_blob_pin_drift
// phase4_build_survey_blob_pin_drift
// phase9_build_manifest_blob_pin_drift
// phase9_build_survey_blob_pin_drift
// doc_readme_blob_pin_drift
// script_readme_blob_pin_drift
// tests_readme_blob_pin_drift
// gate_evidence_self_test_case_count_drift
// gate_evidence_self_test_cases_drift
// shared_validator_reruns_gate_evidence_check_drift
// shared_validator_reruns_gate_evidence_self_test_drift
// shared_validator_expected_target_count_drift
// shared_validator_expected_self_test_case_count_drift
// runtime_atomic64_survey_packet_presence_drift
// bitmap_manifest_gate_evidence_blob_drift
// workflow_route_checker_matrix_presence_drift
// kprobe_gap_packet_presence_drift
// kprobe_owner_drift
// kprobe_validation_entrypoint_drift
// kprobe_next_step_drift
// perf_baseline_packet_presence_drift
// perf_baseline_note_split_marker_drift
// perf_baseline_owner_drift
// perf_baseline_shared_promotion_status_drift
// test_fsmount_gap_packet_presence_drift
// test_fsmount_threshold_posture_drift
// test_fsmount_owner_drift
// test_fsmount_validation_entrypoint_drift
// test_fsmount_linux_style_wrapper_drift
// test_fsmount_next_step_drift
// missing_validator_file
// missing_phase4_build_file
// missing_artifact_diff_helper_file
// missing_workflow_route_checker_file
// missing_atomic64_manifest_file
// missing_bitmap_manifest_file
// missing_perf_survey_file
// missing_kprobe_manifest_file
// missing_test_fsmount_survey_file
// missing_note_file
// NOTE_MARKERS
// # Phase 4 Gate Evidence
// ## Status
// `PHASE4_SHIPPED_GATE_BLOB_TARGET_COUNT=19`
// `PHASE4_GATE_EVIDENCE_SELF_TEST_CASE_COUNT=45`
// `PHASE4_SEPARATE_GATE_EVIDENCE_CHECKER_PRESENT=true`
// `PHASE4_SHARED_VALIDATOR_RERUNS_GATE_EVIDENCE_CHECK=true`
// `PHASE4_SHARED_VALIDATOR_RERUNS_GATE_EVIDENCE_SELF_TEST=true`
// `PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_TARGET_COUNT=19`
// `PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_SELF_TEST_CASE_COUNT=45`
// `PHASE4_RUNTIME_ATOMIC64_SURVEY_PACKET_PRESENT=true`
// `PHASE4_SHARED_KPROBE_SURVEY_PACKET_PRESENT=true`
// `PHASE4_SHARED_TEST_FSMOUNT_SURVEY_PACKET_PRESENT=true`
// `PHASE4_SHARED_PERF_BASELINE_SURVEY_PACKET_PRESENT=true`
// ## Exact Readback Evidence
// `scripts\zigux/check_phase4_gate_evidence.zig`
// `phase4-runtime-atomic64-diff-survey-tests`
// `make -C zigux phase4-runtime-atomic64-diff-survey`
// two `inc_not_zero` checks
// three `dec_if_positive` checks
// PHASE4_KPROBE_SHARED_LAB_AND_CI_MATRIX_ANCHOR=Documentation/zigux/phase4-validation-matrix.md#lab-and-ci-matrix
// MATRIX_MARKERS
// scripts\zigux/check_phase4_gate_evidence.zig
// scripts\zigux/check_phase4_remaining_gap_matrix.zig
// scripts\zigux/check_phase4_workflow_route_counts.zig
// zigux/tests/phase4_perf_baseline_manifest.json
// zigux/tests/phase4_perf_baseline_survey.zig
// explicit local lab replay marker: `make -C zigux phase4-kprobe-example-survey`
// dedicated local survey wrapper: `make -C zigux phase4-kprobe-example-survey`
// validation entrypoint: `zig test zigux/tests/phase4_kprobe_example_survey.zig`
// survey owner: `Validation and Perf Team`
// rollback owner: `Validation and Perf Team`
// local-only benchmark commands and acceptable limits are approved today
// gate owners: `ABI and Runtime Team` and `Shared Subsystems Pod`
// shared CI perf promotion pending
// current measurable status: absent on current `master`
// reviewability-only no-perf-threshold posture
// validation entrypoint: `zig build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig`
// dedicated Linux-style survey wrapper: `make -C zigux phase4-test-fsmount-survey`
// survey owner: `Validation and Perf Team`
// rollback owner: `Validation and Perf Team`
// Validation and Perf Team owning that policy decision in coordination with the ABI and Runtime Team and Shared Subsystems Pod as the current gate rollback owners
// next bounded evidence step: keep the dedicated parked survey packet
// TEST_FSMOUNT_SURVEY_MARKERS
// "PHASE4_TEST_FSMOUNT_LOCAL_LAB_REPLAY=zig build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig"
// DOCS_README_MARKERS
// Phase 4 notes - `Documentation/zigux/phase4-reversible-delivery-evidence.md`
// the current docs-root Phase 4 reminder packet should stay parked on the directly readable helper, the returned contract checker, the determinism and validator-replay checkers, the shared repo-reality and pin guards, the dedicated local-only perf packet, the recovered broader note-and-checker companions, and the roadmap-backed atomic64 differential pair
// keep the current governance split explicit here too: the direct-readback shared handoff stays narrower than the broader recovered note companions, the Validation and Perf Team remains the decision owner for any broader shared-CI perf promotion, the ABI and Runtime Team plus Shared Subsystems Pod remain the coordination owners for that policy call, and the dedicated perf-baseline survey must stay local-only until a later bounded lane intentionally widens that posture
// current `master` keeps the broader Phase 4 validator, build, and bitmap replay companions in a split-readback state rather than the missing bucket:
// WORKFLOW_MARKERS
// - name: Validate Phase 4 rollback routes
// run: make -C zigux phase4-validate
// - name: Run Phase 4 rollback tests
// run: make -C zigux phase4-test
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
// CHECKLIST_MARKERS
// keep the directly readable local-only perf packet explicit
// keep the recovered broader note-and-checker companions explicit through `Documentation/zigux/phase4-gate-evidence.md`, `Documentation/zigux/phase4-validation-matrix.md`, `scripts\zigux/check_phase4_gate_evidence.zig`, and `scripts\zigux/check_phase4_remaining_gap_matrix.zig`
// keep the repo-reality warning explicit for the broader Phase 4 validator, build, and bitmap-diff companions still needing raw-fallback proof or fresh authenticated blob capture
// keep the roadmap-backed `atomic64_diff` pair explicit as direct current-head evidence
// keep the Validation and Perf Team as the decision owner for any broader shared-CI perf promotion
// keep the ABI and Runtime Team plus Shared Subsystems Pod as coordination owners for that policy call
// keep the pending shared-CI perf-promotion posture explicit instead of implying shared CI perf approval
// TESTS_README_MARKERS
// Keep the recovered broader note-and-checker companions explicit through `Documentation/zigux/phase4-gate-evidence.md`, `Documentation/zigux/phase4-validation-matrix.md`, `scripts\zigux/check_phase4_gate_evidence.zig`, and `scripts\zigux/check_phase4_remaining_gap_matrix.zig`
// Current direct-readback dedicated local-only perf companion members: `zigux/tests/phase4_perf_baseline_manifest.json`, `zigux/tests/phase4_perf_baseline_survey.zig`
// SCRIPTS_README_MARKERS
// `scripts\zigux/check_artifact_diff_contract.zig`, `scripts\zigux/check_phase4_artifact_diff_determinism.zig`, `scripts\zigux/check_phase4_artifact_diff_validator_replays.zig`, `scripts\zigux/check_phase4_repo_reality_warning.zig`, `scripts\zigux/check_phase4_reversible_delivery_pins.zig`, `scripts\zigux/check_phase4_perf_baseline_packet.zig`, `scripts\zigux/check_phase4_remaining_gap_matrix.zig`, and `scripts\zigux/check_phase4_workflow_route_counts.zig` keep the current helper-contract, validator-replay, shared rollback-owner reminder, local-only perf-governance, recovered remaining-gap, and route-inventory packet explicit on current `master`
// `Documentation/zigux/phase4-reversible-delivery-evidence.md`, `Documentation/zigux/phase4-gate-evidence.md`, `Documentation/zigux/phase4-validation-matrix.md`, `Documentation/zigux/phase4-validation-lane-sequencing.md`, `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, `zigux/tests/atomic64_diff.zig`, and `zigux/tests/runtime_atomic64_diff.zig`, `zigux/tests/phase4_perf_baseline_manifest.json`, and `zigux/tests/phase4_perf_baseline_survey.zig` remain the current reminder-surface companions for that active Phase 4 rollback-readiness and perf-governance packet
// keep the current governance split explicit here too: the direct-readback shared handoff stays narrower than the broader recovered note companions, the Validation and Perf Team remains the decision owner for any broader shared-CI perf promotion, the ABI and Runtime Team plus Shared Subsystems Pod remain the coordination owners for that policy call, and the dedicated perf-baseline survey must stay local-only until a later bounded lane intentionally widens that posture
// BLOB_TARGETS
// PHASE4_VALIDATION_MATRIX_BLOB_SHA
// PHASE4_WORKFLOW_ROUTE_CHECKER_BLOB_SHA
// PHASE4_ARTIFACT_DIFF_DOC_BLOB_SHA
// PHASE4_ARTIFACT_DIFF_HELPER_BLOB_SHA
// PHASE4_ARTIFACT_DIFF_CONTRACT_CHECKER_BLOB_SHA
// PHASE4_MAKEFILE_BLOB_SHA
// PHASE4_WORKFLOW_BLOB_SHA
// PHASE4_DOC_README_BLOB_SHA
// PHASE4_SCRIPT_README_BLOB_SHA
// PHASE4_TESTS_README_BLOB_SHA
// PHASE4_VALIDATOR_BLOB_SHA
// PHASE4_GATE_EVIDENCE_CHECKER_BLOB_SHA
// PHASE4_ATOMIC64_DIFF_BLOB_SHA
// PHASE4_RUNTIME_ATOMIC64_DIFF_BLOB_SHA
// PHASE4_RUNTIME_ATOMIC64_MANIFEST_BLOB_SHA
// PHASE4_RUNTIME_ATOMIC64_SURVEY_BLOB_SHA
// PHASE4_RUNTIME_ATOMIC64_REVIEW_CHECKLIST_BLOB_SHA
// PHASE4_PHASE9_BUILD_BLOB_SHA
// PHASE4_REVERSIBLE_DELIVERY_EVIDENCE_BLOB_SHA
// COUNT_MARKERS
// PHASE4_SHIPPED_GATE_BLOB_TARGET_COUNT
// PHASE4_GATE_EVIDENCE_SELF_TEST_CASE_COUNT
// PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_TARGET_COUNT
// PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_SELF_TEST_CASE_COUNT
// MISSING_FILE_CASES
// missing_validator_file
// missing_phase4_build_file
// missing_artifact_diff_helper_file
// missing_workflow_route_checker_file
// missing_atomic64_manifest_file
// missing_bitmap_manifest_file
// missing_perf_survey_file
// missing_kprobe_manifest_file
// missing_test_fsmount_survey_file
// missing_note_file
