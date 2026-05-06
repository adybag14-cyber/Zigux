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
        if (!std.ascii.isDigit(byte) and (byte < 'a' or byte > 'f')) {
            return false;
        }
    }

    return true;
}

test "phase 5 bytestream fifo manifest records the exact bounded checks" {
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
    try std.testing.expectEqual(@as(usize, 5), manifest.review_prompts.len);
    try std.testing.expectEqual(@as(usize, 12), manifest.exact_checks.len);
    try std.testing.expectEqual(@as(usize, 4), manifest.non_goals.len);

    var saw_descriptor_prompt = false;
    var saw_approved_idiom_prompt = false;
    var saw_manifest_prompt = false;
    var saw_preview_prompt = false;
    var saw_exact_sequence = false;
    var saw_capacity = false;
    var saw_helper_boundary = false;
    var saw_preview_boundary = false;
    var saw_available_capacity = false;
    var saw_snapshot = false;
    var saw_short_drain_prefix = false;
    var saw_lifecycle = false;

    for (manifest.review_prompts) |prompt| {
        try std.testing.expect(prompt.len > 0);

        if (std.mem.indexOf(u8, prompt, "requires_runtime_substrate false") != null) {
            saw_descriptor_prompt = true;
        }
        if (std.mem.indexOf(u8, prompt, "approved Phase 5 in-memory FIFO idiom") != null) {
            saw_approved_idiom_prompt = true;
        }
        if (std.mem.indexOf(u8, prompt, "phase5_build.zig") != null) {
            saw_manifest_prompt = true;
        }
        if (std.mem.indexOf(u8, prompt, "preview truncation boundary") != null) {
            saw_preview_prompt = true;
        }
    }

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
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "snapshotInto still begins with [2,3,4,5]") != null);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "previewInto copies [2,3,4,5,6,7,8,9]") != null);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "reports 10 visible bytes") != null);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "leaves the queued data intact") != null);
        }
        if (std.mem.eql(u8, check.id, "remaining-capacity")) {
            saw_available_capacity = true;
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "available() reports 32 at cold, initialized, replay-complete, reset, and exited boundaries") != null);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "27 after enqueueing \"hello\"") != null);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "22 after the preview-boundary setup") != null);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "0 at full capacity") != null);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "1 immediately after skip-at-capacity") != null);
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
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "\\\"hel\\\"") != null);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "\\\"lo\\\"") != null);
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
    try std.testing.expect(saw_manifest_prompt);
    try std.testing.expect(saw_preview_prompt);
    try std.testing.expect(saw_exact_sequence);
    try std.testing.expect(saw_capacity);
    try std.testing.expect(saw_helper_boundary);
    try std.testing.expect(saw_preview_boundary);
    try std.testing.expect(saw_available_capacity);
    try std.testing.expect(saw_snapshot);
    try std.testing.expect(saw_short_drain_prefix);
    try std.testing.expect(saw_lifecycle);
    try std.testing.expect(std.mem.eql(u8, manifest.non_goals[0], "procfs parity"));
    try std.testing.expect(std.mem.eql(u8, manifest.non_goals[1], "kfifo_from_user or kfifo_to_user parity"));
}

