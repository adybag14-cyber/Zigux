const std = @import("std");

fn segmentWindow(manifest_json: []const u8, slug: []const u8) ![]const u8 {
    const slug_index = std.mem.indexOf(u8, manifest_json, slug) orelse return error.MissingManifestSegment;
    const window_end = @min(manifest_json.len, slug_index + 900);
    return manifest_json[slug_index..window_end];
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

test "phase 8 file-path-handle boundary guard keeps landed helper slices distinct from the deferred bridge" {
    const manifest_json = @embedFile("../../tools/lib/bpf/zigux_segments/manifest.json");
    const bridge_test_source = @embedFile("phase8_file_path_handle_bridge.zig");

    const fdinfo_window = try segmentWindow(manifest_json, "\"slug\": \"fdinfo-map-info-helpers\"");
    try expectContains(fdinfo_window, "\"status\": \"starter_landed\"");

    const reuse_window = try segmentWindow(manifest_json, "\"slug\": \"map-reuse-compatibility\"");
    try expectContains(reuse_window, "\"status\": \"starter_landed\"");

    const bridge_window = try segmentWindow(manifest_json, "\"slug\": \"file-path-and-handle-bridge\"");
    try expectContains(bridge_window, "\"status\": \"deferred_high_risk\"");
    try expectContains(bridge_window, "\"kind\": \"resource_boundary\"");
    try expectContains(bridge_window, "real bpffs path opens");
    try expectContains(bridge_window, "token creation");
    try expectContains(bridge_window, "pinned-object reopen flows");
    try expectContains(bridge_window, "fd ownership");

    try expectContains(bridge_test_source, "planTokenPreparation");
    try expectContains(bridge_test_source, "classifyTokenPreparationFailure");
    try expectContains(bridge_test_source, "parseMapInfoFromFdinfo");
    try expectContains(bridge_test_source, "chooseReusedMapName");
    try expectContains(bridge_test_source, "isMapReuseCompatible");
}
