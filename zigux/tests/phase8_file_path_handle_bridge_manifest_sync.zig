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
        "\"lane_key\": \"P8-L13\"",
    );
    try expectContains(
        manifest,
        "\"id\": \"P8-L13-S05\"",
    );
    try expectContains(
        manifest,
        "\"id\": \"P8-L13-S06\"",
    );
    try expectContains(
        manifest,
        "\"id\": \"P8-L13-S07\"",
    );
    try expectContains(
        manifest,
        "\"surveyed_commit\": \"3fbd40a49963769118cb15f2aadfc175540c833d\"",
    );
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

test "phase 8 file-path handle bridge slice keeps the landed helper rationale aligned with the manifest" {
    const note = try readWorkspaceFile(
        std.testing.allocator,
        "Documentation/zigux/phase8-file-path-handle-bridge-slice.md",
        32 * 1024,
    );
    defer std.testing.allocator.free(note);

    try expectContains(
        note,
        "The shared file-path bridge destination already carries the bounded procfs path construction and fdinfo text parsing helpers, so this landed slice should stay explicitly smaller than direct file reads, descriptor ownership, or pinned-object reopen flow.",
    );
    try expectContains(
        note,
        "The shared bridge surface now already carries the reused-map-name chooser and compatibility comparison as landed helper-only behavior, and it should stay reviewable without widening into FD duplication, close-on-replacement, or pinned-map reopen side effects.",
    );
}

test "phase 8 bridge boundary survey keeps the mixed-source helper packet and deferred side-effect boundary explicit" {
    const note = try readWorkspaceFile(
        std.testing.allocator,
        "Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md",
        32 * 1024,
    );
    defer std.testing.allocator.free(note);

    try expectContains(
        note,
        "Current `master` still keeps the mixed-source bridge packet reviewable, but the readable sources stay split in this runtime.",
    );
    try expectContains(
        note,
        "Current authenticated contents readback now also reaches the bridge helper and witness files directly again, but the narrower split recorded here is packet role only: those files still belong to the bridge-boundary companion packet instead of the exact stable-output helper set.",
    );
    try expectContains(
        note,
        "`tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig`",
    );
    try expectContains(
        note,
        "`zigux/tests/phase8_file_path_handle_bridge.zig`",
    );
    try expectContains(
        note,
        "`zigux/tests/phase8_file_path_handle_bridge_manifest_sync.zig`",
    );
    try expectContains(
        note,
        "That packet stays smaller than live procfs reads, live bpffs opens, token materialization, `bpf_obj_get()` reopen flow, descriptor replacement, or broader fd ownership behavior.",
    );
    try expectContains(
        note,
        "The landed `fdinfo-map-info-helpers` slice therefore still mirrors the manifest rationale exactly: The shared file-path bridge destination already carries the bounded procfs path construction and fdinfo text parsing helpers, so this landed slice should stay explicitly smaller than direct file reads, descriptor ownership, or pinned-object reopen flow.",
    );
    try expectContains(
        note,
        "The sibling `map-reuse-compatibility` slice likewise still mirrors the manifest rationale exactly: The shared bridge surface now already carries the reused-map-name chooser and compatibility comparison as landed helper-only behavior, and it should stay reviewable without widening into FD duplication, close-on-replacement, or pinned-map reopen side effects.",
    );
    try expectContains(
        note,
        "The timing-adjacent poll reminder also stays explicit through `Documentation/zigux/phase8-perf-buffer-poll-slice.md`, `python3 scripts/zigux/check-phase8-perf-buffer-poll-gate.py`, `make -C zigux phase8-perf-buffer-poll-test`, and the shared `phase8` routes; that dedicated packet keeps no standalone timer helper behavior, no standalone clockevent helper behavior, and no broader timeout-sensitive routing behavior explicit while the surrounding setup-side bridge remains deferred.",
    );
}

test "phase 8 bridge manifest sync keeps the shared validator bridge packet explicit" {
    const validate_phase8 = try readWorkspaceFile(
        std.testing.allocator,
        "scripts/zigux/validate-phase8.py",
        96 * 1024,
    );
    defer std.testing.allocator.free(validate_phase8);

    try expectContains(
        validate_phase8,
        "Documentation/zigux/phase8-file-path-handle-bridge-slice.md",
    );
    try expectContains(
        validate_phase8,
        "zigux/tests/phase8_file_path_handle_boundary_guard.zig",
    );
    try expectContains(
        validate_phase8,
        "zigux/tests/phase8_file_path_handle_bridge_manifest_sync.zig",
    );
    try expectContains(
        validate_phase8,
        "tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig",
    );
    try expectContains(
        validate_phase8,
        "phase8-file-path-handle-bridge-test",
    );
}