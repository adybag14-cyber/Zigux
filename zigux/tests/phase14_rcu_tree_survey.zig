const std = @import("std");

const BoundaryMapEntry = struct {
    roadmap_destination: []const u8,
    current_state: []const u8,
    reviewable_artifact: []const u8,
    blocker: []const u8,
};

const DecisionChecklistEntry = struct {
    id: []const u8,
    ownership: []const u8,
    anchor_symbols: []const []const u8,
    rationale: []const u8,
};

const Gap = struct {
    id: []const u8,
    status: []const u8,
    kind: []const u8,
    zigux_destination: []const u8,
    why_now: []const u8,
};

const RollbackThreshold = struct {
    status_bucket: []const u8,
    review_blocker_status: []const u8,
    owner: []const u8,
    rollback_owner: []const u8,
    required_evidence: []const []const u8,
    rollback_triggers: []const []const u8,
};

const Manifest = struct {
    lane_key: []const u8,
    phase: []const u8,
    surveyed_commit: []const u8,
    anchor: []const u8,
    boundary_map: []const BoundaryMapEntry,
    decision_checklist: []const DecisionChecklistEntry,
    gaps: []const Gap,
    rollback_threshold: RollbackThreshold,
};

fn readFileAlloc(allocator: std.mem.Allocator, path: []const u8, limit: usize) ![]u8 {
    var io_instance: std.Io.Threaded = .init(allocator, .{});
    defer io_instance.deinit();

    return std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        path,
        allocator,
        .limited(limit),
    );
}

fn findChecklistEntry(entries: []const DecisionChecklistEntry, id: []const u8) ?DecisionChecklistEntry {
    for (entries) |entry| {
        if (std.mem.eql(u8, entry.id, id)) return entry;
    }
    return null;
}

fn findGap(entries: []const Gap, id: []const u8) ?Gap {
    for (entries) |entry| {
        if (std.mem.eql(u8, entry.id, id)) return entry;
    }
    return null;
}

test "phase 14 rcu tree manifest stays aligned with lane P14-L16 and the memory-ordering audit" {
    const allocator = std.testing.allocator;
    const manifest_json = try readFileAlloc(allocator, "zigux/tests/phase14_rcu_tree_manifest.json", 32 * 1024);
    defer allocator.free(manifest_json);

    const parsed = try std.json.parseFromSlice(Manifest, allocator, manifest_json, .{});
    defer parsed.deinit();

    const manifest = parsed.value;
    try std.testing.expectEqualStrings("P14-L16", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 14", manifest.phase);
    try std.testing.expectEqualStrings("355b71d89807a217a6b7c405c996cbd623c48ca0", manifest.surveyed_commit);
    try std.testing.expectEqualStrings("kernel/rcu/tree.c", manifest.anchor);
    try std.testing.expectEqual(@as(usize, 3), manifest.boundary_map.len);
    try std.testing.expectEqual(@as(usize, 7), manifest.decision_checklist.len);
    try std.testing.expectEqual(@as(usize, 17), manifest.gaps.len);

    const bridge_boundary = manifest.boundary_map[2];
    try std.testing.expectEqualStrings("kernel/rcu/tree_bridge.zig", bridge_boundary.roadmap_destination);
    try std.testing.expectEqualStrings("blocked_on_stay_in_c_evidence", bridge_boundary.current_state);
    try std.testing.expect(std.mem.indexOf(u8, bridge_boundary.blocker, "freeze-in-C") != null);
    try std.testing.expect(std.mem.indexOf(u8, bridge_boundary.blocker, "placeholder wrapper") != null);

    const memory_ordering = findChecklistEntry(manifest.decision_checklist, "memory-ordering-lock-network") orelse return error.MissingChecklistEntry;
    try std.testing.expectEqualStrings("stay_in_c", memory_ordering.ownership);
    try std.testing.expectEqualStrings("raw_spin_lock_rcu_node", memory_ordering.anchor_symbols[0]);
    try std.testing.expectEqualStrings("smp_mb__after_unlock_lock", memory_ordering.anchor_symbols[1]);
    try std.testing.expectEqualStrings("smp_store_release", memory_ordering.anchor_symbols[2]);
    try std.testing.expect(std.mem.indexOf(u8, memory_ordering.rationale, "memory-ordering") != null);

    const memory_ordering_gap = findGap(manifest.gaps, "phase14-rcu-tree-memory-ordering-followup") orelse return error.MissingGap;
    try std.testing.expectEqualStrings("starter_landed", memory_ordering_gap.status);
    try std.testing.expectEqualStrings("Documentation/zigux/phase14-rcu-tree-survey.md", memory_ordering_gap.zigux_destination);
    try std.testing.expect(std.mem.indexOf(u8, memory_ordering_gap.why_now, "raw_spin_lock_rcu_node()") != null);

    const bridge_blocker = findGap(manifest.gaps, "phase14-rcu-tree-bridge-blocker") orelse return error.MissingGap;
    try std.testing.expectEqualStrings("blocked_on_stay_in_c_evidence", bridge_blocker.status);

    var landed_count: usize = 0;
    var blocked_count: usize = 0;
    for (manifest.gaps) |gap| {
        if (std.mem.eql(u8, gap.status, "starter_landed")) landed_count += 1;
        if (std.mem.eql(u8, gap.status, "blocked_on_stay_in_c_evidence")) blocked_count += 1;
    }
    try std.testing.expectEqual(@as(usize, 16), landed_count);
    try std.testing.expectEqual(@as(usize, 1), blocked_count);
}

test "phase 14 rcu tree note, review checklist, and freeze map keep the blocked bridge packet explicit" {
    const allocator = std.testing.allocator;
    const survey_note = try readFileAlloc(allocator, "Documentation/zigux/phase14-rcu-tree-survey.md", 24 * 1024);
    defer allocator.free(survey_note);
    const review_checklist = try readFileAlloc(allocator, "Documentation/zigux/review-checklist.md", 32 * 1024);
    defer allocator.free(review_checklist);
    const freeze_map = try readFileAlloc(allocator, "Documentation/zigux/freeze-map.md", 16 * 1024);
    defer allocator.free(freeze_map);

    try std.testing.expect(std.mem.indexOf(u8, survey_note, "bounded Phase 14 survey lane `P14-L16` around `kernel/rcu/tree.c`") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "PHASE14_LANE_KEY=P14-L16") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "`kernel/rcu/tree_bridge.zig`: `blocked_on_stay_in_c_evidence`") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "placeholder wrapper") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "rollback owner: `Repo Tooling Pod`") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "memory-ordering network") != null);

    try std.testing.expect(std.mem.indexOf(u8, review_checklist, "Phase 14 RCU tree survey packet") != null);
    try std.testing.expect(std.mem.indexOf(u8, review_checklist, "`blocked_on_stay_in_c_evidence` boundary-map status for `kernel/rcu/tree_bridge.zig`") != null);

    try std.testing.expect(std.mem.indexOf(u8, freeze_map, "`kernel/rcu/tree.c`") != null);
    try std.testing.expect(std.mem.indexOf(u8, freeze_map, "rollback threshold that forces the anchor back to its blocked freeze posture") != null);
}
