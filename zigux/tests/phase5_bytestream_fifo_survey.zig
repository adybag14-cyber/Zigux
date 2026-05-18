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

test "phase 5 bytestream fifo manifest records the expanded bounded checks" {
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
    try std.testing.expectEqual(@as(usize, 17), manifest.exact_checks.len);
    try std.testing.expectEqual(@as(usize, 4), manifest.non_goals.len);

    var saw_descriptor_prompt = false;
    var saw_approved_idiom_prompt = false;
    var saw_split_readback_prompt = false;
    var saw_manifest_refresh_prompt = false;
    var saw_non_goal_prompt = false;

    for (manifest.review_prompts) |prompt| {
        try std.testing.expect(prompt.len > 0);
        if (std.mem.indexOf(u8, prompt, "requires_runtime_substrate false") != null) {
            saw_descriptor_prompt = true;
        }
        if (std.mem.indexOf(u8, prompt, "approved Phase 5 in-memory FIFO idiom") != null) {
            saw_approved_idiom_prompt = true;
        }
        if (std.mem.indexOf(u8, prompt, "public-tree-backed side of the current split-readback packet") != null) {
            saw_split_readback_prompt = true;
        }
        if (std.mem.indexOf(u8, prompt, "sample-behavior changes update the manifest-backed replay contract") != null) {
            saw_manifest_refresh_prompt = true;
        }
        if (std.mem.indexOf(u8, prompt, "procfs, user-copy, locking, and runtime registration out of scope") != null) {
            saw_non_goal_prompt = true;
        }
    }

    var saw_exact_sequence = false;
    var saw_capacity = false;
    var saw_preview_boundary = false;
    var saw_anchor_preview = false;
    var saw_remaining_capacity = false;
    var saw_occupancy_boundary = false;
    var saw_wrapped_storage = false;
    var saw_writable_span = false;
    var saw_snapshot = false;
    var saw_helper_boundary = false;
    var saw_short_drain_prefix = false;
    var saw_lifecycle = false;

    for (manifest.exact_checks, 0..) |check, i| {
        try std.testing.expect(check.id.len > 0);
        try std.testing.expect(check.kind.len > 0);
        try std.testing.expect(check.expected.len > 0);

        if (std.mem.eql(u8, check.id, "final-drain-sequence")) {
            saw_exact_sequence = true;
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "3,4,5,6,7,8,9,0,1,20") != null);
        }
        if (std.mem.eql(u8, check.id, "fill-to-capacity")) {
            saw_capacity = true;
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "20 through 42 inclusive") != null);
        }
        if (std.mem.eql(u8, check.id, "preview-truncation-boundary")) {
            saw_preview_boundary = true;
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "truncated preview stays non-destructive") != null);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "queue_len_after_preview at 10") != null);
        }
        if (std.mem.eql(u8, check.id, "anchor-preview-truncation-contract")) {
            saw_anchor_preview = true;
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "preview_len is 8") != null);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "preview_total_visible is 32") != null);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "preview_truncated is true") != null);
        }
        if (std.mem.eql(u8, check.id, "remaining-capacity")) {
            saw_remaining_capacity = true;
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "available() reports 32 at cold") != null);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "1 immediately after skip-at-capacity") != null);
        }
        if (std.mem.eql(u8, check.id, "occupancy-summary-boundary")) {
            saw_occupancy_boundary = true;
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "wrapped_window=true") != null);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "used=32, available=0") != null);
        }
        if (std.mem.eql(u8, check.id, "wrapped-storage-window-boundary")) {
            saw_wrapped_storage = true;
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "{31,1}") != null);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "preserving the wrapped {28,4} split") != null);
        }
        if (std.mem.eql(u8, check.id, "writable-span-boundary")) {
            saw_writable_span = true;
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "tail_index=17") != null);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "tail_index=4") != null);
        }
        if (std.mem.eql(u8, check.id, "non-destructive-snapshot")) {
            saw_snapshot = true;
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "without mutating queue state") != null);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "[3,4,5,6,7,8,9,0,1,20") != null);
        }
        if (std.mem.eql(u8, check.id, "bounded-helper-behavior")) {
            saw_helper_boundary = true;
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "empty enqueue copies 0 bytes") != null);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "skip-at-capacity returns 0") != null);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "pop-after-reset null") != null);
        }
        if (std.mem.eql(u8, check.id, "short-drain-prefix")) {
            saw_short_drain_prefix = true;
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "\"hel\"") != null);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "\"lo\"") != null);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "returns 0") != null);
        }
        if (std.mem.eql(u8, check.id, "lifecycle-boundary")) {
            saw_lifecycle = true;
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "requires init before replay") != null);
        }

        for (manifest.exact_checks[i + 1 ..]) |other| {
            try std.testing.expect(!std.mem.eql(u8, check.id, other.id));
        }
    }

    try std.testing.expect(saw_descriptor_prompt);
    try std.testing.expect(saw_approved_idiom_prompt);
    try std.testing.expect(saw_split_readback_prompt);
    try std.testing.expect(saw_manifest_refresh_prompt);
    try std.testing.expect(saw_non_goal_prompt);
    try std.testing.expect(saw_exact_sequence);
    try std.testing.expect(saw_capacity);
    try std.testing.expect(saw_preview_boundary);
    try std.testing.expect(saw_anchor_preview);
    try std.testing.expect(saw_remaining_capacity);
    try std.testing.expect(saw_occupancy_boundary);
    try std.testing.expect(saw_wrapped_storage);
    try std.testing.expect(saw_writable_span);
    try std.testing.expect(saw_snapshot);
    try std.testing.expect(saw_helper_boundary);
    try std.testing.expect(saw_short_drain_prefix);
    try std.testing.expect(saw_lifecycle);
    try std.testing.expect(std.mem.eql(u8, manifest.non_goals[0], "procfs parity"));
    try std.testing.expect(std.mem.eql(u8, manifest.non_goals[1], "kfifo_from_user or kfifo_to_user parity"));
}

