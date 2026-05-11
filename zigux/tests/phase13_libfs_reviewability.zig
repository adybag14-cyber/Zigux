const std = @import("std");
const libfs = @import("libfs");

test "descriptor keeps the current bounded helper surface explicit" {
    const descriptor = libfs.LibfsHelperLab.descriptor();

    try std.testing.expectEqualStrings("libfs_helper_lab", descriptor.name);
    try std.testing.expectEqualStrings("fs/libfs.c", descriptor.anchor);
    try std.testing.expect(descriptor.provides_positive_entry_classification);
    try std.testing.expect(descriptor.provides_directory_emptiness_planning);
    try std.testing.expect(descriptor.provides_transaction_release_planning);
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
