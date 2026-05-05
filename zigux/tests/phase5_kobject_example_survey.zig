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
    try std.testing.expectEqualStrings("P5-Y03", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 5", manifest.phase);
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
    var saw_dispatch_prompt = false;
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
        if (std.mem.indexOf(u8, prompt, "initialized-but-not-registered") != null and
            std.mem.indexOf(u8, prompt, "registerAttributes()") != null)
        {
            saw_pre_registration_prompt = true;
        }
        if (std.mem.indexOf(u8, prompt, "ownershipSummary()") != null and
            std.mem.indexOf(u8, prompt, "cold, initialized, registered, and exited") != null)
        {
            saw_ownership_summary_prompt = true;
        }
        if (std.mem.indexOf(u8, prompt, "shared baz/bar dispatch") != null) {
            saw_dispatch_prompt = true;
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
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "activeAttrCount stays zero") != null);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "InvalidLifecycleTransition") != null);
        }
        if (std.mem.eql(u8, check.id, "ownership-summary")) {
            saw_ownership_summary = true;
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
    try std.testing.expect(saw_dispatch_prompt);
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

test "phase 5 kobject survey note stays repo-local, lane-scoped, and keeps the approved idiom explicit" {
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
        "PHASE5_LANE_KEY=P5-Y03",
        "## Approved idiom for the landed kobject-style sample",
        "approved Phase 5 in-memory ownership-and-lifetime idiom",
        "before `registerAttributes()`, the sample still reports zero active attributes and blocks `showValue()` or `storeValue()`",
        "`ownershipSummary()`",
        "`abandoned_before_registration`",
        "`tore_down_registered_attributes`",
        "manifest-backed replay",
        "keep sysfs creation, `kernel_kobj` integration, uevents, and module-registration claims out of scope",
        "zig build test --build-file zigux/tests/phase5_build.zig --summary all",
    };

    for (required_markers) |needle| {
        try std.testing.expect(std.mem.indexOf(u8, survey_note, needle) != null);
    }

    try std.testing.expect(std.mem.indexOf(u8, survey_note, surveyed_commit_marker) != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "/workspace/agent_files") == null);

    const review_checklist = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/review-checklist.md",
        std.testing.allocator,
        .limited(128 * 1024),
    );
    defer std.testing.allocator.free(review_checklist);

    const checklist_markers = [_][]const u8{
        "no standalone `samples/zigux/*rbtree*` reference sample",
        "Documentation/zigux/phase7-rbtree-slice.md",
        "lib/rbtree.zig",
        "zigux/tests/phase7_rbtree.zig",
        "zigux/tests/phase7_build.zig",
    };

    for (checklist_markers) |needle| {
        try std.testing.expect(std.mem.indexOf(u8, review_checklist, needle) != null);
    }
}
