const std = @import("std");

fn segmentWindow(manifest_json: []const u8, slug: []const u8) ![]const u8 {
    const slug_index = std.mem.indexOf(u8, manifest_json, slug) orelse return error.MissingManifestSegment;
    const window_end = @min(manifest_json.len, slug_index + 1400);
    return manifest_json[slug_index..window_end];
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

test "phase 8 file-path-handle boundary guard keeps landed helper slices distinct from the deferred bridge" {
    const manifest_json = @embedFile("../../tools/lib/bpf/zigux_segments/manifest.json");
    const bridge_test_source = @embedFile("phase8_file_path_handle_bridge.zig");
    const bridge_slice = @embedFile("../../Documentation/zigux/phase8-file-path-handle-bridge-slice.md");
    const boundary_survey = @embedFile("../../Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md");
    const shared_build = @embedFile("phase8_build.zig");

    const fdinfo_window = try segmentWindow(manifest_json, "\"slug\": \"fdinfo-map-info-helpers\"");
    try expectContains(fdinfo_window, "\"status\": \"starter_landed\"");
    try expectContains(fdinfo_window, "bounded procfs path construction");
    try expectContains(fdinfo_window, "fdinfo text parsing");

    const reuse_window = try segmentWindow(manifest_json, "\"slug\": \"map-reuse-compatibility\"");
    try expectContains(reuse_window, "\"status\": \"starter_landed\"");
    try expectContains(reuse_window, "reused-map-name chooser");
    try expectContains(reuse_window, "compatibility comparison");

    const bridge_window = try segmentWindow(manifest_json, "\"slug\": \"file-path-and-handle-bridge\"");
    try expectContains(bridge_window, "\"status\": \"deferred_high_risk\"");
    try expectContains(bridge_window, "\"kind\": \"resource_boundary\"");
    try expectContains(bridge_window, "procfs reads");
    try expectContains(bridge_window, "bpffs opens");
    try expectContains(bridge_window, "token creation");
    try expectContains(bridge_window, "bpf_obj_get() reopen flow");
    try expectContains(bridge_window, "fd ownership semantics");

    try expectContains(bridge_test_source, "buildProcFdinfoPath");
    try expectContains(bridge_test_source, "parseFdinfoMapInfo");
    try expectContains(bridge_test_source, "applyFdinfoMapInfoLine");
    try expectContains(bridge_test_source, "mapReuseObservationFromFdinfo");
    try expectContains(bridge_test_source, "resolveReusedMapName");
    try expectContains(bridge_test_source, "isMapReuseCompatible");
    try expectContains(bridge_test_source, "resolveReusePinnedMapAttempt");
    try expectContains(bridge_test_source, "planTokenPreparation");

    try expectContains(bridge_slice, "scope: helper-local fdinfo parsing, reuse-planning, and deferred bridge-boundary truthfulness only");
    try expectContains(bridge_slice, "planning-only `resolveReusePinnedMapAttempt()` gating");
    try expectContains(bridge_slice, "planning-only `planTokenPreparation()` gating");
    try expectContains(bridge_slice, "no direct procfs reads");
    try expectContains(bridge_slice, "no live bpffs opens");
    try expectContains(bridge_slice, "no `bpf_obj_get()` reopen flow");
    try expectContains(bridge_slice, "no token materialization");
    try expectContains(bridge_slice, "no descriptor replacement, transfer, or close ownership semantics");
    try expectContains(bridge_slice, "`scripts/zigux/validate-phase8.py`");
    try expectContains(bridge_slice, "`make -C zigux phase8-file-path-handle-bridge-test`");
    try expectContains(bridge_slice, "`make -C zigux phase8`");

    try expectContains(boundary_survey, "keep the landed helper-local bridge packet");
    try expectContains(boundary_survey, "Current `master` still keeps the mixed-source bridge packet reviewable, and authenticated contents readback now reaches the bridge-side helper and witness files directly again in this runtime.");
    try expectContains(boundary_survey, "`zigux/tests/phase8_file_path_handle_boundary_guard.zig`");
    try expectContains(boundary_survey, "`zigux/tests/phase8_file_path_handle_bridge_manifest_sync.zig`");
    try expectContains(boundary_survey, "live procfs reads, live bpffs opens, token materialization, `bpf_obj_get()` reopen flow, descriptor replacement, or broader fd ownership behavior");
    try expectContains(boundary_survey, "`scripts/zigux/validate-phase8.py`");
    try expectContains(boundary_survey, "`make -C zigux phase8-file-path-handle-bridge-test`");
    try expectContains(boundary_survey, "`make -C zigux phase8`");

    try expectContains(shared_build, "phase8_file_path_handle_boundary_guard.zig");
    try expectContains(shared_build, "phase8-file-path-handle-boundary-guard-tests");
    try expectContains(shared_build, "phase8_file_path_handle_bridge_manifest_sync.zig");
    try expectContains(shared_build, "phase8-file-path-handle-bridge-manifest-sync-tests");
}
