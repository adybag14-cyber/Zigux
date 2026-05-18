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
    try std.testing.expect(std.mem.indexOf(u8, manifest.validation_entrypoint, "zig test samples/zigux/kretprobe_example.zig") != null);
    try std.testing.expectEqual(@as(usize, 7), manifest.review_prompts.len);
    try std.testing.expectEqual(@as(usize, 8), manifest.exact_checks.len);
    try std.testing.expectEqual(@as(usize, 4), manifest.non_goals.len);

    var saw_descriptor_prompt = false;
    var saw_private_data_prompt = false;
    var saw_symbol_prompt = false;
    var saw_maxactive_prompt = false;
    var saw_non_goal_prompt = false;
    var saw_private_data_check = false;
    var saw_symbol_check = false;
    var saw_duration_check = false;
    var saw_maxactive_check = false;
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
        if (std.mem.indexOf(u8, prompt, "maxactive stays") != null and
            std.mem.indexOf(u8, prompt, "pre-init") != null)
        {
            saw_maxactive_prompt = true;
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
        if (std.mem.eql(u8, check.id, "maxactive-retarget")) {
            saw_maxactive_check = true;
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "retargetMaxactive(3)") != null);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "maxactive explicit") != null);
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
    try std.testing.expect(saw_maxactive_prompt);
    try std.testing.expect(saw_non_goal_prompt);
    try std.testing.expect(saw_private_data_check);
    try std.testing.expect(saw_symbol_check);
    try std.testing.expect(saw_duration_check);
    try std.testing.expect(saw_maxactive_check);
    try std.testing.expect(saw_exit_check);
    try std.testing.expect(std.mem.eql(u8, manifest.non_goals[0], "register_kretprobe parity"));
    try std.testing.expect(std.mem.eql(u8, manifest.non_goals[1], "unregister_kretprobe parity"));
}

test "phase 5 kretprobe note stays aligned with the manifest packet" {
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

    const note = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase5-kretprobe-sample-survey.md",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(note);

    try std.testing.expect(std.mem.indexOf(u8, note, "`PHASE5_STATUS=restored-direct-sample-packet`") != null);
    try std.testing.expect(std.mem.indexOf(u8, note, "`PHASE5_LANE_KEY=P5-L18`") != null);
    try std.testing.expect(std.mem.indexOf(u8, note, "`PHASE5_SLICE=kretprobe-sample-reviewability-packet`") != null);
    try std.testing.expect(std.mem.indexOf(u8, note, manifest.surveyed_commit) != null);
    try std.testing.expect(std.mem.indexOf(u8, note, manifest.sample_path) != null);
    try std.testing.expect(std.mem.indexOf(u8, note, "zigux/tests/phase5_kretprobe_example_manifest.json") != null);
    try std.testing.expect(std.mem.indexOf(u8, note, "zigux/tests/phase5_kretprobe_example_survey.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, note, "zigux/tests/phase5_build.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, note, "current public-tree-backed companion evidence") != null);
    try std.testing.expect(std.mem.indexOf(u8, note, "runtime_kretprobe") != null);
}
