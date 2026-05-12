const std = @import("std");

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn readRepoFileAlloc(allocator: std.mem.Allocator, path: []const u8, max_bytes: usize) ![]u8 {
    var io_instance: std.Io.Threaded = .init(allocator, .{});
    defer io_instance.deinit();
    return try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        path,
        allocator,
        .limited(max_bytes),
    );
}

test "phase 9 runtime bitmap module gate keeps the shipped sample and loader packet explicit" {
    const runtime_bitmap_sample = try readRepoFileAlloc(
        std.testing.allocator,
        "samples/zigux/runtime_bitmap.zig",
        64 * 1024,
    );
    defer std.testing.allocator.free(runtime_bitmap_sample);

    const runtime_bitmap_loader = try readRepoFileAlloc(
        std.testing.allocator,
        "samples/zigux/runtime_bitmap_loader.zig",
        64 * 1024,
    );
    defer std.testing.allocator.free(runtime_bitmap_loader);

    const runtime_bitmap_top_bit = try readRepoFileAlloc(
        std.testing.allocator,
        "samples/zigux/runtime_bitmap_top_bit_contract.zig",
        32 * 1024,
    );
    defer std.testing.allocator.free(runtime_bitmap_top_bit);

    const runtime_bitmap_diff = try readRepoFileAlloc(
        std.testing.allocator,
        "zigux/tests/runtime_bitmap_diff.zig",
        32 * 1024,
    );
    defer std.testing.allocator.free(runtime_bitmap_diff);

    const module_slice = try readRepoFileAlloc(
        std.testing.allocator,
        "Documentation/zigux/phase9-runtime-bitmap-module-slice.md",
        32 * 1024,
    );
    defer std.testing.allocator.free(module_slice);

    const phase9_build = try readRepoFileAlloc(
        std.testing.allocator,
        "zigux/tests/phase9_build.zig",
        96 * 1024,
    );
    defer std.testing.allocator.free(phase9_build);

    try expectContains(runtime_bitmap_sample, "name = \"runtime_bitmap\"");
    try expectContains(runtime_bitmap_sample, "anchor = \"lib/test_bitmap.c\"");
    try expectContains(runtime_bitmap_sample, "requires_runtime_substrate = true");
    try expectContains(runtime_bitmap_sample, "provides_selftest_hook = true");
    try expectContains(runtime_bitmap_sample, "init_runs: usize = 0");
    try expectContains(runtime_bitmap_sample, "selftest_runs: usize = 0");
    try expectContains(runtime_bitmap_sample, "exit_runs: usize = 0");
    try expectContains(runtime_bitmap_sample, "pub fn copyFrom");
    try expectContains(runtime_bitmap_sample, "pub fn runSelftest");
    try expectContains(runtime_bitmap_sample, "pub fn exit");

    try expectContains(runtime_bitmap_loader, "allocator_handoff = .arena");
    try expectContains(runtime_bitmap_loader, "test \"runtime bitmap loader keeps initialized shared-request snapshots stable across later selftest activity\"");
    try expectContains(runtime_bitmap_loader, "test \"runtime bitmap loader bridges the shared request lifecycle without widening bitmap claims\"");
    try expectContains(runtime_bitmap_loader, "test \"runtime bitmap loader rejects shared-load-plan snapshot drift\"");

    try expectContains(runtime_bitmap_top_bit, "test \"runtime bitmap top-bit contract keeps the highest valid bit explicit\"");
    try expectContains(runtime_bitmap_top_bit, "test \"runtime bitmap top-bit contract keeps exit-path lifecycle parity explicit\"");

    try expectContains(runtime_bitmap_diff, "test \"runtime bitmap diff gate replays bounded lib/test_bitmap.c expectations\"");
    try expectContains(runtime_bitmap_diff, "test \"runtime bitmap diff gate keeps copy parity and cleared tail semantics explicit\"");

    try expectContains(module_slice, "`samples/zigux/runtime_bitmap.zig`");
    try expectContains(module_slice, "`samples/zigux/runtime_bitmap_loader.zig`");
    try expectContains(module_slice, "`samples/zigux/runtime_bitmap_top_bit_contract.zig`");
    try expectContains(module_slice, "`zigux/tests/runtime_bitmap_module.zig`");
    try expectContains(module_slice, "`zigux/tests/runtime_bitmap_diff.zig`");
    try expectContains(module_slice, "`zigux/tests/runtime_bitmap_survey.zig`");
    try expectContains(module_slice, "`zigux/tests/runtime_bitmap_manifest.json`");
    try expectContains(module_slice, "`zig build phase9-runtime-bitmap-tests --build-file zigux/tests/phase9_build.zig`");
    try expectContains(module_slice, "`zig build phase9-runtime-loader-shared-tests --build-file zigux/tests/phase9_build.zig`");
    try expectContains(module_slice, "The live runtime substrate is still missing");

    try expectContains(phase9_build, ".root_source_file = b.path(\"runtime_bitmap_module.zig\")");
    try expectContains(phase9_build, ".root_source_file = b.path(\"runtime_bitmap_diff.zig\")");
    try expectContains(phase9_build, ".root_source_file = b.path(\"runtime_bitmap_survey.zig\")");
    try expectContains(phase9_build, "\"phase9-runtime-bitmap-module-tests\"");
    try expectContains(phase9_build, "\"phase9-runtime-bitmap-diff-tests\"");
    try expectContains(phase9_build, "\"phase9-runtime-bitmap-survey-tests\"");
    try expectContains(phase9_build, "\"phase9-runtime-bitmap-top-bit-tests\"");
    try expectContains(phase9_build, "\"phase9-runtime-loader-shared-tests\"");
    try expectContains(phase9_build, "\"phase9-runtime-bitmap-tests\"");
}
