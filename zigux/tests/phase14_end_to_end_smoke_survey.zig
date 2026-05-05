const std = @import("std");

const Surface = struct {
    path: []const u8,
    required_marker: []const u8,
};

const Manifest = struct {
    lane_key: []const u8,
    phase: []const u8,
    packet_name: []const u8,
    focus: []const u8,
    rollback_owner: []const u8,
    commands: []const []const u8,
    surfaces: []const Surface,
    blocked_anchors: []const []const u8,
};

fn containsMarker(haystack: []const u8, needle: []const u8) bool {
    return std.mem.indexOf(u8, haystack, needle) != null;
}

test "phase14 shared smoke manifest records the bounded study-only packet" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const manifest_json = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase14_end_to_end_smoke_manifest.json",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(manifest_json);

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{});
    defer parsed.deinit();
    const manifest = parsed.value;

    try std.testing.expectEqualStrings("core-adjacent", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 14", manifest.phase);
    try std.testing.expectEqualStrings("phase14_shared_smoke_packet", manifest.packet_name);
    try std.testing.expectEqualStrings("study_only_shared_smoke_packet", manifest.focus);
    try std.testing.expectEqual(@as(usize, 6), manifest.commands.len);
    try std.testing.expectEqual(@as(usize, 19), manifest.surfaces.len);
    try std.testing.expectEqual(@as(usize, 4), manifest.blocked_anchors.len);
    try std.testing.expectEqualStrings("make -C zigux phase14-validate", manifest.commands[0]);
    try std.testing.expectEqualStrings("make -C zigux phase14-smoke", manifest.commands[1]);
    try std.testing.expectEqualStrings("make -C zigux phase14-test", manifest.commands[3]);
    try std.testing.expectEqualStrings("Documentation/zigux/README.md", manifest.surfaces[0].path);
    try std.testing.expectEqualStrings("Documentation/zigux/phase14-release-boundary-survey.md", manifest.surfaces[1].path);
    try std.testing.expectEqualStrings("scripts/zigux/README.md", manifest.surfaces[3].path);
    try std.testing.expectEqualStrings("scripts/zigux/validate-phase14.py", manifest.surfaces[4].path);
    try std.testing.expectEqualStrings("zigux/tests/phase14_build.zig", manifest.surfaces[8].path);
    try std.testing.expectEqualStrings("zigux/tests/phase14_workqueue_bridge_manifest.json", manifest.surfaces[11].path);
    try std.testing.expectEqualStrings("zigux/tests/phase14_skbuff_bridge_manifest.json", manifest.surfaces[12].path);
    try std.testing.expectEqualStrings("zigux/tests/phase14_ring_buffer_manifest.json", manifest.surfaces[15].path);
    try std.testing.expectEqualStrings("zigux/tests/phase14_rcu_tree_manifest.json", manifest.surfaces[16].path);
    try std.testing.expectEqualStrings("kernel/workqueue_bridge.zig", manifest.surfaces[17].path);
    try std.testing.expectEqualStrings("net/core/skbuff_bridge.zig", manifest.surfaces[18].path);
    try std.testing.expectEqualStrings("kernel/workqueue.c", manifest.blocked_anchors[0]);
    try std.testing.expectEqualStrings("net/core/skbuff.c", manifest.blocked_anchors[3]);
    try std.testing.expect(containsMarker(manifest.rollback_owner, "freeze-map anchors"));
}

test "phase14 shared smoke survey confirms the current packet surfaces" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const manifest_json = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase14_end_to_end_smoke_manifest.json",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(manifest_json);

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{});
    defer parsed.deinit();
    const manifest = parsed.value;

    for (manifest.surfaces) |surface| {
        const text = try std.Io.Dir.cwd().readFileAlloc(
            io_instance.io(),
            surface.path,
            std.testing.allocator,
            .limited(256 * 1024),
        );
        defer std.testing.allocator.free(text);
        try std.testing.expect(containsMarker(text, surface.required_marker));
    }

    const makefile_text = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/Makefile",
        std.testing.allocator,
        .limited(64 * 1024),
    );
    defer std.testing.allocator.free(makefile_text);
    try std.testing.expect(containsMarker(makefile_text, "phase14-smoke:"));
    try std.testing.expect(containsMarker(makefile_text, "phase14-test:"));
    try std.testing.expect(containsMarker(makefile_text, "phase14: phase14-validate phase14-smoke phase14-test"));
    try std.testing.expect(containsMarker(makefile_text, "zigux/tests/phase14_build.zig"));
}