test "phase 5 bytestream fifo survey packet keeps split-readback guidance explicit" {
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
        "PHASE5_STATUS=verified-split-readback-packet",
        "PHASE5_SLICE=kfifo-reference-sample-readback",
        "split across those two paths",
        "public-tree blob readback for `zigux/tests/phase5_bytestream_fifo.zig`",
        "public-tree blob readback for `zigux/tests/phase5_bytestream_fifo_manifest.json`",
        "public-tree blob readback for `zigux/tests/phase5_bytestream_fifo_survey.zig`",
        "public-tree blob readback for `zigux/tests/phase5_build.zig`",
        "StorageBacking.embedded_fixed_buffer",
        "visibleSpanSummary()",
        "usesWrappedStorageWindow()",
        "eight in-file `test` blocks on current `master`",
        "authenticated connector readback for those broader packet files still fails in this environment",
    };
    for (required_mentions) |needle| {
        try std.testing.expect(std.mem.indexOf(u8, survey_note, needle) != null);
    }

    try std.testing.expect(std.mem.indexOf(u8, survey_note, lane_key_marker) != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, manifest.surveyed_commit) != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "/workspace/agent_files") == null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "samples/kfifo/bytestream-example.c|PHASE5_LANE_KEY=P5-L01|PHASE5_SURVEYED_COMMIT=") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "PHASE5_STATUS=parked") == null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "PHASE5_SLICE=kfifo-reference-sample-starter") == null);
}

test "phase 5 bytestream fifo survey note records the short-drain helper contract" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const survey_note = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase5-kfifo-sample-survey.md",
        std.testing.allocator,
        .limited(64 * 1024),
    );
    defer std.testing.allocator.free(survey_note);

    try std.testing.expect(std.mem.indexOf(u8, survey_note, "draining a three-byte buffer leaves `\"lo\"` queued") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "draining `\"hello\"` into a three-byte buffer leaves `\"lo\"` queued") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "drain on an empty queue returns `0`") != null);
}

test "phase 5 bytestream fifo survey note records the current exact replay snapshot" {
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
        "## Exact checks verified on 2026-05-15",
        "zig test samples/zigux/bytestream_fifo.zig",
        "eight in-file `test` blocks on current `master`",
        "reviewContract().focus",
        "previewInto() reports `copied = 8`, `total_visible = 32`, and `truncated = true`",
        "fill range remains `20` through `42`",
        "empty `peekByte()` and `skipByte()` return `null`",
        "draining `\"hello\"` into a three-byte buffer leaves `\"lo\"` queued",
        "first_window_len = 31`, `second_window_len = 1`, and `usesWrappedStorageWindow() = true`",
        "cold`, `initialized`, `replay_complete`, and `exited` stages",
        "recorded `5/5` sample self-checks at that time",
        "passed `5/5` build steps and `8/8` tests",
    };
    for (required_markers) |needle| {
        try std.testing.expect(std.mem.indexOf(u8, survey_note, needle) != null);
    }

    try std.testing.expect(std.mem.indexOf(u8, survey_note, "passed all six in-file checks") == null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "## Exact checks verified on 2026-05-14") == null);
}
