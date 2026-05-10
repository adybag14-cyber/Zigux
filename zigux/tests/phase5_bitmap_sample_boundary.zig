const std = @import("std");

const expected_runtime_bitmap_samples = [_][]const u8{
    "runtime_bitmap.zig",
    "runtime_bitmap_loader.zig",
    "runtime_bitmap_top_bit_contract.zig",
};

const expected_phase5_samples = [_][]const u8{
    "bytestream_fifo.zig",
    "kobject_example.zig",
    "kretprobe_example.zig",
    "trace_events_sample.zig",
};

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectNotContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

fn expectOccurrenceCount(haystack: []const u8, needle: []const u8, expected_count: usize) !void {
    var count: usize = 0;
    var start: usize = 0;
    while (std.mem.indexOfPos(u8, haystack, start, needle)) |index| {
        count += 1;
        start = index + needle.len;
    }
    try std.testing.expectEqual(expected_count, count);
}

fn readRepoFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(std.testing.io, path, allocator, .limited(512 * 1024));
}

fn markSeen(name: []const u8, expected: []const []const u8, seen: []bool) bool {
    for (expected, 0..) |item, index| {
        if (std.mem.eql(u8, name, item)) {
            seen[index] = true;
            return true;
        }
    }
    return false;
}

test "phase 5 bitmap boundary keeps bitmap files out of the direct sample packet" {
    const io = std.testing.io;
    try std.testing.expectError(error.FileNotFound, std.Io.Dir.cwd().access(io, "samples/zigux/bitmap.zig", .{}));
    try std.testing.expectError(error.FileNotFound, std.Io.Dir.cwd().access(io, "samples/zigux/bitmap_sample.zig", .{}));

    var dir = try std.Io.Dir.cwd().openDir(io, "samples/zigux", .{ .iterate = true });
    defer dir.close(io);

    var bitmap_count: usize = 0;
    var runtime_bitmap_seen = [_]bool{false} ** expected_runtime_bitmap_samples.len;
    var iterator = dir.iterate();
    while (try iterator.next(io)) |entry| {
        if (entry.kind != .file) continue;
        if (!std.mem.endsWith(u8, entry.name, ".zig")) continue;
        if (std.mem.indexOf(u8, entry.name, "bitmap") == null) continue;

        bitmap_count += 1;
        try std.testing.expect(markSeen(entry.name, expected_runtime_bitmap_samples[0..], runtime_bitmap_seen[0..]));
    }

    try std.testing.expectEqual(@as(usize, expected_runtime_bitmap_samples.len), bitmap_count);
    for (runtime_bitmap_seen) |seen| try std.testing.expect(seen);
}

