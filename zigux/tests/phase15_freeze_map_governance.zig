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

fn expectSliceContains(haystack: []const []const u8, needle: []const u8) !void {
    for (haystack) |item| if (std.mem.eql(u8, item, needle)) return;
    return error.TestUnexpectedResult;
}

test "phase 15 freeze-map manifest records route recovery without status change" {
    const manifest = try readRepoFile("zigux/tests/phase15_freeze_map_manifest.json");
    defer std.testing.allocator.free(manifest);

    try expectContains(manifest, "current-master-readback-2026-07-21");
    try expectContains(manifest, "phase15-shared-wrapper-route-readback");
    try expectContains(manifest, "materialized_in_contents_readback");
    try expectContains(manifest, "phase15-validate, phase15-test, and phase15");
    try expectContains(manifest, "separate Architecture Council decision before any freeze-map status change");
}

test "phase 15 freeze-map governance keeps deep-core and study-only boundaries exact" {
    const freeze_map = try readRepoFile("Documentation/zigux/freeze-map.md");
    defer std.testing.allocator.free(freeze_map);
    const route_note = try readRepoFile("Documentation/zigux/phase15-route-recovery.md");
    defer std.testing.allocator.free(route_note);

    for ([_][]const u8{
        "kernel/sched/core.c",
        "mm/page_alloc.c",
        "kernel/rcu/tree.c",
        "net/core/skbuff.c",
        "kernel/workqueue.c",
        "kernel/trace/ring_buffer.c",
    }) |marker| try expectContains(freeze_map, marker);
    try expectContains(route_note, "PHASE15_FREEZE_MAP_STATUS_CHANGE=false");
    try expectContains(route_note, "PHASE15_STUDY_ONLY_BOUNDARY_UNCHANGED=true");
    try expectContains(route_note, "No direct deep-core Zig delivery claim");
}

test "phase 15 freeze-map governance keeps maintenance replay current" {
    const manifest = try readRepoFile("zigux/tests/phase15_freeze_map_manifest.json");
    defer std.testing.allocator.free(manifest);
    try expectContains(manifest, "Documentation/zigux/phase15-route-recovery.md");
    try expectContains(manifest, ".github/workflows/zigux-bootstrap.yml");
    try expectContains(manifest, "zigux/tests/phase15_route_recovery.zig");
    try expectContains(manifest, "scripts\\\\zigux/check_phase15_blocked_route_recovery.zig");
}
