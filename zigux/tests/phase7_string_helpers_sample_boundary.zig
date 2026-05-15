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

fn readRepoFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(std.testing.io, path, allocator, .limited(256 * 1024));
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
        if (std.mem.indexOf(u8, entry.name, "string") != null) saw_string_file = true;

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

test "phase 7 string helper boundary keeps the lane-local helper packet aligned without claiming shared control surfaces" {
    const allocator = std.testing.allocator;
    const io = std.testing.io;

    try std.Io.Dir.cwd().access(io, "lib/string_helpers.zig", .{});
    try std.Io.Dir.cwd().access(io, "zigux/tests/phase7_string_helpers.zig", .{});
    try std.Io.Dir.cwd().access(io, "zigux/tests/phase7_string_helpers_survey.zig", .{});
    try std.Io.Dir.cwd().access(io, "zigux/tests/phase7_string_helpers_manifest.json", .{});

    const slice_note = try readRepoFile(allocator, "Documentation/zigux/phase7-string-helpers-slice.md");
    defer allocator.free(slice_note);
    try expectContains(slice_note, "PHASE7_STATUS=starter_landed");
    try expectContains(slice_note, "expanded starter packet");
    try expectContains(slice_note, "Current `master` still ships no `samples/zigux/*string*` Phase 5 reference sample");
    try expectNotContains(slice_note, "restored starter packet");
    try expectNotContains(slice_note, "missing both `lib/string_helpers.zig` and `zigux/tests/phase7_string_helpers.zig`");

    const helper = try readRepoFile(allocator, "lib/string_helpers.zig");
    defer allocator.free(helper);
    try expectContains(helper, "pub fn stringEscapeMem");
    try expectContains(helper, "pub fn stringEscapeStrAnyNp");
    try expectContains(helper, "pub fn memcpyAndPad");
    try expectContains(helper, "pub fn strreplace");

    const helper_tests = try readRepoFile(allocator, "zigux/tests/phase7_string_helpers.zig");
    defer allocator.free(helper_tests);
    try expectContains(helper_tests, "phase 7 string helpers starter escapes bounded memory across flag families and dictionary modes");
    try expectContains(helper_tests, "phase 7 string helpers starter pads bounded copies without reading past the provided source slice");
    try expectContains(helper_tests, "phase 7 string helpers starter replaces bytes only inside the exported c-string prefix");

    const survey = try readRepoFile(allocator, "zigux/tests/phase7_string_helpers_survey.zig");
    defer allocator.free(survey);
    try expectContains(survey, "phase 7 string helpers survey keeps the expanded starter packet truthful");
    try expectContains(survey, "zigux/tests/phase7_string_helpers_sample_boundary.zig");
    try expectNotContains(survey, "Documentation/zigux/review-checklist.md");
    try expectNotContains(survey, "Documentation/zigux/phase7-make-wrapper-selftest-alignment.md");
    try expectNotContains(survey, "zigux/tests/phase7_build.zig");

    const manifest = try readRepoFile(allocator, "zigux/tests/phase7_string_helpers_manifest.json");
    defer allocator.free(manifest);
    try expectContains(manifest, "\"current_master_state\": \"expanded_starter_packet\"");
    try expectContains(manifest, "\"zigux/tests/phase7_string_helpers_sample_boundary.zig\"");
    try expectContains(manifest, "\"zigux/tests/phase7_string_helpers_survey.zig\"");
    try expectNotContains(manifest, "missing_review_surfaces");
    try expectNotContains(manifest, "missing_on_master");
}
