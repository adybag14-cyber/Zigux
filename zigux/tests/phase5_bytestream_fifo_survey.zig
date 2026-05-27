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
    try std.testing.expectEqual(@as(usize, 9), manifest.review_prompts.len);
    try std.testing.expectEqual(@as(usize, 20), manifest.exact_checks.len);
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

    const visible_contract = findExactCheck(manifest, "window-contract-visible-shapes") orelse return error.MissingExactCheck;
    try std.testing.expect(std.mem.indexOf(u8, visible_contract.expected, "samples/zigux/bytestream_fifo_window_contract.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, visible_contract.expected, "head_index=7, tail_index=17, total_visible=10") != null);
    try std.testing.expect(std.mem.indexOf(u8, visible_contract.expected, "head_index=4, tail_index=4, total_visible=32") != null);
    try std.testing.expect(std.mem.indexOf(u8, visible_contract.expected, "head_index=9, tail_index=1, total_visible=24") != null);

    const writable = findExactCheck(manifest, "writable-span-boundary") orelse return error.MissingExactCheck;
    try std.testing.expect(std.mem.indexOf(u8, writable.expected, "tail_index=17, writable_count=22") != null);
    try std.testing.expect(std.mem.indexOf(u8, writable.expected, "tail_index=4, writable_count=0") != null);
    try std.testing.expect(std.mem.indexOf(u8, writable.expected, "tail_index=1, writable_count=8") != null);
    try std.testing.expect(std.mem.indexOf(u8, writable.expected, "total_available=") == null);

    const writable_contract = findExactCheck(manifest, "window-contract-writable-shapes") orelse return error.MissingExactCheck;
    try std.testing.expect(std.mem.indexOf(u8, writable_contract.expected, "samples/zigux/bytestream_fifo_window_contract.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, writable_contract.expected, "tail_index=17, writable_count=22") != null);
    try std.testing.expect(std.mem.indexOf(u8, writable_contract.expected, "tail_index=4, writable_count=0") != null);
    try std.testing.expect(std.mem.indexOf(u8, writable_contract.expected, "tail_index=1, writable_count=8") != null);
    try std.testing.expect(std.mem.indexOf(u8, writable_contract.expected, "preview_is_non_destructive") != null);
    try std.testing.expect(std.mem.indexOf(u8, writable_contract.expected, "visible_windows_never_exceed_two") != null);

    const checkpoint_lookup = findExactCheck(manifest, "window-contract-checkpoint-lookups") orelse return error.MissingExactCheck;
    try std.testing.expect(std.mem.indexOf(u8, checkpoint_lookup.expected, "checkpointName()") != null);
    try std.testing.expect(std.mem.indexOf(u8, checkpoint_lookup.expected, "visibleWindowForCheckpoint()") != null);
    try std.testing.expect(std.mem.indexOf(u8, checkpoint_lookup.expected, "writableWindowForCheckpoint()") != null);
    try std.testing.expect(std.mem.indexOf(u8, checkpoint_lookup.expected, "preview_after_skip_and_requeue") != null);
    try std.testing.expect(std.mem.indexOf(u8, checkpoint_lookup.expected, "partial_drain_after_wrap_refill") != null);

    const reinit = findExactCheck(manifest, "reinit-after-exit") orelse return error.MissingExactCheck;
    try std.testing.expect(std.mem.indexOf(u8, reinit.expected, "available() back at 32") != null);
    try std.testing.expect(std.mem.indexOf(u8, reinit.expected, "init_runs = 2 and exit_runs = 2") != null);
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
        "sample-root file currently carries four in-file self-checks",
        "`runReinitBoundaryReplay()` and its `init_runs` / `exit_runs` accounting",
        "five focused replay tests",
        "five survey-packet checks",
        "phase5_build.zig` route",
        "StorageBacking.embedded_fixed_buffer",
        "reviewContract().focus",
        "`checkpointName()`, `visibleWindowForCheckpoint()`, and `writableWindowForCheckpoint()`",
        "keep remaining-capacity, rollover, occupancy, and queue-shape cues explicit through `runRemainingCapacityReplay()`, `occupancySummary()`, `visibleSpanSummary()`, `writableSpanSummary()`, and `usesWrappedStorageWindow()`",
        "keep the direct `available()` helper explicit as the first remaining-capacity cue at cold, initialized, preview, wrapped, full, replay-complete, reset, and exited boundaries instead of leaving free-space review to derived queue-length math alone",
        "draining `\\\"hello\\\"` into a three-byte buffer yields `\\\"hel\\\"`",
        "partial `enqueueSlice()` truncation at the last two slots",
        "authenticated GitHub contents reads in this environment now recover `zigux/tests/phase5_build.zig` directly again",
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
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "sample-root file currently carries three in-file self-check") == null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "four focused replay tests") == null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "passed all six in-file checks") == null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "still do not recover `zigux/tests/phase5_bytestream_fifo.zig`") == null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "authenticated GitHub contents reads in this environment still do not recover `zigux/tests/phase5_build.zig`") == null);
}

