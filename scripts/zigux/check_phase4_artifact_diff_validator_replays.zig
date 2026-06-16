const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE4_ARTIFACT_DIFF_VALIDATOR_REPLAYS=pass";
pub const self_test_pass_marker = "PHASE4_ARTIFACT_DIFF_VALIDATOR_REPLAYS_SELF_TEST=pass";

const EXPECTED_VALIDATOR_REPLAY_MARKERS = [_][]const u8{
    "CheckSpec(\"phase4-artifact-diff-helper-self-test\", (\"python\", \"scripts/zigux/artifact_diff.zig\", \"--self-test\")),",
    "CheckSpec(\"phase4-artifact-diff-contract-self-test\", (\"python\", \"scripts\\zigux/check_artifact_diff_contract.zig\", \"--self-test\")),",
    "CheckSpec(\"phase4-artifact-diff-contract\", (\"python\", \"scripts\\zigux/check_artifact_diff_contract.zig\")),",
    "CheckSpec(\"phase4-artifact-diff-determinism-self-test\", (\"python\", \"scripts\\zigux/check_phase4_artifact_diff_determinism.zig\", \"--self-test\")),",
    "CheckSpec(\"phase4-artifact-diff-determinism\", (\"python\", \"scripts\\zigux/check_phase4_artifact_diff_determinism.zig\")),",
    "CheckSpec(\"phase4-artifact-diff-validator-replays-self-test\", (\"python\", \"scripts\\zigux/check_phase4_artifact_diff_validator_replays.zig\", \"--self-test\")),",
    "CheckSpec(\"phase4-artifact-diff-validator-replays\", (\"python\", \"scripts\\zigux/check_phase4_artifact_diff_validator_replays.zig\")),",
};

const EXPECTED_VALIDATOR_OUTPUT_MARKERS = [_][]const u8{
    "\"phase4-artifact-diff-contract-self-test\": (",
    "\"ARTIFACT_DIFF_CONTRACT_SELF_TEST=pass\",",
    "\"ARTIFACT_DIFF_CONTRACT_SELF_TEST_CASE_COUNT=24\",",
    "\"ARTIFACT_DIFF_CONTRACT_SELF_TEST_CASES=\"",
    "\"phase4-artifact-diff-contract\": (",
    "\"ARTIFACT_DIFF_CONTRACT=pass\",",
    "\"ARTIFACT_DIFF_CONTRACT_BASE_CASE_COUNT=25\",",
    "\"ARTIFACT_DIFF_CONTRACT_REPEAT_CASE_COUNT=5\",",
    "\"ARTIFACT_DIFF_CONTRACT_CASE_COUNT=30\",",
    "\"phase4-artifact-diff-determinism-self-test\": (",
    "\"PHASE4_ARTIFACT_DIFF_DETERMINISM_SELF_TEST=pass\",",
    "\"PHASE4_ARTIFACT_DIFF_DETERMINISM_SELF_TEST_CASE_COUNT=13\",",
    "\"PHASE4_ARTIFACT_DIFF_DETERMINISM_SELF_TEST_CASES=\"",
    "\"phase4-artifact-diff-determinism\": (",
    "\"PHASE4_ARTIFACT_DIFF_DETERMINISM=pass\",",
    "\"PHASE4_ARTIFACT_DIFF_DETERMINISM_DIRECT_PACKET_MEMBERS=11\",",
    "\"PHASE4_ARTIFACT_DIFF_DETERMINISM_AUTH_MISSING_BROADER_COMPANIONS=0\",",
    "\"phase4-artifact-diff-validator-replays-self-test\": (",
    "\"PHASE4_ARTIFACT_DIFF_VALIDATOR_REPLAYS_SELF_TEST=pass\",",
    "\"PHASE4_ARTIFACT_DIFF_VALIDATOR_REPLAYS_SELF_TEST_CASE_COUNT=14\",",
    "\"PHASE4_ARTIFACT_DIFF_VALIDATOR_REPLAYS_SELF_TEST_CASES=\"",
    "\"phase4-artifact-diff-validator-replays\": (",
    "\"PHASE4_ARTIFACT_DIFF_VALIDATOR_REPLAYS=pass\",",
    "\"PHASE4_ARTIFACT_DIFF_VALIDATOR_REPLAYS_MODE=validator_present\",",
    "\"PHASE4_ARTIFACT_DIFF_VALIDATOR_REPLAYS_MARKER_COUNT=7\",",
    "\"PHASE4_ARTIFACT_DIFF_VALIDATOR_REPLAYS_MARKERS=\"",
    "\"PHASE4_ARTIFACT_DIFF_VALIDATOR_REPLAYS_WORKFLOW_MARKER_COUNT=16\",",
};

const EXPECTED_REPO_REALITY_HANDOFF_MARKERS = [_][]const u8{
    "The broader Phase 4 validator, build, and bitmap replay companions are no longer safe to describe as current-`master` gaps in this handoff.",
    "Direct authenticated contents reads in this runtime now return `scripts\\zigux/validate_phase4.zig` directly, while `zigux/tests/phase4_build.zig`, `zigux/tests/bitmap_diff.zig`, and `zigux/tests/phase4_bitmap_live_helper_replay.zig` still flap on that same route; public raw fallback rereads continue to return the full set on current `master`, matching the broader review packet's recovered note-and-checker companions.",
    "The remaining shared reminder follow-up from the older mixed-readback packet is now narrower: `zigux/tests/README.md`, `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, and `scripts\\zigux/check_phase4_tests_readme_packet.zig` should align on the recovered note pair, the returned helper-contract and checker packet, the direct local-only perf packet, the roadmap-backed `atomic64_diff` pair, the directly returned validator, and the still-public-raw-returned build and bitmap replay companions, while exact blob-pin refresh for that broader packet remains the remaining authenticated-readback gap in this handoff.",
    "`Documentation/zigux/artifact-diff.md`",
    "`scripts\\zigux/check_artifact_diff_contract.zig`",
    "`scripts\\zigux/validate_phase4.zig`",
};

