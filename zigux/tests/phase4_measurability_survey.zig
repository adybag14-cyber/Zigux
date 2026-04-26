const std = @import("std");

const SurveySummary = struct {
    roadmap_anchor_count: usize,
    landed_phase4_diff_gates: usize,
    preexisting_phase4_build_present: bool,
    preexisting_phase4_validator_present: bool,
    preexisting_phase4_doc_note_present: bool,
    preexisting_phase4_ci_matrix_present: bool,
    preexisting_phase4_lab_matrix_note_present: bool,
    preexisting_phase4_perf_threshold_note_present: bool,
    preexisting_phase4_sample_path_count: usize,
};

const OwnershipAudit = struct {
    id: []const u8,
    surface: []const u8,
    status: []const u8,
    rollback_owner_recorded: bool,
    fallback_path_recorded: bool,
    note: []const u8,
};

const LabMatrixEntry = struct {
    id: []const u8,
    scope: []const u8,
    status: []const u8,
    evidence_path: []const u8,
    note: []const u8,
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
    anchor_paths: []const []const u8,
    roadmap_destinations: []const []const u8,
    survey_summary: SurveySummary,
    ownership_audit: []const OwnershipAudit,
    lab_matrix_audit: []const LabMatrixEntry,
    gaps: []const Gap,
};

fn isAllowedGapStatus(status: []const u8) bool {
    return std.mem.eql(u8, status, "starter_landed") or
        std.mem.eql(u8, status, "ready_next") or
        std.mem.eql(u8, status, "blocked_on_phase5_reference_patterns");
}

test "phase 4 measurability survey manifest records the remaining roadmap gaps" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const manifest_json = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase4_measurability_manifest.json",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(manifest_json);

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{});
    defer parsed.deinit();

    const manifest = parsed.value;
    try std.testing.expectEqualStrings("P4-L19", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 4", manifest.phase);
    try std.testing.expectEqualStrings("35fee78114aac187c525d477cfa599f65a1f813f", manifest.surveyed_commit);
    try std.testing.expectEqual(@as(usize, 4), manifest.anchor_paths.len);
    try std.testing.expectEqual(@as(usize, 5), manifest.roadmap_destinations.len);
    try std.testing.expectEqual(@as(usize, 4), manifest.survey_summary.roadmap_anchor_count);
    try std.testing.expectEqual(@as(usize, 2), manifest.survey_summary.landed_phase4_diff_gates);
    try std.testing.expect(manifest.survey_summary.preexisting_phase4_build_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase4_validator_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase4_doc_note_present);
    try std.testing.expect(!manifest.survey_summary.preexisting_phase4_ci_matrix_present);
    try std.testing.expect(!manifest.survey_summary.preexisting_phase4_lab_matrix_note_present);
    try std.testing.expect(!manifest.survey_summary.preexisting_phase4_perf_threshold_note_present);
    try std.testing.expectEqual(@as(usize, 0), manifest.survey_summary.preexisting_phase4_sample_path_count);
    try std.testing.expectEqual(@as(usize, 3), manifest.ownership_audit.len);
    try std.testing.expectEqual(@as(usize, 4), manifest.lab_matrix_audit.len);
    try std.testing.expect(manifest.gaps.len >= 8);

    var landed_count: usize = 0;
    var ready_next_count: usize = 0;
    var blocked_count: usize = 0;
    var saw_owner_gap = false;
    var saw_matrix_gap = false;
    var saw_sample_blocker = false;

    for (manifest.gaps, 0..) |gap, i| {
        try std.testing.expect(gap.id.len > 0);
        try std.testing.expect(gap.kind.len > 0);
        try std.testing.expect(gap.why_now.len > 0);
        try std.testing.expect(isAllowedGapStatus(gap.status));

        if (std.mem.eql(u8, gap.status, "starter_landed")) {
            landed_count += 1;
        } else if (std.mem.eql(u8, gap.status, "ready_next")) {
            ready_next_count += 1;
        } else if (std.mem.eql(u8, gap.status, "blocked_on_phase5_reference_patterns")) {
            blocked_count += 1;
        }

        if (std.mem.eql(u8, gap.id, "phase4-rollback-owner-record")) {
            saw_owner_gap = true;
            try std.testing.expectEqualStrings("ready_next", gap.status);
            try std.testing.expectEqualStrings("Documentation/zigux/phase4-measurability-survey.md", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "explicit rollback owner") != null);
        }
        if (std.mem.eql(u8, gap.id, "phase4-lab-matrix-note")) {
            saw_matrix_gap = true;
            try std.testing.expectEqualStrings("ready_next", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "lab matrix") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "CI matrix") != null);
        }
        if (std.mem.eql(u8, gap.id, "phase4-reference-sample-ports")) {
            saw_sample_blocker = true;
            try std.testing.expectEqualStrings("blocked_on_phase5_reference_patterns", gap.status);
            try std.testing.expectEqualStrings("samples/zigux/kprobe_example.zig", gap.zigux_destination);
        }

        for (manifest.gaps[i + 1 ..]) |other| {
            try std.testing.expect(!std.mem.eql(u8, gap.id, other.id));
        }
    }

    try std.testing.expectEqual(@as(usize, 5), landed_count);
    try std.testing.expectEqual(@as(usize, 3), ready_next_count);
    try std.testing.expectEqual(@as(usize, 1), blocked_count);
    try std.testing.expect(saw_owner_gap);
    try std.testing.expect(saw_matrix_gap);
    try std.testing.expect(saw_sample_blocker);
}

test "phase 4 measurability survey records the missing rollback-owner and matrix follow-ups" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const manifest_json = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase4_measurability_manifest.json",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(manifest_json);

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{});
    defer parsed.deinit();

    const ownership = parsed.value.ownership_audit;
    try std.testing.expectEqualStrings("phase4-shared-diff-gate", ownership[0].id);
    try std.testing.expectEqualStrings("implicit_only", ownership[0].status);
    try std.testing.expect(!ownership[0].rollback_owner_recorded);
    try std.testing.expect(ownership[0].fallback_path_recorded);

    try std.testing.expectEqualStrings("phase4-atomic64-bitmap-diff-files", ownership[1].id);
    try std.testing.expectEqualStrings("implicit_only", ownership[1].status);
    try std.testing.expect(!ownership[1].rollback_owner_recorded);
    try std.testing.expect(std.mem.indexOf(u8, ownership[1].note, "file-local expectations") != null);

    try std.testing.expectEqualStrings("phase4-reference-sample-paths", ownership[2].id);
    try std.testing.expectEqualStrings("missing_reference_samples", ownership[2].status);
    try std.testing.expect(!ownership[2].rollback_owner_recorded);
    try std.testing.expect(!ownership[2].fallback_path_recorded);

    const matrix = parsed.value.lab_matrix_audit;
    try std.testing.expectEqualStrings("phase4-bootstrap-entrypoint", matrix[0].id);
    try std.testing.expectEqualStrings("single_target_bootstrap_only", matrix[0].status);
    try std.testing.expect(std.mem.indexOf(u8, matrix[0].evidence_path, "zigux/tests/phase4_build.zig") != null);

    try std.testing.expectEqualStrings("phase4-ci-matrix", matrix[1].id);
    try std.testing.expectEqualStrings("missing_matrix", matrix[1].status);

    try std.testing.expectEqualStrings("phase4-lab-replay-matrix", matrix[2].id);
    try std.testing.expectEqualStrings("missing_matrix", matrix[2].status);

    try std.testing.expectEqualStrings("phase4-perf-thresholds", matrix[3].id);
    try std.testing.expectEqualStrings("missing_thresholds", matrix[3].status);
}
