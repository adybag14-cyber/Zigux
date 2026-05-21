const std = @import("std");

const present_bitmap_family_files = [_][]const u8{
    "Documentation/zigux/phase9-runtime-bitmap-survey.md",
    "Documentation/zigux/phase9-runtime-bitmap-module-slice.md",
    "zigux/tests/runtime_bitmap_manifest.json",
    "zigux/tests/runtime_bitmap_survey.zig",
    "zigux/tests/phase9_build.zig",
    "samples/zigux/runtime_bitmap.zig",
    "samples/zigux/runtime_bitmap_loader.zig",
    "samples/zigux/runtime_bitmap_top_bit_contract.zig",
};

const missing_bitmap_family_files = [_][]const u8{
    "zigux/tests/runtime_bitmap_module.zig",
    "zigux/tests/runtime_bitmap_diff.zig",
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

fn expectNotContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

fn expectPresent(path: []const u8) !void {
    const payload = try readRepoFileAlloc(path, 64 * 1024);
    defer std.testing.allocator.free(payload);
}

fn expectMissing(path: []const u8) !void {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    _ = std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        path,
        std.testing.allocator,
        .limited(8 * 1024),
    ) catch |err| switch (err) {
        error.FileNotFound => return,
        else => return err,
    };
    return error.UnexpectedVisibleBitmapFamilyFile;
}

test "phase9 runtime bitmap survey gate matches the manifest-backed partial bitmap packet" {
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

    const manifest = try readRepoFileAlloc(
        "zigux/tests/runtime_bitmap_manifest.json",
        32 * 1024,
    );
    defer std.testing.allocator.free(manifest);

    const phase9_build = try readRepoFileAlloc(
        "zigux/tests/phase9_build.zig",
        32 * 1024,
    );
    defer std.testing.allocator.free(phase9_build);

    const sample_file = try readRepoFileAlloc(
        "samples/zigux/runtime_bitmap.zig",
        64 * 1024,
    );
    defer std.testing.allocator.free(sample_file);

    const top_bit_file = try readRepoFileAlloc(
        "samples/zigux/runtime_bitmap_top_bit_contract.zig",
        32 * 1024,
    );
    defer std.testing.allocator.free(top_bit_file);

    try expectContains(survey_note, "`PHASE9_STATUS=active`");
    try expectContains(survey_note, "`PHASE9_LANE_KEY=P9-L08`");
    try expectContains(survey_note, "`PHASE9_SURVEYED_COMMIT=2026-05-21-runtime-bitmap-manifest-restored`");
    try expectContains(survey_note, "scope: partial reminder packet, direct sample proof, direct loader proof, manifest-backed ownership packet, top-bit companion proof, and blocked module-side follow-through only");
    try expectContains(survey_note, "trusted current-tree contents reads on 2026-05-21 do materialize");
    try expectContains(survey_note, "`zigux/tests/runtime_bitmap_manifest.json`");
    try expectContains(survey_note, "the same trusted read path still returns missing for `zigux/tests/runtime_bitmap_module.zig` and `zigux/tests/runtime_bitmap_diff.zig`");
    try expectContains(survey_note, "the current runtime bitmap reminder packet is still `partial_packet_without_module_and_diff_follow_through`");
    try expectContains(survey_note, "manifest-backed ownership packet");
    try expectNotContains(survey_note, "and `zigux/tests/runtime_bitmap_manifest.json`");

    try expectContains(module_slice_note, "`PHASE9_SLICE=runtime-bitmap-partial-slice`");
    try expectContains(module_slice_note, "`PHASE9_SURVEYED_COMMIT=2026-05-21-runtime-bitmap-manifest-restored`");
    try expectContains(module_slice_note, "scope: partial runtime bitmap reminder packet, direct sample proof, direct loader proof, manifest-backed ownership packet, top-bit companion proof, bounded build-bundle vocabulary, and no broader shared runtime-loader claim");
    try expectContains(module_slice_note, "## Current visible slice");
    try expectContains(module_slice_note, "`zigux/tests/runtime_bitmap_manifest.json`");
    try expectContains(module_slice_note, "## Repo-reality gaps inside the bitmap family");
    try expectContains(module_slice_note, "`zigux/tests/runtime_bitmap_module.zig`");
    try expectContains(module_slice_note, "`zigux/tests/runtime_bitmap_diff.zig`");

    try expectContains(manifest, "\"phase\": \"Phase 9\"");
    try expectContains(manifest, "\"lane_key\": \"P9-L08\"");
    try expectContains(manifest, "\"status\": \"active\"");
    try expectContains(manifest, "\"surveyed_commit\": \"2026-05-21-runtime-bitmap-manifest-restored\"");
    try expectContains(manifest, "\"sample_path\": \"samples/zigux/runtime_bitmap.zig\"");
    try expectContains(manifest, "\"loader_path\": \"samples/zigux/runtime_bitmap_loader.zig\"");
    try expectContains(manifest, "\"top_bit_path\": \"samples/zigux/runtime_bitmap_top_bit_contract.zig\"");
    try expectContains(manifest, "\"validation_entrypoint\": \"phase9-runtime-bitmap-tests\"");
    try expectContains(manifest, "\"descriptor_and_anchor\"");
    try expectContains(manifest, "\"loader_payload_and_invalid_payload\"");
    try expectContains(manifest, "\"top_bit_contract\"");
    try expectContains(manifest, "\"loadable runtime bitmap module parity\"");
    try expectContains(manifest, "\"shared runtime-loader command-name or argv-policy controls\"");

    try expectContains(phase9_build, "\"phase9-runtime-bitmap-sample-tests\"");
    try expectContains(phase9_build, "\"phase9-runtime-bitmap-loader-tests\"");
    try expectContains(phase9_build, "\"phase9-runtime-bitmap-survey-tests\"");
    try expectContains(phase9_build, "\"phase9-runtime-bitmap-top-bit-tests\"");
    try expectContains(phase9_build, "\"phase9-runtime-bitmap-tests\"");
    try expectNotContains(phase9_build, "\"phase9-runtime-bitmap-module-tests\"");
    try expectNotContains(phase9_build, "\"phase9-runtime-bitmap-diff-tests\"");

    try expectContains(sample_file, "pub const sample_review_focus = [_]SampleFocus");
    try expectContains(sample_file, "\"loadable runtime bitmap module parity\",");
    try expectContains(sample_file, "\"shared runtime-loader command-name or argv-policy controls\",");
    try expectContains(sample_file, ".top_bit_contract,");
    try expectContains(sample_file, "pub fn reviewContract() ReviewContract");
    try expectContains(sample_file, "pub fn runSelftest(self: *Self) !SelftestSummary");

    try expectContains(top_bit_file, "runtime bitmap sample keeps the highest valid bit explicit");
    try expectContains(top_bit_file, "runtime bitmap sample keeps top-bit lifecycle mutation explicit");
    try expectContains(top_bit_file, "runtime bitmap sample rejects exited top-bit source copies without disturbing the target sample leg");
    try expectContains(top_bit_file, "runtime bitmap sample rejects cold top-bit source copies without disturbing the target sample leg");
    try expectContains(top_bit_file, "runtime bitmap sample rejects copy reentry after target exit without disturbing either sample leg");
    try expectContains(top_bit_file, "runtime bitmap sample copies selftest-complete top-bit state into an initialized target without disturbing the source sample leg");

    inline for (present_bitmap_family_files) |path| {
        try expectPresent(path);
    }
    inline for (missing_bitmap_family_files) |path| {
        try expectMissing(path);
    }
}
