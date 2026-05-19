const std = @import("std");

const ExactCheck = struct {
    id: []const u8,
    kind: []const u8,
    expected: []const u8,
};

const Manifest = struct {
    lane_key: []const u8,
    phase: []const u8,
    surveyed_commit: []const u8,
    anchor: []const u8,
    sample_path: []const u8,
    validation_entrypoint: []const u8,
    review_prompts: []const []const u8,
    exact_checks: []const ExactCheck,
    non_goals: []const []const u8,
};

fn isLowerHexCommitSha(value: []const u8) bool {
    if (value.len != 40) return false;
    for (value) |byte| {
        if (!std.ascii.isDigit(byte) and (byte < 'a' or byte > 'f')) return false;
    }
    return true;
}

fn findExactCheck(manifest: Manifest, id: []const u8) ?ExactCheck {
    for (manifest.exact_checks) |check| {
        if (std.mem.eql(u8, check.id, id)) return check;
    }
    return null;
}

test "phase 5 bytestream fifo manifest still records the bounded replay contract" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const manifest_json = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase5_bytestream_fifo_manifest.json",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(manifest_json);

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{});
    defer parsed.deinit();
    const manifest = parsed.value;

    try std.testing.expectEqualStrings("P5-L01", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 5", manifest.phase);
    try std.testing.expect(isLowerHexCommitSha(manifest.surveyed_commit));
    try std.testing.expectEqualStrings("samples/kfifo/bytestream-example.c", manifest.anchor);
    try std.testing.expectEqualStrings("samples/zigux/bytestream_fifo.zig", manifest.sample_path);
    try std.testing.expect(std.mem.indexOf(u8, manifest.validation_entrypoint, "phase5_build.zig") != null);
    try std.testing.expectEqual(@as(usize, 8), manifest.review_prompts.len);
    try std.testing.expectEqual(@as(usize, 16), manifest.exact_checks.len);
    try std.testing.expectEqual(@as(usize, 4), manifest.non_goals.len);
}

test "phase 5 bytestream fifo manifest keeps queue-shape wording aligned" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const manifest_json = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase5_bytestream_fifo_manifest.json",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(manifest_json);

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{});
    defer parsed.deinit();
    const manifest = parsed.value;

    const occupancy = findExactCheck(manifest, "occupancy-summary-boundary") orelse return error.MissingExactCheck;
    try std.testing.expect(std.mem.indexOf(u8, occupancy.expected, "queue_len=10, available=22, and wrapped=false") != null);
    try std.testing.expect(std.mem.indexOf(u8, occupancy.expected, "queue_len=32, available=0, and wrapped=true") != null);
    try std.testing.expect(std.mem.indexOf(u8, occupancy.expected, "queue_len=24, available=8, and wrapped=true") != null);
    try std.testing.expect(std.mem.indexOf(u8, occupancy.expected, "used=") == null);

    const writable = findExactCheck(manifest, "writable-span-boundary") orelse return error.MissingExactCheck;
    try std.testing.expect(std.mem.indexOf(u8, writable.expected, "tail_index=17, writable_count=22") != null);
    try std.testing.expect(std.mem.indexOf(u8, writable.expected, "tail_index=4, writable_count=0") != null);
    try std.testing.expect(std.mem.indexOf(u8, writable.expected, "tail_index=1, writable_count=8") != null);
    try std.testing.expect(std.mem.indexOf(u8, writable.expected, "total_available=") == null);
}

