const std = @import("std");

const readme_path = "zigux-alpha/README.md";

const start_here_heading = "Start here";
const active_product_surfaces_heading = "Active product surfaces";

const start_here_lines = [_][]const u8{
    "- [ZAR to Zigux Product Roadmap](./ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md)",
    "- [Bootstrap Commit Ledger](./BOOTSTRAP_COMMIT_LEDGER.md)",
    "- [Live Product Docs](../Documentation/zigux/README.md)",
    "- [Review Checklist](../Documentation/zigux/review-checklist.md)",
    "- [Freeze Map](../Documentation/zigux/freeze-map.md)",
    "- [Freeze Governance Companion](../Documentation/zigux/phase15-freeze-map-governance.md)",
};

fn loadReadme() ![]u8 {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    return std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        readme_path,
        std.testing.allocator,
        .limited(32 * 1024),
    );
}

fn countOccurrences(haystack: []const u8, needle: []const u8) usize {
    var count: usize = 0;
    var offset: usize = 0;

    while (std.mem.indexOfPos(u8, haystack, offset, needle)) |index| {
        count += 1;
        offset = index + needle.len;
    }

    return count;
}

fn expectOrdered(readme: []const u8, needles: []const []const u8) !void {
    var cursor: usize = 0;

    for (needles) |needle| {
        const index = std.mem.indexOfPos(u8, readme, cursor, needle) orelse return error.MissingExpectedLine;
        cursor = index + needle.len;
    }
}

test "Lane 01 README keeps the Start here packet complete and ordered" {
    const readme = try loadReadme();
    defer std.testing.allocator.free(readme);

    try std.testing.expectEqual(@as(usize, 1), countOccurrences(readme, start_here_heading));
    try expectOrdered(readme, &start_here_lines);

    for (start_here_lines) |line| {
        try std.testing.expectEqual(@as(usize, 1), countOccurrences(readme, line));
    }
}

test "Lane 01 Start here packet follows active product surfaces handoff" {
    const readme = try loadReadme();
    defer std.testing.allocator.free(readme);

    const surfaces_index = std.mem.indexOf(u8, readme, active_product_surfaces_heading) orelse return error.MissingActiveProductSurfaces;
    const start_here_index = std.mem.indexOf(u8, readme, start_here_heading) orelse return error.MissingStartHere;

    try std.testing.expect(surfaces_index < start_here_index);
    try std.testing.expect(std.mem.indexOfPos(u8, readme, start_here_index, "[Live Product Docs](../Documentation/zigux/README.md)") != null);
    try std.testing.expect(std.mem.indexOfPos(u8, readme, start_here_index, "[Freeze Governance Companion](../Documentation/zigux/phase15-freeze-map-governance.md)") != null);
}

test "Lane 01 Start here packet rejects stale navigation replacements" {
    const readme = try loadReadme();
    defer std.testing.allocator.free(readme);

    try std.testing.expect(std.mem.indexOf(u8, readme, "../Documentation/zigux/status.md") == null);
    try std.testing.expect(std.mem.indexOf(u8, readme, "../Documentation/zigux/freeze-governance.md") == null);
    try std.testing.expect(std.mem.indexOf(u8, readme, "../zigux-alpha/BOOTSTRAP_COMMIT_LEDGER.md") == null);
}
