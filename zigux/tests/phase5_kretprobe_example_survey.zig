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

test "phase 5 kretprobe manifest records the exact bounded checks" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const manifest_json = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase5_kretprobe_example_manifest.json",
        std.testing.allocator,
        .limited(review_doc_read_limit),
    );
    defer std.testing.allocator.free(manifest_json);

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{});
    defer parsed.deinit();

    const manifest = parsed.value;
    try std.testing.expectEqualStrings("P5-L22", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 5", manifest.phase);
    try std.testing.expectEqual(@as(usize, 40), manifest.surveyed_commit.len);
    for (manifest.surveyed_commit) |byte| {
        try std.testing.expect(std.ascii.isLower(byte) or std.ascii.isDigit(byte));
    }
    try std.testing.expectEqualStrings("samples/kprobes/kretprobe_example.c", manifest.anchor);
    try std.testing.expectEqualStrings("samples/zigux/kretprobe_example.zig", manifest.sample_path);
    try std.testing.expect(std.mem.indexOf(u8, manifest.validation_entrypoint, "phase5_build.zig") != null);
    try std.testing.expectEqual(@as(usize, 9), manifest.review_prompts.len);
    try std.testing.expectEqual(@as(usize, 10), manifest.exact_checks.len);
    try std.testing.expectEqual(@as(usize, 4), manifest.non_goals.len);

    var saw_descriptor_prompt = false;
    var saw_surveyed_commit_prompt = false;
    var saw_docs_prompt = false;
    var saw_private_data_prompt = false;
    var saw_maxactive_prompt = false;
    var saw_exact_contract_prompt = false;
    var saw_helper_contract_prompt = false;
    var saw_symbol_prompt = false;
    var saw_non_goal_prompt = false;
    var saw_private_data_check = false;
    var saw_maxactive_check = false;
    var saw_symbol_check = false;
    var saw_retarget_check = false;
    var saw_duration_check = false;
    var saw_timestamp_order_check = false;
    var saw_exit_check = false;

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
            std.mem.indexOf(u8, prompt, "shared sample-root catalog") != null and
            std.mem.indexOf(u8, prompt, "shared tests-root guide") != null and
            std.mem.indexOf(u8, prompt, "top-level Phase 5 README note") != null and
            std.mem.indexOf(u8, prompt, "shared review checklist") != null and
            std.mem.indexOf(u8, prompt, "Phase 9 runtime starter") != null)
        {
            saw_docs_prompt = true;
        }
        if (std.mem.indexOf(u8, prompt, "private entry timestamp") != null and
            std.mem.indexOf(u8, prompt, "my_data") != null)
        {
            saw_private_data_prompt = true;
        }
        if (std.mem.indexOf(u8, prompt, "maxactive budget") != null and
            std.mem.indexOf(u8, prompt, "fixed helper-backed reviewable ceiling") != null)
        {
            saw_maxactive_prompt = true;
        }
        if (std.mem.indexOf(u8, prompt, "pre-init retargeting") != null and
            std.mem.indexOf(u8, prompt, "timestamp-order") != null and
            std.mem.indexOf(u8, prompt, "ownership replay") != null)
        {
            saw_exact_contract_prompt = true;
        }
        if (std.mem.indexOf(u8, prompt, "runRetargetRecoveryReplay()") != null and
            std.mem.indexOf(u8, prompt, "runMaxactiveBudgetReplay()") != null and
            std.mem.indexOf(u8, prompt, "runOwnershipBoundaryReplay()") != null)
        {
            saw_helper_contract_prompt = true;
        }
        if (std.mem.indexOf(u8, prompt, "pre-init") != null and
            std.mem.indexOf(u8, prompt, "module_param") != null)
        {
            saw_symbol_prompt = true;
        }
        if (std.mem.indexOf(u8, prompt, "register_kretprobe") != null and
            std.mem.indexOf(u8, prompt, "pt_regs") != null)
        {
            saw_non_goal_prompt = true;
        }
    }

    for (manifest.exact_checks, 0..) |check, i| {
        try std.testing.expect(check.id.len > 0);
        try std.testing.expect(check.kind.len > 0);
        try std.testing.expect(check.expected.len > 0);

        if (std.mem.eql(u8, check.id, "default-symbol")) {
            saw_symbol_check = true;
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "kernel_clone") != null);
        }
        if (std.mem.eql(u8, check.id, "pre-init-retargeting")) {
            saw_retarget_check = true;
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "do_sys_openat2") != null);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "module_param") != null);
        }
        if (std.mem.eql(u8, check.id, "private-data-shape")) {
            saw_private_data_check = true;
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "my_data") != null);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "i64-sized word") != null);
        }
        if (std.mem.eql(u8, check.id, "return-duration")) {
            saw_duration_check = true;
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "retval 42") != null);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "75 ns") != null);
        }
        if (std.mem.eql(u8, check.id, "timestamp-order-boundary")) {
            saw_timestamp_order_check = true;
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "199") != null);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "200") != null);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "260") != null);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "60 ns") != null);
        }
        if (std.mem.eql(u8, check.id, "maxactive-budget")) {
            saw_maxactive_check = true;
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "runMaxactiveBudgetReplay()") != null);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "maxactive budget") != null);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "maxactiveBudget()") != null);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "20 concurrent instances") != null);
        }
        if (std.mem.eql(u8, check.id, "post-exit-rejection")) {
            saw_exit_check = true;
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "runOwnershipBoundaryReplay") != null);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "recordMissedInstance") != null);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "entryHandler") != null);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "retHandler") != null);
        }

        for (manifest.exact_checks[i + 1 ..]) |other| {
            try std.testing.expect(!std.mem.eql(u8, check.id, other.id));
        }
    }

    try std.testing.expect(saw_descriptor_prompt);
    try std.testing.expect(saw_surveyed_commit_prompt);
    try std.testing.expect(saw_docs_prompt);
    try std.testing.expect(saw_private_data_prompt);
    try std.testing.expect(saw_maxactive_prompt);
    try std.testing.expect(saw_exact_contract_prompt);
    try std.testing.expect(saw_helper_contract_prompt);
    try std.testing.expect(saw_symbol_prompt);
    try std.testing.expect(saw_non_goal_prompt);
    try std.testing.expect(saw_private_data_check);
    try std.testing.expect(saw_maxactive_check);
    try std.testing.expect(saw_symbol_check);
    try std.testing.expect(saw_retarget_check);
    try std.testing.expect(saw_duration_check);
    try std.testing.expect(saw_timestamp_order_check);
    try std.testing.expect(saw_exit_check);
    try std.testing.expect(std.mem.eql(u8, manifest.non_goals[0], "register_kretprobe parity"));
    try std.testing.expect(std.mem.eql(u8, manifest.non_goals[1], "unregister_kretprobe parity"));
}

