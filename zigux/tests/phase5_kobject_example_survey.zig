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
    try std.testing.expectEqualStrings("P5-L10", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 5", manifest.phase);
    try std.testing.expectEqual(@as(usize, 40), manifest.surveyed_commit.len);
    for (manifest.surveyed_commit) |char| {
        try std.testing.expect(std.ascii.isHex(char));
        try std.testing.expect(!std.ascii.isUpper(char));
    }
    try std.testing.expectEqualStrings("samples/kobject/kobject-example.c", manifest.anchor);
    try std.testing.expectEqualStrings("samples/zigux/kobject_example.zig", manifest.sample_path);
    try std.testing.expect(std.mem.indexOf(u8, manifest.validation_entrypoint, "phase5_build.zig") != null);
    try std.testing.expectEqual(@as(usize, 8), manifest.review_prompts.len);
    try std.testing.expectEqual(@as(usize, 11), manifest.exact_checks.len);
    try std.testing.expectEqual(@as(usize, 4), manifest.non_goals.len);

    var saw_descriptor_prompt = false;
    var saw_order_prompt = false;
    var saw_mode_prompt = false;
    var saw_docs_prompt = false;
    var saw_group_boundary_prompt = false;
    var saw_pre_registration_prompt = false;
    var saw_registration_prompt = false;
    var saw_static_name_prompt = false;
    var saw_exit_terminal_prompt = false;
    var saw_directory = false;
    var saw_order = false;
    var saw_registration = false;
    var saw_mode = false;
    var saw_static_name = false;
    var saw_pre_registration = false;
    var saw_initialized_exit = false;
    var saw_dispatch = false;
    var saw_exit = false;

    for (manifest.review_prompts) |prompt| {
        try std.testing.expect(prompt.len > 0);
        if (std.mem.indexOf(u8, prompt, "requires_runtime_substrate false") != null) {
            saw_descriptor_prompt = true;
        }
        if (std.mem.indexOf(u8, prompt, "foo/baz/bar attribute order") != null) {
            saw_order_prompt = true;
        }
        if (std.mem.indexOf(u8, prompt, "single register_runs ownership claim") != null) {
            saw_registration_prompt = true;
        }
        if (std.mem.indexOf(u8, prompt, "0664 attribute mode pattern") != null) {
            saw_mode_prompt = true;
        }
        if (std.mem.indexOf(u8, prompt, "sample-backed survey note") != null and
            std.mem.indexOf(u8, prompt, "sample-root catalog") != null and
            std.mem.indexOf(u8, prompt, "review checklist") != null and
            std.mem.indexOf(u8, prompt, "phase5_build.zig") != null)
        {
            saw_docs_prompt = true;
        }
        if (std.mem.indexOf(u8, prompt, "static directory-name cue") != null and
            std.mem.indexOf(u8, prompt, "emits_uevent false") != null and
            std.mem.indexOf(u8, prompt, "dynamic kobjects stay out of scope") != null)
        {
            saw_static_name_prompt = true;
        }
        if (std.mem.indexOf(u8, prompt, "unnamed attribute group") != null and
            std.mem.indexOf(u8, prompt, "pre-registration") != null and
            std.mem.indexOf(u8, prompt, "initialized-only exit summary") != null and
            std.mem.indexOf(u8, prompt, "post-exit") != null)
        {
            saw_group_boundary_prompt = true;
        }
        if (std.mem.indexOf(u8, prompt, "initialized-but-not-registered stage") != null and
            std.mem.indexOf(u8, prompt, "registerAttributes claims ownership") != null)
        {
            saw_pre_registration_prompt = true;
        }
        if (std.mem.indexOf(u8, prompt, "teardown-summary") != null and
            std.mem.indexOf(u8, prompt, "lifecycle contract") != null)
        {
            saw_exit_terminal_prompt = true;
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
        if (std.mem.eql(u8, check.id, "attribute-order")) {
            saw_order = true;
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "foo, baz, bar") != null);
        }
        if (std.mem.eql(u8, check.id, "attribute-mode")) {
            saw_mode = true;
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "0664") != null);
        }
        if (std.mem.eql(u8, check.id, "registration-step")) {
            saw_registration = true;
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "exactly one register_runs increment") != null);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "leaves the sample registered with attributes accessible") != null);
        }
        if (std.mem.eql(u8, check.id, "static-name-no-uevent-boundary")) {
            saw_static_name = true;
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "static directory name explicit") != null);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "no uevent delivery") != null);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "dynamic kobjects out of scope") != null);
        }
        if (std.mem.eql(u8, check.id, "pre-registration-boundary")) {
            saw_pre_registration = true;
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "active attribute count at zero") != null);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "registerAttributes claims ownership") != null);
        }
        if (std.mem.eql(u8, check.id, "initialized-exit-teardown")) {
            saw_initialized_exit = true;
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "abandoned-before-registration teardown summary") != null);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "registerRuns at zero") != null);
        }
        if (std.mem.eql(u8, check.id, "shared-b-dispatch")) {
            saw_dispatch = true;
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "7 and -5") != null);
        }
        if (std.mem.eql(u8, check.id, "exit-boundary")) {
            saw_exit = true;
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "registered exit returns a teardown summary") != null);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "rejects later init, registerAttributes, showValue, or storeValue calls") != null);
        }

        for (manifest.exact_checks[i + 1 ..]) |other| {
            try std.testing.expect(!std.mem.eql(u8, check.id, other.id));
        }
    }

    try std.testing.expect(saw_descriptor_prompt);
    try std.testing.expect(saw_order_prompt);
    try std.testing.expect(saw_mode_prompt);
    try std.testing.expect(saw_docs_prompt);
    try std.testing.expect(saw_static_name_prompt);
    try std.testing.expect(saw_group_boundary_prompt);
    try std.testing.expect(saw_pre_registration_prompt);
    try std.testing.expect(saw_registration_prompt);
    try std.testing.expect(saw_exit_terminal_prompt);
    try std.testing.expect(saw_directory);
    try std.testing.expect(saw_order);
    try std.testing.expect(saw_registration);
    try std.testing.expect(saw_mode);
    try std.testing.expect(saw_static_name);
    try std.testing.expect(saw_pre_registration);
    try std.testing.expect(saw_initialized_exit);
    try std.testing.expect(saw_dispatch);
    try std.testing.expect(saw_exit);
    try std.testing.expect(std.mem.eql(u8, manifest.non_goals[0], "sysfs file creation parity"));
    try std.testing.expect(std.mem.eql(u8, manifest.non_goals[1], "kernel_kobj integration"));
}

