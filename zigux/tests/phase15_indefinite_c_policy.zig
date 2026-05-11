const std = @import("std");

const Requirement = struct {
    id: []const u8,
    summary: []const u8,
    required_terms: []const []const u8,
};

const Gap = struct {
    id: []const u8,
    status: []const u8,
    kind: []const u8,
    zigux_destination: []const u8,
    why_now: []const u8,
};

const Handoff = struct {
    current_mode: []const u8,
    replay_commands: []const []const u8,
    blocker_posture_requirement: []const u8,
    next_step: []const u8,
};

const Manifest = struct {
    lane_key: []const u8,
    phase: []const u8,
    surveyed_commit: []const u8,
    roadmap_requirement: []const u8,
    anchors: []const []const u8,
    supporting_artifacts: []const []const u8,
    indefinite_c_requirements: []const Requirement,
    handoff: Handoff,
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

fn isDatedReadbackMarker(text: []const u8) bool {
    return std.mem.startsWith(u8, text, "current-master-readback-") and text.len >= "current-master-readback-2026-05-11".len;
}

test "phase 15 indefinite-C policy packet matches the current policy, exception posture, and blocker evidence" {
    const policy_note = try readRepoFile("Documentation/zigux/phase15-indefinite-c-policy.md", 24 * 1024);
    defer std.testing.allocator.free(policy_note);

    const review_process = try readRepoFile("Documentation/zigux/phase15-architecture-council-review-process.md", 24 * 1024);
    defer std.testing.allocator.free(review_process);

    const parity_scorecard = try readRepoFile("Documentation/zigux/phase15-parity-scorecard.md", 24 * 1024);
    defer std.testing.allocator.free(parity_scorecard);

    const manifest_json = try readRepoFile("zigux/tests/phase15_indefinite_c_policy.json", 24 * 1024);
    defer std.testing.allocator.free(manifest_json);

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{});
    defer parsed.deinit();

    const manifest = parsed.value;
    try std.testing.expectEqualStrings("P15-L02", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 15", manifest.phase);
    try std.testing.expect(isDatedReadbackMarker(manifest.surveyed_commit));
    try std.testing.expectEqualStrings("policy for code that remains in C indefinitely", manifest.roadmap_requirement);
    try std.testing.expectEqual(@as(usize, 4), manifest.anchors.len);
    try std.testing.expectEqual(@as(usize, 5), manifest.supporting_artifacts.len);
    try std.testing.expectEqual(@as(usize, 6), manifest.indefinite_c_requirements.len);
    try std.testing.expectEqual(@as(usize, 6), manifest.gaps.len);
    try std.testing.expectEqualStrings("maintenance_mode", manifest.handoff.current_mode);
    try std.testing.expectEqualStrings("deep_core_blocker_posture_change", manifest.handoff.blocker_posture_requirement);
    try std.testing.expectEqual(@as(usize, 3), manifest.handoff.replay_commands.len);
    try std.testing.expectEqualStrings("make -C zigux phase15-validate", manifest.handoff.replay_commands[0]);
    try std.testing.expectEqualStrings("make -C zigux phase15-test", manifest.handoff.replay_commands[1]);
    try std.testing.expectEqualStrings("make -C zigux phase15", manifest.handoff.replay_commands[2]);

    try expectArtifactListContains(manifest.supporting_artifacts, "Documentation/zigux/freeze-map.md");
    try expectArtifactListContains(manifest.supporting_artifacts, "Documentation/zigux/review-checklist.md");
    try expectArtifactListContains(manifest.supporting_artifacts, "Documentation/zigux/phase15-architecture-council-review-process.md");
    try expectArtifactListContains(manifest.supporting_artifacts, "Documentation/zigux/phase15-parity-scorecard.md");
    try expectArtifactListContains(manifest.supporting_artifacts, "Documentation/zigux/phase15-governance-lane-sequencing.md");

    try expectContains(policy_note, "PHASE15_LANE_KEY=P15-L02");
    try expectContains(policy_note, "There is no silent exception path around the indefinite-C policy.");
    try expectContains(policy_note, "The only allowed exception is an Architecture Council reopen request");
    try expectContains(policy_note, "existing blocker remains recorded");
    try expectContains(policy_note, "Keep this lane in maintenance mode until new stay-in-C evidence changes one of the named reopen triggers or the deep-core blocker posture changes.");
    try expectContains(policy_note, "named owner");
    try expectContains(policy_note, "required approver set");
    try expectContains(policy_note, "benchmark-notes status");
    try expectContains(policy_note, "replay command");
    try expectContains(policy_note, "automatic return-to-blocked trigger");
    try expectContains(policy_note, "named reopen-trigger catalog item");
    try expectContains(policy_note, "trigger-specific evidence refresh");

    try expectContains(review_process, "named owner for the lane");
    try expectContains(review_process, "required approver set");
    try expectContains(review_process, "rollback threshold");
    try expectContains(review_process, "retired_from_active_discussion");

    try expectContains(parity_scorecard, "blocked status-change anchor count: `4`");
    try expectContains(parity_scorecard, "Architecture Council approvals recorded for status change: `0`");
    try expectContains(parity_scorecard, "keep the anchor frozen until");

    var saw_recordkeeping = false;
    var saw_exception_path = false;
    var saw_reopen_gate = false;
    var saw_reopen_catalog = false;
    var saw_blocker_gap = false;

    for (manifest.indefinite_c_requirements) |requirement| {
        try std.testing.expect(requirement.id.len > 0);
        try std.testing.expect(requirement.summary.len > 0);
        try std.testing.expect(requirement.required_terms.len >= 2);

        if (std.mem.eql(u8, requirement.id, "indefinite-c-recordkeeping")) {
            saw_recordkeeping = true;
            try std.testing.expectEqualStrings("named owner", requirement.required_terms[5]);
            try expectContains(requirement.required_terms[13], "automatic return-to-blocked trigger");
            try std.testing.expect(std.mem.indexOfScalar(u8, requirement.summary, '\n') == null);
        }
        if (std.mem.eql(u8, requirement.id, "indefinite-c-exception-path")) {
            saw_exception_path = true;
            try std.testing.expectEqual(@as(usize, 3), requirement.required_terms.len);
            try expectContains(requirement.required_terms[0], "no silent exception path");
        }
        if (std.mem.eql(u8, requirement.id, "indefinite-c-reopen-gate")) {
            saw_reopen_gate = true;
            try std.testing.expectEqual(@as(usize, 5), requirement.required_terms.len);
            try expectContains(requirement.required_terms[0], "named reopen-trigger catalog item");
            try expectContains(requirement.required_terms[4], "trigger-specific evidence refresh");
        }
        if (std.mem.eql(u8, requirement.id, "indefinite-c-reopen-trigger-catalog")) {
            saw_reopen_catalog = true;
            try std.testing.expectEqual(@as(usize, 3), requirement.required_terms.len);
        }
    }

    for (manifest.gaps) |gap| {
        try std.testing.expect(gap.id.len > 0);
        try std.testing.expect(gap.kind.len > 0);
        try std.testing.expect(gap.zigux_destination.len > 0);
        try std.testing.expect(gap.why_now.len > 0);

        if (std.mem.eql(u8, gap.id, "phase15-deep-core-status-change-blocker")) {
            saw_blocker_gap = true;
            try std.testing.expectEqualStrings("blocked_on_stay_in_c_evidence", gap.status);
            try std.testing.expectEqualStrings("Documentation/zigux/phase15-parity-scorecard.md", gap.zigux_destination);
        }
    }

    try std.testing.expect(saw_recordkeeping);
    try std.testing.expect(saw_exception_path);
    try std.testing.expect(saw_reopen_gate);
    try std.testing.expect(saw_reopen_catalog);
    try std.testing.expect(saw_blocker_gap);
}
