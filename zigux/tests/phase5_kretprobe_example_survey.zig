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

test "phase 5 kretprobe manifest records the exact bounded checks" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const manifest_json = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase5_kretprobe_example_manifest.json",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(manifest_json);

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{});
    defer parsed.deinit();

    const manifest = parsed.value;
    try std.testing.expectEqualStrings("P5-L18", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 5", manifest.phase);
    try std.testing.expect(isLowerHexCommitSha(manifest.surveyed_commit));
    try std.testing.expectEqualStrings("samples/kprobes/kretprobe_example.c", manifest.anchor);
    try std.testing.expectEqualStrings("samples/zigux/kretprobe_example.zig", manifest.sample_path);
    try std.testing.expect(std.mem.indexOf(u8, manifest.validation_entrypoint, "phase5_build.zig") != null);
    try std.testing.expectEqual(@as(usize, 7), manifest.review_prompts.len);
    try std.testing.expectEqual(@as(usize, 9), manifest.exact_checks.len);
    try std.testing.expectEqual(@as(usize, 4), manifest.non_goals.len);

    var saw_descriptor_prompt = false;
    var saw_lifecycle_guard_prompt = false;
    var saw_private_data_prompt = false;
    var saw_symbol_prompt = false;
    var saw_ownership_prompt = false;
    var saw_budget_prompt = false;
    var saw_non_goal_prompt = false;
    var saw_private_data_check = false;
    var saw_symbol_check = false;
    var saw_duration_check = false;
    var saw_budget_check = false;
    var saw_ownership_check = false;
    var saw_exit_check = false;

    for (manifest.review_prompts) |prompt| {
        try std.testing.expect(prompt.len > 0);
        if (std.mem.indexOf(u8, prompt, "requires_runtime_substrate false") != null) {
            saw_descriptor_prompt = true;
        }
        if (std.mem.indexOf(u8, prompt, "runLifecycleGuardReplay()") != null and
            std.mem.indexOf(u8, prompt, "pre-init") != null and
            std.mem.indexOf(u8, prompt, "post-init") != null)
        {
            saw_lifecycle_guard_prompt = true;
        }
        if (std.mem.indexOf(u8, prompt, "private entry timestamp") != null and
            std.mem.indexOf(u8, prompt, "my_data") != null)
        {
            saw_private_data_prompt = true;
        }
        if (std.mem.indexOf(u8, prompt, "pre-init") != null and
            std.mem.indexOf(u8, prompt, "module_param") != null)
        {
            saw_symbol_prompt = true;
        }
        if (std.mem.indexOf(u8, prompt, "maxactiveBudget()") != null and
            std.mem.indexOf(u8, prompt, "20") != null)
        {
            saw_budget_prompt = true;
        }
        if (std.mem.indexOf(u8, prompt, "ownershipSummary") != null and
            std.mem.indexOf(u8, prompt, "replay_complete") != null)
        {
            saw_ownership_prompt = true;
        }
        if (std.mem.indexOf(u8, prompt, "register_kretprobe") != null and
            std.mem.indexOf(u8, prompt, "pt_regs") != null)
        {
            saw_non_goal_prompt = true;
        }
    }

    for (manifest.exact_checks, 0..) |check, i| {
        try std.testing.expect(check.id.len > 0);
        try std.testing.expect(check.kind.len > 0);
        try std.testing.expect(check.expected.len > 0);

        if (std.mem.eql(u8, check.id, "default-symbol")) {
            saw_symbol_check = true;
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "kernel_clone") != null);
        }
        if (std.mem.eql(u8, check.id, "private-data-shape")) {
            saw_private_data_check = true;
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "my_data") != null);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "i64-sized word") != null);
        }
        if (std.mem.eql(u8, check.id, "return-duration")) {
            saw_duration_check = true;
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "retval 42") != null);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "75 ns") != null);
        }
        if (std.mem.eql(u8, check.id, "maxactive-budget")) {
            saw_budget_check = true;
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "maxactiveBudget()") != null);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "20") != null);
        }
        if (std.mem.eql(u8, check.id, "ownership-summary-snapshots")) {
            saw_ownership_check = true;
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "cold, initialized, armed, replay_complete, and exited") != null);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "entry-timestamp state") != null);
        }
        if (std.mem.eql(u8, check.id, "post-exit-rejection")) {
            saw_exit_check = true;
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "after exit") != null);
        }

        for (manifest.exact_checks[i + 1 ..]) |other| {
            try std.testing.expect(!std.mem.eql(u8, check.id, other.id));
        }
    }

    try std.testing.expect(saw_descriptor_prompt);
    try std.testing.expect(saw_lifecycle_guard_prompt);
    try std.testing.expect(saw_private_data_prompt);
    try std.testing.expect(saw_symbol_prompt);
    try std.testing.expect(saw_budget_prompt);
    try std.testing.expect(saw_ownership_prompt);
    try std.testing.expect(saw_non_goal_prompt);
    try std.testing.expect(saw_private_data_check);
    try std.testing.expect(saw_symbol_check);
    try std.testing.expect(saw_duration_check);
    try std.testing.expect(saw_budget_check);
    try std.testing.expect(saw_ownership_check);
    try std.testing.expect(saw_exit_check);
    try std.testing.expect(std.mem.eql(u8, manifest.non_goals[0], "register_kretprobe parity"));
    try std.testing.expect(std.mem.eql(u8, manifest.non_goals[1], "unregister_kretprobe parity"));
}

