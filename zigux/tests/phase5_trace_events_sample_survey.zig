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

fn readFile(allocator: std.mem.Allocator, path: []const u8, limit: usize) ![]u8 {
    var io_instance: std.Io.Threaded = .init(allocator, .{});
    defer io_instance.deinit();
    return std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        path,
        allocator,
        .limited(limit),
    );
}

fn manifestById(manifest: Manifest, id: []const u8) ?ExactCheck {
    for (manifest.exact_checks) |check| {
        if (std.mem.eql(u8, check.id, id)) return check;
    }
    return null;
}

fn isLowerHexCommitSha(value: []const u8) bool {
    if (value.len != 40) return false;

    for (value) |byte| {
        const is_digit = byte >= '0' and byte <= '9';
        const is_lower_hex = byte >= 'a' and byte <= 'f';
        if (!is_digit and !is_lower_hex) return false;
    }

    return true;
}

test "phase 5 trace-events manifest records the focused direct replay packet" {
    const manifest_json = try readFile(
        std.testing.allocator,
        "zigux/tests/phase5_trace_events_sample_manifest.json",
        review_doc_read_limit,
    );
    defer std.testing.allocator.free(manifest_json);

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{});
    defer parsed.deinit();

    const manifest = parsed.value;
    try std.testing.expectEqualStrings("P5-L16", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 5", manifest.phase);
    try std.testing.expect(isLowerHexCommitSha(manifest.surveyed_commit));
    try std.testing.expectEqualStrings("samples/trace_events/trace-events-sample.c", manifest.anchor);
    try std.testing.expectEqualStrings("samples/zigux/trace_events_sample.zig", manifest.sample_path);
    try std.testing.expectEqualStrings(
        "zig test zigux/tests/phase5_trace_events_sample_survey.zig",
        manifest.validation_entrypoint,
    );
    try std.testing.expectEqual(@as(usize, 10), manifest.review_prompts.len);
    try std.testing.expectEqual(@as(usize, 15), manifest.exact_checks.len);
    try std.testing.expectEqual(@as(usize, 4), manifest.non_goals.len);

    var saw_surveyed_commit_prompt = false;
    var saw_docs_prompt = false;
    var saw_direct_replay_prompt = false;
    var saw_lifecycle_prompt = false;
    var saw_cycle_prompt = false;
    var saw_callback_prompt = false;
    for (manifest.review_prompts) |prompt| {
        if (std.mem.indexOf(u8, prompt, "surveyed_commit") != null and
            std.mem.indexOf(u8, prompt, "floating branch label") != null)
        {
            saw_surveyed_commit_prompt = true;
        }
        if (std.mem.indexOf(u8, prompt, "samples/zigux/README.md") != null and
            std.mem.indexOf(u8, prompt, "Documentation/zigux/README.md") != null and
            std.mem.indexOf(u8, prompt, "Documentation/zigux/review-checklist.md") != null and
            std.mem.indexOf(u8, prompt, "Phase 9 runtime pilot") != null)
        {
            saw_docs_prompt = true;
        }
        if (std.mem.indexOf(u8, prompt, "zig test samples/zigux/trace_events_sample.zig") != null and
            std.mem.indexOf(u8, prompt, "zig test zigux/tests/phase5_trace_events_sample.zig") != null and
            std.mem.indexOf(u8, prompt, "zig test zigux/tests/phase5_trace_events_sample_survey.zig") != null and
            std.mem.indexOf(u8, prompt, "phase5_build.zig") != null)
        {
            saw_direct_replay_prompt = true;
        }
        if (std.mem.indexOf(u8, prompt, "lifecycle summary") != null and
            std.mem.indexOf(u8, prompt, "registration depth") != null and
            std.mem.indexOf(u8, prompt, "private field access") != null)
        {
            saw_lifecycle_prompt = true;
        }
        if (std.mem.indexOf(u8, prompt, "runStringFormattingCycleReplay()") != null and
            std.mem.indexOf(u8, prompt, "modulo-selected string cycle") != null and
            std.mem.indexOf(u8, prompt, "iter-format messages") != null)
        {
            saw_cycle_prompt = true;
        }
        if (std.mem.indexOf(u8, prompt, "FunctionCallbackNotRegistered") != null and
            std.mem.indexOf(u8, prompt, "OutstandingRegistration") != null and
            std.mem.indexOf(u8, prompt, "tracepoint enablement parity") != null)
        {
            saw_callback_prompt = true;
        }
    }
    try std.testing.expect(saw_surveyed_commit_prompt);
    try std.testing.expect(saw_docs_prompt);
    try std.testing.expect(saw_direct_replay_prompt);
    try std.testing.expect(saw_lifecycle_prompt);
    try std.testing.expect(saw_cycle_prompt);
    try std.testing.expect(saw_callback_prompt);

    const descriptor_check = manifestById(manifest, "descriptor-anchor") orelse return error.MissingExactCheck;
    try std.testing.expect(std.mem.indexOf(u8, descriptor_check.expected, "non-runtime reference-sample lane") != null);

    const cycle_check = manifestById(manifest, "modulo-string-cycle") orelse return error.MissingExactCheck;
    try std.testing.expect(std.mem.indexOf(u8, cycle_check.expected, "Mother Goose") != null);
    try std.testing.expect(std.mem.indexOf(u8, cycle_check.expected, "One ring to rule them all") != null);

    const callback_check = manifestById(manifest, "registration-underflow-and-armed-exit") orelse return error.MissingExactCheck;
    try std.testing.expect(std.mem.indexOf(u8, callback_check.expected, "OutstandingRegistration") != null);
    try std.testing.expect(std.mem.indexOf(u8, callback_check.expected, "unregisterFunctionCallback underflow") != null);
}

