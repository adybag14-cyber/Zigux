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
    reference_patterns: []const []const u8,
    review_prompts: []const []const u8,
    exact_checks: []const ExactCheck,
    non_goals: []const []const u8,
};

const review_doc_read_limit = 64 * 1024;

fn expectedReplayFocus() [7][]const u8 {
    return .{
        "bounded_fifo_order",
        "wraparound_requeue",
        "peek_and_skip",
        "non_destructive_snapshot",
        "preview_truncation",
        "reset_and_replay",
        "ownership_and_lifetime",
    };
}

test "phase 5 bytestream fifo manifest records the exact bounded checks" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const manifest_json = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase5_bytestream_fifo_manifest.json",
        std.testing.allocator,
        .limited(review_doc_read_limit),
    );
    defer std.testing.allocator.free(manifest_json);

    const sample_source = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "samples/zigux/bytestream_fifo.zig",
        std.testing.allocator,
        .limited(review_doc_read_limit),
    );
    defer std.testing.allocator.free(sample_source);

    const helper_review_source = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase5_bytestream_fifo.zig",
        std.testing.allocator,
        .limited(review_doc_read_limit),
    );
    defer std.testing.allocator.free(helper_review_source);

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{});
    defer parsed.deinit();

    const manifest = parsed.value;
    const expected_focus = expectedReplayFocus();
    try std.testing.expectEqualStrings("P5-L04", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 5", manifest.phase);
    try std.testing.expectEqual(@as(usize, 40), manifest.surveyed_commit.len);
    for (manifest.surveyed_commit) |char| {
        try std.testing.expect(std.ascii.isHex(char));
        try std.testing.expect(!std.ascii.isUpper(char));
    }
    try std.testing.expectEqualStrings("samples/kfifo/bytestream-example.c", manifest.anchor);
    try std.testing.expectEqualStrings("samples/zigux/bytestream_fifo.zig", manifest.sample_path);
    try std.testing.expect(std.mem.indexOf(u8, manifest.validation_entrypoint, "phase5_build.zig") != null);
    try std.testing.expectEqual(@as(usize, 5), manifest.reference_patterns.len);
    try std.testing.expectEqual(@as(usize, 8), manifest.review_prompts.len);
    try std.testing.expectEqual(@as(usize, 17), manifest.exact_checks.len);
    try std.testing.expectEqual(@as(usize, 4), manifest.non_goals.len);

    try std.testing.expect(std.mem.indexOf(u8, helper_review_source, "phase 5 bytestream fifo sample keeps bounded helper behavior explicit") != null);
    try std.testing.expect(std.mem.indexOf(u8, helper_review_source, "empty_preview.total_visible") != null);
    try std.testing.expect(std.mem.indexOf(u8, helper_review_source, "preview_replay.preview_total_visible") != null);
    try std.testing.expect(std.mem.indexOf(u8, helper_review_source, "full_preview_result.total_visible") != null);
    try std.testing.expect(std.mem.indexOf(u8, helper_review_source, "!module.pushByte(255)") != null);
    try std.testing.expect(std.mem.indexOf(u8, helper_review_source, "short_drain") != null);
    try std.testing.expect(std.mem.indexOf(u8, helper_review_source, "phase 5 bytestream fifo reset clears queue state without restarting lifecycle bookkeeping") != null);
    try std.testing.expect(std.mem.indexOf(u8, helper_review_source, ".wraparound_requeue") != null);
    try std.testing.expect(std.mem.indexOf(u8, helper_review_source, ".non_destructive_snapshot") != null);
    try std.testing.expect(std.mem.indexOf(u8, helper_review_source, ".preview_truncation") != null);

    var saw_embedded_pattern = false;
    var saw_anchor_pattern = false;
    var saw_wraparound_pattern = false;
    var saw_snapshot_pattern = false;
    var saw_lifecycle_pattern = false;
    var saw_descriptor_prompt = false;
    var saw_manifest_prompt = false;
    var saw_surveyed_commit_prompt = false;
    var saw_helper_surface_prompt = false;
    var saw_docs_prompt = false;
    var saw_sample_root_prompt = false;
    var saw_storage_prompt = false;
    var saw_runtime_boundary_prompt = false;
    var saw_exact_sequence = false;
    var saw_snapshot = false;
    var saw_capacity = false;
    var saw_storage_contract = false;
    var saw_transfer_counts = false;
    var saw_preview_prefix = false;
    var saw_short_drain_prefix = false;
    var saw_preview_truncation = false;
    var saw_queue_only_reset = false;
    var saw_focus_list = false;
    var saw_lifecycle = false;
    var saw_lifecycle_guards = false;

    for (manifest.reference_patterns) |pattern| {
        try std.testing.expect(pattern.len > 0);

        if (std.mem.indexOf(u8, pattern, "fixed embedded 32-byte ring buffer") != null) {
            saw_embedded_pattern = true;
        }
        if (std.mem.indexOf(u8, pattern, "exact queue-order replay mirrors the Linux bytestream anchor") != null) {
            saw_anchor_pattern = true;
        }
        if (std.mem.indexOf(u8, pattern, "wraparound requeue, skip, and peek") != null) {
            saw_wraparound_pattern = true;
        }
        if (std.mem.indexOf(u8, pattern, "non-destructive snapshot") != null) {
            saw_snapshot_pattern = true;
        }
        if (std.mem.indexOf(u8, pattern, "ownership and lifetime boundaries explicit") != null) {
            saw_lifecycle_pattern = true;
        }
    }

    for (manifest.review_prompts) |prompt| {
        try std.testing.expect(prompt.len > 0);

        if (std.mem.indexOf(u8, prompt, "requires_runtime_substrate false") != null) {
            saw_descriptor_prompt = true;
        }
        if (std.mem.indexOf(u8, prompt, "phase5_build.zig") != null) {
            saw_manifest_prompt = true;
        }
        if (std.mem.indexOf(u8, prompt, "surveyed_commit") != null and
            std.mem.indexOf(u8, prompt, "PHASE5_SURVEYED_COMMIT") != null and
            std.mem.indexOf(u8, prompt, "floating branch label") != null)
        {
            saw_surveyed_commit_prompt = true;
        }
        if (std.mem.indexOf(u8, prompt, "phase5_bytestream_fifo.zig") != null and
            std.mem.indexOf(u8, prompt, "preview truncation") != null and
            std.mem.indexOf(u8, prompt, "capacity ceiling") != null)
        {
            saw_helper_surface_prompt = true;
        }
        if (std.mem.indexOf(u8, prompt, "sample-backed survey note") != null and
            std.mem.indexOf(u8, prompt, "review checklist") != null)
        {
            saw_docs_prompt = true;
        }
        if (std.mem.indexOf(u8, prompt, "samples/zigux/README.md") != null and
            std.mem.indexOf(u8, prompt, "four Phase 5 reference samples") != null and
            std.mem.indexOf(u8, prompt, "runtime starters") != null and
            std.mem.indexOf(u8, prompt, "review-packet stanza") != null and
            std.mem.indexOf(u8, prompt, "checked_focus order") != null and
            std.mem.indexOf(u8, prompt, "bounded_fifo_order") != null and
            std.mem.indexOf(u8, prompt, "ownership_and_lifetime") != null and
            std.mem.indexOf(u8, prompt, "helper-only review surface") != null and
            std.mem.indexOf(u8, prompt, "out-of-scope runtime claims") != null)
        {
            saw_sample_root_prompt = true;
        }
        if (std.mem.indexOf(u8, prompt, "fixed embedded backing") != null) {
            saw_storage_prompt = true;
        }
        if (std.mem.indexOf(u8, prompt, "approved in-memory FIFO idiom") != null and
            std.mem.indexOf(u8, prompt, "runtime-substrate claim") != null)
        {
            saw_runtime_boundary_prompt = true;
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
        if (std.mem.eql(u8, check.id, "snapshot-before-final-drain")) {
            saw_snapshot = true;
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "non-destructive snapshot") != null);
        }
        if (std.mem.eql(u8, check.id, "fill-to-capacity")) {
            saw_capacity = true;
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "20 through 42 inclusive") != null);
        }
        if (std.mem.eql(u8, check.id, "storage-backing-contract")) {
            saw_storage_contract = true;
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "fixed embedded 32-byte ring buffer") != null);
        }
        if (std.mem.eql(u8, check.id, "transfer-count-contract")) {
            saw_transfer_counts = true;
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "initial string copy count is 5") != null);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "first drain count is 5") != null);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "second drain count is 2") != null);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "requeue count is 2") != null);
        }
        if (std.mem.eql(u8, check.id, "wrapped-preview-prefix")) {
            saw_preview_prefix = true;
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "truncated 8-byte preview prefix preserves exactly [3,4,5,6,7,8,9,0]") != null);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "without consuming state") != null);
        }
        if (std.mem.eql(u8, check.id, "short-drain-prefix")) {
            saw_short_drain_prefix = true;
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "\"hel\"") != null);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "\"lo\"") != null);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "returns 0") != null);
        }
        if (std.mem.eql(u8, check.id, "preview-truncation")) {
            saw_preview_truncation = true;
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "length-8 preview yields exactly [2,3,4,5,6,7,8,9]") != null);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "queue length at 10") != null);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "total_visible") != null);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "0") != null);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "10") != null);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "32") != null);
        }
        if (std.mem.eql(u8, check.id, "queue-only-reset")) {
            saw_queue_only_reset = true;
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "without rewinding lifecycle stage") != null);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "init_runs and exit_runs") != null);
        }
        if (std.mem.eql(u8, check.id, "lifecycle-boundary")) {
            saw_lifecycle = true;
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "requires init before replay") != null);
        }
        if (std.mem.eql(u8, check.id, "checked-focus-list")) {
            saw_focus_list = true;
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "exactly seven focus areas") != null);
            for (expected_focus) |focus_name| {
                try std.testing.expect(std.mem.indexOf(u8, check.expected, focus_name) != null);
                try std.testing.expect(std.mem.indexOf(u8, sample_source, focus_name) != null);
            }
        }
        if (std.mem.eql(u8, check.id, "lifecycle-guards-and-counters")) {
            saw_lifecycle_guards = true;
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "after exit") != null);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "init_runs and exit_runs at 1") != null);
        }

        for (manifest.exact_checks[i + 1 ..]) |other| {
            try std.testing.expect(!std.mem.eql(u8, check.id, other.id));
        }
    }

    try std.testing.expect(saw_embedded_pattern);
    try std.testing.expect(saw_anchor_pattern);
    try std.testing.expect(saw_wraparound_pattern);
    try std.testing.expect(saw_snapshot_pattern);
    try std.testing.expect(saw_lifecycle_pattern);
    try std.testing.expect(saw_descriptor_prompt);
    try std.testing.expect(saw_manifest_prompt);
    try std.testing.expect(saw_surveyed_commit_prompt);
    try std.testing.expect(saw_helper_surface_prompt);
    try std.testing.expect(saw_docs_prompt);
    try std.testing.expect(saw_sample_root_prompt);
    try std.testing.expect(saw_storage_prompt);
    try std.testing.expect(saw_runtime_boundary_prompt);
    try std.testing.expect(saw_exact_sequence);
    try std.testing.expect(saw_snapshot);
    try std.testing.expect(saw_capacity);
    try std.testing.expect(saw_storage_contract);
    try std.testing.expect(saw_transfer_counts);
    try std.testing.expect(saw_preview_prefix);
    try std.testing.expect(saw_short_drain_prefix);
    try std.testing.expect(saw_preview_truncation);
    try std.testing.expect(saw_queue_only_reset);
    try std.testing.expect(saw_focus_list);
    try std.testing.expect(saw_lifecycle);
    try std.testing.expect(saw_lifecycle_guards);
    try std.testing.expect(std.mem.eql(u8, manifest.non_goals[0], "procfs parity"));
    try std.testing.expect(std.mem.eql(u8, manifest.non_goals[1], "kfifo_from_user or kfifo_to_user parity"));
    try std.testing.expect(std.mem.eql(u8, manifest.non_goals[2], "loadable module registration"));
    try std.testing.expect(std.mem.eql(u8, manifest.non_goals[3], "locking or blocking semantics"));
}

