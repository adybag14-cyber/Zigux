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
