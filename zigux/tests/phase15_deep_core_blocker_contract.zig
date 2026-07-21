const std = @import("std");

fn readRepoFile(path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(
        std.testing.io,
        path,
        std.testing.allocator,
        .limited(1024 * 1024),
    );
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectNotContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

test "phase 15 deep-core blockers remain explicit" {
    const survey = try readRepoFile("Documentation/zigux/phase15-deep-core-blocker-survey.md");
    defer std.testing.allocator.free(survey);
    for ([_][]const u8{
        "kernel/sched/core.c",
        "mm/page_alloc.c",
        "kernel/rcu/tree.c",
        "net/core/skbuff.c",
    }) |anchor| try expectContains(survey, anchor);
}

test "route recovery preserves deep-core and study-only boundaries" {
    const note = try readRepoFile("Documentation/zigux/phase15-route-recovery.md");
    defer std.testing.allocator.free(note);
    const checker = try readRepoFile("scripts/zigux/check_phase15_blocked_route_recovery.zig");
    defer std.testing.allocator.free(checker);
    try expectContains(note, "PHASE15_FREEZE_MAP_STATUS_CHANGE=false");
    try expectContains(note, "PHASE15_STUDY_ONLY_BOUNDARY_UNCHANGED=true");
    try expectContains(checker, "PHASE15_ROUTE_RECOVERY_NO_APPROVAL_CLAIM=true");
}
