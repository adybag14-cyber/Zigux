const std = @import("std");
const sample = @import("runtime_trace_events_sample");

const SurveySummary = struct {
    trace_events_sample_c_lines: usize,
    trace_events_sample_header_lines: usize,
    preexisting_runtime_trace_events_test_files: usize,
    preexisting_runtime_trace_events_sample_present: bool,
    preexisting_trace_events_header_present: bool,
    runtime_trace_events_loader_present: bool,
    preexisting_phase9_build_present: bool,
    preexisting_runtime_trace_events_doc_present: bool,
    preexisting_runtime_trace_events_summary_surface_present: bool,
};

const Gap = struct {
    id: []const u8,
    status: []const u8,
    kind: []const u8,
    zigux_destination: []const u8,
    why_now: []const u8,
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
    delivery_evidence_catalog: []const DeliveryEvidence,
    ownership_map: []const OwnershipEntry,
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

fn readWorkspaceFile(
    io: anytype,
    allocator: std.mem.Allocator,
    path: []const u8,
    limit: usize,
) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(io, path, allocator, .limited(limit));
}

test "phase 9 runtime trace-events survey manifest stays anchored to the survey lane while recording the landed diff gate and blocker" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const manifest_json = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/runtime_trace_events_manifest.json",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(manifest_json);

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{});
    defer parsed.deinit();

    const manifest = parsed.value;
    const surveyed_commit = manifest.surveyed_commit;
    try std.testing.expectEqualStrings("P9-L12", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 9", manifest.phase);
    try std.testing.expect(isLowerHexSha(surveyed_commit));
    try std.testing.expectEqualStrings("samples/trace_events/trace-events-sample.c", manifest.anchor);
    try std.testing.expectEqual(@as(usize, 2), manifest.roadmap_destinations.len);
    try std.testing.expectEqualStrings("samples/zigux/runtime_trace_events.zig", manifest.sample_path);
    try std.testing.expectEqualStrings("zig build test --build-file zigux/tests/phase9_build.zig --summary all", manifest.validation_entrypoint);
    try std.testing.expect(manifest.survey_summary.trace_events_sample_c_lines >= 150);
    try std.testing.expectEqual(@as(usize, 640), manifest.survey_summary.trace_events_sample_header_lines);
    try std.testing.expectEqual(@as(usize, 3), manifest.survey_summary.preexisting_runtime_trace_events_test_files);
    try std.testing.expect(manifest.survey_summary.preexisting_runtime_trace_events_sample_present);
    try std.testing.expect(manifest.survey_summary.preexisting_trace_events_header_present);
    try std.testing.expect(manifest.survey_summary.runtime_trace_events_loader_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase9_build_present);
    try std.testing.expect(manifest.survey_summary.preexisting_runtime_trace_events_doc_present);
    try std.testing.expect(manifest.survey_summary.preexisting_runtime_trace_events_summary_surface_present);
    try std.testing.expectEqual(@as(usize, 6), manifest.review_prompts.len);
    try std.testing.expectEqual(@as(usize, 10), manifest.delivery_evidence_catalog.len);
    try std.testing.expectEqual(@as(usize, 10), manifest.ownership_map.len);
    try std.testing.expectEqual(@as(usize, 10), manifest.exact_checks.len);
    try std.testing.expect(manifest.gaps.len >= 6);
    try std.testing.expectEqual(@as(usize, 7), manifest.non_goals.len);

    var runtime_test_destination_count: usize = 0;
    var starter_landed_count: usize = 0;
    var ready_next_count: usize = 0;
    var blocked_count: usize = 0;
    var saw_loader_free_prompt = false;
    var saw_header_boundary_prompt = false;
    var saw_freeze_map_prompt = false;
    var saw_ownership_prompt = false;
    var saw_descriptor_contract = false;
    var saw_summary_surface = false;
    var saw_summary_run_counters = false;
    var saw_main_payload_surface = false;
    var saw_function_balance = false;
    var saw_selftest_family_order = false;
    var saw_failed_exit_rollback = false;
    var saw_trace_header_boundary_check = false;
    var saw_freeze_map_boundary_check = false;
    var saw_loader_free_blocker_check = false;
    var saw_sample_module = false;
    var saw_loader_scaffold_gap = false;
    var saw_diff_gate = false;
    var saw_freeze_map_boundary = false;
    var saw_manifest_catalog = false;
    var saw_loader_scaffold_catalog = false;
    var saw_module_slice_catalog = false;
    var saw_shared_build_catalog = false;
    var saw_freeze_map_catalog = false;
    var saw_loader_scaffold_ownership = false;
    var saw_module_slice_ownership = false;

    for (manifest.review_prompts) |prompt| {
        try std.testing.expect(prompt.len > 0);
        if (std.mem.indexOf(u8, prompt, "blocked loader boundary") != null) {
            saw_loader_free_prompt = true;
        }
        if (std.mem.indexOf(u8, prompt, "delivery catalog and ownership map") != null) {
            saw_ownership_prompt = true;
        }
        if (std.mem.indexOf(u8, prompt, "module-slice note") != null) {
            saw_ownership_prompt = true;
        }
        if (std.mem.indexOf(u8, prompt, "trace-events-sample.h") != null) {
            saw_header_boundary_prompt = true;
        }
        if (std.mem.indexOf(u8, prompt, "`kernel/trace/ring_buffer.c`") != null) {
            saw_freeze_map_prompt = true;
        }
    }

    for (manifest.delivery_evidence_catalog, 0..) |entry, i| {
        try std.testing.expect(entry.id.len > 0);
        try std.testing.expect(entry.kind.len > 0);
        try std.testing.expect(entry.path.len > 0);
        try std.testing.expect(entry.role.len > 0);

        if (std.mem.eql(u8, entry.id, "runtime-trace-events-manifest")) {
            saw_manifest_catalog = true;
            try std.testing.expectEqualStrings("manifest", entry.kind);
            try std.testing.expectEqualStrings("zigux/tests/runtime_trace_events_manifest.json", entry.path);
            try std.testing.expect(std.mem.indexOf(u8, entry.role, "delivery catalog") != null);
            try std.testing.expect(std.mem.indexOf(u8, entry.role, "ownership map") != null);
        }
        if (std.mem.eql(u8, entry.id, "runtime-trace-events-loader-scaffold")) {
            saw_loader_scaffold_catalog = true;
            try std.testing.expectEqualStrings("runtime_loader_scaffold", entry.kind);
            try std.testing.expectEqualStrings("samples/zigux/runtime_trace_events_loader.zig", entry.path);
            try std.testing.expect(std.mem.indexOf(u8, entry.role, "loader-plan scaffold") != null);
            try std.testing.expect(std.mem.indexOf(u8, entry.role, "release-without-substrate fallback") != null);
        }
        if (std.mem.eql(u8, entry.id, "phase9-trace-events-build-gate")) {
            saw_shared_build_catalog = true;
            try std.testing.expectEqualStrings("validation", entry.kind);
            try std.testing.expectEqualStrings("zigux/tests/phase9_build.zig", entry.path);
            try std.testing.expect(std.mem.indexOf(u8, entry.role, "shared Phase 9 runtime bundle entrypoint") != null);
            try std.testing.expect(std.mem.indexOf(u8, entry.role, "loader scaffold replayable") != null);
            try std.testing.expect(std.mem.indexOf(u8, entry.role, "shared runtime-loader binding still stays absent") != null);
        }
        if (std.mem.eql(u8, entry.id, "runtime-trace-events-module-slice")) {
            saw_module_slice_catalog = true;
            try std.testing.expectEqualStrings("documentation", entry.kind);
            try std.testing.expectEqualStrings("Documentation/zigux/phase9-runtime-trace-events-module-slice.md", entry.path);
            try std.testing.expect(std.mem.indexOf(u8, entry.role, "landed starter surface summary") != null);
            try std.testing.expect(std.mem.indexOf(u8, entry.role, "blocked loader-scaffold restatement") != null);
            try std.testing.expect(std.mem.indexOf(u8, entry.role, "header-side macro boundary note") != null);
        }
        if (std.mem.eql(u8, entry.id, "runtime-trace-events-freeze-map")) {
            saw_freeze_map_catalog = true;
            try std.testing.expectEqualStrings("governance", entry.kind);
            try std.testing.expectEqualStrings("Documentation/zigux/freeze-map.md", entry.path);
            try std.testing.expect(std.mem.indexOf(u8, entry.role, "`kernel/trace/ring_buffer.c`") != null);
            try std.testing.expect(std.mem.indexOf(u8, entry.role, "Architecture Council") != null);
        }

        for (manifest.delivery_evidence_catalog[i + 1 ..]) |other| {
            try std.testing.expect(!std.mem.eql(u8, entry.id, other.id));
        }
    }

    for (manifest.ownership_map, 0..) |entry, i| {
        try std.testing.expect(entry.surface.len > 0);
        try std.testing.expect(entry.owns.len > 0);

        if (std.mem.eql(u8, entry.surface, "samples/zigux/runtime_trace_events_loader.zig")) {
            saw_loader_scaffold_ownership = true;
            try std.testing.expect(std.mem.indexOf(u8, entry.owns, "loader-plan scaffold") != null);
            try std.testing.expect(std.mem.indexOf(u8, entry.owns, "release-without-substrate fallback") != null);
        }
        if (std.mem.eql(u8, entry.surface, "zigux/tests/runtime_trace_events_manifest.json")) {
            try std.testing.expect(std.mem.indexOf(u8, entry.owns, "delivery catalog") != null);
            try std.testing.expect(std.mem.indexOf(u8, entry.owns, "ownership map") != null);
        }
        if (std.mem.eql(u8, entry.surface, "Documentation/zigux/freeze-map.md")) {
            try std.testing.expect(std.mem.indexOf(u8, entry.owns, "`kernel/trace/ring_buffer.c`") != null);
            try std.testing.expect(std.mem.indexOf(u8, entry.owns, "Architecture Council") != null);
        }
        if (std.mem.eql(u8, entry.surface, "Documentation/zigux/phase9-runtime-trace-events-module-slice.md")) {
            saw_module_slice_ownership = true;
            try std.testing.expect(std.mem.indexOf(u8, entry.owns, "landed starter surface summary") != null);
            try std.testing.expect(std.mem.indexOf(u8, entry.owns, "blocked loader-scaffold restatement") != null);
            try std.testing.expect(std.mem.indexOf(u8, entry.owns, "header-side macro boundary note") != null);
        }
        if (std.mem.eql(u8, entry.surface, "zigux/tests/phase9_build.zig")) {
            try std.testing.expect(std.mem.indexOf(u8, entry.owns, "shared Phase 9 runtime bundle entrypoint") != null);
            try std.testing.expect(std.mem.indexOf(u8, entry.owns, "loader scaffold") != null);
            try std.testing.expect(std.mem.indexOf(u8, entry.owns, "shared runtime-loader binding still stays absent") != null);
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
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "runtime_trace_events") != null);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "provides_selftest_hook true") != null);
        }
        if (std.mem.eql(u8, check.id, "diagnostics-summary-surface")) {
            saw_summary_surface = true;
            try std.testing.expectEqualStrings("summary_contract", check.kind);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "RuntimeTraceEventsSummary") != null);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "explicit main-thread and function-thread event totals") != null);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "replay run counters") != null);
        }
        if (std.mem.eql(u8, check.id, "summary-run-counters")) {
            saw_summary_run_counters = true;
            try std.testing.expectEqualStrings("observability_contract", check.kind);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "init_runs") != null);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "selftest_runs") != null);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "exit_runs") != null);
        }
        if (std.mem.eql(u8, check.id, "main-thread-payload-surface")) {
            saw_main_payload_surface = true;
            try std.testing.expectEqualStrings("payload_contract", check.kind);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "foo_bar") != null);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "count % 5 array-shape details") != null);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "iter=%d") != null);
        }
        if (std.mem.eql(u8, check.id, "function-callback-balance")) {
            saw_function_balance = true;
            try std.testing.expectEqualStrings("registration_contract", check.kind);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "registration depth") != null);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "underflow protection") != null);
        }
        if (std.mem.eql(u8, check.id, "selftest-family-order")) {
            saw_selftest_family_order = true;
            try std.testing.expectEqualStrings("selftest_contract", check.kind);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "relative_location") != null);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "8 total-event") != null);
        }
        if (std.mem.eql(u8, check.id, "failed-exit-rollback")) {
            saw_failed_exit_rollback = true;
            try std.testing.expectEqualStrings("rollback_contract", check.kind);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "error.OutstandingRegistration") != null);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "initialized stage") != null);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "replay run counters") != null);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "explicit per-thread event totals") != null);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "payload literals intact") != null);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "selftest-to-exit path resumes") != null);
        }
        if (std.mem.eql(u8, check.id, "trace-header-boundary")) {
            saw_trace_header_boundary_check = true;
            try std.testing.expectEqualStrings("header_boundary", check.kind);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "trace-events-sample.h") != null);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "640-line surveyed boundary") != null);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "generated tracepoint macro parity") != null);
        }
        if (std.mem.eql(u8, check.id, "freeze-map-boundary")) {
            saw_freeze_map_boundary_check = true;
            try std.testing.expectEqualStrings("governance_surface", check.kind);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "Documentation/zigux/freeze-map.md") != null);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "Architecture Council") != null);
        }
        if (std.mem.eql(u8, check.id, "loader-free-blocker")) {
            saw_loader_free_blocker_check = true;
            try std.testing.expectEqualStrings("runtime_substrate_boundary", check.kind);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "runtime_trace_events_loader.zig") != null);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "bounded blocked scaffold") != null);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "phase9-runtime-trace-events-loader-tests is now present") != null);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "shared runtime-loader binding still stays absent") != null);
        }

        for (manifest.exact_checks[i + 1 ..]) |other| {
            try std.testing.expect(!std.mem.eql(u8, check.id, other.id));
        }
    }

    for (manifest.gaps, 0..) |gap, i| {
        try std.testing.expect(gap.id.len > 0);
        try std.testing.expect(gap.kind.len > 0);
        try std.testing.expect(gap.why_now.len > 0);
        try std.testing.expect(isAllowedStatus(gap.status));

        if (std.mem.startsWith(u8, gap.zigux_destination, "zigux/tests/")) {
            runtime_test_destination_count += 1;
        } else if (std.mem.startsWith(u8, gap.zigux_destination, "samples/zigux/")) {} else if (std.mem.startsWith(u8, gap.zigux_destination, "Documentation/zigux/")) {} else {
            try std.testing.expect(std.mem.startsWith(u8, gap.zigux_destination, "zigux/kernel/"));
        }

        if (std.mem.eql(u8, gap.status, "ready_next")) {
            ready_next_count += 1;
        } else if (std.mem.eql(u8, gap.status, "starter_landed")) {
            starter_landed_count += 1;
        } else if (std.mem.eql(u8, gap.status, "blocked_on_runtime_substrate")) {
            blocked_count += 1;
        }

        if (std.mem.eql(u8, gap.id, "runtime-trace-events-sample-module")) {
            saw_sample_module = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("samples/zigux/runtime_trace_events.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "selftest hook") != null);
        }
        if (std.mem.eql(u8, gap.id, "runtime-trace-events-loader-scaffold")) {
            saw_loader_scaffold_gap = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("samples/zigux/runtime_trace_events_loader.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "release-without-substrate fallback") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "shared-build replay") != null);
        }
        if (std.mem.eql(u8, gap.id, "runtime-trace-events-diff-gate")) {
            saw_diff_gate = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("zigux/tests/runtime_trace_events_diff.zig", gap.zigux_destination);
        }
        if (std.mem.eql(u8, gap.id, "runtime-trace-events-freeze-map-boundary")) {
            saw_freeze_map_boundary = true;
            try std.testing.expectEqualStrings("blocked_on_runtime_substrate", gap.status);
            try std.testing.expectEqualStrings("Documentation/zigux/phase9-runtime-trace-events-survey.md", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "`kernel/trace/ring_buffer.c`") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "parity scorecard") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "Architecture Council") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "status-change request") != null);
        }
        if (std.mem.eql(u8, gap.id, "runtime-trace-events-module-tests")) {
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "lifecycle parity") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "diagnostics-summary") != null);
        }
        if (std.mem.eql(u8, gap.id, "runtime-trace-events-substrate-handoff")) {
            try std.testing.expectEqualStrings("blocked_on_runtime_substrate", gap.status);
            try std.testing.expectEqualStrings("samples/zigux/runtime_trace_events_loader.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "bounded loader scaffold now exists") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "shared Phase 9 build packet") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "loadable module entry point") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "shared runtime-loader binding") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "runtime task ownership") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "polling and event-loop substrate") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "thread creation") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "tracepoint registration parity") != null);
        }

        for (manifest.gaps[i + 1 ..]) |other| {
            try std.testing.expect(!std.mem.eql(u8, gap.id, other.id));
            try std.testing.expect(!std.mem.eql(u8, gap.zigux_destination, other.zigux_destination));
        }
    }

    try std.testing.expect(runtime_test_destination_count >= 4);
    try std.testing.expect(starter_landed_count >= 6);
    try std.testing.expectEqual(@as(usize, 0), ready_next_count);
    try std.testing.expect(blocked_count >= 2);
    try std.testing.expect(saw_loader_free_prompt);
    try std.testing.expect(saw_header_boundary_prompt);
    try std.testing.expect(saw_ownership_prompt);
    try std.testing.expect(saw_freeze_map_prompt);
    try std.testing.expect(saw_manifest_catalog);
    try std.testing.expect(saw_loader_scaffold_catalog);
    try std.testing.expect(saw_module_slice_catalog);
    try std.testing.expect(saw_shared_build_catalog);
    try std.testing.expect(saw_freeze_map_catalog);
    try std.testing.expect(saw_loader_scaffold_ownership);
    try std.testing.expect(saw_module_slice_ownership);
    try std.testing.expect(saw_descriptor_contract);
    try std.testing.expect(saw_summary_surface);
    try std.testing.expect(saw_summary_run_counters);
    try std.testing.expect(saw_main_payload_surface);
    try std.testing.expect(saw_function_balance);
    try std.testing.expect(saw_selftest_family_order);
    try std.testing.expect(saw_failed_exit_rollback);
    try std.testing.expect(saw_trace_header_boundary_check);
    try std.testing.expect(saw_freeze_map_boundary_check);
    try std.testing.expect(saw_loader_free_blocker_check);
    try std.testing.expect(saw_sample_module);
    try std.testing.expect(saw_loader_scaffold_gap);
    try std.testing.expect(saw_diff_gate);
    try std.testing.expect(saw_freeze_map_boundary);
}

