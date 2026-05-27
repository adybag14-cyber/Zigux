const std = @import("std");

fn segmentWindow(manifest_json: []const u8, slug: []const u8) ![]const u8 {
    const slug_index = std.mem.indexOf(u8, manifest_json, slug) orelse return error.MissingManifestSegment;
    const window_end = @min(manifest_json.len, slug_index + 1400);
    return manifest_json[slug_index..window_end];
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn readWorkspaceFile(allocator: std.mem.Allocator, path: []const u8, limit: usize) ![]u8 {
    var io_instance: std.Io.Threaded = .init(allocator, .{});
    defer io_instance.deinit();

    return std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        path,
        allocator,
        .limited(limit),
    );
}

test "phase 8 file-path-handle boundary guard keeps landed helper slices distinct from the deferred bridge" {
    const manifest_json = try readWorkspaceFile(
        std.testing.allocator,
        "tools/lib/bpf/zigux_segments/manifest.json",
        64 * 1024,
    );
    defer std.testing.allocator.free(manifest_json);
    const bridge_test_source = try readWorkspaceFile(
        std.testing.allocator,
        "zigux/tests/phase8_file_path_handle_bridge.zig",
        64 * 1024,
    );
    defer std.testing.allocator.free(bridge_test_source);
    const bridge_slice = try readWorkspaceFile(
        std.testing.allocator,
        "Documentation/zigux/phase8-file-path-handle-bridge-slice.md",
        32 * 1024,
    );
    defer std.testing.allocator.free(bridge_slice);
    const boundary_survey = try readWorkspaceFile(
        std.testing.allocator,
        "Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md",
        32 * 1024,
    );
    defer std.testing.allocator.free(boundary_survey);
    const shared_build = try readWorkspaceFile(
        std.testing.allocator,
        "zigux/tests/phase8_build.zig",
        32 * 1024,
    );
    defer std.testing.allocator.free(shared_build);

    const fdinfo_window = try segmentWindow(manifest_json, "\"slug\": \"fdinfo-map-info-helpers\"");
    try expectContains(fdinfo_window, "\"status\": \"starter_landed\"");
    try expectContains(fdinfo_window, "bounded procfs path construction");
    try expectContains(fdinfo_window, "fdinfo text parsing");

    const reuse_window = try segmentWindow(manifest_json, "\"slug\": \"map-reuse-compatibility\"");
    try expectContains(reuse_window, "\"status\": \"starter_landed\"");
    try expectContains(reuse_window, "reused-map-name chooser");
    try expectContains(reuse_window, "compatibility comparison");

    const footholds_window = try segmentWindow(manifest_json, "\"slug\": \"fdinfo-path-and-reuse-name-footholds\"");
    try expectContains(footholds_window, "\"status\": \"starter_landed\"");
    try expectContains(footholds_window, "side-effect-free pathname shaping");
    try expectContains(footholds_window, "bounded reused-map name retention");
    try expectContains(footholds_window, "direct procfs reads");
    try expectContains(footholds_window, "live bpffs opens");
    try expectContains(footholds_window, "token materialization");
    try expectContains(footholds_window, "`bpf_obj_get()` reopen flow");
    try expectContains(footholds_window, "descriptor ownership side effects");

    const bridge_window = try segmentWindow(manifest_json, "\"slug\": \"file-path-and-handle-bridge\"");
    try expectContains(bridge_window, "\"status\": \"deferred_high_risk\"");
    try expectContains(bridge_window, "\"kind\": \"resource_boundary\"");
    try expectContains(bridge_window, "procfs reads");
    try expectContains(bridge_window, "bpffs opens");
    try expectContains(bridge_window, "token creation");
    try expectContains(bridge_window, "bpf_obj_get() reopen flow");
    try expectContains(bridge_window, "fd ownership semantics");

    try expectContains(bridge_test_source, "buildProcFdinfoPath");
    try expectContains(bridge_test_source, "buildCurrentProcessFdinfoPath");
    try expectContains(bridge_test_source, "parseFdinfoLine");
    try expectContains(bridge_test_source, "applyFdinfoMapInfoLine");
    try expectContains(bridge_test_source, "parseFdinfoMapInfo");
    try expectContains(bridge_test_source, "summarizeFdinfoMapInfo");
    try expectContains(bridge_test_source, "mapReuseObservationFromFdinfo");
    try expectContains(bridge_test_source, "summarizeMapReuseCompatibility");
    try expectContains(bridge_test_source, "isMapReuseCompatible");
    try expectContains(bridge_test_source, "resolveReusePinnedMapAttempt");
    try expectContains(bridge_test_source, "planTokenPreparation");

    try expectContains(bridge_slice, "scope: helper-local pathname shaping, fdinfo map-info parsing, reused-map compatibility planning, and deferred bridge-boundary truthfulness only");
    try expectContains(bridge_slice, "buildCurrentProcessFdinfoPath()");
    try expectContains(bridge_slice, "applyFdinfoMapInfoLine()");
    try expectContains(bridge_slice, "parseFdinfoMapInfo()");
    try expectContains(bridge_slice, "summarizeFdinfoMapInfo()");
    try expectContains(bridge_slice, "summarizeMapReuseCompatibility()");
    try expectContains(bridge_slice, "isMapReuseCompatible()");
    try expectContains(bridge_slice, "planning-only `resolveReusePinnedMapAttempt()` gating");
    try expectContains(bridge_slice, "planning-only `planTokenPreparation()` gating");
    try expectContains(bridge_slice, "no live bpffs opens");
    try expectContains(bridge_slice, "no token materialization");
    try expectContains(bridge_slice, "no descriptor replacement, transfer, or close ownership semantics");

    try expectContains(boundary_survey, "Current `master` still keeps the mixed-source bridge packet reviewable");
    try expectContains(boundary_survey, "`tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig`");
    try expectContains(boundary_survey, "`zigux/tests/phase8_file_path_handle_bridge.zig`");
    try expectContains(boundary_survey, "`zigux/tests/phase8_file_path_handle_boundary_guard.zig`");
    try expectContains(boundary_survey, "`zigux/tests/phase8_file_path_handle_bridge_manifest_sync.zig`");
    try expectContains(boundary_survey, "`scripts/zigux/validate-phase8.py`");
    try expectContains(boundary_survey, "`make -C zigux phase8-file-path-handle-bridge-test`");
    try expectContains(boundary_survey, "`make -C zigux phase8`");
    try expectContains(boundary_survey, "buildCurrentProcessFdinfoPath()");
    try expectContains(boundary_survey, "applyFdinfoMapInfoLine()");
    try expectContains(boundary_survey, "parseFdinfoMapInfo()");
    try expectContains(boundary_survey, "summarizeFdinfoMapInfo()");
    try expectContains(boundary_survey, "summarizeMapReuseCompatibility()");
    try expectContains(boundary_survey, "isMapReuseCompatible()");
    try expectContains(boundary_survey, "resolveReusePinnedMapAttempt()");
    try expectContains(boundary_survey, "planTokenPreparation()");
    try expectContains(boundary_survey, "The landed `fdinfo-path-and-reuse-name-footholds` slice therefore now mirrors the manifest rationale exactly: This materializes the shared bridge destination with side-effect-free pathname shaping and bounded reused-map name retention while leaving direct procfs reads, live bpffs opens, token materialization, `bpf_obj_get()` reopen flow, and descriptor ownership side effects to the deferred file-path-and-handle bridge boundary.");
    try expectContains(boundary_survey, "live procfs reads, live bpffs opens, token materialization, `bpf_obj_get()` reopen flow, descriptor replacement, or broader fd ownership behavior");

    try expectContains(shared_build, "phase8_file_path_handle_boundary_guard.zig");
    try expectContains(shared_build, "phase8-file-path-handle-boundary-guard-tests");
    try expectContains(shared_build, "phase8_file_path_handle_bridge_manifest_sync.zig");
    try expectContains(shared_build, "phase8-file-path-handle-bridge-manifest-sync-tests");
}