const EXPECTED_ARTIFACT_DIFF_NOTE_MARKERS = [_][]const u8{
    "`scripts\\zigux/check_phase4_artifact_diff_validator_replays.zig`",
    "validator hook set explicit or falls back to the narrower repo-reality handoff markers when exact validator readback is unavailable",
    "`PHASE4_ARTIFACT_DIFF_VALIDATOR_REPLAYS_SELF_TEST_CASE_COUNT=14`",
    "`PHASE4_ARTIFACT_DIFF_VALIDATOR_REPLAYS_SELF_TEST_CASES=catalog_shape,validator_marker_round_trip,validator_helper_marker_drift,validator_marker_drift,validator_replay_marker_drift,repo_reality_handoff_round_trip,repo_reality_handoff_drift,repo_reality_handoff_note_missing,workflow_marker_round_trip,workflow_make_route_marker_drift,workflow_marker_drift,workflow_missing,artifact_diff_note_round_trip,artifact_diff_note_marker_drift`",
    "`PHASE4_ARTIFACT_DIFF_VALIDATOR_REPLAYS_MARKER_COUNT=7`",
    "`PHASE4_ARTIFACT_DIFF_VALIDATOR_REPLAYS_WORKFLOW_MARKER_COUNT=16`",
};

const EXPECTED_WORKFLOW_REPLAY_MARKERS = [_][]const u8{
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

const EXPECTED_SELF_TEST_CASES = [_][]const u8{
    "catalog_shape",
    "validator_marker_round_trip",
    "validator_helper_marker_drift",
    "validator_marker_drift",
    "validator_replay_marker_drift",
    "repo_reality_handoff_round_trip",
    "repo_reality_handoff_drift",
    "repo_reality_handoff_note_missing",
    "workflow_marker_round_trip",
    "workflow_make_route_marker_drift",
    "workflow_marker_drift",
    "workflow_missing",
    "artifact_diff_note_round_trip",
    "artifact_diff_note_marker_drift",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_expected_validator_replay_markers_path = try guard.joinPath(allocator, root, "scripts\zigux/validate_phase4.zig");
    defer allocator.free(text_expected_validator_replay_markers_path);
    const text_expected_validator_replay_markers = try guard.readUtf8File(io, allocator, text_expected_validator_replay_markers_path);
    defer allocator.free(text_expected_validator_replay_markers);
    for (EXPECTED_VALIDATOR_REPLAY_MARKERS) |marker| try guard.requireMarker(text_expected_validator_replay_markers, marker);
    const text_expected_validator_output_markers_path = try guard.joinPath(allocator, root, "scripts\zigux/validate_phase4.zig");
    defer allocator.free(text_expected_validator_output_markers_path);
    const text_expected_validator_output_markers = try guard.readUtf8File(io, allocator, text_expected_validator_output_markers_path);
    defer allocator.free(text_expected_validator_output_markers);
    for (EXPECTED_VALIDATOR_OUTPUT_MARKERS) |marker| try guard.requireMarker(text_expected_validator_output_markers, marker);
    const text_expected_repo_reality_handoff_markers_path = try guard.joinPath(allocator, root, "scripts\zigux/validate_phase4.zig");
    defer allocator.free(text_expected_repo_reality_handoff_markers_path);
    const text_expected_repo_reality_handoff_markers = try guard.readUtf8File(io, allocator, text_expected_repo_reality_handoff_markers_path);
    defer allocator.free(text_expected_repo_reality_handoff_markers);
    for (EXPECTED_REPO_REALITY_HANDOFF_MARKERS) |marker| try guard.requireMarker(text_expected_repo_reality_handoff_markers, marker);
    const text_expected_artifact_diff_note_markers_path = try guard.joinPath(allocator, root, "scripts\zigux/validate_phase4.zig");
    defer allocator.free(text_expected_artifact_diff_note_markers_path);
    const text_expected_artifact_diff_note_markers = try guard.readUtf8File(io, allocator, text_expected_artifact_diff_note_markers_path);
    defer allocator.free(text_expected_artifact_diff_note_markers);
    for (EXPECTED_ARTIFACT_DIFF_NOTE_MARKERS) |marker| try guard.requireMarker(text_expected_artifact_diff_note_markers, marker);
    const text_expected_workflow_replay_markers_path = try guard.joinPath(allocator, root, "scripts\zigux/validate_phase4.zig");
    defer allocator.free(text_expected_workflow_replay_markers_path);
    const text_expected_workflow_replay_markers = try guard.readUtf8File(io, allocator, text_expected_workflow_replay_markers_path);
    defer allocator.free(text_expected_workflow_replay_markers);
    for (EXPECTED_WORKFLOW_REPLAY_MARKERS) |marker| try guard.requireMarker(text_expected_workflow_replay_markers, marker);
    const text_expected_self_test_cases_path = try guard.joinPath(allocator, root, "scripts\zigux/validate_phase4.zig");
    defer allocator.free(text_expected_self_test_cases_path);
    const text_expected_self_test_cases = try guard.readUtf8File(io, allocator, text_expected_self_test_cases_path);
    defer allocator.free(text_expected_self_test_cases);
    for (EXPECTED_SELF_TEST_CASES) |marker| try guard.requireMarker(text_expected_self_test_cases, marker);
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
