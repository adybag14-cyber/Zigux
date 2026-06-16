const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "CHECK_PHASE4_GATE_EVIDENCE=pass";
pub const self_test_pass_marker = "CHECK_PHASE4_GATE_EVIDENCE_SELF_TEST=pass";

const SELF_TEST_CASES = [_][]const u8{
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
};

const NOTE_MARKERS = [_][]const u8{
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
};

const MATRIX_MARKERS = [_][]const u8{
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

const TEST_FSMOUNT_SURVEY_MARKERS = [_][]const u8{
    "\"PHASE4_TEST_FSMOUNT_LOCAL_LAB_REPLAY=zig build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig\"",
};

const DOCS_README_MARKERS = [_][]const u8{
    "Phase 4 notes - `Documentation/zigux/phase4-reversible-delivery-evidence.md`",
    "the current docs-root Phase 4 reminder packet should stay parked on the directly readable helper, the returned contract checker, the determinism and validator-replay checkers, the shared repo-reality and pin guards, the dedicated local-only perf packet, the recovered broader note-and-checker companions, and the roadmap-backed atomic64 differential pair",
    "keep the current governance split explicit here too: the direct-readback shared handoff stays narrower than the broader recovered note companions, the Validation and Perf Team remains the decision owner for any broader shared-CI perf promotion, the ABI and Runtime Team plus Shared Subsystems Pod remain the coordination owners for that policy call, and the dedicated perf-baseline survey must stay local-only until a later bounded lane intentionally widens that posture",
    "current `master` keeps the broader Phase 4 validator, build, and bitmap replay companions in a split-readback state rather than the missing bucket:",
};

const WORKFLOW_MARKERS = [_][]const u8{
    "- name: Validate Phase 4 rollback routes",
    "run: make -C zigux phase4-validate",
    "- name: Run Phase 4 rollback tests",
    "run: make -C zigux phase4-test",
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

const CHECKLIST_MARKERS = [_][]const u8{
    "keep the directly readable local-only perf packet explicit",
    "keep the recovered broader note-and-checker companions explicit through `Documentation/zigux/phase4-gate-evidence.md`, `Documentation/zigux/phase4-validation-matrix.md`, `scripts\\zigux/check_phase4_gate_evidence.zig`, and `scripts\\zigux/check_phase4_remaining_gap_matrix.zig`",
    "keep the repo-reality warning explicit for the broader Phase 4 validator, build, and bitmap-diff companions still needing raw-fallback proof or fresh authenticated blob capture",
    "keep the roadmap-backed `atomic64_diff` pair explicit as direct current-head evidence",
    "keep the Validation and Perf Team as the decision owner for any broader shared-CI perf promotion",
    "keep the ABI and Runtime Team plus Shared Subsystems Pod as coordination owners for that policy call",
    "keep the pending shared-CI perf-promotion posture explicit instead of implying shared CI perf approval",
};

const TESTS_README_MARKERS = [_][]const u8{
    "Keep the recovered broader note-and-checker companions explicit through `Documentation/zigux/phase4-gate-evidence.md`, `Documentation/zigux/phase4-validation-matrix.md`, `scripts\\zigux/check_phase4_gate_evidence.zig`, and `scripts\\zigux/check_phase4_remaining_gap_matrix.zig`",
    "Current direct-readback dedicated local-only perf companion members: `zigux/tests/phase4_perf_baseline_manifest.json`, `zigux/tests/phase4_perf_baseline_survey.zig`",
};

const SCRIPTS_README_MARKERS = [_][]const u8{
    "`scripts\\zigux/check_artifact_diff_contract.zig`, `scripts\\zigux/check_phase4_artifact_diff_determinism.zig`, `scripts\\zigux/check_phase4_artifact_diff_validator_replays.zig`, `scripts\\zigux/check_phase4_repo_reality_warning.zig`, `scripts\\zigux/check_phase4_reversible_delivery_pins.zig`, `scripts\\zigux/check_phase4_perf_baseline_packet.zig`, `scripts\\zigux/check_phase4_remaining_gap_matrix.zig`, and `scripts\\zigux/check_phase4_workflow_route_counts.zig` keep the current helper-contract, validator-replay, shared rollback-owner reminder, local-only perf-governance, recovered remaining-gap, and route-inventory packet explicit on current `master`",
    "`Documentation/zigux/phase4-reversible-delivery-evidence.md`, `Documentation/zigux/phase4-gate-evidence.md`, `Documentation/zigux/phase4-validation-matrix.md`, `Documentation/zigux/phase4-validation-lane-sequencing.md`, `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, `zigux/tests/atomic64_diff.zig`, and `zigux/tests/runtime_atomic64_diff.zig`, `zigux/tests/phase4_perf_baseline_manifest.json`, and `zigux/tests/phase4_perf_baseline_survey.zig` remain the current reminder-surface companions for that active Phase 4 rollback-readiness and perf-governance packet",
    "keep the current governance split explicit here too: the direct-readback shared handoff stays narrower than the broader recovered note companions, the Validation and Perf Team remains the decision owner for any broader shared-CI perf promotion, the ABI and Runtime Team plus Shared Subsystems Pod remain the coordination owners for that policy call, and the dedicated perf-baseline survey must stay local-only until a later bounded lane intentionally widens that posture",
};

const BLOB_TARGETS = [_][]const u8{
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
};

const COUNT_MARKERS = [_][]const u8{
    "PHASE4_SHIPPED_GATE_BLOB_TARGET_COUNT",
    "PHASE4_GATE_EVIDENCE_SELF_TEST_CASE_COUNT",
    "PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_TARGET_COUNT",
    "PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_SELF_TEST_CASE_COUNT",
};

const MISSING_FILE_CASES = [_][]const u8{
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

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_self_test_cases_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_self_test_cases_path);
    const text_self_test_cases = try guard.readUtf8File(io, allocator, text_self_test_cases_path);
    defer allocator.free(text_self_test_cases);
    for (SELF_TEST_CASES) |marker| try guard.requireMarker(text_self_test_cases, marker);
    const text_note_markers_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase4-gate-evidence.md");
    defer allocator.free(text_note_markers_path);
    const text_note_markers = try guard.readUtf8File(io, allocator, text_note_markers_path);
    defer allocator.free(text_note_markers);
    for (NOTE_MARKERS) |marker| try guard.requireMarker(text_note_markers, marker);
    const text_matrix_markers_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase4-validation-matrix.md");
    defer allocator.free(text_matrix_markers_path);
    const text_matrix_markers = try guard.readUtf8File(io, allocator, text_matrix_markers_path);
    defer allocator.free(text_matrix_markers);
    for (MATRIX_MARKERS) |marker| try guard.requireMarker(text_matrix_markers, marker);
    const text_test_fsmount_survey_markers_path = try guard.joinPath(allocator, root, "zigux/tests/phase4_test_fsmount_survey.zig");
    defer allocator.free(text_test_fsmount_survey_markers_path);
    const text_test_fsmount_survey_markers = try guard.readUtf8File(io, allocator, text_test_fsmount_survey_markers_path);
    defer allocator.free(text_test_fsmount_survey_markers);
    for (TEST_FSMOUNT_SURVEY_MARKERS) |marker| try guard.requireMarker(text_test_fsmount_survey_markers, marker);
    const text_docs_readme_markers_path = try guard.joinPath(allocator, root, "Documentation/zigux/README.md");
    defer allocator.free(text_docs_readme_markers_path);
    const text_docs_readme_markers = try guard.readUtf8File(io, allocator, text_docs_readme_markers_path);
    defer allocator.free(text_docs_readme_markers);
    for (DOCS_README_MARKERS) |marker| try guard.requireMarker(text_docs_readme_markers, marker);
    const text_workflow_markers_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_workflow_markers_path);
    const text_workflow_markers = try guard.readUtf8File(io, allocator, text_workflow_markers_path);
    defer allocator.free(text_workflow_markers);
    for (WORKFLOW_MARKERS) |marker| try guard.requireMarker(text_workflow_markers, marker);
    const text_checklist_markers_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_checklist_markers_path);
    const text_checklist_markers = try guard.readUtf8File(io, allocator, text_checklist_markers_path);
    defer allocator.free(text_checklist_markers);
    for (CHECKLIST_MARKERS) |marker| try guard.requireMarker(text_checklist_markers, marker);
    const text_tests_readme_markers_path = try guard.joinPath(allocator, root, "zigux/tests/README.md");
    defer allocator.free(text_tests_readme_markers_path);
    const text_tests_readme_markers = try guard.readUtf8File(io, allocator, text_tests_readme_markers_path);
    defer allocator.free(text_tests_readme_markers);
    for (TESTS_README_MARKERS) |marker| try guard.requireMarker(text_tests_readme_markers, marker);
    const text_scripts_readme_markers_path = try guard.joinPath(allocator, root, "scripts/zigux/README.md");
    defer allocator.free(text_scripts_readme_markers_path);
    const text_scripts_readme_markers = try guard.readUtf8File(io, allocator, text_scripts_readme_markers_path);
    defer allocator.free(text_scripts_readme_markers);
    for (SCRIPTS_README_MARKERS) |marker| try guard.requireMarker(text_scripts_readme_markers, marker);
    const text_blob_targets_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_blob_targets_path);
    const text_blob_targets = try guard.readUtf8File(io, allocator, text_blob_targets_path);
    defer allocator.free(text_blob_targets);
    for (BLOB_TARGETS) |marker| try guard.requireMarker(text_blob_targets, marker);
    const text_count_markers_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_count_markers_path);
    const text_count_markers = try guard.readUtf8File(io, allocator, text_count_markers_path);
    defer allocator.free(text_count_markers);
    for (COUNT_MARKERS) |marker| try guard.requireMarker(text_count_markers, marker);
    const text_missing_file_cases_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_missing_file_cases_path);
    const text_missing_file_cases = try guard.readUtf8File(io, allocator, text_missing_file_cases_path);
    defer allocator.free(text_missing_file_cases);
    for (MISSING_FILE_CASES) |marker| try guard.requireMarker(text_missing_file_cases, marker);
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