test "phase 5 kobject contributor docs stay aligned with the shipped review surface" {
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

    const survey_note = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase5-kobject-sample-survey.md",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(survey_note);

    const review_checklist = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/review-checklist.md",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(review_checklist);

    try std.testing.expect(std.mem.indexOf(u8, survey_note, "sample-backed survey note") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "samples/zigux/README.md") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "phase5_kobject_example_manifest.json") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "phase5_kobject_example_survey.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "phase5_build.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "shared sample-root catalog in `samples/zigux/README.md` plus the shared prompts in `Documentation/zigux/review-checklist.md`") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "dedicated kobject review-packet stanza") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "PHASE5_LANE_KEY=P5-L10") != null);
    {
        const surveyed_commit_line = try std.fmt.allocPrint(
            std.testing.allocator,
            "PHASE5_SURVEYED_COMMIT={s}",
            .{manifest.surveyed_commit},
        );
        defer std.testing.allocator.free(surveyed_commit_line);
        try std.testing.expect(std.mem.indexOf(u8, survey_note, surveyed_commit_line) != null);
    }
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "unnamed attribute group shape") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "shared `0664` attribute mode pattern") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "static directory-name cue explicit") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "no uevent delivery") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "dynamic kobjects out of scope") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "initialized-but-not-registered stage keeps the active attribute count at `0`") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "initialized-only `exit()` path returns an `abandoned_before_registration` teardown summary") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "post-`exit()` `init()`, `registerAttributes()`, `showValue()`, and `storeValue()` calls all remain rejected") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "## Latest verification snapshot") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "zig test samples/zigux/kobject_example.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "zig test zigux/tests/phase5_kobject_example_survey.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "1/2 phase5_kobject_example_survey.test.phase 5 kobject manifest records the exact bounded checks...OK") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "2/2 phase5_kobject_example_survey.test.phase 5 kobject contributor docs stay aligned with the shipped review surface...OK") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "Build Summary: 17/17 steps succeeded; 27/27 tests passed") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "phase5-kobject-example-tests 5 pass (5 total)") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "phase5-kobject-example-survey-tests 2 pass (2 total)") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "The roadmap delivery gap is already closed.") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "/workspace/agent_files/") == null);
    {
        const pinned_commit_line = try std.fmt.allocPrint(
            std.testing.allocator,
            "approved ownership-and-lifetime idiom is now pinned to `PHASE5_SURVEYED_COMMIT={s}`",
            .{manifest.surveyed_commit},
        );
        defer std.testing.allocator.free(pinned_commit_line);
        try std.testing.expect(std.mem.indexOf(u8, survey_note, pinned_commit_line) != null);
    }
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "approved ownership-and-lifetime idiom inside that completed anchor set") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "shared sample-root catalog, shared review checklist, and contributor review path all point at the same inspected `master` head") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "sysfs creation, `kernel_kobj` integration, uevents, and loadable module registration remain out of scope") != null);

    try std.testing.expect(std.mem.indexOf(u8, review_checklist, "manifest-backed survey") != null);
    try std.testing.expect(std.mem.indexOf(u8, review_checklist, "sample-backed survey note") != null);
    try std.testing.expect(std.mem.indexOf(u8, review_checklist, "phase5_build.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, review_checklist, "exact replay contract") != null);
    try std.testing.expect(std.mem.indexOf(u8, review_checklist, "landed Phase 5 `kobject` sample packet") != null);
    try std.testing.expect(std.mem.indexOf(u8, review_checklist, "approved ownership-and-lifetime idiom") != null);
}