test "phase 5 bytestream fifo survey packet stays repo-local and keeps shared review surfaces explicit" {
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

    var surveyed_commit_marker_buf: [96]u8 = undefined;
    const surveyed_commit_marker = try std.fmt.bufPrint(
        surveyed_commit_marker_buf[0..],
        "PHASE5_SURVEYED_COMMIT={s}",
        .{manifest.surveyed_commit},
    );

    var lane_key_marker_buf: [64]u8 = undefined;
    const lane_key_marker = try std.fmt.bufPrint(
        lane_key_marker_buf[0..],
        "PHASE5_LANE_KEY={s}",
        .{manifest.lane_key},
    );

    var review_gate_marker_buf: [160]u8 = undefined;
    const review_gate_marker = try std.fmt.bufPrint(
        review_gate_marker_buf[0..],
        "samples/kfifo/bytestream-example.c|PHASE5_LANE_KEY={s}|PHASE5_SURVEYED_COMMIT={s}|Phase 5",
        .{ manifest.lane_key, manifest.surveyed_commit },
    );

    const survey_note = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase5-kfifo-sample-survey.md",
        std.testing.allocator,
        .limited(64 * 1024),
    );
    defer std.testing.allocator.free(survey_note);

    const required_mentions = [_][]const u8{
        "PHASE5_STATUS=parked",
        "PHASE5_SLICE=kfifo-reference-sample-starter",
        "samples/kfifo/bytestream-example.c",
        "phase5_bytestream_fifo_manifest.json",
        "phase5_build.zig",
        "runtime_atomic64.zig",
        "runtime_atomic64_loader.zig",
        "runtime_bitmap.zig",
        "runtime_bitmap_loader.zig",
        "runtime_kretprobe.zig",
        "runtime_kretprobe_loader.zig",
        "runtime_trace_events.zig",
        "runtime_trace_events_loader.zig",
        "loader-side follow-ons",
        "`samples/zigux/README.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md`",
        "shared docs-root, sample-root, scripts-root, and tests-root contributor packet should stay explicit here too",
    };

    for (required_mentions) |needle| {
        try std.testing.expect(std.mem.indexOf(u8, survey_note, needle) != null);
    }

    try std.testing.expect(std.mem.indexOf(u8, survey_note, lane_key_marker) != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, surveyed_commit_marker) != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "/workspace/agent_files") == null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, review_gate_marker) != null);

    const docs_root = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/README.md",
        std.testing.allocator,
        .limited(128 * 1024),
    );
    defer std.testing.allocator.free(docs_root);

    const docs_root_markers = [_][]const u8{
        "Documentation/zigux/phase5-kfifo-sample-survey.md",
        "samples/zigux/bytestream_fifo.zig",
        "exact replay checks",
        "remaining non-goals around procfs, user-copy, and module registration parity",
        "descriptor, manifest, and shared build-entrypoint prompts",
    };

    for (docs_root_markers) |needle| {
        try std.testing.expect(std.mem.indexOf(u8, docs_root, needle) != null);
    }

    const review_checklist = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/review-checklist.md",
        std.testing.allocator,
        .limited(128 * 1024),
    );
    defer std.testing.allocator.free(review_checklist);

    const checklist_markers = [_][]const u8{
        "if the change is a reference sample under `samples/zigux/`, is the self-check or behavior replay explicit and small enough to stay reviewable?",
        "if the change updates an existing Phase 5 sample, do the descriptor, manifest, and shared `phase5_build.zig` entrypoint still agree on the same Linux anchor and exact replay contract?",
        "if the change updates a landed Phase 5 sample that keeps a Linux concurrency or private-data cue only for reviewability, does the note or checklist still say clearly what remains in-memory-only and what runtime parity is still out of scope?",
        "if the change updates the landed Phase 5 `bytestream_fifo` sample packet, do the note, shared checklist text, and paired manifest-backed replays keep the exact queue-order drain contract, non-destructive `snapshotInto()` cue, short-drain `\"hel\"` plus queued `\"lo\"` helper boundary, and the `init()` -> `runAnchorReplay()` -> `exit()` ownership path explicit instead of implying procfs, user-copy, locking, or module-registration parity?",
        "if the change updates a landed Phase 5 sample, does it update the directly coupled survey note or manifest-backed contributor prompts when the sample contract changes?",
    };

    for (checklist_markers) |needle| {
        try std.testing.expect(std.mem.indexOf(u8, review_checklist, needle) != null);
    }

    const tests_root = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/README.md",
        std.testing.allocator,
        .limited(256 * 1024),
    );
    defer std.testing.allocator.free(tests_root);

    const tests_root_markers = [_][]const u8{
        "keep the shared Phase 5 reference-sample checks wired through `zigux/tests/phase5_build.zig`",
        "four shipped sample-backed surveys stay reviewable without implying runtime-substrate closure",
    };

    for (tests_root_markers) |needle| {
        try std.testing.expect(std.mem.indexOf(u8, tests_root, needle) != null);
    }

    const samples_root = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "samples/zigux/README.md",
        std.testing.allocator,
        .limited(64 * 1024),
    );
    defer std.testing.allocator.free(samples_root);

    const samples_root_markers = [_][]const u8{
        "samples/zigux/bytestream_fifo.zig",
        "approved in-memory queue-order and ownership-and-lifetime idiom",
        "samples/kfifo/bytestream-example.c",
        "phase5-kfifo-sample-survey.md",
        "phase5_bytestream_fifo_survey.zig",
    };

    for (samples_root_markers) |needle| {
        try std.testing.expect(std.mem.indexOf(u8, samples_root, needle) != null);
    }

    const scripts_root = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "scripts/zigux/README.md",
        std.testing.allocator,
        .limited(128 * 1024),
    );
    defer std.testing.allocator.free(scripts_root);

    const scripts_root_markers = [_][]const u8{
        "Phase 5 flow",
        "Documentation/zigux/phase5-kfifo-sample-survey.md",
        "samples/zigux/bytestream_fifo.zig",
        "zigux/tests/phase5_bytestream_fifo_manifest.json",
        "zigux/tests/phase5_bytestream_fifo_survey.zig",
        "zigux/tests/phase5_build.zig",
    };

    for (scripts_root_markers) |needle| {
        try std.testing.expect(std.mem.indexOf(u8, scripts_root, needle) != null);
    }

    const build_zig = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase5_build.zig",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(build_zig);

    const build_markers = [_][]const u8{
        "../../samples/zigux/bytestream_fifo.zig",
        "phase5_bytestream_fifo_survey.zig",
        "phase5-bytestream-fifo-tests",
        "phase5-bytestream-fifo-survey-tests",
        "run_phase5_bytestream_fifo_tests.step",
        "run_phase5_bytestream_fifo_survey_tests.step",
    };

    for (build_markers) |needle| {
        try std.testing.expect(std.mem.indexOf(u8, build_zig, needle) != null);
    }
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

    try std.testing.expect(std.mem.indexOf(u8, survey_note, "draining a three-byte destination from the queued string `\\\"hello\\\"` yields `\\\"hel\\\"`") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "leaves the remaining prefix `\\\"lo\\\"` queued in order") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "follow-up drain on the now-empty queue returns `0`") != null);
}

