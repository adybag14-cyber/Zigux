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

test "phase 8 file-path-handle bridge manifest keeps the current landed and queued helper wording explicit" {
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
        "\"id\": \"P8-L13-S13\"",
    );
    try expectContains(
        manifest,
        "\"surveyed_commit\": \"3fbd40a49963769118cb15f2aadfc175540c833d\"",
    );
    try expectContains(
        manifest,
        "\"slug\": \"fdinfo-map-info-helpers\",\n      \"status\": \"blocked_on_fdinfo_parser_materialization\"",
    );
    try expectContains(
        manifest,
        "\"why_now\": \"The shared file-path bridge destination is now materialized for helper-only proc-fdinfo pathname shaping, but the fdinfo line parser, numeric map-info decoder, and completion summary helpers are still queued, so this slice must stay explicit as partially landed rather than complete.\"",
    );
    try expectContains(
        manifest,
        "\"slug\": \"map-reuse-compatibility\",\n      \"status\": \"blocked_on_reuse_comparison_materialization\"",
    );
    try expectContains(
        manifest,
        "\"why_now\": \"The shared bridge file now carries bounded reused-map name retention, but the helper-only compatibility observation, flag normalization, and mismatch reporting work remains queued, so the segment cannot yet be reported as fully landed on master.\"",
    );
    try expectContains(
        manifest,
        "\"slug\": \"file-path-and-handle-bridge\",\n      \"status\": \"deferred_high_risk\",\n      \"kind\": \"resource_boundary\"",
    );
    try expectContains(
        manifest,
        "\"why_now\": \"This remaining file-path and handle bridge still crosses real procfs reads, bpffs opens, token creation, bpf_obj_get() reopen flow, and fd ownership semantics, so the helper-first packet should keep it deferred.\"",
    );
    try expectContains(
        manifest,
        "\"slug\": \"fdinfo-path-and-reuse-name-footholds\",\n      \"status\": \"starter_landed\"",
    );
    try expectContains(
        manifest,
        "\"why_now\": \"This materializes the shared bridge destination with side-effect-free pathname shaping and bounded reused-map name retention while keeping procfs reads, fdinfo parsing, and reuse comparison logic deferred.\"",
    );
    try expectContains(
        manifest,
        "\"why_now\": \"Master now materializes the shared bridge file for stable path-shaping and name-retention outputs, while the remaining fdinfo parser and reuse-comparison packet stays explicit as queued groundwork instead of being overstated as complete.\"",
    );
    try expectContains(
        manifest,
        "direct procfs reads and descriptor ownership flow",
    );
    try expectContains(
        manifest,
        "token creation, bpffs reopen flow, and other fd-handle bridge side effects",
    );
}

test "phase 8 file-path-handle bridge slice keeps the landed helper rationale aligned with the manifest" {
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
        "Current `master` still keeps the mixed-source bridge packet reviewable, and authenticated contents readback now reaches the bridge-side helper and witness files directly again in this runtime.",
    );
    try expectContains(
        note,
        "Exact authenticated contents readback now serves this survey note, `Documentation/zigux/phase8-file-path-handle-bridge-slice.md`, `tools/lib/bpf/zigux_segments/manifest.json`, `tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig`, and `zigux/tests/phase8_file_path_handle_bridge.zig` directly, while the focused bridge build and broader replay companions remain reminder evidence through `zigux/tests/phase8_file_path_handle_bridge_only_build.zig`, `zigux/tests/phase8_file_path_handle_boundary_guard.zig`, `zigux/tests/phase8_file_path_handle_bridge_manifest_sync.zig`, `zigux/tests/phase8_build.zig`, `scripts/zigux/validate-phase8.py`, `zigux/Makefile`, `make -C zigux phase8-file-path-handle-bridge-test`, and `make -C zigux phase8`.",
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
        "The sibling `map-reuse-compatibility` slice likewise still mirrors the manifest rationale exactly: The shared bridge surface now already carries the reused-map-name chooser, truncated-name retention through `resolveReusedMapName()`, devmap readonly-prog flag normalization through `normalizeObservedReuseMapFlags()`, and compatibility comparison as landed helper-only behavior, and it should stay reviewable without widening into FD duplication, close-on-replacement, or pinned-map reopen side effects.",
    );
    try expectContains(
        note,
        "resolveReusedMapName()",
    );
    try expectContains(
        note,
        "normalizeObservedReuseMapFlags()",
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
