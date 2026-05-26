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

test "phase 8 file-path handle bridge manifest keeps the current landed foothold, queued helper wording, and deferred boundary explicit" {
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

test "phase 8 file-path-handle bridge slice keeps the landed foothold and queued helper rationale aligned with the manifest" {
    const note = try readWorkspaceFile(
        std.testing.allocator,
        "Documentation/zigux/phase8-file-path-handle-bridge-slice.md",
        32 * 1024,
    );
    defer std.testing.allocator.free(note);

    try expectContains(
        note,
        "scope: helper-local pathname shaping, fdinfo line splitting, reused-map-name retention, and deferred bridge-boundary truthfulness only",
    );
    try expectContains(
        note,
        "That landed helper packet keeps bounded `\"/proc/%d/fdinfo/%d\"` pathname shaping through `validateProcFdinfoRoot()` and `buildProcFdinfoPath()`, `parseFdinfoLine()` field splitting, `summarizeReusedMapName()` retained-name summaries, and `resolveReusedMapName()` plus errno-shaped wrappers explicit without claiming direct file reads, numeric fdinfo map-info decoding, or reuse-comparison side effects.",
    );
    try expectContains(
        note,
        "The landed `fdinfo-path-and-reuse-name-footholds` slice therefore now mirrors the manifest rationale exactly: This materializes the shared bridge destination with side-effect-free pathname shaping and bounded reused-map name retention while keeping procfs reads, full fdinfo map-info parsing, and reuse comparison logic deferred.",
    );
    try expectContains(
        note,
        "The neighboring `fdinfo-map-info-helpers` slice now stays explicit as queued groundwork rather than landed bridge proof: the shared bridge destination is materialized for helper-only proc-fdinfo pathname shaping, but the fdinfo line parser, numeric map-info decoder, and completion summary helpers still need their own follow-through before that slice can be reported as fully landed.",
    );
    try expectContains(
        note,
        "The sibling `map-reuse-compatibility` slice likewise stays explicit as queued groundwork rather than landed bridge proof: current helper source retains reused-map names, but helper-only compatibility observation, flag normalization, and mismatch reporting still need follow-through before that slice can be reported as fully landed.",
    );
    try expectContains(
        note,
        "The deferred boundary still covers direct procfs reads, live bpffs opens, `bpf_obj_get()` reopen flow, token materialization, and descriptor replacement, transfer, or close ownership semantics.",
    );
}

test "phase 8 bridge boundary survey keeps the mixed-source helper packet, landed foothold, queued helper groundwork, and deferred side-effect boundary explicit" {
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
        "Within that bounded packet, current `master` keeps `validateProcFdinfoRoot()`, `buildProcFdinfoPath()`, `parseFdinfoLine()`, `summarizeReusedMapName()`, and `resolveReusedMapName()` explicit as side-effect-free bridge-adjacent helpers. They keep pathname shaping, line splitting, and retained-name summaries reviewable without claiming direct procfs reads, bpffs opens, token materialization, or descriptor ownership behavior.",
    );
    try expectContains(
        note,
        "The landed `fdinfo-path-and-reuse-name-footholds` slice therefore now mirrors the manifest rationale exactly: This materializes the shared bridge destination with side-effect-free pathname shaping and bounded reused-map name retention while keeping procfs reads, full fdinfo map-info parsing, and reuse comparison logic deferred.",
    );
    try expectContains(
        note,
        "The neighboring `fdinfo-map-info-helpers` slice now stays explicit as queued groundwork rather than landed bridge proof: the shared bridge destination is materialized for helper-only proc-fdinfo pathname shaping, but the fdinfo line parser, numeric map-info decoder, and completion summary helpers still need their own follow-through before that slice can be reported as fully landed.",
    );
    try expectContains(
        note,
        "The sibling `map-reuse-compatibility` slice likewise stays explicit as queued groundwork rather than landed bridge proof: current helper source retains reused-map names, but helper-only compatibility observation, flag normalization, and mismatch reporting still need follow-through before that slice can be reported as fully landed.",
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
