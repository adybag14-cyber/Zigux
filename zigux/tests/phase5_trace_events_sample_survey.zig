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

const review_doc_read_limit = 64 * 1024;

test "phase 5 trace-events manifest records the exact bounded checks" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const manifest_json = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase5_trace_events_sample_manifest.json",
        std.testing.allocator,
        .limited(review_doc_read_limit),
    );
    defer std.testing.allocator.free(manifest_json);

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{});
    defer parsed.deinit();

    const manifest = parsed.value;
    try std.testing.expectEqualStrings("P5-L16", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 5", manifest.phase);
    try std.testing.expectEqual(@as(usize, 40), manifest.surveyed_commit.len);
    for (manifest.surveyed_commit) |byte| {
        try std.testing.expect(std.ascii.isLower(byte) or std.ascii.isDigit(byte));
    }
    try std.testing.expectEqualStrings("samples/trace_events/trace-events-sample.c", manifest.anchor);
    try std.testing.expectEqualStrings("samples/zigux/trace_events_sample.zig", manifest.sample_path);
    try std.testing.expect(std.mem.indexOf(u8, manifest.validation_entrypoint, "phase5_build.zig") != null);
    try std.testing.expectEqual(@as(usize, 10), manifest.review_prompts.len);
    try std.testing.expectEqual(@as(usize, 15), manifest.exact_checks.len);
    try std.testing.expectEqual(@as(usize, 4), manifest.non_goals.len);

    var saw_descriptor_prompt = false;
    var saw_surveyed_commit_prompt = false;
    var saw_docs_prompt = false;
    var saw_payload_prompt = false;
    var saw_lifecycle_prompt = false;
    var saw_cycle_prompt = false;
    var saw_callback_prompt = false;
    var saw_non_goal_prompt = false;
    var saw_descriptor_check = false;
    var saw_message_check = false;
    var saw_modulo_cycle_check = false;
    var saw_iteration_check = false;
    var saw_array_shape_check = false;
    var saw_rel_loc_check = false;
    var saw_vararg_check = false;
    var saw_counts_check = false;
    var saw_lifecycle_check = false;
    var saw_focus_check = false;
    var saw_callback_balance_check = false;
    var saw_pre_registration_check = false;
    var saw_single_registration_check = false;
    var saw_underflow_and_armed_exit_check = false;
    var saw_exit_check = false;
    var saw_exit_prompt = false;
    var saw_sync_prompt = false;

    for (manifest.review_prompts) |prompt| {
        try std.testing.expect(prompt.len > 0);
        if (std.mem.indexOf(u8, prompt, "requires_runtime_substrate false") != null) {
            saw_descriptor_prompt = true;
        }
        if (std.mem.indexOf(u8, prompt, "surveyed_commit") != null and
            std.mem.indexOf(u8, prompt, "exact inspected master head") != null and
            std.mem.indexOf(u8, prompt, "floating branch label") != null)
        {
            saw_surveyed_commit_prompt = true;
        }
        if (std.mem.indexOf(u8, prompt, "sample-backed survey note") != null and
            std.mem.indexOf(u8, prompt, "samples/zigux/README.md") != null and
            std.mem.indexOf(u8, prompt, "Documentation/zigux/README.md") != null and
            std.mem.indexOf(u8, prompt, "Documentation/zigux/review-checklist.md") != null and
            std.mem.indexOf(u8, prompt, "approved payload-and-callback idiom") != null and
            std.mem.indexOf(u8, prompt, "reviewable and repeatable") != null and
            std.mem.indexOf(u8, prompt, "Phase 9 runtime pilot") != null)
        {
            saw_docs_prompt = true;
        }
        if (std.mem.indexOf(u8, prompt, "selected-string-slot") != null and
            std.mem.indexOf(u8, prompt, "payload-length") != null and
            std.mem.indexOf(u8, prompt, "main-iteration") != null and
            std.mem.indexOf(u8, prompt, "callback-iteration") != null and
            std.mem.indexOf(u8, prompt, "vararg-payload") != null and
            std.mem.indexOf(u8, prompt, "lifecycle-summary") != null and
            std.mem.indexOf(u8, prompt, "relative-location") != null and
            std.mem.indexOf(u8, prompt, "callback-path") != null)
        {
            saw_payload_prompt = true;
        }
        if (std.mem.indexOf(u8, prompt, "lifecycle summary") != null and
            std.mem.indexOf(u8, prompt, "init or replay or exit counts") != null and
            std.mem.indexOf(u8, prompt, "registration depth") != null and
            std.mem.indexOf(u8, prompt, "private field access") != null)
        {
            saw_lifecycle_prompt = true;
        }
        if (std.mem.indexOf(u8, prompt, "runStringFormattingCycleReplay()") != null and
            std.mem.indexOf(u8, prompt, "full modulo-selected string cycle") != null and
            std.mem.indexOf(u8, prompt, "selected-string slot cues") != null and
            std.mem.indexOf(u8, prompt, "iter-format messages") != null)
        {
            saw_cycle_prompt = true;
        }
        if (std.mem.indexOf(u8, prompt, "single live") != null and
            std.mem.indexOf(u8, prompt, "replayFunctionIteration before registration") != null and
            std.mem.indexOf(u8, prompt, "FunctionCallbackNotRegistered") != null and
            std.mem.indexOf(u8, prompt, "register-then-unregister") != null and
            std.mem.indexOf(u8, prompt, "unregisterFunctionCallback underflow") != null and
            std.mem.indexOf(u8, prompt, "OutstandingRegistration") != null and
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
        if (std.mem.indexOf(u8, prompt, "sample-behavior changes") != null and
            std.mem.indexOf(u8, prompt, "manifest-backed replay contract") != null and
            std.mem.indexOf(u8, prompt, "infer the new boundary from code alone") != null)
        {
            saw_sync_prompt = true;
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
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "slot 2") != null);
        }
        if (std.mem.eql(u8, check.id, "descriptor-anchor")) {
            saw_descriptor_check = true;
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "samples/trace_events/trace-events-sample.c") != null);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "non-runtime reference-sample lane") != null);
        }
        if (std.mem.eql(u8, check.id, "modulo-string-cycle")) {
            saw_modulo_cycle_check = true;
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "runStringFormattingCycleReplay()") != null);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "five public cases") != null);
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
        if (std.mem.eql(u8, check.id, "array-and-sentinel-shape")) {
            saw_array_shape_check = true;
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "payload length 2") != null);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "1,2 payload prefix") != null);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "zero sentinel") != null);
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
        if (std.mem.eql(u8, check.id, "lifecycle-summary-counts")) {
            saw_lifecycle_check = true;
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "replay_complete") != null);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "1,1,0") != null);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "zero registration depth") != null);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "eight total event calls") != null);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "exited") != null);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "1,1,1") != null);
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
        if (std.mem.eql(u8, check.id, "pre-registration-callback-rejection")) {
            saw_pre_registration_check = true;
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "replayFunctionIteration before registration") != null);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "FunctionCallbackNotRegistered") != null);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "tracepoint enablement parity") != null);
        }
        if (std.mem.eql(u8, check.id, "single-registration-boundary")) {
            saw_single_registration_check = true;
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "second registerFunctionCallback call") != null);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "one live callback registration") != null);
        }
        if (std.mem.eql(u8, check.id, "registration-underflow-and-armed-exit")) {
            saw_underflow_and_armed_exit_check = true;
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "unregisterFunctionCallback underflow") != null);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "OutstandingRegistration") != null);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "one callback remains armed") != null);
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
    try std.testing.expect(saw_surveyed_commit_prompt);
    try std.testing.expect(saw_docs_prompt);
    try std.testing.expect(saw_payload_prompt);
    try std.testing.expect(saw_lifecycle_prompt);
    try std.testing.expect(saw_cycle_prompt);
    try std.testing.expect(saw_callback_prompt);
    try std.testing.expect(saw_exit_prompt);
    try std.testing.expect(saw_sync_prompt);
    try std.testing.expect(saw_non_goal_prompt);
    try std.testing.expect(saw_descriptor_check);
    try std.testing.expect(saw_message_check);
    try std.testing.expect(saw_modulo_cycle_check);
    try std.testing.expect(saw_iteration_check);
    try std.testing.expect(saw_array_shape_check);
    try std.testing.expect(saw_rel_loc_check);
    try std.testing.expect(saw_vararg_check);
    try std.testing.expect(saw_counts_check);
    try std.testing.expect(saw_lifecycle_check);
    try std.testing.expect(saw_focus_check);
    try std.testing.expect(saw_callback_balance_check);
    try std.testing.expect(saw_pre_registration_check);
    try std.testing.expect(saw_single_registration_check);
    try std.testing.expect(saw_underflow_and_armed_exit_check);
    try std.testing.expect(saw_exit_check);
    try std.testing.expect(std.mem.eql(u8, manifest.non_goals[0], "CREATE_TRACE_POINTS parity"));
    try std.testing.expect(std.mem.eql(u8, manifest.non_goals[1], "tracepoint macro parity from trace-events-sample.h"));
    try std.testing.expect(std.mem.eql(u8, manifest.non_goals[2], "kernel thread scheduling or timeout parity"));
    try std.testing.expect(std.mem.eql(u8, manifest.non_goals[3], "module registration or unregister wiring parity"));
}