test "phase 5 trace-events survey note stays aligned with the focused direct replay packet" {
    const manifest_json = try readFile(
        std.testing.allocator,
        "zigux/tests/phase5_trace_events_sample_manifest.json",
        review_doc_read_limit,
    );
    defer std.testing.allocator.free(manifest_json);

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{});
    defer parsed.deinit();
    const manifest = parsed.value;

    const survey_note = try readFile(
        std.testing.allocator,
        "Documentation/zigux/phase5-trace-events-sample-survey.md",
        review_doc_read_limit,
    );
    defer std.testing.allocator.free(survey_note);

    const docs_readme = try readFile(
        std.testing.allocator,
        "Documentation/zigux/README.md",
        review_doc_read_limit,
    );
    defer std.testing.allocator.free(docs_readme);

    const samples_readme = try readFile(
        std.testing.allocator,
        "samples/zigux/README.md",
        review_doc_read_limit,
    );
    defer std.testing.allocator.free(samples_readme);

    const tests_readme = try readFile(
        std.testing.allocator,
        "zigux/tests/README.md",
        review_doc_read_limit,
    );
    defer std.testing.allocator.free(tests_readme);

    const review_checklist = try readFile(
        std.testing.allocator,
        "Documentation/zigux/review-checklist.md",
        32 * 1024,
    );
    defer std.testing.allocator.free(review_checklist);

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
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "sample-backed survey note") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "phase5_trace_events_sample_manifest.json") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "phase5_trace_events_sample_survey.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "zig test samples/zigux/trace_events_sample.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, manifest.validation_entrypoint) != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "phase5_build.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "selected-string slot `2`") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "main iteration `7`") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "function-callback iteration `9`") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "`checked_focus`") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "FunctionCallbackNotRegistered") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "`OutstandingRegistration`") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "tests-root shared reminder now keeps the current landed helper vocabulary aligned too") != null);

    try std.testing.expect(std.mem.indexOf(u8, docs_readme, "phase5-trace-events-sample-survey.md") != null);
    try std.testing.expect(std.mem.indexOf(u8, docs_readme, "samples/zigux/trace_events_sample.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, docs_readme, "Phase 9 runtime pilot") != null);

    try std.testing.expect(std.mem.indexOf(u8, samples_readme, "samples/zigux/trace_events_sample.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, samples_readme, "phase5_trace_events_sample_manifest.json") != null);
    try std.testing.expect(std.mem.indexOf(u8, samples_readme, "phase5_trace_events_sample_survey.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, samples_readme, "phase5_build.zig") != null);

    try std.testing.expect(std.mem.indexOf(u8, tests_readme, "zigux/tests/phase5_trace_events_sample.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, tests_readme, "zigux/tests/phase5_trace_events_sample_manifest.json") != null);
    try std.testing.expect(std.mem.indexOf(u8, tests_readme, "zigux/tests/phase5_trace_events_sample_survey.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, tests_readme, "runPayloadBoundaryReplay()") != null);
    try std.testing.expect(std.mem.indexOf(u8, tests_readme, "runCallbackBoundaryRecoveryReplay()") != null);
    try std.testing.expect(std.mem.indexOf(u8, tests_readme, "runStringFormattingCycleReplay()") != null);
    try std.testing.expect(std.mem.indexOf(u8, tests_readme, "runLifecycleBoundaryReplay()") != null);
    try std.testing.expect(std.mem.indexOf(u8, tests_readme, "lifecycleSummary()") != null);
    try std.testing.expect(std.mem.indexOf(u8, tests_readme, "selected-string plus `iter=%d`") != null);
    try std.testing.expect(std.mem.indexOf(u8, tests_readme, "OutstandingRegistration") != null);

    try std.testing.expect(std.mem.indexOf(u8, review_checklist, "trace-events") != null);
    try std.testing.expect(std.mem.indexOf(u8, review_checklist, "`checked_focus` order") != null);
    try std.testing.expect(std.mem.indexOf(u8, review_checklist, "selected-string plus `iter=%d` reminder") != null);
}
