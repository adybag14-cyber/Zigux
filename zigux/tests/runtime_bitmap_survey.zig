const std = @import("std");

const SurveySummary = struct {
    test_bitmap_c_lines: usize,
    preexisting_runtime_bitmap_test_files: usize,
    preexisting_runtime_bitmap_sample_present: bool,
    preexisting_phase9_build_present: bool,
    preexisting_runtime_bitmap_doc_present: bool,
};

const Gap = struct {
    id: []const u8,
    status: []const u8,
    kind: []const u8,
    zigux_destination: []const u8,
    why_now: []const u8,
};

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
    roadmap_destinations: []const []const u8,
    sample_path: []const u8,
    validation_entrypoint: []const u8,
    survey_summary: SurveySummary,
    review_prompts: []const []const u8,
    exact_checks: []const ExactCheck,
    gaps: []const Gap,
    non_goals: []const []const u8,
};

fn isAllowedStatus(status: []const u8) bool {
    return std.mem.eql(u8, status, "starter_landed") or
        std.mem.eql(u8, status, "ready_next") or
        std.mem.eql(u8, status, "blocked_on_runtime_substrate");
}

fn isLowerHexSha(value: []const u8) bool {
    if (value.len != 40) return false;
    for (value) |byte| {
        if (!std.ascii.isHex(byte) or std.ascii.isUpper(byte)) return false;
    }
    return true;
}

