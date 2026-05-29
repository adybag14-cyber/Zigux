const std = @import("std");

const Section = struct {
    name: []const u8,
    marker: []const u8,
};

const required_sections = [_]Section{
    .{ .name = "zar-feed", .marker = "## How ZAR Should Feed Zigux" },
    .{ .name = "alpha-scope", .marker = "## zigux-alpha Scope" },
    .{ .name = "phase-features", .marker = "## Product Features by Phase" },
};

const staging_markers = [_][]const u8{
    "`zigux-alpha/` is the staging area for:",
    "- roadmap and phase sequencing",
    "- source mapping",
    "- validation strategy",
    "- freeze map",
    "- first commit ledger",
    "- workstream ownership",
};

const non_final_home_markers = [_][]const u8{
    "`zigux-alpha/` is not the final home for:",
    "- subsystem ports",
    "- runtime helpers",
    "- drivers",
    "- bindings",
    "- UAPI shims",
};

const destination_markers = [_][]const u8{
    "Those should eventually land in:",
    "- `tools/lib/*.zig`",
    "- `scripts/zigux/`",
    "- `zigux/`",
    "- `Documentation/zigux/`",
    "- `samples/zigux/`",
    "- `lib/*.zig`",
    "- `drivers/*/*.zig`",
    "- `fs/*.zig`",
    "- `security/*/*.zig`",
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

fn expectMarkerSet(haystack: []const u8, comptime markers: []const []const u8) !void {
    inline for (markers) |marker| {
        try expectContains(haystack, marker);
    }
}

test "lane 01 roadmap keeps alpha scope in the bootstrap charter sequence" {
    const roadmap = try readRepoFile("zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md", 128 * 1024);
    defer std.testing.allocator.free(roadmap);

    try expectSectionOrder(roadmap);
}

test "lane 01 roadmap preserves alpha staging and non-final-home boundaries" {
    const roadmap = try readRepoFile("zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md", 128 * 1024);
    defer std.testing.allocator.free(roadmap);

    try expectMarkerSet(roadmap, &staging_markers);
    try expectMarkerSet(roadmap, &non_final_home_markers);
}

test "lane 01 roadmap preserves eventual destination paths for real Zigux code" {
    const roadmap = try readRepoFile("zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md", 128 * 1024);
    defer std.testing.allocator.free(roadmap);

    try expectMarkerSet(roadmap, &destination_markers);
}
