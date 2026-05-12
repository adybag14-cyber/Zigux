const std = @import("std");

const Requirement = struct {
    id: []const u8,
    summary: []const u8,
    required_terms: []const []const u8,
};

const MaintenanceHandoff = struct {
    current_lane_posture: []const u8,
    replay_before_trusting: []const []const u8,
    reopen_conditions: []const []const u8,
    next_future_target: []const u8,
};

const Gap = struct {
    id: []const u8,
    status: []const u8,
    kind: []const u8,
    zigux_destination: []const u8,
    why_now: []const u8,
};

const Manifest = struct {
    lane_key: []const u8,
    phase: []const u8,
    surveyed_commit: []const u8,
    roadmap_requirement: []const u8,
    anchors: []const []const u8,
    supporting_artifacts: []const []const u8,
    indefinite_c_requirements: []const Requirement,
    maintenance_handoff: MaintenanceHandoff,
    gaps: []const Gap,
};

fn readRepoFile(path: []const u8, limit: usize) ![]u8 {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();
    return std.Io.Dir.cwd().readFileAlloc(io_instance.io(), path, std.testing.allocator, .limited(limit));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectArtifactListContains(list: []const []const u8, needle: []const u8) !void {
    for (list) |item| {
        if (std.mem.eql(u8, item, needle)) return;
    }
    return error.TestUnexpectedResult;
}

fn isLowerHexCommit(text: []const u8) bool {
    if (text.len != 40) return false;
    for (text) |byte| {
        if (!std.ascii.isHex(byte) or std.ascii.isUpper(byte)) return false;
    }
    return true;
}

fn findRequirement(requirements: []const Requirement, id: []const u8) ?Requirement {
    for (requirements) |requirement| {
        if (std.mem.eql(u8, requirement.id, id)) return requirement;
    }
    return null;
}

fn findGap(gaps: []const Gap, id: []const u8) ?Gap {
    for (gaps) |gap| {
        if (std.mem.eql(u8, gap.id, id)) return gap;
    }
    return null;
}

test "phase 15 indefinite-C policy packet matches the live stay-in-C note, maintenance handoff, exception posture, and blocker accounting" {
    const policy_note = try readRepoFile("Documentation/zigux/phase15-indefinite-c-policy.md", 32 * 1024);
    defer std.testing.allocator.free(policy_note);

    const review_process = try readRepoFile("Documentation/zigux/phase15-architecture-council-review-process.md", 24 * 1024);
    defer std.testing.allocator.free(review_process);

    const parity_scorecard = try readRepoFile("Documentation/zigux/phase15-parity-scorecard.md", 24 * 1024);
    defer std.testing.allocator.free(parity_scorecard);

    const manifest_json = try readRepoFile("zigux/tests/phase15_indefinite_c_policy.json", 32 * 1024);
    defer std.testing.allocator.free(manifest_json);

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{});
    defer parsed.deinit();

    const manifest = parsed.value;
    try std.testing.expectEqualStrings("P15-L16", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 15", manifest.phase);
    try std.testing.expect(isLowerHexCommit(manifest.surveyed_commit));
    try std.testing.expectEqualStrings("policy for code that remains in C indefinitely", manifest.roadmap_requirement);
    try std.testing.expectEqual(@as(usize, 4), manifest.anchors.len);
    try std.testing.expectEqual(@as(usize, 8), manifest.supporting_artifacts.len);
    try std.testing.expectEqual(@as(usize, 6), manifest.indefinite_c_requirements.len);
    try std.testing.expectEqualStrings("maintenance_mode", manifest.maintenance_handoff.current_lane_posture);
    try std.testing.expectEqual(@as(usize, 4), manifest.maintenance_handoff.replay_before_trusting.len);
    try std.testing.expectEqual(@as(usize, 3), manifest.maintenance_handoff.reopen_conditions.len);
    try std.testing.expectEqual(@as(usize, 7), manifest.gaps.len);

    try expectArtifactListContains(manifest.supporting_artifacts, "Documentation/zigux/freeze-map.md");
    try expectArtifactListContains(manifest.supporting_artifacts, "Documentation/zigux/review-checklist.md");
    try expectArtifactListContains(manifest.supporting_artifacts, "Documentation/zigux/phase15-architecture-council-review-process.md");
    try expectArtifactListContains(manifest.supporting_artifacts, "Documentation/zigux/phase15-parity-scorecard.md");
    try expectArtifactListContains(manifest.supporting_artifacts, "Documentation/zigux/phase15-governance-lane-sequencing.md");
    try expectArtifactListContains(manifest.supporting_artifacts, "zigux/tests/phase15_indefinite_c_blocker_evidence.zig");
    try expectArtifactListContains(manifest.supporting_artifacts, "zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig");
    try expectArtifactListContains(manifest.supporting_artifacts, "zigux/tests/phase15_build.zig");

    try expectContains(policy_note, "PHASE15_STATUS=indefinite_c_policy_packet_landed");
    try expectContains(policy_note, "PHASE15_LANE_KEY=P15-L16");
    try expectContains(policy_note, "PHASE15_PROVENANCE_MODE=exact_master_commit_readback");
    try expectContains(policy_note, "survey provenance refreshed against current `master` commit `");
    try expectContains(policy_note, manifest.surveyed_commit);
    try expectContains(policy_note, "There is no silent exception path around the indefinite-C policy.");
    try expectContains(policy_note, "The only allowed exception is an Architecture Council reopen request");
    try expectContains(policy_note, "existing blocker remains recorded");
    try expectContains(policy_note, "decision record ID, the lane owner, the required approver set, and the rollback owner");
    try expectContains(policy_note, "automatic return-to-blocked trigger");
    try expectContains(policy_note, "retired_from_active_discussion");
    try expectContains(policy_note, "named reopen-trigger catalog item");
    try expectContains(policy_note, "trigger-specific evidence refresh");
    try expectContains(policy_note, "## Maintenance-Mode Handoff");
    try expectContains(policy_note, "current lane posture: `maintenance_mode`");
    try expectContains(policy_note, "zig test zigux/tests/phase15_indefinite_c_policy.zig");
    try expectContains(policy_note, "zig test zigux/tests/phase15_indefinite_c_blocker_evidence.zig");
    try expectContains(policy_note, "zig test zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig");
    try expectContains(policy_note, "zig build test --build-file zigux/tests/phase15_build.zig");
    try expectContains(policy_note, "policy packet's truthfulness");
    try expectContains(policy_note, "keep the repair inside the policy packet and its direct replays");
    try expectContains(policy_note, "Keep this lane in maintenance mode until new stay-in-C evidence changes one of the named reopen triggers or the deep-core blocker posture changes.");

    try expectContains(review_process, "named owner for the lane");
    try expectContains(review_process, "required approver set");
    try expectContains(review_process, "rollback threshold");
    try expectContains(review_process, "`retired_from_active_discussion`");

    try expectContains(parity_scorecard, "blocked status-change anchor count: `4`");
    try expectContains(parity_scorecard, "Architecture Council approvals recorded for status change: `0`");
    try expectContains(parity_scorecard, "keep the anchor frozen until");

    const recordkeeping = findRequirement(manifest.indefinite_c_requirements, "indefinite-c-recordkeeping") orelse return error.MissingRequirement;
    try std.testing.expectEqual(@as(usize, 19), recordkeeping.required_terms.len);
    try std.testing.expectEqualStrings("lane owner", recordkeeping.required_terms[3]);
    try std.testing.expectEqualStrings("required approver set", recordkeeping.required_terms[6]);
    try std.testing.expectEqualStrings("rollback owner", recordkeeping.required_terms[7]);
    try std.testing.expectEqualStrings("automatic return-to-blocked trigger", recordkeeping.required_terms[13]);
    try std.testing.expectEqualStrings("retained discussion state", recordkeeping.required_terms[14]);
    try std.testing.expectEqualStrings("reopen triggers", recordkeeping.required_terms[15]);

    const exception_path = findRequirement(manifest.indefinite_c_requirements, "indefinite-c-exception-path") orelse return error.MissingRequirement;
    try std.testing.expectEqual(@as(usize, 3), exception_path.required_terms.len);
    try expectContains(exception_path.required_terms[0], "no silent exception path");
    try expectContains(exception_path.required_terms[1], "Architecture Council reopen request");
    try expectContains(exception_path.required_terms[2], "existing blocker remains recorded");

    const reopen_gate = findRequirement(manifest.indefinite_c_requirements, "indefinite-c-reopen-gate") orelse return error.MissingRequirement;
    try std.testing.expectEqual(@as(usize, 5), reopen_gate.required_terms.len);
    try expectContains(reopen_gate.required_terms[0], "named reopen-trigger catalog item");
    try std.testing.expectEqualStrings("narrower_followup_answers_blocker", reopen_gate.required_terms[1]);
    try std.testing.expectEqualStrings("evidence_packet_stale_or_contradictory", reopen_gate.required_terms[2]);
    try std.testing.expectEqualStrings("ownership_or_validation_changed", reopen_gate.required_terms[3]);
    try expectContains(reopen_gate.required_terms[4], "trigger-specific evidence refresh");

    const reopen_catalog = findRequirement(manifest.indefinite_c_requirements, "indefinite-c-reopen-trigger-catalog") orelse return error.MissingRequirement;
    try std.testing.expectEqual(@as(usize, 3), reopen_catalog.required_terms.len);
    try std.testing.expectEqualStrings("narrower_followup_answers_blocker", reopen_catalog.required_terms[0]);
    try std.testing.expectEqualStrings("evidence_packet_stale_or_contradictory", reopen_catalog.required_terms[1]);
    try std.testing.expectEqualStrings("ownership_or_validation_changed", reopen_catalog.required_terms[2]);

    try expectContains(manifest.maintenance_handoff.replay_before_trusting[0], "phase15_indefinite_c_policy.zig");
    try expectContains(manifest.maintenance_handoff.replay_before_trusting[1], "phase15_indefinite_c_blocker_evidence.zig");
    try expectContains(manifest.maintenance_handoff.replay_before_trusting[2], "phase15_indefinite_c_lane_owner_alignment.zig");
    try expectContains(manifest.maintenance_handoff.replay_before_trusting[3], "phase15_build.zig");
    try expectContains(manifest.maintenance_handoff.reopen_conditions[0], "trigger-specific evidence refresh");
    try expectContains(manifest.maintenance_handoff.reopen_conditions[1], "parity scorecard blocker record");
    try expectContains(manifest.maintenance_handoff.reopen_conditions[2], "supporting-artifact route drift");
    try expectContains(manifest.maintenance_handoff.next_future_target, "inside the policy packet");

    var landed_gap_count: usize = 0;
    for (manifest.gaps) |gap| {
        try std.testing.expect(gap.id.len > 0);
        try std.testing.expect(gap.kind.len > 0);
        try std.testing.expect(gap.zigux_destination.len > 0);
        try std.testing.expect(gap.why_now.len > 0);
        if (std.mem.eql(u8, gap.status, "landed")) landed_gap_count += 1;
    }
    try std.testing.expectEqual(@as(usize, 6), landed_gap_count);

    const handoff_gap = findGap(manifest.gaps, "phase15-indefinite-c-maintenance-handoff") orelse return error.MissingGap;
    try std.testing.expectEqualStrings("landed", handoff_gap.status);
    try std.testing.expectEqualStrings("maintenance_handoff", handoff_gap.kind);
    try std.testing.expectEqualStrings("Documentation/zigux/phase15-indefinite-c-policy.md", handoff_gap.zigux_destination);
    try expectContains(handoff_gap.why_now, "when to reopen");

    const blocker_gap = findGap(manifest.gaps, "phase15-deep-core-status-change-blocker") orelse return error.MissingGap;
    try std.testing.expectEqualStrings("blocked_on_stay_in_c_evidence", blocker_gap.status);
    try std.testing.expectEqualStrings("freeze_map", blocker_gap.kind);
    try std.testing.expectEqualStrings("Documentation/zigux/phase15-parity-scorecard.md", blocker_gap.zigux_destination);
    try expectContains(blocker_gap.why_now, "lacks evidence strong enough");
}