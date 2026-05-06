const std = @import("std");

const SurveySummary = struct {
    trace_events_sample_c_lines: usize,
    preexisting_runtime_trace_events_test_files: usize,
    preexisting_runtime_trace_events_sample_present: bool,
    preexisting_phase9_build_present: bool,
    preexisting_runtime_trace_events_doc_present: bool,
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
    why_now: []const u8,
};

const OwnershipEntry = struct {
    surface: []const u8,
    role: []const u8,
    owner: []const u8,
    boundary: []const u8,
};

const Manifest = struct {
    lane_key: []const u8,
    phase: []const u8,
    surveyed_commit: []const u8,
    anchor: []const u8,
    roadmap_destinations: []const []const u8,
    survey_summary: SurveySummary,
    delivery_evidence_catalog: []const DeliveryEvidence,
    ownership_map: []const OwnershipEntry,
    gaps: []const Gap,
};

fn isAllowedStatus(status: []const u8) bool {
    return std.mem.eql(u8, status, "starter_landed") or
        std.mem.eql(u8, status, "ready_next") or
        std.mem.eql(u8, status, "blocked_on_runtime_substrate");
}

fn isAllowedDeliveryKind(kind: []const u8) bool {
    return std.mem.eql(u8, kind, "review_note") or
        std.mem.eql(u8, kind, "validation");
}

fn allowsSharedDestination(first_id: []const u8, second_id: []const u8) bool {
    return (std.mem.eql(u8, first_id, "runtime-trace-events-sample-module") and
        std.mem.eql(u8, second_id, "runtime-trace-events-selftest-hook")) or
        (std.mem.eql(u8, first_id, "runtime-trace-events-selftest-hook") and
            std.mem.eql(u8, second_id, "runtime-trace-events-sample-module"));
}

