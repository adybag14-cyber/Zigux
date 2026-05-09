const std = @import("std");

const Surface = struct {
    path: []const u8,
    required_marker: []const u8,
};

const CompileArtifact = struct {
    label: []const u8,
    root_source: []const u8,
    coverage: []const u8,
};

const Manifest = struct {
    lane_key: []const u8,
    phase: []const u8,
    packet_name: []const u8,
    focus: []const u8,
    rollback_owner: []const u8,
    commands: []const []const u8,
    compile_shards: []const CompileArtifact,
    surfaces: []const Surface,
    blocked_anchors: []const []const u8,
};

const TraceabilityExpectation = struct {
    section_heading: []const u8,
    survey_note_path: []const u8,
    lane_key_marker: []const u8,
    ready_next_gap_marker: []const u8,
    retained_boundary_marker: []const u8,
    blocked_gap_marker: []const u8,
};

const expected_compile_artifacts = [_]CompileArtifact{
    .{ .label = "phase14-workqueue-bridge-tests", .root_source = "phase14_workqueue_bridge.zig", .coverage = "full_bundle_only" },
    .{ .label = "phase14-workqueue-reviewability-tests", .root_source = "phase14_workqueue_reviewability.zig", .coverage = "full_bundle_only" },
    .{ .label = "phase14-skbuff-bridge-tests", .root_source = "phase14_skbuff_bridge.zig", .coverage = "full_bundle_only" },
    .{ .label = "phase14-ring-buffer-survey-tests", .root_source = "phase14_ring_buffer_survey.zig", .coverage = "full_bundle_only" },
    .{ .label = "phase14-rcu-tree-survey-tests", .root_source = "phase14_rcu_tree_survey.zig", .coverage = "full_bundle_only" },
    .{ .label = "phase14-end-to-end-smoke-tests", .root_source = "phase14_end_to_end_smoke_survey.zig", .coverage = "focused_and_full_bundle" },
};

const expected_traceability_markers = [_]TraceabilityExpectation{
    .{ .section_heading = "### Workqueue", .survey_note_path = "Documentation/zigux/phase14-workqueue-bridge-survey.md", .lane_key_marker = "- lane key: `P14-L02`", .ready_next_gap_marker = "- ready-next gap: none currently recorded", .retained_boundary_marker = "live worker-pool execution", .blocked_gap_marker = "`phase14-workqueue-live-execution-blocker`" },
    .{ .section_heading = "### Ring buffer", .survey_note_path = "Documentation/zigux/phase14-ring-buffer-survey.md", .lane_key_marker = "- lane key: `P14-L08`", .ready_next_gap_marker = "- ready-next gap: `phase14-ring-buffer-read-page-copy-followup`", .retained_boundary_marker = "exported-page forced-copy decisions", .blocked_gap_marker = "`phase14-ring-buffer-zig-port-blocker`" },
    .{ .section_heading = "### Skbuff", .survey_note_path = "Documentation/zigux/phase14-skbuff-bridge-survey.md", .lane_key_marker = "- lane key: `P14-L10`", .ready_next_gap_marker = "- ready-next gap: none currently recorded", .retained_boundary_marker = "live skb lifetime", .blocked_gap_marker = "`phase14-skbuff-live-ownership-blocker`" },
    .{ .section_heading = "### RCU tree", .survey_note_path = "Documentation/zigux/phase14-rcu-tree-survey.md", .lane_key_marker = "- lane key: `P14-L13`", .ready_next_gap_marker = "- ready-next gap: none currently recorded", .retained_boundary_marker = "grace-period sequence publication", .blocked_gap_marker = "`phase14-rcu-tree-bridge-blocker`" },
};

fn containsMarker(haystack: []const u8, needle: []const u8) bool {
    return std.mem.indexOf(u8, haystack, needle) != null;
}

fn hasSurfacePath(surfaces: []const Surface, expected_path: []const u8) bool {
    for (surfaces) |surface| {
        if (std.mem.eql(u8, surface.path, expected_path)) return true;
    }
    return false;
}

fn countSurfacesWithPrefix(surfaces: []const Surface, prefix: []const u8) usize {
    var count: usize = 0;
    for (surfaces) |surface| {
        if (std.mem.startsWith(u8, surface.path, prefix)) count += 1;
    }
    return count;
}

fn countExactSurfacePath(surfaces: []const Surface, expected_path: []const u8) usize {
    var count: usize = 0;
    for (surfaces) |surface| {
        if (std.mem.eql(u8, surface.path, expected_path)) count += 1;
    }
    return count;
}

