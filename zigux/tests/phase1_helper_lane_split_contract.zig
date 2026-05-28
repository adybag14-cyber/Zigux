const std = @import("std");

const HelperFamily = enum {
    shared_replay_parked,
    direct_anchor_followup,
};

const HelperLane = struct {
    path: []const u8,
    family: HelperFamily,
};

const helper_lanes = [_]HelperLane{
    .{ .path = "tools/lib/argv_split.zig", .family = .shared_replay_parked },
    .{ .path = "tools/lib/cmdline.zig", .family = .shared_replay_parked },
    .{ .path = "tools/lib/ctype.zig", .family = .shared_replay_parked },
    .{ .path = "tools/lib/hweight.zig", .family = .shared_replay_parked },
    .{ .path = "tools/lib/list_sort.zig", .family = .shared_replay_parked },
    .{ .path = "tools/lib/slab.zig", .family = .shared_replay_parked },
    .{ .path = "tools/lib/str_error_r.zig", .family = .shared_replay_parked },
    .{ .path = "tools/lib/vsprintf.zig", .family = .shared_replay_parked },
    .{ .path = "tools/lib/zalloc.zig", .family = .shared_replay_parked },
    .{ .path = "tools/lib/bitmap.zig", .family = .direct_anchor_followup },
    .{ .path = "tools/lib/find_bit.zig", .family = .direct_anchor_followup },
    .{ .path = "tools/lib/rbtree.zig", .family = .direct_anchor_followup },
    .{ .path = "tools/lib/string.zig", .family = .direct_anchor_followup },
};

const shared_replay_csv = "tools/lib/argv_split.zig,tools/lib/cmdline.zig,tools/lib/ctype.zig,tools/lib/hweight.zig,tools/lib/list_sort.zig,tools/lib/slab.zig,tools/lib/str_error_r.zig,tools/lib/vsprintf.zig,tools/lib/zalloc.zig";
const direct_anchor_csv = "tools/lib/bitmap.zig,tools/lib/find_bit.zig,tools/lib/rbtree.zig,tools/lib/string.zig";

fn contains(haystack: []const u8, needle: []const u8) bool {
    return std.mem.indexOf(u8, haystack, needle) != null;
}

fn openRepoRoot() !std.Io.Dir {
    const candidates = [_][]const u8{ ".", "..", "../.." };
    for (candidates) |candidate| {
        var dir = std.Io.Dir.cwd().openDir(std.testing.io, candidate, .{}) catch continue;
        if (dir.access(std.testing.io, "Documentation/zigux/phase1-closure.md", .{})) |_| {
            return dir;
        } else |_| {
            dir.close(std.testing.io);
        }
    }
    return error.RepositoryRootNotFound;
}

fn readRepoFile(allocator: std.mem.Allocator, root: std.Io.Dir, path: []const u8) ![]u8 {
    return root.readFileAlloc(std.testing.io, path, allocator, .limited(1024 * 1024));
}

fn countFamily(family: HelperFamily) usize {
    var count: usize = 0;
    for (helper_lanes) |entry| {
        if (entry.family == family) count += 1;
    }
    return count;
}

fn expectFamilyPathList(note: []const u8, marker: []const u8, csv: []const u8) !void {
    var expected: [512]u8 = undefined;
    const expected_text = try std.fmt.bufPrint(&expected, "`{s}={s}`", .{ marker, csv });
    try std.testing.expect(contains(note, expected_text));
}

test "phase 1 helper lane split keeps the closed helper count exact" {
    try std.testing.expectEqual(@as(usize, 13), helper_lanes.len);
    try std.testing.expectEqual(@as(usize, 9), countFamily(.shared_replay_parked));
    try std.testing.expectEqual(@as(usize, 4), countFamily(.direct_anchor_followup));
    try std.testing.expectEqualStrings("tools/lib/argv_split.zig", helper_lanes[0].path);
    try std.testing.expectEqualStrings("tools/lib/string.zig", helper_lanes[helper_lanes.len - 1].path);
}

test "phase 1 lane sequencing note names the shared and direct helper rosters" {
    var root = try openRepoRoot();
    defer root.close(std.testing.io);

    const lane_note = try readRepoFile(std.testing.allocator, root, "Documentation/zigux/phase1-host-helper-lane-sequencing.md");
    defer std.testing.allocator.free(lane_note);

    try expectFamilyPathList(lane_note, "PHASE1_SHARED_REPLAY_PARKED_HELPERS", shared_replay_csv);
    try expectFamilyPathList(lane_note, "PHASE1_DIRECT_ANCHOR_FOLLOWUP_HELPERS", direct_anchor_csv);
    try std.testing.expect(contains(lane_note, "shared-replay parked helpers reopen only for packet drift"));
    try std.testing.expect(contains(lane_note, "direct-anchor helpers reopen only for their existing helper-local anchors"));

    for (helper_lanes) |entry| {
        var bullet: [128]u8 = undefined;
        const bullet_text = try std.fmt.bufPrint(&bullet, "- `{s}`", .{entry.path});
        try std.testing.expect(contains(lane_note, bullet_text));
    }
}

test "phase 1 closure note preserves the same lane split tie-breakers" {
    var root = try openRepoRoot();
    defer root.close(std.testing.io);

    const closure_note = try readRepoFile(std.testing.allocator, root, "Documentation/zigux/phase1-closure.md");
    defer std.testing.allocator.free(closure_note);

    try std.testing.expect(contains(closure_note, "`PHASE1_STATUS=parked`"));
    try std.testing.expect(contains(closure_note, "`PHASE1_HELPER_COUNT=13`"));
    try std.testing.expect(contains(closure_note, "bounded Phase 1 helper tranche is still the same thirteen helper ports named in the committed manifest"));
    try std.testing.expect(contains(closure_note, "shared tests-root smoke route and committed Phase 1 fixture already recheck duplicate-range iteration"));
    try std.testing.expect(contains(closure_note, "`PHASE1_NEXT_SAFE_STEP=sync one shared reminder surface or one helper-family tie-breaker"));
}

test "phase 1 helper manifest records the lane split as structured evidence" {
    var root = try openRepoRoot();
    defer root.close(std.testing.io);

    const manifest = try readRepoFile(std.testing.allocator, root, "zigux/tests/fixtures/phase1_helper_manifest.json");
    defer std.testing.allocator.free(manifest);

    try std.testing.expect(contains(manifest, "\"helper_count\": 13"));
    try std.testing.expect(contains(manifest, "\"lane_sequencing\""));
    try std.testing.expect(contains(manifest, "\"shared_replay_parked_helpers\""));
    try std.testing.expect(contains(manifest, "\"direct_anchor_followup_helpers\""));
    try std.testing.expect(contains(manifest, "\"rule_summary\": \"Phase 1 helper follow-up stays parked on shared replay for the nine helpers above"));
    try std.testing.expect(contains(manifest, "\"anti_overlap_rule\": \"Do not reopen Phase 1 by batching helpers across those two sets in one lane"));

    for (helper_lanes) |entry| {
        try std.testing.expect(contains(manifest, entry.path));
    }
}
