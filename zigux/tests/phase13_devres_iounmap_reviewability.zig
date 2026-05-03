const std = @import("std");
const devres = @import("devres");

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectNotContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

test "phase13 devres iounmap descriptor keeps the planner explicit" {
    const descriptor = devres.DevresHelperLab.descriptor();

    try std.testing.expectEqualStrings("lib/devres.c", descriptor.anchor);
    try std.testing.expect(descriptor.provides_iounmap_call_planning);

    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const devres_source = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "lib/devres.zig",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(devres_source);

    try expectContains(devres_source, ".provides_iounmap_call_planning = true");
    try expectContains(devres_source, "pub fn planManagedIounmap(");
    try expectContains(devres_source, ".warns_on_release_miss = !release_matches");
    try expectNotContains(devres_source, "iounmap(");
}

test "phase13 devres iounmap planner stays pointer-exact and warns on release misses" {
    const exact = devres.DevresHelperLab.planManagedIounmap(0x4000, 0x4000);
    try std.testing.expectEqualStrings("lib/devres.c", exact.anchor);
    try std.testing.expectEqual(@as(usize, 0x4000), exact.tracked_address);
    try std.testing.expectEqual(@as(usize, 0x4000), exact.candidate_address);
    try std.testing.expect(exact.release_matches);
    try std.testing.expect(!exact.warns_on_release_miss);

    const miss = devres.DevresHelperLab.planManagedIounmap(0x4000, 0x4010);
    try std.testing.expectEqualStrings("lib/devres.c", miss.anchor);
    try std.testing.expectEqual(@as(usize, 0x4000), miss.tracked_address);
    try std.testing.expectEqual(@as(usize, 0x4010), miss.candidate_address);
    try std.testing.expect(!miss.release_matches);
    try std.testing.expect(miss.warns_on_release_miss);
}
