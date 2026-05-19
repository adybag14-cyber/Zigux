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
    try std.testing.expectError(
        error.FileNotFound,
        std.Io.Dir.cwd().readFileAlloc(
            io_instance.io(),
            path,
            std.testing.allocator,
            .limited(8 * 1024),
        ),
    );
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

test "phase 9 runtime bitmap survey gate matches the visible partial reminder packet" {
    const survey_note = try readRepoFileAlloc(
        "Documentation/zigux/phase9-runtime-bitmap-survey.md",
        32 * 1024,
    );
    defer std.testing.allocator.free(survey_note);

    const sequencing_note = try readRepoFileAlloc(
        "Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md",
        48 * 1024,
    );
    defer std.testing.allocator.free(sequencing_note);

    const phase9_build = try readRepoFileAlloc(
        "zigux/tests/phase9_build.zig",
        32 * 1024,
    );
    defer std.testing.allocator.free(phase9_build);

    try expectContains(survey_note, "`PHASE9_STATUS=active`");
    try expectContains(survey_note, "`PHASE9_LANE_KEY=P9-L08`");
    try expectContains(survey_note, "trusted current-tree contents reads on 2026-05-19 do materialize");
    try expectContains(survey_note, "`Documentation/zigux/phase9-runtime-bitmap-survey.md`");
    try expectContains(survey_note, "`Documentation/zigux/phase9-runtime-bitmap-module-slice.md`");
    try expectContains(survey_note, "`zigux/tests/runtime_bitmap_survey.zig`");
    try expectContains(survey_note, "`zigux/tests/phase9_build.zig`");
    try expectContains(survey_note, "the same trusted read path still returns missing for");
    try expectContains(survey_note, "`samples/zigux/runtime_bitmap.zig`");
    try expectContains(survey_note, "`samples/zigux/runtime_bitmap_loader.zig`");
    try expectContains(survey_note, "`samples/zigux/runtime_bitmap_top_bit_contract.zig`");
    try expectContains(survey_note, "`zigux/tests/runtime_bitmap_module.zig`");
    try expectContains(survey_note, "`zigux/tests/runtime_bitmap_diff.zig`");
    try expectContains(survey_note, "`zigux/tests/runtime_bitmap_manifest.json`");
    try expectContains(survey_note, "partial runtime bitmap reminder packet");
    try expectContains(survey_note, "Treat gates 2 and 3 as bounded reminder-bundle handles only");

    try expectContains(sequencing_note, "The runtime bitmap side is narrower than older shared reminders claimed.");
    try expectContains(sequencing_note, "direct authenticated reads do materialize `Documentation/zigux/phase9-runtime-bitmap-survey.md`");
    try expectContains(sequencing_note, "`zigux/tests/runtime_bitmap_survey.zig`");
    try expectContains(sequencing_note, "`zigux/tests/phase9_build.zig`");
    try expectContains(sequencing_note, "the same trusted read path still returns missing for `samples/zigux/runtime_bitmap.zig`");
    try expectContains(sequencing_note, "`samples/zigux/runtime_bitmap_loader.zig`");
    try expectContains(sequencing_note, "`samples/zigux/runtime_bitmap_top_bit_contract.zig`");
    try expectContains(sequencing_note, "`zigux/tests/runtime_bitmap_module.zig`");
    try expectContains(sequencing_note, "`zigux/tests/runtime_bitmap_diff.zig`");
    try expectContains(sequencing_note, "`zigux/tests/runtime_bitmap_manifest.json`");
    try expectContains(sequencing_note, "partial runtime bitmap reminder packet plus a bounded build bundle");

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
