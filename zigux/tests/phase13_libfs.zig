const std = @import("std");
const libfs = @import("libfs");

test "positive child classification stays bounded" {
    try std.testing.expect(!libfs.LibfsHelperLab.isPositiveEntry(.{ .kind = .dot }));
    try std.testing.expect(!libfs.LibfsHelperLab.isPositiveEntry(.{ .kind = .child, .inode_present = false }));
    try std.testing.expect(libfs.LibfsHelperLab.isPositiveEntry(.{ .kind = .child, .inode_present = true }));
}

test "simple empty planning reports first blocking child" {
    const entries = [_]libfs.DirectoryEntry{
        .{ .kind = .dot },
        .{ .kind = .dotdot },
        .{ .kind = .child, .inode_present = false },
        .{ .kind = .child, .inode_present = true },
    };

    const plan = libfs.LibfsHelperLab.planSimpleEmpty(&entries);
    try std.testing.expectEqualStrings("fs/libfs.c", plan.anchor);
    try std.testing.expect(!plan.only_trivial_entries);
    try std.testing.expectEqual(@as(?usize, 3), plan.first_blocking_index);
    try std.testing.expect(plan.saw_negative_child);
}

test "simple empty planning records truncation at lane bound" {
    var entries = [_]libfs.DirectoryEntry{.{ .kind = .dot }} ** (libfs.max_directory_entries + 1);
    entries[libfs.max_directory_entries] = .{ .kind = .child, .inode_present = true };

    const plan = libfs.LibfsHelperLab.planSimpleEmpty(&entries);
    try std.testing.expect(plan.only_trivial_entries);
    try std.testing.expectEqual(@as(usize, libfs.max_directory_entries), plan.examined_entries);
    try std.testing.expect(plan.truncated);
}

test "simple lookup planning keeps the negative-dentry install boundary explicit" {
    const addressable = libfs.LibfsHelperLab.planSimpleLookup(libfs.name_max);
    const oversized = libfs.LibfsHelperLab.planSimpleLookup(libfs.name_max + 1);

    try std.testing.expectEqualStrings("fs/libfs.c", addressable.anchor);
    try std.testing.expectEqual(libfs.LookupMode.negative_dentry_install, addressable.mode);
    try std.testing.expect(addressable.addressable);
    try std.testing.expect(addressable.installs_negative_dentry);

    try std.testing.expectEqual(libfs.LookupMode.name_too_long, oversized.mode);
    try std.testing.expect(!oversized.addressable);
    try std.testing.expect(!oversized.installs_negative_dentry);
}

test "offset seek planning keeps the bounded window and sentinel paths explicit" {
    const window_plan = libfs.LibfsHelperLab.planOffsetDirectorySeek(0, libfs.dir_offset_first + 4, .set);
    const sentinel_plan = libfs.LibfsHelperLab.planOffsetDirectorySeek(0, libfs.dir_offset_end_of_directory, .set);
    const invalid_plan = libfs.LibfsHelperLab.planOffsetDirectorySeek(0, -1, .set);

    try std.testing.expectEqual(libfs.OffsetSeekStatus.ok, window_plan.status);
    try std.testing.expect(window_plan.points_at_real_entry_window);
    try std.testing.expect(!window_plan.points_at_end_of_directory);

    try std.testing.expectEqual(libfs.OffsetSeekStatus.ok, sentinel_plan.status);
    try std.testing.expect(!sentinel_plan.points_at_real_entry_window);
    try std.testing.expect(sentinel_plan.points_at_end_of_directory);

    try std.testing.expectEqual(libfs.OffsetSeekStatus.negative_offset, invalid_plan.status);
    try std.testing.expectEqual(@as(?i64, null), invalid_plan.resolved_offset);
}

test "offset readdir planning keeps emit-dots gating and eod handoff explicit" {
    const blocked = libfs.LibfsHelperLab.planOffsetReaddir(libfs.dir_offset_first + 4, false);
    try std.testing.expectEqualStrings("fs/libfs.c", blocked.anchor);
    try std.testing.expectEqual(libfs.OffsetReaddirStatus.ok, blocked.status);
    try std.testing.expectEqual(libfs.OffsetReaddirMode.blocked_on_emit_dots, blocked.mode.?);
    try std.testing.expect(blocked.returns_zero);
    try std.testing.expect(blocked.requires_dir_emit_dots);
    try std.testing.expect(!blocked.enters_offset_iteration);
    try std.testing.expect(blocked.keeps_current_pos);
    try std.testing.expect(!blocked.treats_end_of_directory_as_terminal);

    const active = libfs.LibfsHelperLab.planOffsetReaddir(libfs.dir_offset_first + 4, true);
    try std.testing.expectEqual(libfs.OffsetReaddirMode.ready_to_iterate, active.mode.?);
    try std.testing.expect(active.enters_offset_iteration);

    const terminal = libfs.LibfsHelperLab.planOffsetReaddir(libfs.dir_offset_end_of_directory, true);
    try std.testing.expectEqual(libfs.OffsetReaddirMode.ready_at_end_of_directory, terminal.mode.?);
    try std.testing.expect(!terminal.enters_offset_iteration);
    try std.testing.expect(terminal.keeps_current_pos);
    try std.testing.expect(terminal.treats_end_of_directory_as_terminal);

    const invalid = libfs.LibfsHelperLab.planOffsetReaddir(-1, true);
    try std.testing.expectEqual(libfs.OffsetReaddirStatus.negative_position, invalid.status);
    try std.testing.expectEqual(@as(?libfs.OffsetReaddirMode, null), invalid.mode);
}

test "transaction release planning frees staged private data when present" {
    const plan = libfs.LibfsHelperLab.simpleTransactionReleasePlan(true);

    try std.testing.expect(plan.private_data_present);
    try std.testing.expect(plan.frees_page_backed_private_data);
    try std.testing.expect(plan.clears_private_data);
    try std.testing.expect(plan.returns_zero);
}

test "transaction release planning leaves the null-private-data no-op path explicit" {
    const plan = libfs.LibfsHelperLab.simpleTransactionReleasePlan(false);

    try std.testing.expect(!plan.private_data_present);
    try std.testing.expect(!plan.frees_page_backed_private_data);
    try std.testing.expect(!plan.clears_private_data);
    try std.testing.expect(plan.returns_zero);
}
