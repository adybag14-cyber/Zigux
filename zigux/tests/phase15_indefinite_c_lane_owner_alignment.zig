const std = @import("std");

const EvidenceArchive = struct {
    latest_blocker_disposition: []const u8,
};

const ScorecardAnchor = struct {
    path: []const u8,
    lane_owner: []const u8,
    phase: []const u8,
    current_status_bucket: []const u8,
    required_approver_set: []const u8,
    validation_gate_summary: []const u8,
    rollback_owner: []const u8,
    current_blocker: []const u8,
    evidence_archive: EvidenceArchive,
};

const ScorecardManifest = struct {
    anchors: []const ScorecardAnchor,
};

const OwnershipRecord = struct {
    anchor: []const u8,
    owner: []const u8,
    phase: []const u8,
    status_bucket: []const u8,
    required_approver_set: []const u8,
    validation_gate: []const u8,
    rollback_owner: []const u8,
    latest_blocker_disposition: []const u8,
};

const FreezeMapManifest = struct {
    blocker_ownership: []const OwnershipRecord,
};

fn readRepoFile(path: []const u8, limit: usize) ![]u8 {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();
    return std.Io.Dir.cwd().readFileAlloc(io_instance.io(), path, std.testing.allocator, .limited(limit));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

test "phase 15 lane owner alignment stays synced between the scorecard and freeze-map manifest" {
    const scorecard_json = try readRepoFile("zigux/tests/phase15_parity_scorecard.json", 24 * 1024);
    defer std.testing.allocator.free(scorecard_json);
    const scorecard = try std.json.parseFromSlice(ScorecardManifest, std.testing.allocator, scorecard_json, .{
        .ignore_unknown_fields = true,
    });
    defer scorecard.deinit();

    const freeze_map_json = try readRepoFile("zigux/tests/phase15_freeze_map_manifest.json", 40 * 1024);
    defer std.testing.allocator.free(freeze_map_json);
    const freeze_map = try std.json.parseFromSlice(FreezeMapManifest, std.testing.allocator, freeze_map_json, .{
        .ignore_unknown_fields = true,
    });
    defer freeze_map.deinit();

    try std.testing.expectEqual(scorecard.value.anchors.len, freeze_map.value.blocker_ownership.len);

    for (scorecard.value.anchors, freeze_map.value.blocker_ownership) |anchor, ownership| {
        try std.testing.expectEqualStrings(anchor.path, ownership.anchor);
        try std.testing.expectEqualStrings(anchor.lane_owner, ownership.owner);
        try std.testing.expectEqualStrings(anchor.phase, ownership.phase);
        try std.testing.expectEqualStrings(anchor.current_status_bucket, ownership.status_bucket);
        try std.testing.expectEqualStrings(anchor.required_approver_set, ownership.required_approver_set);
        try std.testing.expectEqualStrings(anchor.validation_gate_summary, ownership.validation_gate);
        try std.testing.expectEqualStrings(anchor.rollback_owner, ownership.rollback_owner);
        try std.testing.expectEqualStrings(anchor.evidence_archive.latest_blocker_disposition, ownership.latest_blocker_disposition);
        try std.testing.expectEqualStrings(anchor.current_blocker, ownership.latest_blocker_disposition);
    }
}

test "phase 15 lane owner alignment remains reviewable in the note surfaces" {
    const governance_note = try readRepoFile("Documentation/zigux/phase15-freeze-map-governance.md", 32 * 1024);
    defer std.testing.allocator.free(governance_note);

    const review_process = try readRepoFile("Documentation/zigux/phase15-architecture-council-review-process.md", 32 * 1024);
    defer std.testing.allocator.free(review_process);

    const policy_note = try readRepoFile("Documentation/zigux/phase15-indefinite-c-policy.md", 24 * 1024);
    defer std.testing.allocator.free(policy_note);

    try expectContains(governance_note, "Architecture Council + PMO / Release Management");
    try expectContains(governance_note, "Architecture Council + Validation and Perf Team");
    try expectContains(governance_note, "Architecture Council + ABI and Runtime Team");
    try expectContains(governance_note, "Architecture Council + Shared Subsystems Pod");
    try expectContains(review_process, "named owner for the lane");
    try expectContains(review_process, "required approver set");
    try expectContains(policy_note, "lane owner");
    try expectContains(policy_note, "required approver set");
}
