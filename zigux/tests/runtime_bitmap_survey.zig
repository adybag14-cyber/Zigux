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

const DeliveryEvidence = struct {
    id: []const u8,
    kind: []const u8,
    path: []const u8,
    role: []const u8,
};

const OwnershipEntry = struct {
    surface: []const u8,
    owns: []const u8,
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
    delivery_evidence_catalog: []const DeliveryEvidence,
    ownership_map: []const OwnershipEntry,
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

fn expectSurveyedCommitMarker(document: []const u8, commit: []const u8) !void {
    const marker = try std.fmt.allocPrint(std.testing.allocator, "`PHASE9_SURVEYED_COMMIT={s}`", .{commit});
    defer std.testing.allocator.free(marker);
    try std.testing.expect(std.mem.indexOf(u8, document, marker) != null);
}

fn expectPinnedCommitSentence(document: []const u8, commit: []const u8) !void {
    const sentence = try std.fmt.allocPrint(
        std.testing.allocator,
        "the current survey packet is pinned to `master` commit `{s}`",
        .{commit},
    );
    defer std.testing.allocator.free(sentence);
    try std.testing.expect(std.mem.indexOf(u8, document, sentence) != null);
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
    try std.testing.expectEqualStrings("P9-L08", manifest.lane_key);
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
    try std.testing.expect(manifest.review_prompts.len >= 8);
    try std.testing.expectEqual(@as(usize, 17), manifest.exact_checks.len);
    try std.testing.expectEqual(@as(usize, 12), manifest.delivery_evidence_catalog.len);
    try std.testing.expectEqual(@as(usize, 12), manifest.ownership_map.len);
    try std.testing.expect(manifest.gaps.len >= 6);
    try std.testing.expectEqual(@as(usize, 6), manifest.non_goals.len);

    var saw_descriptor_contract = false;
    var saw_initial_summary = false;
    var saw_range_mutation_copy = false;
    var saw_selftest_surface = false;
    var saw_sparse_nth_set_bit_replay = false;
    var saw_post_selftest_mutation_replay = false;
    var saw_exit_lifecycle = false;
    var saw_bounds_errors = false;
    var saw_zero_length_source_guards = false;
    var saw_bit_list_guards = false;
    var saw_loader_request_surface = false;
    var saw_loader_prepared_snapshot = false;
    var saw_loader_build_leg = false;
    var saw_diff_fill_case = false;
    var saw_diff_cutout_case = false;
    var saw_diff_sparse_copy_case = false;
    var saw_manifest_catalog = false;
    var saw_module_slice_catalog = false;
    var saw_shared_build_catalog = false;
    var saw_loader_gap_note = false;
    var saw_runtime_loader_binding_catalog = false;
    var saw_bitmap_loader_scaffold_catalog = false;
    var saw_freeze_map_catalog = false;
    var saw_loader_gap_ownership = false;
    var saw_module_slice_ownership = false;
    var saw_bitmap_diff_ownership = false;
    var saw_bitmap_sample_ownership = false;
    var saw_freeze_map_ownership = false;
    var saw_loader_gap_review_prompt = false;
    var saw_freeze_map_review_prompt = false;
    var saw_loader_snapshot_review_prompt = false;

    for (manifest.review_prompts) |prompt| {
        try std.testing.expect(prompt.len > 0);
        if (std.mem.indexOf(u8, prompt, "Documentation/zigux/phase9-runtime-loader-gap-survey.md") != null) {
            saw_loader_gap_review_prompt = true;
        }
        if (std.mem.indexOf(u8, prompt, "Documentation/zigux/freeze-map.md") != null) {
            saw_freeze_map_review_prompt = true;
        }
        if (std.mem.indexOf(u8, prompt, "prepared-summary snapshot explicit") != null) {
            saw_loader_snapshot_review_prompt = true;
        }
    }

    for (manifest.delivery_evidence_catalog, 0..) |entry, i| {
        try std.testing.expect(entry.id.len > 0);
        try std.testing.expect(entry.kind.len > 0);
        try std.testing.expect(entry.path.len > 0);
        try std.testing.expect(entry.role.len > 0);

        if (std.mem.eql(u8, entry.id, "runtime-bitmap-manifest")) {
            saw_manifest_catalog = true;
            try std.testing.expectEqualStrings("manifest", entry.kind);
            try std.testing.expectEqualStrings("zigux/tests/runtime_bitmap_manifest.json", entry.path);
            try std.testing.expect(std.mem.indexOf(u8, entry.role, "delivery catalog") != null);
            try std.testing.expect(std.mem.indexOf(u8, entry.role, "ownership map") != null);
            try std.testing.expect(std.mem.indexOf(u8, entry.role, "runtime bitmap packet") != null);
        }
        if (std.mem.eql(u8, entry.id, "runtime-bitmap-module-slice")) {
            saw_module_slice_catalog = true;
            try std.testing.expectEqualStrings("documentation", entry.kind);
            try std.testing.expectEqualStrings("Documentation/zigux/phase9-runtime-bitmap-module-slice.md", entry.path);
            try std.testing.expect(std.mem.indexOf(u8, entry.role, "loader handoff wording") != null);
            try std.testing.expect(std.mem.indexOf(u8, entry.role, "prepared-summary snapshot replay") != null);
            try std.testing.expect(std.mem.indexOf(u8, entry.role, "shared-build-leg explanation") != null);
        }
        if (std.mem.eql(u8, entry.id, "phase9-bitmap-build-gate")) {
            saw_shared_build_catalog = true;
            try std.testing.expectEqualStrings("zigux/tests/phase9_build.zig", entry.path);
            try std.testing.expect(std.mem.indexOf(u8, entry.role, "phase9-runtime-bitmap-sample-tests") != null);
            try std.testing.expect(std.mem.indexOf(u8, entry.role, "phase9-runtime-bitmap-loader-tests") != null);
        }
        if (std.mem.eql(u8, entry.id, "runtime-loader-gap-note")) {
            saw_loader_gap_note = true;
            try std.testing.expectEqualStrings("documentation", entry.kind);
            try std.testing.expectEqualStrings("Documentation/zigux/phase9-runtime-loader-gap-survey.md", entry.path);
            try std.testing.expect(std.mem.indexOf(u8, entry.role, "argv-policy") != null);
        }
        if (std.mem.eql(u8, entry.id, "runtime-bitmap-shared-loader-binding")) {
            saw_runtime_loader_binding_catalog = true;
            try std.testing.expectEqualStrings("zigux/kernel/runtime_loader.zig", entry.path);
            try std.testing.expect(std.mem.indexOf(u8, entry.role, "shared runtime-loader request contract") != null);
            try std.testing.expect(std.mem.indexOf(u8, entry.role, "prepared-summary snapshot replay") != null);
        }
        if (std.mem.eql(u8, entry.id, "runtime-bitmap-loader-scaffold")) {
            saw_bitmap_loader_scaffold_catalog = true;
            try std.testing.expectEqualStrings("samples/zigux/runtime_bitmap_loader.zig", entry.path);
            try std.testing.expect(std.mem.indexOf(u8, entry.role, "released_without_substrate") != null);
            try std.testing.expect(std.mem.indexOf(u8, entry.role, "explicit shared command-name preservation") != null);
            try std.testing.expect(std.mem.indexOf(u8, entry.role, "prepared-summary snapshot replay") != null);
        }
        if (std.mem.eql(u8, entry.id, "runtime-bitmap-freeze-map")) {
            saw_freeze_map_catalog = true;
            try std.testing.expectEqualStrings("governance", entry.kind);
            try std.testing.expectEqualStrings("Documentation/zigux/freeze-map.md", entry.path);
            try std.testing.expect(std.mem.indexOf(u8, entry.role, "kernel/workqueue.c") != null);
            try std.testing.expect(std.mem.indexOf(u8, entry.role, "Architecture Council reopen rule") != null);
        }

        for (manifest.delivery_evidence_catalog[i + 1 ..]) |other| {
            try std.testing.expect(!std.mem.eql(u8, entry.id, other.id));
        }
    }

    for (manifest.ownership_map, 0..) |entry, i| {
        try std.testing.expect(entry.surface.len > 0);
        try std.testing.expect(entry.owns.len > 0);

        if (std.mem.eql(u8, entry.surface, "Documentation/zigux/phase9-runtime-loader-gap-survey.md")) {
            saw_loader_gap_ownership = true;
            try std.testing.expect(std.mem.indexOf(u8, entry.owns, "argv-policy") != null);
        }
        if (std.mem.eql(u8, entry.surface, "Documentation/zigux/phase9-runtime-bitmap-module-slice.md")) {
            saw_module_slice_ownership = true;
            try std.testing.expect(std.mem.indexOf(u8, entry.owns, "loader handoff wording") != null);
            try std.testing.expect(std.mem.indexOf(u8, entry.owns, "prepared-summary snapshot replay") != null);
            try std.testing.expect(std.mem.indexOf(u8, entry.owns, "shared-build-leg explanation") != null);
        }
        if (std.mem.eql(u8, entry.surface, "zigux/tests/runtime_bitmap_diff.zig")) {
            saw_bitmap_diff_ownership = true;
            try std.testing.expect(std.mem.indexOf(u8, entry.owns, "differential replay") != null);
        }
        if (std.mem.eql(u8, entry.surface, "samples/zigux/runtime_bitmap.zig")) {
            saw_bitmap_sample_ownership = true;
            try std.testing.expect(std.mem.indexOf(u8, entry.owns, "selftest-hook metadata") != null);
        }
        if (std.mem.eql(u8, entry.surface, "Documentation/zigux/freeze-map.md")) {
            saw_freeze_map_ownership = true;
            try std.testing.expect(std.mem.indexOf(u8, entry.owns, "kernel/workqueue.c") != null);
            try std.testing.expect(std.mem.indexOf(u8, entry.owns, "Architecture Council reopen rule") != null);
        }
        if (std.mem.eql(u8, entry.surface, "samples/zigux/runtime_bitmap_loader.zig")) {
            try std.testing.expect(std.mem.indexOf(u8, entry.owns, "explicit shared command-name preservation") != null);
            try std.testing.expect(std.mem.indexOf(u8, entry.owns, "prepared-summary snapshot replay") != null);
        }
        if (std.mem.eql(u8, entry.surface, "zigux/kernel/runtime_loader.zig")) {
            try std.testing.expect(std.mem.indexOf(u8, entry.owns, "prepared-summary snapshot replay") != null);
        }

        for (manifest.ownership_map[i + 1 ..]) |other| {
            try std.testing.expect(!std.mem.eql(u8, entry.surface, other.surface));
        }
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
        if (std.mem.eql(u8, check.id, "sparse-nth-set-bit-replay")) {
            saw_sparse_nth_set_bit_replay = true;
            try std.testing.expectEqualStrings("iteration_contract", check.kind);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "nthSetBit") != null);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "bits 10, 20, 30, 40, 50, 60, 80, and 123") != null);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "returns null") != null);
        }
        if (std.mem.eql(u8, check.id, "post-selftest-mutation-replay")) {
            saw_post_selftest_mutation_replay = true;
            try std.testing.expectEqualStrings("selftest_lifecycle", check.kind);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "selftest_complete") != null);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "weight 7") != null);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "copyFrom") != null);
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
        if (std.mem.eql(u8, check.id, "bit-list-guards")) {
            saw_bit_list_guards = true;
            try std.testing.expectEqualStrings("input_validation", check.kind);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "trailing or doubled separators") != null);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "out-of-bounds bit lists") != null);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "canonical 0,5,64,70 replay") != null);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "empty string") != null);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "null nthSetBit(0)") != null);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "InvalidLifecycleTransition") != null);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "failed parsed or direct init attempts cold and empty") != null);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "clean follow-up init") != null);
        }
        if (std.mem.eql(u8, check.id, "loader-request-surface")) {
            saw_loader_request_surface = true;
            try std.testing.expectEqualStrings("runtime_loader_contract", check.kind);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "zigux_runtime_bitmap_init") != null);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "released_without_substrate") != null);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "helper_owned") != null);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "explicit shared command-name preservation") != null);
        }
        if (std.mem.eql(u8, check.id, "loader-prepared-snapshot")) {
            saw_loader_prepared_snapshot = true;
            try std.testing.expectEqualStrings("runtime_loader_contract", check.kind);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "snapshots the current bitmap summary") != null);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "waiting_on_runtime_substrate") != null);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "released_without_substrate") != null);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "summary or counters") != null);
        }
        if (std.mem.eql(u8, check.id, "loader-build-leg")) {
            saw_loader_build_leg = true;
            try std.testing.expectEqualStrings("shared_build_contract", check.kind);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "phase9-runtime-bitmap-loader-tests") != null);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "phase9-runtime-bitmap-sample-tests") != null);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "phase9-runtime-bitmap-module-tests") != null);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "phase9-runtime-bitmap-diff-tests") != null);
        }
        if (std.mem.eql(u8, check.id, "shared-loader-freeze-map-boundary")) {
            try std.testing.expectEqualStrings("governance_boundary", check.kind);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "Documentation/zigux/freeze-map.md") != null);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "kernel/workqueue.c") != null);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "Architecture Council") != null);
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
    var saw_direct_sample_build_leg = false;

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

        if (std.mem.eql(u8, gap.id, "phase9-build-gate")) {
            saw_direct_sample_build_leg = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("zigux/tests/phase9_build.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "phase9-runtime-bitmap-sample-tests") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "phase9-runtime-bitmap-loader-tests") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "sample, module, diff, and loader contracts stay first-class") != null);
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
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "prepared-summary snapshot") != null);
        }
        if (std.mem.eql(u8, gap.id, "runtime-bitmap-live-loader-binding")) {
            saw_live_loader_binding = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("zigux/kernel/runtime_loader.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "shared runtime-loader request surface") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "bitmap loader handoff") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "prepared-summary snapshot replay") != null);
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
    try std.testing.expect(saw_sparse_nth_set_bit_replay);
    try std.testing.expect(saw_post_selftest_mutation_replay);
    try std.testing.expect(saw_exit_lifecycle);
    try std.testing.expect(saw_bounds_errors);
    try std.testing.expect(saw_zero_length_source_guards);
    try std.testing.expect(saw_bit_list_guards);
    try std.testing.expect(saw_loader_request_surface);
    try std.testing.expect(saw_loader_prepared_snapshot);
    try std.testing.expect(saw_loader_build_leg);
    try std.testing.expect(saw_diff_fill_case);
    try std.testing.expect(saw_diff_cutout_case);
    try std.testing.expect(saw_diff_sparse_copy_case);
    try std.testing.expect(saw_manifest_catalog);
    try std.testing.expect(saw_module_slice_catalog);
    try std.testing.expect(saw_shared_build_catalog);
    try std.testing.expect(saw_loader_gap_note);
    try std.testing.expect(saw_runtime_loader_binding_catalog);
    try std.testing.expect(saw_bitmap_loader_scaffold_catalog);
    try std.testing.expect(saw_freeze_map_catalog);
    try std.testing.expect(saw_loader_gap_ownership);
    try std.testing.expect(saw_module_slice_ownership);
    try std.testing.expect(saw_bitmap_diff_ownership);
    try std.testing.expect(saw_bitmap_sample_ownership);
    try std.testing.expect(saw_freeze_map_ownership);
    try std.testing.expect(saw_loader_gap_review_prompt);
    try std.testing.expect(saw_freeze_map_review_prompt);
    try std.testing.expect(saw_loader_snapshot_review_prompt);
    try std.testing.expect(saw_direct_sample_build_leg);
    try std.testing.expect(saw_sample_module);
    try std.testing.expect(saw_diff_gate);
    try std.testing.expect(saw_loader_scaffold);
    try std.testing.expect(saw_live_loader_binding);
    try std.testing.expect(saw_shared_loader_controls_blocker);
}

test "phase 9 runtime bitmap survey doc keeps the direct sample, sparse iteration, loader build legs, and snapshot evidence explicit" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const survey_doc = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase9-runtime-bitmap-survey.md",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(survey_doc);

    const sample_source = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "samples/zigux/runtime_bitmap.zig",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(sample_source);

    const phase9_build = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase9_build.zig",
        std.testing.allocator,
        .limited(64 * 1024),
    );
    defer std.testing.allocator.free(phase9_build);

    try std.testing.expect(std.mem.indexOf(u8, phase9_build, "phase9-runtime-bitmap-sample-tests") != null);
    try std.testing.expect(std.mem.indexOf(u8, phase9_build, "phase9-runtime-bitmap-module-tests") != null);
    try std.testing.expect(std.mem.indexOf(u8, phase9_build, "phase9-runtime-bitmap-diff-tests") != null);
    try std.testing.expect(std.mem.indexOf(u8, phase9_build, "phase9-runtime-bitmap-loader-tests") != null);
    try std.testing.expect(std.mem.indexOf(u8, sample_source, "test \"runtime bitmap sample exposes ordered set-bit replay for sparse populations\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, sample_source, "nthSetBit") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_doc, "manifest-backed delivery catalog and ownership map") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_doc, "`PHASE9_LANE_KEY=P9-L08`") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_doc, "direct `phase9-runtime-bitmap-sample-tests`") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_doc, "direct `phase9-runtime-bitmap-loader-tests`") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_doc, "`Documentation/zigux/freeze-map.md` keeps `kernel/workqueue.c` in `Study / Boundary Only`") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_doc, "No parity scorecard entry or Architecture Council status-change request is attached to this Phase 9 runtime bitmap lane.") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_doc, "## Delivery ownership map") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_doc, "prepared the handoff snapshot stable after later sample mutation") == null);
    try std.testing.expect(std.mem.indexOf(u8, survey_doc, "preparing the loader handoff snapshots the current bitmap summary, and later sample mutations do not rewrite the pending `waiting_on_runtime_substrate` request or `released_without_substrate` fallback summary or counters") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_doc, "`Documentation/zigux/phase9-runtime-bitmap-module-slice.md` owns the bounded starter surface, loader handoff wording, and shared-build-leg explanation for the shipped bitmap packet") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_doc, "`Documentation/zigux/phase9-runtime-loader-gap-survey.md` owns the still-blocked shared command-name, argv-policy, and environment-derived activation-control posture that keeps this bitmap packet pre-execution") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_doc, "`zigux/kernel/runtime_loader.zig` owns the shared runtime-loader request contract that consumes the bitmap loader handoff") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_doc, "prepared-summary snapshot replay") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_doc, "explicit shared command-name preservation") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_doc, "the direct sample leg replays sparse `nthSetBit()` iteration across bits `10`, `20`, `30`, `40`, `50`, `60`, `80`, and `123`") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_doc, "`initFromBitList()` rejects trailing or doubled separators, rejects out-of-bounds bit lists, normalizes duplicate bit lists to the canonical `0,5,64,70` replay, preserves empty parse-and-print replay as an empty string plus `null` first `nthSetBit()`, blocks repeat parse initialization with `InvalidLifecycleTransition` once the first parse succeeds, and keeps failed parsed or direct init attempts cold and empty so a clean follow-up init can still succeed") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_doc, "the landed `phase9-build-gate`, including the direct `phase9-runtime-bitmap-sample-tests`, `phase9-runtime-bitmap-module-tests`, `phase9-runtime-bitmap-diff-tests`, and `phase9-runtime-bitmap-loader-tests` shared-build legs") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_doc, "this shared build now includes the direct `phase9-runtime-bitmap-sample-tests`, `phase9-runtime-bitmap-module-tests`, `phase9-runtime-bitmap-diff-tests`, and `phase9-runtime-bitmap-loader-tests` legs") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_doc, "any freeze-map status change for the scheduler-facing workqueue boundary without an Architecture Council decision") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_doc, "while keeping the separate `kernel/workqueue.c` freeze-map boundary in study-only status unless the Architecture Council explicitly reopens it") != null);

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
    try expectSurveyedCommitMarker(survey_doc, manifest.surveyed_commit);
    try expectPinnedCommitSentence(survey_doc, manifest.surveyed_commit);
}

