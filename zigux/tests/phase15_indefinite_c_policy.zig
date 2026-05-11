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

const Manifest = struct {
    lane_key: []const u8,
    phase: []const u8,
    surveyed_commit: []const u8,
    roadmap_requirement: []const u8,
    anchors: []const []const u8,
    supporting_artifacts: []const []const u8,
    indefinite_c_requirements: []const Requirement,
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

fn isLowerHexCommitId(text: []const u8) bool {
    if (text.len != 40) return false;
    for (text) |ch| {
        if (!std.ascii.isHex(ch) or std.ascii.isUpper(ch)) return false;
    }
    return true;
}

test "phase 15 indefinite-C policy packet matches the current ownership and exception posture" {
    const policy_note = try readRepoFile("Documentation/zigux/phase15-indefinite-c-policy.md", 24 * 1024);
    defer std.testing.allocator.free(policy_note);

    const review_process = try readRepoFile("Documentation/zigux/phase15-architecture-council-review-process.md", 24 * 1024);
    defer std.testing.allocator.free(review_process);

    const manifest_json = try readRepoFile("zigux/tests/phase15_indefinite_c_policy.json", 24 * 1024);
    defer std.testing.allocator.free(manifest_json);

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{});
    defer parsed.deinit();

    const manifest = parsed.value;
    try std.testing.expectEqualStrings("P15-L16", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 15", manifest.phase);
    try std.testing.expect(isLowerHexCommitId(manifest.surveyed_commit));
    try std.testing.expectEqualStrings("policy for code that remains in C indefinitely", manifest.roadmap_requirement);
    try std.testing.expectEqual(@as(usize, 4), manifest.anchors.len);
    try std.testing.expectEqual(@as(usize, 8), manifest.supporting_artifacts.len);
    try std.testing.expectEqual(@as(usize, 6), manifest.indefinite_c_requirements.len);
    try std.testing.expectEqual(@as(usize, 6), manifest.gaps.len);

    try expectContains(policy_note, "PHASE15_LANE_KEY=P15-L16");
    try expectContains(policy_note, "There is no silent exception path around the indefinite-C policy.");
    try expectContains(policy_note, "The only allowed exception is an Architecture Council reopen request");
    try expectContains(policy_note, "the existing blocker remains recorded");
    try expectContains(policy_note, "Keep this lane in maintenance mode until new stay-in-C evidence changes one of the named reopen triggers or the deep-core blocker posture changes.");
    try expectContains(policy_note, "lane owner");
    try std.testing.expect(std.mem.indexOf(u8, policy_note, "named owner") == null);

    try expectContains(review_process, "named owner for the lane");
    try expectContains(review_process, "required approver set");
    try expectContains(review_process, "lane ownership");

    var saw_recordkeeping = false;
    var saw_exception_path = false;
    var saw_reopen_catalog = false;
    var saw_blocker_gap = false;

    for (manifest.indefinite_c_requirements) |requirement| {
        try std.testing.expect(requirement.id.len > 0);
        try std.testing.expect(requirement.summary.len > 0);
        try std.testing.expect(requirement.required_terms.len >= 2);

        if (std.mem.eql(u8, requirement.id, "indefinite-c-recordkeeping")) {
            saw_recordkeeping = true;
            try std.testing.expectEqualStrings("lane owner", requirement.required_terms[3]);
            try std.testing.expect(std.mem.indexOfScalar(u8, requirement.summary, '\n') == null);
        }
        if (std.mem.eql(u8, requirement.id, "indefinite-c-exception-path")) {
            saw_exception_path = true;
            try std.testing.expectEqual(@as(usize, 3), requirement.required_terms.len);
            try expectContains(requirement.required_terms[0], "no silent exception path");
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
    try std.testing.expect(saw_reopen_catalog);
    try std.testing.expect(saw_blocker_gap);
}
