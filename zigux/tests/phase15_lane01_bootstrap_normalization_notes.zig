const std = @import("std");

const Section = struct {
    name: []const u8,
    marker: []const u8,
};

const required_sections = [_]Section{
    .{ .name = "inputs-reviewed", .marker = "## Inputs Reviewed" },
    .{ .name = "bundle-normalization", .marker = "## Bundle Normalization Notes" },
    .{ .name = "licensing", .marker = "## Licensing and Reuse Policy" },
};

const normalization_markers = [_][]const u8{
    "The workbook and CSV corpus are directionally aligned, but the workbook executive summary contains stale aggregate counts.",
    "Normalized counts from the extracted structured files:",
    "- phases: `15`",
    "- phase targets: `60`",
    "- parity-focus rows: `12`",
    "- workstreams: `15`",
    "- risks: `12`",
    "- structure rules: `18`",
    "- source anchors: `61`",
    "Stale executive-summary metadata in the workbook that should not drive planning:",
    "- phases: `17`",
    "- file-level target rows: `62`",
    "- workstreams: `17`",
    "- risks: `14`",
    "For execution, use the structured CSV/workbook tables themselves, not the executive-summary metrics block.",
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

test "lane 01 roadmap keeps normalization notes in the bootstrap charter sequence" {
    const roadmap = try readRepoFile("zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md", 128 * 1024);
    defer std.testing.allocator.free(roadmap);

    try expectSectionOrder(roadmap);
}

test "lane 01 roadmap preserves normalized and stale workbook count boundaries" {
    const roadmap = try readRepoFile("zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md", 128 * 1024);
    defer std.testing.allocator.free(roadmap);

    inline for (normalization_markers) |marker| {
        try expectContains(roadmap, marker);
    }
}
