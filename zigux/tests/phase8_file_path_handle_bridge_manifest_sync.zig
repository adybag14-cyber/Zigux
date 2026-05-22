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

test "phase 8 file-path handle bridge manifest keeps the landed helper wording explicit" {
    const manifest = try readWorkspaceFile(
        std.testing.allocator,
        "tools/lib/bpf/zigux_segments/manifest.json",
        64 * 1024,
    );
    defer std.testing.allocator.free(manifest);

    try expectContains(
        manifest,
        "\"slug\": \"fdinfo-map-info-helpers\", \"status\": \"starter_landed\"",
    );
    try expectContains(
        manifest,
        "\"why_now\": \"The shared file-path bridge destination already carries the bounded procfs path construction and fdinfo text parsing helpers, so this landed slice should stay explicitly smaller than direct file reads, descriptor ownership, or pinned-object reopen flow.\"",
    );
    try expectContains(
        manifest,
        "\"slug\": \"map-reuse-compatibility\", \"status\": \"starter_landed\"",
    );
    try expectContains(
        manifest,
        "\"why_now\": \"The shared bridge surface now already carries the reused-map-name chooser and compatibility comparison as landed helper-only behavior, and it should stay reviewable without widening into FD duplication, close-on-replacement, or pinned-map reopen side effects.\"",
    );
    try expectContains(
        manifest,
        "\"slug\": \"file-path-and-handle-bridge\", \"status\": \"deferred_high_risk\", \"kind\": \"resource_boundary\"",
    );
    try expectContains(
        manifest,
        "\"why_now\": \"This remaining file-path and handle bridge still crosses real procfs reads, bpffs opens, token creation, bpf_obj_get() reopen flow, and fd ownership semantics, so the helper-first packet should keep it deferred.\"",
    );
    try expectContains(
        manifest,
        "\"why_now\": \"The shared file-path bridge destination now records the fdinfo parsing foundation, helper-only observation shaping, reused-map compatibility summaries, pinned-map reuse planning, and planning-only token-readiness gating as a reviewable landed helper slice, so future surveys can keep promoting bounded bridge behavior without crossing into live descriptor, token materialization, or reopen side effects.\"",
    );
}
