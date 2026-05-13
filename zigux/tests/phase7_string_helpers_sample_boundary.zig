const std = @import("std");

const expected_phase5_samples = [_][]const u8{
    "bytestream_fifo.zig",
    "kobject_example.zig",
    "kretprobe_example.zig",
    "trace_events_sample.zig",
};

const expected_runtime_samples = [_][]const u8{
    "runtime_atomic64.zig",
    "runtime_atomic64_loader.zig",
    "runtime_bitmap.zig",
    "runtime_bitmap_loader.zig",
    "runtime_bitmap_top_bit_contract.zig",
    "runtime_kretprobe.zig",
    "runtime_kretprobe_loader.zig",
    "runtime_trace_events.zig",
    "runtime_trace_events_loader.zig",
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

test "phase 7 string helper boundary keeps the exact current sample inventory and no string sample" {
    const io = std.testing.io;
    try std.testing.expectError(error.FileNotFound, std.Io.Dir.cwd().access(io, "samples/zigux/string_helpers_sample.zig", .{}));

    var dir = try std.Io.Dir.cwd().openDir(io, "samples/zigux", .{ .iterate = true });
    defer dir.close(io);

    var saw_string_file = false;
    var saw_unexpected_file = false;
    var total_zig_files: usize = 0;
    var phase5_count: usize = 0;
    var runtime_count: usize = 0;
    var phase5_seen = [_]bool{false} ** expected_phase5_samples.len;
    var runtime_seen = [_]bool{false} ** expected_runtime_samples.len;

    var iterator = dir.iterate();
    while (try iterator.next(io)) |entry| {
        if (entry.kind != .file) continue;
        if (!std.mem.endsWith(u8, entry.name, ".zig")) continue;

        total_zig_files += 1;

        if (std.mem.indexOf(u8, entry.name, "string") != null) {
            saw_string_file = true;
        }

        if (markSeen(entry.name, expected_phase5_samples[0..], phase5_seen[0..])) {
            phase5_count += 1;
            continue;
        }

        if (markSeen(entry.name, expected_runtime_samples[0..], runtime_seen[0..])) {
            runtime_count += 1;
            continue;
        }

        saw_unexpected_file = true;
    }

    try std.testing.expect(!saw_string_file);
    try std.testing.expect(!saw_unexpected_file);
    try std.testing.expectEqual(@as(usize, expected_phase5_samples.len + expected_runtime_samples.len), total_zig_files);
    try std.testing.expectEqual(@as(usize, expected_phase5_samples.len), phase5_count);
    try std.testing.expectEqual(@as(usize, expected_runtime_samples.len), runtime_count);

    for (phase5_seen) |seen| try std.testing.expect(seen);
    for (runtime_seen) |seen| try std.testing.expect(seen);
}

test "phase 7 sample root notes keep the exact parked no-sample boundaries explicit" {
    const allocator = std.testing.allocator;
    const readme = try readRepoFile(allocator, "samples/zigux/README.md");
    defer allocator.free(readme);

    for (expected_phase5_samples) |name| {
        try expectContains(readme, name);
    }
    try expectContains(readme, "current `master` still ships no `samples/zigux/*string*` Phase 5 reference sample;");
    try expectContains(readme, "treat any new `samples/zigux/*string*.zig` file as review-blocking");
    try expectContains(readme, "Documentation/zigux/phase7-string-helpers-slice.md");
    try expectContains(readme, "lib/string_helpers.zig");
    try expectContains(readme, "zigux/tests/phase7_build.zig");
    try expectContains(readme, "current `master` still ships no `samples/zigux/*cmdline*` Phase 5 reference sample;");
    try expectContains(readme, "Documentation/zigux/phase7-cmdline-slice.md");
    try expectContains(readme, "zigux/tests/phase7_cmdline.zig");
    try expectContains(readme, "zigux/tests/phase7_cmdline_survey.zig");
    try expectContains(readme, "current `master` still ships no `samples/zigux/*argv*` Phase 5 reference sample;");
    try expectContains(readme, "Documentation/zigux/phase7-argv-split-slice.md");
    try expectContains(readme, "zigux/tests/phase7_argv_split.zig");
    try expectContains(readme, "zigux/tests/phase7_argv_split_survey.zig");
    try expectContains(readme, "scripts/zigux/check-phase7-argv-split-packet.py");
    try expectContains(readme, "current `master` still ships no `samples/zigux/*rbtree*` Phase 5 reference sample;");
    try expectContains(readme, "Documentation/zigux/phase7-rbtree-slice.md");
    try expectContains(readme, "lib/rbtree.zig");
    try expectContains(readme, "zigux/tests/phase7_rbtree.zig");
    try expectContains(readme, "zigux/tests/phase7_rbtree_survey.zig");
    try expectContains(readme, "scripts/zigux/check-phase7-rbtree-parity.py");
    try expectContains(readme, "samples/zigux/runtime_bitmap_top_bit_contract.zig");

    try expectOccurrenceCount(readme, "current `master` still ships no `samples/zigux/*string*` Phase 5 reference sample;", 1);
    try expectOccurrenceCount(readme, "current `master` still ships no `samples/zigux/*cmdline*` Phase 5 reference sample;", 1);
    try expectOccurrenceCount(readme, "current `master` still ships no `samples/zigux/*argv*` Phase 5 reference sample;", 1);
    try expectOccurrenceCount(readme, "current `master` still ships no `samples/zigux/*rbtree*` Phase 5 reference sample;", 1);
    try expectOccurrenceCount(readme, "scripts/zigux/check-phase7-argv-split-packet.py", 1);
    try expectOccurrenceCount(readme, "scripts/zigux/check-phase7-rbtree-parity.py", 1);
}

test "phase 7 helper packet keeps the exact sample-boundary guard and Phase 5 build boundary wired" {
    const allocator = std.testing.allocator;

    const slice_note = try readRepoFile(allocator, "Documentation/zigux/phase7-string-helpers-slice.md");
    defer allocator.free(slice_note);
    try expectContains(slice_note, "zigux/tests/phase7_string_helpers_sample_boundary.zig");
    try expectContains(slice_note, "This is intentionally not a Phase 5 `samples/zigux/` reference-sample lane.");
    try expectContains(slice_note, "no `samples/zigux/*string*` Phase 5 reference sample is expected here;");
    try expectContains(slice_note, "keep stronger ownership and pointer discipline explicit through bounded C-string prefix helpers");
    try expectContains(slice_note, "destination-size accounting");
    try expectContains(slice_note, "Linux-style size rendering cues");
    try expectContains(slice_note, "one count-prefixed integer-array starter");
    try expectContains(slice_note, "zig build test --build-file zigux/tests/phase7_build.zig --summary all");
    try expectContains(slice_note, "keep integration with validation substrate explicit through `zigux/tests/phase7_build.zig`, the shared `zig build test --build-file zigux/tests/phase7_build.zig --summary all` replay, `zigux/tests/phase7_string_helpers_sample_boundary.zig`, `scripts/zigux/validate-phase7.py`, and `make -C zigux phase7`");

    const build_file = try readRepoFile(allocator, "zigux/tests/phase7_build.zig");
    defer allocator.free(build_file);
    try expectContains(build_file, "\"phase7_string_helpers_sample_boundary.zig\"");
    try expectContains(build_file, "\"phase7-string-helpers-sample-boundary-tests\"");
    try expectContains(build_file, "setCwd(b.path(\"../..\"))");

    const phase5_build = try readRepoFile(allocator, "zigux/tests/phase5_build.zig");
    defer allocator.free(phase5_build);
    try expectOccurrenceCount(phase5_build, "../../samples/zigux/", 4);
    try expectContains(phase5_build, "../../samples/zigux/bytestream_fifo.zig");
    try expectContains(phase5_build, "../../samples/zigux/kobject_example.zig");
    try expectContains(phase5_build, "../../samples/zigux/kretprobe_example.zig");
    try expectContains(phase5_build, "../../samples/zigux/trace_events_sample.zig");
    try expectNotContains(phase5_build, "string_helpers_sample.zig");
    try expectNotContains(phase5_build, "runtime_bitmap.zig");
    try expectNotContains(phase5_build, "runtime_trace_events.zig");

    const tests_readme = try readRepoFile(allocator, "zigux/tests/README.md");
    defer allocator.free(tests_readme);
    try expectContains(tests_readme, "zigux/tests/phase7_string_helpers_sample_boundary.zig");
    try expectContains(tests_readme, "the dedicated `zigux/tests/phase7_string_helpers_sample_boundary.zig` boundary replay");

    const scripts_readme = try readRepoFile(allocator, "scripts/zigux/README.md");
    defer allocator.free(scripts_readme);
    try expectContains(scripts_readme, "zigux/tests/phase7_string_helpers_sample_boundary.zig");
    try expectContains(scripts_readme, "current `master` also still ships no standalone `samples/zigux/*string*` Phase 5 reference sample");
    try expectNotContains(scripts_readme, "current `master` still ships no `samples/zigux/*string*` Phase 5 reference sample");
    try expectContains(scripts_readme, "there is no separate shared `check-phase7-build-inventory.py`, `phase7_build_inventory.json`, or broader packet-checker stack on `master`;");
}