fn countBridgeRootSurfaces(surfaces: []const Surface) usize {
    return countExactSurfacePath(surfaces, "kernel/workqueue_bridge.zig") +
        countExactSurfacePath(surfaces, "net/core/skbuff_bridge.zig") +
        countExactSurfacePath(surfaces, "kernel/rcu/tree_bridge.zig");
}

test "phase14 shared smoke manifest records the bounded study-only packet" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const manifest_json = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase14_end_to_end_smoke_manifest.json",
        std.testing.allocator,
        .limited(48 * 1024),
    );
    defer std.testing.allocator.free(manifest_json);

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{});
    defer parsed.deinit();
    const manifest = parsed.value;

    try std.testing.expectEqualStrings("P14-L07", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 14", manifest.phase);
    try std.testing.expectEqualStrings("phase14_shared_smoke_packet", manifest.packet_name);
    try std.testing.expectEqualStrings("study_only_shared_smoke_packet", manifest.focus);
    try std.testing.expectEqual(@as(usize, 6), manifest.commands.len);
    try std.testing.expectEqual(@as(usize, 6), manifest.compile_shards.len);
    try std.testing.expectEqual(@as(usize, 29), manifest.surfaces.len);
    try std.testing.expectEqual(@as(usize, 6), countSurfacesWithPrefix(manifest.surfaces, "Documentation/zigux/"));
    try std.testing.expectEqual(@as(usize, 5), countSurfacesWithPrefix(manifest.surfaces, "scripts/zigux/"));
    try std.testing.expectEqual(@as(usize, 13), countSurfacesWithPrefix(manifest.surfaces, "zigux/tests/"));
    try std.testing.expectEqual(@as(usize, 3), countBridgeRootSurfaces(manifest.surfaces));
    try std.testing.expectEqual(@as(usize, 1), countExactSurfacePath(manifest.surfaces, "zigux/Makefile"));
    try std.testing.expectEqual(@as(usize, 1), countSurfacesWithPrefix(manifest.surfaces, ".github/workflows/"));
    try std.testing.expectEqual(@as(usize, 4), manifest.blocked_anchors.len);
    try std.testing.expectEqualStrings("make -C zigux phase14-validate", manifest.commands[0]);
    try std.testing.expectEqualStrings("make -C zigux phase14-smoke", manifest.commands[1]);
    try std.testing.expectEqualStrings("make -C zigux phase14-test", manifest.commands[3]);
    try std.testing.expect(hasSurfacePath(manifest.surfaces, "zigux/tests/phase14_workqueue_reviewability.zig"));
    try std.testing.expect(hasSurfacePath(manifest.surfaces, ".github/workflows/zigux-bootstrap.yml"));
    try std.testing.expectEqualStrings("kernel/workqueue.c", manifest.blocked_anchors[0]);
    try std.testing.expectEqualStrings("net/core/skbuff.c", manifest.blocked_anchors[3]);
    try std.testing.expect(containsMarker(manifest.rollback_owner, "freeze-map anchors"));

    for (expected_compile_artifacts, manifest.compile_shards) |expected, actual| {
        try std.testing.expectEqualStrings(expected.label, actual.label);
        try std.testing.expectEqualStrings(expected.root_source, actual.root_source);
        try std.testing.expectEqualStrings(expected.coverage, actual.coverage);
    }
}

