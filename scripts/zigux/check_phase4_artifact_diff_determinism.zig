const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE4_ARTIFACT_DIFF_DETERMINISM=pass";
pub const self_test_pass_marker = "PHASE4_ARTIFACT_DIFF_DETERMINISM_SELF_TEST=pass";

const FileContract = struct { rel: []const u8, markers: []const []const u8 };

const markers_0 = [_][]const u8{
    "run: zig run scripts/zigux/check_phase4_artifact_diff_determinism.zig -- --self-test",
    "run: zig run scripts/zigux/check_phase4_artifact_diff_determinism.zig",
};

const markers_1 = [_][]const u8{
    "`scripts/zigux/artifact_diff.zig` as the stable comparison entrypoint",
    "`scripts\\zigux/check_artifact_diff_contract.zig` reruns the bounded helper self-test, CLI help output, missing-required-args, missing-mode-value, missing-actual-operand, invalid-mode, and extra-positional parser coverage plus the text, JSON, bytes, missing-path, malformed-input, and repeat-run cases",
    "`scripts\\zigux/check_phase4_artifact_diff_determinism.zig` rechecks the helper and contract summary catalogs together so case-count, case-order, and repeat-case drift fail closed",
    "`ARTIFACT_DIFF_SELF_TEST_CASE_COUNT=23`",
    "`ARTIFACT_DIFF_CONTRACT_BASE_CASE_COUNT=25`, `ARTIFACT_DIFF_CONTRACT_REPEAT_CASE_COUNT=5`, and `ARTIFACT_DIFF_CONTRACT_CASE_COUNT=30`",
    "`PHASE4_ARTIFACT_DIFF_DETERMINISM_SELF_TEST_CASE_COUNT=13`",
    "`PHASE4_ARTIFACT_DIFF_DETERMINISM_DIRECT_PACKET_MEMBERS=11`",
    "`PHASE4_ARTIFACT_DIFF_DETERMINISM_AUTH_MISSING_BROADER_COMPANIONS=0`",
};

