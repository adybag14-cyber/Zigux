const std = @import("std");

const Gap = struct {
    id: []const u8,
    status: []const u8,
    kind: []const u8,
    zigux_destination: []const u8,
    why_now: []const u8,
};

const PolicyManifest = struct {
    lane_key: []const u8,
    phase: []const u8,
    surveyed_commit: []const u8,
    surveyed_commit_mode: []const u8,
    surveyed_commit_mode_reason: []const u8,
    roadmap_requirement: []const u8,
    anchors: []const []const u8,
    supporting_artifacts: []const []const u8,
    gaps: []const Gap,
};

const ScorecardPosture = struct {
    architecture_council_status_change_approval_recorded: bool,
    scorecard_role: []const u8,
};

const ScorecardMetrics = struct {
    active_freeze_in_c_anchor_count: usize,
    blocked_status_change_anchor_count: usize,
    architecture_council_status_change_approval_count: usize,
};

const ScorecardManifest = struct {
    lane_key: []const u8,
    posture: ScorecardPosture,
    metrics: ScorecardMetrics,
};

fn readRepoFile(path: []const u8, limit: usize) ![]u8 {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();
    return std.Io.Dir.cwd().readFileAlloc(io_instance.io(), path, std.testing.allocator, .limited(limit));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectListContains(list: []const []const u8, needle: []const u8) !void {
    for (list) |item| {
        if (std.mem.eql(u8, item, needle)) return;
    }
    return error.TestUnexpectedResult;
}

fn isDatedMasterReadbackMarker(text: []const u8) bool {
    return std.mem.startsWith(u8, text, "current-master-readback-");
}

fn findGap(gaps: []const Gap, id: []const u8) ?Gap {
    for (gaps) |gap| {
        if (std.mem.eql(u8, gap.id, id)) return gap;
    }
    return null;
}

test "phase 15 blocker evidence packet keeps the blocked posture and focused companions explicit" {
    const policy_json = try readRepoFile("zigux/tests/phase15_indefinite_c_policy.json", 24 * 1024);
    defer std.testing.allocator.free(policy_json);

    const parsed = try std.json.parseFromSlice(PolicyManifest, std.testing.allocator, policy_json, .{
        .ignore_unknown_fields = true,
    });
    defer parsed.deinit();
    const manifest = parsed.value;

    try std.testing.expectEqualStrings("P15-L16", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 15", manifest.phase);
    try std.testing.expect(isDatedMasterReadbackMarker(manifest.surveyed_commit));
    try std.testing.expectEqualStrings("dated_master_readback", manifest.surveyed_commit_mode);
    try expectContains(manifest.surveyed_commit_mode_reason, "dated master-readback marker");
    try std.testing.expectEqualStrings("policy for code that remains in C indefinitely", manifest.roadmap_requirement);
    try std.testing.expectEqual(@as(usize, 4), manifest.anchors.len);
    try expectListContains(manifest.supporting_artifacts, "zigux/tests/phase15_indefinite_c_blocker_evidence.zig");
    try expectListContains(manifest.supporting_artifacts, "zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig");
    try expectListContains(manifest.supporting_artifacts, "zigux/tests/phase15_build.zig");

    const dated_refresh = findGap(manifest.gaps, "phase15-indefinite-c-dated-readback-provenance-refresh") orelse return error.MissingGap;
    try std.testing.expectEqualStrings("landed", dated_refresh.status);
    try std.testing.expectEqualStrings("provenance_refresh", dated_refresh.kind);
    try expectContains(dated_refresh.why_now, "dated readback marker");

    const blocker_gap = findGap(manifest.gaps, "phase15-deep-core-status-change-blocker") orelse return error.MissingGap;
    try std.testing.expectEqualStrings("blocked_on_stay_in_c_evidence", blocker_gap.status);
    try std.testing.expectEqualStrings("Documentation/zigux/phase15-parity-scorecard.md", blocker_gap.zigux_destination);
    try expectContains(blocker_gap.why_now, "lacks evidence strong enough");
}

test "phase 15 blocker evidence docs and scorecard still agree on the no approval posture" {
    const policy_note = try readRepoFile("Documentation/zigux/phase15-indefinite-c-policy.md", 24 * 1024);
    defer std.testing.allocator.free(policy_note);

    const review_process = try readRepoFile("Documentation/zigux/phase15-architecture-council-review-process.md", 32 * 1024);
    defer std.testing.allocator.free(review_process);

    const readiness_note = try readRepoFile("Documentation/zigux/phase15-readiness-gate-survey.md", 24 * 1024);
    defer std.testing.allocator.free(readiness_note);

    const scorecard_doc = try readRepoFile("Documentation/zigux/phase15-parity-scorecard.md", 24 * 1024);
    defer std.testing.allocator.free(scorecard_doc);

    const scorecard_json = try readRepoFile("zigux/tests/phase15_parity_scorecard.json", 24 * 1024);
    defer std.testing.allocator.free(scorecard_json);

    const parsed = try std.json.parseFromSlice(ScorecardManifest, std.testing.allocator, scorecard_json, .{
        .ignore_unknown_fields = true,
    });
    defer parsed.deinit();

    try std.testing.expectEqualStrings("P15-Y03", parsed.value.lane_key);
    try std.testing.expect(!parsed.value.posture.architecture_council_status_change_approval_recorded);
    try std.testing.expectEqualStrings("blocked_posture_accounting_not_port_readiness", parsed.value.posture.scorecard_role);
    try std.testing.expectEqual(@as(usize, 4), parsed.value.metrics.active_freeze_in_c_anchor_count);
    try std.testing.expectEqual(@as(usize, 4), parsed.value.metrics.blocked_status_change_anchor_count);
    try std.testing.expectEqual(@as(usize, 0), parsed.value.metrics.architecture_council_status_change_approval_count);

    try expectContains(policy_note, "PHASE15_PROVENANCE_MODE=dated_master_readback");
    try expectContains(policy_note, "current-master-readback-2026-05-13");
    try expectContains(policy_note, "There is no silent exception path around the indefinite-C policy.");
    try expectContains(policy_note, "The only allowed exception is an Architecture Council reopen request");
    try expectContains(policy_note, "existing blocker remains recorded");
    try expectContains(review_process, "no Architecture Council approval is currently recorded for a freeze-map status change");
    try expectContains(readiness_note, "the remaining blocker is still `phase15-deep-core-status-change-blocker`");
    try expectContains(scorecard_doc, "Architecture Council approvals recorded for status change: `0`");
    try expectContains(scorecard_doc, "blocked status-change anchor count: `4`");
}