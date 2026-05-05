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
    try std.testing.expectEqual(@as(usize, 5), manifest.commands.len);
    try std.testing.expectEqual(@as(usize, 14), manifest.surfaces.len);
    try std.testing.expectEqual(@as(usize, 4), manifest.blocked_anchors.len);
    try std.testing.expectEqualStrings("make -C zigux phase14-smoke", manifest.commands[0]);
    try std.testing.expectEqualStrings("make -C zigux phase14-test", manifest.commands[2]);
    try std.testing.expectEqualStrings("make -C zigux phase14", manifest.commands[4]);
    try std.testing.expectEqualStrings("Documentation/zigux/README.md", manifest.surfaces[0].path);
    try std.testing.expectEqualStrings("zigux/tests/phase14_build.zig", manifest.surfaces[6].path);
    try std.testing.expectEqualStrings("zigux/tests/phase14_end_to_end_smoke_survey.zig", manifest.surfaces[11].path);
    try std.testing.expectEqualStrings("zigux/Makefile", manifest.surfaces[13].path);
    try std.testing.expectEqualStrings("kernel/workqueue.c", manifest.blocked_anchors[0]);
    try std.testing.expectEqualStrings("net/core/skbuff.c", manifest.blocked_anchors[3]);
    try std.testing.expect(containsMarker(manifest.rollback_owner, "freeze-map anchors"));
}

test "phase14 shared smoke survey confirms the current packet surfaces" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const survey_text = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase14-end-to-end-smoke-survey.md",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(survey_text);

    const makefile_text = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/Makefile",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(makefile_text);

    const build_text = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase14_build.zig",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(build_text);

    try std.testing.expect(containsMarker(survey_text, "PHASE14_VALIDATE_ENTRYPOINT=absent_on_master"));
    try std.testing.expect(containsMarker(survey_text, "PHASE14_COMPILE_ARTIFACT_COUNT=5"));
    try std.testing.expect(containsMarker(survey_text, "PHASE14_FOCUSED_SHARD_COUNT=1"));
    try std.testing.expect(containsMarker(survey_text, "make -C zigux phase14-smoke"));
    try std.testing.expect(containsMarker(survey_text, "make -C zigux phase14-test"));
    try std.testing.expect(containsMarker(survey_text, "make -C zigux phase14"));
    try std.testing.expect(!containsMarker(survey_text, "make -C zigux phase14-validate"));

    try std.testing.expect(containsMarker(makefile_text, "phase14-smoke:"));
    try std.testing.expect(containsMarker(makefile_text, "phase14-test:"));
    try std.testing.expect(containsMarker(makefile_text, "phase14: phase14-smoke phase14-test"));
    try std.testing.expect(!containsMarker(makefile_text, "phase14-validate:"));

    try std.testing.expect(containsMarker(build_text, "b.step(\"phase14-smoke\", \"Run the focused Phase 14 end-to-end smoke survey\")"));
    try std.testing.expect(containsMarker(build_text, "test_step.dependOn(&run_phase14_end_to_end_smoke_tests.step);"));
}
