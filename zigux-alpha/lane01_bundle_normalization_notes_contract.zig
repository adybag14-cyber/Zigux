const std = @import("std");

const roadmap = @embedFile("ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md");

const normalized_count_markers = [_][]const u8{
    "- phases: `15`",
    "- phase targets: `60`",
    "- parity-focus rows: `12`",
    "- workstreams: `15`",
    "- risks: `12`",
    "- structure rules: `18`",
    "- source anchors: `61`",
};

const stale_summary_markers = [_][]const u8{
    "- phases: `17`",
    "- file-level target rows: `62`",
    "- workstreams: `17`",
    "- risks: `14`",
};

test "roadmap normalization notes preserve live structured counts" {
    try expectContains("## Bundle Normalization Notes");
    try expectContains("The workbook and CSV corpus are directionally aligned");
    try expectContains("Normalized counts from the extracted structured files:");

    for (normalized_count_markers) |marker| {
        try expectContains(marker);
    }
}

test "roadmap normalization notes keep stale executive summary warning explicit" {
    try expectContains("Stale executive-summary metadata in the workbook that should not drive planning:");

    for (stale_summary_markers) |marker| {
        try expectContains(marker);
    }

    try expectContains("For execution, use the structured CSV/workbook tables themselves, not the executive-summary metrics block.");
}

test "roadmap normalization packet stays between input review and licensing policy" {
    try expectOrder("## Inputs Reviewed", "## Bundle Normalization Notes");
    try expectOrder("## Bundle Normalization Notes", "## Licensing and Reuse Policy");
    try expectOrder("I also checked the current public repo state at:", "## Bundle Normalization Notes");
    try expectOrder("For execution, use the structured CSV/workbook tables themselves", "## Licensing and Reuse Policy");
}

fn expectContains(needle: []const u8) !void {
    try std.testing.expect(std.mem.containsAtLeast(u8, roadmap, 1, needle));
}

fn expectOrder(before: []const u8, after: []const u8) !void {
    const before_index = std.mem.indexOf(u8, roadmap, before) orelse return error.MissingBeforeMarker;
    const after_index = std.mem.indexOf(u8, roadmap, after) orelse return error.MissingAfterMarker;
    try std.testing.expect(before_index < after_index);
}
