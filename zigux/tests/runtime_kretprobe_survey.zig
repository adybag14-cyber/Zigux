const std = @import("std");

const SurveySummary = struct {
    kretprobe_example_c_lines: usize,
    preexisting_runtime_kretprobe_test_files: usize,
    preexisting_runtime_kretprobe_sample_present: bool,
    preexisting_phase9_build_present: bool,
    preexisting_runtime_kretprobe_doc_present: bool,
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

fn readWorkspaceFile(
    io: anytype,
    allocator: std.mem.Allocator,
    path: []const u8,
    limit: usize,
) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(io, path, allocator, .limited(limit));
}

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

test "phase 9 runtime kretprobe survey manifest records the landed ownership packet and remaining shared control blocker" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const manifest_json = try readWorkspaceFile(
        io_instance.io(),
        std.testing.allocator,
        "zigux/tests/runtime_kretprobe_manifest.json",
        32 * 1024,
    );
    defer std.testing.allocator.free(manifest_json);

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{});
    defer parsed.deinit();

    const manifest = parsed.value;
    try std.testing.expectEqualStrings("P9-L13", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 9", manifest.phase);
    try std.testing.expect(isLowerHexSha(manifest.surveyed_commit));
    try std.testing.expectEqualStrings("samples/kprobes/kretprobe_example.c", manifest.anchor);
    try std.testing.expectEqual(@as(usize, 2), manifest.roadmap_destinations.len);
    try std.testing.expectEqualStrings("samples/zigux/runtime_kretprobe.zig", manifest.sample_path);
    try std.testing.expectEqualStrings("zig build test --build-file zigux/tests/phase9_build.zig --summary all", manifest.validation_entrypoint);
    try std.testing.expect(manifest.survey_summary.kretprobe_example_c_lines >= 100);
    try std.testing.expectEqual(@as(usize, 3), manifest.survey_summary.preexisting_runtime_kretprobe_test_files);
    try std.testing.expect(manifest.survey_summary.preexisting_runtime_kretprobe_sample_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase9_build_present);
    try std.testing.expect(manifest.survey_summary.preexisting_runtime_kretprobe_doc_present);
    try std.testing.expectEqual(@as(usize, 7), manifest.review_prompts.len);
    try std.testing.expectEqual(@as(usize, 8), manifest.exact_checks.len);
    try std.testing.expectEqual(@as(usize, 11), manifest.delivery_evidence_catalog.len);
    try std.testing.expectEqual(@as(usize, 11), manifest.ownership_map.len);
    try std.testing.expectEqual(@as(usize, 8), manifest.gaps.len);
    try std.testing.expectEqual(@as(usize, 5), manifest.non_goals.len);

    var saw_loader_rollback_prompt = false;
    var saw_loader_command_name_prompt = false;
    var saw_shared_build_prompt = false;
    var saw_roadmap_gap_prompt = false;
    for (manifest.review_prompts) |prompt| {
        try std.testing.expect(prompt.len > 0);
        if (std.mem.indexOf(u8, prompt, "released_without_substrate") != null) {
            saw_loader_rollback_prompt = true;
        }
        if (std.mem.indexOf(u8, prompt, "synthetic non-null shared command_name") != null) {
            saw_loader_command_name_prompt = true;
        }
        if (std.mem.indexOf(u8, prompt, "phase9-runtime-kretprobe-module-tests") != null) {
            saw_shared_build_prompt = true;
        }
        if (std.mem.indexOf(u8, prompt, "first loadable Zigux runtime modules") != null) {
            saw_roadmap_gap_prompt = true;
        }
    }

    var saw_lifecycle_summary_check = false;
    var saw_maxactive_preinit_check = false;
    var saw_loader_rollback_check = false;
    var saw_loader_command_name_check = false;
    var saw_shared_build_check = false;
    var saw_delivery_packet_check = false;
    var saw_shared_controls_check = false;
    var saw_roadmap_gap_check = false;
    for (manifest.exact_checks, 0..) |check, i| {
        try std.testing.expect(check.id.len > 0);
        try std.testing.expect(check.kind.len > 0);
        try std.testing.expect(check.expected.len > 0);

        if (std.mem.eql(u8, check.id, "lifecycle-summary-surface")) {
            saw_lifecycle_summary_check = true;
            try std.testing.expectEqualStrings("summary_contract", check.kind);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "RuntimeKretprobeSummary") != null);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "latest bounded probe results") != null);
        }
        if (std.mem.eql(u8, check.id, "maxactive-preinit-surface")) {
            saw_maxactive_preinit_check = true;
            try std.testing.expectEqualStrings("starter_contract", check.kind);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "configureMaxactive()") != null);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "default_maxactive") != null);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "rejecting zero, over-cap, or post-init retunes") != null);
        }
        if (std.mem.eql(u8, check.id, "loader-rollback-surface")) {
            saw_loader_rollback_check = true;
            try std.testing.expectEqualStrings("runtime_loader_contract", check.kind);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "register and unregister API names") != null);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "released_without_substrate") != null);
        }
        if (std.mem.eql(u8, check.id, "loader-command-name-preservation")) {
            saw_loader_command_name_check = true;
            try std.testing.expectEqualStrings("runtime_loader_contract", check.kind);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "perf-runtime-kretprobe") != null);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "argv-policy") != null);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "environment-derived activation ownership") != null);
        }
        if (std.mem.eql(u8, check.id, "shared-build-leg-surface")) {
            saw_shared_build_check = true;
            try std.testing.expectEqualStrings("shared_build_contract", check.kind);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "phase9-runtime-kretprobe-sample-tests") != null);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "phase9-runtime-kretprobe-module-tests") != null);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "phase9-runtime-kretprobe-loader-tests") != null);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "phase9-runtime-kretprobe-survey-tests") != null);
        }
        if (std.mem.eql(u8, check.id, "delivery-ownership-packet")) {
            saw_delivery_packet_check = true;
            try std.testing.expectEqualStrings("review_surface", check.kind);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "delivery catalog") != null);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "ownership map") != null);
        }
        if (std.mem.eql(u8, check.id, "shared-loader-controls-blocker")) {
            saw_shared_controls_check = true;
            try std.testing.expectEqualStrings("runtime_control_surface", check.kind);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "command-name") != null);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "argv-policy") != null);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "environment-derived activation handling") != null);
        }
        if (std.mem.eql(u8, check.id, "roadmap-gap-vs-pilot-module")) {
            saw_roadmap_gap_check = true;
            try std.testing.expectEqualStrings("roadmap_gap", check.kind);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "selftest hooks are landed") != null);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "module_init()") != null);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "module_exit()") != null);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "register_kretprobe()") != null);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "unregister_kretprobe()") != null);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "first loadable Zigux runtime modules") != null);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "runtime module lifecycle parity") != null);
        }

        for (manifest.exact_checks[i + 1 ..]) |other| {
            try std.testing.expect(!std.mem.eql(u8, check.id, other.id));
        }
    }

    var saw_manifest_catalog = false;
    var saw_build_catalog = false;
    var saw_sample_catalog = false;
    var saw_loader_catalog = false;
    var saw_binding_catalog = false;
    var saw_gap_note_catalog = false;
    for (manifest.delivery_evidence_catalog, 0..) |entry, i| {
        try std.testing.expect(entry.id.len > 0);
        try std.testing.expect(entry.kind.len > 0);
        try std.testing.expect(entry.path.len > 0);
        try std.testing.expect(entry.role.len > 0);

        if (std.mem.eql(u8, entry.id, "runtime-kretprobe-manifest")) {
            saw_manifest_catalog = true;
            try std.testing.expectEqualStrings("manifest", entry.kind);
            try std.testing.expectEqualStrings("zigux/tests/runtime_kretprobe_manifest.json", entry.path);
            try std.testing.expect(std.mem.indexOf(u8, entry.role, "delivery catalog") != null);
            try std.testing.expect(std.mem.indexOf(u8, entry.role, "ownership map") != null);
        }
        if (std.mem.eql(u8, entry.id, "phase9-kretprobe-build-gate")) {
            saw_build_catalog = true;
            try std.testing.expectEqualStrings("zigux/tests/phase9_build.zig", entry.path);
            try std.testing.expect(std.mem.indexOf(u8, entry.role, "phase9-runtime-kretprobe-sample-tests") != null);
            try std.testing.expect(std.mem.indexOf(u8, entry.role, "phase9-runtime-kretprobe-module-tests") != null);
            try std.testing.expect(std.mem.indexOf(u8, entry.role, "phase9-runtime-kretprobe-loader-tests") != null);
        }
        if (std.mem.eql(u8, entry.id, "runtime-kretprobe-sample")) {
            saw_sample_catalog = true;
            try std.testing.expectEqualStrings("samples/zigux/runtime_kretprobe.zig", entry.path);
            try std.testing.expect(std.mem.indexOf(u8, entry.role, "selftest-hook metadata") != null);
        }
        if (std.mem.eql(u8, entry.id, "runtime-kretprobe-loader-scaffold")) {
            saw_loader_catalog = true;
            try std.testing.expectEqualStrings("samples/zigux/runtime_kretprobe_loader.zig", entry.path);
            try std.testing.expect(std.mem.indexOf(u8, entry.role, "explicit shared command_name preservation") != null);
            try std.testing.expect(std.mem.indexOf(u8, entry.role, "released_without_substrate") != null);
        }
        if (std.mem.eql(u8, entry.id, "runtime-kretprobe-shared-loader-binding")) {
            saw_binding_catalog = true;
            try std.testing.expectEqualStrings("zigux/kernel/runtime_loader.zig", entry.path);
            try std.testing.expect(std.mem.indexOf(u8, entry.role, "shared runtime-loader request contract") != null);
        }
        if (std.mem.eql(u8, entry.id, "runtime-loader-gap-note")) {
            saw_gap_note_catalog = true;
            try std.testing.expectEqualStrings("Documentation/zigux/phase9-runtime-loader-gap-survey.md", entry.path);
            try std.testing.expect(std.mem.indexOf(u8, entry.role, "argv-policy") != null);
        }

        for (manifest.delivery_evidence_catalog[i + 1 ..]) |other| {
            try std.testing.expect(!std.mem.eql(u8, entry.id, other.id));
        }
    }

    var saw_phase9_build_ownership = false;
    var saw_sample_ownership = false;
    var saw_loader_gap_ownership = false;
    for (manifest.ownership_map, 0..) |entry, i| {
        try std.testing.expect(entry.surface.len > 0);
        try std.testing.expect(entry.owns.len > 0);

        if (std.mem.eql(u8, entry.surface, "zigux/tests/phase9_build.zig")) {
            saw_phase9_build_ownership = true;
            try std.testing.expect(std.mem.indexOf(u8, entry.owns, "sample, module, diff, loader, and survey legs") != null);
        }
        if (std.mem.eql(u8, entry.surface, "samples/zigux/runtime_kretprobe.zig")) {
            saw_sample_ownership = true;
            try std.testing.expect(std.mem.indexOf(u8, entry.owns, "selftest-hook metadata") != null);
        }
        if (std.mem.eql(u8, entry.surface, "samples/zigux/runtime_kretprobe_loader.zig")) {
            try std.testing.expect(std.mem.indexOf(u8, entry.owns, "explicit shared command_name preservation") != null);
        }
        if (std.mem.eql(u8, entry.surface, "Documentation/zigux/phase9-runtime-loader-gap-survey.md")) {
            saw_loader_gap_ownership = true;
            try std.testing.expect(std.mem.indexOf(u8, entry.owns, "argv-policy") != null);
        }

        for (manifest.ownership_map[i + 1 ..]) |other| {
            try std.testing.expect(!std.mem.eql(u8, entry.surface, other.surface));
        }
    }

    var runtime_test_destination_count: usize = 0;
    var starter_landed_count: usize = 0;
    var blocked_count: usize = 0;
    var saw_build_gap = false;
    var saw_loader_gap = false;
    for (manifest.gaps, 0..) |gap, i| {
        try std.testing.expect(gap.id.len > 0);
        try std.testing.expect(gap.kind.len > 0);
        try std.testing.expect(gap.why_now.len > 0);
        try std.testing.expect(isAllowedStatus(gap.status));

        if (std.mem.startsWith(u8, gap.zigux_destination, "zigux/tests/")) {
            runtime_test_destination_count += 1;
        }
        if (std.mem.eql(u8, gap.status, "starter_landed")) starter_landed_count += 1;
        if (std.mem.eql(u8, gap.status, "blocked_on_runtime_substrate")) blocked_count += 1;

        if (std.mem.eql(u8, gap.id, "phase9-build-gate")) {
            saw_build_gap = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "phase9-runtime-kretprobe-sample-tests") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "phase9-runtime-kretprobe-module-tests") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "phase9-runtime-kretprobe-survey-tests") != null);
        }
        if (std.mem.eql(u8, gap.id, "runtime-kretprobe-shared-loader-controls")) {
            saw_loader_gap = true;
            try std.testing.expectEqualStrings("blocked_on_runtime_substrate", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "command-name") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "pre-execution") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "first loadable Zigux runtime modules") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "runtime module lifecycle parity") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "selftest-hook surface") != null);
        }

        for (manifest.gaps[i + 1 ..]) |other| {
            try std.testing.expect(!std.mem.eql(u8, gap.id, other.id));
            try std.testing.expect(!std.mem.eql(u8, gap.zigux_destination, other.zigux_destination));
        }
    }

    try std.testing.expect(runtime_test_destination_count >= 4);
    try std.testing.expect(starter_landed_count >= 7);
    try std.testing.expectEqual(@as(usize, 1), blocked_count);
    try std.testing.expect(saw_loader_rollback_prompt);
    try std.testing.expect(saw_loader_command_name_prompt);
    try std.testing.expect(saw_shared_build_prompt);
    try std.testing.expect(saw_roadmap_gap_prompt);
    try std.testing.expect(saw_lifecycle_summary_check);
    try std.testing.expect(saw_maxactive_preinit_check);
    try std.testing.expect(saw_loader_rollback_check);
    try std.testing.expect(saw_loader_command_name_check);
    try std.testing.expect(saw_shared_build_check);
    try std.testing.expect(saw_delivery_packet_check);
    try std.testing.expect(saw_shared_controls_check);
    try std.testing.expect(saw_roadmap_gap_check);
    try std.testing.expect(saw_manifest_catalog);
    try std.testing.expect(saw_build_catalog);
    try std.testing.expect(saw_sample_catalog);
    try std.testing.expect(saw_loader_catalog);
    try std.testing.expect(saw_binding_catalog);
    try std.testing.expect(saw_gap_note_catalog);
    try std.testing.expect(saw_phase9_build_ownership);
    try std.testing.expect(saw_sample_ownership);
    try std.testing.expect(saw_loader_gap_ownership);
    try std.testing.expect(saw_build_gap);
    try std.testing.expect(saw_loader_gap);
}

