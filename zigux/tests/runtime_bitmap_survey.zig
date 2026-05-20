const std = @import("std");

const missing_bitmap_family_files = [_][]const u8{
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

fn expectMissing(path: []const u8) !void {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const payload = std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        path,
        std.testing.allocator,
        .limited(8 * 1024),
    ) catch |err| switch (err) {
        error.FileNotFound => return,
        else => return err,
    };
    defer std.testing.allocator.free(payload);
    return error.UnexpectedVisibleBitmapFamilyFile;
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

test "phase 9 runtime bitmap survey gate matches the partial bitmap reminder packet" {
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

    const sample_root_readme = try readRepoFileAlloc(
        "samples/zigux/README.md",
        64 * 1024,
    );
    defer std.testing.allocator.free(sample_root_readme);

    const phase9_build = try readRepoFileAlloc(
        "zigux/tests/phase9_build.zig",
        32 * 1024,
    );
    defer std.testing.allocator.free(phase9_build);

    try expectContains(survey_note, "`PHASE9_STATUS=active`");
    try expectContains(survey_note, "`PHASE9_LANE_KEY=P9-L08`");
    try expectContains(survey_note, "trusted current-tree contents reads on 2026-05-20 do materialize");
    try expectContains(survey_note, "`Documentation/zigux/phase9-runtime-bitmap-module-slice.md`");
    try expectContains(survey_note, "the same trusted read path still returns missing for");
    try expectContains(survey_note, "`samples/zigux/runtime_bitmap_loader.zig`");
    try expectContains(survey_note, "`zigux/tests/runtime_bitmap_manifest.json`");
    try expectContains(survey_note, "`partial_packet_without_loadable_runtime_substrate`");
    try expectContains(survey_note, "`zigux/tests/runtime_atomic64_diff.zig`");
    try expectContains(survey_note, "bounded reminder-bundle handles only");
    try expectContains(survey_note, "current `master` still ships no `samples/zigux/*bitmap*` Phase 5 reference sample");

    try expectContains(module_slice_note, "`PHASE9_SLICE=runtime-bitmap-partial-slice`");
    try expectContains(module_slice_note, "## Current visible slice");
    try expectContains(module_slice_note, "## Repo-reality gaps inside the bitmap family");
    try expectContains(module_slice_note, "`samples/zigux/runtime_bitmap.zig`");
    try expectContains(module_slice_note, "`zigux/tests/runtime_bitmap_diff.zig`");
    try expectContains(module_slice_note, "`zigux/tests/runtime_bitmap_manifest.json`");
    try expectContains(module_slice_note, "false proof that the broader shared runtime-loader substrate returned too");
    try expectContains(module_slice_note, "`partial_packet_without_loadable_runtime_substrate`");

    try expectContains(sample_root_readme, "Current `master` still ships no `samples/zigux/*bitmap*` Phase 5 reference sample");
    try expectContains(sample_root_readme, "* `*bitmap*`");
    try expectContains(sample_root_readme, "`samples/zigux/runtime_bitmap.zig`");
    try expectContains(sample_root_readme, "or as evidence that a fifth approved Phase 5 sample family landed here");

    try expectContains(phase9_build, "\"phase9-runtime-atomic64-diff-tests\"");
    try expectContains(phase9_build, "\"phase9-runtime-bitmap-sample-tests\"");
    try expectContains(phase9_build, "\"phase9-runtime-bitmap-module-tests\"");
    try expectContains(phase9_build, "\"phase9-runtime-bitmap-diff-tests\"");
    try expectContains(phase9_build, "\"phase9-runtime-bitmap-loader-tests\"");
    try expectContains(phase9_build, "\"phase9-runtime-bitmap-survey-tests\"");
    try expectContains(phase9_build, "\"phase9-runtime-bitmap-top-bit-tests\"");
    try expectContains(phase9_build, "\"phase9-runtime-bitmap-tests\"");
    try std.testing.expect(std.mem.indexOf(u8, phase9_build, "\"phase9-runtime-loader-shared-tests\"") == null);

    inline for (missing_bitmap_family_files) |path| {
        try expectMissing(path);
    }
}
