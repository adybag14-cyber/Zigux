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

    try expectContains(sample_root_readme, "`samples/zigux/README.md`");
    try expectExactCount(sample_root_readme, "`samples/zigux/README.md`", 1);
    try expectContains(sample_root_readme, "`samples/zigux/runtime_trace_events.zig`");
    try expectExactCount(sample_root_readme, "`samples/zigux/runtime_trace_events.zig`", 2);
    try expectContains(sample_root_readme, "`samples/zigux/runtime_trace_events_unregistered_gate.zig`");
    try expectExactCount(sample_root_readme, "`samples/zigux/runtime_trace_events_unregistered_gate.zig`", 2);
    try expectContains(sample_root_readme, "`samples/zigux/trace_events_string_formatting_sample.zig`");
    try expectExactCount(sample_root_readme, "`samples/zigux/trace_events_string_formatting_sample.zig`", 2);

    const phase5_linux_anchors = [_][]const u8{
        "`samples/kfifo/bytestream-example.c`",
        "`samples/kobject/kobject-example.c`",
        "`samples/kprobes/kretprobe_example.c`",
        "`samples/trace_events/trace-events-sample.c`",
    };
    for (phase5_linux_anchors) |anchor| {
        try expectContains(sample_root_readme, anchor);
        try expectExactCount(sample_root_readme, anchor, 1);
    }

    const sample_root_markers = [_][]const u8{
        "Current repo reality on `master`",
        "The Phase 5 roadmap still scopes the non-runtime sample lane to these four Linux anchors:",
        "Those four roadmap-backed anchors are not currently directly readable as sample-root files on current `master` through this route.",
        "Separate helper-backed sample packet",
        "`samples/zigux/string_helpers_sample.zig`",
        "Treat it as a bounded Phase 7 string-helper replay, not a fifth Phase 5 reference anchor.",
        "Review that packet through `Documentation/zigux/phase7-string-helpers-slice.md`, `zigux/tests/phase7_string_helpers_sample_manifest.json`, `zigux/tests/phase7_string_helpers_sample_survey.zig`, and `zigux/tests/phase7_build.zig`.",
        "Keep the sample tied to the shared Phase 7 helper lane instead of treating it as a new standalone sample family.",
        "Current `master` does carry one bounded `*string*` and `*format*` companion through `samples/zigux/trace_events_string_formatting_sample.zig`, but keep it tied to the non-runtime `trace-events` anchor and its selected-string plus `iter=%d` formatting cue instead of treating it as standalone string-helper delivery.",
        "Phase 9 runtime pilot family",
        "Keep those files in the separate Phase 9 runtime packet instead of counting them as extra Phase 5 samples.",
    };
    for (sample_root_markers) |marker| {
        try expectContains(sample_root_readme, marker);
    }
    try expectExactCount(sample_root_readme, "Separate helper-backed sample packet", 1);
    try expectExactCount(sample_root_readme, "`samples/zigux/string_helpers_sample.zig`", 1);
    try expectExactCount(sample_root_readme, "`samples/zigux/trace_events_string_formatting_sample.zig`", 2);

    const slice_markers = [_][]const u8{
        "This is intentionally not a Phase 5 `samples/zigux/` reference-sample lane.",
        "The four approved Phase 5 anchors remain the bounded bytestream FIFO, kobject, kretprobe, and trace-events sample packets.",
        "The bounded `samples/zigux/string_helpers_sample.zig` replay stays review-only evidence for the Phase 7 helper lane.",
        "The manifest-backed `zigux/tests/phase7_string_helpers_sample_survey.zig` gate keeps the helper, shared fixtures, sample replay, and slice note aligned in one reviewable packet.",
        "The sample-facing note packet keeps the review route explicit for the draft branch while preserving the current `master` rule that string helpers still are not part of the frozen Phase 5 reference-sample set.",
    };
    for (slice_markers) |marker| {
        try expectContains(slice_note, marker);
    }
    try expectExactCount(slice_note, "This is intentionally not a Phase 5 `samples/zigux/` reference-sample lane.", 1);
    try expectExactCount(slice_note, "`samples/zigux/string_helpers_sample.zig`", 1);
    try expectExactCount(slice_note, "`zigux/tests/phase7_string_helpers_sample_survey.zig`", 1);
}