test "phase 9 runtime bitmap survey manifest records the landed diff gate and remaining blocker" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const manifest_json = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/runtime_bitmap_manifest.json",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(manifest_json);

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{});
    defer parsed.deinit();

    const manifest = parsed.value;
    try std.testing.expectEqualStrings("P9-L05", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 9", manifest.phase);
    try std.testing.expect(isLowerHexSha(manifest.surveyed_commit));
    try std.testing.expectEqualStrings("lib/test_bitmap.c", manifest.anchor);
    try std.testing.expectEqual(@as(usize, 2), manifest.roadmap_destinations.len);
    try std.testing.expectEqualStrings("samples/zigux/runtime_bitmap.zig", manifest.sample_path);
    try std.testing.expectEqualStrings("zig build test --build-file zigux/tests/phase9_build.zig --summary all", manifest.validation_entrypoint);
    try std.testing.expect(manifest.survey_summary.test_bitmap_c_lines >= 1000);
    try std.testing.expectEqual(@as(usize, 3), manifest.survey_summary.preexisting_runtime_bitmap_test_files);
    try std.testing.expect(manifest.survey_summary.preexisting_runtime_bitmap_sample_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase9_build_present);
    try std.testing.expect(manifest.survey_summary.preexisting_runtime_bitmap_doc_present);
    try std.testing.expect(manifest.review_prompts.len >= 5);
    try std.testing.expectEqual(@as(usize, 11), manifest.exact_checks.len);
    try std.testing.expect(manifest.gaps.len >= 6);
    try std.testing.expectEqual(@as(usize, 4), manifest.non_goals.len);

    var saw_descriptor_contract = false;
    var saw_initial_summary = false;
    var saw_range_mutation_copy = false;
    var saw_selftest_surface = false;
    var saw_exit_lifecycle = false;
    var saw_bounds_errors = false;
    var saw_zero_length_source_guards = false;
    var saw_shared_build_sample_gate = false;
    var saw_diff_fill_case = false;
    var saw_diff_cutout_case = false;
    var saw_diff_sparse_copy_case = false;

    for (manifest.review_prompts) |prompt| {
        try std.testing.expect(prompt.len > 0);
    }

    for (manifest.exact_checks, 0..) |check, i| {
        try std.testing.expect(check.id.len > 0);
        try std.testing.expect(check.kind.len > 0);
        try std.testing.expect(check.expected.len > 0);

        if (std.mem.eql(u8, check.id, "descriptor-contract")) {
            saw_descriptor_contract = true;
            try std.testing.expectEqualStrings("review_surface", check.kind);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "runtime_bitmap") != null);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "requires_runtime_substrate true") != null);
        }
        if (std.mem.eql(u8, check.id, "initial-summary")) {
            saw_initial_summary = true;
            try std.testing.expectEqualStrings("summary_contract", check.kind);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "first_set 0") != null);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "weight 4") != null);
        }
        if (std.mem.eql(u8, check.id, "range-mutation-and-copy")) {
            saw_range_mutation_copy = true;
            try std.testing.expectEqualStrings("mutation_contract", check.kind);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "weight 7") != null);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "copyFrom") != null);
        }
        if (std.mem.eql(u8, check.id, "selftest-surface")) {
            saw_selftest_surface = true;
            try std.testing.expectEqualStrings("selftest_contract", check.kind);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "clear_set") != null);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "iteration_and_ranges") != null);
        }
        if (std.mem.eql(u8, check.id, "exit-and-lifecycle-guards")) {
            saw_exit_lifecycle = true;
            try std.testing.expectEqualStrings("ownership_lifetime", check.kind);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "InvalidLifecycleTransition") != null);
        }
        if (std.mem.eql(u8, check.id, "bounds-errors")) {
            saw_bounds_errors = true;
            try std.testing.expectEqualStrings("input_validation", check.kind);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "BitRangeOutOfBounds") != null);
        }
        if (std.mem.eql(u8, check.id, "zero-length-and-source-guards")) {
            saw_zero_length_source_guards = true;
            try std.testing.expectEqualStrings("helper_contract", check.kind);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "InvalidSourceLifecycle") != null);
        }
        if (std.mem.eql(u8, check.id, "shared-build-sample-gate")) {
            saw_shared_build_sample_gate = true;
            try std.testing.expectEqualStrings("validation_entrypoint", check.kind);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "phase9-runtime-bitmap-sample-tests") != null);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "samples/zigux/runtime_bitmap.zig") != null);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "module, diff, loader, and survey gates") != null);
        }
        if (std.mem.eql(u8, check.id, "diff-fill-set-case")) {
            saw_diff_fill_case = true;
            try std.testing.expectEqualStrings("differential_validation", check.kind);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "first_zero 9") != null);
        }
        if (std.mem.eql(u8, check.id, "diff-clear-cutout-case")) {
            saw_diff_cutout_case = true;
            try std.testing.expectEqualStrings("differential_validation", check.kind);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "clearRange(79, 19)") != null);
        }
        if (std.mem.eql(u8, check.id, "diff-find-nth-and-copy-case")) {
            saw_diff_sparse_copy_case = true;
            try std.testing.expectEqualStrings("differential_validation", check.kind);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "bits 10, 20, 30, 40, 50, 60, 80, and 123") != null);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "weight 109") != null);
        }

        for (manifest.exact_checks[i + 1 ..]) |other| {
            try std.testing.expect(!std.mem.eql(u8, check.id, other.id));
        }
    }

    var runtime_test_destination_count: usize = 0;
    var starter_landed_count: usize = 0;
    var ready_next_count: usize = 0;
    var blocked_count: usize = 0;
    var saw_sample_module = false;
    var saw_diff_gate = false;
    var saw_loader_scaffold = false;
    var saw_live_loader_binding = false;
    var saw_shared_loader_controls_blocker = false;

    for (manifest.gaps, 0..) |gap, i| {
        try std.testing.expect(gap.id.len > 0);
        try std.testing.expect(gap.kind.len > 0);
        try std.testing.expect(gap.why_now.len > 0);
        try std.testing.expect(isAllowedStatus(gap.status));

        if (std.mem.startsWith(u8, gap.zigux_destination, "zigux/tests/")) {
            runtime_test_destination_count += 1;
        } else if (std.mem.startsWith(u8, gap.zigux_destination, "samples/zigux/")) {
            // Sample-side starter and loader handoff scaffolds stay under samples.
        } else if (std.mem.startsWith(u8, gap.zigux_destination, "Documentation/zigux/")) {
            // Broader shared loader-control blockers may be tracked by the canonical runtime-loader gap note.
        } else {
            try std.testing.expect(std.mem.startsWith(u8, gap.zigux_destination, "zigux/kernel/"));
        }

        if (std.mem.eql(u8, gap.status, "ready_next")) {
            ready_next_count += 1;
        } else if (std.mem.eql(u8, gap.status, "starter_landed")) {
            starter_landed_count += 1;
        } else if (std.mem.eql(u8, gap.status, "blocked_on_runtime_substrate")) {
            blocked_count += 1;
        }

        if (std.mem.eql(u8, gap.id, "runtime-bitmap-sample-module")) {
            saw_sample_module = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("samples/zigux/runtime_bitmap.zig", gap.zigux_destination);
        }
        if (std.mem.eql(u8, gap.id, "runtime-bitmap-diff-gate")) {
            saw_diff_gate = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("zigux/tests/runtime_bitmap_diff.zig", gap.zigux_destination);
        }
        if (std.mem.eql(u8, gap.id, "runtime-bitmap-loader-scaffold")) {
            saw_loader_scaffold = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("samples/zigux/runtime_bitmap_loader.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "requires_runtime_substrate") != null);
        }
        if (std.mem.eql(u8, gap.id, "runtime-bitmap-live-loader-binding")) {
            saw_live_loader_binding = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("zigux/kernel/runtime_loader.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "shared runtime-loader request surface") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "bitmap loader handoff") != null);
        }
        if (std.mem.eql(u8, gap.id, "runtime-bitmap-shared-loader-controls")) {
            saw_shared_loader_controls_blocker = true;
            try std.testing.expectEqualStrings("blocked_on_runtime_substrate", gap.status);
            try std.testing.expectEqualStrings("Documentation/zigux/phase9-runtime-loader-gap-survey.md", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "command-name") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "argv-policy") != null);
        }

        for (manifest.gaps[i + 1 ..]) |other| {
            try std.testing.expect(!std.mem.eql(u8, gap.id, other.id));
            try std.testing.expect(!std.mem.eql(u8, gap.zigux_destination, other.zigux_destination));
        }
    }

    try std.testing.expect(runtime_test_destination_count >= 4);
    try std.testing.expect(starter_landed_count >= 7);
    try std.testing.expectEqual(@as(usize, 0), ready_next_count);
    try std.testing.expect(blocked_count >= 1);
    try std.testing.expect(saw_descriptor_contract);
    try std.testing.expect(saw_initial_summary);
    try std.testing.expect(saw_range_mutation_copy);
    try std.testing.expect(saw_selftest_surface);
    try std.testing.expect(saw_exit_lifecycle);
    try std.testing.expect(saw_bounds_errors);
    try std.testing.expect(saw_zero_length_source_guards);
    try std.testing.expect(saw_shared_build_sample_gate);
    try std.testing.expect(saw_diff_fill_case);
    try std.testing.expect(saw_diff_cutout_case);
    try std.testing.expect(saw_diff_sparse_copy_case);
    try std.testing.expect(saw_sample_module);
    try std.testing.expect(saw_diff_gate);
    try std.testing.expect(saw_loader_scaffold);
    try std.testing.expect(saw_live_loader_binding);
    try std.testing.expect(saw_shared_loader_controls_blocker);
}