test "phase 5 kretprobe contributor docs stay aligned with the shipped review surface" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const manifest_json = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase5_kretprobe_example_manifest.json",
        std.testing.allocator,
        .limited(review_doc_read_limit),
    );
    defer std.testing.allocator.free(manifest_json);

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{});
    defer parsed.deinit();

    const manifest = parsed.value;

    const survey_note = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase5-kretprobe-sample-survey.md",
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

    const tests_readme = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/README.md",
        std.testing.allocator,
        .limited(review_doc_read_limit),
    );
    defer std.testing.allocator.free(tests_readme);

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
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(review_checklist);

    try expectContains(survey_note, "sample-backed survey note");
    try expectContains(survey_note, "samples/zigux/README.md");
    try expectContains(survey_note, "Documentation/zigux/README.md");
    try expectContains(survey_note, "Documentation/zigux/review-checklist.md");
    try expectContains(survey_note, "phase5_kretprobe_example_manifest.json");
    try expectContains(survey_note, "phase5_kretprobe_example.zig");
    try expectContains(survey_note, "phase5_kretprobe_example_survey.zig");
    try expectContains(survey_note, "phase5_build.zig");
    try expectContains(survey_note, "kretprobe_example_sample");
    try expectContains(survey_note, "focused shared-build replay rather than a standalone `zig test` command");
    try expectContains(survey_note, "separate Phase 9 runtime starter");
    try expectContains(survey_note, "PHASE5_LANE_KEY=P5-L22");
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "/workspace/agent_files/") == null);
    {
        const surveyed_commit_line = try std.fmt.allocPrint(
            std.testing.allocator,
            "PHASE5_SURVEYED_COMMIT={s}",
            .{manifest.surveyed_commit},
        );
        defer std.testing.allocator.free(surveyed_commit_line);
        try expectContains(survey_note, surveyed_commit_line);
    }
    try expectContains(survey_note, "- `Documentation/zigux/review-checklist.md`");
    try expectContains(survey_note, "- `zigux/tests/README.md`");
    try expectContains(survey_note, "shared sample-root catalog in `samples/zigux/README.md`");
    try expectContains(survey_note, "shared `Documentation/zigux/review-checklist.md` prompts are part of that boundary now");
    try expectContains(survey_note, "shared tests-root guide in `zigux/tests/README.md` is part of that same contributor packet now");
    try expectContains(survey_note, "the direct `zig test samples/zigux/kretprobe_example.zig` replay, the paired `zig test zigux/tests/phase5_kretprobe_example_survey.zig` replay");
    try expectContains(survey_note, "runOwnershipBoundaryReplay()");
    try expectContains(survey_note, "Latest verification snapshot");
    try expectContains(survey_note, "zig test samples/zigux/kretprobe_example.zig");
    try expectContains(survey_note, "All 1 tests passed.");
    try expectContains(survey_note, "zig test zigux/tests/phase5_kretprobe_example_survey.zig");
    try expectContains(survey_note, "Build Summary: 18/18 steps succeeded; 29/29 tests passed");
    try expectContains(survey_note, "phase5-kretprobe-example-tests 5 pass (5 total)");
    try expectContains(survey_note, "phase5-kretprobe-example-survey-tests 2 pass (2 total)");
    try expectContains(survey_note, "register_kretprobe()");
    try expectContains(survey_note, "do_sys_openat2");
    try expectContains(survey_note, "199");
    try expectContains(survey_note, "260");
    try expectContains(survey_note, "recordMissedInstance()");
    try expectContains(survey_note, "entryHandler()");
    try expectContains(survey_note, "retHandler()");
    {
        const pinned_commit_line = try std.fmt.allocPrint(
            std.testing.allocator,
            "this approved probe-lifecycle idiom is now pinned to `PHASE5_SURVEYED_COMMIT={s}`",
            .{manifest.surveyed_commit},
        );
        defer std.testing.allocator.free(pinned_commit_line);
        try expectContains(survey_note, pinned_commit_line);
    }

    try expectContains(readme, "phase5-kretprobe-sample-survey.md");
    try expectContains(readme, "samples/zigux/kretprobe_example.zig");
    try expectContains(readme, "shared sample-root catalog, shared review checklist, manifest, and shared `phase5_build.zig` entrypoint prompts");
    try expectContains(readme, "separate Phase 9 runtime starter");

    try expectContains(tests_readme, "zigux/tests/phase5_kretprobe_example.zig");
    try expectContains(tests_readme, "zigux/tests/phase5_kretprobe_example_manifest.json");
    try expectContains(tests_readme, "zigux/tests/phase5_kretprobe_example_survey.zig");
    try expectContains(tests_readme, "scripts/zigux/validate-phase5.py");
    try expectContains(tests_readme, "make -C zigux phase5-validate");
    try expectContains(tests_readme, "zig test samples/zigux/kretprobe_example.zig");
    try expectContains(tests_readme, "zig test zigux/tests/phase5_kretprobe_example_survey.zig");
    try expectContains(tests_readme, "keep the current Phase 5 reference-sample packet reviewable through `zigux/tests/phase5_build.zig`");

    try expectContains(sample_root_readme, "Kretprobe review packet");
    try expectContains(sample_root_readme, "phase5_kretprobe_example_manifest.json");
    try expectContains(sample_root_readme, "phase5_kretprobe_example_survey.zig");
    try expectContains(sample_root_readme, "phase5-kretprobe-sample-survey.md");
    try expectContains(sample_root_readme, "approved Phase 5 non-runtime probe-lifecycle idiom");
    try expectContains(sample_root_readme, "maxactive = 20");
    try expectContains(sample_root_readme, "Phase 9 starter claim");

    try expectContains(survey_note, "runMaxactiveBudgetReplay()");

    try expectContains(review_checklist, "manifest-backed survey");
    try expectContains(review_checklist, "sample-backed survey note");
    try expectContains(review_checklist, "phase5_build.zig");
    try expectContains(review_checklist, "exact surveyed commit");
    try expectContains(review_checklist, "in-memory-only");
    try expectContains(review_checklist, "runtime parity is still out of scope");
}
