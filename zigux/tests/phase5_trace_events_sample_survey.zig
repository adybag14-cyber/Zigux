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

test "phase 5 trace-events manifest records the exact bounded checks" {
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
    try std.testing.expectEqualStrings("P5-L19", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 5", manifest.phase);
    try std.testing.expectEqual(@as(usize, 40), manifest.surveyed_commit.len);
    for (manifest.surveyed_commit) |byte| {
        try std.testing.expect(std.ascii.isLower(byte) or std.ascii.isDigit(byte));
    }
    try std.testing.expectEqualStrings("samples/trace_events/trace-events-sample.c", manifest.anchor);
    try std.testing.expectEqualStrings("samples/zigux/trace_events_sample.zig", manifest.sample_path);
    try std.testing.expect(std.mem.indexOf(u8, manifest.validation_entrypoint, "phase5_build.zig") != null);
    try std.testing.expectEqual(@as(usize, 8), manifest.review_prompts.len);
    try std.testing.expectEqual(@as(usize, 11), manifest.exact_checks.len);
    try std.testing.expectEqual(@as(usize, 4), manifest.non_goals.len);

    var saw_descriptor_prompt = false;
    var saw_docs_prompt = false;
    var saw_payload_prompt = false;
    var saw_callback_prompt = false;
    var saw_non_goal_prompt = false;
    var saw_message_check = false;
    var saw_modulo_cycle_check = false;
    var saw_iteration_check = false;
    var saw_rel_loc_check = false;
    var saw_vararg_check = false;
    var saw_counts_check = false;
    var saw_focus_check = false;
    var saw_callback_balance_check = false;
    var saw_exit_check = false;
    var saw_exit_prompt = false;

    for (manifest.review_prompts) |prompt| {
        try std.testing.expect(prompt.len > 0);
        if (std.mem.indexOf(u8, prompt, "requires_runtime_substrate false") != null) {
            saw_descriptor_prompt = true;
        }
        if (std.mem.indexOf(u8, prompt, "sample-backed survey note") != null and
            std.mem.indexOf(u8, prompt, "Documentation/zigux/README.md") != null and
            std.mem.indexOf(u8, prompt, "Documentation/zigux/review-checklist.md") != null and
            std.mem.indexOf(u8, prompt, "Phase 9 runtime pilot") != null)
        {
            saw_docs_prompt = true;
        }
        if (std.mem.indexOf(u8, prompt, "vararg-payload") != null and
            std.mem.indexOf(u8, prompt, "main-iteration") != null and
            std.mem.indexOf(u8, prompt, "callback-iteration") != null and
            std.mem.indexOf(u8, prompt, "relative-location") != null and
            std.mem.indexOf(u8, prompt, "callback-path") != null)
        {
            saw_payload_prompt = true;
        }
        if (std.mem.indexOf(u8, prompt, "register-then-unregister") != null and
            std.mem.indexOf(u8, prompt, "kthread") != null)
        {
            saw_callback_prompt = true;
        }
        if (std.mem.indexOf(u8, prompt, "after `exit()`") != null and
            std.mem.indexOf(u8, prompt, "replayFunctionIteration") != null and
            std.mem.indexOf(u8, prompt, "unregisterFunctionCallback") != null)
        {
            saw_exit_prompt = true;
        }
        if (std.mem.indexOf(u8, prompt, "CREATE_TRACE_POINTS") != null and
            std.mem.indexOf(u8, prompt, "tracepoint macros") != null)
        {
            saw_non_goal_prompt = true;
        }
    }

    for (manifest.exact_checks, 0..) |check, i| {
        try std.testing.expect(check.id.len > 0);
        try std.testing.expect(check.kind.len > 0);
        try std.testing.expect(check.expected.len > 0);

        if (std.mem.eql(u8, check.id, "message-and-string-shape")) {
            saw_message_check = true;
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "iter=7") != null);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "Gandalf") != null);
        }
        if (std.mem.eql(u8, check.id, "modulo-string-cycle")) {
            saw_modulo_cycle_check = true;
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "Mother Goose") != null);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "Snoopy") != null);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "Gandalf") != null);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "Frodo") != null);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "One ring to rule them all") != null);
        }
        if (std.mem.eql(u8, check.id, "iteration-cues")) {
            saw_iteration_check = true;
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "main iteration 7") != null);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "function-callback iteration 9") != null);
        }
        if (std.mem.eql(u8, check.id, "bitmask-and-rel-loc")) {
            saw_rel_loc_check = true;
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "0xdeadbeef") != null);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "relative-location") != null);
        }
        if (std.mem.eql(u8, check.id, "vararg-payload-path")) {
            saw_vararg_check = true;
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "vararg payload") != null);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "va_list") != null);
        }
        if (std.mem.eql(u8, check.id, "event-family-counts")) {
            saw_counts_check = true;
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "six") != null);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "eight") != null);
        }
        if (std.mem.eql(u8, check.id, "checked-focus-order")) {
            saw_focus_check = true;
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "payload_shape") != null);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "string_selection") != null);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "formatted_message") != null);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "ownership_and_lifetime") != null);
        }
        if (std.mem.eql(u8, check.id, "callback-registration-balance")) {
            saw_callback_balance_check = true;
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "callback path") != null);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "zero") != null);
        }
        if (std.mem.eql(u8, check.id, "post-exit-rejection")) {
            saw_exit_check = true;
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "after exit") != null);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "replayFunctionIteration") != null);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "unregisterFunctionCallback") != null);
        }

        for (manifest.exact_checks[i + 1 ..]) |other| {
            try std.testing.expect(!std.mem.eql(u8, check.id, other.id));
        }
    }

    try std.testing.expect(saw_descriptor_prompt);
    try std.testing.expect(saw_docs_prompt);
    try std.testing.expect(saw_payload_prompt);
    try std.testing.expect(saw_callback_prompt);
    try std.testing.expect(saw_exit_prompt);
    try std.testing.expect(saw_non_goal_prompt);
    try std.testing.expect(saw_message_check);
    try std.testing.expect(saw_modulo_cycle_check);
    try std.testing.expect(saw_iteration_check);
    try std.testing.expect(saw_rel_loc_check);
    try std.testing.expect(saw_vararg_check);
    try std.testing.expect(saw_counts_check);
    try std.testing.expect(saw_focus_check);
    try std.testing.expect(saw_callback_balance_check);
    try std.testing.expect(saw_exit_check);
    try std.testing.expect(std.mem.eql(u8, manifest.non_goals[0], "CREATE_TRACE_POINTS parity"));
    try std.testing.expect(std.mem.eql(u8, manifest.non_goals[1], "tracepoint macro parity from trace-events-sample.h"));
}

