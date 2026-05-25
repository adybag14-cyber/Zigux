const std = @import("std");

const RepoEvidence = struct {
    phase15_readiness_packet_checker_present: bool,
    phase15_validator_script_present: bool,
    phase15_docs_readme_checker_present: bool,
    phase15_scripts_readme_checker_present: bool,
    phase15_tests_readme_checker_present: bool,
    phase15_review_checklist_study_only_alignment_checker_present: bool,
    phase15_handoff_note_checker_present: bool,
    phase15_governance_lane_manifest_present: bool,
    phase15_governance_lane_replay_present: bool,
    phase15_handoff_manifest_present: bool,
    phase15_review_process_build_replay_present: bool,
    phase15_build_zig_present: bool,
    phase15_indefinite_c_lane_owner_alignment_present: bool,
    phase15_makefile_present: bool,
    phase15_validate_target_present: bool,
    phase15_test_target_present: bool,
    phase15_aggregate_target_present: bool,
    shared_ci_phase15_present: bool,
    phase15_replay_green_on_current_master: bool,
};

const Manifest = struct {
    lane_key: []const u8,
    phase: []const u8,
    surveyed_commit_mode: []const u8,
    surveyed_commit: []const u8,
    readiness_packet_checker: []const u8,
    direct_packet_paths: []const []const u8,
    still_missing_broader_paths: []const []const u8,
    repo_evidence: RepoEvidence,
    phase15_validate_checkers: []const []const u8,
};

