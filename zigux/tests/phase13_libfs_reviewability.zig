const std = @import("std");
const libfs = @import("libfs");

const SurveySummary = struct {
    libfs_c_lines: usize,
    preexisting_phase13_build_present: bool,
    preexisting_phase13_make_target_present: bool,
    preexisting_fs_libfs_zig_present: bool,
    preexisting_phase13_libfs_test_present: bool,
    preexisting_phase13_slice_note_present: bool,
    preexisting_phase13_reviewability_present: bool,
    preexisting_phase13_survey_note_present: bool,
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
        std.mem.eql(u8, status, "blocked_on_vfs_state");
}

test "phase13 libfs manifest records the landed starter and remaining helper-surface gap" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const manifest_json = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase13_libfs_manifest.json",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(manifest_json);

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{});
    defer parsed.deinit();

    const manifest = parsed.value;
    try std.testing.expectEqualStrings("P13-L03", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 13", manifest.phase);
    try std.testing.expectEqualStrings("fs/libfs.c", manifest.anchor);
    try std.testing.expectEqualStrings("master-reviewability", manifest.surveyed_commit);
    try std.testing.expectEqual(@as(usize, 3), manifest.roadmap_destinations.len);
    try std.testing.expect(manifest.survey_summary.libfs_c_lines >= 2300);
    try std.testing.expect(manifest.survey_summary.preexisting_phase13_build_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase13_make_target_present);
    try std.testing.expect(manifest.survey_summary.preexisting_fs_libfs_zig_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase13_libfs_test_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase13_slice_note_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase13_reviewability_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase13_survey_note_present);
    try std.testing.expectEqual(@as(usize, 10), manifest.gaps.len);

    const descriptor = libfs.LibFsHelperLab.descriptor();
    try std.testing.expectEqualStrings("fs/libfs.c", descriptor.anchor);
    try std.testing.expect(descriptor.provides_statfs_defaults);
    try std.testing.expect(descriptor.provides_lookup_policy);
    try std.testing.expect(descriptor.provides_buffer_copy_helpers);
    try std.testing.expect(descriptor.provides_offset_seek_helpers);
    try std.testing.expect(descriptor.provides_directory_emit_planning);
    try std.testing.expect(!descriptor.touches_live_dcache);
    try std.testing.expect(!descriptor.touches_live_inode_state);

    var starter_landed_count: usize = 0;
    var ready_next_count: usize = 0;
    var blocked_count: usize = 0;
    var saw_build_gate = false;
    var saw_make_target = false;
    var saw_starter = false;
    var saw_tests = false;
    var saw_slice_note = false;
    var saw_reviewability_gate = false;
    var saw_survey_note = false;
    var saw_offset_followup = false;
    var saw_emit_followup = false;
    var saw_transaction_followup = false;

    for (manifest.gaps, 0..) |gap, i| {
        try std.testing.expect(gap.id.len > 0);
        try std.testing.expect(gap.kind.len > 0);
        try std.testing.expect(gap.why_now.len > 0);
        try std.testing.expect(isAllowedStatus(gap.status));

        if (std.mem.eql(u8, gap.status, "starter_landed")) {
            starter_landed_count += 1;
        } else if (std.mem.eql(u8, gap.status, "ready_next")) {
            ready_next_count += 1;
        } else if (std.mem.eql(u8, gap.status, "blocked_on_vfs_state")) {
            blocked_count += 1;
        }

        if (std.mem.eql(u8, gap.id, "phase13-build-gate")) {
            saw_build_gate = true;
            try std.testing.expectEqualStrings("zigux/tests/phase13_build.zig", gap.zigux_destination);
        }
        if (std.mem.eql(u8, gap.id, "phase13-make-target")) {
            saw_make_target = true;
            try std.testing.expectEqualStrings("zigux/Makefile", gap.zigux_destination);
        }
        if (std.mem.eql(u8, gap.id, "phase13-libfs-starter")) {
            saw_starter = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("filesystem_helper_surface", gap.kind);
            try std.testing.expectEqualStrings("fs/libfs.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "simple_statfs") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "simple_lookup") != null);
        }
        if (std.mem.eql(u8, gap.id, "phase13-libfs-tests")) {
            saw_tests = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("zigux/tests/phase13_libfs.zig", gap.zigux_destination);
        }
        if (std.mem.eql(u8, gap.id, "phase13-libfs-slice-note")) {
            saw_slice_note = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("Documentation/zigux/phase13-libfs-slice.md", gap.zigux_destination);
        }
        if (std.mem.eql(u8, gap.id, "phase13-libfs-reviewability-gate")) {
            saw_reviewability_gate = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("zigux/tests/phase13_libfs_reviewability.zig", gap.zigux_destination);
        }
        if (std.mem.eql(u8, gap.id, "phase13-libfs-survey-note")) {
            saw_survey_note = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("Documentation/zigux/phase13-libfs-survey.md", gap.zigux_destination);
        }
        if (std.mem.eql(u8, gap.id, "phase13-libfs-offset-seek-helper")) {
            saw_offset_followup = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("filesystem_helper_surface", gap.kind);
            try std.testing.expectEqualStrings("fs/libfs.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "dcache_dir_lseek") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "offset_dir_llseek") != null);
        }
        if (std.mem.eql(u8, gap.id, "phase13-libfs-directory-emit-helper")) {
            saw_emit_followup = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("filesystem_helper_surface", gap.kind);
            try std.testing.expectEqualStrings("fs/libfs.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "dcache_readdir") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "dir_emit_dots") != null);
        }
        if (std.mem.eql(u8, gap.id, "phase13-libfs-transaction-buffer-followup")) {
            saw_transaction_followup = true;
            try std.testing.expectEqualStrings("ready_next", gap.status);
            try std.testing.expectEqualStrings("filesystem_helper_surface", gap.kind);
            try std.testing.expectEqualStrings("fs/libfs.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "simple_transaction") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "staging buffer") != null);
        }

        for (manifest.gaps[i + 1 ..]) |other| {
            try std.testing.expect(!std.mem.eql(u8, gap.id, other.id));
        }
    }

    try std.testing.expectEqual(@as(usize, 9), starter_landed_count);
    try std.testing.expectEqual(@as(usize, 1), ready_next_count);
    try std.testing.expectEqual(@as(usize, 0), blocked_count);
    try std.testing.expect(saw_build_gate);
    try std.testing.expect(saw_make_target);
    try std.testing.expect(saw_starter);
    try std.testing.expect(saw_tests);
    try std.testing.expect(saw_slice_note);
    try std.testing.expect(saw_reviewability_gate);
    try std.testing.expect(saw_survey_note);
    try std.testing.expect(saw_offset_followup);
    try std.testing.expect(saw_emit_followup);
    try std.testing.expect(saw_transaction_followup);
}
