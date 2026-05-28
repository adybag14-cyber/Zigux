const std = @import("std");

const Section = struct {
    name: []const u8,
    marker: []const u8,
};

const required_sections = [_]Section{
    .{ .name = "bundle-normalization", .marker = "## Bundle Normalization Notes" },
    .{ .name = "licensing", .marker = "## Licensing and Reuse Policy" },
    .{ .name = "non-negotiable-rules", .marker = "## Non-Negotiable Product Rules" },
};

const licensing_markers = [_][]const u8{
    "For Zigux product work, licensing is not the blocker.",
    "Working rule for this repo:",
    "- direct copies from same-license Zigux or ZAR material are allowed when legally valid and reviewable",
    "- machine translations or human translations from Linux C into Zig are allowed when legally valid and reviewable",
    "- adaptations from Linux, ZAR, or other same-license material are allowed when legally valid and reviewable",
    "That does not remove engineering discipline.",
    "Even when copying or translating is legally allowed, the product still requires:",
    "- bounded scope",
    "- explicit ownership",
    "- parity and validation gates",
    "- rollback paths",
    "- maintainable placement in the Linux-owned tree",
    "Legal permission expands the implementation options.",
    "It does not justify mirror-tree sprawl, unclear ownership, or skipping validation.",
};

fn readRepoFile(path: []const u8, limit: usize) ![]u8 {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const prefixes = [_][]const u8{ "", "../", "../../" };
    for (prefixes) |prefix| {
        const candidate = if (prefix.len == 0)
            path
        else
            try std.mem.concat(std.testing.allocator, u8, &.{ prefix, path });
        defer if (prefix.len != 0) std.testing.allocator.free(candidate);

        return std.Io.Dir.cwd().readFileAlloc(io_instance.io(), candidate, std.testing.allocator, .limited(limit)) catch |err| switch (err) {
            error.FileNotFound => continue,
            else => return err,
        };
    }

    return error.FileNotFound;
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectSectionOrder(haystack: []const u8) !void {
    var previous: ?usize = null;
    for (required_sections) |section| {
        const current = std.mem.indexOf(u8, haystack, section.marker) orelse return error.MissingRoadmapSection;
        if (previous) |position| {
            try std.testing.expect(current > position);
        }
        previous = current;
    }
}

test "lane 01 roadmap keeps licensing policy in the bootstrap charter sequence" {
    const roadmap = try readRepoFile("zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md", 128 * 1024);
    defer std.testing.allocator.free(roadmap);

    try expectSectionOrder(roadmap);
}

test "lane 01 roadmap preserves the licensing and reuse policy packet" {
    const roadmap = try readRepoFile("zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md", 128 * 1024);
    defer std.testing.allocator.free(roadmap);

    inline for (licensing_markers) |marker| {
        try expectContains(roadmap, marker);
    }
}