test "phase 5 bytestream fifo contributor docs stay aligned with the shipped review surface" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const manifest_json = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase5_bytestream_fifo_manifest.json",
        std.testing.allocator,
        .limited(review_doc_read_limit),
    );
    defer std.testing.allocator.free(manifest_json);

    const survey_note = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase5-kfifo-sample-survey.md",
        std.testing.allocator,
        .limited(review_doc_read_limit),
    );
    defer std.testing.allocator.free(survey_note);

    const readme = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/README.md",
        std.testing.allocator,
        .limited(review_doc_read_limit),
    );
    defer std.testing.allocator.free(readme);

    const samples_readme = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "samples/zigux/README.md",
        std.testing.allocator,
        .limited(review_doc_read_limit),
    );
    defer std.testing.allocator.free(samples_readme);

    const tests_readme = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/README.md",
        std.testing.allocator,
        .limited(review_doc_read_limit),
    );
    defer std.testing.allocator.free(tests_readme);

    const review_checklist = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/review-checklist.md",
        std.testing.allocator,
        .limited(review_doc_read_limit),
    );
    defer std.testing.allocator.free(review_checklist);

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{});
    defer parsed.deinit();

    const manifest = parsed.value;
    const lane_marker = try std.fmt.allocPrint(
        std.testing.allocator,
        "PHASE5_LANE_KEY={s}",
        .{manifest.lane_key},
    );
    defer std.testing.allocator.free(lane_marker);
    const surveyed_commit_marker = try std.fmt.allocPrint(
        std.testing.allocator,
        "PHASE5_SURVEYED_COMMIT={s}",
        .{manifest.surveyed_commit},
    );
    defer std.testing.allocator.free(surveyed_commit_marker);

    const pinned_commit_line = try std.fmt.allocPrint(
        std.testing.allocator,
        "approved in-memory FIFO idiom is now pinned to `PHASE5_SURVEYED_COMMIT={s}`",
        .{manifest.surveyed_commit},
    );
    defer std.testing.allocator.free(pinned_commit_line);

    try std.testing.expect(std.mem.indexOf(u8, survey_note, "sample-backed survey note") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "phase5_bytestream_fifo_manifest.json") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "phase5_bytestream_fifo_survey.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "phase5_build.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, lane_marker) != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, surveyed_commit_marker) != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "reference-pattern list") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "samples/zigux/README.md") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "zigux/tests/README.md") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "shared tests-root guide in `zigux/tests/README.md`") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "zig test samples/zigux/bytestream_fifo.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "zig test zigux/tests/phase5_bytestream_fifo_survey.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "fixed embedded 32-byte ring buffer") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "wraparound requeue, skip, and peek") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "runtime_atomic64_loader.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "runtime_bitmap_loader.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "runtime_kretprobe_loader.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "runtime_trace_events_loader.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "blocked `samples/zigux/runtime_trace_events.zig` pilot") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "bounded `samples/zigux/runtime_trace_events_loader.zig` scaffold is shipped now") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "preview truncation") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "fixed embedded") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "phase5_bytestream_fifo.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "initial string copy count is `5`") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "`kfifo_in()` and `kfifo_out()` transfer sizes stay reviewable") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "draining a three-byte destination from the queued string `\\\"hello\\\"` yields `\\\"hel\\\"`") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "follow-up drain on the now-empty queue returns `0`") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "capacity ceiling") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "outside the main replay path") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "procfs, user-copy, locking, and runtime registration remain out of scope") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "exactly seven review-focus areas") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "`preview_truncation`") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "1/4 bytestream_fifo.test.bytestream fifo sample replays the Linux anchor result sequence...OK") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "4/4 bytestream_fifo.test.bytestream fifo sample reset clears queue state without rewinding lifecycle bookkeeping...OK") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "All 4 tests passed.") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "The shared `zigux/tests/phase5_build.zig` entrypoint remains the umbrella review gate recorded in the manifest and contributor prompts, but this bounded verification pass did not rerun the whole Phase 5 sample bundle, so this note no longer republishes the older pre-expansion shared test count.") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "zig test zigux/tests/phase5_bytestream_fifo_survey.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "All 2 tests passed.") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "surveyed_commit") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "floating branch label") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, pinned_commit_line) != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "The roadmap delivery gap is already closed.") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "approved in-memory FIFO idiom inside that completed anchor set") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "shared sample-root catalog, shared tests-root guide, shared review checklist, and contributor refresh path all point at the same inspected `master` head") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "without reopening the closed Phase 5 sample-delivery gap") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "no `samples/zigux/*string*` or `samples/zigux/*cmdline*` Phase 5 reference sample") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "no `samples/zigux/*cmdline*` Phase 5 boundary explicit") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "exact `checked_focus` order `bounded_fifo_order`, `wraparound_requeue`, `peek_and_skip`, `non_destructive_snapshot`, `preview_truncation`, `reset_and_replay`, and `ownership_and_lifetime`") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "phase7-cmdline-slice.md") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "lib/cmdline.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "phase7_cmdline.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "phase7_build.zig") != null);

    try std.testing.expect(std.mem.indexOf(u8, readme, "phase5-kfifo-sample-survey.md") != null);
    try std.testing.expect(std.mem.indexOf(u8, readme, "samples/zigux/README.md") != null);
    try std.testing.expect(std.mem.indexOf(u8, readme, "samples/zigux/bytestream_fifo.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, readme, "preview-truncation") != null);
    try std.testing.expect(std.mem.indexOf(u8, readme, "fixed embedded backing") != null);
    try std.testing.expect(std.mem.indexOf(u8, readme, "lifecycle-boundary checks") != null);
    try std.testing.expect(std.mem.indexOf(u8, readme, "procfs, user-copy, locking, and module registration parity") != null);
    try std.testing.expect(std.mem.indexOf(u8, readme, "phase7-cmdline-slice.md") != null);
    try std.testing.expect(std.mem.indexOf(u8, readme, "lib/cmdline.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, readme, "phase7_cmdline.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, readme, "phase7_build.zig") != null);

    try std.testing.expect(std.mem.indexOf(u8, samples_readme, "Phase 5 reference samples") != null);
    try std.testing.expect(std.mem.indexOf(u8, samples_readme, "Bytestream FIFO review packet") != null);
    try std.testing.expect(std.mem.indexOf(u8, samples_readme, "phase5_bytestream_fifo_manifest.json") != null);
    try std.testing.expect(std.mem.indexOf(u8, samples_readme, "phase5_bytestream_fifo_survey.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, samples_readme, "phase5-kfifo-sample-survey.md") != null);
    try std.testing.expect(std.mem.indexOf(u8, samples_readme, "phase5_build.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, samples_readme, "exact queue-order replay") != null);
    try std.testing.expect(std.mem.indexOf(u8, samples_readme, "transfer counts") != null);
    try std.testing.expect(std.mem.indexOf(u8, samples_readme, "checked_focus") != null);
    try std.testing.expect(std.mem.indexOf(u8, samples_readme, "bounded_fifo_order") != null);
    try std.testing.expect(std.mem.indexOf(u8, samples_readme, "wraparound_requeue") != null);
    try std.testing.expect(std.mem.indexOf(u8, samples_readme, "peek_and_skip") != null);
    try std.testing.expect(std.mem.indexOf(u8, samples_readme, "non_destructive_snapshot") != null);
    try std.testing.expect(std.mem.indexOf(u8, samples_readme, "preview_truncation") != null);
    try std.testing.expect(std.mem.indexOf(u8, samples_readme, "reset_and_replay") != null);
    try std.testing.expect(std.mem.indexOf(u8, samples_readme, "ownership_and_lifetime") != null);
    try std.testing.expect(std.mem.indexOf(u8, samples_readme, "helper-only review surface") != null);
    try std.testing.expect(std.mem.indexOf(u8, samples_readme, "capacity ceiling") != null);
    try std.testing.expect(std.mem.indexOf(u8, samples_readme, "kfifo_from_user()") != null);
    try std.testing.expect(std.mem.indexOf(u8, samples_readme, "runtime module claim") != null);
    try std.testing.expect(std.mem.indexOf(u8, samples_readme, "Later runtime starters and loader-side follow-ons") != null);
    try std.testing.expect(std.mem.indexOf(u8, samples_readme, "samples/zigux/bytestream_fifo.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, samples_readme, "samples/zigux/kobject_example.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, samples_readme, "samples/zigux/kretprobe_example.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, samples_readme, "samples/zigux/trace_events_sample.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, samples_readme, "samples/zigux/runtime_atomic64.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, samples_readme, "samples/zigux/runtime_atomic64_loader.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, samples_readme, "samples/zigux/runtime_bitmap.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, samples_readme, "samples/zigux/runtime_bitmap_loader.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, samples_readme, "samples/zigux/runtime_kretprobe.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, samples_readme, "samples/zigux/runtime_kretprobe_loader.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, samples_readme, "samples/zigux/runtime_trace_events.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, samples_readme, "samples/zigux/runtime_trace_events_loader.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, samples_readme, "sample-only blocked Phase 9 pilot") != null);
    try std.testing.expect(std.mem.indexOf(u8, samples_readme, "runtime-substrate handoff still stays blocked") != null);
    try std.testing.expect(std.mem.indexOf(u8, samples_readme, "no `samples/zigux/*string*` Phase 5 reference sample") != null);
    try std.testing.expect(std.mem.indexOf(u8, samples_readme, "no `samples/zigux/*cmdline*` Phase 5 reference sample") != null);
    try std.testing.expect(std.mem.indexOf(u8, samples_readme, "phase7-cmdline-slice.md") != null);
    try std.testing.expect(std.mem.indexOf(u8, samples_readme, "lib/cmdline.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, samples_readme, "phase7_cmdline.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, samples_readme, "phase7_build.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, samples_readme, "zig test zigux/tests/phase5_bytestream_fifo.zig") != null);

    try std.testing.expect(std.mem.indexOf(u8, tests_readme, "zigux/tests/phase5_bytestream_fifo.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, tests_readme, "zigux/tests/phase5_bytestream_fifo_manifest.json") != null);
    try std.testing.expect(std.mem.indexOf(u8, tests_readme, "zigux/tests/phase5_bytestream_fifo_survey.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, tests_readme, "scripts/zigux/validate-phase5.py") != null);
    try std.testing.expect(std.mem.indexOf(u8, tests_readme, "make -C zigux phase5-validate") != null);
    try std.testing.expect(std.mem.indexOf(u8, tests_readme, "zig test samples/zigux/bytestream_fifo.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, tests_readme, "zig test zigux/tests/phase5_bytestream_fifo_survey.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, tests_readme, "keep the current Phase 5 reference-sample packet reviewable through `zigux/tests/phase5_build.zig`") != null);
    try std.testing.expect(std.mem.indexOf(u8, tests_readme, "direct sample replays and paired survey replays explicit for every shipped Phase 5 family") != null);

    try std.testing.expect(std.mem.indexOf(u8, review_checklist, "manifest-backed survey") != null);
    try std.testing.expect(std.mem.indexOf(u8, review_checklist, "sample-backed survey note") != null);
    try std.testing.expect(std.mem.indexOf(u8, review_checklist, "phase5_build.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, review_checklist, "exact replay contract") != null);
    try std.testing.expect(std.mem.indexOf(u8, review_checklist, "no `samples/zigux/*cmdline*` Phase 5 reference sample") != null);
    try std.testing.expect(std.mem.indexOf(u8, review_checklist, "lib/cmdline.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, review_checklist, "phase7_cmdline.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, review_checklist, "phase7_build.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, review_checklist, "zig test zigux/tests/phase5_bytestream_fifo.zig") == null);
}