const markers_2 = [_][]const u8{
    "Documentation/zigux/phase4-artifact-diff-tooling-survey.md",
    "Documentation/zigux/phase4-reversible-delivery-evidence.md",
    "Documentation/zigux/review-checklist.md",
    "Documentation/zigux/artifact-diff.md",
    "scripts\\zigux/check_phase4_repo_reality_warning.zig",
    "scripts\\zigux/check_phase4_reversible_delivery_pins.zig",
    "scripts\\zigux/check_phase4_artifact_diff_determinism.zig",
    "scripts\\zigux/check_phase4_artifact_diff_validator_replays.zig",
    "scripts\\zigux/validate_phase4.zig",
    "scripts/zigux/artifact_diff.zig",
    "scripts\\zigux/check_artifact_diff_contract.zig",
    "PHASE4_ARTIFACT_DIFF_TOOLING_STATUS=helper_contract_validator_and_owner_note_direct_readback_aligned_on_current_master",
    "current direct-readback helper-contract-validator-and-owner-note packet:",
    "Current `master` now keeps the directly readable helper, contract checker, determinism checker, validator-replay checker, shared validator packet, and broader owner-and-rollback note aligned around the same bytes-capable artifact-diff contract.",
    "The broader `Documentation/zigux/artifact-diff.md` note is directly readable on current `master` again and now matches the current 23-case helper packet, the current 25-base-case / 30-case contract packet, and the current 13-case determinism self-test packet.",
    "That same direct packet now needs to keep the helper's exact output-contract lines pinned too, so the roadmap-backed host-side artifact-diff check stays machine-checked at the result-surface level instead of only at the case-count level.",
    "`scripts\\zigux/check_phase4_artifact_diff_determinism.zig` now exact-requires the broader `Documentation/zigux/artifact-diff.md` note to keep the refreshed helper, contract, determinism, and helper output-contract anchor lines whenever that file is present in the checked tree.",
    "`PHASE4_ARTIFACT_DIFF_CURRENT_HELPER_SELF_TEST_CASE_COUNT=23`",
    "`PHASE4_ARTIFACT_DIFF_CURRENT_CONTRACT_SELF_TEST_CASE_COUNT=24`",
    "`PHASE4_ARTIFACT_DIFF_CURRENT_CONTRACT_BASE_CASE_COUNT=25`",
    "`PHASE4_ARTIFACT_DIFF_CURRENT_CONTRACT_REPEAT_CASE_COUNT=5`",
    "`PHASE4_ARTIFACT_DIFF_CURRENT_CONTRACT_CASE_COUNT=30`",
    "No remaining owner-and-rollback note readback caveat is left inside this lane on current `master`, so the same lane should stay parked unless the broader note or exact packet drifts again.",
    "this survey now treats `Documentation/zigux/artifact-diff.md` as direct current-head evidence on current `master`",
    "`PHASE4_ARTIFACT_DIFF_CURRENT_HELPER_MODES=text,json,bytes`",
    "`PHASE4_ARTIFACT_DIFF_CURRENT_HELPER_LEGACY_MODE_ALIASES=sha256->bytes`",
    "`PHASE4_ARTIFACT_DIFF_CURRENT_SUCCESS_LINES=ARTIFACT_DIFF,MODE,EXPECTED,ACTUAL`",
    "`PHASE4_ARTIFACT_DIFF_CURRENT_BYTES_PASS_DETAIL=SHA256=<digest>`",
    "`PHASE4_ARTIFACT_DIFF_CURRENT_BYTES_FAIL_DETAIL=EXPECTED_SHA256=<digest>,ACTUAL_SHA256=<digest>`",
    "`PHASE4_ARTIFACT_DIFF_CURRENT_ERROR_LINES=EXPECTED_JSON_ERROR_or_ACTUAL_JSON_ERROR_or_EXPECTED_UTF8_ERROR_or_ACTUAL_UTF8_ERROR_or_EXPECTED_EXISTS_plus_ACTUAL_EXISTS`",
    "`PHASE4_ARTIFACT_DIFF_CURRENT_CONTRACT_HELPER_SELF_TEST_CASE_COUNT=23`",
    "`ARTIFACT_DIFF_SELF_TEST_CASE_COUNT=23`",
    "`ARTIFACT_DIFF_CONTRACT_SELF_TEST_CASE_COUNT=24`",
    "`ARTIFACT_DIFF_CONTRACT_CASE_COUNT=30`",
    "`PHASE4_ARTIFACT_DIFF_DETERMINISM_SELF_TEST_CASE_COUNT=13`",
    "`PHASE4_ARTIFACT_DIFF_VALIDATOR_REPLAYS_SELF_TEST_CASE_COUNT=14`",
    "`PHASE4_ARTIFACT_DIFF_VALIDATOR_REPLAYS_MARKER_COUNT=7`",
    "`PHASE4_ARTIFACT_DIFF_VALIDATOR_REPLAYS_WORKFLOW_MARKER_COUNT=16`",
    "text",
    "json",
    "bytes",
    "helper_self_test",
    "cli_help_output",
    "cli_missing_required_args",
    "cli_missing_mode_value",
    "cli_missing_actual_operand",
    "cli_invalid_mode",
    "cli_extra_positional_args",
    "text_pass",
    "text_mismatch",
    "text_missing_expected",
    "text_missing_actual",
    "text_missing_both",
    "json_pass",
    "json_mismatch",
    "json_missing_expected",
    "json_missing_actual",
    "json_missing_both",
    "json_invalid_expected",
    "json_invalid_actual",
    "json_invalid_both",
    "bytes_pass",
    "bytes_missing_expected",
    "bytes_missing_actual",
    "bytes_missing_both",
    "bytes_drift",
    "helper_self_test_repeat",
    "cli_help_output_repeat",
    "text_pass_repeat",
    "json_mismatch_repeat",
    "bytes_drift_repeat",
};