test "phase 5 trace-events contributor docs stay aligned with the shipped review surface" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const manifest_json = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase5_trace_events_sample_manifest.json",
        std.testing.allocator,
        .limited(review_doc_read_limit),
    );
    defer std.testing.allocator.free(manifest_json);

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{});
    defer parsed.deinit();

    const manifest = parsed.value;

    const survey_note = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase5-trace-events-sample-survey.md",
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

    const sample_root_readme = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "samples/zigux/README.md",
        std.testing.allocator,
        .limited(review_doc_read_limit),
    );
    defer std.testing.allocator.free(sample_root_readme);

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
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(review_checklist);

    try std.testing.expect(std.mem.indexOf(u8, survey_note, "sample-backed survey note") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "Documentation/zigux/README.md") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "Documentation/zigux/review-checklist.md") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "zigux/tests/phase5_trace_events_sample.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "phase5_trace_events_sample_manifest.json") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "phase5_trace_events_sample_survey.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "phase5_build.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "PHASE5_LANE_KEY=P5-L16") != null);
    {
        const surveyed_commit_line = try std.fmt.allocPrint(
            std.testing.allocator,
            "PHASE5_SURVEYED_COMMIT={s}",
            .{manifest.surveyed_commit},
        );
        defer std.testing.allocator.free(surveyed_commit_line);
        try std.testing.expect(std.mem.indexOf(u8, survey_note, surveyed_commit_line) != null);
    }
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "Phase 9 runtime pilot") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "approved payload and callback idiom guidance") != null or std.mem.indexOf(u8, survey_note, "approved payload-and-callback idiom") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "reviewable and repeatable") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "samples/zigux/README.md") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "shared tests-root guide in `zigux/tests/README.md`") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "zig test samples/zigux/trace_events_sample.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "zig test zigux/tests/phase5_trace_events_sample_survey.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "surveyed_commit") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "floating branch label") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "CREATE_TRACE_POINTS") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "runStringFormattingCycleReplay()") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "no standalone `samples/zigux/*printf*`, `samples/zigux/*vsprintf*`, or `*format*` Phase 5 reference sample") != null or std.mem.indexOf(u8, survey_note, "no standalone `samples/zigux/*printf*`, `*vsprintf*`, or `*format*` Phase 5 reference sample") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "`tools/lib/vsprintf.zig`") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "`string_get_size()` helper packet") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "FunctionCallbackNotRegistered") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "before a callback is registered") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "second `registerFunctionCallback()`") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "`unregisterFunctionCallback()` underflow") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "`OutstandingRegistration`") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "replayFunctionIteration()") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "unregisterFunctionCallback()") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "Mother Goose") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "One ring to rule them all") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "counts `0` through `4`") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "five public cases") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "selected-string slot `2`") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "main iteration `7`") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "function-callback iteration `9`") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "payload length `2`") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "`lifecycleSummary()`") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "private field access") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "`checked_focus`") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "`payload_shape`") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "`ownership_and_lifetime`") != null);

    try std.testing.expect(std.mem.indexOf(u8, readme, "phase5-trace-events-sample-survey.md") != null);
    try std.testing.expect(std.mem.indexOf(u8, readme, "samples/zigux/trace_events_sample.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, readme, "Phase 9 runtime pilot tranche") != null or std.mem.indexOf(u8, readme, "Phase 9 runtime pilot") != null);

    try std.testing.expect(std.mem.indexOf(u8, sample_root_readme, "phase5_trace_events_sample_manifest.json") != null);
    try std.testing.expect(std.mem.indexOf(u8, sample_root_readme, "phase5_trace_events_sample_survey.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, sample_root_readme, "phase5-trace-events-sample-survey.md") != null);
    try std.testing.expect(std.mem.indexOf(u8, sample_root_readme, "selected-string plus `iter=%d` replay in `samples/zigux/trace_events_sample.zig`") != null);

    try std.testing.expect(std.mem.indexOf(u8, tests_readme, "zigux/tests/phase5_trace_events_sample.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, tests_readme, "zigux/tests/phase5_trace_events_sample_manifest.json") != null);
    try std.testing.expect(std.mem.indexOf(u8, tests_readme, "zigux/tests/phase5_trace_events_sample_survey.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, tests_readme, "zig build test --build-file zigux/tests/phase5_build.zig --summary all") != null);

    try std.testing.expect(std.mem.indexOf(u8, review_checklist, "trace-events") != null);
    try std.testing.expect(std.mem.indexOf(u8, review_checklist, "`checked_focus` order") != null);
    try std.testing.expect(std.mem.indexOf(u8, review_checklist, "selected-string plus `iter=%d` reminder") != null);
}
