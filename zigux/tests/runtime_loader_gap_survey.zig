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

test "phase 9 runtime loader gap survey keeps bitmap shared-request snapshots explicit" {
    const allocator = std.testing.allocator;
    const bitmap_loader = try readRepoFileAlloc(allocator, "samples/zigux/runtime_bitmap_loader.zig", 128 * 1024);
    defer allocator.free(bitmap_loader);

    try expectContains(bitmap_loader, "keepsSharedLoadPlanSnapshotExplicit");
    try expectContains(bitmap_loader, "runtime bitmap loader rejects shared-load-plan snapshot drift");
    try expectContains(bitmap_loader, "runtime bitmap loader keeps initialized shared-request snapshots stable across later selftest activity");
    try expectContains(bitmap_loader, "runtime bitmap loader keeps selftest-complete shared-request snapshots stable across later exit activity");
    try expectContains(bitmap_loader, "runtime_loader.RequestState.waiting_on_runtime_substrate");
    try expectContains(bitmap_loader, "runtime_loader.RequestState.released_without_substrate");
    try expectContains(bitmap_loader, "releaseSharedWithoutSubstrate");
}

test "phase 9 runtime loader gap survey keeps kretprobe shared-request snapshots explicit" {
    const allocator = std.testing.allocator;
    const kretprobe_loader = try readRepoFileAlloc(allocator, "samples/zigux/runtime_kretprobe_loader.zig", 128 * 1024);
    defer allocator.free(kretprobe_loader);

    try expectContains(kretprobe_loader, "keepsSharedLoadPlanSnapshotExplicit");
    try expectContains(kretprobe_loader, "runtime kretprobe loader rejects shared-load-plan snapshot drift");
    try expectContains(kretprobe_loader, "runtime kretprobe loader keeps initialized shared-request snapshots stable across later selftest activity");
    try expectContains(kretprobe_loader, "runtime kretprobe loader keeps selftest-complete shared-request snapshots stable across later exit activity");
    try expectContains(kretprobe_loader, "runtime_loader.RequestState.waiting_on_runtime_substrate");
    try expectContains(kretprobe_loader, "runtime_loader.RequestState.released_without_substrate");
    try expectContains(kretprobe_loader, "releaseSharedWithoutSubstrate");
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

test "phase 9 runtime loader gap survey keeps lifecycle-boundary manifest surfaces explicit" {
    const allocator = std.testing.allocator;
    const manifest = try readRepoFileAlloc(allocator, "zigux/tests/runtime_loader_gap_manifest.json", 128 * 1024);
    defer allocator.free(manifest);

    const kretprobe_loader = try readRepoFileAlloc(allocator, "samples/zigux/runtime_kretprobe_loader.zig", 128 * 1024);
    defer allocator.free(kretprobe_loader);

    const trace_events_loader = try readRepoFileAlloc(allocator, "samples/zigux/runtime_trace_events_loader.zig", 128 * 1024);
    defer allocator.free(trace_events_loader);

    try expectContains(manifest, "\"shared_request_boundary_surface\": \"zigux/kernel/runtime_loader.zig\"");
    try expectContains(manifest, "\"shared_request_boundary_guard\": \"RuntimeLoadRequest.keepsPreExecutionLifecycleBoundaryExplicit\"");
    try expectContains(manifest, "\"review_only_loader_plan_surfaces\": [");
    try expectContains(manifest, "\"samples/zigux/runtime_atomic64_loader.zig\"");
    try expectContains(manifest, "\"samples/zigux/runtime_bitmap_loader.zig\"");
    try expectContains(manifest, "\"samples/zigux/runtime_kretprobe_loader.zig\"");
    try expectContains(manifest, "\"samples/zigux/runtime_trace_events_loader.zig\"");
    try expectContains(manifest, "\"metadata_only_registration_surfaces\": [");
    try expectContains(manifest, "\"forbidden_live_calls\": [ \"module_init()\", \"module_exit()\", \"register_kretprobe()\", \"unregister_kretprobe()\" ]");
    try expectContains(kretprobe_loader, "register_kretprobe");
    try expectContains(kretprobe_loader, "unregister_kretprobe");
    try expectContains(trace_events_loader, "tracepoint_probe_register");
    try expectContains(trace_events_loader, "tracepoint_probe_unregister");
    try expectContains(trace_events_loader, "registration_depth");
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

test "phase 9 runtime loader gap survey keeps module metadata and depmod boundaries explicit" {
    const allocator = std.testing.allocator;
    const manifest = try readRepoFileAlloc(allocator, "zigux/tests/runtime_loader_gap_manifest.json", 128 * 1024);
    defer allocator.free(manifest);

    const note = try readRepoFileAlloc(allocator, "Documentation/zigux/phase9-runtime-loader-gap-survey.md", 128 * 1024);
    defer allocator.free(note);

    const runtime_loader = try readRepoFileAlloc(allocator, "zigux/kernel/runtime_loader.zig", 128 * 1024);
    defer allocator.free(runtime_loader);

    try expectContains(manifest, "\"module_metadata_depmod_boundaries\"");
    try expectContains(manifest, "\"surface\": \".modinfo\"");
    try expectContains(manifest, "\"surface\": \"MODULE_ALIAS()\"");
    try expectContains(manifest, "\"surface\": \"modules.alias\"");
    try expectContains(manifest, "\"surface\": \"scripts/depmod.sh\"");
    try expectContains(note, "the shared loader-gap manifest also keeps the blocked module-metadata and depmod-publication boundary explicit: `.modinfo`, `MODULE_ALIAS()`, `modules.alias`, and `scripts/depmod.sh` stay named only as blocked boundary surfaces until a real depmod bridge exists");
    try expectContains(note, "no path here claims `.modinfo`, `MODULE_ALIAS()`, `modules.alias`, or `scripts/depmod.sh` parity while the depmod bridge remains absent");
    try expectContains(note, "`.modinfo`, `MODULE_ALIAS()`, `modules.alias`, and `scripts/depmod.sh` remain blocked boundary references in `zigux/tests/runtime_loader_gap_manifest.json` until a real depmod bridge exists");
    try expectNotContains(runtime_loader, ".modinfo");
    try expectNotContains(runtime_loader, "MODULE_ALIAS()");
    try expectNotContains(runtime_loader, "modules.alias");
    try expectNotContains(runtime_loader, "scripts/depmod.sh");
}
