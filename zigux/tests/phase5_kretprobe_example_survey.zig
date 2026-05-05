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
    try std.testing.expectEqualStrings("samples/kprobes/kretprobe_example.c", manifest.anchor);
    try std.testing.expectEqualStrings("samples/zigux/kretprobe_example.zig", manifest.sample_path);
    try std.testing.expect(std.mem.indexOf(u8, manifest.validation_entrypoint, "phase5_build.zig") != null);
    try std.testing.expectEqual(@as(usize, 6), manifest.review_prompts.len);
    try std.testing.expectEqual(@as(usize, 7), manifest.exact_checks.len);
    try std.testing.expectEqual(@as(usize, 4), manifest.non_goals.len);

    var saw_descriptor_prompt = false;
    var saw_private_data_prompt = false;
    var saw_symbol_prompt = false;
    var saw_non_goal_prompt = false;
    var saw_private_data_check = false;
    var saw_symbol_check = false;
    var saw_duration_check = false;
    var saw_exit_check = false;

    for (manifest.review_prompts) |prompt| {
        try std.testing.expect(prompt.len > 0);
        if (std.mem.indexOf(u8, prompt, "requires_runtime_substrate false") != null) {
            saw_descriptor_prompt = true;
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
        if (std.mem.eql(u8, check.id, "post-exit-rejection")) {
            saw_exit_check = true;
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "after exit") != null);
        }

        for (manifest.exact_checks[i + 1 ..]) |other| {
            try std.testing.expect(!std.mem.eql(u8, check.id, other.id));
        }
    }

    try std.testing.expect(saw_descriptor_prompt);
    try std.testing.expect(saw_private_data_prompt);
    try std.testing.expect(saw_symbol_prompt);
    try std.testing.expect(saw_non_goal_prompt);
    try std.testing.expect(saw_private_data_check);
    try std.testing.expect(saw_symbol_check);
    try std.testing.expect(saw_duration_check);
    try std.testing.expect(saw_exit_check);
    try std.testing.expect(std.mem.eql(u8, manifest.non_goals[0], "register_kretprobe parity"));
    try std.testing.expect(std.mem.eql(u8, manifest.non_goals[1], "unregister_kretprobe parity"));
}

test "phase 5 kretprobe survey note stays repo-local and keeps the build-wired boundary explicit" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const survey_note = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase5-kretprobe-sample-survey.md",
        std.testing.allocator,
        .limited(64 * 1024),
    );
    defer std.testing.allocator.free(survey_note);

    const required_mentions = [_][]const u8{
        "samples/kprobes/kretprobe_example.c|Phase 5",
        "phase5_build.zig",
        "runtime_kretprobe",
        "## Latest verification snapshot",
        "zig fmt --check",
        "zig test samples/zigux/kretprobe_example.zig",
        "zig build test --build-file zigux/tests/build.zig --summary all",
        "passed `1/1` sample self-check",
        "passed `5/5` build steps and `6/6` tests",
        "symbol_name = kernel_clone",
        "private_data_size_bytes = 8",
        "return_value = 42",
        "duration_ns = 75",
        "nmissed = 1",
        "maxactive = 20",
        "replay_runs = 1",
        "pre_init_anchor_rejected = true",
        "pre_init_exit_rejected = true",
        "double_init_rejected = true",
        "post_init_retarget_rejected = true",
        "stage_after_init = initialized",
        "entryHandler(false, 11) still skips the kernel-thread path",
        "entryHandler(true, 120) still rejects an outstanding tracked instance",
        "retHandler(37, 145) still yields duration 45",
        "retHandler(9, 199) still rejects invalid timestamp order",
        "retHandler(9, 260) still recovers with duration 60",
        "cold -> initialized -> replay_complete",
        "cold -> initialized -> exited",
    };

    for (required_mentions) |needle| {
        try std.testing.expect(std.mem.indexOf(u8, survey_note, needle) != null);
    }

    try std.testing.expect(std.mem.indexOf(u8, survey_note, "/workspace/agent_files") == null);
}
