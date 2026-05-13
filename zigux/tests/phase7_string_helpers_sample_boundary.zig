const std = @import("std");

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn countOccurrences(haystack: []const u8, needle: []const u8) usize {
    var total: usize = 0;
    var cursor: usize = 0;
    while (std.mem.indexOfPos(u8, haystack, cursor, needle)) |index| {
        total += 1;
        cursor = index + needle.len;
    }
    return total;
}

fn expectExactCount(haystack: []const u8, needle: []const u8, expected_count: usize) !void {
    try std.testing.expectEqual(expected_count, countOccurrences(haystack, needle));
}

test "phase 7 string helper sample boundary keeps the Phase 5 anchor set closed" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const sample_root_readme = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "samples/zigux/README.md",
        std.testing.allocator,
        .limited(16 * 1024),
    );
    defer std.testing.allocator.free(sample_root_readme);

    const slice_note = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase7-string-helpers-slice.md",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(slice_note);

    const phase5_anchors = [_][]const u8{
        "`samples/zigux/bytestream_fifo.zig`",
        "`samples/zigux/kobject_example.zig`",
        "`samples/zigux/kretprobe_example.zig`",
        "`samples/zigux/trace_events_sample.zig`",
    };
    for (phase5_anchors) |anchor| {
        try expectContains(sample_root_readme, anchor);
        try expectExactCount(sample_root_readme, anchor, 1);
    }

    const runtime_family = [_][]const u8{
        "`samples/zigux/runtime_atomic64.zig`",
        "`samples/zigux/runtime_atomic64_loader.zig`",
        "`samples/zigux/runtime_bitmap.zig`",
        "`samples/zigux/runtime_bitmap_loader.zig`",
        "`samples/zigux/runtime_bitmap_top_bit_contract.zig`",
        "`samples/zigux/runtime_kretprobe.zig`",
        "`samples/zigux/runtime_kretprobe_loader.zig`",
        "`samples/zigux/runtime_trace_events.zig`",
        "`samples/zigux/runtime_trace_events_loader.zig`",
    };
    for (runtime_family) |sample| {
        try expectContains(sample_root_readme, sample);
        try expectExactCount(sample_root_readme, sample, 1);
    }

    const sample_root_markers = [_][]const u8{
        "Current Phase 5 reference anchors",
        "Separate helper-backed sample packet",
        "`samples/zigux/string_helpers_sample.zig` is a bounded Phase 7 string-helper replay, not a fifth Phase 5 reference anchor",
        "review that packet through `Documentation/zigux/phase7-string-helpers-slice.md`, `zigux/tests/phase7_string_helpers_sample_manifest.json`, `zigux/tests/phase7_string_helpers_sample_survey.zig`, and `zigux/tests/phase7_build.zig`",
        "keep the sample tied to the shared Phase 7 helper lane instead of treating it as a new standalone sample family",
        "current `master` still ships no `samples/zigux/*cmdline*` Phase 5 reference sample; keep cmdline reviewability under the shared Phase 7 helper packet instead of counting it as a fifth Phase 5 sample",
        "current `master` still ships no `samples/zigux/*argv*` Phase 5 reference sample; keep `argv_split` reviewability under the shared Phase 7 helper packet instead of counting it as a fifth Phase 5 sample",
        "current `master` still ships no `samples/zigux/*rbtree*` Phase 5 reference sample; keep `rbtree` reviewability under the shared Phase 7 helper packet instead of counting it as a fifth Phase 5 sample",
        "later runtime follow-ons stay under the separate Phase 9 `samples/zigux/runtime_*` family and should not be counted as extra Phase 5 reference anchors",
        "Separate runtime pilot family",
        "the current readable `runtime_*` packet above stays in the separate Phase 9 runtime pilot family and is not extra Phase 5 anchor evidence",
    };
    for (sample_root_markers) |marker| {
        try expectContains(sample_root_readme, marker);
    }
    try expectExactCount(sample_root_readme, "Separate helper-backed sample packet", 1);
    try expectExactCount(sample_root_readme, "`samples/zigux/string_helpers_sample.zig` is a bounded Phase 7 string-helper replay, not a fifth Phase 5 reference anchor", 1);
    try expectExactCount(sample_root_readme, "keep the sample tied to the shared Phase 7 helper lane instead of treating it as a new standalone sample family", 1);
    try expectExactCount(sample_root_readme, "`samples/zigux/string_helpers_sample.zig`", 1);
    try expectExactCount(sample_root_readme, "`samples/zigux/runtime_bitmap_top_bit_contract.zig`", 1);

    const slice_markers = [_][]const u8{
        "This is intentionally not a Phase 5 `samples/zigux/` reference-sample lane.",
        "The four approved Phase 5 anchors remain the bounded bytestream FIFO, kobject, kretprobe, and trace-events sample packets.",
        "the bounded `samples/zigux/string_helpers_sample.zig` replay for descriptor ownership, lifecycle transitions, newline-tolerant matching, binary size rendering, compact no-space-no-bytes formatting, one exact-fit unescape destination proof, deterministic only-selected newline escaping, and append-selected newline hex escaping through the shared Phase 7 build",
        "the manifest-backed `zigux/tests/phase7_string_helpers_sample_survey.zig` gate so the helper, shared fixtures, sample replay, and slice note stay aligned in one reviewable packet after the added compact-format, exact-fit unescape boundary, only-selected newline escaping, and append-selected escape proofs",
        "the sample-facing note packet keeps the review route explicit for the draft branch while preserving the current `master` rule that string helpers still are not part of the frozen Phase 5 reference-sample set",
    };
    for (slice_markers) |marker| {
        try expectContains(slice_note, marker);
    }
    try expectExactCount(slice_note, "This is intentionally not a Phase 5 `samples/zigux/` reference-sample lane.", 1);
    try expectExactCount(slice_note, "`samples/zigux/string_helpers_sample.zig`", 1);
    try expectExactCount(slice_note, "`zigux/tests/phase7_string_helpers_sample_survey.zig`", 1);
}