test "phase 9 runtime trace-events survey manifest records the landed loader scaffold and remaining blocker" {
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
    try std.testing.expectEqualStrings("P9-L12", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 9", manifest.phase);
    try std.testing.expectEqualStrings("samples/trace_events/trace-events-sample.c", manifest.anchor);
    try std.testing.expectEqual(@as(usize, 2), manifest.roadmap_destinations.len);
    try std.testing.expect(manifest.survey_summary.trace_events_sample_c_lines >= 150);
    try std.testing.expectEqual(@as(usize, 3), manifest.survey_summary.preexisting_runtime_trace_events_test_files);
    try std.testing.expect(manifest.survey_summary.preexisting_runtime_trace_events_sample_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase9_build_present);
    try std.testing.expect(manifest.survey_summary.preexisting_runtime_trace_events_doc_present);
    try std.testing.expect(manifest.delivery_evidence_catalog.len >= 4);
    try std.testing.expect(manifest.ownership_map.len >= 6);
    try std.testing.expect(manifest.gaps.len >= 8);

    var review_note_catalog_count: usize = 0;
    var validation_catalog_count: usize = 0;
    var saw_survey_note_catalog = false;
    var saw_module_slice_catalog = false;
    var saw_survey_gate_catalog = false;
    var saw_build_gate_catalog = false;

    for (manifest.delivery_evidence_catalog, 0..) |entry, i| {
        try std.testing.expect(entry.id.len > 0);
        try std.testing.expect(entry.path.len > 0);
        try std.testing.expect(entry.why_now.len > 0);
        try std.testing.expect(isAllowedDeliveryKind(entry.kind));

        if (std.mem.eql(u8, entry.kind, "review_note")) {
            review_note_catalog_count += 1;
        } else if (std.mem.eql(u8, entry.kind, "validation")) {
            validation_catalog_count += 1;
        }

        if (std.mem.eql(u8, entry.id, "trace-events-survey-note")) {
            saw_survey_note_catalog = true;
            try std.testing.expectEqualStrings("Documentation/zigux/phase9-runtime-trace-events-survey.md", entry.path);
        }
        if (std.mem.eql(u8, entry.id, "trace-events-module-slice-note")) {
            saw_module_slice_catalog = true;
            try std.testing.expectEqualStrings("Documentation/zigux/phase9-runtime-trace-events-module-slice.md", entry.path);
        }
        if (std.mem.eql(u8, entry.id, "trace-events-survey-gate")) {
            saw_survey_gate_catalog = true;
            try std.testing.expectEqualStrings("zigux/tests/runtime_trace_events_survey.zig", entry.path);
        }
        if (std.mem.eql(u8, entry.id, "trace-events-shared-build-gate")) {
            saw_build_gate_catalog = true;
            try std.testing.expectEqualStrings("zigux/tests/phase9_build.zig", entry.path);
        }

        for (manifest.delivery_evidence_catalog[i + 1 ..]) |other| {
            try std.testing.expect(!std.mem.eql(u8, entry.id, other.id));
            try std.testing.expect(!std.mem.eql(u8, entry.path, other.path));
        }
    }

    try std.testing.expectEqual(@as(usize, 2), review_note_catalog_count);
    try std.testing.expectEqual(@as(usize, 2), validation_catalog_count);
    try std.testing.expect(saw_survey_note_catalog);
    try std.testing.expect(saw_module_slice_catalog);
    try std.testing.expect(saw_survey_gate_catalog);
    try std.testing.expect(saw_build_gate_catalog);

    var saw_survey_note_owner = false;
    var saw_module_slice_owner = false;
    var saw_sample_owner = false;
    var saw_loader_owner = false;
    var saw_survey_gate_owner = false;
    var saw_build_gate_owner = false;

    for (manifest.ownership_map, 0..) |entry, i| {
        try std.testing.expect(entry.surface.len > 0);
        try std.testing.expect(entry.role.len > 0);
        try std.testing.expect(entry.boundary.len > 0);
        try std.testing.expectEqualStrings("P9-L12", entry.owner);

        if (std.mem.eql(u8, entry.surface, "Documentation/zigux/phase9-runtime-trace-events-survey.md")) saw_survey_note_owner = true;
        if (std.mem.eql(u8, entry.surface, "Documentation/zigux/phase9-runtime-trace-events-module-slice.md")) saw_module_slice_owner = true;
        if (std.mem.eql(u8, entry.surface, "samples/zigux/runtime_trace_events.zig")) saw_sample_owner = true;
        if (std.mem.eql(u8, entry.surface, "samples/zigux/runtime_trace_events_loader.zig")) saw_loader_owner = true;
        if (std.mem.eql(u8, entry.surface, "zigux/tests/runtime_trace_events_survey.zig")) saw_survey_gate_owner = true;
        if (std.mem.eql(u8, entry.surface, "zigux/tests/phase9_build.zig")) saw_build_gate_owner = true;

        for (manifest.ownership_map[i + 1 ..]) |other| {
            try std.testing.expect(!std.mem.eql(u8, entry.surface, other.surface));
        }
    }

    try std.testing.expect(saw_survey_note_owner);
    try std.testing.expect(saw_module_slice_owner);
    try std.testing.expect(saw_sample_owner);
    try std.testing.expect(saw_loader_owner);
    try std.testing.expect(saw_survey_gate_owner);
    try std.testing.expect(saw_build_gate_owner);

    var runtime_test_destination_count: usize = 0;
    var starter_landed_count: usize = 0;
    var ready_next_count: usize = 0;
    var blocked_count: usize = 0;
    var saw_sample_module = false;
    var saw_selftest_hook = false;
    var saw_diff_gate = false;
    var saw_loader_scaffold = false;
    var saw_live_loader_blocker = false;

    for (manifest.gaps, 0..) |gap, i| {
        try std.testing.expect(gap.id.len > 0);
        try std.testing.expect(gap.kind.len > 0);
        try std.testing.expect(gap.why_now.len > 0);
        try std.testing.expect(isAllowedStatus(gap.status));

        if (std.mem.startsWith(u8, gap.zigux_destination, "zigux/tests/")) {
            runtime_test_destination_count += 1;
        } else if (std.mem.startsWith(u8, gap.zigux_destination, "samples/zigux/")) {
            // Sample-side starter and loader scaffolds stay under samples.
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

        if (std.mem.eql(u8, gap.id, "runtime-trace-events-sample-module")) {
            saw_sample_module = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("samples/zigux/runtime_trace_events.zig", gap.zigux_destination);
        }
        if (std.mem.eql(u8, gap.id, "runtime-trace-events-selftest-hook")) {
            saw_selftest_hook = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("samples/zigux/runtime_trace_events.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "selftest hooks") != null);
        }
        if (std.mem.eql(u8, gap.id, "runtime-trace-events-diff-gate")) {
            saw_diff_gate = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("zigux/tests/runtime_trace_events_diff.zig", gap.zigux_destination);
        }
        if (std.mem.eql(u8, gap.id, "runtime-trace-events-loader-scaffold")) {
            saw_loader_scaffold = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("samples/zigux/runtime_trace_events_loader.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "tracepoint register and unregister APIs") != null);
        }
        if (std.mem.eql(u8, gap.id, "runtime-trace-events-substrate-handoff")) {
            saw_live_loader_blocker = true;
            try std.testing.expectEqualStrings("blocked_on_runtime_substrate", gap.status);
            try std.testing.expectEqualStrings("zigux/kernel/runtime_loader.zig", gap.zigux_destination);
        }

        for (manifest.gaps[i + 1 ..]) |other| {
            try std.testing.expect(!std.mem.eql(u8, gap.id, other.id));
            if (!allowsSharedDestination(gap.id, other.id)) {
                try std.testing.expect(!std.mem.eql(u8, gap.zigux_destination, other.zigux_destination));
            }
        }
    }

    try std.testing.expect(runtime_test_destination_count >= 4);
    try std.testing.expect(starter_landed_count >= 7);
    try std.testing.expectEqual(@as(usize, 0), ready_next_count);
    try std.testing.expect(blocked_count >= 1);
    try std.testing.expect(saw_sample_module);
    try std.testing.expect(saw_selftest_hook);
    try std.testing.expect(saw_diff_gate);
    try std.testing.expect(saw_loader_scaffold);
    try std.testing.expect(saw_live_loader_blocker);
}

test "phase 9 runtime trace-events survey keeps the manifest-backed surveyed commit and loader boundary explicit" {
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

    const surveyed_commit_marker = try std.fmt.allocPrint(
        std.testing.allocator,
        "`PHASE9_SURVEYED_COMMIT={s}`",
        .{parsed.value.surveyed_commit},
    );
    defer std.testing.allocator.free(surveyed_commit_marker);

    const survey_note = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase9-runtime-trace-events-survey.md",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(survey_note);

    const module_slice = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase9-runtime-trace-events-module-slice.md",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(module_slice);

    const freeze_map = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/freeze-map.md",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(freeze_map);

    const loader_source = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "samples/zigux/runtime_trace_events_loader.zig",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(loader_source);

    const sample_source = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "samples/zigux/runtime_trace_events.zig",
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

    try std.testing.expectEqual(@as(usize, 1), std.mem.count(u8, survey_note, surveyed_commit_marker));
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "shared `zigux/tests/phase9_build.zig` coverage for the trace-events starter lane") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "the current loader scaffold now records explicit tracepoint register and unregister API names") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "release-without-substrate behavior rather than executable runtime registration parity") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "the live repo now also carries `zigux/kernel/runtime_loader.zig` as the shared request surface for the bounded Phase 9 loader-handoff packet") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "the live repo also carries `zigux/kernel/runtime_loader_contract.zig`, `zigux/tests/runtime_loader_allocator_init_flow.zig`, and the focused `phase9-runtime-loader-shared-tests` build step") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "zig build phase9-runtime-loader-shared-tests --build-file zigux/tests/phase9_build.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "the trace-events starter still stops before a real module-loading substrate or live tracepoint registration lifecycle") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "the current bounded starter still advertises `requires_runtime_substrate=true` and `provides_selftest_hook=true`") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "runtime task ownership or event-loop substrate parity remains blocked behind that same shared runtime-loader boundary") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "polling-backed wake or dispatch behavior also remains blocked until the shared runtime substrate exists") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "the manifest-backed ownership packet now records a four-entry `delivery_evidence_catalog` and a six-surface `ownership_map`") != null);

    try std.testing.expectEqual(@as(usize, 1), std.mem.count(u8, module_slice, surveyed_commit_marker));
    try std.testing.expect(std.mem.indexOf(u8, module_slice, "a loader-handoff scaffold") != null);
    try std.testing.expect(std.mem.indexOf(u8, module_slice, "samples/zigux/runtime_trace_events_loader.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, module_slice, "zigux/tests/runtime_trace_events_survey.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, module_slice, "zigux/tests/phase9_build.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, module_slice, "shared runtime-loader facade plus allocator/init-flow contract replay") != null);
    try std.testing.expect(std.mem.indexOf(u8, module_slice, "zig build phase9-runtime-loader-shared-tests --build-file zigux/tests/phase9_build.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, module_slice, "shared runtime loader substrate can consume the bounded loader-handoff plan") != null);
    try std.testing.expect(std.mem.indexOf(u8, module_slice, "keeping the roadmap-required selftest hook explicit through `provides_selftest_hook=true`") != null);
    try std.testing.expect(std.mem.indexOf(u8, module_slice, "runtime task ownership or event-loop substrate parity remains blocked behind that shared runtime-loader surface") != null);
    try std.testing.expect(std.mem.indexOf(u8, module_slice, "polling-backed wake or dispatch behavior remains blocked behind the same shared runtime-loader surface") != null);

    try std.testing.expect(std.mem.indexOf(u8, freeze_map, "`kernel/workqueue.c`") != null);
    try std.testing.expect(std.mem.indexOf(u8, freeze_map, "`kernel/trace/ring_buffer.c`") != null);
    try std.testing.expect(std.mem.indexOf(u8, freeze_map, "the shared Phase 9 runtime-loader packet stays review-only beside `kernel/workqueue.c` and `kernel/trace/ring_buffer.c`") != null);
    try std.testing.expect(std.mem.indexOf(u8, freeze_map, "the four `samples/zigux/runtime_*_loader.zig` scaffolds keep the bounded loader handoff explicit without implying scheduler-facing substrate closure or a freeze-map status change") != null);

    try std.testing.expect(std.mem.indexOf(u8, loader_source, ".entry_symbol = \"zigux_runtime_trace_events_init\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, loader_source, ".exit_symbol = \"zigux_runtime_trace_events_exit\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, loader_source, ".register_api = \"tracepoint_probe_register\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, loader_source, ".unregister_api = \"tracepoint_probe_unregister\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, loader_source, "self.stage_state = .waiting_on_runtime_substrate;") != null);
    try std.testing.expect(std.mem.indexOf(u8, loader_source, "self.stage_state = .released_without_substrate;") != null);
    try std.testing.expect(std.mem.indexOf(u8, loader_source, "test \"runtime trace-events loader keeps the prepared snapshot stable across later sample mutation\"") != null);

    try std.testing.expect(std.mem.indexOf(u8, sample_source, ".provides_selftest_hook = true") != null);
    try std.testing.expect(std.mem.indexOf(u8, sample_source, "pub fn runSelftest(self: *Self) !EmissionSummary") != null);

    try std.testing.expect(std.mem.indexOf(u8, phase9_build, "runtime_trace_events_loader_module") != null);
    try std.testing.expect(std.mem.indexOf(u8, phase9_build, "phase9-runtime-trace-events-loader-tests") != null);
    try std.testing.expect(std.mem.indexOf(u8, phase9_build, "run_runtime_trace_events_loader_tests.step") != null);
    try std.testing.expect(std.mem.indexOf(u8, phase9_build, "runtime_loader_contract_module") != null);
    try std.testing.expect(std.mem.indexOf(u8, phase9_build, "runtime_loader_facade_module") != null);
    try std.testing.expect(std.mem.indexOf(u8, phase9_build, "runtime_loader_allocator_init_flow_module") != null);
    try std.testing.expect(std.mem.indexOf(u8, phase9_build, "phase9-runtime-loader-shared-tests") != null);
    try std.testing.expect(std.mem.indexOf(u8, phase9_build, "run_runtime_loader_contract_tests.step") != null);
    try std.testing.expect(std.mem.indexOf(u8, phase9_build, "run_runtime_loader_facade_tests.step") != null);
    try std.testing.expect(std.mem.indexOf(u8, phase9_build, "run_runtime_loader_allocator_init_flow_tests.step") != null);
}
