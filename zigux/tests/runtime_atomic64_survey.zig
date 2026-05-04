const std = @import("std");

const SurveySummary = struct {
    atomic64_test_c_lines: usize,
    preexisting_runtime_test_files: usize,
    preexisting_samples_zigux_present: bool,
    preexisting_phase9_build_present: bool,
    preexisting_phase9_doc_present: bool,
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

test "phase 9 runtime atomic64 survey manifest records the landed diff gate and remaining blocker" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const manifest_json = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/runtime_atomic64_manifest.json",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(manifest_json);

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{});
    defer parsed.deinit();

    const manifest = parsed.value;
    try std.testing.expectEqualStrings("P9-L04", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 9", manifest.phase);
    try std.testing.expect(isLowerHexSha(manifest.surveyed_commit));
    try std.testing.expectEqualStrings("lib/atomic64_test.c", manifest.anchor);
    try std.testing.expectEqual(@as(usize, 2), manifest.roadmap_destinations.len);
    try std.testing.expectEqualStrings("samples/zigux/runtime_atomic64.zig", manifest.sample_path);
    try std.testing.expectEqualStrings("zig build test --build-file zigux/tests/phase9_build.zig --summary all", manifest.validation_entrypoint);
    try std.testing.expect(manifest.survey_summary.atomic64_test_c_lines >= 200);
    try std.testing.expectEqual(@as(usize, 3), manifest.survey_summary.preexisting_runtime_test_files);
    try std.testing.expect(manifest.survey_summary.preexisting_samples_zigux_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase9_build_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase9_doc_present);
    try std.testing.expect(manifest.review_prompts.len >= 6);
    try std.testing.expectEqual(@as(usize, 14), manifest.exact_checks.len);
    try std.testing.expectEqual(@as(usize, 12), manifest.delivery_evidence_catalog.len);
    try std.testing.expectEqual(@as(usize, 12), manifest.ownership_map.len);
    try std.testing.expect(manifest.gaps.len >= 7);
    try std.testing.expectEqual(@as(usize, 6), manifest.non_goals.len);

    var saw_descriptor_contract = false;
    var saw_initial_lifecycle = false;
    var saw_bitwise_surface = false;
    var saw_swap_compare_surface = false;
    var saw_guard_surface = false;
    var saw_selftest_surface = false;
    var saw_post_selftest_replay = false;
    var saw_exit_lifecycle = false;
    var saw_loader_request_surface = false;
    var saw_loader_command_name_preservation = false;
    var saw_loader_build_leg = false;
    var saw_freeze_map_boundary_check = false;
    var saw_diff_add_bitwise = false;
    var saw_diff_swap_guard = false;
    var saw_manifest_catalog = false;
    var saw_module_slice_catalog = false;
    var saw_shared_build_catalog = false;
    var saw_loader_gap_note = false;
    var saw_runtime_loader_binding_catalog = false;
    var saw_atomic64_loader_scaffold_catalog = false;
    var saw_loader_gap_ownership = false;
    var saw_atomic64_diff_ownership = false;
    var saw_atomic64_sample_ownership = false;
    var saw_atomic64_loader_scaffold_ownership = false;
    var saw_module_slice_ownership = false;
    var saw_freeze_map_prompt = false;

    for (manifest.review_prompts) |prompt| {
        try std.testing.expect(prompt.len > 0);
        if (std.mem.indexOf(u8, prompt, "Documentation/zigux/freeze-map.md") != null) {
            saw_freeze_map_prompt = true;
        }
    }

    for (manifest.delivery_evidence_catalog, 0..) |entry, i| {
        try std.testing.expect(entry.id.len > 0);
        try std.testing.expect(entry.kind.len > 0);
        try std.testing.expect(entry.path.len > 0);
        try std.testing.expect(entry.role.len > 0);

        if (std.mem.eql(u8, entry.id, "runtime-atomic64-module-slice")) {
            saw_module_slice_catalog = true;
            try std.testing.expectEqualStrings("documentation", entry.kind);
            try std.testing.expectEqualStrings("Documentation/zigux/phase9-runtime-atomic64-module-slice.md", entry.path);
            try std.testing.expect(std.mem.indexOf(u8, entry.role, "bounded starter surface") != null);
            try std.testing.expect(std.mem.indexOf(u8, entry.role, "shared-build-leg explanation") != null);
        }
        if (std.mem.eql(u8, entry.id, "runtime-atomic64-manifest")) {
            saw_manifest_catalog = true;
            try std.testing.expectEqualStrings("manifest", entry.kind);
            try std.testing.expectEqualStrings("zigux/tests/runtime_atomic64_manifest.json", entry.path);
            try std.testing.expect(std.mem.indexOf(u8, entry.role, "delivery catalog") != null);
            try std.testing.expect(std.mem.indexOf(u8, entry.role, "ownership map") != null);
        }
        if (std.mem.eql(u8, entry.id, "phase9-atomic64-build-gate")) {
            saw_shared_build_catalog = true;
            try std.testing.expectEqualStrings("zigux/tests/phase9_build.zig", entry.path);
            try std.testing.expect(std.mem.indexOf(u8, entry.role, "phase9-runtime-atomic64-sample-tests") != null);
            try std.testing.expect(std.mem.indexOf(u8, entry.role, "phase9-runtime-atomic64-loader-tests") != null);
        }
        if (std.mem.eql(u8, entry.id, "runtime-loader-gap-note")) {
            saw_loader_gap_note = true;
            try std.testing.expectEqualStrings("documentation", entry.kind);
            try std.testing.expectEqualStrings("Documentation/zigux/phase9-runtime-loader-gap-survey.md", entry.path);
            try std.testing.expect(std.mem.indexOf(u8, entry.role, "argv-policy") != null);
        }
        if (std.mem.eql(u8, entry.id, "runtime-atomic64-shared-loader-binding")) {
            saw_runtime_loader_binding_catalog = true;
            try std.testing.expectEqualStrings("zigux/kernel/runtime_loader.zig", entry.path);
            try std.testing.expect(std.mem.indexOf(u8, entry.role, "shared runtime-loader request contract") != null);
        }
        if (std.mem.eql(u8, entry.id, "runtime-atomic64-loader-scaffold")) {
            saw_atomic64_loader_scaffold_catalog = true;
            try std.testing.expectEqualStrings("samples/zigux/runtime_atomic64_loader.zig", entry.path);
            try std.testing.expect(std.mem.indexOf(u8, entry.role, "prepared loader-summary snapshot replay") != null);
            try std.testing.expect(std.mem.indexOf(u8, entry.role, "released_without_substrate") != null);
        }

        for (manifest.delivery_evidence_catalog[i + 1 ..]) |other| {
            try std.testing.expect(!std.mem.eql(u8, entry.id, other.id));
        }
    }

    for (manifest.ownership_map, 0..) |entry, i| {
        try std.testing.expect(entry.surface.len > 0);
        try std.testing.expect(entry.owns.len > 0);

        if (std.mem.eql(u8, entry.surface, "Documentation/zigux/phase9-runtime-atomic64-module-slice.md")) {
            saw_module_slice_ownership = true;
            try std.testing.expect(std.mem.indexOf(u8, entry.owns, "bounded starter surface") != null);
            try std.testing.expect(std.mem.indexOf(u8, entry.owns, "shared-build-leg explanation") != null);
        }
        if (std.mem.eql(u8, entry.surface, "Documentation/zigux/phase9-runtime-loader-gap-survey.md")) {
            saw_loader_gap_ownership = true;
            try std.testing.expect(std.mem.indexOf(u8, entry.owns, "argv-policy") != null);
        }
        if (std.mem.eql(u8, entry.surface, "zigux/tests/runtime_atomic64_diff.zig")) {
            saw_atomic64_diff_ownership = true;
            try std.testing.expect(std.mem.indexOf(u8, entry.owns, "differential replay") != null);
        }
        if (std.mem.eql(u8, entry.surface, "samples/zigux/runtime_atomic64.zig")) {
            saw_atomic64_sample_ownership = true;
            try std.testing.expect(std.mem.indexOf(u8, entry.owns, "selftest-hook metadata") != null);
        }
        if (std.mem.eql(u8, entry.surface, "samples/zigux/runtime_atomic64_loader.zig")) {
            saw_atomic64_loader_scaffold_ownership = true;
            try std.testing.expect(std.mem.indexOf(u8, entry.owns, "prepared loader-summary snapshot replay") != null);
            try std.testing.expect(std.mem.indexOf(u8, entry.owns, "command_name preservation") != null);
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
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "runtime_atomic64") != null);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "requires_runtime_substrate true") != null);
        }
        if (std.mem.eql(u8, check.id, "initial-lifecycle-and-summary")) {
            saw_initial_lifecycle = true;
            try std.testing.expectEqualStrings("lifecycle_contract", check.kind);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "runSelftest is rejected while the sample is still cold") != null);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "init_runs 1") != null);
        }
        if (std.mem.eql(u8, check.id, "bitwise-surface")) {
            saw_bitwise_surface = true;
            try std.testing.expectEqualStrings("mutation_contract", check.kind);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "orCounter") != null);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "andNotCounter") != null);
        }
        if (std.mem.eql(u8, check.id, "swap-and-compare-swap-surface")) {
            saw_swap_compare_surface = true;
            try std.testing.expectEqualStrings("returning_contract", check.kind);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "swapCounter returns the prior 64-bit value") != null);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "mismatch previous-value path") != null);
        }
        if (std.mem.eql(u8, check.id, "guard-return-surface")) {
            saw_guard_surface = true;
            try std.testing.expectEqualStrings("guard_contract", check.kind);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "addUnlessCounter") != null);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "decIfPositiveCounter") != null);
        }
        if (std.mem.eql(u8, check.id, "selftest-surface")) {
            saw_selftest_surface = true;
            try std.testing.expectEqualStrings("selftest_contract", check.kind);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "arithmetic") != null);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "guard_ops") != null);
        }
        if (std.mem.eql(u8, check.id, "post-selftest-replay")) {
            saw_post_selftest_replay = true;
            try std.testing.expectEqualStrings("selftest_lifecycle", check.kind);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "selftest_complete") != null);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "dec_if_positive") != null);
        }
        if (std.mem.eql(u8, check.id, "exit-and-lifecycle-guards")) {
            saw_exit_lifecycle = true;
            try std.testing.expectEqualStrings("ownership_lifetime", check.kind);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "InvalidLifecycleTransition") != null);
        }
        if (std.mem.eql(u8, check.id, "loader-request-surface")) {
            saw_loader_request_surface = true;
            try std.testing.expectEqualStrings("runtime_loader_contract", check.kind);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "zigux_runtime_atomic64_init") != null);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "prepared") != null);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "waiting_on_runtime_substrate") != null);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "released_without_substrate") != null);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "kernel_heap") != null);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "before later sample mutation") != null);
        }
        if (std.mem.eql(u8, check.id, "loader-command-name-preservation")) {
            saw_loader_command_name_preservation = true;
            try std.testing.expectEqualStrings("runtime_loader_contract", check.kind);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "perf-runtime-atomic64") != null);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "releasedWithoutSubstrate") != null);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "argv-policy") != null);
        }
        if (std.mem.eql(u8, check.id, "loader-build-leg")) {
            saw_loader_build_leg = true;
            try std.testing.expectEqualStrings("shared_build_contract", check.kind);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "phase9-runtime-atomic64-loader-tests") != null);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "phase9-runtime-atomic64-sample-tests") != null);
        }
        if (std.mem.eql(u8, check.id, "shared-loader-freeze-map-boundary")) {
            saw_freeze_map_boundary_check = true;
            try std.testing.expectEqualStrings("governance_surface", check.kind);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "Documentation/zigux/freeze-map.md") != null);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "kernel/workqueue.c") != null);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "Architecture Council") != null);
        }
        if (std.mem.eql(u8, check.id, "diff-add-and-bitwise-cases")) {
            saw_diff_add_bitwise = true;
            try std.testing.expectEqualStrings("differential_validation", check.kind);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "onestwos add path") != null);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "andnot") != null);
        }
        if (std.mem.eql(u8, check.id, "diff-swap-and-guard-cases")) {
            saw_diff_swap_guard = true;
            try std.testing.expectEqualStrings("differential_validation", check.kind);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "cmpxchg success and mismatch") != null);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "single-shot lifecycle") != null);
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
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "phase9-runtime-atomic64-sample-tests") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "phase9-runtime-atomic64-loader-tests") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "sample and loader contracts stay first-class") != null);
        }
        if (std.mem.eql(u8, gap.id, "runtime-atomic64-sample-module")) {
            saw_sample_module = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("samples/zigux/runtime_atomic64.zig", gap.zigux_destination);
        }
        if (std.mem.eql(u8, gap.id, "runtime-atomic64-diff-gate")) {
            saw_diff_gate = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("zigux/tests/runtime_atomic64_diff.zig", gap.zigux_destination);
        }
        if (std.mem.eql(u8, gap.id, "runtime-atomic64-loader-scaffold")) {
            saw_loader_scaffold = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("samples/zigux/runtime_atomic64_loader.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "requires_runtime_substrate") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "no-substrate release path") != null);
        }
        if (std.mem.eql(u8, gap.id, "runtime-atomic64-live-loader-binding")) {
            saw_live_loader_binding = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("zigux/kernel/runtime_loader.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "allocator posture") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "atomic64 payload facts") != null);
        }
        if (std.mem.eql(u8, gap.id, "runtime-atomic64-shared-loader-controls")) {
            saw_shared_loader_controls_blocker = true;
            try std.testing.expectEqualStrings("blocked_on_runtime_substrate", gap.status);
            try std.testing.expectEqualStrings("Documentation/zigux/phase9-runtime-loader-gap-survey.md", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "command-name") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "pre-execution") != null);
        }

        for (manifest.gaps[i + 1 ..]) |other| {
            try std.testing.expect(!std.mem.eql(u8, gap.id, other.id));
            try std.testing.expect(!std.mem.eql(u8, gap.zigux_destination, other.zigux_destination));
        }
    }

    try std.testing.expect(runtime_test_destination_count >= 4);
    try std.testing.expect(starter_landed_count >= 7);
    try std.testing.expectEqual(@as(usize, 0), ready_next_count);
    try std.testing.expectEqual(@as(usize, 1), blocked_count);
    try std.testing.expect(saw_direct_sample_build_leg);
    try std.testing.expect(saw_sample_module);
    try std.testing.expect(saw_diff_gate);
    try std.testing.expect(saw_loader_scaffold);
    try std.testing.expect(saw_live_loader_binding);
    try std.testing.expect(saw_shared_loader_controls_blocker);
    try std.testing.expect(saw_descriptor_contract);
    try std.testing.expect(saw_initial_lifecycle);
    try std.testing.expect(saw_bitwise_surface);
    try std.testing.expect(saw_swap_compare_surface);
    try std.testing.expect(saw_guard_surface);
    try std.testing.expect(saw_selftest_surface);
    try std.testing.expect(saw_post_selftest_replay);
    try std.testing.expect(saw_exit_lifecycle);
    try std.testing.expect(saw_loader_request_surface);
    try std.testing.expect(saw_loader_build_leg);
    try std.testing.expect(saw_diff_add_bitwise);
    try std.testing.expect(saw_diff_swap_guard);
    try std.testing.expect(saw_manifest_catalog);
    try std.testing.expect(saw_module_slice_catalog);
    try std.testing.expect(saw_shared_build_catalog);
    try std.testing.expect(saw_loader_gap_note);
    try std.testing.expect(saw_runtime_loader_binding_catalog);
    try std.testing.expect(saw_atomic64_loader_scaffold_catalog);
    try std.testing.expect(saw_loader_gap_ownership);
    try std.testing.expect(saw_atomic64_diff_ownership);
    try std.testing.expect(saw_atomic64_sample_ownership);
    try std.testing.expect(saw_atomic64_loader_scaffold_ownership);
    try std.testing.expect(saw_module_slice_ownership);
    try std.testing.expect(saw_freeze_map_prompt);
    try std.testing.expect(saw_freeze_map_boundary_check);
    try std.testing.expect(saw_loader_command_name_preservation);
}

