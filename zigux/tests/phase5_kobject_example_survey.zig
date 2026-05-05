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

test "phase 5 kobject manifest records the exact bounded checks" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const manifest_json = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase5_kobject_example_manifest.json",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(manifest_json);

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{});
    defer parsed.deinit();

    const manifest = parsed.value;
    try std.testing.expectEqualStrings("P5-Y03", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 5", manifest.phase);
    try std.testing.expectEqualStrings("samples/kobject/kobject-example.c", manifest.anchor);
    try std.testing.expectEqualStrings("samples/zigux/kobject_example.zig", manifest.sample_path);
    try std.testing.expect(std.mem.indexOf(u8, manifest.validation_entrypoint, "phase5_build.zig") != null);
    try std.testing.expectEqual(@as(usize, 5), manifest.review_prompts.len);
    try std.testing.expectEqual(@as(usize, 6), manifest.exact_checks.len);
    try std.testing.expectEqual(@as(usize, 4), manifest.non_goals.len);

    var saw_descriptor_prompt = false;
    var saw_dispatch_prompt = false;
    var saw_group_boundary_prompt = false;
    var saw_directory = false;
    var saw_dispatch = false;
    var saw_exit = false;

    for (manifest.review_prompts) |prompt| {
        try std.testing.expect(prompt.len > 0);
        if (std.mem.indexOf(u8, prompt, "requires_runtime_substrate false") != null) {
            saw_descriptor_prompt = true;
        }
        if (std.mem.indexOf(u8, prompt, "shared baz/bar dispatch") != null) {
            saw_dispatch_prompt = true;
        }
        if (std.mem.indexOf(u8, prompt, "unnamed attribute group") != null and
            std.mem.indexOf(u8, prompt, "post-exit") != null)
        {
            saw_group_boundary_prompt = true;
        }
    }

    for (manifest.exact_checks, 0..) |check, i| {
        try std.testing.expect(check.id.len > 0);
        try std.testing.expect(check.kind.len > 0);
        try std.testing.expect(check.expected.len > 0);

        if (std.mem.eql(u8, check.id, "directory-name")) {
            saw_directory = true;
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "kobject_example") != null);
        }
        if (std.mem.eql(u8, check.id, "shared-b-dispatch")) {
            saw_dispatch = true;
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "7 and -5") != null);
        }
        if (std.mem.eql(u8, check.id, "exit-boundary")) {
            saw_exit = true;
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "rejects later show or store calls") != null);
        }

        for (manifest.exact_checks[i + 1 ..]) |other| {
            try std.testing.expect(!std.mem.eql(u8, check.id, other.id));
        }
    }

    try std.testing.expect(saw_descriptor_prompt);
    try std.testing.expect(saw_dispatch_prompt);
    try std.testing.expect(saw_group_boundary_prompt);
    try std.testing.expect(saw_directory);
    try std.testing.expect(saw_dispatch);
    try std.testing.expect(saw_exit);
    try std.testing.expect(std.mem.eql(u8, manifest.non_goals[0], "sysfs file creation parity"));
    try std.testing.expect(std.mem.eql(u8, manifest.non_goals[1], "kernel_kobj integration"));
}

test "phase 5 kobject survey note stays repo-local and lane-scoped" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const survey_note = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase5-kobject-sample-survey.md",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(survey_note);

    try std.testing.expect(std.mem.indexOf(u8, survey_note, "PHASE5_LANE_KEY=P5-Y03") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "samples/kobject/kobject-example.c") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "zig build test --build-file zigux/tests/phase5_build.zig --summary all") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "/workspace/agent_files") == null);
}
