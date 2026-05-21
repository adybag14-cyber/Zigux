const std = @import("std");

const present_bitmap_family_files = [_][]const u8{
    "Documentation/zigux/phase9-runtime-bitmap-survey.md",
    "Documentation/zigux/phase9-runtime-bitmap-module-slice.md",
    "zigux/tests/runtime_bitmap_survey.zig",
    "zigux/tests/phase9_build.zig",
    "samples/zigux/runtime_bitmap.zig",
    "samples/zigux/runtime_bitmap_loader.zig",
    "samples/zigux/runtime_bitmap_top_bit_contract.zig",
};

const missing_bitmap_family_files = [_][]const u8{
    "zigux/tests/runtime_bitmap_module.zig",
    "zigux/tests/runtime_bitmap_diff.zig",
    "zigux/tests/runtime_bitmap_manifest.json",
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

test "phase9 runtime bitmap survey gate matches the partial bitmap reminder packet" {
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
    try expectContains(survey_note, "`PHASE9_SURVEYED_COMMIT=2026-05-20-runtime-bitmap-loader-partial-return`");
    try expectContains(survey_note, "scope: partial reminder packet, direct sample proof, direct loader proof, top-bit companion proof, and blocked module-side follow-through only");
    try expectContains(survey_note, "trusted current-tree contents reads on 2026-05-20 do materialize");
    try expectContains(survey_note, "`samples/zigux/runtime_bitmap.zig`");
    try expectContains(survey_note, "`samples/zigux/runtime_bitmap_loader.zig`");
    try expectContains(survey_note, "`samples/zigux/runtime_bitmap_top_bit_contract.zig`");
    try expectContains(survey_note, "`zigux/tests/runtime_bitmap_module.zig`");
    try expectContains(survey_note, "`zigux/tests/runtime_bitmap_diff.zig`");
    try expectContains(survey_note, "`zigux/tests/runtime_bitmap_manifest.json`");
    try expectContains(survey_note, "live body now reruns the direct sample, loader, survey, and top-bit proofs");
    try expectContains(survey_note, "`partial_packet_without_loadable_runtime_substrate`");
    try expectNotContains(survey_note, "restored direct sample proof");
    try expectNotContains(survey_note, "restored top-bit companion proof");

    try expectContains(module_slice_note, "`PHASE9_SLICE=runtime-bitmap-partial-slice`");
    try expectContains(module_slice_note, "`PHASE9_SURVEYED_COMMIT=2026-05-20-runtime-bitmap-loader-partial-return`");
    try expectContains(module_slice_note, "scope: partial runtime bitmap reminder packet, direct sample proof, direct loader proof, top-bit companion proof, bounded build-bundle vocabulary, and no broader shared runtime-loader claim");
    try expectContains(module_slice_note, "## Current visible slice");
    try expectContains(module_slice_note, "## Repo-reality gaps inside the bitmap family");
    try expectContains(module_slice_note, "`samples/zigux/runtime_bitmap.zig`");
    try expectContains(module_slice_note, "`samples/zigux/runtime_bitmap_loader.zig`");
    try expectContains(module_slice_note, "`samples/zigux/runtime_bitmap_top_bit_contract.zig`");
    try expectContains(module_slice_note, "`zigux/tests/runtime_bitmap_manifest.json`");
    try expectContains(module_slice_note, "bundle now reruns the direct sample, loader, survey gate, and top-bit companion");
    try expectContains(module_slice_note, "broader shared runtime-loader substrate");
    try expectNotContains(module_slice_note, "restored direct sample proof");
    try expectNotContains(module_slice_note, "restored top-bit companion proof");

    try expectContains(phase9_build, "\"phase9-runtime-bitmap-sample-tests\"");
    try expectContains(phase9_build, "\"phase9-runtime-bitmap-loader-tests\"");
    try expectContains(phase9_build, "\"phase9-runtime-bitmap-survey-tests\"");
    try expectContains(phase9_build, "\"phase9-runtime-bitmap-top-bit-tests\"");
    try expectContains(phase9_build, "\"../../samples/zigux/runtime_bitmap.zig\"");
    try expectContains(phase9_build, "\"../../samples/zigux/runtime_bitmap_loader.zig\"");
    try expectContains(phase9_build, "\"runtime_bitmap_survey.zig\"");
    try expectContains(phase9_build, "\"../../samples/zigux/runtime_bitmap_top_bit_contract.zig\"");
    try expectContains(phase9_build, "\"Run the Phase 9 runtime bitmap sample, loader, survey, and top-bit tests.\"");
    try expectContains(phase9_build, "\"phase9-runtime-bitmap-tests\"");
    try expectNotContains(phase9_build, "\"phase9-runtime-bitmap-module-tests\"");
    try expectNotContains(phase9_build, "\"phase9-runtime-bitmap-diff-tests\"");
    try expectNotContains(phase9_build, "\"runtime_bitmap_module.zig\"");
    try expectNotContains(phase9_build, "\"runtime_bitmap_diff.zig\"");

    try expectContains(sample_file, "pub const sample_review_focus = [_]SampleFocus");
    try expectContains(sample_file, "pub const sample_review_non_goals = [_][]const u8{");
    try expectContains(sample_file, "\"loadable runtime bitmap module parity\",");
    try expectContains(sample_file, "\"shared runtime-loader command-name or argv-policy controls\",");
    try expectContains(sample_file, "\"real runtime execution through a live substrate\",");
    try expectContains(sample_file, ".requires_runtime_substrate = true,");
    try expectContains(sample_file, ".provides_selftest_hook = true,");
    try expectContains(sample_file, ".top_bit_contract,");
    try expectContains(sample_file, "pub fn reviewContract() ReviewContract");
    try expectContains(sample_file, "pub fn runSelftest(self: *Self) !SelftestSummary");
    try expectContains(top_bit_file, "runtime bitmap sample keeps the highest valid bit explicit");
    try expectContains(top_bit_file, "runtime bitmap sample keeps top-bit lifecycle mutation explicit");
    try expectContains(top_bit_file, "runtime bitmap sample rejects exited top-bit source copies without disturbing the target sample leg");
    try expectContains(top_bit_file, "runtime bitmap sample rejects cold top-bit source copies without disturbing the target sample leg");
    try expectContains(top_bit_file, "runtime bitmap sample rejects copy reentry after target exit without disturbing either sample leg");
    try expectContains(top_bit_file, "const top_bit = runtime_bitmap_sample.RuntimeBitmapSample.bitmap_nbits - 1;");
    try expectContains(top_bit_file, "try std.testing.expectEqualStrings(\"127\", direct_formatted);");
    try expectContains(top_bit_file, "try module.clearRange(top_bit, 1);");
    try expectContains(top_bit_file, "try module.setRange(top_bit, 1);");
    try expectContains(top_bit_file, "try std.testing.expectEqual(runtime_bitmap_sample.ModuleStage.exited, module.stage());");
    try expectContains(top_bit_file, "try std.testing.expectError(error.InvalidSourceLifecycle, target.copyFrom(&exited_source));");
    try expectContains(top_bit_file, "try std.testing.expectError(error.InvalidSourceLifecycle, target.copyFrom(&cold_source));");
    try expectContains(top_bit_file, "try std.testing.expectError(error.InvalidLifecycleTransition, target.copyFrom(&source));");
    try expectContains(top_bit_file, "try std.testing.expectEqual(source_before.first_set, source_after.first_set);");
    try expectContains(top_bit_file, "try std.testing.expectEqual(source_before.weight, source_after.weight);");
    try expectContains(top_bit_file, "try std.testing.expectEqual(target_before.first_set, target_after.first_set);");
    try expectContains(top_bit_file, "try std.testing.expectEqual(target_before.exit_runs, target_after.exit_runs);");

    inline for (present_bitmap_family_files) |path| {
        try expectPresent(path);
    }
    inline for (missing_bitmap_family_files) |path| {
        try expectMissing(path);
    }
}