test "phase 5 bytestream fifo survey note records the preview boundary contract" {
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
        "runPreviewBoundaryReplay()",
        "preview truncation stay non-destructive",
        "truncated preview stays non-destructive",
        "`snapshotInto()` still begins with `[2,3,4,5]`",
        "`previewInto()` copies `[2,3,4,5,6,7,8,9]`",
        "reports `10` visible bytes",
        "leaves the queued data intact",
        "preview truncation boundary",
        "preview-boundary replay also held",
        "`snapshot_prefix = {2, 3, 4, 5}`",
        "`preview_prefix = {2, 3, 4, 5, 6, 7, 8, 9}`",
        "`preview_total_visible = 10`",
        "`queue_len_after_preview = 10`",
    };

    for (required_markers) |needle| {
        try std.testing.expect(std.mem.indexOf(u8, survey_note, needle) != null);
    }
}

test "phase 5 bytestream fifo survey note records the latest verification snapshot" {
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
        "## Latest verification snapshot",
        "0.17.0-dev.87+9b177a7d2",
        "zig test samples/zigux/bytestream_fifo.zig",
        "passed `5/5` sample self-checks",
        "passed `5/5` build steps and `8/8` tests",
        "len_after_initial_fill = 15",
        "first_out = \\\"hello\\\"",
        "second_out = {0, 1}",
        "skipped_byte = 2",
        "peek_value = 3",
        "fill_start = 20",
        "fill_end = 42",
        "snapshot_len = 32",
        "snapshot_sequence stayed [3,4,5,6,7,8,9,0,1,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42]",
        "final_len = 32",
        "peek and skip returned `null`",
        "empty enqueue copied `0` bytes",
        "overflow push was rejected at the 32-byte capacity",
        "skip-at-capacity returned `0`",
        "pop-after-reset returned `null`",
        "cold -> initialized -> replay_complete -> exited",
    };

    for (required_markers) |needle| {
        try std.testing.expect(std.mem.indexOf(u8, survey_note, needle) != null);
    }
}