test "phase 9 runtime trace-events docs keep the task and event-loop substrate gap explicit" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const manifest_json = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/runtime_trace_events_manifest.json",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(manifest_json);

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{});
    defer parsed.deinit();

    const surveyed_commit = parsed.value.surveyed_commit;

    const freeze_map = try readWorkspaceFile(io_instance.io(), std.testing.allocator, "Documentation/zigux/freeze-map.md", 16 * 1024);
    defer std.testing.allocator.free(freeze_map);

    const survey_doc = try readWorkspaceFile(io_instance.io(), std.testing.allocator, "Documentation/zigux/phase9-runtime-trace-events-survey.md", 16 * 1024);
    defer std.testing.allocator.free(survey_doc);

    const module_doc = try readWorkspaceFile(io_instance.io(), std.testing.allocator, "Documentation/zigux/phase9-runtime-trace-events-module-slice.md", 16 * 1024);
    defer std.testing.allocator.free(module_doc);

    try std.testing.expect(std.mem.indexOf(u8, freeze_map, "## Study / Boundary Only") != null);
    try std.testing.expect(std.mem.indexOf(u8, freeze_map, "`kernel/trace/ring_buffer.c`") != null);

    try std.testing.expect(std.mem.indexOf(u8, survey_doc, "runtime task ownership") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_doc, "selftest hook") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_doc, "provides_selftest_hook = true") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_doc, "lifecycle parity") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_doc, "runtime_trace_events_diff.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_doc, "Delivery ownership map") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_doc, "manifest-backed delivery catalog") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_doc, "zigux/tests/runtime_trace_events_manifest.json") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_doc, "zigux/tests/phase9_build.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_doc, "Documentation/zigux/phase9-runtime-trace-events-module-slice.md") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_doc, "`PHASE9_LANE_KEY=P9-L12`") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_doc, "RuntimeTraceEventsSummary") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_doc, "explicit per-thread event totals") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_doc, "explicit main-thread and function-thread event totals") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_doc, "`init_runs`") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_doc, "`selftest_runs`") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_doc, "`exit_runs`") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_doc, "array-shape replay explicit") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_doc, "latest bounded main-thread and function-thread payload literals") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_doc, "zig test --dep runtime_trace_events_sample") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_doc, "-Mroot=zigux/tests/runtime_trace_events_survey.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_doc, "-Mruntime_trace_events_sample=samples/zigux/runtime_trace_events.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_doc, "make -C zigux phase9-trace-events-survey") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_doc, "zig build test --build-file zigux/tests/phase9_build.zig --summary all") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_doc, "phase9-runtime-trace-events-sample-tests") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_doc, "phase9-runtime-trace-events-module-tests") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_doc, "phase9-runtime-trace-events-diff-tests") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_doc, "phase9-runtime-trace-events-loader-tests") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_doc, "phase9-runtime-trace-events-survey-tests") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_doc, surveyed_commit) != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_doc, "`PHASE9_SURVEYED_COMMIT=") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_doc, "failed-exit rollback proof") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_doc, "runtime task ownership or event-loop substrate parity") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_doc, "polling and event-loop substrate") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_doc, "polling-backed wake or dispatch behavior") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_doc, "module entry") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_doc, "thread creation") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_doc, "tracepoint-registration lifecycle wiring") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_doc, "samples/zigux/runtime_trace_events_loader.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_doc, "shared Phase 9 build packet") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_doc, "shared runtime-loader binding") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_doc, "samples/trace_events/trace-events-sample.h") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_doc, "header-side macro boundary") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_doc, "640-line surveyed boundary") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_doc, "generated tracepoint macro parity") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_doc, "Documentation/zigux/freeze-map.md") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_doc, "`kernel/trace/ring_buffer.c`") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_doc, "Study / Boundary Only") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_doc, "ring-buffer parity") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_doc, "No parity scorecard entry or Architecture Council status-change request is attached to this Phase 9 lane.") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_doc, "study-boundary note rather than a freeze-map reopen request") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_doc, "Architecture Council") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_doc, "the current survey packet is pinned to `master` commit `") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_doc, "landed starter surface summary") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_doc, "blocked loader-scaffold restatement") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_doc, "paired header-side macro boundary note") != null);

    try std.testing.expect(std.mem.indexOf(u8, module_doc, "runtime task ownership") != null);
    try std.testing.expect(std.mem.indexOf(u8, module_doc, "`PHASE9_LANE_KEY=P9-L12`") != null);
    try std.testing.expect(std.mem.indexOf(u8, module_doc, "RuntimeTraceEventsSummary") != null);
    try std.testing.expect(std.mem.indexOf(u8, module_doc, "explicit main-thread and function-thread event totals") != null);
    try std.testing.expect(std.mem.indexOf(u8, module_doc, "`init_runs`") != null);
    try std.testing.expect(std.mem.indexOf(u8, module_doc, "`selftest_runs`") != null);
    try std.testing.expect(std.mem.indexOf(u8, module_doc, "`exit_runs`") != null);
    try std.testing.expect(std.mem.indexOf(u8, module_doc, "explicit per-thread event-total") != null);
    try std.testing.expect(std.mem.indexOf(u8, module_doc, "array-shape replay explicit") != null);
    try std.testing.expect(std.mem.indexOf(u8, module_doc, "latest bounded main-thread and function-thread payload literals") != null);
    try std.testing.expect(std.mem.indexOf(u8, module_doc, "phase9-runtime-trace-events-sample-tests") != null);
    try std.testing.expect(std.mem.indexOf(u8, module_doc, "phase9-runtime-trace-events-loader-tests") != null);
    try std.testing.expect(std.mem.indexOf(u8, module_doc, surveyed_commit) != null);
    try std.testing.expect(std.mem.indexOf(u8, module_doc, "`PHASE9_SURVEYED_COMMIT=") != null);
    try std.testing.expect(std.mem.indexOf(u8, module_doc, "failed-exit rollback proof") != null);
    try std.testing.expect(std.mem.indexOf(u8, module_doc, "runtime task ownership or event-loop substrate parity") != null);
    try std.testing.expect(std.mem.indexOf(u8, module_doc, "polling and event-loop substrate") != null);
    try std.testing.expect(std.mem.indexOf(u8, module_doc, "polling-backed wake or dispatch behavior") != null);
    try std.testing.expect(std.mem.indexOf(u8, module_doc, "real kernel thread scheduling or timeout behavior") != null);
    try std.testing.expect(std.mem.indexOf(u8, module_doc, "samples/zigux/runtime_trace_events_loader.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, module_doc, "shared runtime-loader binding or executable substrate handoff") != null);
    try std.testing.expect(std.mem.indexOf(u8, module_doc, "samples/trace_events/trace-events-sample.h") != null);
    try std.testing.expect(std.mem.indexOf(u8, module_doc, "header-side macro boundary") != null);
    try std.testing.expect(std.mem.indexOf(u8, module_doc, "640-line surveyed boundary") != null);
    try std.testing.expect(std.mem.indexOf(u8, module_doc, "generated tracepoint macro parity") != null);
    try std.testing.expect(std.mem.indexOf(u8, module_doc, "thread creation") != null);
    try std.testing.expect(std.mem.indexOf(u8, module_doc, "tracepoint-registration lifecycle wiring") != null);
    try std.testing.expect(std.mem.indexOf(u8, module_doc, "Documentation/zigux/freeze-map.md") != null);
    try std.testing.expect(std.mem.indexOf(u8, module_doc, "`kernel/trace/ring_buffer.c`") != null);
    try std.testing.expect(std.mem.indexOf(u8, module_doc, "Study / Boundary Only") != null);
    try std.testing.expect(std.mem.indexOf(u8, module_doc, "ring-buffer parity") != null);
    try std.testing.expect(std.mem.indexOf(u8, module_doc, "No parity scorecard entry or Architecture Council status-change request is attached to this Phase 9 lane.") != null);
    try std.testing.expect(std.mem.indexOf(u8, module_doc, "does not reopen the trace-core freeze posture") != null);
    try std.testing.expect(std.mem.indexOf(u8, module_doc, "Architecture Council") != null);
}

test "phase 9 runtime trace-events survey keeps the starter descriptor blocked on runtime substrate" {
    const descriptor = sample.RuntimeTraceEventsSample.descriptor();

    try std.testing.expectEqualStrings("runtime_trace_events", descriptor.name);
    try std.testing.expectEqualStrings("samples/trace_events/trace-events-sample.c", descriptor.anchor);
    try std.testing.expect(descriptor.requires_runtime_substrate);
    try std.testing.expect(descriptor.provides_selftest_hook);
}

test "phase 9 runtime trace-events blocker keeps the shared build replay honest while the scaffold stays blocked" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const loader_file = try readWorkspaceFile(io_instance.io(), std.testing.allocator, "samples/zigux/runtime_trace_events_loader.zig", 32 * 1024);
    defer std.testing.allocator.free(loader_file);

    const phase9_build = try readWorkspaceFile(io_instance.io(), std.testing.allocator, "zigux/tests/phase9_build.zig", 32 * 1024);
    defer std.testing.allocator.free(phase9_build);

    try std.testing.expect(std.mem.indexOf(u8, loader_file, "pub const RuntimeTraceEventsLoader = struct") != null);
    try std.testing.expect(std.mem.indexOf(u8, loader_file, "pub fn requestRuntimeLoad") != null);
    try std.testing.expect(std.mem.indexOf(u8, loader_file, "pub fn releaseWithoutSubstrate") != null);
    try std.testing.expect(std.mem.indexOf(u8, loader_file, "foo_bar_reg") != null);
    try std.testing.expect(std.mem.indexOf(u8, loader_file, "foo_bar_unreg") != null);
    try std.testing.expect(std.mem.indexOf(u8, loader_file, "command_name: ?[]const u8") != null);
    try std.testing.expect(std.mem.indexOf(u8, loader_file, "pub fn withCommandName") != null);
    try std.testing.expect(std.mem.indexOf(u8, loader_file, "pub fn prepareWithCommandName") != null);
    try std.testing.expect(std.mem.indexOf(u8, loader_file, "error.InvalidCommandName") != null);
    try std.testing.expect(std.mem.indexOf(u8, loader_file, "\"perf-runtime-trace-events\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, phase9_build, "runtime_trace_events_loader") != null);
    try std.testing.expect(std.mem.indexOf(u8, phase9_build, "phase9-runtime-trace-events-loader-tests") != null);
    try std.testing.expect(std.mem.indexOf(u8, phase9_build, "phase9-runtime-loader-tests") != null);
    try std.testing.expect(std.mem.indexOf(u8, phase9_build, "phase9-runtime-loader-gap-survey-tests") != null);
    try std.testing.expect(std.mem.indexOf(u8, phase9_build, "phase9-runtime-trace-events-module-tests") != null);
    try std.testing.expect(std.mem.indexOf(u8, phase9_build, "phase9-runtime-trace-events-sample-tests") != null);
    try std.testing.expect(std.mem.indexOf(u8, phase9_build, "phase9-runtime-trace-events-diff-tests") != null);
    try std.testing.expect(std.mem.indexOf(u8, phase9_build, "phase9-runtime-trace-events-survey-tests") != null);
}