test "phase 9 runtime bitmap module slice note stays aligned with the landed loader-backed review packet" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const module_slice = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase9-runtime-bitmap-module-slice.md",
        std.testing.allocator,
        .limited(16 * 1024),
    );
    defer std.testing.allocator.free(module_slice);

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

    const required_markers = [_][]const u8{
        "`PHASE9_LANE_KEY=P9-L08`",
        "adjacent loader scaffold plus shared loader-request binding",
        "prepared loader-summary snapshot replay",
        "zigux/kernel/runtime_loader.zig",
        "direct post-selftest mutation replay proof",
        "phase9-runtime-bitmap-sample-tests",
        "phase9-runtime-bitmap-loader-tests",
        "shared runtime-loader request binding in `zigux/kernel/runtime_loader.zig`",
        "explicit shared command-name preservation",
        "bounded two-word runtime bitmap backing store",
        "bounded parse-and-print replay",
        "duplicate bit-list normalization and empty formatting",
        "transactional failed-init recovery",
        "failed parsed or direct init attempts stay cold and empty until a clean follow-up init succeeds",
        "freezes the prepared summary before later sample mutation",
    };

    for (required_markers) |marker| {
        try std.testing.expect(std.mem.indexOf(u8, module_slice, marker) != null);
    }

    try expectSurveyedCommitMarker(module_slice, manifest.surveyed_commit);

    try std.testing.expect(std.mem.indexOf(
        u8,
        module_slice,
        "lane-local manifest closure only",
    ) == null);
    try std.testing.expect(std.mem.indexOf(
        u8,
        module_slice,
        "parse, print, region-allocation, or performance-path differentials",
    ) == null);
}

