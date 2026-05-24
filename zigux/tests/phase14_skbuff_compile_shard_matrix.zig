const std = @import("std");

const AnchorPacket = struct {
    lane_key: []const u8,
    anchor: []const u8,
    surveyed_commit: []const u8,
    manifest_path: []const u8,
    survey_note_path: []const u8,
    ready_next_gap: []const u8,
    blocked_gap: []const u8,
};

const SharedCompileShard = struct {
    label: []const u8,
    root_source: []const u8,
    coverage: []const u8,
};

const SharedSmokeManifest = struct {
    shared_smoke_surfaces: []const []const u8,
    anchor_packets: []const AnchorPacket,
    smoke_shard_commands: []const []const u8,
    compile_shards: []const SharedCompileShard,
};

fn containsString(items: []const []const u8, needle: []const u8) bool {
    for (items) |item| {
        if (std.mem.eql(u8, item, needle)) return true;
    }
    return false;
}

fn findAnchorPacket(items: []const AnchorPacket, lane_key: []const u8) ?AnchorPacket {
    for (items) |item| {
        if (std.mem.eql(u8, item.lane_key, lane_key)) return item;
    }
    return null;
}

fn hasCompileShard(items: []const SharedCompileShard, label: []const u8, root_source: []const u8, coverage: []const u8) bool {
    for (items) |item| {
        if (!std.mem.eql(u8, item.label, label)) continue;
        if (!std.mem.eql(u8, item.root_source, root_source)) continue;
        if (!std.mem.eql(u8, item.coverage, coverage)) continue;
        return true;
    }
    return false;
}

test "phase14 skbuff shared smoke manifest keeps the compile shard matrix row explicit" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const manifest_json = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase14_end_to_end_smoke_manifest.json",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(manifest_json);

    const parsed = try std.json.parseFromSlice(SharedSmokeManifest, std.testing.allocator, manifest_json, .{
        .ignore_unknown_fields = true,
    });
    defer parsed.deinit();
    const manifest = parsed.value;

    try std.testing.expect(containsString(manifest.shared_smoke_surfaces, "zigux/tests/phase14_build.zig"));
    try std.testing.expect(containsString(manifest.shared_smoke_surfaces, "Documentation/zigux/phase14-skbuff-bridge-survey.md"));
    try std.testing.expectEqual(@as(usize, 1), manifest.smoke_shard_commands.len);
    try std.testing.expectEqualStrings(
        "zig build phase14-smoke --build-file zigux/tests/phase14_build.zig",
        manifest.smoke_shard_commands[0],
    );
    try std.testing.expect(hasCompileShard(
        manifest.compile_shards,
        "phase14-skbuff-bridge-tests",
        "phase14_skbuff_bridge.zig",
        "full_bundle_only",
    ));

    const packet = findAnchorPacket(manifest.anchor_packets, "P14-L11") orelse return error.MissingSkbuffAnchorPacket;
    try std.testing.expectEqualStrings("net/core/skbuff.c", packet.anchor);
    try std.testing.expectEqualStrings("zigux/tests/phase14_skbuff_bridge_manifest.json", packet.manifest_path);
    try std.testing.expectEqualStrings("Documentation/zigux/phase14-skbuff-bridge-survey.md", packet.survey_note_path);
    try std.testing.expectEqualStrings("phase14-skbuff-live-ownership-blocker", packet.blocked_gap);
}

test "phase14 skbuff build shard keeps the bridge-local route wired" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const build_file = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase14_build.zig",
        std.testing.allocator,
        .limited(16 * 1024),
    );
    defer std.testing.allocator.free(build_file);

    try std.testing.expect(std.mem.indexOf(u8, build_file, "../../net/core/skbuff_bridge.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, build_file, "phase14_skbuff_bridge.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, build_file, "phase14-skbuff-bridge-tests") != null);
    try std.testing.expect(std.mem.indexOf(u8, build_file, "phase14_skbuff_bridge_module.addImport(\"skbuff_bridge\", skbuff_bridge_module);") != null);
    try std.testing.expect(std.mem.indexOf(u8, build_file, "test_step.dependOn(&run_phase14_skbuff_bridge_tests.step);") != null);
}

test "phase14 skbuff survey note keeps the compile-route wording explicit" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const note = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase14-skbuff-bridge-survey.md",
        std.testing.allocator,
        .limited(16 * 1024),
    );
    defer std.testing.allocator.free(note);

    try std.testing.expect(std.mem.indexOf(u8, note, "zigux/tests/phase14_build.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, note, "../../net/core/skbuff_bridge.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, note, "phase14_skbuff_bridge.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, note, "dedicated Phase 14 build shard") != null);
    try std.testing.expect(std.mem.indexOf(u8, note, "live skbuff-local review route") != null);
}

test "phase14 skbuff bridge packet keeps the note and manifest markers explicit" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const bridge_test = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase14_skbuff_bridge.zig",
        std.testing.allocator,
        .limited(16 * 1024),
    );
    defer std.testing.allocator.free(bridge_test);

    try std.testing.expect(std.mem.indexOf(u8, bridge_test, "phase14_skbuff_bridge_manifest.json") != null);
    try std.testing.expect(std.mem.indexOf(u8, bridge_test, "Documentation/zigux/phase14-skbuff-bridge-survey.md") != null);
}
