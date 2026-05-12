const std = @import("std");
const libfs = @import("libfs");

test "descriptor keeps the current bounded helper surface explicit" {
    const descriptor = libfs.LibfsHelperLab.descriptor();

    try std.testing.expectEqualStrings("libfs_helper_lab", descriptor.name);
    try std.testing.expectEqualStrings("fs/libfs.c", descriptor.anchor);
    try std.testing.expect(descriptor.provides_positive_entry_classification);
    try std.testing.expect(descriptor.provides_directory_emptiness_planning);
    try std.testing.expect(descriptor.provides_lookup_planning);
    try std.testing.expect(descriptor.provides_transaction_release_planning);
    try std.testing.expect(descriptor.provides_offset_seek_planning);
    try std.testing.expect(descriptor.provides_offset_readdir_planning);
    try std.testing.expect(descriptor.provides_offset_rename_planning);
    try std.testing.expect(!descriptor.touches_live_dcache);
    try std.testing.expect(!descriptor.touches_live_inode_state);
}

test "simple empty planner stays negative-child tolerant and truncation-bounded" {
    var entries = [_]libfs.DirectoryEntry{.{ .kind = .dot }} ** (libfs.max_directory_entries + 1);
    entries[1] = .{ .kind = .dotdot };
    entries[2] = .{ .kind = .child, .inode_present = false };
    entries[libfs.max_directory_entries] = .{ .kind = .child, .inode_present = true };

    const plan = libfs.LibfsHelperLab.planSimpleEmpty(&entries);
    try std.testing.expectEqualStrings("fs/libfs.c", plan.anchor);
    try std.testing.expect(plan.only_trivial_entries);
    try std.testing.expectEqual(@as(?usize, null), plan.first_blocking_index);
    try std.testing.expect(plan.saw_negative_child);
    try std.testing.expectEqual(@as(usize, libfs.max_directory_entries), plan.examined_entries);
    try std.testing.expect(plan.truncated);
}

test "lookup offset seek and offset readdir helpers stay reviewable without implying live VFS mutation" {
    const addressable_lookup = libfs.LibfsHelperLab.planSimpleLookup(libfs.name_max);
    const oversized_lookup = libfs.LibfsHelperLab.planSimpleLookup(libfs.name_max + 1);
    const relative_seek = libfs.LibfsHelperLab.planOffsetDirectorySeek(libfs.dir_offset_first, -1, .cur);
    const unsupported_seek = libfs.LibfsHelperLab.planOffsetDirectorySeek(libfs.dir_offset_first, 8, .unsupported);
    const blocked_readdir = libfs.LibfsHelperLab.planOffsetReaddir(libfs.dir_offset_first + 1, false);
    const terminal_readdir = libfs.LibfsHelperLab.planOffsetReaddir(libfs.dir_offset_end_of_directory, true);

    try std.testing.expectEqualStrings("fs/libfs.c", addressable_lookup.anchor);
    try std.testing.expect(addressable_lookup.installs_negative_dentry);
    try std.testing.expectEqual(libfs.LookupMode.name_too_long, oversized_lookup.mode);
    try std.testing.expect(!oversized_lookup.installs_negative_dentry);

    try std.testing.expectEqual(libfs.OffsetSeekStatus.ok, relative_seek.status);
    try std.testing.expectEqual(@as(?i64, 1), relative_seek.resolved_offset);
    try std.testing.expect(!relative_seek.points_at_real_entry_window);
    try std.testing.expectEqual(libfs.OffsetSeekStatus.unsupported_whence, unsupported_seek.status);
    try std.testing.expectEqual(@as(?i64, null), unsupported_seek.resolved_offset);

    try std.testing.expectEqual(libfs.OffsetReaddirStatus.ok, blocked_readdir.status);
    try std.testing.expectEqual(libfs.OffsetReaddirMode.blocked_on_emit_dots, blocked_readdir.mode.?);
    try std.testing.expect(!blocked_readdir.enters_offset_iteration);
    try std.testing.expect(blocked_readdir.keeps_current_pos);

    try std.testing.expectEqual(libfs.OffsetReaddirStatus.ok, terminal_readdir.status);
    try std.testing.expectEqual(libfs.OffsetReaddirMode.ready_at_end_of_directory, terminal_readdir.mode.?);
    try std.testing.expect(!terminal_readdir.enters_offset_iteration);
    try std.testing.expect(terminal_readdir.treats_end_of_directory_as_terminal);
}

test "transaction release planner stays helper-only and unconditional-zero" {
    const release_with_private = libfs.LibfsHelperLab.simpleTransactionReleasePlan(true);
    const release_without_private = libfs.LibfsHelperLab.simpleTransactionReleasePlan(false);

    try std.testing.expectEqualStrings("fs/libfs.c", release_with_private.anchor);
    try std.testing.expect(release_with_private.private_data_present);
    try std.testing.expect(release_with_private.frees_page_backed_private_data);
    try std.testing.expect(release_with_private.clears_private_data);
    try std.testing.expect(release_with_private.returns_zero);

    try std.testing.expect(!release_without_private.private_data_present);
    try std.testing.expect(!release_without_private.frees_page_backed_private_data);
    try std.testing.expect(!release_without_private.clears_private_data);
    try std.testing.expect(release_without_private.returns_zero);
}
