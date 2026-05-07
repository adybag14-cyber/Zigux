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
    try std.testing.expect(isLowerHexCommitSha(manifest.surveyed_commit));
    try std.testing.expectEqualStrings("samples/kobject/kobject-example.c", manifest.anchor);
    try std.testing.expectEqualStrings("samples/zigux/kobject_example.zig", manifest.sample_path);
    try std.testing.expect(std.mem.indexOf(u8, manifest.validation_entrypoint, "phase5_build.zig") != null);
    try std.testing.expectEqual(@as(usize, 8), manifest.review_prompts.len);
    try std.testing.expectEqual(@as(usize, 9), manifest.exact_checks.len);
    try std.testing.expectEqual(@as(usize, 4), manifest.non_goals.len);

    var saw_descriptor_prompt = false;
    var saw_approved_idiom_prompt = false;
    var saw_pre_registration_prompt = false;
    var saw_ownership_summary_prompt = false;
    var saw_exit_prompt = false;
    var saw_group_boundary_prompt = false;
    var saw_directory = false;
    var saw_pre_registration = false;
    var saw_ownership_summary = false;
    var saw_initialized_exit = false;
    var saw_dispatch = false;
    var saw_exit = false;

    for (manifest.review_prompts) |prompt| {
        try std.testing.expect(prompt.len > 0);
        if (std.mem.indexOf(u8, prompt, "requires_runtime_substrate false") != null) {
            saw_descriptor_prompt = true;
        }
        if (std.mem.indexOf(u8, prompt, "approved Phase 5 in-memory ownership-and-lifetime idiom") != null) {
            saw_approved_idiom_prompt = true;
        }
        if (std.mem.indexOf(u8, prompt, "runPreRegistrationBoundaryReplay()") != null and
            std.mem.indexOf(u8, prompt, "initialized-but-not-registered") != null)
        {
            saw_pre_registration_prompt = true;
        }
        if (std.mem.indexOf(u8, prompt, "ownershipSummary()") != null and
            std.mem.indexOf(u8, prompt, "cold, initialized, registered, and exited") != null)
        {
            saw_ownership_summary_prompt = true;
        }
        if (std.mem.indexOf(u8, prompt, "abandoned_before_registration") != null and
            std.mem.indexOf(u8, prompt, "tore_down_registered_attributes") != null)
        {
            saw_exit_prompt = true;
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
        if (std.mem.eql(u8, check.id, "pre-registration-boundary")) {
            saw_pre_registration = true;
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "runPreRegistrationBoundaryReplay()") != null);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "activeAttrCount") != null);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "InvalidLifecycleTransition") != null);
        }
        if (std.mem.eql(u8, check.id, "ownership-summary")) {
            saw_ownership_summary = true;
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "ownershipSummary()") != null);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "runOwnershipReplay()") != null);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "cold, initialized, registered, and exited") != null);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "0, 0, 3, and 0") != null);
        }
        if (std.mem.eql(u8, check.id, "initialized-exit-disposition")) {
            saw_initialized_exit = true;
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "abandoned_before_registration") != null);
        }
        if (std.mem.eql(u8, check.id, "shared-b-dispatch")) {
            saw_dispatch = true;
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "7 and -5") != null);
        }
        if (std.mem.eql(u8, check.id, "exit-boundary")) {
            saw_exit = true;
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "tore_down_registered_attributes") != null);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "rejects later show or store calls") != null);
        }

        for (manifest.exact_checks[i + 1 ..]) |other| {
            try std.testing.expect(!std.mem.eql(u8, check.id, other.id));
        }
    }

    try std.testing.expect(saw_descriptor_prompt);
    try std.testing.expect(saw_approved_idiom_prompt);
    try std.testing.expect(saw_pre_registration_prompt);
    try std.testing.expect(saw_ownership_summary_prompt);
    try std.testing.expect(saw_exit_prompt);
    try std.testing.expect(saw_group_boundary_prompt);
    try std.testing.expect(saw_directory);
    try std.testing.expect(saw_pre_registration);
    try std.testing.expect(saw_ownership_summary);
    try std.testing.expect(saw_initialized_exit);
    try std.testing.expect(saw_dispatch);
    try std.testing.expect(saw_exit);
    try std.testing.expect(std.mem.eql(u8, manifest.non_goals[0], "sysfs file creation parity"));
    try std.testing.expect(std.mem.eql(u8, manifest.non_goals[1], "kernel_kobj integration"));
}

