const std = @import("std");

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

test "phase9 first-loadable parity note matches the surviving shared packet" {
    const parity_note = try readRepoFileAlloc(
        "../../Documentation/zigux/phase9-first-loadable-runtime-module-parity.md",
        32 * 1024,
    );
    defer std.testing.allocator.free(parity_note);

    const phase9_build = try readRepoFileAlloc(
        "phase9_build.zig",
        16 * 1024,
    );
    defer std.testing.allocator.free(phase9_build);

    try expectContains(parity_note, "`PHASE9_STATUS=active`");
    try expectContains(parity_note, "`PHASE9_LANE_KEY=P9-L02`");
    try expectContains(parity_note, "`Documentation/zigux/phase9-runtime-atomic64-survey.md`");
    try expectContains(parity_note, "`Documentation/zigux/phase9-runtime-atomic64-module-slice.md`");
    try expectContains(parity_note, "`zigux/tests/runtime_atomic64_module.zig`");
    try expectContains(parity_note, "`zigux/tests/runtime_atomic64_diff.zig`");
    try expectContains(parity_note, "`Documentation/zigux/phase9-runtime-bitmap-survey.md`");
    try expectContains(parity_note, "`Documentation/zigux/phase9-runtime-bitmap-module-slice.md`");
    try expectContains(parity_note, "`samples/zigux/runtime_bitmap.zig`");
    try expectContains(parity_note, "`samples/zigux/runtime_bitmap_top_bit_contract.zig`");
    try expectContains(parity_note, "`zigux/tests/runtime_bitmap_survey.zig`");
    try expectContains(parity_note, "`zigux/tests/phase9_build.zig`");
    try expectContains(parity_note, "`samples/zigux/runtime_atomic64.zig`");
    try expectContains(parity_note, "`samples/zigux/runtime_atomic64_loader.zig`");
    try expectContains(parity_note, "`zigux/tests/runtime_atomic64_survey.zig`");
    try expectContains(parity_note, "`zigux/tests/runtime_atomic64_manifest.json`");
    try expectContains(parity_note, "`samples/zigux/runtime_bitmap_loader.zig`");
    try expectContains(parity_note, "`zigux/tests/runtime_bitmap_module.zig`");
    try expectContains(parity_note, "`zigux/tests/runtime_bitmap_diff.zig`");
    try expectContains(parity_note, "`zigux/tests/runtime_bitmap_manifest.json`");
    try expectContains(parity_note, "`zigux/kernel/runtime_loader.zig`");
    try expectContains(parity_note, "`zigux/kernel/runtime_loader_contract.zig`");
    try expectContains(parity_note, "`phase9-runtime-atomic64-diff`");
    try expectContains(parity_note, "bounded bitmap sample, survey, and top-bit routes");
    try expectContains(parity_note, "does not prove a matched pair of first-loadable runtime modules");
    try expectContains(parity_note, "must not claim shipped cross-family loader parity");
    try expectContains(parity_note, "Leave `P9-L02` parked after this shared note refresh");

    try expectContains(phase9_build, "\"phase9-runtime-atomic64-diff\"");
    try expectContains(phase9_build, "\"phase9-runtime-bitmap-tests\"");
    try expectContains(phase9_build, "\"phase9-runtime-bitmap-sample-tests\"");
    try expectContains(phase9_build, "\"phase9-runtime-bitmap-survey-tests\"");
    try expectContains(phase9_build, "\"phase9-runtime-bitmap-top-bit-tests\"");
    try std.testing.expect(std.mem.indexOf(u8, phase9_build, "\"phase9-runtime-atomic64-sample-tests\"") == null);
    try std.testing.expect(std.mem.indexOf(u8, phase9_build, "\"phase9-runtime-atomic64-loader-tests\"") == null);
    try std.testing.expect(std.mem.indexOf(u8, phase9_build, "\"phase9-runtime-atomic64-module-tests\"") == null);
    try std.testing.expect(std.mem.indexOf(u8, phase9_build, "\"phase9-runtime-atomic64-survey-tests\"") == null);
    try std.testing.expect(std.mem.indexOf(u8, phase9_build, "\"phase9-runtime-bitmap-loader-tests\"") == null);
    try std.testing.expect(std.mem.indexOf(u8, phase9_build, "\"phase9-runtime-bitmap-module-tests\"") == null);
    try std.testing.expect(std.mem.indexOf(u8, phase9_build, "\"phase9-runtime-bitmap-diff-tests\"") == null);
    try std.testing.expect(std.mem.indexOf(u8, phase9_build, "\"phase9-runtime-loader-shared-tests\"") == null);
}