test "phase 5 trace-events contributor docs stay aligned with the shipped review surface" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const survey_note = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase5-trace-events-sample-survey.md",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(survey_note);

    const readme = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/README.md",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(readme);

    const review_checklist = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/review-checklist.md",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(review_checklist);

    try std.testing.expect(std.mem.indexOf(u8, survey_note, "sample-backed survey note") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "Documentation/zigux/README.md") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "Documentation/zigux/review-checklist.md") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "phase5_trace_events_sample_manifest.json") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "phase5_trace_events_sample_survey.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "phase5_build.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "Phase 9 runtime pilot") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "CREATE_TRACE_POINTS") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "replayFunctionIteration()") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "unregisterFunctionCallback()") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "Mother Goose") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "One ring to rule them all") != null);

    try std.testing.expect(std.mem.indexOf(u8, readme, "phase5-trace-events-sample-survey.md") != null);
    try std.testing.expect(std.mem.indexOf(u8, readme, "samples/zigux/trace_events_sample.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, readme, "Phase 9 runtime pilot tranche") != null);

    try std.testing.expect(std.mem.indexOf(u8, review_checklist, "manifest-backed survey") != null);
    try std.testing.expect(std.mem.indexOf(u8, review_checklist, "sample-backed survey note") != null);
    try std.testing.expect(std.mem.indexOf(u8, review_checklist, "phase5_build.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, review_checklist, "in-memory-only") != null);
    try std.testing.expect(std.mem.indexOf(u8, review_checklist, "runtime parity is still out of scope") != null);
}
