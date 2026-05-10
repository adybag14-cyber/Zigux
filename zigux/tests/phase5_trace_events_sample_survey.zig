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

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn isLowerHexCommitSha(value: []const u8) bool {
    if (value.len != 40) return false;

    for (value) |byte| {
        if (!std.ascii.isDigit(byte) and (byte < 'a' or byte > 'f')) {
            return false;
        }
    }

    return true;
}

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
    try std.testing.expectEqualStrings("P5-L24", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 5", manifest.phase);
    try std.testing.expect(isLowerHexCommitSha(manifest.surveyed_commit));
    try std.testing.expectEqualStrings("samples/trace_events/trace-events-sample.c", manifest.anchor);
    try std.testing.expectEqualStrings("samples/zigux/trace_events_sample.zig", manifest.sample_path);
    try expectContains(manifest.validation_entrypoint, "phase5_build.zig");
    try std.testing.expectEqual(@as(usize, 10), manifest.review_prompts.len);
    try std.testing.expectEqual(@as(usize, 10), manifest.exact_checks.len);
    try std.testing.expectEqual(@as(usize, 4), manifest.non_goals.len);

    const build_zig = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase5_build.zig",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(build_zig);

    try expectContains(build_zig, "../../samples/zigux/trace_events_sample.zig");
    try expectContains(build_zig, "phase5_trace_events_sample_survey.zig");
    try expectContains(build_zig, "phase5-trace-events-sample-survey-tests");
    try expectContains(build_zig, "run_phase5_trace_events_sample_tests.step");
    try expectContains(build_zig, "run_phase5_trace_events_sample_survey_tests.step");

    var saw_descriptor_prompt = false;
    var saw_payload_prompt = false;
    var saw_formatted_surface_prompt = false;
    var saw_public_payload_prompt = false;
    var saw_public_conditional_prompt = false;
    var saw_callback_prompt = false;
    var saw_callback_boundary_prompt = false;
    var saw_ownership_replay_prompt = false;
    var saw_contract_prompt = false;
    var saw_non_goal_prompt = false;
    var saw_descriptor_check = false;
    var saw_message_check = false;
    var saw_array_check = false;
    var saw_public_payload_helper_check = false;
    var saw_public_conditional_helper_check = false;
    var saw_rel_loc_check = false;
    var saw_vararg_check = false;
    var saw_counts_check = false;
    var saw_callback_balance_check = false;
    var saw_exit_check = false;

    for (manifest.review_prompts) |prompt| {
        try std.testing.expect(prompt.len > 0);
        if (std.mem.indexOf(u8, prompt, "requires_runtime_substrate false") != null) {
            saw_descriptor_prompt = true;
        }
        if (std.mem.indexOf(u8, prompt, "vararg-payload") != null and
            std.mem.indexOf(u8, prompt, "relative-location") != null and
            std.mem.indexOf(u8, prompt, "callback-path") != null)
        {
            saw_payload_prompt = true;
        }
        if (std.mem.indexOf(u8, prompt, "formattedMessage()") != null and
            std.mem.indexOf(u8, prompt, "private message storage") != null)
        {
            saw_formatted_surface_prompt = true;
        }
        if (std.mem.indexOf(u8, prompt, "runPayloadBoundaryReplay()") != null and
            std.mem.indexOf(u8, prompt, "private field inspection") != null)
        {
            saw_public_payload_prompt = true;
        }
        if (std.mem.indexOf(u8, prompt, "runConditionalBoundaryReplay()") != null and
            std.mem.indexOf(u8, prompt, "0..5 selected-string") != null and
            std.mem.indexOf(u8, prompt, "Snoopy") != null and
            std.mem.indexOf(u8, prompt, "One ring to rule them all") != null and
            std.mem.indexOf(u8, prompt, "private sample-state reads") != null)
        {
            saw_public_conditional_prompt = true;
        }
        if (std.mem.indexOf(u8, prompt, "register-then-unregister") != null and
            std.mem.indexOf(u8, prompt, "kthread") != null)
        {
            saw_callback_prompt = true;
        }
        if (std.mem.indexOf(u8, prompt, "checked_focus") != null and
            std.mem.indexOf(u8, prompt, "OutstandingRegistration") != null and
            std.mem.indexOf(u8, prompt, "post-exit replay rejection") != null)
        {
            saw_callback_boundary_prompt = true;
        }
        if (std.mem.indexOf(u8, prompt, "runOwnershipReplay()") != null and
            std.mem.indexOf(u8, prompt, "`cold` -> `initialized` -> `replay_complete` -> `exited`") != null and
            std.mem.indexOf(u8, prompt, "post-exit rejection") != null)
        {
            saw_ownership_replay_prompt = true;
        }
        if (std.mem.indexOf(u8, prompt, "manifest-backed replay contract") != null and
            std.mem.indexOf(u8, prompt, "infer the new boundary from code alone") != null)
        {
            saw_contract_prompt = true;
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

        if (std.mem.eql(u8, check.id, "descriptor-anchor")) {
            saw_descriptor_check = true;
            try expectContains(check.expected, "samples/trace_events/trace-events-sample.c");
            try expectContains(check.expected, "non-runtime reference-sample lane");
        }
        if (std.mem.eql(u8, check.id, "message-and-string-shape")) {
            saw_message_check = true;
            try expectContains(check.expected, "iter=7");
            try expectContains(check.expected, "Gandalf");
        }
        if (std.mem.eql(u8, check.id, "array-and-sentinel-shape")) {
            saw_array_check = true;
            try expectContains(check.expected, "1,2 payload prefix");
            try expectContains(check.expected, "zero sentinel");
        }
        if (std.mem.eql(u8, check.id, "public-payload-boundary-helper")) {
            saw_public_payload_helper_check = true;
            try expectContains(check.expected, "runPayloadBoundaryReplay");
            try expectContains(check.expected, "One ring to rule them all");
            try expectContains(check.expected, "private sample-state reads");
        }
        if (std.mem.eql(u8, check.id, "public-conditional-boundary-helper")) {
            saw_public_conditional_helper_check = true;
            try expectContains(check.expected, "runConditionalBoundaryReplay");
            try expectContains(check.expected, "0..5 selected-string");
            try expectContains(check.expected, "Mother Goose");
            try expectContains(check.expected, "Snoopy");
            try expectContains(check.expected, "Gandalf");
            try expectContains(check.expected, "Frodo");
            try expectContains(check.expected, "One ring to rule them all");
            try expectContains(check.expected, "count-5 wraparound back to Mother Goose");
            try expectContains(check.expected, "0xdeadbeef");
            try expectContains(check.expected, "private sample-state reads");
        }
        if (std.mem.eql(u8, check.id, "bitmask-and-rel-loc")) {
            saw_rel_loc_check = true;
            try expectContains(check.expected, "0xdeadbeef");
            try expectContains(check.expected, "relative-location");
        }
        if (std.mem.eql(u8, check.id, "vararg-payload-path")) {
            saw_vararg_check = true;
            try expectContains(check.expected, "vararg payload");
            try expectContains(check.expected, "va_list");
        }
        if (std.mem.eql(u8, check.id, "event-family-counts")) {
            saw_counts_check = true;
            try expectContains(check.expected, "six");
            try expectContains(check.expected, "eight");
        }
        if (std.mem.eql(u8, check.id, "callback-registration-balance")) {
            saw_callback_balance_check = true;
            try expectContains(check.expected, "callback path");
            try expectContains(check.expected, "zero");
        }
        if (std.mem.eql(u8, check.id, "post-exit-rejection")) {
            saw_exit_check = true;
            try expectContains(check.expected, "after exit");
        }

        for (manifest.exact_checks[i + 1 ..]) |other| {
            try std.testing.expect(!std.mem.eql(u8, check.id, other.id));
        }
    }

    try std.testing.expect(saw_descriptor_prompt);
    try std.testing.expect(saw_payload_prompt);
    try std.testing.expect(saw_formatted_surface_prompt);
    try std.testing.expect(saw_public_payload_prompt);
    try std.testing.expect(saw_public_conditional_prompt);
    try std.testing.expect(saw_callback_prompt);
    try std.testing.expect(saw_callback_boundary_prompt);
    try std.testing.expect(saw_ownership_replay_prompt);
    try std.testing.expect(saw_contract_prompt);
    try std.testing.expect(saw_non_goal_prompt);
    try std.testing.expect(saw_descriptor_check);
    try std.testing.expect(saw_message_check);
    try std.testing.expect(saw_array_check);
    try std.testing.expect(saw_public_payload_helper_check);
    try std.testing.expect(saw_public_conditional_helper_check);
    try std.testing.expect(saw_rel_loc_check);
    try std.testing.expect(saw_vararg_check);
    try std.testing.expect(saw_counts_check);
    try std.testing.expect(saw_callback_balance_check);
    try std.testing.expect(saw_exit_check);
    try std.testing.expect(std.mem.eql(u8, manifest.non_goals[0], "CREATE_TRACE_POINTS parity"));
    try std.testing.expect(std.mem.eql(u8, manifest.non_goals[1], "tracepoint macro parity from trace-events-sample.h"));
    try std.testing.expect(std.mem.eql(u8, manifest.non_goals[2], "kernel thread scheduling or timeout parity"));
    try std.testing.expect(std.mem.eql(u8, manifest.non_goals[3], "module registration or unregister wiring parity"));
}

test "phase 5 trace-events survey packet stays repo-local and keeps shared review surfaces explicit" {
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
        "samples/trace_events/trace-events-sample.c|PHASE5_LANE_KEY={s}|PHASE5_SURVEYED_COMMIT={s}|Phase 5",
        .{ manifest.lane_key, manifest.surveyed_commit },
    );

    const survey_note = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase5-trace-events-sample-survey.md",
        std.testing.allocator,
        .limited(64 * 1024),
    );
    defer std.testing.allocator.free(survey_note);

    const required_survey_markers = [_][]const u8{
        "PHASE5_STATUS=parked",
        "PHASE5_SLICE=trace-events-reference-sample-starter",
        "Documentation/zigux/phase5-sample-review-guide.md",
        "samples/zigux/README.md",
        "scripts/zigux/README.md",
        "zigux/tests/README.md",
        "zig build test --build-file zigux/tests/phase5_build.zig --summary all",
        "make -C zigux phase5-test",
        "make -C zigux phase5",
        "runtime_trace_events",
        "## Latest verification snapshot",
        "`zig fmt --check zigux/tests/phase5_trace_events_sample_survey.zig`",
        "`zig test --test-no-exec zigux/tests/phase5_trace_events_sample_survey.zig`",
        "compile-only recheck of the manifest-backed survey gate",
        "the exact `checked_focus` order plus the `unregisterFunctionCallback()` underflow, `OutstandingRegistration`, and post-exit replay-rejection cues explicit",
        "no standalone `samples/zigux/*printf*`, `*vsprintf*`, or `*format*` Phase 5 reference sample",
        "selected-string plus `iter=%d` replay in `samples/zigux/trace_events_sample.zig`",
        "closed Phase 1 `tools/lib/vsprintf.zig` packet plus the bounded Phase 7 `string_get_size()` helper packet",
        "shared docs-root, sample-root, scripts-root, tests-root, and Phase 5 guide packet should stay explicit here too",
    };

    for (required_survey_markers) |needle| {
        try expectContains(survey_note, needle);
    }

    try expectContains(survey_note, lane_key_marker);
    try expectContains(survey_note, surveyed_commit_marker);
    try expectContains(survey_note, review_gate_marker);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "/workspace/agent_files") == null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "## Latest verification posture") == null);

    const docs_root = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/README.md",
        std.testing.allocator,
        .limited(128 * 1024),
    );
    defer std.testing.allocator.free(docs_root);

    const docs_root_markers = [_][]const u8{
        "Documentation/zigux/phase5-trace-events-sample-survey.md",
        "samples/zigux/trace_events_sample.zig",
        "payload, string-selection, formatted-message, public payload-boundary, conditional-family, callback-boundary, and ownership-lifetime replay checks",
        "sample-backed contributor guide",
        "no standalone `samples/zigux/*printf*`, `*vsprintf*`, or `*format*` Phase 5 reference sample",
        "selected-string plus `iter=%d` replay in `samples/zigux/trace_events_sample.zig`",
        "closed Phase 1 `tools/lib/vsprintf.zig` packet plus the bounded Phase 7 `string_get_size()` helper packet",
        "Phase 9 runtime pilot tranche",
    };

    for (docs_root_markers) |needle| {
        try expectContains(docs_root, needle);
    }

    const review_checklist = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/review-checklist.md",
        std.testing.allocator,
        .limited(128 * 1024),
    );
    defer std.testing.allocator.free(review_checklist);

    const checklist_markers = [_][]const u8{
        "landed Phase 5 `trace-events` sample packet",
        "formattedMessage()",
        "exact `checked_focus` order",
        "registration-first callback replay plus registration-balance cues",
        "`unregisterFunctionCallback()` underflow plus `OutstandingRegistration` rejection",
        "post-exit replay rejection",
        "no standalone `samples/zigux/*printf*`, `*vsprintf*`, or `*format*` Phase 5 reference sample",
        "selected-string plus `iter=%d` replay in `samples/zigux/trace_events_sample.zig` remains the approved formatting idiom cue",
        "if the change updates a landed Phase 5 sample, does it update the directly coupled survey note or manifest-backed contributor prompts when the sample contract changes?",
    };

    for (checklist_markers) |needle| {
        try expectContains(review_checklist, needle);
    }

    const samples_root = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "samples/zigux/README.md",
        std.testing.allocator,
        .limited(128 * 1024),
    );
    defer std.testing.allocator.free(samples_root);

    const samples_root_markers = [_][]const u8{
        "samples/zigux/trace_events_sample.zig",
        "approved tracing-plus-ownership idiom",
        "runPayloadBoundaryReplay()",
        "runCallbackBoundaryReplay()",
        "phase5_trace_events_sample_survey.zig",
        "no standalone `samples/zigux/*printf*`, `*vsprintf*`, or `*format*` reference sample",
        "selected-string plus `iter=%d` replay in `samples/zigux/trace_events_sample.zig`",
        "closed Phase 1 `tools/lib/vsprintf.zig` packet plus the bounded Phase 7 `string_get_size()` helper packet",
        "runtime_trace_events",
    };

    for (samples_root_markers) |needle| {
        try expectContains(samples_root, needle);
    }

    const review_guide = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase5-sample-review-guide.md",
        std.testing.allocator,
        .limited(64 * 1024),
    );
    defer std.testing.allocator.free(review_guide);

    const review_guide_markers = [_][]const u8{
        "### `trace_events_sample`",
        "`Documentation/zigux/phase5-trace-events-sample-survey.md`",
        "`zigux/tests/phase5_trace_events_sample.zig`",
        "`zigux/tests/phase5_trace_events_sample_manifest.json`",
        "`zigux/tests/phase5_trace_events_sample_survey.zig`",
        "`formattedMessage()`, the selected-string plus `iter=%d` replay",
        "`runPayloadBoundaryReplay()` formatting cue",
        "`runConditionalBoundaryReplay()` helper",
        "`runCallbackBoundaryReplay()` helper",
        "exact `checked_focus` order",
        "restored registration balance",
        "`unregisterFunctionCallback()` underflow plus `OutstandingRegistration` rejection",
        "post-exit replay and callback-registration rejection",
        "docs-root and sample-root contributor surfaces",
        "Phase 5-versus-Phase 9 cues",
        "no standalone `samples/zigux/*printf*`, `*vsprintf*`, or `*format*` Phase 5 reference sample",
    };

    for (review_guide_markers) |needle| {
        try expectContains(review_guide, needle);
    }

    const tests_root = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/README.md",
        std.testing.allocator,
        .limited(256 * 1024),
    );
    defer std.testing.allocator.free(tests_root);

    const tests_root_markers = [_][]const u8{
        "keep the landed Phase 5 `trace_events_sample` packet explicit in the tests root too",
        "Documentation/zigux/phase5-trace-events-sample-survey.md",
        "samples/zigux/trace_events_sample.zig",
        "zigux/tests/phase5_trace_events_sample_manifest.json",
        "zigux/tests/phase5_trace_events_sample.zig",
        "zigux/tests/phase5_trace_events_sample_survey.zig",
        "non-runtime selected-string",
        "relative-location",
        "vararg-payload",
        "balanced register-then-unregister callback cues",
        "public `runPayloadBoundaryReplay()` helper",
        "separate Phase 9 `runtime_trace_events` family",
    };

    for (tests_root_markers) |needle| {
        try expectContains(tests_root, needle);
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
        "Documentation/zigux/phase5-sample-review-guide.md",
        "Documentation/zigux/phase5-trace-events-sample-survey.md",
        "samples/zigux/trace_events_sample.zig",
        "zigux/tests/phase5_trace_events_sample_manifest.json",
        "zigux/tests/phase5_trace_events_sample_survey.zig",
        "zigux/tests/phase5_build.zig",
    };

    for (scripts_root_markers) |needle| {
        try expectContains(scripts_root, needle);
    }

    const build_zig = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase5_build.zig",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(build_zig);

    const build_markers = [_][]const u8{
        "../../samples/zigux/trace_events_sample.zig",
        "phase5_trace_events_sample_survey.zig",
        "phase5-trace-events-sample-tests",
        "phase5-trace-events-sample-survey-tests",
        "run_phase5_trace_events_sample_tests.step",
        "run_phase5_trace_events_sample_survey_tests.step",
    };

    for (build_markers) |needle| {
        try expectContains(build_zig, needle);
    }

    const makefile = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/Makefile",
        std.testing.allocator,
        .limited(64 * 1024),
    );
    defer std.testing.allocator.free(makefile);

    const makefile_markers = [_][]const u8{
        "PHONY += phase5-test phase5",
        "phase5-test:",
        "$(ZIG) build test --build-file zigux/tests/phase5_build.zig --summary all",
        "phase5: phase5-test",
    };

    for (makefile_markers) |needle| {
        try expectContains(makefile, needle);
    }

    const workflow = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        ".github/workflows/zigux-bootstrap.yml",
        std.testing.allocator,
        .limited(256 * 1024),
    );
    defer std.testing.allocator.free(workflow);

    const workflow_markers = [_][]const u8{
        "Run Phase 5 reference sample tests",
        "zig build test --build-file zigux/tests/phase5_build.zig --summary all",
        "Documentation/zigux/**",
        "samples/zigux/README.md",
        "zigux/**",
    };

    for (workflow_markers) |needle| {
        try expectContains(workflow, needle);
    }
}

