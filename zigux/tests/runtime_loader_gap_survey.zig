const std = @import("std");

fn readRepoFileAlloc(allocator: std.mem.Allocator, path: []const u8, max_bytes: usize) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(std.testing.io, path, allocator, .limited(max_bytes));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    if (std.mem.indexOf(u8, haystack, needle) == null) {
        std.debug.print("missing marker: {s}\n", .{needle});
        return error.MissingMarker;
    }
}

fn expectNotContains(haystack: []const u8, needle: []const u8) !void {
    if (std.mem.indexOf(u8, haystack, needle) != null) {
        std.debug.print("unexpected marker: {s}\n", .{needle});
        return error.UnexpectedMarker;
    }
}

test "phase 9 runtime loader gap survey keeps manifest and note aligned" {
    const allocator = std.testing.allocator;
    const manifest = try readRepoFileAlloc(allocator, "zigux/tests/runtime_loader_gap_manifest.json", 128 * 1024);
    defer allocator.free(manifest);

    const note = try readRepoFileAlloc(allocator, "Documentation/zigux/phase9-runtime-loader-gap-survey.md", 128 * 1024);
    defer allocator.free(note);

    try expectContains(manifest, "\"path\": \"zigux/tests/runtime_loader_gap_survey.zig\"");
    try expectContains(manifest, "\"role\": \"machine-checks the manifest, the blocker note, the shared request contract, the explicit without-substrate rollback path, the new shared command_name field, and the still-absent argv or environment control surface\"");
    try expectContains(manifest, "\"surface\": \"zigux/tests/runtime_loader_gap_survey.zig\"");
    try expectContains(note, "`zigux/tests/runtime_loader_gap_survey.zig` owns the machine-checkable replay of the manifest, note, shared request surface, and without-substrate rollback posture");
    try expectContains(note, "`make -C zigux phase9-loader-gap-survey`");
    try expectContains(note, "`zigux/tests/runtime_loader_gap_manifest.json` owns the manifest-backed catalog and ownership map for the current delivery packet");
}

test "phase 9 runtime loader gap survey keeps the shared request surface explicit" {
    const allocator = std.testing.allocator;
    const runtime_loader = try readRepoFileAlloc(allocator, "zigux/kernel/runtime_loader.zig", 128 * 1024);
    defer allocator.free(runtime_loader);

    const note = try readRepoFileAlloc(allocator, "Documentation/zigux/phase9-runtime-loader-gap-survey.md", 128 * 1024);
    defer allocator.free(note);

    try expectContains(runtime_loader, "command_name");
    try expectContains(runtime_loader, "released_without_substrate");
    try expectContains(runtime_loader, "releaseWithoutSubstrate");
    try expectContains(note, "the shared request shape carries module identity, an optional shared `command_name` field");
    try expectContains(note, "the current fallback path for the pre-execution packet");
}

test "phase 9 runtime loader gap survey keeps the blocked trace-events boundary visible" {
    const allocator = std.testing.allocator;
    const trace_manifest = try readRepoFileAlloc(allocator, "zigux/tests/runtime_trace_events_manifest.json", 128 * 1024);
    defer allocator.free(trace_manifest);

    const note = try readRepoFileAlloc(allocator, "Documentation/zigux/phase9-runtime-loader-gap-survey.md", 128 * 1024);
    defer allocator.free(note);

    try expectContains(trace_manifest, "runtime-trace-events-substrate-handoff");
    try expectContains(note, "`samples/zigux/runtime_trace_events.zig` plus `zigux/tests/runtime_trace_events_manifest.json` still own the sample-only blocked runtime pilot boundary");
    try expectContains(note, "`samples/zigux/runtime_trace_events_loader.zig` now records the same bounded init or exit handoff shape");
}

test "phase 9 runtime loader gap survey keeps phase 8 argv and environment controls out of the shared runtime surface" {
    const allocator = std.testing.allocator;
    const runtime_loader = try readRepoFileAlloc(allocator, "zigux/kernel/runtime_loader.zig", 128 * 1024);
    defer allocator.free(runtime_loader);

    const note = try readRepoFileAlloc(allocator, "Documentation/zigux/phase9-runtime-loader-gap-survey.md", 128 * 1024);
    defer allocator.free(note);

    try expectNotContains(runtime_loader, "PERF_EXEC_PATH");
    try expectNotContains(runtime_loader, "Config.exec_path_env");
    try expectNotContains(runtime_loader, "LINES");
    try expectNotContains(runtime_loader, "COLUMNS");
    try expectContains(note, "`tools/lib/subcmd/exec-cmd.zig` owns the live Phase 8 command-name and path-shaping surfaces");
    try expectContains(note, "`tools/lib/subcmd/help.zig` owns the live Phase 8 terminal-cue surfaces");
    try expectContains(note, "the shared request contract now records an optional shared `command_name` field, but no broader shared runtime command or environment control surface yet records argv policy or environment-derived activation cues");
}