test "phase 5 kobject survey packet stays repo-local and keeps the shared review surfaces explicit" {
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
        .limited(64 * 1024),
    );
    defer std.testing.allocator.free(survey_note);

    var surveyed_commit_marker_buf: [96]u8 = undefined;
    const surveyed_commit_marker = try std.fmt.bufPrint(
        surveyed_commit_marker_buf[0..],
        "PHASE5_SURVEYED_COMMIT={s}",
        .{manifest.surveyed_commit},
    );

    const required_markers = [_][]const u8{
        "PHASE5_STATUS=parked",
        "PHASE5_LANE_KEY=P5-Y03",
        "## Approved idiom for the landed kobject-style sample",
        "approved Phase 5 in-memory ownership-and-lifetime idiom",
        "before `registerAttributes()`, the sample still reports zero active attributes and blocks `showValue()` or `storeValue()`",
        "`ownershipSummary()` and sample-owned `runOwnershipReplay()`",
        "runPreRegistrationBoundaryReplay()",
        "`abandoned_before_registration`",
        "`tore_down_registered_attributes`",
        "manifest-backed replay",
        "keep sysfs creation, `kernel_kobj` integration, uevents, and module-registration claims out of scope",
        "zig build test --build-file zigux/tests/phase5_build.zig --summary all",
        "make -C zigux phase5-test",
        "`samples/zigux/README.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md`",
        "shared docs-root, sample-root, scripts-root, and tests-root contributor packet should stay explicit here too",
    };

    for (required_markers) |needle| {
        try std.testing.expect(std.mem.indexOf(u8, survey_note, needle) != null);
    }

    try std.testing.expect(std.mem.indexOf(u8, survey_note, surveyed_commit_marker) != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "/workspace/agent_files") == null);

    const docs_root = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/README.md",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(docs_root);

    const docs_root_markers = [_][]const u8{
        "Documentation/zigux/phase5-kobject-sample-survey.md",
        "samples/zigux/kobject_example.zig",
        "registered exactly three attributes",
        "remaining non-goals around sysfs creation, `kernel_kobj`, uevents, and module registration",
        "sample-backed contributor guide",
        "current `master` still ships no `samples/zigux/*cmdline*` Phase 5 reference sample",
        "Documentation/zigux/phase7-cmdline-slice.md",
        "zigux/tests/phase7_cmdline.zig",
        "zigux/tests/phase7_cmdline_survey.zig",
        "zigux/tests/phase7_build.zig",
    };

    for (docs_root_markers) |needle| {
        try std.testing.expect(std.mem.indexOf(u8, docs_root, needle) != null);
    }

    const review_checklist = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/review-checklist.md",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(review_checklist);

    const checklist_markers = [_][]const u8{
        "if the change is a reference sample under `samples/zigux/`, is the self-check or behavior replay explicit and small enough to stay reviewable?",
        "if the change updates an existing Phase 5 sample, do the descriptor, manifest, and shared `phase5_build.zig` entrypoint still agree on the same Linux anchor and exact replay contract?",
        "if the change updates a landed Phase 5 sample that keeps a Linux concurrency or private-data cue only for reviewability, does the note or checklist still say clearly what remains in-memory-only and what runtime parity is still out of scope?",
        "if the change updates the landed Phase 5 `kobject_example` sample packet, do the note, shared checklist text, and paired manifest-backed replays keep the initialized-but-not-registered zero-active-attributes boundary, `ownershipSummary()` lifecycle packet, unnamed attribute-group shape, shared `baz`/`bar` dispatch, and the `abandoned_before_registration` versus `tore_down_registered_attributes` exit split explicit instead of implying sysfs, `kernel_kobj`, uevents, or module-registration parity?",
        "if the change updates a landed Phase 5 sample, does it update the directly coupled survey note or manifest-backed contributor prompts when the sample contract changes?",
        "if the change touches the shared Phase 5 sample packet, do the docs still say clearly that there is no standalone `samples/zigux/*cmdline*` reference sample and that cmdline reviewability remains under `Documentation/zigux/phase7-cmdline-slice.md`, `zigux/tests/phase7_cmdline.zig`, `zigux/tests/phase7_cmdline_survey.zig`, and `zigux/tests/phase7_build.zig` rather than the four shipped Phase 5 samples?",
        "if the change touches the shared Phase 5 sample packet, do the docs still say clearly that there is no standalone `samples/zigux/*rbtree*` reference sample and that `rbtree` reviewability remains under `Documentation/zigux/phase7-rbtree-slice.md`, `lib/rbtree.zig`, and `zigux/tests/phase7_build.zig` rather than the four shipped Phase 5 samples?",
    };

    for (checklist_markers) |needle| {
        try std.testing.expect(std.mem.indexOf(u8, review_checklist, needle) != null);
    }

    const samples_root = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "samples/zigux/README.md",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(samples_root);

    const samples_root_markers = [_][]const u8{
        "samples/zigux/kobject_example.zig",
        "approved in-memory ownership-and-lifetime idiom",
        "samples/kobject/kobject-example.c",
        "phase5-kobject-sample-survey.md",
        "phase5_kobject_example_survey.zig",
        "`ownershipSummary()` and sample-owned `runOwnershipReplay()` explicit as the reviewable lifecycle cues",
        "initialized-only abandonment cue",
        "already-registered duplicate-registration and replay-restart rejection",
        "registered teardown reset",
        "post-`exit()` show-or-store rejection explicit",
        "current `master` still ships no `samples/zigux/*cmdline*` Phase 5 reference sample",
        "Documentation/zigux/phase7-cmdline-slice.md",
        "zigux/tests/phase7_cmdline.zig",
        "zigux/tests/phase7_cmdline_survey.zig",
    };

    for (samples_root_markers) |needle| {
        try std.testing.expect(std.mem.indexOf(u8, samples_root, needle) != null);
    }

    const scripts_root = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "scripts/zigux/README.md",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(scripts_root);

    const scripts_root_markers = [_][]const u8{
        "Phase 5 flow",
        "Documentation/zigux/phase5-kobject-sample-survey.md",
        "zigux/tests/phase5_kobject_example.zig",
        "zigux/tests/phase5_kobject_example_manifest.json",
        "zigux/tests/phase5_kobject_example_survey.zig",
        "zigux/tests/phase5_build.zig",
    };

    for (scripts_root_markers) |needle| {
        try std.testing.expect(std.mem.indexOf(u8, scripts_root, needle) != null);
    }

    const tests_root = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/README.md",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(tests_root);

    const tests_root_markers = [_][]const u8{
        "keep the shared Phase 5 reference-sample checks wired through `zigux/tests/phase5_build.zig`",
        "the four shipped sample-backed surveys stay reviewable without implying runtime-substrate closure",
        "keep the landed Phase 5 `kobject_example` packet explicit in the tests root too",
        "Documentation/zigux/phase5-kobject-sample-survey.md",
        "samples/zigux/kobject_example.zig",
        "zigux/tests/phase5_kobject_example_manifest.json",
        "zigux/tests/phase5_kobject_example.zig",
        "zigux/tests/phase5_kobject_example_survey.zig",
        "initialized-but-not-registered zero-active-attributes boundary",
        "`ownershipSummary()` lifecycle packet",
        "unnamed attribute-group shape",
        "shared `baz`/`bar` dispatch",
        "`abandoned_before_registration` versus `tore_down_registered_attributes` exit split",
    };

    for (tests_root_markers) |needle| {
        try std.testing.expect(std.mem.indexOf(u8, tests_root, needle) != null);
    }

    const build_zig = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase5_build.zig",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(build_zig);

    const build_markers = [_][]const u8{
        "../../samples/zigux/kobject_example.zig",
        "phase5_kobject_example_survey.zig",
        "phase5-kobject-example-tests",
        "phase5-kobject-example-survey-tests",
        "run_phase5_kobject_example_tests.step",
        "run_phase5_kobject_example_survey_tests.step",
    };

    for (build_markers) |needle| {
        try std.testing.expect(std.mem.indexOf(u8, build_zig, needle) != null);
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
        try std.testing.expect(std.mem.indexOf(u8, makefile, needle) != null);
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
        try std.testing.expect(std.mem.indexOf(u8, workflow, needle) != null);
    }
}