test "phase 9 runtime atomic64 docs stay aligned with the manifest-backed surveyed commit" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const manifest_json = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/runtime_atomic64_manifest.json",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(manifest_json);

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{});
    defer parsed.deinit();

    const manifest = parsed.value;

    const survey_doc = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase9-runtime-atomic64-survey.md",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(survey_doc);

    const module_slice = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase9-runtime-atomic64-module-slice.md",
        std.testing.allocator,
        .limited(16 * 1024),
    );
    defer std.testing.allocator.free(module_slice);

    const module_gate = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/runtime_atomic64_module.zig",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(module_gate);

    const required_markers = [_][]const u8{
        "`PHASE9_LANE_KEY=P9-L04`",
        "`Documentation/zigux/freeze-map.md` keeps `kernel/workqueue.c` in `Study / Boundary Only`",
        "No parity scorecard entry or Architecture Council status-change request is attached to this runtime atomic64 starter packet.",
        "the bounded guard-return trio from `lib/atomic64_test.c`: `add_unless`, `inc_not_zero`, and `dec_if_positive`",
        "a narrow differential gate under `zigux/tests/runtime_atomic64_diff.zig` for bounded add, sub, bitwise, swap, compare-swap, and guard-return expectations drawn from `lib/atomic64_test.c`",
        "a landed sample-side loader scaffold under `samples/zigux/runtime_atomic64_loader.zig` plus a shared runtime-loader request binding under `zigux/kernel/runtime_loader.zig`",
        "a prepared loader-summary snapshot replay that freezes the four-field `RuntimeAtomic64Summary` handoff before later sample mutation and keeps that same snapshot explicit through both `waiting_on_runtime_substrate` and `released_without_substrate` review paths",
        "a bounded shared `command_name` preservation check in `samples/zigux/runtime_atomic64_loader.zig` that keeps a synthetic non-null loader request reviewable through both `waiting_on_runtime_substrate` and `released_without_substrate` without claiming live argv policy or runtime execution",
        "this shared build includes the direct `phase9-runtime-atomic64-sample-tests` and `phase9-runtime-atomic64-loader-tests` legs alongside the atomic64 module, diff, survey, loader, and shared runtime-loader checks",
        "any freeze-map status change for the scheduler-facing workqueue boundary without an Architecture Council decision",
        "keep future work narrowly aimed at the remaining runtime substrate handoff or broader shared loader-control blocker, rather than reopening already-landed starter, loader-request, or differential scaffolds",
    };

    for (required_markers) |marker| {
        try std.testing.expect(std.mem.indexOf(u8, module_slice, marker) != null);
    }

    const required_module_gate_markers = [_][]const u8{
        "const cold_summary = module.summary();",
        "const initialized_summary = module.summary();",
        "const post_selftest_summary = module.summary();",
        "const exited_summary = module.summary();",
        "try std.testing.expectEqual(@as(usize, 1), post_selftest_summary.selftest_runs);",
        "try std.testing.expectEqual(@as(usize, 1), exited_summary.exit_runs);",
        "test \"runtime atomic64 sample keeps post-selftest mutation replay explicit at the module boundary\" {",
    };

    for (required_module_gate_markers) |marker| {
        try std.testing.expect(std.mem.indexOf(u8, module_gate, marker) != null);
    }

    try expectSurveyedCommitMarker(survey_doc, manifest.surveyed_commit);
    try expectPinnedCommitSentence(survey_doc, manifest.surveyed_commit);
    try expectSurveyedCommitMarker(module_slice, manifest.surveyed_commit);
    try std.testing.expect(std.mem.indexOf(
        u8,
        survey_doc,
        "keeping the bounded lifecycle, selftest, and pre-execution runtime-pilot packet green without widening into unrelated shared runtime-loader control work.",
    ) != null);
    try std.testing.expect(std.mem.indexOf(
        u8,
        survey_doc,
        "first-loadable-module parity packet",
    ) == null);

    try std.testing.expect(std.mem.indexOf(
        u8,
        module_slice,
        "most likely `dec_if_positive`",
    ) == null);
}