test "phase 5 bytestream fifo survey packet keeps direct sample-and-tests guidance explicit" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const manifest_json = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase5_bytestream_fifo_manifest.json",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(manifest_json);
    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{});
    defer parsed.deinit();
    const manifest = parsed.value;

    var lane_key_marker_buf: [64]u8 = undefined;
    const lane_key_marker = try std.fmt.bufPrint(
        lane_key_marker_buf[0..],
        "PHASE5_LANE_KEY={s}",
        .{manifest.lane_key},
    );

    const survey_note = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase5-kfifo-sample-survey.md",
        std.testing.allocator,
        .limited(64 * 1024),
    );
    defer std.testing.allocator.free(survey_note);

    const required_mentions = [_][]const u8{
        "PHASE5_STATUS=verified-direct-sample-and-tests-packet",
        "PHASE5_SLICE=kfifo-reference-sample-readback",
        "sample-plus-tests packet",
        "sample-root file currently carries three in-file self-checks",
        "four focused replay tests",
        "four survey-packet checks",
        "phase5_build.zig` route",
        "StorageBacking.embedded_fixed_buffer",
        "reviewContract().focus",
        "keep remaining-capacity, rollover, occupancy, and queue-shape cues explicit through `runRemainingCapacityReplay()`, `occupancySummary()`, `visibleSpanSummary()`, `writableSpanSummary()`, and `usesWrappedStorageWindow()`",
        "draining `\"hello\"` into a three-byte buffer yields `\"hel\"`",
        "authenticated GitHub contents reads in this environment still do not recover `zigux/tests/phase5_build.zig`",
        "current `master` still has no standalone `samples/zigux/*bitmap*` Phase 5 reference sample",
    };
    for (required_mentions) |needle| {
        try std.testing.expect(std.mem.indexOf(u8, survey_note, needle) != null);
    }

    try std.testing.expect(std.mem.indexOf(u8, survey_note, lane_key_marker) != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, manifest.surveyed_commit) == null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "/workspace/agent_files") == null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "samples/kfifo/bytestream-example.c") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "PHASE5_STATUS=parked") == null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "sample-root file currently carries one in-file self-check") == null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "passed all six in-file checks") == null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "still do not recover `zigux/tests/phase5_bytestream_fifo.zig`") == null);
}

test "phase 5 bytestream fifo survey note records the exact current check split" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const survey_note = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase5-kfifo-sample-survey.md",
        std.testing.allocator,
        .limited(64 * 1024),
    );
    defer std.testing.allocator.free(survey_note);

    const required_markers = [_][]const u8{
        "## Exact checks verified on 2026-05-18",
        "`samples/zigux/bytestream_fifo.zig` currently carries three in-file self-checks",
        "`zigux/tests/phase5_bytestream_fifo.zig` currently carries four focused replay tests",
        "`zigux/tests/phase5_bytestream_fifo_survey.zig` currently carries four survey-packet checks",
        "`initial_string_copy_count = 5`, `first_drain_count = 5`, `second_drain_count = 2`, and `requeue_count = 2`",
        "`runPreviewBoundaryReplay()` at snapshot prefix `{ 2, 3, 4, 5 }`",
        "wrapped `{ 28, 4 }` visible-span split",
        "`occupancySummary()` keeps that preview state explicit at `queue_len = 10`, `available = 22`, and `wrapped = false`",
        "`writableSpanSummary()` keeps the same preview boundary explicit at `tail_index = 17`, `writable_count = 22`, `first_window_len = 15`, `second_window_len = 7`, and `wraps = true`",
        "`runRemainingCapacityReplay()` with `available_after_hello = 27` and `available_after_partial_drain = 8`",
        "short-drain `\"hel\"` / `\"lo\"` helper boundary",
        "invalid post-exit replay rejection",
    };
    for (required_markers) |needle| {
        try std.testing.expect(std.mem.indexOf(u8, survey_note, needle) != null);
    }
}

test "phase 5 bytestream fifo survey note keeps the non-runtime ownership rule explicit" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const survey_note = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase5-kfifo-sample-survey.md",
        std.testing.allocator,
        .limited(64 * 1024),
    );
    defer std.testing.allocator.free(survey_note);

    const required_markers = [_][]const u8{
        "## Ownership rule",
        "`StorageBacking.embedded_fixed_buffer` is the only declared storage backing",
        "`init()` and `exit()` define the lifetime edges explicitly",
        "`reset()` clears queue contents without turning the sample into a runtime-owned object",
        "no procfs, user-copy, locking, or module-registration surface is claimed",
    };
    for (required_markers) |needle| {
        try std.testing.expect(std.mem.indexOf(u8, survey_note, needle) != null);
    }
}
