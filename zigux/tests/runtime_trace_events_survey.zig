const std = @import("std");

const SurveySummary = struct {
    trace_events_sample_c_lines: usize,
    preexisting_runtime_trace_events_test_files: usize,
    preexisting_runtime_trace_events_sample_present: bool,
    preexisting_runtime_trace_events_loader_present: bool,
    preexisting_phase9_build_present: bool,
    preexisting_runtime_trace_events_doc_present: bool,
    preexisting_runtime_trace_events_manifest_present: bool,
};

const LifecycleBoundarySummary = struct {
    family_local_trace_events_packet_present: bool,
    shared_loader_packet_present: bool,
    shared_request_surface: []const u8,
    family_local_registration_parity: []const u8,
    live_registration_parity: []const u8,
};

const RoadmapGapSummary = struct {
    roadmap_phase_goal: []const u8,
    landed_pilot_state: []const u8,
    missing_capability: []const u8,
    blocked_deliverable: []const u8,
    next_gate: []const u8,
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

const Gap = struct {
    id: []const u8,
    status: []const u8,
    kind: []const u8,
    zigux_destination: []const u8,
    why_now: []const u8,
};

const Manifest = struct {
    lane_key: []const u8,
    phase: []const u8,
    surveyed_commit: []const u8,
    anchor: []const u8,
    roadmap_destinations: []const []const u8,
    survey_summary: SurveySummary,
    lifecycle_boundary_summary: LifecycleBoundarySummary,
    roadmap_gap_summary: RoadmapGapSummary,
    delivery_evidence_catalog: []const DeliveryEvidence,
    ownership_map: []const OwnershipEntry,
    gaps: []const Gap,
};

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectSurveyedCommitMarker(note: []const u8, surveyed_commit: []const u8) !void {
    var marker_buffer: [64]u8 = undefined;
    const marker = try std.fmt.bufPrint(&marker_buffer, "PHASE9_SURVEYED_COMMIT={s}", .{surveyed_commit});
    try expectContains(note, marker);
}

fn isAllowedDeliveryKind(kind: []const u8) bool {
    return std.mem.eql(u8, kind, "sample_starter") or
        std.mem.eql(u8, kind, "runtime_loader_scaffold") or
        std.mem.eql(u8, kind, "validation") or
        std.mem.eql(u8, kind, "differential_validation") or
        std.mem.eql(u8, kind, "review_note");
}

fn isAllowedOwnerRole(role: []const u8) bool {
    return std.mem.eql(u8, role, "packet_truth_manifest") or
        std.mem.eql(u8, role, "survey_note") or
        std.mem.eql(u8, role, "module_slice_note") or
        std.mem.eql(u8, role, "shared_owner_map") or
        std.mem.eql(u8, role, "shared_build_bundle");
}

test "phase 9 runtime trace-events survey packet matches the current manifest and notes" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const cwd = std.Io.Dir.cwd();
    const manifest_json = try cwd.readFileAlloc(
        io_instance.io(),
        "zigux/tests/runtime_trace_events_manifest.json",
        std.testing.allocator,
        .limited(64 * 1024),
    );
    defer std.testing.allocator.free(manifest_json);

    const survey_note = try cwd.readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase9-runtime-trace-events-survey.md",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(survey_note);

    const module_slice_note = try cwd.readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase9-runtime-trace-events-module-slice.md",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(module_slice_note);

    const runtime_trace_events_module = try cwd.readFileAlloc(
        io_instance.io(),
        "zigux/tests/runtime_trace_events_module.zig",
        std.testing.allocator,
        .limited(64 * 1024),
    );
    defer std.testing.allocator.free(runtime_trace_events_module);

    const runtime_trace_events_loader = try cwd.readFileAlloc(
        io_instance.io(),
        "samples/zigux/runtime_trace_events_loader.zig",
        std.testing.allocator,
        .limited(96 * 1024),
    );
    defer std.testing.allocator.free(runtime_trace_events_loader);

    const phase9_build = try cwd.readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase9_build.zig",
        std.testing.allocator,
        .limited(64 * 1024),
    );
    defer std.testing.allocator.free(phase9_build);

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{});
    defer parsed.deinit();
    const manifest = parsed.value;

    try std.testing.expectEqualStrings("P9-L10", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 9", manifest.phase);
    try std.testing.expect(manifest.surveyed_commit.len == 40);
    try expectSurveyedCommitMarker(survey_note, manifest.surveyed_commit);
    try expectSurveyedCommitMarker(module_slice_note, manifest.surveyed_commit);
    try std.testing.expectEqualStrings("samples/trace_events/trace-events-sample.c", manifest.anchor);
    try std.testing.expectEqual(@as(usize, 2), manifest.roadmap_destinations.len);
    try std.testing.expectEqualStrings("zigux/tests/runtime_*", manifest.roadmap_destinations[0]);
    try std.testing.expectEqualStrings("samples/zigux/runtime_*", manifest.roadmap_destinations[1]);

    try std.testing.expect(manifest.survey_summary.trace_events_sample_c_lines >= 150);
    try std.testing.expectEqual(@as(usize, 3), manifest.survey_summary.preexisting_runtime_trace_events_test_files);
    try std.testing.expect(manifest.survey_summary.preexisting_runtime_trace_events_sample_present);
    try std.testing.expect(manifest.survey_summary.preexisting_runtime_trace_events_loader_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase9_build_present);
    try std.testing.expect(manifest.survey_summary.preexisting_runtime_trace_events_doc_present);
    try std.testing.expect(manifest.survey_summary.preexisting_runtime_trace_events_manifest_present);

    try std.testing.expect(manifest.lifecycle_boundary_summary.family_local_trace_events_packet_present);
    try std.testing.expect(manifest.lifecycle_boundary_summary.shared_loader_packet_present);
    try std.testing.expectEqualStrings("zigux/kernel/runtime_loader.zig", manifest.lifecycle_boundary_summary.shared_request_surface);
    try std.testing.expectEqualStrings("reviewable_on_current_master", manifest.lifecycle_boundary_summary.family_local_registration_parity);
    try std.testing.expectEqualStrings("blocked_on_runtime_substrate", manifest.lifecycle_boundary_summary.live_registration_parity);

    try std.testing.expectEqualStrings(
        "first loadable Zigux runtime modules with selftest hooks and runtime module lifecycle parity",
        manifest.roadmap_gap_summary.roadmap_phase_goal,
    );
    try std.testing.expectEqualStrings(
        "family_local_trace_events_review_packet_plus_shared_loader_handoff",
        manifest.roadmap_gap_summary.landed_pilot_state,
    );
    try std.testing.expectEqualStrings(
        "the broader shared runtime substrate that would turn the current reviewable trace-events sample, loader, diff, module, and survey packet into live runtime tracepoint-registration lifecycle parity",
        manifest.roadmap_gap_summary.missing_capability,
    );
    try std.testing.expectEqualStrings(
        "completed live Phase 9 runtime tracepoint registration lifecycle parity beyond the current review packet",
        manifest.roadmap_gap_summary.blocked_deliverable,
    );
    try std.testing.expectEqualStrings(
        "keep the trace-events survey note, module-slice note, and manifest aligned with the visible family-local packet while leaving the shared runtime-substrate blocker explicit",
        manifest.roadmap_gap_summary.next_gate,
    );

    try std.testing.expectEqual(@as(usize, 10), manifest.delivery_evidence_catalog.len);
    try std.testing.expectEqual(@as(usize, 5), manifest.ownership_map.len);
    try std.testing.expectEqual(@as(usize, 1), manifest.gaps.len);

    var saw_sample = false;
    var saw_loader = false;
    var saw_module = false;
    var saw_diff = false;
    var saw_survey = false;
    var saw_manifest = false;
    var saw_survey_note = false;
    var saw_module_slice = false;
    var saw_owner_map = false;
    var saw_build_boundary = false;

    for (manifest.delivery_evidence_catalog, 0..) |entry, i| {
        try std.testing.expect(entry.id.len > 0);
        try std.testing.expect(entry.path.len > 0);
        try std.testing.expect(entry.why_now.len > 0);
        try std.testing.expect(isAllowedDeliveryKind(entry.kind));
        for (manifest.delivery_evidence_catalog[i + 1 ..]) |other| {
            try std.testing.expect(!std.mem.eql(u8, entry.id, other.id));
            try std.testing.expect(!std.mem.eql(u8, entry.path, other.path));
        }

        if (std.mem.eql(u8, entry.id, "trace-events-sample")) {
            saw_sample = true;
            try std.testing.expectEqualStrings("sample_starter", entry.kind);
            try std.testing.expectEqualStrings("samples/zigux/runtime_trace_events.zig", entry.path);
        } else if (std.mem.eql(u8, entry.id, "trace-events-loader-scaffold")) {
            saw_loader = true;
            try std.testing.expectEqualStrings("runtime_loader_scaffold", entry.kind);
            try std.testing.expectEqualStrings("samples/zigux/runtime_trace_events_loader.zig", entry.path);
        } else if (std.mem.eql(u8, entry.id, "trace-events-module-gate")) {
            saw_module = true;
            try std.testing.expectEqualStrings("validation", entry.kind);
            try std.testing.expectEqualStrings("zigux/tests/runtime_trace_events_module.zig", entry.path);
        } else if (std.mem.eql(u8, entry.id, "trace-events-diff-gate")) {
            saw_diff = true;
            try std.testing.expectEqualStrings("differential_validation", entry.kind);
            try std.testing.expectEqualStrings("zigux/tests/runtime_trace_events_diff.zig", entry.path);
        } else if (std.mem.eql(u8, entry.id, "trace-events-survey-gate")) {
            saw_survey = true;
            try std.testing.expectEqualStrings("validation", entry.kind);
            try std.testing.expectEqualStrings("zigux/tests/runtime_trace_events_survey.zig", entry.path);
        } else if (std.mem.eql(u8, entry.id, "trace-events-manifest")) {
            saw_manifest = true;
            try std.testing.expectEqualStrings("review_note", entry.kind);
            try std.testing.expectEqualStrings("zigux/tests/runtime_trace_events_manifest.json", entry.path);
        } else if (std.mem.eql(u8, entry.id, "trace-events-survey-note")) {
            saw_survey_note = true;
            try std.testing.expectEqualStrings("review_note", entry.kind);
            try std.testing.expectEqualStrings("Documentation/zigux/phase9-runtime-trace-events-survey.md", entry.path);
        } else if (std.mem.eql(u8, entry.id, "trace-events-module-slice-note")) {
            saw_module_slice = true;
            try std.testing.expectEqualStrings("review_note", entry.kind);
            try std.testing.expectEqualStrings("Documentation/zigux/phase9-runtime-trace-events-module-slice.md", entry.path);
        } else if (std.mem.eql(u8, entry.id, "trace-events-shared-owner-map")) {
            saw_owner_map = true;
            try std.testing.expectEqualStrings("review_note", entry.kind);
            try std.testing.expectEqualStrings("Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md", entry.path);
        } else if (std.mem.eql(u8, entry.id, "trace-events-shared-build-boundary")) {
            saw_build_boundary = true;
            try std.testing.expectEqualStrings("validation", entry.kind);
            try std.testing.expectEqualStrings("zigux/tests/phase9_build.zig", entry.path);
        }
    }

    try std.testing.expect(saw_sample);
    try std.testing.expect(saw_loader);
    try std.testing.expect(saw_module);
    try std.testing.expect(saw_diff);
    try std.testing.expect(saw_survey);
    try std.testing.expect(saw_manifest);
    try std.testing.expect(saw_survey_note);
    try std.testing.expect(saw_module_slice);
    try std.testing.expect(saw_owner_map);
    try std.testing.expect(saw_build_boundary);

    var saw_manifest_owner = false;
    var saw_survey_note_owner = false;
    var saw_module_slice_owner = false;
    var saw_shared_owner_map = false;
    var saw_shared_build_bundle = false;
    for (manifest.ownership_map, 0..) |entry, i| {
        try std.testing.expect(entry.surface.len > 0);
        try std.testing.expect(entry.boundary.len > 0);
        try std.testing.expect(isAllowedOwnerRole(entry.role));
        for (manifest.ownership_map[i + 1 ..]) |other| {
            try std.testing.expect(!std.mem.eql(u8, entry.surface, other.surface));
        }

        if (std.mem.eql(u8, entry.surface, "zigux/tests/runtime_trace_events_manifest.json")) {
            saw_manifest_owner = true;
            try std.testing.expectEqualStrings("packet_truth_manifest", entry.role);
            try std.testing.expectEqualStrings("P9-L10", entry.owner);
        } else if (std.mem.eql(u8, entry.surface, "Documentation/zigux/phase9-runtime-trace-events-survey.md")) {
            saw_survey_note_owner = true;
            try std.testing.expectEqualStrings("survey_note", entry.role);
            try std.testing.expectEqualStrings("P9-L10", entry.owner);
        } else if (std.mem.eql(u8, entry.surface, "Documentation/zigux/phase9-runtime-trace-events-module-slice.md")) {
            saw_module_slice_owner = true;
            try std.testing.expectEqualStrings("module_slice_note", entry.role);
            try std.testing.expectEqualStrings("P9-L10", entry.owner);
        } else if (std.mem.eql(u8, entry.surface, "Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md")) {
            saw_shared_owner_map = true;
            try std.testing.expectEqualStrings("shared_owner_map", entry.role);
            try std.testing.expectEqualStrings("P9-L11", entry.owner);
        } else if (std.mem.eql(u8, entry.surface, "zigux/tests/phase9_build.zig")) {
            saw_shared_build_bundle = true;
            try std.testing.expectEqualStrings("shared_build_bundle", entry.role);
            try std.testing.expectEqualStrings("P9-L11", entry.owner);
            try expectContains(entry.boundary, "`phase9-runtime-trace-events-tests`");
            try expectContains(entry.boundary, "Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md");
            try expectContains(entry.boundary, "zigux/Makefile");
        }
    }

    try std.testing.expect(saw_manifest_owner);
    try std.testing.expect(saw_survey_note_owner);
    try std.testing.expect(saw_module_slice_owner);
    try std.testing.expect(saw_shared_owner_map);
    try std.testing.expect(saw_shared_build_bundle);

    try std.testing.expectEqualStrings("runtime-trace-events-substrate-handoff", manifest.gaps[0].id);
    try std.testing.expectEqualStrings("blocked_on_runtime_substrate", manifest.gaps[0].status);
    try std.testing.expectEqualStrings("runtime_substrate", manifest.gaps[0].kind);
    try std.testing.expectEqualStrings("zigux/kernel/runtime_loader.zig", manifest.gaps[0].zigux_destination);
    try std.testing.expectEqualStrings(
        "The roadmap's loadable runtime pilot module step still depends on a shared runtime substrate beyond the current reviewable family-local trace-events packet, including runtime task ownership, polling and event-loop substrate, polling-backed wake or dispatch behavior, and the still-blocked `.modinfo`, `MODULE_ALIAS()`, `modules.alias`, `modules.order`, `modules.builtin`, module install-root publication, and `depmod` script or manifest state boundary.",
        manifest.gaps[0].why_now,
    );

    try expectContains(survey_note, "reviewable family-local starter plus the adjacent shared loader-facing reminder packet");
    try expectContains(
        survey_note,
        "The directly coupled module-slice note already keeps `Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md` and `zigux/Makefile` explicit as adjacent reminder surfaces.",
    );
    try expectContains(
        survey_note,
        "the trace-events family owns only the focused `phase9-runtime-trace-events-tests` step in `zigux/tests/phase9_build.zig`",
    );
    try expectContains(survey_note, "The remaining blocker is the broader Phase 9 runtime substrate.");
    try expectContains(
        survey_note,
        "runtime task ownership, polling and event-loop substrate, and polling-backed wake or dispatch behavior",
    );
    try expectContains(
        survey_note,
        "That still-blocked boundary also includes `.modinfo`, `MODULE_ALIAS()`, `modules.alias`, `modules.order`, `modules.builtin`, module install-root publication, and `depmod` script or manifest state.",
    );
    try expectContains(
        survey_note,
        "Those alias and depmod surfaces remain review-only metadata boundaries rather than shipped trace-events-family evidence.",
    );
    try expectContains(survey_note, "Do not invent a dedicated `validate-phase9.py` route");
    try expectContains(module_slice_note, "the broader runtime-substrate handoff remains a separate blocked step");
    try expectContains(module_slice_note, "the live runtime substrate is still missing");
    try expectContains(
        module_slice_note,
        "runtime task ownership, polling and event-loop substrate, and polling-backed wake or dispatch behavior",
    );
    try expectContains(
        module_slice_note,
        "`.modinfo`, `MODULE_ALIAS()`, `modules.alias`, `modules.order`, `modules.builtin`, module install-root publication, and any `depmod` script or manifest state",
    );
    try expectContains(
        module_slice_note,
        "those alias and depmod surfaces remain review-only metadata boundaries rather than shipped trace-events-family evidence.",
    );
    try expectContains(module_slice_note, "Do not invent `validate-phase9.py`, a trace-events-only validator, or a cleared runtime-substrate handoff.");
    try expectContains(
        runtime_trace_events_module,
        "test \"runtime trace-events sample keeps replay-summary continuity explicit after selftest completion\" {",
    );
    try expectContains(
        runtime_trace_events_module,
        "test \"runtime trace-events module gate keeps selftest-ready failed-exit rollback explicit\" {",
    );
    try expectContains(
        runtime_trace_events_module,
        "try std.testing.expectEqual(@as(usize, 1), replay.selftest_runs);",
    );
    try expectContains(
        runtime_trace_events_module,
        "try std.testing.expectEqual(sample.ModuleStage.selftest_complete, after_failed_exit.stage);",
    );

    try expectContains(
        runtime_trace_events_loader,
        "test \"runtime trace-events loader keeps initialized shared-request snapshots stable across later selftest activity\" {",
    );
    try expectContains(
        runtime_trace_events_loader,
        "test \"runtime trace-events loader rejects prepared shared selftest-hook drift before any local runtime handoff\" {",
    );
    try expectContains(
        runtime_trace_events_loader,
        "test \"runtime trace-events loader rejects registration snapshot drift\" {",
    );
    try expectContains(
        runtime_trace_events_loader,
        "test \"runtime trace-events loader keeps selftest-ready single registration drain explicit before shared handoff\" {",
    );
    try expectContains(
        runtime_trace_events_loader,
        "try std.testing.expectEqual(runtime_loader.HandoffStage.initialized, pending_plan.init_flow.handoff_stage);",
    );
    try expectContains(
        runtime_trace_events_loader,
        "try std.testing.expectError(error.OutstandingRegistrationForLoader, RuntimeTraceEventsLoader.planFor(&module));",
    );

    try expectContains(phase9_build, "runtime_trace_events.zig");
    try expectContains(phase9_build, "phase9-runtime-trace-events-sample-tests");
    try expectContains(phase9_build, "runtime_trace_events_module.zig");
    try expectContains(phase9_build, "phase9-runtime-trace-events-module-tests");
    try expectContains(phase9_build, "runtime_trace_events_diff.zig");
    try expectContains(phase9_build, "runtime_trace_events_loader.zig");
    try expectContains(phase9_build, "phase9-runtime-trace-events-loader-tests");
    try expectContains(phase9_build, "phase9-runtime-trace-events-tests");
    try expectContains(phase9_build, "runtime_trace_events_survey.zig");
    try expectContains(phase9_build, "phase9-runtime-trace-events-survey-tests");
}