fn readRepoFile(path: []const u8, limit: usize) ![]u8 {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();
    return std.Io.Dir.cwd().readFileAlloc(io_instance.io(), path, std.testing.allocator, .limited(limit));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

test "phase 15 readiness manifest preserves the validator-first packet truth" {
    const manifest_json = try readRepoFile("zigux/tests/phase15_readiness_gate_manifest.json", 16 * 1024);
    defer std.testing.allocator.free(manifest_json);

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{
        .ignore_unknown_fields = true,
    });
    defer parsed.deinit();

    const manifest = parsed.value;
    try std.testing.expectEqualStrings("P15-L02", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 15", manifest.phase);
    try std.testing.expectEqualStrings("dated_master_readback", manifest.surveyed_commit_mode);
    try std.testing.expectEqualStrings("current-master-readback-2026-05-25", manifest.surveyed_commit);
    try std.testing.expectEqualStrings(
        "scripts/zigux/check-phase15-readiness-gate-packet.py",
        manifest.readiness_packet_checker,
    );
    try std.testing.expectEqual(@as(usize, 38), manifest.direct_packet_paths.len);
    try std.testing.expectEqualStrings(
        "scripts/zigux/check-phase15-review-checklist-study-only-alignment.py",
        manifest.direct_packet_paths[17],
    );
    try std.testing.expectEqualStrings(
        "scripts/zigux/check-phase15-readiness-gate-packet.py",
        manifest.direct_packet_paths[20],
    );
    try std.testing.expectEqualStrings(
        "scripts/zigux/validate-phase15.py",
        manifest.direct_packet_paths[21],
    );
    try std.testing.expectEqualStrings(
        "zigux/tests/phase15_architecture_council_review_process_build.zig",
        manifest.direct_packet_paths[25],
    );
    try std.testing.expectEqualStrings(
        "zigux/tests/phase15_freeze_map_governance.zig",
        manifest.direct_packet_paths[26],
    );
    try std.testing.expectEqualStrings(
        "zigux/tests/phase15_handoff_next_steps_manifest.json",
        manifest.direct_packet_paths[33],
    );
    try std.testing.expectEqualStrings(
        "zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig",
        manifest.direct_packet_paths[35],
    );
    try std.testing.expectEqualStrings(
        "zigux/tests/phase15_build.zig",
        manifest.direct_packet_paths[36],
    );
    try std.testing.expectEqualStrings(
        "zigux/tests/phase15_readiness_gate_manifest.json",
        manifest.direct_packet_paths[37],
    );
    try std.testing.expectEqual(@as(usize, 5), manifest.phase15_validate_checkers.len);
    try std.testing.expectEqualStrings(
        "scripts/zigux/check-phase15-docs-readme-alignment.py",
        manifest.phase15_validate_checkers[0],
    );
    try std.testing.expectEqualStrings(
        "scripts/zigux/check-phase15-shared-summary-gap.py",
        manifest.phase15_validate_checkers[4],
    );
    try std.testing.expectEqual(@as(usize, 0), manifest.still_missing_broader_paths.len);
    try std.testing.expect(manifest.repo_evidence.phase15_readiness_packet_checker_present);
    try std.testing.expect(manifest.repo_evidence.phase15_validator_script_present);
    try std.testing.expect(manifest.repo_evidence.phase15_docs_readme_checker_present);
    try std.testing.expect(manifest.repo_evidence.phase15_scripts_readme_checker_present);
    try std.testing.expect(manifest.repo_evidence.phase15_tests_readme_checker_present);
    try std.testing.expect(manifest.repo_evidence.phase15_review_checklist_study_only_alignment_checker_present);
    try std.testing.expect(manifest.repo_evidence.phase15_handoff_note_checker_present);
    try std.testing.expect(manifest.repo_evidence.phase15_governance_lane_manifest_present);
    try std.testing.expect(manifest.repo_evidence.phase15_governance_lane_replay_present);
    try std.testing.expect(manifest.repo_evidence.phase15_handoff_manifest_present);
    try std.testing.expect(manifest.repo_evidence.phase15_review_process_build_replay_present);
    try std.testing.expect(manifest.repo_evidence.phase15_build_zig_present);
    try std.testing.expect(manifest.repo_evidence.phase15_indefinite_c_lane_owner_alignment_present);
    try std.testing.expect(manifest.repo_evidence.phase15_makefile_present);
    try std.testing.expect(!manifest.repo_evidence.phase15_validate_target_present);
    try std.testing.expect(!manifest.repo_evidence.phase15_test_target_present);
    try std.testing.expect(!manifest.repo_evidence.phase15_aggregate_target_present);
    try std.testing.expect(!manifest.repo_evidence.shared_ci_phase15_present);
    try std.testing.expect(!manifest.repo_evidence.phase15_replay_green_on_current_master);
}

test "phase 15 readiness note stays aligned with the validator-first packet" {
    const readiness_note = try readRepoFile("Documentation/zigux/phase15-readiness-gate-survey.md", 24 * 1024);
    defer std.testing.allocator.free(readiness_note);

    try expectContains(readiness_note, "PHASE15_LANE_KEY=P15-L02");
    try expectContains(readiness_note, "PHASE15_SLICE=validator_first_readiness_packet");
    try expectContains(readiness_note, "current-master-readback-2026-05-25");
    try expectContains(readiness_note, "the governance packet is materially landed and reviewable");
    try expectContains(readiness_note, "the dedicated validator now exists as a directly readable maintenance gate");
    try expectContains(readiness_note, "the dedicated shared-build companion is now directly readable current-master evidence");
    try expectContains(
        readiness_note,
        "broader make-wrapper and workflow companions still block any claim that the larger Phase 15 replay route is one-command or shared-CI ready",
    );
    try expectContains(readiness_note, "`scripts/zigux/check-phase15-review-checklist-study-only-alignment.py`");
    try expectContains(readiness_note, "`scripts/zigux/check-phase15-handoff-note-alignment.py`");
    try expectContains(readiness_note, "`scripts/zigux/check-phase15-readiness-gate-packet.py`");
    try expectContains(readiness_note, "`scripts/zigux/validate-phase15.py`");
    try expectContains(readiness_note, "`zigux/tests/phase15_architecture_council_review_process_build.zig`");
    try expectContains(readiness_note, "`zigux/tests/phase15_freeze_map_governance.zig`");
    try expectContains(readiness_note, "`zigux/tests/phase15_handoff_next_steps_manifest.json`");
    try expectContains(readiness_note, "`zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig`");
    try expectContains(readiness_note, "`zigux/tests/phase15_build.zig`");
    try expectContains(readiness_note, "`make -C zigux phase15-validate` remains blocked route vocabulary");
    try expectContains(readiness_note, "`.github/workflows/zigux-bootstrap.yml` still carries no dedicated Phase 15 validate, test, or aggregate route");
    try expectContains(readiness_note, "ready for maintenance-mode truthfulness refreshes, direct validator-first replay, and shared-build companion review only");
}
