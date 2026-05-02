const std = @import("std");

const current_surveyed_commit = "3ba64cd4e41a4de1c8fd8dbaecb23702ad9701a3";

const SurveySummary = struct {
    test_bitmap_anchor_present: bool,
    bitmap_diff_gate_present: bool,
    rounded_fill_gap_recorded: bool,
    phase4_build_present: bool,
    phase4_build_is_gate_only: bool,
    phase4_validation_matrix_present: bool,
};

const Gap = struct {
    id: []const u8,
    status: []const u8,
    kind: []const u8,
    zigux_destination: []const u8,
    why_now: []const u8,
};

const ThresholdPlan = struct {
    owner: []const u8,
    rollback_owner: []const u8,
    posture: []const u8,
    status: []const u8,
    benchmark_command: []const u8,
    acceptable_limit: []const u8,
    scope: []const u8,
    why_not_approved_yet: []const u8,
};

const Manifest = struct {
    lane_key: []const u8,
    phase: []const u8,
    surveyed_commit: []const u8,
    anchor: []const u8,
    roadmap_destinations: []const []const u8,
    survey_summary: SurveySummary,
    threshold_plan: ThresholdPlan,
    gaps: []const Gap,
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
        std.mem.eql(u8, status, "blocked_on_fill_rounding_parity");
}

fn isLowerHexSha(value: []const u8) bool {
    if (value.len != 40) return false;
    for (value) |byte| {
        if (!std.ascii.isHex(byte) or std.ascii.isUpper(byte)) return false;
    }
    return true;
}

