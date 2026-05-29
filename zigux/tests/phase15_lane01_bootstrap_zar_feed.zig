const std = @import("std");

fn readRoadmap() ![]u8 {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    return std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md",
        std.testing.allocator,
        .limited(1024 * 1024),
    ) catch std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "../../zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md",
        std.testing.allocator,
        .limited(1024 * 1024),
    );
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectOrder(haystack: []const u8, before: []const u8, after: []const u8) !void {
    const before_index = std.mem.indexOf(u8, haystack, before) orelse return error.MissingBeforeMarker;
    const after_index = std.mem.indexOf(u8, haystack, after) orelse return error.MissingAfterMarker;
    try std.testing.expect(before_index < after_index);
}

test "ZAR feed table preserves high-value transfer lanes" {
    const roadmap = try readRoadmap();
    defer std.testing.allocator.free(roadmap);

    const heading = "## How ZAR Should Feed Zigux";
    const section_start = std.mem.indexOf(u8, roadmap, heading) orelse return error.MissingZarFeedSection;
    const alpha_scope_start = std.mem.indexOf(u8, roadmap, "## zigux-alpha Scope") orelse return error.MissingAlphaScopeSection;
    try std.testing.expect(section_start < alpha_scope_start);

    const section = roadmap[section_start..alpha_scope_start];

    try expectContains(section, "ZAR should not try to become Zigux.");
    try expectContains(section, "parity gates and drift checks | High | Rebuild as Linux-facing differential gates inside `zigux/tests/` and `scripts/zigux/` | 2-4");
    try expectContains(section, "build reproducibility discipline | High | Transfer the release-gate mindset, not the exact scripts | 2-4");
    try expectContains(section, "ABI/export/wrapper discipline | High | Convert to Linux-kernel-specific `zigux/` substrate rules | 3");
    try expectContains(section, "driver lifecycle proofs | High | Use to shape lab matrices, teardown checks, and failure-mode expectations | 10-12");
}

test "ZAR feed table keeps experimental work bounded" {
    const roadmap = try readRoadmap();
    defer std.testing.allocator.free(roadmap);

    const heading = "## How ZAR Should Feed Zigux";
    const section_start = std.mem.indexOf(u8, roadmap, heading) orelse return error.MissingZarFeedSection;
    const alpha_scope_start = std.mem.indexOf(u8, roadmap, "## zigux-alpha Scope") orelse return error.MissingAlphaScopeSection;
    try std.testing.expect(section_start < alpha_scope_start);

    const section = roadmap[section_start..alpha_scope_start];

    try expectContains(section, "bare-metal i386 platform and SMP research | Medium | Use as concurrency-validation research input only | 4, 9, 14");
    try expectContains(section, "shell, TTY, tool-service runtime | Low | Product value is indirect; use only where it informs repo-hosted tooling or validation UX | 4-8");
    try expectContains(section, "workspace/package/trust runtime | Low | Mostly ZAR-specific; keep out of near-term Zigux product scope | research only");
    try expectContains(section, "VFS overlay experiments | Medium | Use only as design lessons for bounded helper layers, not as a direct port target | 13-15");
}

test "ZAR feed rule remains before the alpha folder charter" {
    const roadmap = try readRoadmap();
    defer std.testing.allocator.free(roadmap);

    try expectOrder(roadmap, "## Non-Negotiable Product Rules", "## How ZAR Should Feed Zigux");
    try expectOrder(roadmap, "## How ZAR Should Feed Zigux", "The rule is simple:");
    try expectOrder(roadmap, "The rule is simple:", "## zigux-alpha Scope");

    try expectContains(roadmap, "If a ZAR slice reduces Zigux product risk, keep it.");
    try expectContains(roadmap, "only expands ZAR");
    try expectContains(roadmap, "do not let it consume Zigux product bandwidth.");
}
