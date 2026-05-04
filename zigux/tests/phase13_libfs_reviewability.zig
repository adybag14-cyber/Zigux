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

const expected_surveyed_commit = "a8bb936df1520e7be16d3fdf9ee1875de398ead6";

fn isAllowedStatus(status: []const u8) bool {
    return std.mem.eql(u8, status, "starter_landed") or
        std.mem.eql(u8, status, "ready_next") or
        std.mem.eql(u8, status, "blocked_on_vfs_state");
}

test "phase13 libfs manifest records the landed addressability slice and the remaining blocked helpers" {
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
    const survey_note = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase13-libfs-survey.md",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(survey_note);
    const traceability_note = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase13-roadmap-traceability.md",
        std.testing.allocator,
        .limited(64 * 1024),
    );
    defer std.testing.allocator.free(traceability_note);

    try std.testing.expectEqualStrings("P13-L04", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 13", manifest.phase);
    try std.testing.expectEqualStrings("fs/libfs.c", manifest.anchor);
    try std.testing.expectEqualStrings(expected_surveyed_commit, manifest.surveyed_commit);
    try std.testing.expectEqual(@as(usize, 3), manifest.roadmap_destinations.len);
    try std.testing.expect(manifest.survey_summary.libfs_c_lines >= 2300);
    try std.testing.expect(manifest.survey_summary.preexisting_phase13_build_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase13_make_target_present);
    try std.testing.expect(manifest.survey_summary.preexisting_fs_libfs_zig_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase13_libfs_test_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase13_slice_note_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase13_reviewability_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase13_survey_note_present);
    try std.testing.expectEqual(@as(usize, 18), manifest.gaps.len);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, expected_surveyed_commit) != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "PHASE13_SURVEYED_COMMIT=") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "generic_check_addressable()") != null);
    try std.testing.expect(std.mem.indexOf(u8, traceability_note, expected_surveyed_commit) != null);
    try std.testing.expect(std.mem.indexOf(u8, traceability_note, "`fs/libfs.c`") != null);
    try std.testing.expect(std.mem.indexOf(u8, traceability_note, "phase13-libfs-addressability-helper") != null);
    try std.testing.expect(std.mem.indexOf(u8, traceability_note, "generic_check_addressable()") != null);
    try std.testing.expect(std.mem.indexOf(u8, traceability_note, "phase13-libfs-dcache-dir-close-release-bookkeeping") != null);
    try std.testing.expect(std.mem.indexOf(u8, traceability_note, "phase13-libfs-simple-open-private-data-planning") != null);
    try std.testing.expect(std.mem.indexOf(u8, traceability_note, "phase13-libfs-dcache-cursor-helpers") != null);
    try std.testing.expect(std.mem.indexOf(u8, traceability_note, "phase13-libfs-inode-and-pseudofs-lifecycle") != null);
    try std.testing.expect(std.mem.indexOf(u8, traceability_note, "broader cursor traversal") != null);
    try std.testing.expect(std.mem.indexOf(u8, traceability_note, "pseudo-filesystem ownership") != null);

    const descriptor = libfs.LibFsHelperLab.descriptor();
    try std.testing.expectEqualStrings("fs/libfs.c", descriptor.anchor);
    try std.testing.expect(descriptor.provides_statfs_defaults);
    try std.testing.expect(descriptor.provides_lookup_policy);
    try std.testing.expect(descriptor.provides_buffer_copy_helpers);
    try std.testing.expect(descriptor.provides_offset_seek_helpers);
    try std.testing.expect(descriptor.provides_directory_emit_planning);
    try std.testing.expect(descriptor.provides_directory_cursor_preconditions);
    try std.testing.expect(descriptor.provides_directory_cursor_reposition_planning);
    try std.testing.expect(descriptor.provides_directory_close_planning);
    try std.testing.expect(descriptor.provides_transaction_buffer_planning);
    try std.testing.expect(descriptor.provides_transaction_read_release_planning);
    try std.testing.expect(descriptor.provides_open_private_data_planning);
    try std.testing.expect(descriptor.provides_addressability_planning);
    try std.testing.expect(!descriptor.touches_live_dcache);
    try std.testing.expect(!descriptor.touches_live_inode_state);

    var starter_landed_count: usize = 0;
    var ready_next_count: usize = 0;
    var blocked_count: usize = 0;
    var saw_close_release = false;
    var saw_simple_open = false;
    var saw_addressability_helper = false;
    var saw_blocked_cursor_helpers = false;
    var saw_blocked_inode_lifecycle = false;

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

        if (std.mem.eql(u8, gap.id, "phase13-libfs-dcache-dir-close-release-bookkeeping")) {
            saw_close_release = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("fs/libfs.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "dcache_dir_close") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "dput(file->private_data)") != null);
        }
        if (std.mem.eql(u8, gap.id, "phase13-libfs-dcache-cursor-reposition-bookkeeping")) {
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("fs/libfs.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "exported descriptor") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "cursor-reposition planning") != null);
        }
        if (std.mem.eql(u8, gap.id, "phase13-libfs-simple-open-private-data-planning")) {
            saw_simple_open = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("fs/libfs.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "simple_open()") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "inode->i_private") != null);
        }
        if (std.mem.eql(u8, gap.id, "phase13-libfs-addressability-helper")) {
            saw_addressability_helper = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("fs/libfs.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "generic_check_addressable()") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "block-size") != null);
        }
        if (std.mem.eql(u8, gap.id, "phase13-libfs-dcache-cursor-helpers")) {
            saw_blocked_cursor_helpers = true;
            try std.testing.expectEqualStrings("blocked_on_vfs_state", gap.status);
        }
        if (std.mem.eql(u8, gap.id, "phase13-libfs-inode-and-pseudofs-lifecycle")) {
            saw_blocked_inode_lifecycle = true;
            try std.testing.expectEqualStrings("blocked_on_vfs_state", gap.status);
        }

        for (manifest.gaps[i + 1 ..]) |other| {
            try std.testing.expect(!std.mem.eql(u8, gap.id, other.id));
        }
    }

    try std.testing.expectEqual(@as(usize, 16), starter_landed_count);
    try std.testing.expectEqual(@as(usize, 0), ready_next_count);
    try std.testing.expectEqual(@as(usize, 2), blocked_count);
    try std.testing.expect(saw_close_release);
    try std.testing.expect(saw_simple_open);
    try std.testing.expect(saw_addressability_helper);
    try std.testing.expect(saw_blocked_cursor_helpers);
    try std.testing.expect(saw_blocked_inode_lifecycle);
}