test "phase 5 kretprobe survey packet stays repo-local and keeps shared review surfaces explicit" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const manifest_json = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase5_kretprobe_example_manifest.json",
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

    const survey_note = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase5-kretprobe-sample-survey.md",
        std.testing.allocator,
        .limited(64 * 1024),
    );
    defer std.testing.allocator.free(survey_note);

    const required_mentions = [_][]const u8{
        "PHASE5_STATUS=parked",
        "PHASE5_SLICE=kretprobe-reference-sample-starter",
        "samples/kprobes/kretprobe_example.c|PHASE5_LANE_KEY=P5-L18|PHASE5_SURVEYED_COMMIT=7361ac51374149a96b7a7a2c6ea3c995d8cc1231|Phase 5",
        "phase5_build.zig",
        "zigux/tests/phase5_kretprobe_example.zig",
        "runtime_kretprobe",
        "## Latest verification snapshot",
        "zig fmt --check",
        "zig test samples/zigux/kretprobe_example.zig",
        "zig build test --build-file zigux/tests/phase5_build.zig --summary all",
        "passed `3/3` sample self-checks",
        "passed `5/5` build steps and `7/7` tests",
        "symbol_name = kernel_clone",
        "private_data_size_bytes = 8",
        "return_value = 42",
        "duration_ns = 75",
        "maxactive_budget = 20",
        "nmissed = 1",
        "maxactive = 20",
        "replay_runs = 1",
        "pre_init_anchor_rejected = true",
        "pre_init_exit_rejected = true",
        "double_init_rejected = true",
        "post_init_retarget_rejected = true",
        "stage_after_init = initialized",
        "ownershipSummary()",
        "cold`, `initialized`, `armed`, `replay_complete`, and `exited`",
        "active_instances = 1",
        "entry_timestamp_armed = true",
        "the focused `zigux/tests/phase5_kretprobe_example.zig` boundary replay also still held",
        "entryHandler(false, 11) still skips the kernel-thread path",
        "entryHandler(true, 120) still rejects an outstanding tracked instance",
        "retHandler(37, 145) still yields duration 45",
        "retHandler(9, 199) still rejects invalid timestamp order",
        "retHandler(9, 260) still recovers with duration 60",
        "cold -> initialized -> replay_complete",
        "cold -> initialized -> exited",
        "runLifecycleGuardReplay()",
        "focused `zigux/tests/phase5_kretprobe_example.zig` replay still keep direct retargeting, outstanding-instance rejection, timestamp-order rejection and recovery, and post-exit teardown rejection explicit",
    };

    for (required_mentions) |needle| {
        try std.testing.expect(std.mem.indexOf(u8, survey_note, needle) != null);
    }

    try std.testing.expect(std.mem.indexOf(u8, survey_note, lane_key_marker) != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, surveyed_commit_marker) != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "one bounded self-check through `runAnchorReplay()`") == null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "/workspace/agent_files") == null);

    const docs_root = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/README.md",
        std.testing.allocator,
        .limited(128 * 1024),
    );
    defer std.testing.allocator.free(docs_root);

    const docs_root_markers = [_][]const u8{
        "Documentation/zigux/phase5-kretprobe-sample-survey.md",
        "samples/zigux/kretprobe_example.zig",
        "skip, private-data-shape, return-value, duration, fixed `maxactiveBudget()` cue, `ownershipSummary()` lifecycle snapshots, and teardown-boundary replay checks",
        "descriptor, manifest, `ownershipSummary()`, lifecycle-guard, and shared `phase5_build.zig` entrypoint prompts",
        "separate Phase 9 runtime starter",
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
        "landed Phase 5 `kretprobe` sample packet",
        "pre-init retargeting",
        "fixed `maxactiveBudget()` cue",
        "timestamp-order rejection and recovery",
        "post-exit handler rejection",
    };

    for (checklist_markers) |needle| {
        try std.testing.expect(std.mem.indexOf(u8, review_checklist, needle) != null);
    }

    const samples_root = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "samples/zigux/README.md",
        std.testing.allocator,
        .limited(128 * 1024),
    );
    defer std.testing.allocator.free(samples_root);

    const sample_root_markers = [_][]const u8{
        "Kretprobe review packet",
        "samples/zigux/kretprobe_example.zig",
        "approved non-runtime probe-lifecycle idiom",
        "zigux/tests/phase5_kretprobe_example_survey.zig",
        "pre-init retargeting",
        "fixed `maxactiveBudget()` cue",
        "timestamp-order rejection and recovery",
        "post-exit handler rejection",
    };

    for (sample_root_markers) |needle| {
        try std.testing.expect(std.mem.indexOf(u8, samples_root, needle) != null);
    }

    const tests_root = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/README.md",
        std.testing.allocator,
        .limited(256 * 1024),
    );
    defer std.testing.allocator.free(tests_root);

    const tests_root_markers = [_][]const u8{
        "keep the landed Phase 5 `kretprobe` packet explicit in the tests root too",
        "Documentation/zigux/phase5-kretprobe-sample-survey.md",
        "samples/zigux/kretprobe_example.zig",
        "zigux/tests/phase5_kretprobe_example_manifest.json",
        "zigux/tests/phase5_kretprobe_example.zig",
        "zigux/tests/phase5_kretprobe_example_survey.zig",
        "pre-init retargeting",
        "fixed `maxactiveBudget()` cue",
        "timestamp-order rejection and recovery",
        "post-exit handler rejection",
        "Phase 9 `runtime_kretprobe` family",
    };

    for (tests_root_markers) |needle| {
        try std.testing.expect(std.mem.indexOf(u8, tests_root, needle) != null);
    }

    const build_zig = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase5_build.zig",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(build_zig);

    const build_markers = [_][]const u8{
        "../../samples/zigux/kretprobe_example.zig",
        "phase5_kretprobe_example_survey.zig",
        "phase5-kretprobe-example-tests",
        "phase5-kretprobe-example-survey-tests",
        "run_phase5_kretprobe_example_tests.step",
        "run_phase5_kretprobe_example_survey_tests.step",
    };

    for (build_markers) |needle| {
        try std.testing.expect(std.mem.indexOf(u8, build_zig, needle) != null);
    }
}