test "phase 5 trace-events survey packet keeps the formatting boundary aligned" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const survey_note = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase5-trace-events-sample-survey.md",
        std.testing.allocator,
        .limited(64 * 1024),
    );
    defer std.testing.allocator.free(survey_note);

    const sample_root_readme = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "samples/zigux/README.md",
        std.testing.allocator,
        .limited(64 * 1024),
    );
    defer std.testing.allocator.free(sample_root_readme);

    try expectContains(survey_note, "no standalone `samples/zigux/*printf*`, `*vsprintf*`, or `*format*` Phase 5 reference sample");
    try expectContains(survey_note, "selected-string plus `iter=%d` replay in `samples/zigux/trace_events_sample.zig`");
    try expectContains(survey_note, "closed Phase 1 `tools/lib/vsprintf.zig` packet plus the bounded Phase 7 `string_get_size()` helper packet");

    try expectContains(sample_root_readme, "phase5_trace_events_sample_survey.zig");
    try expectContains(sample_root_readme, "phase5-trace-events-sample-survey.md");
    try expectContains(sample_root_readme, "no standalone `samples/zigux/*printf*`, `*vsprintf*`, or `*format*` reference sample");
    try expectContains(sample_root_readme, "selected-string plus `iter=%d` replay in `samples/zigux/trace_events_sample.zig`");
    try expectContains(sample_root_readme, "closed Phase 1 `tools/lib/vsprintf.zig` packet plus the bounded Phase 7 `string_get_size()` helper packet");
}