test "phase14 shared smoke survey confirms the current packet surfaces" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const manifest_json = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase14_end_to_end_smoke_manifest.json",
        std.testing.allocator,
        .limited(48 * 1024),
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

    const smoke_note_text = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase14-end-to-end-smoke-survey.md",
        std.testing.allocator,
        .limited(128 * 1024),
    );
    defer std.testing.allocator.free(smoke_note_text);
    try std.testing.expect(containsMarker(smoke_note_text, "PHASE14_VALIDATE_SELF_TEST=python3 scripts/zigux/validate-phase14.py --self-test"));
    try std.testing.expect(containsMarker(smoke_note_text, "PHASE14_BUILD_ENTRYPOINT=zig build test --build-file zigux/tests/phase14_build.zig --summary all"));
    try std.testing.expect(containsMarker(smoke_note_text, "PHASE14_SHARED_SURFACE_COUNT=29"));
    try std.testing.expect(containsMarker(smoke_note_text, "PHASE14_DOC_SURFACE_COUNT=6"));
    try std.testing.expect(containsMarker(smoke_note_text, "PHASE14_SCRIPT_SURFACE_COUNT=5"));
    try std.testing.expect(containsMarker(smoke_note_text, "PHASE14_TEST_SURFACE_COUNT=13"));
    try std.testing.expect(containsMarker(smoke_note_text, "PHASE14_BRIDGE_ROOT_SURFACE_COUNT=3"));
    try std.testing.expect(containsMarker(smoke_note_text, "PHASE14_WORKFLOW_SURFACE_COUNT=1"));
    try std.testing.expect(containsMarker(smoke_note_text, "PHASE14_MAKEFILE_SURFACE_COUNT=1"));
    try std.testing.expect(containsMarker(smoke_note_text, "PHASE14_COMPILE_ARTIFACT_COUNT=6"));
    try std.testing.expect(containsMarker(smoke_note_text, "PHASE14_FOCUSED_SHARD_COUNT=1"));
    try std.testing.expect(containsMarker(smoke_note_text, "PHASE14_FULL_BUNDLE_ONLY_ARTIFACT_COUNT=5"));
    try std.testing.expect(containsMarker(smoke_note_text, "zigux/tests/phase14_workqueue_reviewability.zig"));
    try std.testing.expectEqual(@as(usize, 1), std.mem.count(u8, smoke_note_text, "coverage `focused_and_full_bundle`"));
    try std.testing.expectEqual(@as(usize, 5), std.mem.count(u8, smoke_note_text, "coverage `full_bundle_only`"));

    const build_text = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase14_build.zig",
        std.testing.allocator,
        .limited(64 * 1024),
    );
    defer std.testing.allocator.free(build_text);
    try std.testing.expectEqual(@as(usize, 6), std.mem.count(u8, build_text, "b.addTest(.{"));
    try std.testing.expectEqual(@as(usize, 6), std.mem.count(u8, build_text, "b.addRunArtifact("));
    try std.testing.expect(containsMarker(build_text, "smoke_step.dependOn(&run_phase14_end_to_end_smoke_tests.step);"));
    try std.testing.expect(!containsMarker(build_text, "smoke_step.dependOn(&run_phase14_workqueue_bridge_tests.step);"));
    try std.testing.expect(containsMarker(build_text, "test_step.dependOn(&run_phase14_workqueue_reviewability_tests.step);"));

    const workflow_text = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        ".github/workflows/zigux-bootstrap.yml",
        std.testing.allocator,
        .limited(256 * 1024),
    );
    defer std.testing.allocator.free(workflow_text);
    try std.testing.expectEqual(@as(usize, 1), std.mem.count(u8, workflow_text, "run: make -C zigux phase14-validate"));
    try std.testing.expectEqual(@as(usize, 1), std.mem.count(u8, workflow_text, "run: make -C zigux phase14-smoke"));
    try std.testing.expectEqual(@as(usize, 1), std.mem.count(u8, workflow_text, "run: make -C zigux phase14-test"));

    const makefile_text = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/Makefile",
        std.testing.allocator,
        .limited(64 * 1024),
    );
    defer std.testing.allocator.free(makefile_text);
    try std.testing.expect(containsMarker(makefile_text, "phase14-smoke:"));
    try std.testing.expect(containsMarker(makefile_text, "phase14-test:"));
    try std.testing.expect(containsMarker(makefile_text, "scripts/zigux/validate-phase14.py --self-test"));
    try std.testing.expect(containsMarker(makefile_text, "phase14: phase14-validate phase14-smoke phase14-test"));

    const validator_text = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "scripts/zigux/validate-phase14.py",
        std.testing.allocator,
        .limited(256 * 1024),
    );
    defer std.testing.allocator.free(validator_text);
    try std.testing.expect(containsMarker(validator_text, "phase14-workqueue-reviewability-tests"));
    try std.testing.expect(containsMarker(validator_text, "zigux/tests/phase14_workqueue_reviewability.zig"));
    try std.testing.expect(containsMarker(validator_text, "phase14 smoke note full-bundle-only compile count drifted from the current five-artifact packet"));

    const traceability_text = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase14-core-boundary-traceability.md",
        std.testing.allocator,
        .limited(64 * 1024),
    );
    defer std.testing.allocator.free(traceability_text);
    for (expected_traceability_markers) |expected| {
        try std.testing.expect(containsMarker(traceability_text, expected.section_heading));
        try std.testing.expect(containsMarker(traceability_text, expected.survey_note_path));
        try std.testing.expect(containsMarker(traceability_text, expected.lane_key_marker));
        try std.testing.expect(containsMarker(traceability_text, expected.ready_next_gap_marker));
        try std.testing.expect(containsMarker(traceability_text, expected.retained_boundary_marker));
        try std.testing.expect(containsMarker(traceability_text, expected.blocked_gap_marker));
    }
}
