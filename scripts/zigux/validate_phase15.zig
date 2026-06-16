const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE15_VALIDATION=pass";
pub const self_test_pass_marker = "PHASE15_VALIDATION_SELF_TEST=pass";

const EXPECTED_PHASE = [_][]const u8{
    "Phase 15",
};

const EXPECTED_SURVEYED_COMMIT = [_][]const u8{
    "current-master-readback-2026-05-27",
};

const EXPECTED_PHASE15_VALIDATE_CHECKERS = [_][]const u8{
    "scripts\\zigux/check_phase15_docs_readme_alignment.zig",
    "scripts\\zigux/check_phase15_scripts_readme_alignment.zig",
    "scripts\\zigux/check_phase15_tests_readme_alignment.zig",
    "scripts\\zigux/check_phase15_architecture_council_packet.zig",
    "scripts\\zigux/check_phase15_review_process_handoff.zig",
    "scripts\\zigux/check_phase15_review_checklist_study_only_alignment.zig",
    "scripts\\zigux/check_phase15_handoff_note_alignment.zig",
    "scripts\\zigux/check_phase15_shared_summary_gap.zig",
    "scripts\\zigux/check_phase15_readiness_gate_packet.zig",
};

const REQUIRED_NOTE_MARKERS = [_][]const u8{
    "PHASE15_STATUS=readiness_gate_survey_landed",
    "PHASE15_LANE_KEY=P15-L04",
    "PHASE15_SLICE=validator_first_readiness_packet",
    "PHASE15_PROVENANCE_MODE=dated_master_readback",
    "the governance packet is materially landed and reviewable",
    "the dedicated validator now exists as a directly readable maintenance gate",
    "the dedicated Architecture Council packet checker now exists as a directly readable maintenance gate within the broader validator-first reminder family",
    "the dedicated shared-build companion is now directly readable current-master evidence",
    "the roadmap-versus-ledger gap matrix now keeps the remaining readiness requirements explicit",
    "`scripts\\zigux/check_phase15_architecture_council_packet.zig`",
    "`scripts\\zigux/validate_phase15.zig`",
    "`zigux/tests/phase15_freeze_map_governance.zig`",
    "`zigux/tests/phase15_build.zig`",
    "`zigux/tests/phase15_readiness_gap_matrix.json`",
    "`make -C zigux phase15-validate` remains blocked route vocabulary",
    "`.github/workflows/zigux-bootstrap.yml` still carries no dedicated Phase 15 validate, test, or aggregate route",
    "no Architecture Council approval is currently recorded for a freeze-map status change",
};

const WORKFLOW_PHASE15_MARKERS = [_][]const u8{
    "validate-phase15.py",
    "make -C zigux phase15-validate",
    "make -C zigux phase15-test",
    "make -C zigux phase15",
    "zigux/tests/phase15_build.zig",
};

