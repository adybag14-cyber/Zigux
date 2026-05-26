const std = @import("std");

const survey_note_source = @embedFile("../../Documentation/zigux/phase9-runtime-atomic64-survey.md");
const module_slice_note_source = @embedFile("../../Documentation/zigux/phase9-runtime-atomic64-module-slice.md");
const docs_root_readme_source = @embedFile("../../Documentation/zigux/README.md");
const samples_root_readme_source = @embedFile("../../samples/zigux/README.md");
const tests_root_readme_source = @embedFile("README.md");

const SurveySummary = struct {
    atomic64_test_c_lines: usize,
    preexisting_runtime_test_files: usize,
    preexisting_samples_zigux_present: bool,
    preexisting_phase9_build_present: bool,
    preexisting_phase9_doc_present: bool,
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

const GovernanceRecord = struct {
    governance_lane: []const u8,
    packet_owner: []const u8,
    phase: []const u8,
    study_boundary_anchor: []const u8,
    status_bucket: []const u8,
    validation_gate_summary: []const []const u8,
    rollback_owner: []const u8,
    reopen_rule: []const u8,
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
    roadmap_gap_summary: RoadmapGapSummary,
    delivery_evidence_catalog: []const DeliveryEvidence,
    ownership_map: []const OwnershipEntry,
    governance_record: GovernanceRecord,
    gaps: []const Gap,
};

fn isAllowedStatus(status: []const u8) bool {
    return std.mem.eql(u8, status, "starter_landed") or
        std.mem.eql(u8, status, "ready_next") or
        std.mem.eql(u8, status, "blocked_on_runtime_substrate") or
        std.mem.eql(u8, status, "visible_review_only_packet");
}

fn findGap(gaps: []const Gap, id: []const u8) ?Gap {
    for (gaps) |gap| {
        if (std.mem.eql(u8, gap.id, id)) return gap;
    }
    return null;
}

fn hasEvidence(entries: []const DeliveryEvidence, id: []const u8, path: []const u8) bool {
    for (entries) |entry| {
        if (std.mem.eql(u8, entry.id, id) and std.mem.eql(u8, entry.path, path)) return true;
    }
    return false;
}

fn hasOwnership(entries: []const OwnershipEntry, surface: []const u8, owner: []const u8) bool {
    for (entries) |entry| {
        if (std.mem.eql(u8, entry.surface, surface) and std.mem.eql(u8, entry.owner, owner)) {
            return true;
        }
    }
    return false;
}

fn findOwnership(entries: []const OwnershipEntry, surface: []const u8) ?OwnershipEntry {
    for (entries) |entry| {
        if (std.mem.eql(u8, entry.surface, surface)) return entry;
    }
    return null;
}

fn hasValidationGate(entries: []const []const u8, path: []const u8) bool {
    for (entries) |entry| {
        if (std.mem.eql(u8, entry, path)) return true;
    }
    return false;
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectLacks(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

fn expectSurveyedCommitMarker(note_source: []const u8, surveyed_commit: []const u8) !void {
    const marker = try std.fmt.allocPrint(
        std.testing.allocator,
        "`PHASE9_SURVEYED_COMMIT={s}`",
        .{surveyed_commit},
    );
    defer std.testing.allocator.free(marker);
    try expectContains(note_source, marker);
}

test "phase 9 runtime atomic64 survey manifest records the visible shared-loader reminder packet" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const manifest_json = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/runtime_atomic64_manifest.json",
        std.testing.allocator,
        .limited(64 * 1024),
    );
    defer std.testing.allocator.free(manifest_json);

    const makefile = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/Makefile",
        std.testing.allocator,
        .limited(64 * 1024),
    );
    defer std.testing.allocator.free(makefile);

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{});
    defer parsed.deinit();

    const manifest = parsed.value;
    try std.testing.expect(manifest.surveyed_commit.len > 0);
    try expectSurveyedCommitMarker(survey_note_source, manifest.surveyed_commit);
    try expectSurveyedCommitMarker(module_slice_note_source, manifest.surveyed_commit);
    try std.testing.expectEqualStrings("P9-L04", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 9", manifest.phase);
    try std.testing.expectEqualStrings("lib/atomic64_test.c", manifest.anchor);
    try std.testing.expectEqual(@as(usize, 2), manifest.roadmap_destinations.len);
    try std.testing.expect(manifest.survey_summary.atomic64_test_c_lines >= 200);
    try std.testing.expectEqual(@as(usize, 3), manifest.survey_summary.preexisting_runtime_test_files);
    try std.testing.expect(manifest.survey_summary.preexisting_samples_zigux_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase9_build_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase9_doc_present);

    try std.testing.expectEqualStrings(
        "starter_landed_with_visible_shared_loader_packet",
        manifest.roadmap_gap_summary.landed_pilot_state,
    );
    try std.testing.expect(std.mem.indexOf(u8, manifest.roadmap_gap_summary.missing_capability, "runtime substrate") != null);
    try std.testing.expect(std.mem.indexOf(u8, manifest.roadmap_gap_summary.next_gate, "review-only evidence") != null);

    try std.testing.expectEqual(@as(usize, 13), manifest.delivery_evidence_catalog.len);
    try std.testing.expect(hasEvidence(
        manifest.delivery_evidence_catalog,
        "runtime-atomic64-sample",
        "samples/zigux/runtime_atomic64.zig",
    ));
    try std.testing.expect(hasEvidence(
        manifest.delivery_evidence_catalog,
        "runtime-atomic64-family-make-route",
        "zigux/Makefile",
    ));
    try std.testing.expect(hasEvidence(
        manifest.delivery_evidence_catalog,
        "runtime-loader-facade",
        "zigux/kernel/runtime_loader.zig",
    ));
    try std.testing.expect(hasEvidence(
        manifest.delivery_evidence_catalog,
        "runtime-loader-contract",
        "zigux/kernel/runtime_loader_contract.zig",
    ));
    try std.testing.expect(hasEvidence(
        manifest.delivery_evidence_catalog,
        "runtime-loader-allocator-init-flow",
        "zigux/tests/runtime_loader_allocator_init_flow.zig",
    ));
    try std.testing.expect(hasEvidence(
        manifest.delivery_evidence_catalog,
        "runtime-loader-command-env-boundary-guard",
        "zigux/kernel/runtime_loader_command_env_boundary_guard.zig",
    ));
    try std.testing.expect(hasEvidence(
        manifest.delivery_evidence_catalog,
        "runtime-bitmap-loader-companion",
        "samples/zigux/runtime_bitmap_loader.zig",
    ));
    try std.testing.expect(hasEvidence(
        manifest.delivery_evidence_catalog,
        "runtime-atomic64-shared-build-boundary",
        "zigux/tests/phase9_build.zig",
    ));
    try std.testing.expect(hasEvidence(
        manifest.delivery_evidence_catalog,
        "runtime-atomic64-survey-note",
        "Documentation/zigux/phase9-runtime-atomic64-survey.md",
    ));
    try std.testing.expect(hasEvidence(
        manifest.delivery_evidence_catalog,
        "runtime-atomic64-module-slice-note",
        "Documentation/zigux/phase9-runtime-atomic64-module-slice.md",
    ));

    try std.testing.expectEqual(@as(usize, 5), manifest.ownership_map.len);
    try std.testing.expect(hasOwnership(
        manifest.ownership_map,
        "zigux/tests/runtime_atomic64_manifest.json",
        "P9-L04",
    ));
    try std.testing.expect(hasOwnership(
        manifest.ownership_map,
        "Documentation/zigux/phase9-runtime-atomic64-survey.md",
        "P9-L04",
    ));
    try std.testing.expect(hasOwnership(
        manifest.ownership_map,
        "Documentation/zigux/phase9-runtime-atomic64-module-slice.md",
        "P9-L04",
    ));
    try std.testing.expect(hasOwnership(
        manifest.ownership_map,
        "Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md",
        "P9-L13",
    ));
    try std.testing.expect(hasOwnership(
        manifest.ownership_map,
        "zigux/tests/phase9_build.zig",
        "P9-L13",
    ));

    const survey_entry = findOwnership(
        manifest.ownership_map,
        "Documentation/zigux/phase9-runtime-atomic64-survey.md",
    ) orelse return error.MissingSurveyOwnership;
    try std.testing.expectEqualStrings("survey_note", survey_entry.role);
    try std.testing.expect(std.mem.indexOf(u8, survey_entry.boundary, "blocked live loader-binding boundary") != null);

    const module_slice_entry = findOwnership(
        manifest.ownership_map,
        "Documentation/zigux/phase9-runtime-atomic64-module-slice.md",
    ) orelse return error.MissingModuleSliceOwnership;
    try std.testing.expectEqualStrings("module_slice_note", module_slice_entry.role);
    try std.testing.expect(std.mem.indexOf(u8, module_slice_entry.boundary, "without claiming loadable-module parity") != null);

    const sequencing_entry = findOwnership(
        manifest.ownership_map,
        "Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md",
    ) orelse return error.MissingSequencingOwnership;
    try std.testing.expectEqualStrings("shared_owner_map", sequencing_entry.role);
    try std.testing.expect(std.mem.indexOf(
        u8,
        sequencing_entry.boundary,
        "shared Phase 9 loader-facing reminder packet separately from this runtime atomic64 family-local packet",
    ) != null);

    const shared_build_entry = findOwnership(
        manifest.ownership_map,
        "zigux/tests/phase9_build.zig",
    ) orelse return error.MissingSharedBuildOwnership;
    try std.testing.expectEqualStrings("shared_build_bundle", shared_build_entry.role);
    try std.testing.expect(std.mem.indexOf(
        u8,
        shared_build_entry.boundary,
        "outside this shared-build ownership surface",
    ) != null);

    try std.testing.expectEqualStrings("P9-L13", manifest.governance_record.governance_lane);
    try std.testing.expectEqualStrings("P9-L04", manifest.governance_record.packet_owner);
    try std.testing.expectEqualStrings("Phase 9", manifest.governance_record.phase);
    try std.testing.expectEqualStrings("kernel/workqueue.c", manifest.governance_record.study_boundary_anchor);
    try std.testing.expect(std.mem.indexOf(u8, manifest.governance_record.status_bucket, "review-only direct starter packet") != null);
    try std.testing.expectEqual(@as(usize, 7), manifest.governance_record.validation_gate_summary.len);
    try std.testing.expect(hasValidationGate(manifest.governance_record.validation_gate_summary, "zigux/tests/runtime_atomic64_survey.zig"));
    try std.testing.expect(hasValidationGate(manifest.governance_record.validation_gate_summary, "zigux/tests/runtime_atomic64_manifest.json"));
    try std.testing.expect(hasValidationGate(manifest.governance_record.validation_gate_summary, "zigux/tests/runtime_atomic64_module.zig"));
    try std.testing.expect(hasValidationGate(manifest.governance_record.validation_gate_summary, "zigux/tests/runtime_atomic64_diff.zig"));
    try std.testing.expect(hasValidationGate(manifest.governance_record.validation_gate_summary, "zigux/tests/phase9_build.zig"));
    try std.testing.expect(hasValidationGate(manifest.governance_record.validation_gate_summary, "zigux/kernel/runtime_loader_command_env_boundary_guard.zig"));
    try std.testing.expect(hasValidationGate(manifest.governance_record.validation_gate_summary, "samples/zigux/runtime_bitmap_loader.zig"));
    try std.testing.expectEqualStrings("lib/atomic64_test.c", manifest.governance_record.rollback_owner);
    try std.testing.expect(std.mem.indexOf(u8, manifest.governance_record.reopen_rule, "kernel/workqueue.c") != null);
    try std.testing.expect(std.mem.indexOf(u8, manifest.governance_record.reopen_rule, "phase15-architecture-council-review-process.md") != null);
    try std.testing.expect(std.mem.indexOf(u8, manifest.governance_record.reopen_rule, "phase15-freeze-map-governance.md") != null);
    try std.testing.expect(std.mem.indexOf(u8, manifest.governance_record.reopen_rule, "phase15-parity-scorecard.md") != null);
    try std.testing.expect(std.mem.indexOf(u8, manifest.governance_record.reopen_rule, "phase15-indefinite-c-policy.md") != null);
    try std.testing.expect(std.mem.indexOf(u8, manifest.governance_record.reopen_rule, "phase15-architecture-council-decision-record-template.md") != null);

    try std.testing.expectEqual(@as(usize, 8), manifest.gaps.len);
    for (manifest.gaps, 0..) |gap, i| {
        try std.testing.expect(gap.id.len > 0);
        try std.testing.expect(gap.kind.len > 0);
        try std.testing.expect(gap.why_now.len > 0);
        try std.testing.expect(isAllowedStatus(gap.status));

        for (manifest.gaps[i + 1 ..]) |other| {
            try std.testing.expect(!std.mem.eql(u8, gap.id, other.id));
        }
    }

    const build_gap = findGap(manifest.gaps, "phase9-build-gate") orelse return error.MissingBuildGap;
    try std.testing.expectEqualStrings("visible_review_only_packet", build_gap.status);
    try std.testing.expectEqualStrings("zigux/tests/phase9_build.zig", build_gap.zigux_destination);
    try std.testing.expect(std.mem.indexOf(u8, build_gap.why_now, "runtime_loader_command_env_boundary_guard.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, build_gap.why_now, "runtime_bitmap_loader.zig") != null);

    const survey_gap = findGap(manifest.gaps, "runtime-atomic64-survey-gate") orelse return error.MissingSurveyGap;
    try std.testing.expectEqualStrings("starter_landed", survey_gap.status);
    try std.testing.expectEqualStrings("zigux/tests/runtime_atomic64_survey.zig", survey_gap.zigux_destination);

    const make_route_gap = findGap(manifest.gaps, "runtime-atomic64-make-route") orelse return error.MissingMakeRouteGap;
    try std.testing.expectEqualStrings("starter_landed", make_route_gap.status);
    try std.testing.expectEqualStrings("zigux/Makefile", make_route_gap.zigux_destination);

    const sample_gap = findGap(manifest.gaps, "runtime-atomic64-sample-module") orelse return error.MissingSampleGap;
    try std.testing.expectEqualStrings("starter_landed", sample_gap.status);
    try std.testing.expectEqualStrings("samples/zigux/runtime_atomic64.zig", sample_gap.zigux_destination);

    const selftest_gap = findGap(manifest.gaps, "runtime-atomic64-selftest-hook") orelse return error.MissingSelftestGap;
    try std.testing.expectEqualStrings("starter_landed", selftest_gap.status);
    try std.testing.expectEqualStrings("samples/zigux/runtime_atomic64.zig", selftest_gap.zigux_destination);

    const module_gap = findGap(manifest.gaps, "runtime-atomic64-module-tests") orelse return error.MissingModuleGap;
    try std.testing.expectEqualStrings("starter_landed", module_gap.status);
    try std.testing.expectEqualStrings("zigux/tests/runtime_atomic64_module.zig", module_gap.zigux_destination);

    const diff_gap = findGap(manifest.gaps, "runtime-atomic64-diff-gate") orelse return error.MissingDiffGap;
    try std.testing.expectEqualStrings("starter_landed", diff_gap.status);
    try std.testing.expectEqualStrings("zigux/tests/runtime_atomic64_diff.zig", diff_gap.zigux_destination);

    const blocked_gap = findGap(manifest.gaps, "runtime-atomic64-live-loader-binding") orelse return error.MissingBlockedGap;
    try std.testing.expectEqualStrings("blocked_on_runtime_substrate", blocked_gap.status);
    try std.testing.expectEqualStrings("zigux/kernel/runtime_loader.zig", blocked_gap.zigux_destination);

    try expectContains(makefile, "phase9-runtime-atomic64-test:");
    try expectContains(makefile, "phase9-runtime-atomic64-tests --build-file zigux/tests/phase9_build.zig --summary all");

    try expectLacks(manifest_json, "scripts/zigux/kconfig/conf_bridge.zig");
    try expectLacks(manifest_json, "scripts/zigux/kconfig/confdata_bridge.zig");
    try expectLacks(manifest_json, "rust/exports.c");
    try expectLacks(manifest_json, "zigux/kernel/export_shim.zig");
}

test "phase 9 runtime atomic64 note family records the current shared-loader reminder packet without older config or export markers" {
    try expectContains(survey_note_source, "zigux/tests/runtime_loader_allocator_init_flow.zig");
    try expectContains(survey_note_source, "zigux/kernel/runtime_loader_command_env_boundary_guard.zig");
    try expectContains(survey_note_source, "samples/zigux/runtime_bitmap_loader.zig");
    try expectContains(survey_note_source, "Documentation/zigux/README.md");
    try expectContains(survey_note_source, "samples/zigux/README.md");
    try expectContains(survey_note_source, "zigux/tests/README.md");
    try expectContains(survey_note_source, "zigux/Makefile");
    try expectContains(survey_note_source, "review-only evidence");
    try expectContains(survey_note_source, "prepared `RuntimeAtomic64LoadSummary` snapshot reviewable");
    try expectContains(survey_note_source, "later counter mutation");
    try expectContains(survey_note_source, "later selftest activity");
    try expectContains(survey_note_source, "later exit activity");
    try expectContains(survey_note_source, "Freeze-Map Governance Evidence");
    try expectContains(survey_note_source, "Minimum Freeze-Map Review Record");
    try expectContains(survey_note_source, "P9-L13");
    try expectContains(survey_note_source, "rollback owner:");
    try expectContains(survey_note_source, "reopen rule:");
    try expectContains(survey_note_source, "phase15-architecture-council-decision-record-template.md");
    try expectContains(survey_note_source, "phase9-runtime-loader-allocator-init-flow-tests");
    try expectContains(survey_note_source, "phase9-runtime-loader-command-env-boundary-guard-tests");
    try expectLacks(survey_note_source, "zigux/tests/runtime_loader_gap_survey.zig");
    try expectLacks(survey_note_source, "zigux/tests/runtime_loader_selftest_complete_exit_parity.zig");
    try expectLacks(survey_note_source, "scripts/zigux/kconfig/conf_bridge.zig");
    try expectLacks(survey_note_source, "scripts/zigux/kconfig/confdata_bridge.zig");
    try expectLacks(survey_note_source, "rust/exports.c");
    try expectLacks(survey_note_source, "zigux/kernel/export_shim.zig");

    try expectContains(module_slice_note_source, "zigux/tests/runtime_loader_allocator_init_flow.zig");
    try expectContains(module_slice_note_source, "zigux/kernel/runtime_loader_command_env_boundary_guard.zig");
    try expectContains(module_slice_note_source, "samples/zigux/runtime_bitmap_loader.zig");
    try expectContains(module_slice_note_source, "Documentation/zigux/README.md");
    try expectContains(module_slice_note_source, "samples/zigux/README.md");
    try expectContains(module_slice_note_source, "zigux/tests/README.md");
    try expectContains(module_slice_note_source, "zigux/Makefile");
    try expectContains(module_slice_note_source, "review-only evidence");
    try expectContains(module_slice_note_source, "Freeze-Map Governance Boundary");
    try expectContains(module_slice_note_source, "Minimum Freeze-Map Review Record");
    try expectLacks(module_slice_note_source, "scripts/zigux/kconfig/conf_bridge.zig");
    try expectLacks(module_slice_note_source, "scripts/zigux/kconfig/confdata_bridge.zig");
    try expectLacks(module_slice_note_source, "rust/exports.c");
    try expectLacks(module_slice_note_source, "zigux/kernel/export_shim.zig");

    try expectContains(docs_root_readme_source, "Phase 9 notes");
    try expectContains(docs_root_readme_source, "Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md");
    try expectContains(docs_root_readme_source, "samples/zigux/README.md");
    try expectContains(docs_root_readme_source, "zigux/tests/README.md");
    try expectContains(docs_root_readme_source, "zigux/tests/phase9_build.zig");
    try expectContains(docs_root_readme_source, "samples/zigux/runtime_bitmap_loader.zig");

    try expectContains(samples_root_readme_source, "## Phase 9 runtime pilot family");
    try expectContains(samples_root_readme_source, "samples/zigux/runtime_atomic64.zig");
    try expectContains(samples_root_readme_source, "samples/zigux/runtime_bitmap_loader.zig");
    try expectContains(samples_root_readme_source, "Keep that bitmap packet framed as a separate Phase 9 runtime reminder");

    try expectContains(tests_root_readme_source, "## Phase 9 runtime packet");
    try expectContains(tests_root_readme_source, "zigux/tests/runtime_loader_allocator_init_flow.zig");
    try expectContains(tests_root_readme_source, "zigux/kernel/runtime_loader_command_env_boundary_guard.zig");
    try expectContains(tests_root_readme_source, "zigux/tests/phase9_build.zig");
    try expectContains(tests_root_readme_source, "samples/zigux/runtime_bitmap_loader.zig");
    try expectContains(tests_root_readme_source, "phase9-runtime-loader-shared-tests");
}
