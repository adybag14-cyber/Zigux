const std = @import("std");
const testing = std.testing;

const roadmap = @embedFile("ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md");

const gates = [_][]const u8{
    "1. Build gate",
    "- deterministic artifact generation where applicable",
    "- pinned toolchain version",
    "- reproducible host-side outputs",
    "2. ABI gate",
    "- layout assertions",
    "- calling-convention checks",
    "- one blessed export surface",
    "3. Behavior gate",
    "- differential tests against current C behavior",
    "- fixture or known-vector parity",
    "4. Performance gate",
    "- perf thresholds for algorithmic helpers and driver-sensitive paths",
    "5. Runtime gate",
    "- load/unload behavior for runtime modules",
    "- teardown parity",
    "- queueing and failure-path coverage for drivers",
    "6. Rollback gate",
    "- named owner",
    "- explicit fallback to current C implementation",
    "- clear disable path when regressions appear",
};

fn validationGateSection() ![]const u8 {
    const start = std.mem.indexOf(u8, roadmap, "## Recommended Validation Gates") orelse return error.MissingValidationGatesStart;
    const end = std.mem.indexOfPos(u8, roadmap, start, "## What Should Start Next in Zigux") orelse return error.MissingValidationGatesEnd;
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

test "recommended validation gates stay in the late bootstrap roadmap slot" {
    try expectOrdered(roadmap, "## First Commit and Push Sequence for Zigux", "## Recommended Validation Gates");
    try expectOrdered(roadmap, "## Recommended Validation Gates", "## What Should Start Next in Zigux");

    const section = try validationGateSection();
    try expectContains(section, "Every approved Zigux slice should declare and satisfy these gates.");
}

test "recommended validation gates preserve the six gate roster" {
    const section = try validationGateSection();

    for (gates) |gate| {
        try expectContains(section, gate);
    }

    inline for (0..gates.len - 1) |index| {
        try expectOrdered(section, gates[index], gates[index + 1]);
    }
}

test "recommended validation gates keep expansion rollback explicit" {
    const section = try validationGateSection();

    try expectOrdered(section, "1. Build gate", "6. Rollback gate");
    try expectOrdered(section, "- named owner", "- explicit fallback to current C implementation");
    try expectOrdered(section, "- explicit fallback to current C implementation", "- clear disable path when regressions appear");
}