test "phase 9 runtime kretprobe docs keep the ownership packet and shared-build legs explicit" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const manifest_json = try readWorkspaceFile(
        io_instance.io(),
        std.testing.allocator,
        "zigux/tests/runtime_kretprobe_manifest.json",
        32 * 1024,
    );
    defer std.testing.allocator.free(manifest_json);

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{});
    defer parsed.deinit();

    const manifest = parsed.value;

    const survey_doc = try readWorkspaceFile(
        io_instance.io(),
        std.testing.allocator,
        "Documentation/zigux/phase9-runtime-kretprobe-survey.md",
        24 * 1024,
    );
    defer std.testing.allocator.free(survey_doc);

    const module_doc = try readWorkspaceFile(
        io_instance.io(),
        std.testing.allocator,
        "Documentation/zigux/phase9-runtime-kretprobe-module-slice.md",
        20 * 1024,
    );
    defer std.testing.allocator.free(module_doc);

    const module_test = try readWorkspaceFile(
        io_instance.io(),
        std.testing.allocator,
        "zigux/tests/runtime_kretprobe_module.zig",
        24 * 1024,
    );
    defer std.testing.allocator.free(module_test);

    const sample_file = try readWorkspaceFile(
        io_instance.io(),
        std.testing.allocator,
        "samples/zigux/runtime_kretprobe.zig",
        24 * 1024,
    );
    defer std.testing.allocator.free(sample_file);

    const loader_file = try readWorkspaceFile(
        io_instance.io(),
        std.testing.allocator,
        "samples/zigux/runtime_kretprobe_loader.zig",
        24 * 1024,
    );
    defer std.testing.allocator.free(loader_file);

    const runtime_loader_file = try readWorkspaceFile(
        io_instance.io(),
        std.testing.allocator,
        "zigux/kernel/runtime_loader.zig",
        40 * 1024,
    );
    defer std.testing.allocator.free(runtime_loader_file);

    const phase9_build_file = try readWorkspaceFile(
        io_instance.io(),
        std.testing.allocator,
        "zigux/tests/phase9_build.zig",
        32 * 1024,
    );
    defer std.testing.allocator.free(phase9_build_file);

    const required_survey_markers = [_][]const u8{
        "`PHASE9_LANE_KEY=P9-L13`",
        "manifest-backed delivery catalog and ownership map",
        "Latest verification snapshot",
        "zig test samples/zigux/runtime_kretprobe.zig",
        "zig fmt --check samples/zigux/runtime_kretprobe.zig",
        "zig test zigux/tests/runtime_kretprobe_survey.zig",
        "zig build test --build-file zigux/tests/phase9_build.zig --summary all",
        "Delivery ownership map",
        "phase9-runtime-kretprobe-sample-tests",
        "phase9-runtime-kretprobe-module-tests",
        "phase9-runtime-kretprobe-diff-tests",
        "phase9-runtime-kretprobe-loader-tests",
        "phase9-runtime-kretprobe-survey-tests",
        "perf-runtime-kretprobe",
        "configureMaxactive()",
        "RuntimeKretprobeSummary",
        "failed-exit rollback proof",
        "released_without_substrate",
        "shared lifecycle-boundary summary",
        "module_init()",
        "module_exit()",
        "register_kretprobe()",
        "unregister_kretprobe()",
        "phase9-runtime-loader-non-owner-boundary-survey-tests",
        "StreamTooLong",
        "first loadable Zigux runtime modules",
        "runtime module lifecycle parity",
        "Documentation/zigux/phase9-runtime-loader-gap-survey.md",
        "rather than reopening already-landed sample, survey, manifest, loader-scaffold, shared binding, module-gate, or diff-gate scaffolding",
    };
    for (required_survey_markers) |marker| {
        try std.testing.expect(std.mem.indexOf(u8, survey_doc, marker) != null);
    }
    try std.testing.expect(std.mem.indexOf(u8, survey_doc, "phase9-runtime-kretprobe-loader-tests") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_doc, "perf-runtime-kretprobe") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_doc, "RuntimeKretprobeSummary") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_doc, "released_without_substrate") != null);

    const required_module_markers = [_][]const u8{
        "`PHASE9_LANE_KEY=P9-L13`",
        "phase9-runtime-kretprobe-sample-tests",
        "phase9-runtime-kretprobe-module-tests",
        "phase9-runtime-kretprobe-diff-tests",
        "phase9-runtime-kretprobe-loader-tests",
        "phase9-runtime-kretprobe-survey-tests",
        "perf-runtime-kretprobe",
        "configureMaxactive()",
        "manifest-backed survey packet",
        "this shared build keeps the dedicated kretprobe sample, module, diff, loader, and survey legs explicit",
        "direct post-selftest replay proof",
        "failed-exit rollback proof",
        "rather than reopening already-landed sample, survey, manifest, loader, module, or diff scaffolding",
    };
    for (required_module_markers) |marker| {
        try std.testing.expect(std.mem.indexOf(u8, module_doc, marker) != null);
    }
    try std.testing.expect(std.mem.indexOf(u8, module_doc, "RuntimeKretprobeSummary") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_doc, "configureMaxactive()") != null);
    try std.testing.expect(std.mem.indexOf(u8, module_doc, "configureMaxactive()") != null);
    try std.testing.expect(std.mem.indexOf(u8, module_doc, "direct post-selftest replay proof") != null);
    try std.testing.expect(std.mem.indexOf(u8, module_doc, "OutstandingProbeInstance") != null);
    try std.testing.expect(std.mem.indexOf(u8, module_doc, "selftest_complete") != null);
    try std.testing.expect(std.mem.indexOf(u8, module_doc, "`nmissed` replay") != null);

    const required_sample_markers = [_][]const u8{
        "pub const RuntimeKretprobeSummary = struct",
        "pub fn configureMaxactive",
        "pub fn runSelftest",
        "pub fn entryHandler",
        "entry_timestamp_armed = self.active_instances > 0",
        "test \"runtime kretprobe sample keeps failed exit rollback explicit in the direct sample leg\"",
        "test \"runtime kretprobe sample keeps lifecycle replay and summary accounting explicit\"",
    };
    for (required_sample_markers) |marker| {
        try std.testing.expect(std.mem.indexOf(u8, sample_file, marker) != null);
    }

    const required_loader_markers = [_][]const u8{
        "pub fn planForWithCommandName",
        "pub fn releaseSharedRuntimeLoadWithoutSubstrate",
        "pub fn toSharedRequest",
        "error.EmptyCommandName",
        "\"perf-runtime-kretprobe\"",
        "request.releasedWithoutSubstrate()",
        "entry_timestamp_armed = plan.summary.entry_timestamp_armed",
    };
    for (required_loader_markers) |marker| {
        try std.testing.expect(std.mem.indexOf(u8, loader_file, marker) != null);
    }

    const required_phase9_build_markers = [_][]const u8{
        ".name = \"phase9-runtime-kretprobe-sample-tests\"",
        ".name = \"phase9-runtime-kretprobe-module-tests\"",
        ".name = \"phase9-runtime-kretprobe-diff-tests\"",
        ".name = \"phase9-runtime-kretprobe-loader-tests\"",
        ".name = \"phase9-runtime-kretprobe-survey-tests\"",
        "test_step.dependOn(&run_runtime_kretprobe_sample_tests.step);",
        "test_step.dependOn(&run_runtime_kretprobe_module_tests.step);",
        "test_step.dependOn(&run_runtime_kretprobe_diff_tests.step);",
        "test_step.dependOn(&run_runtime_kretprobe_loader_tests.step);",
        "test_step.dependOn(&run_runtime_kretprobe_survey_tests.step);",
    };
    for (required_phase9_build_markers) |marker| {
        try std.testing.expect(std.mem.indexOf(u8, phase9_build_file, marker) != null);
    }

    try std.testing.expect(std.mem.indexOf(u8, runtime_loader_file, "pub fn keepsPreExecutionLifecycleBoundaryExplicit") != null);
    try std.testing.expect(std.mem.indexOf(u8, runtime_loader_file, "\"module_init\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, runtime_loader_file, "\"module_exit\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, runtime_loader_file, "payload.register_api.len > 0") != null);
    try std.testing.expect(std.mem.indexOf(u8, runtime_loader_file, "payload.unregister_api.len > 0") != null);
    try std.testing.expect(std.mem.indexOf(u8, runtime_loader_file, "payload.register_api, self.entry_symbol") != null);
    try std.testing.expect(std.mem.indexOf(u8, runtime_loader_file, "payload.unregister_api, self.exit_symbol") != null);

    try expectSurveyedCommitMarker(survey_doc, manifest.surveyed_commit);
    try expectPinnedCommitSentence(survey_doc, manifest.surveyed_commit);
    try expectSurveyedCommitMarker(module_doc, manifest.surveyed_commit);
    try std.testing.expect(std.mem.indexOf(u8, survey_doc, manifest.surveyed_commit) != null);
    try std.testing.expect(std.mem.indexOf(u8, module_doc, manifest.surveyed_commit) != null);
    try std.testing.expect(std.mem.indexOf(u8, module_test, "test \"runtime kretprobe sample keeps post-selftest replay explicit at the module boundary\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, module_test, "try std.testing.expectEqual(@as(usize, 2), summary.nmissed);") != null);
    try std.testing.expect(std.mem.indexOf(u8, module_test, "try std.testing.expectError(error.OutstandingProbeInstance, outstanding.exit());") != null);
    try std.testing.expect(std.mem.indexOf(u8, module_test, "try std.testing.expectEqual(before_failed_exit.entry_timestamp_armed, after_failed_exit.entry_timestamp_armed);") != null);
}