const std = @import("std");

const returned_bitmap_family_files = [_][]const u8{
    "samples/zigux/runtime_bitmap.zig",
    "samples/zigux/runtime_bitmap_loader.zig",
    "samples/zigux/runtime_bitmap_top_bit_contract.zig",
    "zigux/tests/runtime_bitmap_module.zig",
    "zigux/tests/runtime_bitmap_diff.zig",
    "zigux/tests/runtime_bitmap_manifest.json",
};

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectVisible(path: []const u8) !void {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();
    const payload = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        path,
        std.testing.allocator,
        .limited(8 * 1024),
    );
    defer std.testing.allocator.free(payload);
}

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

test "phase 9 runtime bitmap survey gate matches the returned bitmap packet" {
    const survey_note = try readRepoFileAlloc(
        "Documentation/zigux/phase9-runtime-bitmap-survey.md",
        32 * 1024,
    );
    defer std.testing.allocator.free(survey_note);

    const module_slice_note = try readRepoFileAlloc(
        "Documentation/zigux/phase9-runtime-bitmap-module-slice.md",
        32 * 1024,
    );
    defer std.testing.allocator.free(module_slice_note);

    const phase9_build = try readRepoFileAlloc(
        "zigux/tests/phase9_build.zig",
        32 * 1024,
    );
    defer std.testing.allocator.free(phase9_build);

    try expectContains(survey_note, "`PHASE9_STATUS=active`");
    try expectContains(survey_note, "`PHASE9_LANE_KEY=P9-L08`");
    try expectContains(survey_note, "fresh public-tree reread on 2026-05-20 reconfirms");
    try expectContains(survey_note, "`Documentation/zigux/phase9-runtime-bitmap-module-slice.md`");
    try expectContains(survey_note, "`samples/zigux/runtime_bitmap_loader.zig`");
    try expectContains(survey_note, "`zigux/tests/runtime_bitmap_manifest.json`");
    try expectContains(survey_note, "returned runtime bitmap packet");
    try expectContains(survey_note, "broader shared runtime-loader packet returned");
    try expectContains(survey_note, "`zigux/tests/runtime_atomic64_diff.zig`");

    try expectContains(module_slice_note, "`PHASE9_SLICE=runtime-bitmap-returned-slice`");
    try expectContains(module_slice_note, "## Current returned slice");
    try expectContains(module_slice_note, "`samples/zigux/runtime_bitmap.zig`");
    try expectContains(module_slice_note, "`zigux/tests/runtime_bitmap_diff.zig`");
    try expectContains(module_slice_note, "`zigux/tests/runtime_bitmap_manifest.json`");
    try expectContains(module_slice_note, "broader shared runtime-loader substrate returned too");
    try expectContains(module_slice_note, "`broader shared runtime-loader substrate parity`");

    try expectContains(phase9_build, "\"phase9-runtime-atomic64-diff-tests\"");
    try expectContains(phase9_build, "\"phase9-runtime-bitmap-sample-tests\"");
    try expectContains(phase9_build, "\"phase9-runtime-bitmap-module-tests\"");
    try expectContains(phase9_build, "\"phase9-runtime-bitmap-diff-tests\"");
    try expectContains(phase9_build, "\"phase9-runtime-bitmap-loader-tests\"");
    try expectContains(phase9_build, "\"phase9-runtime-bitmap-survey-tests\"");
    try expectContains(phase9_build, "\"phase9-runtime-bitmap-top-bit-tests\"");
    try expectContains(phase9_build, "\"phase9-runtime-bitmap-tests\"");
    try std.testing.expect(std.mem.indexOf(u8, phase9_build, "\"phase9-runtime-loader-shared-tests\"") == null);

    inline for (returned_bitmap_family_files) |path| {
        try expectVisible(path);
    }
}
