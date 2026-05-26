const std = @import("std");

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

test "phase 8 file-path handle bridge manifest keeps the current landed helper packet and deferred boundary explicit" {
    const manifest = try readWorkspaceFile(
        std.testing.allocator,
        "tools/lib/bpf/zigux_segments/manifest.json",
        64 * 1024,
    );
    defer std.testing.allocator.free(manifest);

    try expectContains(manifest, "\"slug\": \"fdinfo-map-info-helpers\"");
    try expectContains(manifest, "\"status\": \"starter_landed\"");
    try expectContains(manifest, "bounded procfs path construction");
    try expectContains(manifest, "fdinfo text parsing");
    try expectContains(manifest, "\"slug\": \"map-reuse-compatibility\"");
    try expectContains(manifest, "\"status\": \"starter_landed\"");
    try expectContains(manifest, "reused-map-name chooser");
    try expectContains(manifest, "compatibility comparison");
    try expectContains(manifest, "\"slug\": \"file-path-and-handle-bridge\"");
    try expectContains(manifest, "\"status\": \"deferred_high_risk\"");
    try expectContains(manifest, "\"kind\": \"resource_boundary\"");
    try expectContains(manifest, "procfs reads");
    try expectContains(manifest, "bpffs opens");
    try expectContains(manifest, "token creation");
    try expectContains(manifest, "bpf_obj_get() reopen flow");
    try expectContains(manifest, "fd ownership semantics");
}

test "phase 8 file-path-handle bridge slice keeps the landed helper packet aligned with the current helper surface" {
    const note = try readWorkspaceFile(
        std.testing.allocator,
        "Documentation/zigux/phase8-file-path-handle-bridge-slice.md",
        32 * 1024,
    );
    defer std.testing.allocator.free(note);

    try expectContains(note, "scope: helper-local pathname shaping, fdinfo map-info parsing, reused-map compatibility planning, and deferred bridge-boundary truthfulness only");
    try expectContains(note, "buildCurrentProcessFdinfoPath()");
    try expectContains(note, "applyFdinfoMapInfoLine()");
    try expectContains(note, "parseFdinfoMapInfo()");
    try expectContains(note, "summarizeFdinfoMapInfo()");
    try expectContains(note, "mapReuseObservationFromFdinfo()");
    try expectContains(note, "summarizeMapReuseCompatibility()");
    try expectContains(note, "isMapReuseCompatible()");
    try expectContains(note, "planning-only `resolveReusePinnedMapAttempt()` gating");
    try expectContains(note, "planning-only `planTokenPreparation()` gating");
    try expectContains(note, "no live bpffs opens");
    try expectContains(note, "no token materialization");
}

test "phase 8 bridge boundary survey keeps the mixed-source helper packet and deferred side-effect boundary explicit" {
    const note = try readWorkspaceFile(
        std.testing.allocator,
        "Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md",
        32 * 1024,
    );
    defer std.testing.allocator.free(note);

    try expectContains(note, "Current `master` still keeps the mixed-source bridge packet reviewable");
    try expectContains(note, "`tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig`");
    try expectContains(note, "`zigux/tests/phase8_file_path_handle_bridge.zig`");
    try expectContains(note, "`zigux/tests/phase8_file_path_handle_boundary_guard.zig`");
    try expectContains(note, "`zigux/tests/phase8_file_path_handle_bridge_manifest_sync.zig`");
    try expectContains(note, "`scripts/zigux/validate-phase8.py`");
    try expectContains(note, "buildCurrentProcessFdinfoPath()");
    try expectContains(note, "applyFdinfoMapInfoLine()");
    try expectContains(note, "parseFdinfoMapInfo()");
    try expectContains(note, "summarizeFdinfoMapInfo()");
    try expectContains(note, "summarizeMapReuseCompatibility()");
    try expectContains(note, "isMapReuseCompatible()");
    try expectContains(note, "resolveReusePinnedMapAttempt()");
    try expectContains(note, "planTokenPreparation()");
    try expectContains(note, "live procfs reads, live bpffs opens, token materialization, `bpf_obj_get()` reopen flow, descriptor replacement, or broader fd ownership behavior");
}

test "phase 8 bridge manifest sync keeps the shared validator bridge packet explicit" {
    const validate_phase8 = try readWorkspaceFile(
        std.testing.allocator,
        "scripts/zigux/validate-phase8.py",
        96 * 1024,
    );
    defer std.testing.allocator.free(validate_phase8);

    try expectContains(validate_phase8, "Documentation/zigux/phase8-file-path-handle-bridge-slice.md");
    try expectContains(validate_phase8, "zigux/tests/phase8_file_path_handle_boundary_guard.zig");
    try expectContains(validate_phase8, "zigux/tests/phase8_file_path_handle_bridge_manifest_sync.zig");
    try expectContains(validate_phase8, "tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig");
    try expectContains(validate_phase8, "phase8-file-path-handle-bridge-test");
}