test "phase4 bitmap diff survey manifest records the shipped gate, the current rounded-fill gap, and the shared replay path" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const manifest_json = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase4_bitmap_diff_manifest.json",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(manifest_json);

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{});
    defer parsed.deinit();

    const manifest = parsed.value;
    try std.testing.expectEqualStrings("P4-L07", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 4", manifest.phase);
    try std.testing.expectEqualStrings("lib/test_bitmap.c", manifest.anchor);
    try std.testing.expect(isLowerHexSha(current_surveyed_commit));
    try std.testing.expectEqualStrings(current_surveyed_commit, manifest.surveyed_commit);
    try std.testing.expect(isLowerHexSha(manifest.surveyed_commit));
    try std.testing.expectEqual(@as(usize, 1), manifest.roadmap_destinations.len);
    try std.testing.expectEqualStrings("zigux/tests/bitmap_diff.zig", manifest.roadmap_destinations[0]);
    try std.testing.expectEqualStrings("Shared Subsystems Pod", manifest.threshold_plan.owner);
    try std.testing.expectEqualStrings("Shared Subsystems Pod", manifest.threshold_plan.rollback_owner);
    try std.testing.expectEqualStrings(
        "threshold_pending_until_bitmap_gate_grows_beyond_bounded_correctness_checks",
        manifest.threshold_plan.posture,
    );
    try std.testing.expectEqualStrings(
        "pending_bounded_benchmark",
        manifest.threshold_plan.status,
    );
    try std.testing.expectEqualStrings(
        "unapproved_until_bitmap_gate_grows_beyond_bounded_correctness_checks",
        manifest.threshold_plan.benchmark_command,
    );
    try std.testing.expectEqualStrings(
        "unapproved_until_bitmap_gate_grows_beyond_bounded_correctness_checks",
        manifest.threshold_plan.acceptable_limit,
    );
    try std.testing.expect(
        std.mem.indexOf(u8, manifest.threshold_plan.scope, "rounded-prefix") != null,
    );
    try std.testing.expect(
        std.mem.indexOf(u8, manifest.threshold_plan.scope, "copy-behavior") != null,
    );
    try std.testing.expect(
        std.mem.indexOf(u8, manifest.threshold_plan.why_not_approved_yet, "bit 114") != null,
    );
    try std.testing.expectEqual(@as(usize, 5), manifest.gaps.len);

    const test_bitmap_c = try readWorkspaceFile(
        io_instance.io(),
        std.testing.allocator,
        "lib/test_bitmap.c",
        256 * 1024,
    );
    defer std.testing.allocator.free(test_bitmap_c);
    const bitmap_diff = try readWorkspaceFile(
        io_instance.io(),
        std.testing.allocator,
        "zigux/tests/bitmap_diff.zig",
        128 * 1024,
    );
    defer std.testing.allocator.free(bitmap_diff);
    const phase4_build = try readWorkspaceFile(
        io_instance.io(),
        std.testing.allocator,
        "zigux/tests/phase4_build.zig",
        32 * 1024,
    );
    defer std.testing.allocator.free(phase4_build);
    const phase4_validation_matrix = try readWorkspaceFile(
        io_instance.io(),
        std.testing.allocator,
        "Documentation/zigux/phase4-validation-matrix.md",
        64 * 1024,
    );
    defer std.testing.allocator.free(phase4_validation_matrix);
    const live_summary = SurveySummary{
        .test_bitmap_anchor_present = std.mem.indexOf(u8, test_bitmap_c, "test_zero_clear") != null and
            std.mem.indexOf(u8, test_bitmap_c, "test_fill_set") != null and
            std.mem.indexOf(u8, test_bitmap_c, "test_find_nth_bit") != null and
            std.mem.indexOf(u8, test_bitmap_c, "test_copy") != null,
        .bitmap_diff_gate_present = std.mem.indexOf(u8, bitmap_diff, "bitmap diff gate replays bounded lib/test_bitmap.c range expectations") != null and
            std.mem.indexOf(u8, bitmap_diff, "bitmap diff gate records exact bounded copy checks") != null and
            std.mem.indexOf(u8, bitmap_diff, "bitmap diff gate records exact bounded find_nth_bit checks") != null,
        .rounded_fill_gap_recorded = std.mem.indexOf(u8, bitmap_diff, "bitmap diff survey keeps the current rounded fill drifts explicit against lib/test_bitmap.c") != null and
            std.mem.indexOf(u8, bitmap_diff, "the current Zig helper stops at bit 114") != null,
        .phase4_build_present = std.mem.indexOf(u8, phase4_build, "bitmap_diff.zig") != null and
            std.mem.indexOf(u8, phase4_build, "phase4-bitmap-diff-tests") != null,
        .phase4_build_is_gate_only = std.mem.indexOf(u8, phase4_build, "phase4_bitmap_diff_survey.zig") == null and
            std.mem.indexOf(u8, phase4_build, "phase4-bitmap-diff-survey-tests") == null and
            std.mem.indexOf(u8, phase4_build, "phase4-bitmap-diff-survey") == null,
        .phase4_validation_matrix_present = std.mem.indexOf(u8, phase4_validation_matrix, "`zigux/tests/bitmap_diff.zig`") != null and
            std.mem.indexOf(u8, phase4_validation_matrix, "threshold_pending_until_bitmap_gate_grows_beyond_bounded_correctness_checks") != null and
            std.mem.indexOf(u8, phase4_validation_matrix, "current rollback evidence gap") != null,
    };

    try std.testing.expectEqualDeep(live_summary, manifest.survey_summary);

    var starter_landed_count: usize = 0;
    var ready_next_count: usize = 0;
    var blocked_count: usize = 0;
    var saw_live_gate = false;
    var saw_survey_gate = false;
    var saw_shared_build_gap = false;
    var saw_matrix_note = false;
    var saw_broader_surface_gap = false;

    for (manifest.gaps, 0..) |gap, i| {
        try std.testing.expect(gap.id.len > 0);
        try std.testing.expect(gap.kind.len > 0);
        try std.testing.expect(gap.why_now.len > 0);
        try std.testing.expect(isAllowedStatus(gap.status));

        if (std.mem.eql(u8, gap.status, "starter_landed")) {
            starter_landed_count += 1;
        } else if (std.mem.eql(u8, gap.status, "ready_next")) {
            ready_next_count += 1;
        } else if (std.mem.eql(u8, gap.status, "blocked_on_fill_rounding_parity")) {
            blocked_count += 1;
        }

        if (std.mem.eql(u8, gap.id, "phase4-bitmap-diff-gate")) {
            saw_live_gate = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("zigux/tests/bitmap_diff.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "rounded-prefix") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "cross-boundary") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "find_nth_bit") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "copy-behavior") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase4-bitmap-diff-survey-packet")) {
            saw_survey_gate = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("zigux/tests/phase4_bitmap_diff_survey.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "manifest-backed bitmap survey") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "rollback evidence gap") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase4-bitmap-diff-survey-build-step")) {
            saw_shared_build_gap = true;
            try std.testing.expectEqualStrings("ready_next", gap.status);
            try std.testing.expectEqualStrings("zigux/tests/phase4_build.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "phase4-bitmap-diff-tests") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "does not yet run a dedicated bitmap survey test") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase4-validation-matrix-note")) {
            saw_matrix_note = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("Documentation/zigux/phase4-validation-matrix.md", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "rollback owner") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "threshold posture") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "current rollback evidence gap") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase4-broader-bitmap-surface")) {
            saw_broader_surface_gap = true;
            try std.testing.expectEqualStrings("blocked_on_fill_rounding_parity", gap.status);
            try std.testing.expectEqualStrings("zigux/tests/bitmap_diff.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "bit 114") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "lib/test_bitmap.c") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "perf threshold") != null);
        }

        for (manifest.gaps[i + 1 ..]) |other| {
            try std.testing.expect(!std.mem.eql(u8, gap.id, other.id));
        }
    }

    try std.testing.expectEqual(@as(usize, 3), starter_landed_count);
    try std.testing.expectEqual(@as(usize, 1), ready_next_count);
    try std.testing.expectEqual(@as(usize, 1), blocked_count);
    try std.testing.expect(saw_live_gate);
    try std.testing.expect(saw_survey_gate);
    try std.testing.expect(saw_shared_build_gap);
    try std.testing.expect(saw_matrix_note);
    try std.testing.expect(saw_broader_surface_gap);
}