test "phase 9 runtime bitmap direct sample keeps parse-and-print and transactional init replay explicit" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const sample_source = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "samples/zigux/runtime_bitmap.zig",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(sample_source);

    try std.testing.expect(std.mem.indexOf(u8, sample_source, "var empty = RuntimeBitmapSample{};") != null);
    try std.testing.expect(std.mem.indexOf(u8, sample_source, "try empty.initFromBitList(\"  \");") != null);
    try std.testing.expect(std.mem.indexOf(u8, sample_source, "const empty_summary = empty.summary();") != null);
    try std.testing.expect(std.mem.indexOf(u8, sample_source, "const empty_formatted = try empty.formatSetBits(std.testing.allocator);") != null);
    try std.testing.expect(std.mem.indexOf(u8, sample_source, "try std.testing.expectEqualStrings(\"\", empty_formatted);") != null);
    try std.testing.expect(std.mem.indexOf(u8, sample_source, "try std.testing.expectEqual(@as(?u32, null), empty.nthSetBit(0));") != null);
    try std.testing.expect(std.mem.indexOf(u8, sample_source, "try duplicate_bits.initFromBitList(\"70, 5, 70, 0, 64, 5\");") != null);
    try std.testing.expect(std.mem.indexOf(u8, sample_source, "const duplicate_formatted = try duplicate_bits.formatSetBits(std.testing.allocator);") != null);
    try std.testing.expect(std.mem.indexOf(u8, sample_source, "try std.testing.expectEqualStrings(\"0,5,64,70\", duplicate_formatted);") != null);
    try std.testing.expect(std.mem.indexOf(u8, sample_source, "test \"runtime bitmap sample keeps transactional init failures explicit in the direct sample leg\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, sample_source, "try std.testing.expectError(error.BitRangeOutOfBounds, parsed.initFromBitList(\"0, 5, 64, 128\"));") != null);
    try std.testing.expect(std.mem.indexOf(u8, sample_source, "try std.testing.expectEqual(ModuleStage.cold, parsed.stage());") != null);
    try std.testing.expect(std.mem.indexOf(u8, sample_source, "try std.testing.expectEqual(@as(u32, 0), parsed_summary.weight);") != null);
    try std.testing.expect(std.mem.indexOf(u8, sample_source, "try parsed.initFromBitList(\"0, 5, 64, 70\");") != null);
    try std.testing.expect(std.mem.indexOf(u8, sample_source, "try std.testing.expectError(error.BitRangeOutOfBounds, direct.initWithSetBits(&.{ 1, RuntimeBitmapSample.bitmap_nbits }));") != null);
    try std.testing.expect(std.mem.indexOf(u8, sample_source, "try std.testing.expectEqual(ModuleStage.cold, direct.stage());") != null);
    try std.testing.expect(std.mem.indexOf(u8, sample_source, "try direct.initWithSetBits(&.{ 1, 3 });") != null);
}