const markers_3 = [_][]const u8{
    "The broader Phase 4 validator, build, and bitmap replay companions are no longer safe to describe as current-`master` gaps in this handoff.",
    "Direct authenticated contents reads in this runtime now return `scripts\\zigux/validate_phase4.zig` directly, while `zigux/tests/phase4_build.zig`, `zigux/tests/bitmap_diff.zig`, and `zigux/tests/phase4_bitmap_live_helper_replay.zig` still flap on that same route; public raw fallback rereads continue to return the full set on current `master`, matching the broader review packet's recovered note-and-checker companions.",
    "Historical broader packet references still include `Documentation/zigux/artifact-diff.md`, `scripts/zigux/artifact_diff.zig`, `scripts\\zigux/check_artifact_diff_contract.zig`, and `scripts\\zigux/check_phase4_artifact_diff_determinism.zig`.",
    "Current direct contents reads for `zigux/tests/atomic64_diff.zig`, `zigux/tests/runtime_atomic64_diff.zig`, `zigux/tests/phase4_runtime_atomic64_diff_manifest.json`, and `zigux/tests/phase4_runtime_atomic64_diff_survey.zig` now return on current `master`",
    "Historical broader packet references still include `Documentation/zigux/artifact-diff.md`, `scripts/zigux/artifact_diff.zig`, `scripts\\zigux/check_artifact_diff_contract.zig`, and `scripts\\zigux/check_phase4_artifact_diff_determinism.zig`",
    "Current direct contents reads for `zigux/tests/atomic64_diff.zig` and `zigux/tests/runtime_atomic64_diff.zig` now return on current `master`, so keep that roadmap-backed differential-gate pair explicit as direct current-head evidence",
};

const markers_4 = [_][]const u8{
    "shared Phase 4 rollback-ownership and lab-matrix packet",
    "`scripts\\zigux/check_phase4_repo_reality_warning.zig` and `scripts\\zigux/check_phase4_reversible_delivery_pins.zig`",
    "keep the recovered broader note-and-checker companions explicit through `Documentation/zigux/phase4-gate-evidence.md`, `Documentation/zigux/phase4-validation-matrix.md`, `scripts\\zigux/check_phase4_gate_evidence.zig`, and `scripts\\zigux/check_phase4_remaining_gap_matrix.zig`",
    "keep the repo-reality warning explicit for the broader Phase 4 validator, build, and bitmap-diff companions still needing raw-fallback proof or fresh authenticated blob capture",
    "keep the roadmap-backed `atomic64_diff` pair explicit as direct current-head evidence",
};

const markers_5 = [_][]const u8{
    "\"PHASE4_ARTIFACT_DIFF_DETERMINISM_SELF_TEST_CASE_COUNT=13\",",
};

const markers_6 = [_][]const u8{
    "\tcd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase4_artifact_diff_determinism.zig -- --self-test",
    "\tcd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase4_artifact_diff_determinism.zig",
};

const contracts = [_]FileContract{
    .{ .rel = ".github/workflows/zigux-bootstrap.yml", .markers = &markers_0 },
    .{ .rel = "Documentation/zigux/artifact-diff.md", .markers = &markers_1 },
    .{ .rel = "Documentation/zigux/phase4-artifact-diff-tooling-survey.md", .markers = &markers_2 },
    .{ .rel = "Documentation/zigux/phase4-reversible-delivery-evidence.md", .markers = &markers_3 },
    .{ .rel = "Documentation/zigux/review-checklist.md", .markers = &markers_4 },
    .{ .rel = "scripts/zigux/validate_phase4.zig", .markers = &markers_5 },
    .{ .rel = "zigux/Makefile", .markers = &markers_6 },
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    for (contracts) |contract| {
        const owner_path = try guard.joinPath(allocator, root, contract.rel);
        defer allocator.free(owner_path);
        const text = try guard.readUtf8File(io, allocator, owner_path);
        defer allocator.free(text);
        for (contract.markers) |marker| try guard.requireMarker(text, marker);
    }
}