const SURFACE_PATHS = [_][]const u8{
    "Documentation/zigux/freeze-map.md",
    "Documentation/zigux/phase15-freeze-map-governance.md",
    "Documentation/zigux/phase15-parity-scorecard.md",
    "Documentation/zigux/phase15-parity-scorecard-survey.md",
    "Documentation/zigux/phase15-architecture-council-review-process.md",
    "Documentation/zigux/phase15-architecture-council-decision-record-template.md",
    "Documentation/zigux/phase15-architecture-council-decision-index.md",
    "Documentation/zigux/phase15-indefinite-c-policy.md",
    "Documentation/zigux/phase15-deep-core-blocker-survey.md",
    "Documentation/zigux/phase15-study-only-anchor-accounting.md",
    "Documentation/zigux/phase15-governance-lane-sequencing.md",
    "Documentation/zigux/phase15-handoff-next-steps-survey.md",
    "Documentation/zigux/phase15-shared-summary-gap.md",
    "Documentation/zigux/review-checklist.md",
    "scripts\\zigux/check_phase15_docs_readme_alignment.zig",
    "scripts\\zigux/check_phase15_scripts_readme_alignment.zig",
    "scripts\\zigux/check_phase15_tests_readme_alignment.zig",
    "scripts\\zigux/check_phase15_architecture_council_packet.zig",
    "scripts\\zigux/check_phase15_review_process_handoff.zig",
    "scripts\\zigux/check_phase15_review_checklist_study_only_alignment.zig",
    "scripts\\zigux/check_phase15_handoff_note_alignment.zig",
    "scripts\\zigux/check_phase15_shared_summary_gap.zig",
    "scripts\\zigux/check_phase15_readiness_gate_packet.zig",
    "scripts\\zigux/validate_phase15.zig",
    "zigux/tests/README.md",
    "zigux/tests/phase15_architecture_council_review_process_manifest.json",
    "zigux/tests/phase15_architecture_council_review_process.zig",
    "zigux/tests/phase15_architecture_council_review_process_build.zig",
    "zigux/tests/phase15_freeze_map_governance.zig",
    "zigux/tests/phase15_governance_lane_sequencing_manifest.json",
    "zigux/tests/phase15_governance_lane_sequencing.zig",
    "zigux/tests/phase15_parity_scorecard.json",
    "zigux/tests/phase15_parity_scorecard.zig",
    "zigux/tests/phase15_indefinite_c_policy.json",
    "zigux/tests/phase15_indefinite_c_policy.zig",
    "zigux/tests/phase15_handoff_next_steps_manifest.json",
    "zigux/tests/phase15_handoff_next_steps.zig",
    "zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig",
    "zigux/tests/phase15_build.zig",
    "zigux/tests/phase15_readiness_gate_manifest.json",
    "zigux/tests/phase15_readiness_gap_matrix.json",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_expected_phase_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase15-readiness-gate-survey.md");
    defer allocator.free(text_expected_phase_path);
    const text_expected_phase = try guard.readUtf8File(io, allocator, text_expected_phase_path);
    defer allocator.free(text_expected_phase);
    for (EXPECTED_PHASE) |marker| try guard.requireMarker(text_expected_phase, marker);
    const text_expected_surveyed_commit_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase15-readiness-gate-survey.md");
    defer allocator.free(text_expected_surveyed_commit_path);
    const text_expected_surveyed_commit = try guard.readUtf8File(io, allocator, text_expected_surveyed_commit_path);
    defer allocator.free(text_expected_surveyed_commit);
    for (EXPECTED_SURVEYED_COMMIT) |marker| try guard.requireMarker(text_expected_surveyed_commit, marker);
    const text_expected_phase15_validate_checkers_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase15-readiness-gate-survey.md");
    defer allocator.free(text_expected_phase15_validate_checkers_path);
    const text_expected_phase15_validate_checkers = try guard.readUtf8File(io, allocator, text_expected_phase15_validate_checkers_path);
    defer allocator.free(text_expected_phase15_validate_checkers);
    for (EXPECTED_PHASE15_VALIDATE_CHECKERS) |marker| try guard.requireMarker(text_expected_phase15_validate_checkers, marker);
    const text_required_note_markers_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase15-readiness-gate-survey.md");
    defer allocator.free(text_required_note_markers_path);
    const text_required_note_markers = try guard.readUtf8File(io, allocator, text_required_note_markers_path);
    defer allocator.free(text_required_note_markers);
    for (REQUIRED_NOTE_MARKERS) |marker| try guard.requireMarker(text_required_note_markers, marker);
    const text_workflow_phase15_markers_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase15-readiness-gate-survey.md");
    defer allocator.free(text_workflow_phase15_markers_path);
    const text_workflow_phase15_markers = try guard.readUtf8File(io, allocator, text_workflow_phase15_markers_path);
    defer allocator.free(text_workflow_phase15_markers);
    for (WORKFLOW_PHASE15_MARKERS) |marker| try guard.requireMarker(text_workflow_phase15_markers, marker);
    for (SURFACE_PATHS) |rel| {
        const path = try guard.joinPath(allocator, root, rel);
        defer allocator.free(path);
        if (!guard.pathExists(io, path)) return guard.GuardError.IOError;
    }
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