test "phase 5 bitmap boundary keeps the shared packet routing explicit" {
    const allocator = std.testing.allocator;

    const docs_root = try readRepoFile(allocator, "Documentation/zigux/README.md");
    defer allocator.free(docs_root);
    try expectContains(docs_root, "current `master` still ships no standalone `samples/zigux/*bitmap*` Phase 5 reference sample");
    try expectContains(docs_root, "tools/lib/bitmap.zig");
    try expectContains(docs_root, "Documentation/zigux/phase1-closure.md");
    try expectContains(docs_root, "Documentation/zigux/phase4-validation-matrix.md");
    try expectContains(docs_root, "samples/zigux/runtime_bitmap.zig");
    try expectContains(docs_root, "samples/zigux/runtime_bitmap_loader.zig");
    try expectContains(docs_root, "samples/zigux/runtime_bitmap_top_bit_contract.zig");
    try expectContains(docs_root, "zigux/tests/phase9_build.zig");
    try expectOccurrenceCount(docs_root, "current `master` still ships no standalone `samples/zigux/*bitmap*` Phase 5 reference sample", 1);

    const samples_root = try readRepoFile(allocator, "samples/zigux/README.md");
    defer allocator.free(samples_root);
    try expectContains(samples_root, "current `master` still ships no `samples/zigux/*bitmap*` Phase 5 reference sample;");
    try expectContains(samples_root, "tools/lib/bitmap.zig");
    try expectContains(samples_root, "Documentation/zigux/phase1-closure.md");
    try expectContains(samples_root, "Documentation/zigux/phase4-validation-matrix.md");
    try expectContains(samples_root, "separate runtime bitmap family stays under");
    try expectContains(samples_root, "samples/zigux/runtime_bitmap.zig");
    try expectContains(samples_root, "samples/zigux/runtime_bitmap_loader.zig");
    try expectContains(samples_root, "samples/zigux/runtime_bitmap_top_bit_contract.zig");
    try expectContains(samples_root, "zigux/tests/phase9_build.zig");
    try expectOccurrenceCount(samples_root, "current `master` still ships no `samples/zigux/*bitmap*` Phase 5 reference sample;", 1);

    const review_guide = try readRepoFile(allocator, "Documentation/zigux/phase5-sample-review-guide.md");
    defer allocator.free(review_guide);
    try expectContains(review_guide, "The four shipped Phase 5 samples are the whole current reference-sample packet; later `samples/zigux/runtime_*` files belong to Phase 9.");
    try expectContains(review_guide, "Current `master` still ships no standalone `samples/zigux/*string*`, `*cmdline*`, `*argv*`, `*rbtree*`, or direct `*bitmap*` Phase 5 reference sample.");
    try expectContains(review_guide, "Keep direct bitmap helper reviewability under `tools/lib/bitmap.zig`, `Documentation/zigux/phase1-closure.md`, and `Documentation/zigux/phase4-validation-matrix.md` instead of counting bitmap as a fifth Phase 5 sample.");
    try expectContains(review_guide, "Keep the separate runtime bitmap family under `Documentation/zigux/phase9-runtime-bitmap-survey.md`, `samples/zigux/runtime_bitmap.zig`, `samples/zigux/runtime_bitmap_loader.zig`, `samples/zigux/runtime_bitmap_top_bit_contract.zig`, `zigux/kernel/runtime_loader.zig`, `zigux/kernel/runtime_loader_contract.zig`, and `zigux/tests/phase9_build.zig` instead of treating bitmap as a shared Phase 5 approved idiom.");
    try expectOccurrenceCount(review_guide, "Current `master` still ships no standalone `samples/zigux/*string*`, `*cmdline*`, `*argv*`, `*rbtree*`, or direct `*bitmap*` Phase 5 reference sample.", 1);

    const checklist = try readRepoFile(allocator, "Documentation/zigux/review-checklist.md");
    defer allocator.free(checklist);
    try expectContains(checklist, "if the change touches the shared Phase 5 sample packet, do the docs still say clearly that there is no standalone `samples/zigux/*bitmap*` reference sample");
    try expectContains(checklist, "direct bitmap helper reviewability remains under `tools/lib/bitmap.zig`, `Documentation/zigux/phase1-closure.md`, and `Documentation/zigux/phase4-validation-matrix.md`");
    try expectContains(checklist, "samples/zigux/runtime_bitmap.zig");
    try expectContains(checklist, "samples/zigux/runtime_bitmap_loader.zig");
    try expectContains(checklist, "samples/zigux/runtime_bitmap_top_bit_contract.zig");
    try expectContains(checklist, "zigux/tests/phase9_build.zig");

    const tests_root = try readRepoFile(allocator, "zigux/tests/README.md");
    defer allocator.free(tests_root);
    try expectContains(tests_root, "current `master` still ships no standalone `samples/zigux/*bitmap*` Phase 5 reference sample");
    try expectContains(tests_root, "tools/lib/bitmap.zig");
    try expectContains(tests_root, "Documentation/zigux/phase1-closure.md");
    try expectContains(tests_root, "Documentation/zigux/phase4-validation-matrix.md");
    try expectContains(tests_root, "samples/zigux/runtime_bitmap.zig");
    try expectContains(tests_root, "samples/zigux/runtime_bitmap_loader.zig");
    try expectContains(tests_root, "samples/zigux/runtime_bitmap_top_bit_contract.zig");
}

test "phase 5 bitmap boundary keeps the shared build packet four-sample only" {
    const allocator = std.testing.allocator;

    const build_file = try readRepoFile(allocator, "zigux/tests/phase5_build.zig");
    defer allocator.free(build_file);

    try expectContains(build_file, "\"phase5_bitmap_sample_boundary.zig\"");
    try expectContains(build_file, "\"phase5-bitmap-sample-boundary-tests\"");
    try expectContains(build_file, "run_phase5_bitmap_sample_boundary_tests.step");
    try expectOccurrenceCount(build_file, "../../samples/zigux/", expected_phase5_samples.len);

    for (expected_phase5_samples) |sample_name| {
        var path_buf: [128]u8 = undefined;
        const path = try std.fmt.bufPrint(path_buf[0..], "../../samples/zigux/{s}", .{sample_name});
        try expectContains(build_file, path);
    }

    try expectNotContains(build_file, "../../samples/zigux/runtime_bitmap.zig");
    try expectNotContains(build_file, "../../samples/zigux/runtime_bitmap_loader.zig");
    try expectNotContains(build_file, "../../samples/zigux/runtime_bitmap_top_bit_contract.zig");
    try expectNotContains(build_file, "../../samples/zigux/bitmap.zig");
}