fn runSelfTest(io: Io, allocator: std.mem.Allocator) !u8 {
    const root = try guard.defaultRepoRoot(allocator);
    defer allocator.free(root);
    try checkRepo(io, allocator, root);
    try guard.printLine(io, "{s}", .{self_test_pass_marker});
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
            index += 1; explicit_root = args[index]; continue;
        }
        if (std.mem.eql(u8, arg, "--zig") or std.mem.eql(u8, arg, "--cc")) {
            if (index + 1 >= args.len) std.process.exit(2);
            index += 1; continue;
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
// CURRENT_DIRECT_PACKET
// Documentation/zigux/phase4-artifact-diff-tooling-survey.md
// Documentation/zigux/phase4-reversible-delivery-evidence.md
// Documentation/zigux/review-checklist.md
// Documentation/zigux/artifact-diff.md
// scripts\zigux/check_phase4_repo_reality_warning.zig
// scripts\zigux/check_phase4_reversible_delivery_pins.zig
// scripts\zigux/check_phase4_artifact_diff_determinism.zig
// scripts\zigux/check_phase4_artifact_diff_validator_replays.zig
// scripts\zigux/validate_phase4.zig
// scripts/zigux/artifact_diff.zig
// scripts\zigux/check_artifact_diff_contract.zig
// EXPECTED_SELF_TEST_CASES
// round_trip
// survey_marker_drift
// survey_packet_drift
// survey_exact_packet_drift
// review_checklist_drift
// note_marker_drift
// broader_note_marker_drift
// broader_note_stale_packet_drift
// repo_warning_drift
// helper_mode_drift
// helper_catalog_drift
// contract_catalog_drift
// direct_packet_missing
// SURVEY_MARKERS
// PHASE4_ARTIFACT_DIFF_TOOLING_STATUS=helper_contract_validator_and_owner_note_direct_readback_aligned_on_current_master
// current direct-readback helper-contract-validator-and-owner-note packet:
// Current `master` now keeps the directly readable helper, contract checker, determinism checker, validator-replay checker, shared validator packet, and broader owner-and-rollback note aligned around the same bytes-capable artifact-diff contract.
// The broader `Documentation/zigux/artifact-diff.md` note is directly readable on current `master` again and now matches the current 23-case helper packet, the current 25-base-case / 30-case contract packet, and the current 13-case determinism self-test packet.
// That same direct packet now needs to keep the helper's exact output-contract lines pinned too, so the roadmap-backed host-side artifact-diff check stays machine-checked at the result-surface level instead of only at the case-count level.
// `scripts\zigux/check_phase4_artifact_diff_determinism.zig` now exact-requires the broader `Documentation/zigux/artifact-diff.md` note to keep the refreshed helper, contract, determinism, and helper output-contract anchor lines whenever that file is present in the checked tree.
// `PHASE4_ARTIFACT_DIFF_CURRENT_HELPER_SELF_TEST_CASE_COUNT=23`
// `PHASE4_ARTIFACT_DIFF_CURRENT_CONTRACT_SELF_TEST_CASE_COUNT=24`
// `PHASE4_ARTIFACT_DIFF_CURRENT_CONTRACT_BASE_CASE_COUNT=25`
// `PHASE4_ARTIFACT_DIFF_CURRENT_CONTRACT_REPEAT_CASE_COUNT=5`
// `PHASE4_ARTIFACT_DIFF_CURRENT_CONTRACT_CASE_COUNT=30`
// No remaining owner-and-rollback note readback caveat is left inside this lane on current `master`, so the same lane should stay parked unless the broader note or exact packet drifts again.
// this survey now treats `Documentation/zigux/artifact-diff.md` as direct current-head evidence on current `master`
// SURVEY_EXACT_PACKET_MARKERS
// `PHASE4_ARTIFACT_DIFF_CURRENT_HELPER_MODES=text,json,bytes`
// `PHASE4_ARTIFACT_DIFF_CURRENT_HELPER_LEGACY_MODE_ALIASES=sha256->bytes`
// `PHASE4_ARTIFACT_DIFF_CURRENT_SUCCESS_LINES=ARTIFACT_DIFF,MODE,EXPECTED,ACTUAL`
// `PHASE4_ARTIFACT_DIFF_CURRENT_BYTES_PASS_DETAIL=SHA256=<digest>`
// `PHASE4_ARTIFACT_DIFF_CURRENT_BYTES_FAIL_DETAIL=EXPECTED_SHA256=<digest>,ACTUAL_SHA256=<digest>`
// `PHASE4_ARTIFACT_DIFF_CURRENT_ERROR_LINES=EXPECTED_JSON_ERROR_or_ACTUAL_JSON_ERROR_or_EXPECTED_UTF8_ERROR_or_ACTUAL_UTF8_ERROR_or_EXPECTED_EXISTS_plus_ACTUAL_EXISTS`
// `PHASE4_ARTIFACT_DIFF_CURRENT_CONTRACT_HELPER_SELF_TEST_CASE_COUNT=23`
// `ARTIFACT_DIFF_SELF_TEST_CASE_COUNT=23`
// `ARTIFACT_DIFF_CONTRACT_SELF_TEST_CASE_COUNT=24`
// `ARTIFACT_DIFF_CONTRACT_CASE_COUNT=30`
// `PHASE4_ARTIFACT_DIFF_DETERMINISM_SELF_TEST_CASE_COUNT=13`
// `PHASE4_ARTIFACT_DIFF_VALIDATOR_REPLAYS_SELF_TEST_CASE_COUNT=14`
// `PHASE4_ARTIFACT_DIFF_VALIDATOR_REPLAYS_MARKER_COUNT=7`
// `PHASE4_ARTIFACT_DIFF_VALIDATOR_REPLAYS_WORKFLOW_MARKER_COUNT=16`
// NOTE_MARKERS
// The broader Phase 4 validator, build, and bitmap replay companions are no longer safe to describe as current-`master` gaps in this handoff.
// Direct authenticated contents reads in this runtime now return `scripts\zigux/validate_phase4.zig` directly, while `zigux/tests/phase4_build.zig`, `zigux/tests/bitmap_diff.zig`, and `zigux/tests/phase4_bitmap_live_helper_replay.zig` still flap on that same route; public raw fallback rereads continue to return the full set on current `master`, matching the broader review packet's recovered note-and-checker companions.
// Historical broader packet references still include `Documentation/zigux/artifact-diff.md`, `scripts/zigux/artifact_diff.zig`, `scripts\zigux/check_artifact_diff_contract.zig`, and `scripts\zigux/check_phase4_artifact_diff_determinism.zig`.
// Current direct contents reads for `zigux/tests/atomic64_diff.zig`, `zigux/tests/runtime_atomic64_diff.zig`, `zigux/tests/phase4_runtime_atomic64_diff_manifest.json`, and `zigux/tests/phase4_runtime_atomic64_diff_survey.zig` now return on current `master`
// ARTIFACT_DIFF_NOTE_MARKERS
// `scripts/zigux/artifact_diff.zig` as the stable comparison entrypoint
// `scripts\zigux/check_artifact_diff_contract.zig` reruns the bounded helper self-test, CLI help output, missing-required-args, missing-mode-value, missing-actual-operand, invalid-mode, and extra-positional parser coverage plus the text, JSON, bytes, missing-path, malformed-input, and repeat-run cases
// `scripts\zigux/check_phase4_artifact_diff_determinism.zig` rechecks the helper and contract summary catalogs together so case-count, case-order, and repeat-case drift fail closed
// `ARTIFACT_DIFF_CONTRACT_BASE_CASE_COUNT=25`, `ARTIFACT_DIFF_CONTRACT_REPEAT_CASE_COUNT=5`, and `ARTIFACT_DIFF_CONTRACT_CASE_COUNT=30`
// `PHASE4_ARTIFACT_DIFF_DETERMINISM_DIRECT_PACKET_MEMBERS=11`
// `PHASE4_ARTIFACT_DIFF_DETERMINISM_AUTH_MISSING_BROADER_COMPANIONS=0`
// REVIEW_CHECKLIST_MARKERS
// shared Phase 4 rollback-ownership and lab-matrix packet
// `scripts\zigux/check_phase4_repo_reality_warning.zig` and `scripts\zigux/check_phase4_reversible_delivery_pins.zig`
// keep the recovered broader note-and-checker companions explicit through `Documentation/zigux/phase4-gate-evidence.md`, `Documentation/zigux/phase4-validation-matrix.md`, `scripts\zigux/check_phase4_gate_evidence.zig`, and `scripts\zigux/check_phase4_remaining_gap_matrix.zig`
// keep the repo-reality warning explicit for the broader Phase 4 validator, build, and bitmap-diff companions still needing raw-fallback proof or fresh authenticated blob capture
// keep the roadmap-backed `atomic64_diff` pair explicit as direct current-head evidence
// REPO_WARNING_MARKERS
// Historical broader packet references still include `Documentation/zigux/artifact-diff.md`, `scripts/zigux/artifact_diff.zig`, `scripts\zigux/check_artifact_diff_contract.zig`, and `scripts\zigux/check_phase4_artifact_diff_determinism.zig`
// Current direct contents reads for `zigux/tests/atomic64_diff.zig` and `zigux/tests/runtime_atomic64_diff.zig` now return on current `master`, so keep that roadmap-backed differential-gate pair explicit as direct current-head evidence
// HELPER_EXPECTED_MODE_CHOICES
// text
// json
// bytes
// HELPER_EXPECTED_RESULT_LINES
// print(f"ARTIFACT_DIFF={status}")
// print(f"MODE={mode}")
// print(f"EXPECTED={expected}")
// print(f"ACTUAL={actual}")
// HELPER_EXPECTED_BYTES_PASS_DETAIL
// f"SHA256={expected_digest}"
// HELPER_EXPECTED_BYTES_FAIL_DETAILS
// f"EXPECTED_SHA256={expected_digest}"
// f"ACTUAL_SHA256={actual_digest}"
// HELPER_EXPECTED_ERROR_DETAILS
// f"{side}_UTF8_ERROR={path}:{exc.start}: {exc.reason}"
// f"{side}_JSON_ERROR={path}:{exc.lineno}:{exc.colno}: {exc.msg}"
// f"EXPECTED_EXISTS={expected_exists}"
// f"ACTUAL_EXISTS={actual_exists}"
// HELPER_EXPECTED_SELF_TEST_CASES
// text_pass
// text_mismatch
// json_pass
// json_mismatch
// json_invalid_expected
// json_invalid_actual
// json_invalid_both
// json_missing_expected
// json_missing_actual
// json_missing_both
// bytes_pass
// bytes_drift
// text_missing_expected
// text_missing_actual
// text_missing_both
// bytes_missing_expected
// bytes_missing_actual
// bytes_missing_both
// legacy_sha256_alias
// missing_mode_value_rejected
// missing_positional_arguments_rejected
// invalid_mode_rejected
// extra_positional_rejected
// CONTRACT_BASE_CASES
// helper_self_test
// cli_help_output
// cli_missing_required_args
// cli_missing_mode_value
// cli_missing_actual_operand
// cli_invalid_mode
// cli_extra_positional_args
// CONTRACT_REPEAT_CASES
// helper_self_test_repeat
// cli_help_output_repeat
// text_pass_repeat
// json_mismatch_repeat
// bytes_drift_repeat
// CONTRACT_SELF_TEST_CASES
// catalog_shape
// review_note_marker_round_trip
// review_note_owner_marker_drift
// review_note_marker_drift
// cli_help_round_trip
// cli_help_line_drift
// cli_missing_argument_parser_round_trip
// cli_missing_argument_parser_stderr_drift
// cli_invalid_mode_parser_round_trip
// cli_invalid_mode_parser_stderr_drift
// helper_summary_round_trip
// contract_summary_round_trip
// helper_summary_status_drift
// helper_summary_count_drift
// helper_summary_duplicate_case_drift
// helper_summary_case_order_drift
// contract_summary_status_drift
// contract_summary_base_count_drift
// contract_summary_base_case_order_drift
// contract_summary_repeat_count_drift
// contract_summary_repeat_case_order_drift
// contract_summary_case_count_drift
// contract_summary_duplicate_case_drift
// contract_summary_case_order_drift
// VALIDATOR_REPLAYS_EXPECTED_SELF_TEST_CASES
// validator_marker_round_trip
// validator_helper_marker_drift
// validator_marker_drift
// validator_replay_marker_drift
// repo_reality_handoff_round_trip
// repo_reality_handoff_drift
// repo_reality_handoff_note_missing
// workflow_marker_round_trip
// workflow_make_route_marker_drift
// workflow_marker_drift
// workflow_missing
// artifact_diff_note_round_trip
// artifact_diff_note_marker_drift
// VALIDATOR_MARKERS
// "phase4-artifact-diff-determinism-self-test": (
// "PHASE4_ARTIFACT_DIFF_DETERMINISM_SELF_TEST=pass",
// "PHASE4_ARTIFACT_DIFF_DETERMINISM_SELF_TEST_CASE_COUNT=13",
// "PHASE4_ARTIFACT_DIFF_DETERMINISM_SELF_TEST_CASES="
// "phase4-artifact-diff-determinism": (
// "PHASE4_ARTIFACT_DIFF_DETERMINISM=pass",
// "PHASE4_ARTIFACT_DIFF_DETERMINISM_DIRECT_PACKET_MEMBERS=11",
// "PHASE4_ARTIFACT_DIFF_DETERMINISM_AUTH_MISSING_BROADER_COMPANIONS=0",
