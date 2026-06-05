const std = @import("std");
const testing = std.testing;

const roadmap = @embedFile("ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md");

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

fn riskSection() ![]const u8 {
    const start = std.mem.indexOf(u8, roadmap, "## Risk Register That Must Drive Prioritization") orelse return error.MissingRiskRegisterStart;
    const end = std.mem.indexOfPos(u8, roadmap, start, "## First Commit and Push Sequence for Zigux") orelse return error.MissingRiskRegisterEnd;
    return roadmap[start..end];
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectOrdered(haystack: []const u8, before: []const u8, after: []const u8) !void {
    const before_index = std.mem.indexOf(u8, haystack, before) orelse return error.MissingBeforeMarker;
    const after_index = std.mem.indexOf(u8, haystack, after) orelse return error.MissingAfterMarker;
    try testing.expect(before_index < after_index);
}

test "risk register remains between ownership and commit sequence" {
    try expectOrdered(roadmap, "## Workstreams and Ownership Model", "## Risk Register That Must Drive Prioritization");
    try expectOrdered(roadmap, "## Risk Register That Must Drive Prioritization", "## First Commit and Push Sequence for Zigux");

    const section = try riskSection();
    try expectContains(section, "The highest-risk items from the bundle are the ones that must shape scope:");
    try expectContains(section, "The most important operational consequence is this:");
}

test "risk register preserves the roadmap risk roster and order" {
    const section = try riskSection();

    for (risks) |risk| {
        try expectContains(section, risk);
    }

    inline for (0..risks.len - 1) |index| {
        try expectOrdered(section, risks[index], risks[index + 1]);
    }
}

test "risk register keeps bounded readiness rule explicit" {
    const section = try riskSection();

    try expectOrdered(section, "The most important operational consequence is this:", "if a proposed Zigux task does not come with bounded scope, validation, rollback, and ownership");
    try expectContains(section, "if a proposed Zigux task does not come with bounded scope, validation, rollback, and ownership, it is not ready for the product repo");
}
