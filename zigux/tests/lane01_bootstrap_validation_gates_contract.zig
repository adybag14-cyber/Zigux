const std = @import("std");

const roadmap_path = "../../zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md";

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectBefore(haystack: []const u8, earlier: []const u8, later: []const u8) !void {
    const earlier_index = std.mem.indexOf(u8, haystack, earlier) orelse return error.MissingEarlierMarker;
    const later_index = std.mem.indexOf(u8, haystack, later) orelse return error.MissingLaterMarker;
    try std.testing.expect(earlier_index < later_index);
}

fn readRoadmap(allocator: std.mem.Allocator) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(std.testing.io, roadmap_path, allocator, .limited(128 * 1024));
}

fn validationGatesSection(roadmap: []const u8) ![]const u8 {
    const section_start = std.mem.indexOf(u8, roadmap, "## Recommended Validation Gates") orelse return error.MissingValidationGatesSection;
    const section_end = std.mem.indexOfPos(u8, roadmap, section_start, "## What Should Start Next in Zigux") orelse return error.MissingNextSection;
    return roadmap[section_start..section_end];
}

test "roadmap keeps recommended validation gates between commit train and next-step packet" {
    const roadmap = try readRoadmap(std.testing.allocator);
    defer std.testing.allocator.free(roadmap);

    try expectBefore(roadmap, "## First Commit and Push Sequence for Zigux", "## Recommended Validation Gates");
    try expectBefore(roadmap, "## Recommended Validation Gates", "## What Should Start Next in Zigux");

    const section = try validationGatesSection(roadmap);
    try expectContains(section, "Every approved Zigux slice should declare and satisfy these gates.");
}

test "validation gate packet keeps all six named gates in order" {
    const roadmap = try readRoadmap(std.testing.allocator);
    defer std.testing.allocator.free(roadmap);

    const section = try validationGatesSection(roadmap);

    try expectBefore(section, "1. Build gate", "2. ABI gate");
    try expectBefore(section, "2. ABI gate", "3. Behavior gate");
    try expectBefore(section, "3. Behavior gate", "4. Performance gate");
    try expectBefore(section, "4. Performance gate", "5. Runtime gate");
    try expectBefore(section, "5. Runtime gate", "6. Rollback gate");
}

test "validation gate packet preserves concrete truthfulness criteria" {
    const roadmap = try readRoadmap(std.testing.allocator);
    defer std.testing.allocator.free(roadmap);

    const section = try validationGatesSection(roadmap);

    const required_lines = [_][]const u8{
        "- deterministic artifact generation where applicable",
        "- pinned toolchain version",
        "- reproducible host-side outputs",
        "- layout assertions",
        "- calling-convention checks",
        "- one blessed export surface",
        "- differential tests against current C behavior",
        "- fixture or known-vector parity",
        "- perf thresholds for algorithmic helpers and driver-sensitive paths",
        "- load/unload behavior for runtime modules",
        "- teardown parity",
        "- queueing and failure-path coverage for drivers",
        "- named owner",
        "- explicit fallback to current C implementation",
        "- clear disable path when regressions appear",
    };

    for (required_lines) |line| {
        try expectContains(section, line);
    }
}
