const std = @import("std");

const SurveySummary = struct {
    atomic64_test_c_lines: usize,
    runtime_atomic64_diff_lines: usize,
    runtime_atomic64_diff_present: bool,
    phase4_build_present: bool,
    runtime_atomic64_sample_present: bool,
    phase4_validation_matrix_present: bool,
    tests_readme_runtime_atomic64_diff_present: bool,
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
    gaps: []const Gap,
};

fn isAllowedStatus(status: []const u8) bool {
    return std.mem.eql(u8, status, "starter_landed") or
        std.mem.eql(u8, status, "ready_next") or
        std.mem.eql(u8, status, "blocked_on_broader_atomic64_surface");
}

test "phase4 runtime atomic64 survey manifest records the shipped bounded gate and the remaining roadmap gap" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const manifest_json = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase4_runtime_atomic64_diff_manifest.json",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(manifest_json);

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{});
    defer parsed.deinit();

    const manifest = parsed.value;
    try std.testing.expectEqualStrings("P4-L01", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 4", manifest.phase);
    try std.testing.expectEqualStrings("lib/atomic64_test.c", manifest.anchor);
    try std.testing.expectEqualStrings("c5e4b230582aa802127d96e4bf11ba03aa82381f", manifest.surveyed_commit);
    try std.testing.expectEqual(@as(usize, 1), manifest.roadmap_destinations.len);
    try std.testing.expectEqualStrings("zigux/tests/atomic64_diff.zig", manifest.roadmap_destinations[0]);
    try std.testing.expect(manifest.survey_summary.atomic64_test_c_lines >= 250);
    try std.testing.expect(manifest.survey_summary.runtime_atomic64_diff_lines >= 200);
    try std.testing.expect(manifest.survey_summary.runtime_atomic64_diff_present);
    try std.testing.expect(manifest.survey_summary.phase4_build_present);
    try std.testing.expect(manifest.survey_summary.runtime_atomic64_sample_present);
    try std.testing.expect(manifest.survey_summary.phase4_validation_matrix_present);
    try std.testing.expect(manifest.survey_summary.tests_readme_runtime_atomic64_diff_present);
    try std.testing.expectEqual(@as(usize, 6), manifest.gaps.len);

    var starter_landed_count: usize = 0;
    var ready_next_count: usize = 0;
    var blocked_count: usize = 0;
    var saw_live_gate = false;
    var saw_runtime_sample = false;
    var saw_shared_build = false;
    var saw_matrix_note = false;
    var saw_path_gap = false;
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
        } else if (std.mem.eql(u8, gap.status, "blocked_on_broader_atomic64_surface")) {
            blocked_count += 1;
        }

        if (std.mem.eql(u8, gap.id, "phase4-runtime-atomic64-diff-gate")) {
            saw_live_gate = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("zigux/tests/runtime_atomic64_diff.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "exchange, cmpxchg, add_unless, inc_not_zero, dec_if_positive") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "selftest-family") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase4-runtime-atomic64-sample-starter")) {
            saw_runtime_sample = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("samples/zigux/runtime_atomic64.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "selftest-hook replay") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase4-shared-build-entrypoint")) {
            saw_shared_build = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("zigux/tests/phase4_build.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "bitmap gate") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "rollback surface") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase4-validation-matrix-note")) {
            saw_matrix_note = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("Documentation/zigux/phase4-validation-matrix.md", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "rollback owner") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "threshold posture") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase4-roadmap-path-alignment")) {
            saw_path_gap = true;
            try std.testing.expectEqualStrings("ready_next", gap.status);
            try std.testing.expectEqualStrings("zigux/tests/atomic64_diff.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "runtime_atomic64_diff.zig") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "canonical path") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase4-broader-atomic64-surface")) {
            saw_broader_surface_gap = true;
            try std.testing.expectEqualStrings("blocked_on_broader_atomic64_surface", gap.status);
            try std.testing.expectEqualStrings("zigux/tests/runtime_atomic64_diff.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "full wider atomic64_test.c surface") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "perf threshold") != null);
        }

        for (manifest.gaps[i + 1 ..]) |other| {
            try std.testing.expect(!std.mem.eql(u8, gap.id, other.id));
        }
    }

    try std.testing.expectEqual(@as(usize, 4), starter_landed_count);
    try std.testing.expectEqual(@as(usize, 1), ready_next_count);
    try std.testing.expectEqual(@as(usize, 1), blocked_count);
    try std.testing.expect(saw_live_gate);
    try std.testing.expect(saw_runtime_sample);
    try std.testing.expect(saw_shared_build);
    try std.testing.expect(saw_matrix_note);
    try std.testing.expect(saw_path_gap);
    try std.testing.expect(saw_broader_surface_gap);
}