test "phase 5 bytestream fifo survey note keeps exact direct rerun routes visible" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const survey_note = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase5-kfifo-sample-survey.md",
        std.testing.allocator,
        .limited(64 * 1024),
    );
    defer std.testing.allocator.free(survey_note);

    const direct_routes = [_][]const u8{
        "`zig test samples/zigux/bytestream_fifo.zig`",
        "`zig test --dep bytestream_fifo_sample -Mroot=zigux/tests/phase5_bytestream_fifo.zig -Mbytestream_fifo_sample=samples/zigux/bytestream_fifo.zig`",
        "`zig test zigux/tests/phase5_bytestream_fifo_survey.zig`",
        "`zig build test --build-file zigux/tests/phase5_build.zig --summary all`",
    };
    for (direct_routes) |needle| {
        try std.testing.expect(std.mem.indexOf(u8, survey_note, needle) != null);
    }
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
        "Fresh repo-first inspection on 2026-05-25 confirmed these same-lane facts:",
        "## Exact checks verified on 2026-05-25",
        "Fresh direct sample and tests readback on 2026-05-25 showed this exact packet on current `master`:",
        "`samples/zigux/bytestream_fifo.zig` currently carries four in-file self-checks",
        "the fixed-buffer storage backing",
        "the ten-item `reviewContract().focus` order",
        "`samples/zigux/bytestream_fifo_window_contract.zig` currently carries three direct companion checks",
        "`zigux/tests/phase5_bytestream_fifo.zig` currently carries five focused replay tests",
        "`zigux/tests/phase5_bytestream_fifo_survey.zig` currently carries five survey-packet checks",
        "`initial_string_copy_count = 5`, `first_drain_count = 5`, `second_drain_count = 2`, and `requeue_count = 2`",
        "`runPreviewBoundaryReplay()` at snapshot prefix `{ 2, 3, 4, 5 }`",
        "wrapped `{ 28, 4 }` visible-span split",
        "the reinit path through `runReinitBoundaryReplay()` with `init_runs_after_reinit = 2` and `exit_runs_after_second_exit = 2`",
        "`runPartialEnqueueBoundaryReplay()` with `requested_extra_len = 4`, `copied_extra_len = 2`, and `dropped_extra_len = 2`",
        "`occupancySummary()` keeps that preview state explicit at `queue_len = 10`, `available = 22`, and `wrapped = false`",
        "`writableSpanSummary()` keeps the same preview boundary explicit at `tail_index = 17`, `writable_count = 22`, `first_window_len = 15`, `second_window_len = 7`, and `wraps = true`",
        "`runRemainingCapacityReplay()` with `available_after_hello = 27` and `available_after_partial_drain = 8`",
        "`checkpointName()`, `visibleWindowForCheckpoint()`, and `writableWindowForCheckpoint()` still line up with the same preview, wrapped-full, and partial-drain checkpoints",
        "short-drain `\\\"hel\\\"` / `\\\"lo\\\"` helper boundary",
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
        "`runReinitBoundaryReplay()` keeps repeatable reuse explicit without promoting the sample into a runtime-owned registration surface",
        "no procfs, user-copy, locking, or module-registration surface is claimed",
    };
    for (required_markers) |needle| {
        try std.testing.expect(std.mem.indexOf(u8, survey_note, needle) != null);
    }
}
