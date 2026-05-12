const std = @import("std");

fn readRepoFileAlloc(allocator: std.mem.Allocator, path: []const u8, max_bytes: usize) ![]u8 {
    var io_instance: std.Io.Threaded = .init(allocator, .{});
    defer io_instance.deinit();
    return try std.Io.Dir.cwd().readFileAlloc(io_instance.io(), path, allocator, .limited(max_bytes));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectMissingRepoFile(path: []const u8) !void {
    const maybe_bytes = readRepoFileAlloc(std.testing.allocator, path, 1024);
    if (maybe_bytes) |bytes| {
        defer std.testing.allocator.free(bytes);
        return error.ExpectedMissingRepoFile;
    } else |err| switch (err) {
        error.FileNotFound => {},
        else => return err,
    }
}

test "phase 9 runtime loader gap survey keeps note, manifest, and stale shared-build boundary aligned" {
    const allocator = std.testing.allocator;

    const manifest = try readRepoFileAlloc(
        allocator,
        "zigux/tests/runtime_loader_gap_manifest.json",
        64 * 1024,
    );
    defer allocator.free(manifest);

    const note = try readRepoFileAlloc(
        allocator,
        "Documentation/zigux/phase9-runtime-loader-gap-survey.md",
        64 * 1024,
    );
    defer allocator.free(note);

    const phase9_build = try readRepoFileAlloc(
        allocator,
        "zigux/tests/phase9_build.zig",
        64 * 1024,
    );
    defer allocator.free(phase9_build);

    try expectContains(manifest, "\"lane_key\": \"P9-L15\"");
    try expectContains(manifest, "\"phase\": \"Phase 9\"");
    try expectContains(manifest, "\"shared_runtime_loader_files_present\": false");
    try expectContains(manifest, "\"shared_runtime_loader_contract_present\": false");
    try expectContains(manifest, "\"shared_phase9_build_route_replayable\": false");
    try expectContains(manifest, "\"current_honest_gate\": \"zig test zigux/tests/runtime_loader_gap_survey.zig\"");
    try expectContains(manifest, "\"role\": \"adjacent_stale_shared_build_scaffold\"");
    try expectContains(manifest, "\"status\": \"missing_on_current_master\"");
    try expectContains(manifest, "\"status\": \"present_but_not_replayable\"");
    try expectContains(manifest, "\"status\": \"starter_landed\"");
    try expectContains(manifest, "\"surface\": \"samples/zigux/runtime_trace_events_loader.zig\"");
    try expectContains(manifest, "\"surface\": \"zigux/tests/runtime_loader_gap_survey.zig\"");

    try expectContains(note, "PHASE9_STATUS=active");
    try expectContains(note, "PHASE9_SLICE=runtime-loader-gap-survey");
    try expectContains(note, "PHASE9_LANE_KEY=P9-L15");
    try expectContains(note, "`zigux/tests/runtime_loader_gap_manifest.json`");
    try expectContains(note, "`zigux/tests/runtime_loader_gap_survey.zig`");
    try expectContains(note, "`zigux/kernel/runtime_loader.zig` and `zigux/kernel/runtime_loader_contract.zig`\nreturn missing-file results on current `master`");
    try expectContains(note, "`zigux/tests/phase9_build.zig` remains an adjacent stale shared-build scaffold");
    try expectContains(note, "`zig test zigux/tests/runtime_loader_gap_survey.zig`");
    try expectContains(note, "`make -C zigux phase9-runtime-loader-shared-tests` stays blocked until the\nshared runtime-loader files land");
    try expectContains(note, "`make -C zigux phase9` stays blocked until the shared runtime-loader files\nland");
    try expectContains(note, "`tools/lib/subcmd/exec-cmd.zig`");
    try expectContains(note, "`tools/lib/subcmd/help.zig`");

    try expectContains(phase9_build, "../kernel/runtime_loader.zig");
    try expectContains(phase9_build, "../kernel/runtime_loader_contract.zig");
    try expectContains(phase9_build, "\"phase9-runtime-loader-shared-tests\"");
}

test "phase 9 runtime loader gap survey keeps missing shared runtime-loader surfaces explicit" {
    try expectMissingRepoFile("zigux/kernel/runtime_loader.zig");
    try expectMissingRepoFile("zigux/kernel/runtime_loader_contract.zig");
}

test "phase 9 runtime loader gap survey keeps loader-scaffold rollback and lifecycle evidence reviewable" {
    const allocator = std.testing.allocator;

    const atomic64_loader = try readRepoFileAlloc(
        allocator,
        "samples/zigux/runtime_atomic64_loader.zig",
        128 * 1024,
    );
    defer allocator.free(atomic64_loader);

    const bitmap_loader = try readRepoFileAlloc(
        allocator,
        "samples/zigux/runtime_bitmap_loader.zig",
        128 * 1024,
    );
    defer allocator.free(bitmap_loader);

    const kretprobe_loader = try readRepoFileAlloc(
        allocator,
        "samples/zigux/runtime_kretprobe_loader.zig",
        160 * 1024,
    );
    defer allocator.free(kretprobe_loader);

    const trace_loader = try readRepoFileAlloc(
        allocator,
        "samples/zigux/runtime_trace_events_loader.zig",
        192 * 1024,
    );
    defer allocator.free(trace_loader);

    try expectContains(atomic64_loader, "releaseSharedWithoutSubstrate");
    try expectContains(atomic64_loader, "runtime atomic64 loader keeps initialized shared-request snapshots stable across later selftest activity");
    try expectContains(atomic64_loader, "runtime atomic64 loader keeps selftest-complete shared-request snapshots stable across later exit activity");
    try expectContains(atomic64_loader, "runtime_loader.RequestState.released_without_substrate");

    try expectContains(bitmap_loader, "releaseSharedWithoutSubstrate");
    try expectContains(bitmap_loader, "runtime bitmap loader keeps initialized shared-request snapshots stable across later selftest activity");
    try expectContains(bitmap_loader, "runtime bitmap loader keeps selftest-complete shared-request snapshots stable across later exit activity");
    try expectContains(bitmap_loader, "runtime_loader.RequestState.released_without_substrate");

    try expectContains(kretprobe_loader, "releaseSharedWithoutSubstrate");
    try expectContains(kretprobe_loader, "runtime kretprobe loader keeps initialized shared-request snapshots stable across later selftest activity");
    try expectContains(kretprobe_loader, "runtime kretprobe loader keeps selftest-complete shared-request snapshots stable across later exit activity");
    try expectContains(kretprobe_loader, "runtime_loader.RequestState.released_without_substrate");

    try expectContains(trace_loader, "releaseSharedWithoutSubstrate");
    try expectContains(trace_loader, "runtime trace-events loader keeps initialized shared-request snapshots stable across later selftest activity");
    try expectContains(trace_loader, "runtime trace-events loader keeps selftest-complete shared-request snapshots stable across later exit activity");
    try expectContains(trace_loader, "runtime trace-events loader rejects registration snapshot drift");
    try expectContains(trace_loader, "runtime_loader.RequestState.released_without_substrate");
}

test "phase 9 runtime loader gap survey keeps adjacent family-local blockers explicit" {
    const allocator = std.testing.allocator;

    const manifest = try readRepoFileAlloc(
        allocator,
        "zigux/tests/runtime_loader_gap_manifest.json",
        64 * 1024,
    );
    defer allocator.free(manifest);

    const trace_manifest = try readRepoFileAlloc(
        allocator,
        "zigux/tests/runtime_trace_events_manifest.json",
        64 * 1024,
    );
    defer allocator.free(trace_manifest);

    const kretprobe_manifest = try readRepoFileAlloc(
        allocator,
        "zigux/tests/runtime_kretprobe_manifest.json",
        32 * 1024,
    );
    defer allocator.free(kretprobe_manifest);

    try expectContains(manifest, "\"surface\": \"zigux/tests/runtime_trace_events_manifest.json\"");
    try expectContains(manifest, "\"surface\": \"zigux/tests/runtime_kretprobe_manifest.json\"");
    try expectContains(manifest, "\"zigux_destination\": \"zigux/tests/phase9_build.zig\"");
    try expectContains(manifest, "\"zigux_destination\": \"zigux/kernel/runtime_loader.zig\"");

    try expectContains(trace_manifest, "runtime-trace-events-substrate-handoff");
    try expectContains(trace_manifest, "\"live_registration_parity\": \"blocked_on_runtime_substrate\"");

    try expectContains(kretprobe_manifest, "runtime-kretprobe-substrate-handoff");
    try expectContains(kretprobe_manifest, "\"live_registration_parity\": \"blocked_on_runtime_substrate\"");
}
