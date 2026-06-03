const std = @import("std");

const roadmap_path = "zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md";

const risks = [_][]const u8{
    "mirror-tree sprawl",
    "toolchain instability",
    "ABI and layout drift",
    "hidden runtime behavior",
    "memory-ordering mistakes",
    "insufficient validation before expansion",
    "reviewability collapse",
    "DMA and queueing regressions",
    "resource-lifetime mis-modeling",
    "overpromising full parity",
    "upstream process misalignment",
    "deep-core scope creep",
};

const readiness_markers = [_][]const u8{
    "if a proposed Zigux task does not come with bounded scope, validation, rollback, and ownership, it is not ready for the product repo",
    "bounded scope",
    "validation",
    "rollback",
    "ownership",
};

fn readRoadmap() ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(
        std.testing.io,
        roadmap_path,
        std.testing.allocator,
        .limited(128 * 1024),
    );
}

fn requireContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn sectionBetween(source: []const u8, start_marker: []const u8, end_marker: []const u8) ![]const u8 {
    const start = std.mem.indexOf(u8, source, start_marker) orelse return error.MissingStartMarker;
    const after_start = start + start_marker.len;
    const end_relative = std.mem.indexOf(u8, source[after_start..], end_marker) orelse return error.MissingEndMarker;
    return source[after_start .. after_start + end_relative];
}

test "Lane 01 roadmap keeps risk register as prioritization input" {
    const roadmap = try readRoadmap();
    defer std.testing.allocator.free(roadmap);

    const section = try sectionBetween(
        roadmap,
        "## Risk Register That Must Drive Prioritization",
        "## First Commit and Push Sequence for Zigux",
    );

    try requireContains(section, "The highest-risk items from the bundle are the ones that must shape scope:");

    var previous_index: usize = 0;
    for (risks, 0..) |risk, index| {
        const position = std.mem.indexOf(u8, section, risk) orelse return error.MissingRiskMarker;
        if (index > 0) {
            try std.testing.expect(position > previous_index);
        }
        previous_index = position;
    }

    try std.testing.expectEqual(@as(usize, 12), risks.len);
}

test "Lane 01 roadmap keeps readiness rule bounded and reviewable" {
    const roadmap = try readRoadmap();
    defer std.testing.allocator.free(roadmap);

    const section = try sectionBetween(
        roadmap,
        "## Risk Register That Must Drive Prioritization",
        "## First Commit and Push Sequence for Zigux",
    );

    try requireContains(section, "The most important operational consequence is this:");
    for (readiness_markers) |marker| {
        try requireContains(section, marker);
    }
}
