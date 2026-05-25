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

test "phase 5 trace-events manifest records the callback-ownership packet" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const manifest_json = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase5_trace_events_sample_manifest.json",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(manifest_json);

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{});
    defer parsed.deinit();

    const manifest = parsed.value;
    try std.testing.expectEqualStrings("P5-L16", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 5", manifest.phase);
    try std.testing.expectEqualStrings("samples/trace_events/trace-events-sample.c", manifest.anchor);
    try std.testing.expectEqualStrings("samples/zigux/trace_events_sample.zig", manifest.sample_path);
    try std.testing.expect(std.mem.indexOf(u8, manifest.validation_entrypoint, "phase5_build.zig") != null);
    try std.testing.expectEqual(@as(usize, 8), manifest.review_prompts.len);
    try std.testing.expectEqual(@as(usize, 11), manifest.exact_checks.len);
    try std.testing.expectEqual(@as(usize, 4), manifest.non_goals.len);
    try std.testing.expectEqual(@as(usize, 40), manifest.surveyed_commit.len);

    var saw_payload_prompt = false;
    var saw_single_live_prompt = false;
    var saw_exit_prompt = false;
    var saw_iteration_check = false;
    var saw_focus_check = false;
    var saw_single_registration_check = false;
    var saw_exit_check = false;

    for (manifest.review_prompts) |prompt| {
        if (std.mem.indexOf(u8, prompt, "main-iteration") != null and
            std.mem.indexOf(u8, prompt, "callback-iteration") != null and
            std.mem.indexOf(u8, prompt, "relative-location") != null)
        {
            saw_payload_prompt = true;
        }
        if (std.mem.indexOf(u8, prompt, "single live") != null and
            std.mem.indexOf(u8, prompt, "register-then-unregister") != null)
        {
            saw_single_live_prompt = true;
        }
        if (std.mem.indexOf(u8, prompt, "after `exit()`") != null and
            std.mem.indexOf(u8, prompt, "unregisterFunctionCallback") != null)
        {
            saw_exit_prompt = true;
        }
    }

    for (manifest.exact_checks) |check| {
        if (std.mem.eql(u8, check.id, "iteration-cues")) {
            saw_iteration_check = true;
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "main iteration 7") != null);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "function-callback iteration 9") != null);
        }
        if (std.mem.eql(u8, check.id, "checked-focus-order")) {
            saw_focus_check = true;
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "payload_shape") != null);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "ownership_and_lifetime") != null);
        }
        if (std.mem.eql(u8, check.id, "single-registration-boundary")) {
            saw_single_registration_check = true;
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "second registerFunctionCallback call") != null);
        }
        if (std.mem.eql(u8, check.id, "post-exit-rejection")) {
            saw_exit_check = true;
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "replayFunctionIteration") != null);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "unregisterFunctionCallback") != null);
        }
    }

    try std.testing.expect(saw_payload_prompt);
    try std.testing.expect(saw_single_live_prompt);
    try std.testing.expect(saw_exit_prompt);
    try std.testing.expect(saw_iteration_check);
    try std.testing.expect(saw_focus_check);
    try std.testing.expect(saw_single_registration_check);
    try std.testing.expect(saw_exit_check);
    try std.testing.expect(std.mem.eql(u8, manifest.non_goals[0], "CREATE_TRACE_POINTS parity"));
    try std.testing.expect(std.mem.eql(u8, manifest.non_goals[1], "tracepoint macro parity from trace-events-sample.h"));
}
