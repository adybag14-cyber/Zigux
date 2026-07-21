const std = @import("std");

fn readRepoFileAlloc(allocator: std.mem.Allocator, path: []const u8, max_bytes: usize) ![]u8 {
    var io_instance: std.Io.Threaded = .init(allocator, .{});
    defer io_instance.deinit();
    return try std.Io.Dir.cwd().readFileAlloc(io_instance.io(), path, allocator, .limited(max_bytes));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectMissing(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

fn expectOrder(haystack: []const u8, before: []const u8, after: []const u8) !void {
    const before_index = std.mem.indexOf(u8, haystack, before) orelse {
        try std.testing.expect(false);
        return;
    };
    const after_index = std.mem.indexOf(u8, haystack, after) orelse {
        try std.testing.expect(false);
        return;
    };
    try std.testing.expect(before_index < after_index);
}

test "phase 2 closure note keeps current parked status and restored surface pointers" {
    const allocator = std.testing.allocator;
    const closure = try readRepoFileAlloc(
        allocator,
        "Documentation/zigux/phase2-closure.md",
        128 * 1024,
    );
    defer allocator.free(closure);

    try expectContains(closure, "This note keeps the shared Phase 2 closure packet parked");
    try expectContains(closure, "`PHASE2_STATUS=parked`");
    try expectContains(closure, "`PHASE2_CLOSURE_RESTORE_STATE=docs_plus_manifest`");
    try expectContains(closure, "manifest: `zigux/tests/fixtures/phase2_tool_manifest.json`");
    try expectContains(closure, "shared note: `Documentation/zigux/phase2-toolchain-bootstrap-notes.md`");
    try expectContains(closure, "shared validator pair: `zig run scripts/zigux/validate_phase2.zig` and `zig run scripts/zigux/validate_phase2_closure.zig`");
    try expectMissing(closure, "`PHASE2_STATUS=closed`");
    try expectMissing(closure, "`PHASE2_CLOSURE_RESTORE_STATE=workflow_only`");
}

test "phase 2 closure next step preserves kconfig and genksyms implementation handoffs" {
    const allocator = std.testing.allocator;
    const closure = try readRepoFileAlloc(
        allocator,
        "Documentation/zigux/phase2-closure.md",
        128 * 1024,
    );
    defer allocator.free(closure);

    try expectContains(closure, "`PHASE2_CURRENT_GAP_PACKET=Documentation/zigux/phase2-kconfig-bridge-gap-survey.md`");
    try expectContains(closure, "current authenticated repo reads do not expose `scripts/kconfig/conf.c` or `scripts/kconfig/confdata.c` on `master`");
    try expectContains(closure, "request-plan `allconfig` overrides stay limited to `allmodconfig`, `alldefconfig`, and `randconfig`");
    try expectContains(closure, "`allconfig_sentinel_packet` still covers `allnoconfig` and `allyesconfig`");
    try expectContains(closure, "the helper-local explicit-override roster remains broader by design");
    try expectContains(closure, "start with one smallest same-family step that preserves the restored CRC-side evidence and wrapper bridge packet");
    try expectOrder(
        closure,
        "If the kconfig bridge lane resumes substantive implementation",
        "If the `genksyms` lane resumes substantive implementation",
    );
}

test "phase 2 manifest keeps closure notes and validators aligned with the parked packet" {
    const allocator = std.testing.allocator;
    const manifest = try readRepoFileAlloc(
        allocator,
        "zigux/tests/fixtures/phase2_tool_manifest.json",
        256 * 1024,
    );
    defer allocator.free(manifest);

    try expectContains(manifest, "\"status\": \"active\"");
    try expectContains(manifest, "\"repo_reality_gaps\": []");
    try expectContains(manifest, "\"Documentation/zigux/phase2-closure.md\"");
    try expectContains(manifest, "\"Documentation/zigux/phase2-toolchain-bootstrap-notes.md\"");
    try expectContains(manifest, "\"scripts\zigux/validate_phase2.zig\"");
    try expectContains(manifest, "\"scripts\zigux/validate_phase2_closure.zig\"");
    try expectContains(manifest, "\"scripts\zigux/check_phase2_tool_manifest.zig\"");
    try expectContains(manifest, "\"scripts\zigux/check_phase2_bootstrap_workflow_routes.zig\"");
    try expectContains(manifest, "\"scripts\zigux/check_phase2_artifact_tools_manifest.zig\"");
}
