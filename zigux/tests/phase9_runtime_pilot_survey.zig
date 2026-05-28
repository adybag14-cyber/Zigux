const std = @import("std");

const present_phase9_files = [_][]const u8{
    "Documentation/zigux/phase9-first-loadable-runtime-module-parity.md",
    "Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md",
    "zigux/tests/phase9_build.zig",
    "zigux/Makefile",
    "zigux/tests/runtime_first_loadable_parity_survey.zig",
    "zigux/tests/runtime_bitmap_survey.zig",
    "zigux/tests/runtime_trace_events_survey.zig",
    "zigux/tests/runtime_kretprobe_survey.zig",
    "zigux/tests/runtime_atomic64_survey.zig",
    "zigux/tests/runtime_bitmap_manifest.json",
    "zigux/tests/runtime_trace_events_manifest.json",
    "zigux/tests/runtime_kretprobe_manifest.json",
    "zigux/tests/runtime_atomic64_manifest.json",
    "samples/zigux/runtime_atomic64_loader.zig",
    "samples/zigux/runtime_bitmap_loader.zig",
    "samples/zigux/runtime_trace_events.zig",
    "samples/zigux/runtime_kretprobe_loader.zig",
};

fn readRepoFileAlloc(path: []const u8, max_bytes: usize) ![]u8 {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();
    return try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        path,
        std.testing.allocator,
        .limited(max_bytes),
    );
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectPresent(path: []const u8) !void {
    const payload = try readRepoFileAlloc(path, 96 * 1024);
    defer std.testing.allocator.free(payload);
}

test "phase9 runtime pilot survey keeps the cross-family parity note and rerun routes explicit" {
    const parity_note = try readRepoFileAlloc(
        "Documentation/zigux/phase9-first-loadable-runtime-module-parity.md",
        32 * 1024,
    );
    defer std.testing.allocator.free(parity_note);

    const sequencing_note = try readRepoFileAlloc(
        "Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md",
        48 * 1024,
    );
    defer std.testing.allocator.free(sequencing_note);

    const phase9_build = try readRepoFileAlloc("zigux/tests/phase9_build.zig", 64 * 1024);
    defer std.testing.allocator.free(phase9_build);

    const makefile = try readRepoFileAlloc("zigux/Makefile", 96 * 1024);
    defer std.testing.allocator.free(makefile);

    try expectContains(parity_note, "`PHASE9_STATUS=active`");
    try expectContains(parity_note, "`PHASE9_SLICE=first-loadable-runtime-module-parity`");
    try expectContains(parity_note, "`PHASE9_LANE_KEY=P9-L01`");
    try expectContains(
        parity_note,
        "first loadable Zigux runtime modules with selftest hooks and runtime module lifecycle parity",
    );
    try expectContains(
        parity_note,
        "must not claim shipped cross-family loader parity, shipped runtime-loader handoff parity, or shipped end-to-end module lifecycle parity",
    );
    try expectContains(parity_note, "`samples/zigux/runtime_atomic64_loader.zig`");
    try expectContains(parity_note, "`samples/zigux/runtime_kretprobe_loader.zig`");
    try expectContains(parity_note, "`samples/zigux/runtime_bitmap_direct_init_contract.zig`");

    try expectContains(sequencing_note, "`zigux/tests/phase9_build.zig`");
    try expectContains(sequencing_note, "`zigux/kernel/runtime_loader_command_env_boundary_guard.zig`");
    try expectContains(sequencing_note, "`samples/zigux/runtime_trace_events.zig`");
    try expectContains(sequencing_note, "`samples/zigux/runtime_bitmap_cold_stage_guard.zig`");

    try expectContains(phase9_build, "\"phase9-runtime-atomic64-tests\"");
    try expectContains(phase9_build, "\"phase9-runtime-bitmap-tests\"");
    try expectContains(phase9_build, "\"phase9-runtime-loader-shared-tests\"");
    try expectContains(phase9_build, "\"phase9-runtime-trace-events-tests\"");
    try expectContains(phase9_build, "\"phase9-runtime-kretprobe-tests\"");
    try expectContains(phase9_build, "\"phase9-first-loadable-runtime-module-parity-tests\"");

    try expectContains(makefile, "phase9-runtime-atomic64-test:");
    try expectContains(makefile, "phase9-runtime-bitmap-test:");
    try expectContains(makefile, "phase9-runtime-loader-shared-test:");
    try expectContains(makefile, "phase9-runtime-trace-events-test:");
    try expectContains(makefile, "phase9-runtime-kretprobe-test:");
    try expectContains(makefile, "phase9-first-loadable-runtime-module-parity-test:");
    try expectContains(
        makefile,
        "phase9-test: phase9-runtime-atomic64-test phase9-runtime-bitmap-test phase9-runtime-loader-shared-test phase9-runtime-trace-events-test phase9-runtime-kretprobe-test phase9-first-loadable-runtime-module-parity-test",
    );
}

test "phase9 runtime pilot survey keeps the family-local survey witnesses and manifests readable" {
    const parity_survey = try readRepoFileAlloc(
        "zigux/tests/runtime_first_loadable_parity_survey.zig",
        24 * 1024,
    );
    defer std.testing.allocator.free(parity_survey);

    const bitmap_survey = try readRepoFileAlloc("zigux/tests/runtime_bitmap_survey.zig", 96 * 1024);
    defer std.testing.allocator.free(bitmap_survey);

    const trace_events_survey = try readRepoFileAlloc(
        "zigux/tests/runtime_trace_events_survey.zig",
        96 * 1024,
    );
    defer std.testing.allocator.free(trace_events_survey);

    const kretprobe_survey = try readRepoFileAlloc(
        "zigux/tests/runtime_kretprobe_survey.zig",
        96 * 1024,
    );
    defer std.testing.allocator.free(kretprobe_survey);

    const atomic64_manifest = try readRepoFileAlloc(
        "zigux/tests/runtime_atomic64_manifest.json",
        32 * 1024,
    );
    defer std.testing.allocator.free(atomic64_manifest);

    try expectContains(
        parity_survey,
        "returned atomic64 and kretprobe direct packets with their family-local loader companions",
    );
    try expectContains(parity_survey, "must not claim shipped cross-family loader parity");

    try expectContains(bitmap_survey, "\"phase9-runtime-bitmap-tests\"");
    try expectContains(bitmap_survey, "\"lane_key\": \"P9-L08\"");
    try expectContains(
        bitmap_survey,
        "loadable Phase 9 runtime bitmap pilot module parity",
    );

    try expectContains(trace_events_survey, "\"P9-L12\"");
    try expectContains(trace_events_survey, "\"phase9-runtime-loader-shared-test\"");
    try expectContains(trace_events_survey, ".provides_selftest_hook = true");

    try expectContains(kretprobe_survey, "\"P9-L13\"");
    try expectContains(kretprobe_survey, "\"phase9-runtime-kretprobe-tests\"");
    try expectContains(
        kretprobe_survey,
        "runtime kretprobe loader keeps initialized-stage shared contract plans explicit",
    );

    try expectContains(atomic64_manifest, "\"phase\": \"Phase 9\"");
    try expectContains(atomic64_manifest, "\"validation_entrypoint\"");

    inline for (present_phase9_files) |path| {
        try expectPresent(path);
    }
}
