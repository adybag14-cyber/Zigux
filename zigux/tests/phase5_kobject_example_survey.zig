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
    try std.testing.expectEqualStrings("P5-L07", manifest.lane_key);
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
    try std.testing.expectEqual(@as(usize, 13), manifest.exact_checks.len);
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
    var saw_replay_readiness = false;
    var saw_ownership_summary = false;
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
            std.mem.indexOf(u8, prompt, "shared docs-root guide") != null and
            std.mem.indexOf(u8, prompt, "shared sample-root catalog") != null and
            std.mem.indexOf(u8, prompt, "shared tests-root guide") != null and
            std.mem.indexOf(u8, prompt, "shared review checklist") != null and
            std.mem.indexOf(u8, prompt, "phase5_build.zig") != null)
        {
            saw_docs_prompt = true;
        }
        if (std.mem.indexOf(u8, prompt, "unnamed attribute group shape") != null and
            std.mem.indexOf(u8, prompt, "pre-registration ownership boundary") != null and
            std.mem.indexOf(u8, prompt, "ownershipSummary lifecycle snapshot") != null and
            std.mem.indexOf(u8, prompt, "post-exit init/register/show/store rejection boundaries") != null)
        {
            saw_group_boundary_prompt = true;
        }
        if (std.mem.indexOf(u8, prompt, "replay-readiness") != null and
            std.mem.indexOf(u8, prompt, "infer it from code alone") != null)
        {
            saw_sync_prompt = true;
        }
        if (std.mem.indexOf(u8, prompt, "initialized-but-not-registered stage explicit") != null and
            std.mem.indexOf(u8, prompt, "zero active attributes") != null and
            std.mem.indexOf(u8, prompt, "ownershipSummary must expose replay readiness plus the cold, initialized, registered, and exited stage transitions directly") != null)
        {
            saw_ownership_prompt = true;
        }
        if (std.mem.indexOf(u8, prompt, "sysfs creation") != null and
            std.mem.indexOf(u8, prompt, "kernel_kobj integration") != null and
            std.mem.indexOf(u8, prompt, "uevents") != null and
            std.mem.indexOf(u8, prompt, "module registration out of scope") != null and
            std.mem.indexOf(u8, prompt, "approved Phase 5 ownership-and-lifetime idiom") != null)
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
        if (std.mem.eql(u8, check.id, "replay-readiness-boundary")) {
            saw_replay_readiness = true;
            try expectContains(check.expected, "runAnchorReplay reviewable");
            try expectContains(check.expected, "only in the initialized stage");
            try expectContains(check.expected, "after the sample has registered or exited");
        }
        if (std.mem.eql(u8, check.id, "ownership-summary")) {
            saw_ownership_summary = true;
            try expectContains(check.expected, "replay readiness plus the cold, initialized, registered, and exited stages");
            try expectContains(check.expected, "0, 0, 3, and 0");
            try expectContains(check.expected, "register-or-exit availability");
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
            try expectContains(check.expected, "runAnchorReplay");
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
    try std.testing.expect(saw_replay_readiness);
    try std.testing.expect(saw_ownership_summary);
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

    try expectContains(survey_note, "sample-backed survey note");
    try expectContains(survey_note, "scope: roadmap-vs-repo sample reviewability, approved ownership-and-lifetime guidance, and exact bounded checks for the landed `samples/zigux/` kobject-style replay");
    try expectContains(survey_note, "- `Documentation/zigux/README.md`");
    try expectContains(survey_note, "- `Documentation/zigux/review-checklist.md`");
    try expectContains(survey_note, "- `samples/zigux/README.md`");
    try expectContains(survey_note, "- `zigux/tests/README.md`");
    try expectContains(survey_note, "phase5_kobject_example_manifest.json");
    try expectContains(survey_note, "phase5_kobject_example_survey.zig");
    try expectContains(survey_note, "phase5_build.zig");
    try expectContains(survey_note, "PHASE5_LANE_KEY=P5-L07");
    {
        const surveyed_commit_line = try std.fmt.allocPrint(
            std.testing.allocator,
            "PHASE5_SURVEYED_COMMIT={s}",
            .{manifest.surveyed_commit},
        );
        defer std.testing.allocator.free(surveyed_commit_line);
        try expectContains(survey_note, surveyed_commit_line);
    }
    try expectContains(survey_note, "shared sample-root catalog in `samples/zigux/README.md`");
    try expectContains(survey_note, "top-level docs-root guide in `Documentation/zigux/README.md`");
    try expectContains(survey_note, "shared tests-root guide in `zigux/tests/README.md`");
    try expectContains(survey_note, "direct `zig test samples/zigux/kobject_example.zig` replay");
    try expectContains(survey_note, "paired `zig test zigux/tests/phase5_kobject_example_survey.zig` replay");
    try expectContains(survey_note, "approved Phase 5 ownership-and-lifetime idiom");
    try expectContains(survey_note, "ownershipSummary()");
    try expectContains(survey_note, "replay readiness");
    try expectContains(survey_note, "cold, initialized, registered, and exited");
    try expectContains(survey_note, "registered teardown summary");
    try expectContains(survey_note, "runtime_atomic64_loader.zig");
    try expectContains(survey_note, "runtime_bitmap_loader.zig");
    try expectContains(survey_note, "runtime_kretprobe_loader.zig");
    try expectContains(survey_note, "runtime_trace_events_loader.zig");
    try expectContains(survey_note, "visibly separate from those later runtime starters");
    try expectContains(survey_note, "sysfs creation, `kernel_kobj` integration, uevents, and loadable module registration remain out of scope");
    try expectContains(survey_note, "zig test samples/zigux/kobject_example.zig");
    try expectContains(survey_note, "All 5 tests passed.");
    try expectContains(survey_note, "zig test zigux/tests/phase5_kobject_example_survey.zig");
    try expectContains(survey_note, "All 2 tests passed.");

    try expectContains(readme, "phase5-kobject-sample-survey.md");
    try expectContains(readme, "samples/zigux/kobject_example.zig");
    try expectContains(readme, "shared sample-root catalog, shared tests-root guide, shared review checklist, manifest, and shared `phase5_build.zig` entrypoint prompts");
    try expectContains(readme, "direct sample replays and paired survey replays explicit for the four shipped Phase 5 families");
    try expectContains(readme, "samples/zigux/runtime_bitmap.zig");
    try expectContains(readme, "samples/zigux/runtime_bitmap_loader.zig");
    try expectContains(readme, "sample-only blocked Phase 9 pilot");
    try expectContains(readme, "samples/zigux/runtime_trace_events_loader.zig");
    try expectContains(readme, "no `samples/zigux/*string*` Phase 5 reference sample");
    try expectContains(readme, "no `samples/zigux/*cmdline*` Phase 5 reference sample");
    try expectContains(readme, "phase7-string-helpers-slice.md");
    try expectContains(readme, "phase7-cmdline-slice.md");

    try expectContains(sample_root_readme, "Kobject review packet");
    try expectContains(sample_root_readme, "phase5_kobject_example_manifest.json");
    try expectContains(sample_root_readme, "phase5_kobject_example_survey.zig");
    try expectContains(sample_root_readme, "phase5-kobject-sample-survey.md");
    try expectContains(sample_root_readme, "approved Phase 5 in-memory ownership-and-lifetime idiom");
    try expectContains(sample_root_readme, "pre-registration zero-active-attributes boundary");
    try expectContains(sample_root_readme, "replay-readiness boundary");
    try expectContains(sample_root_readme, "initialized-only abandonment path");
    try expectContains(sample_root_readme, "registered teardown summary");
    try expectContains(sample_root_readme, "post-exit rejection boundaries");
    try expectContains(sample_root_readme, "sysfs creation, `kernel_kobj` integration, uevents, and runtime registration out of scope");
    try expectContains(sample_root_readme, "sample-only blocked Phase 9 pilot");
    try expectContains(sample_root_readme, "runtime-substrate handoff still stays blocked");
    try expectContains(sample_root_readme, "no `samples/zigux/*string*` Phase 5 reference sample");
    try expectContains(sample_root_readme, "no `samples/zigux/*cmdline*` Phase 5 reference sample");
    try expectContains(sample_root_readme, "phase7-string-helpers-slice.md");
    try expectContains(sample_root_readme, "phase7-cmdline-slice.md");
    try expectContains(sample_root_readme, "zig test zigux/tests/phase5_kobject_example_survey.zig");

    try expectContains(tests_readme, "zigux/tests/phase5_kobject_example.zig");
    try expectContains(tests_readme, "zigux/tests/phase5_kobject_example_manifest.json");
    try expectContains(tests_readme, "zigux/tests/phase5_kobject_example_survey.zig");
    try expectContains(tests_readme, "scripts/zigux/validate-phase5.py");
    try expectContains(tests_readme, "make -C zigux phase5-validate");
    try expectContains(tests_readme, "zig test samples/zigux/kobject_example.zig");
    try expectContains(tests_readme, "zig test zigux/tests/phase5_kobject_example_survey.zig");
    try expectContains(tests_readme, "keep the current Phase 5 reference-sample packet reviewable through `zigux/tests/phase5_build.zig`");
    try expectContains(tests_readme, "direct sample replays and paired survey replays explicit for every shipped Phase 5 family");
    try expectContains(tests_readme, "runtime_bitmap_top_bit_contract.zig");
    try expectContains(tests_readme, "runtime_trace_events_loader.zig");
    try expectContains(tests_readme, "no `samples/zigux/*string*` or `samples/zigux/*cmdline*` Phase 5 reference sample");
    try expectContains(tests_readme, "phase7_string_helpers.zig");
    try expectContains(tests_readme, "phase7_cmdline.zig");

    try expectContains(review_checklist, "landed Phase 5 `kobject` sample packet");
    try expectContains(review_checklist, "manifest-backed survey still pin the exact inspected `master` head");
    try expectContains(review_checklist, "approved ownership-and-lifetime idiom rather than a new runtime-substrate claim");
    try expectContains(review_checklist, "sample-backed survey note");
    try expectContains(review_checklist, "phase5_build.zig");
    try expectContains(review_checklist, "no `samples/zigux/*string*` Phase 5 reference sample");
    try expectContains(review_checklist, "no `samples/zigux/*cmdline*` Phase 5 reference sample");
    try expectContains(review_checklist, "phase7-string-helpers-slice.md");
    try expectContains(review_checklist, "phase7-cmdline-slice.md");
}
