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
        .limited(20 * 1024),
    );
    defer std.testing.allocator.free(sample_root_readme);

    const slice_note = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase7-string-helpers-slice.md",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(slice_note);

    const current_master_sample_root_files = [_][]const u8{
        "`samples/zigux/README.md`",
        "`samples/zigux/bytestream_fifo.zig`",
        "`samples/zigux/bytestream_fifo_window_contract.zig`",
        "`samples/zigux/kobject_example.zig`",
        "`samples/zigux/kobject_example_attr_group_contract.zig`",
        "`samples/zigux/kretprobe_example.zig`",
        "`samples/zigux/kretprobe_example_instance_budget_contract.zig`",
        "`samples/zigux/trace_events_sample.zig`",
        "`samples/zigux/trace_events_callback_focus_contract.zig`",
        "`samples/zigux/trace_events_string_formatting_sample.zig`",
        "`samples/zigux/runtime_atomic64.zig`",
        "`samples/zigux/runtime_bitmap.zig`",
        "`samples/zigux/runtime_bitmap_cold_stage_guard.zig`",
        "`samples/zigux/runtime_bitmap_loader.zig`",
        "`samples/zigux/runtime_bitmap_top_bit_contract.zig`",
        "`samples/zigux/runtime_trace_events.zig`",
        "`samples/zigux/runtime_trace_events_exit_rollback_guard.zig`",
        "`samples/zigux/runtime_trace_events_unregistered_gate.zig`",
        "`samples/zigux/runtime_trace_events_registration_reentry_gate.zig`",
        "`samples/zigux/runtime_trace_events_reinit_rollback_guard.zig`",
        "`samples/zigux/runtime_trace_events_reinit_reexit_guard.zig`",
    };
    for (current_master_sample_root_files) |path| {
        try expectContains(sample_root_readme, path);
    }

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
        "Fresh mixed readback on 2026-05-25 confirmed these current sample-root reminder-packet files on `master`:",
        "Current `master` keeps the bytestream sample-root packet on the approved anchor through `samples/zigux/bytestream_fifo.zig`, while `samples/zigux/bytestream_fifo_window_contract.zig` stays a bounded companion inside the same approved anchor rather than a fifth sample family.",
        "Current `master` keeps the kobject sample-root packet through `samples/zigux/kobject_example.zig`, while `samples/zigux/kobject_example_attr_group_contract.zig` stays a bounded companion inside the same approved anchor rather than a fifth sample family.",
        "Current `master` keeps the kretprobe sample-root packet through `samples/zigux/kretprobe_example.zig`, while `samples/zigux/kretprobe_example_instance_budget_contract.zig` stays a bounded companion inside the same approved anchor rather than a fifth sample family.",
        "For the trace-events anchor, current `master` keeps the direct non-runtime evidence split between the broader companion `samples/zigux/trace_events_sample.zig`, the callback-focus contract `samples/zigux/trace_events_callback_focus_contract.zig`, the bounded formatting companion at `samples/zigux/trace_events_string_formatting_sample.zig`, and the shared reminder packet carried by `Documentation/zigux/phase5-trace-events-approved-idiom-gap.md`, `Documentation/zigux/phase5-trace-events-sample-survey.md`, `Documentation/zigux/phase5-sample-review-guide.md`, `Documentation/zigux/phase5-sample-lane-sequencing.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md`.",
        "Keep those trace-events files tied to the same approved anchor rather than as proof that string helpers became a fifth Phase 5 sample family.",
        "Keep the shared `zigux/tests/phase5_build.zig` route framed as companion evidence rather than direct authenticated proof.",
        "Current `master` still ships no `samples/zigux/*bitmap*` Phase 5 reference sample. Keep the returned runtime bitmap files framed only as separate Phase 9 runtime-pilot evidence.",
        "Separate helper-backed sample packet",
        "`samples/zigux/string_helpers_sample.zig`",
        "Treat it as a bounded Phase 7 string-helper replay, not a fifth Phase 5 reference anchor.",
        "Review that packet through `Documentation/zigux/phase7-string-helpers-slice.md`, `zigux/tests/phase7_string_helpers_sample_manifest.json`, `zigux/tests/phase7_string_helpers_sample_survey.zig`, and `zigux/tests/phase7_build.zig`.",
        "Keep the sample tied to the shared Phase 7 helper lane instead of treating it as a new standalone sample family.",
        "Current `master` still ships no standalone `samples/zigux/*cmdline*`, `samples/zigux/*argv*`, or `samples/zigux/*rbtree*` Phase 5 reference sample.",
        "Current `master` does carry one bounded `*string*` and `*format*` companion through `samples/zigux/trace_events_string_formatting_sample.zig`, but keep it tied to the non-runtime `trace_events` anchor and its selected-string plus `iter=%d` formatting cue instead of treating it as standalone string-helper delivery.",
        "Phase 9 runtime pilot family",
        "`samples/zigux/runtime_atomic64.zig`",
        "`samples/zigux/runtime_bitmap.zig`",
        "`samples/zigux/runtime_bitmap_cold_stage_guard.zig`",
        "`samples/zigux/runtime_bitmap_loader.zig`",
        "`samples/zigux/runtime_bitmap_top_bit_contract.zig`",
        "`samples/zigux/runtime_trace_events_reinit_rollback_guard.zig`",
        "`samples/zigux/runtime_trace_events_reinit_reexit_guard.zig`",
        "Keep those files in the separate Phase 9 runtime packet instead of counting them as extra Phase 5 samples.",
    };
    for (sample_root_markers) |marker| {
        try expectContains(sample_root_readme, marker);
    }
    try expectExactCount(sample_root_readme, "Separate helper-backed sample packet", 1);
    try expectExactCount(sample_root_readme, "`samples/zigux/string_helpers_sample.zig`", 1);

    const slice_markers = [_][]const u8{
        "This is intentionally not a Phase 5 `samples/zigux/` reference-sample lane.",
        "The four approved Phase 5 anchors remain the bounded bytestream FIFO, kobject, kretprobe, and trace-events sample packets.",
        "The bounded sample replay added on this draft branch exists only to keep the landed helper contract reviewable through the shared Phase 7 lane, without recasting string helpers as a fifth Phase 5 sample family.",
        "The manifest-backed `zigux/tests/phase7_string_helpers_sample_survey.zig` gate so the helper, shared fixtures, sample replay, and slice note stay aligned in one reviewable packet",
        "The dedicated no-string-sample boundary packet in `samples/zigux/README.md` plus `zigux/tests/phase7_string_helpers_sample_boundary.zig` keeps the helper-backed replay explicit without recasting it as a fifth Phase 5 anchor.",
    };
    for (slice_markers) |marker| {
        try expectContains(slice_note, marker);
    }
    try expectExactCount(slice_note, "This is intentionally not a Phase 5 `samples/zigux/` reference-sample lane.", 1);
}
