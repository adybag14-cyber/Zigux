const std = @import("std");

fn readRepoFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(std.testing.io, path, allocator, .limited(512 * 1024));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectBefore(haystack: []const u8, first: []const u8, second: []const u8) !void {
    const first_index = std.mem.indexOf(u8, haystack, first) orelse return error.MissingFirstMarker;
    const second_index = std.mem.indexOf(u8, haystack, second) orelse return error.MissingSecondMarker;
    try std.testing.expect(first_index < second_index);
}

test "Lane 01 roadmap keeps bootstrap bundle input list explicit" {
    const allocator = std.testing.allocator;
    const roadmap = try readRepoFile(allocator, "zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md");
    defer allocator.free(roadmap);

    try expectContains(roadmap, "## Inputs Reviewed");
    try expectContains(roadmap, "The roadmap is based on all bundle artifacts in `zigux_bundle_v2.zip`:");
    try expectContains(roadmap, "- `zigux_bundle_review_v2.csv`");
    try expectContains(roadmap, "- `zigux_full_parity_focus_v2.csv`");
    try expectContains(roadmap, "- `zigux_linux_to_zigux_map_v2.csv`");
    try expectContains(roadmap, "- `zigux_master_phases_v2.csv`");
    try expectContains(roadmap, "- `zigux_phase_targets_v2.csv`");
    try expectContains(roadmap, "- `zigux_pm_roadmap_v2.xlsx`");
    try expectContains(roadmap, "- `zigux_risk_register_v2.csv`");
    try expectContains(roadmap, "- `zigux_sources_v2.csv`");
    try expectContains(roadmap, "- `zigux_structure_v2.csv`");
    try expectContains(roadmap, "- `zigux_workstreams_v2.csv`");
}

test "Lane 01 roadmap records live Zigux repo grounding after bundle inputs" {
    const allocator = std.testing.allocator;
    const roadmap = try readRepoFile(allocator, "zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md");
    defer allocator.free(roadmap);

    try expectContains(roadmap, "I also checked the current public repo state at:");
    try expectContains(roadmap, "- <https://github.com/adybag14-cyber/Zigux>");
    try expectBefore(roadmap, "- `zigux_workstreams_v2.csv`", "I also checked the current public repo state at:");
    try expectBefore(roadmap, "I also checked the current public repo state at:", "## Bundle Normalization Notes");
}

test "Lane 01 roadmap keeps inputs packet in bootstrap context order" {
    const allocator = std.testing.allocator;
    const roadmap = try readRepoFile(allocator, "zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md");
    defer allocator.free(roadmap);

    try expectBefore(roadmap, "## Purpose", "## Bootstrap Status Note");
    try expectBefore(roadmap, "## Bootstrap Status Note", "## Inputs Reviewed");
    try expectBefore(roadmap, "## Inputs Reviewed", "## Bundle Normalization Notes");
    try expectBefore(roadmap, "## Bundle Normalization Notes", "## Licensing and Reuse Policy");
}
