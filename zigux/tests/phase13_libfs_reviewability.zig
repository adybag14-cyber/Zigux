const std = @import("std");
const libfs = @import("libfs");

const SurveySummary = struct {
    libfs_c_lines: usize,
    preexisting_phase13_build_present: bool,
    preexisting_phase13_make_target_present: bool,
    preexisting_fs_libfs_zig_present: bool,
    preexisting_phase13_libfs_test_present: bool,
    preexisting_phase13_libfs_addressability_test_present: bool,
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

fn readPacketFile(path: []const u8, allocator: std.mem.Allocator) ![]u8 {
    var io_instance: std.Io.Threaded = .init(allocator, .{});
    defer io_instance.deinit();
    return std.Io.Dir.cwd().readFileAlloc(io_instance.io(), path, allocator, .limited(32 * 1024));
}

fn contains(haystack: []const u8, needle: []const u8) bool {
    return std.mem.indexOf(u8, haystack, needle) != null;
}

test "phase13 libfs reviewability gate records the landed helper surfaces and remaining cursor gap" {
    const manifest_json = try readPacketFile(
        "zigux/tests/phase13_libfs_manifest.json",
        std.testing.allocator,
    );
    defer std.testing.allocator.free(manifest_json);

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{});
    defer parsed.deinit();

    const manifest = parsed.value;
    try std.testing.expectEqualStrings("P13-L01", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 13", manifest.phase);
    try std.testing.expectEqualStrings("fs/libfs.c", manifest.anchor);
    try std.testing.expectEqualStrings("master-reviewability", manifest.surveyed_commit);
    try std.testing.expectEqual(@as(usize, 3), manifest.roadmap_destinations.len);
    try std.testing.expect(manifest.survey_summary.libfs_c_lines >= 2300);
    try std.testing.expect(manifest.survey_summary.preexisting_phase13_build_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase13_make_target_present);
    try std.testing.expect(manifest.survey_summary.preexisting_fs_libfs_zig_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase13_libfs_test_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase13_libfs_addressability_test_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase13_slice_note_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase13_reviewability_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase13_survey_note_present);
    try std.testing.expectEqual(@as(usize, 19), manifest.gaps.len);

    const descriptor = libfs.LibFsHelperLab.descriptor();
    try std.testing.expectEqualStrings("fs/libfs.c", descriptor.anchor);
    try std.testing.expect(descriptor.provides_statfs_defaults);
    try std.testing.expect(descriptor.provides_lookup_policy);
    try std.testing.expect(descriptor.provides_buffer_copy_helpers);
    try std.testing.expect(descriptor.provides_offset_seek_helpers);
    try std.testing.expect(descriptor.provides_directory_emit_planning);
    try std.testing.expect(descriptor.provides_directory_cursor_open_planning);
    try std.testing.expect(descriptor.provides_directory_cursor_close_planning);
    try std.testing.expect(descriptor.provides_directory_cursor_reposition_planning);
    try std.testing.expect(descriptor.provides_transaction_buffer_planning);
    try std.testing.expect(descriptor.provides_transaction_publish_planning);
    try std.testing.expect(descriptor.provides_transaction_release_planning);
    try std.testing.expect(descriptor.provides_addressability_planning);
    try std.testing.expect(descriptor.provides_simple_open_planning);
    try std.testing.expect(descriptor.provides_simple_dir_operations_wrapper);
    try std.testing.expect(!descriptor.touches_live_dcache);
    try std.testing.expect(!descriptor.touches_live_inode_state);

    var starter_landed_count: usize = 0;
    var blocked_count: usize = 0;
    var helper_surface_count: usize = 0;
    var saw_dir_close = false;
    var saw_cursor_reposition = false;
    var saw_simple_dir_operations_wrapper = false;
    var saw_cursor_blocker = false;

    for (manifest.gaps) |gap| {
        try std.testing.expect(gap.id.len > 0);
        try std.testing.expect(gap.kind.len > 0);
        try std.testing.expect(gap.why_now.len > 0);

        if (std.mem.eql(u8, gap.status, "starter_landed")) starter_landed_count += 1;
        if (std.mem.eql(u8, gap.status, "blocked_on_vfs_state")) blocked_count += 1;
        if (std.mem.eql(u8, gap.kind, "filesystem_helper_surface")) helper_surface_count += 1;

        if (std.mem.eql(u8, gap.id, "phase13-libfs-starter")) {
            try std.testing.expect(contains(gap.why_now, "helper packet"));
            try std.testing.expect(contains(gap.why_now, "simple_statfs()"));
            try std.testing.expect(contains(gap.why_now, "simple_lookup()"));
        }
        if (std.mem.eql(u8, gap.id, "phase13-libfs-tests")) {
            try std.testing.expectEqualStrings("zigux/tests/phase13_libfs.zig", gap.zigux_destination);
            try std.testing.expect(contains(gap.why_now, "Dedicated libfs helper tests"));
            try std.testing.expect(contains(gap.why_now, "cursor-reposition planner"));
            try std.testing.expect(contains(gap.why_now, "simple_open()"));
        }
        if (std.mem.eql(u8, gap.id, "phase13-libfs-reviewability-gate")) {
            try std.testing.expectEqualStrings("zigux/tests/phase13_libfs_reviewability.zig", gap.zigux_destination);
            try std.testing.expect(contains(gap.why_now, "current helper packet"));
            try std.testing.expect(contains(gap.why_now, "focused addressability shard"));
        }
        if (std.mem.eql(u8, gap.id, "phase13-libfs-offset-seek-helper")) {
            try std.testing.expect(contains(gap.why_now, "dcache_dir_lseek()"));
            try std.testing.expect(contains(gap.why_now, "offset_dir_llseek()"));
        }
        if (std.mem.eql(u8, gap.id, "phase13-libfs-directory-emit-helper")) {
            try std.testing.expect(contains(gap.why_now, "dcache_readdir()"));
            try std.testing.expect(contains(gap.why_now, "dir_emit_dots()"));
        }
        if (std.mem.eql(u8, gap.id, "phase13-libfs-transaction-buffer-helper")) {
            try std.testing.expect(contains(gap.why_now, "simple_transaction_get()"));
            try std.testing.expect(contains(gap.why_now, "single-write-per-open"));
        }
        if (std.mem.eql(u8, gap.id, "phase13-libfs-transaction-publish-helper")) {
            try std.testing.expect(contains(gap.why_now, "simple_transaction_set()"));
            try std.testing.expect(contains(gap.why_now, "publish bookkeeping"));
        }
        if (std.mem.eql(u8, gap.id, "phase13-libfs-transaction-release-helper")) {
            try std.testing.expect(contains(gap.why_now, "simple_transaction_release()"));
            try std.testing.expect(contains(gap.why_now, "release bookkeeping"));
        }
        if (std.mem.eql(u8, gap.id, "phase13-libfs-dcache-dir-open-helper")) {
            try std.testing.expect(contains(gap.why_now, "dcache_dir_open()"));
            try std.testing.expect(contains(gap.why_now, "private_data"));
        }
        if (std.mem.eql(u8, gap.id, "phase13-libfs-dcache-dir-close-helper")) {
            saw_dir_close = true;
            try std.testing.expectEqualStrings("fs/libfs.zig", gap.zigux_destination);
            try std.testing.expect(contains(gap.why_now, "dcache_dir_close()"));
            try std.testing.expect(contains(gap.why_now, "null-cursor"));
        }
        if (std.mem.eql(u8, gap.id, "phase13-libfs-cursor-reposition-helper")) {
            saw_cursor_reposition = true;
            try std.testing.expectEqualStrings("fs/libfs.zig", gap.zigux_destination);
            try std.testing.expect(contains(gap.why_now, "hlist_del_init()"));
            try std.testing.expect(contains(gap.why_now, "before-target"));
            try std.testing.expect(contains(gap.why_now, "behind-target"));
        }
        if (std.mem.eql(u8, gap.id, "phase13-libfs-addressability-helper")) {
            try std.testing.expect(contains(gap.why_now, "generic_check_addressable()"));
            try std.testing.expect(contains(gap.why_now, "sector-addressability"));
        }
        if (std.mem.eql(u8, gap.id, "phase13-libfs-simple-open-helper")) {
            try std.testing.expect(contains(gap.why_now, "simple_open()"));
            try std.testing.expect(contains(gap.why_now, "inode->i_private"));
        }
        if (std.mem.eql(u8, gap.id, "phase13-libfs-simple-dir-operations-wrapper")) {
            saw_simple_dir_operations_wrapper = true;
            try std.testing.expectEqualStrings("fs/libfs.zig", gap.zigux_destination);
            try std.testing.expect(contains(gap.why_now, "simple_dir_operations"));
            try std.testing.expect(contains(gap.why_now, "dcache_dir_open()"));
            try std.testing.expect(contains(gap.why_now, "noop_fsync()"));
        }
        if (std.mem.eql(u8, gap.id, "phase13-libfs-dcache-cursor-helpers")) {
            saw_cursor_blocker = true;
            try std.testing.expectEqualStrings("blocked_on_vfs_state", gap.status);
            try std.testing.expect(contains(gap.why_now, "dcache_readdir()"));
            try std.testing.expect(contains(gap.why_now, "lock-ordering"));
        }
    }

    try std.testing.expectEqual(@as(usize, 18), starter_landed_count);
    try std.testing.expectEqual(@as(usize, 1), blocked_count);
    try std.testing.expectEqual(@as(usize, 13), helper_surface_count);
    try std.testing.expect(saw_dir_close);
    try std.testing.expect(saw_cursor_reposition);
    try std.testing.expect(saw_simple_dir_operations_wrapper);
    try std.testing.expect(saw_cursor_blocker);

    const survey_note = try readPacketFile(
        "Documentation/zigux/phase13-libfs-survey.md",
        std.testing.allocator,
    );
    defer std.testing.allocator.free(survey_note);

    try std.testing.expect(contains(survey_note, "PHASE13_SLICE=libfs-helper-reviewability-packet"));
    try std.testing.expect(contains(survey_note, "landed `fs/libfs.zig` helper packet"));
    try std.testing.expect(contains(survey_note, "current helper packet stays intentionally bounded"));
    try std.testing.expect(contains(survey_note, "landed `phase13-make-target`"));
    try std.testing.expect(contains(survey_note, "landed `phase13-libfs-starter`"));
    try std.testing.expect(contains(survey_note, "landed `phase13-libfs-tests`"));
    try std.testing.expect(contains(survey_note, "landed `phase13-libfs-dcache-dir-open-helper`"));
    try std.testing.expect(contains(survey_note, "landed `phase13-libfs-dcache-dir-close-helper`"));
    try std.testing.expect(contains(survey_note, "landed `phase13-libfs-cursor-reposition-helper`"));
    try std.testing.expect(contains(survey_note, "landed `phase13-libfs-transaction-release-helper`"));
    try std.testing.expect(contains(survey_note, "landed `phase13-libfs-addressability-helper`"));
    try std.testing.expect(contains(survey_note, "landed `phase13-libfs-simple-open-helper`"));
    try std.testing.expect(contains(survey_note, "landed `phase13-libfs-simple-dir-operations-wrapper`"));
    try std.testing.expect(contains(survey_note, "blocked `phase13-libfs-dcache-cursor-helpers`"));
    try std.testing.expect(contains(survey_note, "focused `zigux/tests/phase13_libfs_addressability.zig` file"));
    try std.testing.expect(contains(survey_note, "focused addressability proof"));
    try std.testing.expect(contains(survey_note, "Documentation/zigux/phase13-roadmap-traceability.md"));
    try std.testing.expect(contains(survey_note, "dedicated helper-local evidence rather than a ninth shared replay step"));
    try std.testing.expect(contains(survey_note, "shared eight-test `phase13_build.zig` route"));
    try std.testing.expect(!contains(survey_note, "small `fs/libfs.zig` starter"));
    try std.testing.expect(!contains(survey_note, "current starter stays intentionally narrow"));
    try std.testing.expect(!contains(survey_note, "landed `phase13-libfs-helper-starter`"));
    try std.testing.expect(!contains(survey_note, "landed `phase13-libfs-test-gate`"));
    try std.testing.expect(!contains(survey_note, "blocked `phase13-libfs-inode-and-pseudofs-lifecycle`"));

    const traceability_note = try readPacketFile(
        "Documentation/zigux/phase13-roadmap-traceability.md",
        std.testing.allocator,
    );
    defer std.testing.allocator.free(traceability_note);

    try std.testing.expect(contains(traceability_note, "## Libfs lane traceability"));
    try std.testing.expect(contains(traceability_note, "zigux/tests/phase13_libfs_reviewability.zig"));
    try std.testing.expect(contains(traceability_note, "cursor-reposition bookkeeping"));
    try std.testing.expect(contains(traceability_note, "transaction acquire, publish, and release helpers"));
    try std.testing.expect(contains(traceability_note, "`generic_check_addressable()` planner"));
    try std.testing.expect(contains(traceability_note, "`simple_open()` private-data handoff"));
    try std.testing.expect(contains(traceability_note, "`simple_dir_operations` wrapper"));
    try std.testing.expect(contains(traceability_note, "deeper `dcache_readdir()` cursor-resume packet"));
    try std.testing.expect(!contains(traceability_note, "A pure `simple_open()` private-data handoff planner is the best next helper-first candidate"));
    try std.testing.expect(contains(traceability_note, "helper-first filesystem planning"));
}
