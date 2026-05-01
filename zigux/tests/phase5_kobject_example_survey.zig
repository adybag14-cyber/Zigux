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

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

test "phase 5 kobject manifest records the exact bounded checks" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const manifest_json = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase5_kobject_example_manifest.json",
        std.testing.allocator,
        .limited(review_doc_read_limit),
    );
    defer std.testing.allocator.free(manifest_json);

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{});
    defer parsed.deinit();

    const manifest = parsed.value;
    try std.testing.expectEqualStrings("P5-L12", manifest.lane_key);
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
    var saw_contract_prompt = false;
    var saw_static_name_prompt = false;
    var saw_docs_prompt = false;
    var saw_group_boundary_prompt = false;
    var saw_sync_prompt = false;
    var saw_ownership_prompt = false;
    var saw_non_goal_prompt = false;
    var saw_directory = false;
    var saw_order = false;
    var saw_mode = false;
    var saw_registration = false;
    var saw_static_name = false;
    var saw_pre_registration = false;
    var saw_initialized_exit = false;
    var saw_foo_roundtrip = false;
    var saw_dispatch = false;
    var saw_parse_failure = false;
    var saw_exit = false;

    for (manifest.review_prompts) |prompt| {
        try std.testing.expect(prompt.len > 0);
        if (std.mem.indexOf(u8, prompt, "requires_runtime_substrate false") != null and
            std.mem.indexOf(u8, prompt, "provides_selfcheck stays true") != null)
        {
            saw_descriptor_prompt = true;
        }
        if (std.mem.indexOf(u8, prompt, "single register_runs ownership claim") != null and
            std.mem.indexOf(u8, prompt, "Linux foo/baz/bar attribute order") != null and
            std.mem.indexOf(u8, prompt, "shared 0664 attribute mode pattern") != null)
        {
            saw_contract_prompt = true;
        }
        if (std.mem.indexOf(u8, prompt, "static directory-name cue") != null and
            std.mem.indexOf(u8, prompt, "emits_uevent false") != null and
            std.mem.indexOf(u8, prompt, "dynamic kobjects stay out of scope") != null)
        {
            saw_static_name_prompt = true;
        }
        if (std.mem.indexOf(u8, prompt, "sample-backed survey note") != null and
            std.mem.indexOf(u8, prompt, "shared sample-root catalog") != null and
            std.mem.indexOf(u8, prompt, "shared tests-root guide") != null and
            std.mem.indexOf(u8, prompt, "shared review checklist") != null and
            std.mem.indexOf(u8, prompt, "phase5_build.zig") != null)
        {
            saw_docs_prompt = true;
        }
        if (std.mem.indexOf(u8, prompt, "unnamed attribute group shape") != null and
            std.mem.indexOf(u8, prompt, "pre-registration ownership boundary") != null and
            std.mem.indexOf(u8, prompt, "initialized-only exit summary") != null and
            std.mem.indexOf(u8, prompt, "post-exit init/register/show/store rejection boundaries") != null)
        {
            saw_group_boundary_prompt = true;
        }
        if (std.mem.indexOf(u8, prompt, "sample-behavior changes update the manifest-backed") != null and
            std.mem.indexOf(u8, prompt, "infer it from code alone") != null)
        {
            saw_sync_prompt = true;
        }
        if (std.mem.indexOf(u8, prompt, "initialized-but-not-registered stage explicit") != null and
            std.mem.indexOf(u8, prompt, "zero active attributes") != null and
            std.mem.indexOf(u8, prompt, "registerAttributes claims ownership") != null)
        {
            saw_ownership_prompt = true;
        }
        if (std.mem.indexOf(u8, prompt, "sysfs creation") != null and
            std.mem.indexOf(u8, prompt, "kernel_kobj integration") != null and
            std.mem.indexOf(u8, prompt, "uevents") != null and
            std.mem.indexOf(u8, prompt, "module registration out of scope") != null)
        {
            saw_non_goal_prompt = true;
        }
    }

    for (manifest.exact_checks, 0..) |check, i| {
        try std.testing.expect(check.id.len > 0);
        try std.testing.expect(check.kind.len > 0);
        try std.testing.expect(check.expected.len > 0);

        if (std.mem.eql(u8, check.id, "directory-name")) {
            saw_directory = true;
            try expectContains(check.expected, "kobject_example");
            try expectContains(check.expected, "unnamed attribute group");
        }
        if (std.mem.eql(u8, check.id, "attribute-order")) {
            saw_order = true;
            try expectContains(check.expected, "foo, baz, bar");
        }
        if (std.mem.eql(u8, check.id, "attribute-mode")) {
            saw_mode = true;
            try expectContains(check.expected, "0664");
        }
        if (std.mem.eql(u8, check.id, "registration-step")) {
            saw_registration = true;
            try expectContains(check.expected, "exactly one register_runs increment");
            try expectContains(check.expected, "registers exactly three attributes");
            try expectContains(check.expected, "attributes accessible");
        }
        if (std.mem.eql(u8, check.id, "static-name-no-uevent-boundary")) {
            saw_static_name = true;
            try expectContains(check.expected, "static directory name explicit");
            try expectContains(check.expected, "no uevent delivery");
            try expectContains(check.expected, "dynamic kobjects out of scope");
        }
        if (std.mem.eql(u8, check.id, "pre-registration-boundary")) {
            saw_pre_registration = true;
            try expectContains(check.expected, "active attribute count at zero");
            try expectContains(check.expected, "registerAttributes claims ownership");
        }
        if (std.mem.eql(u8, check.id, "initialized-exit-teardown")) {
            saw_initialized_exit = true;
            try expectContains(check.expected, "abandoned-before-registration teardown summary");
            try expectContains(check.expected, "registerRuns at zero");
        }
        if (std.mem.eql(u8, check.id, "foo-roundtrip")) {
            saw_foo_roundtrip = true;
            try expectContains(check.expected, "42 followed by a newline");
        }
        if (std.mem.eql(u8, check.id, "shared-b-dispatch")) {
            saw_dispatch = true;
            try expectContains(check.expected, "7 and -5");
            try expectContains(check.expected, "their own attribute names");
        }
        if (std.mem.eql(u8, check.id, "parse-failure")) {
            saw_parse_failure = true;
            try expectContains(check.expected, "InvalidInteger");
            try expectContains(check.expected, "unknown attribute names");
        }
        if (std.mem.eql(u8, check.id, "exit-boundary")) {
            saw_exit = true;
            try expectContains(check.expected, "registered exit returns a teardown summary");
            try expectContains(check.expected, "rejects later init, registerAttributes, showValue, or storeValue calls");
        }

        for (manifest.exact_checks[i + 1 ..]) |other| {
            try std.testing.expect(!std.mem.eql(u8, check.id, other.id));
        }
    }

    try std.testing.expect(saw_descriptor_prompt);
    try std.testing.expect(saw_contract_prompt);
    try std.testing.expect(saw_static_name_prompt);
    try std.testing.expect(saw_docs_prompt);
    try std.testing.expect(saw_group_boundary_prompt);
    try std.testing.expect(saw_sync_prompt);
    try std.testing.expect(saw_ownership_prompt);
    try std.testing.expect(saw_non_goal_prompt);
    try std.testing.expect(saw_directory);
    try std.testing.expect(saw_order);
    try std.testing.expect(saw_mode);
    try std.testing.expect(saw_registration);
    try std.testing.expect(saw_static_name);
    try std.testing.expect(saw_pre_registration);
    try std.testing.expect(saw_initialized_exit);
    try std.testing.expect(saw_foo_roundtrip);
    try std.testing.expect(saw_dispatch);
    try std.testing.expect(saw_parse_failure);
    try std.testing.expect(saw_exit);
    try std.testing.expect(std.mem.eql(u8, manifest.non_goals[0], "sysfs file creation parity"));
    try std.testing.expect(std.mem.eql(u8, manifest.non_goals[1], "kernel_kobj integration"));
    try std.testing.expect(std.mem.eql(u8, manifest.non_goals[2], "uevent delivery"));
    try std.testing.expect(std.mem.eql(u8, manifest.non_goals[3], "loadable module registration"));
}

test "phase 5 kobject contributor docs stay aligned with the shipped review surface" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const manifest_json = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase5_kobject_example_manifest.json",
        std.testing.allocator,
        .limited(review_doc_read_limit),
    );
    defer std.testing.allocator.free(manifest_json);

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{});
    defer parsed.deinit();

    const manifest = parsed.value;

    const survey_note = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase5-kobject-sample-survey.md",
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

    const review_checklist = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/review-checklist.md",
        std.testing.allocator,
        .limited(review_doc_read_limit),
    );
    defer std.testing.allocator.free(review_checklist);

    try expectContains(survey_note, "sample-backed survey note");
    try expectContains(survey_note, "samples/zigux/README.md");
    try expectContains(survey_note, "Documentation/zigux/review-checklist.md");
    try expectContains(survey_note, "phase5_kobject_example_manifest.json");
    try expectContains(survey_note, "phase5_kobject_example_survey.zig");
    try expectContains(survey_note, "phase5_build.zig");
    try expectContains(survey_note, "PHASE5_LANE_KEY=P5-L12");
    {
        const surveyed_commit_line = try std.fmt.allocPrint(
            std.testing.allocator,
            "PHASE5_SURVEYED_COMMIT={s}",
            .{manifest.surveyed_commit},
        );
        defer std.testing.allocator.free(surveyed_commit_line);
        try expectContains(survey_note, surveyed_commit_line);
    }
    try expectContains(survey_note, "shared sample-root catalog in `samples/zigux/README.md` plus the shared prompts in `Documentation/zigux/review-checklist.md`");
    try expectContains(survey_note, "dedicated kobject review-packet stanza");
    try expectContains(survey_note, "Linux `foo`/`baz`/`bar` attribute-array order");
    try expectContains(survey_note, "shared `0664` attribute mode pattern");
    try expectContains(survey_note, "initialized-but-not-registered ownership boundary");
    try expectContains(survey_note, "abandoned_before_registration");
    try expectContains(survey_note, "zig fmt --check samples/zigux/kobject_example.zig zigux/tests/phase5_kobject_example_survey.zig");
    try expectContains(survey_note, "zig test samples/zigux/kobject_example.zig");
    try expectContains(survey_note, "All 3 tests passed.");
    try expectContains(survey_note, "zig test zigux/tests/phase5_kobject_example_survey.zig");
    try expectContains(survey_note, "All 2 tests passed.");
    try expectContains(survey_note, "did not rerun the whole Phase 5 sample bundle");
    {
        const pinned_commit_line = try std.fmt.allocPrint(
            std.testing.allocator,
            "this approved ownership-and-lifetime idiom is now pinned to `PHASE5_SURVEYED_COMMIT={s}`",
            .{manifest.surveyed_commit},
        );
        defer std.testing.allocator.free(pinned_commit_line);
        try expectContains(survey_note, pinned_commit_line);
    }

    try expectContains(readme, "phase5-kobject-sample-survey.md");
    try expectContains(readme, "samples/zigux/kobject_example.zig");
    try expectContains(readme, "exact registration");
    try expectContains(readme, "Linux `foo`/`baz`/`bar` attribute-order");
    try expectContains(readme, "attribute-roundtrip checks");
    try expectContains(readme, "sysfs creation, `kernel_kobj`, uevents, and module registration");
    try expectContains(readme, "sample-backed contributor guide for the landed kobject slice");

    try expectContains(sample_root_readme, "Kobject review packet");
    try expectContains(sample_root_readme, "phase5_kobject_example_manifest.json");
    try expectContains(sample_root_readme, "phase5_kobject_example_survey.zig");
    try expectContains(sample_root_readme, "phase5-kobject-sample-survey.md");
    try expectContains(sample_root_readme, "Linux `foo` or `baz` or `bar` attribute order");
    try expectContains(sample_root_readme, "shared `0664` mode pattern");
    try expectContains(sample_root_readme, "unnamed attribute-group shape");
    try expectContains(sample_root_readme, "initialized-only abandonment path");
    try expectContains(sample_root_readme, "runtime sysfs claim");

    try expectContains(review_checklist, "manifest-backed survey");
    try expectContains(review_checklist, "sample-backed survey note");
    try expectContains(review_checklist, "phase5_build.zig");
    try expectContains(review_checklist, "landed Phase 5 `kobject` sample packet");
    try expectContains(review_checklist, "exact reviewed commit");
    try expectContains(review_checklist, "approved ownership-and-lifetime idiom");
}
