const std = @import("std");

pub const page_size: u32 = 4096;
pub const name_max: u32 = 255;
pub const simple_transaction_limit: usize = page_size;

pub const max_directory_entries: usize = 128;
pub const dir_offset_first: i64 = 2;
pub const dir_offset_end_of_directory: i64 = std.math.maxInt(i32);

pub const ModuleDescriptor = struct {
    name: []const u8,
    anchor: []const u8,
    provides_positive_entry_classification: bool,
    provides_directory_emptiness_planning: bool,
    provides_lookup_planning: bool,
    provides_transaction_release_planning: bool,
    provides_offset_seek_planning: bool,
    touches_live_dcache: bool,
    touches_live_inode_state: bool,
};

pub const EntryKind = enum {
    dot,
    dotdot,
    child,
};

pub const DirectoryEntry = struct {
    kind: EntryKind,
    inode_present: bool = true,
};

pub const DirectoryEmptinessPlan = struct {
    anchor: []const u8,
    examined_entries: usize,
    only_trivial_entries: bool,
    first_blocking_index: ?usize,
    saw_negative_child: bool,
    truncated: bool,
};

pub const LookupMode = enum {
    negative_dentry_install,
    name_too_long,
};

pub const LookupPlan = struct {
    anchor: []const u8,
    name_length: usize,
    mode: LookupMode,
    addressable: bool,
    installs_negative_dentry: bool,
};

pub const TransactionReleasePlan = struct {
    anchor: []const u8,
    private_data_present: bool,
    frees_page_backed_private_data: bool,
    clears_private_data: bool,
    returns_zero: bool,
};

pub const OffsetSeekWhence = enum {
    set,
    cur,
    unsupported,
};

pub const OffsetSeekStatus = enum {
    ok,
    negative_offset,
    unsupported_whence,
};

pub const OffsetDirectorySeekPlan = struct {
    anchor: []const u8,
    start_position: i64,
    requested_offset: i64,
    whence: OffsetSeekWhence,
    resolved_offset: ?i64,
    status: OffsetSeekStatus,
    points_at_real_entry_window: bool,
    points_at_end_of_directory: bool,
};

pub const LibfsHelperLab = struct {
    pub fn descriptor() ModuleDescriptor {
        return .{
            .name = "libfs_helper_lab",
            .anchor = "fs/libfs.c",
            .provides_positive_entry_classification = true,
            .provides_directory_emptiness_planning = true,
            .provides_lookup_planning = true,
            .provides_transaction_release_planning = true,
            .provides_offset_seek_planning = true,
            .touches_live_dcache = false,
            .touches_live_inode_state = false,
        };
    }

    pub fn isPositiveEntry(entry: DirectoryEntry) bool {
        return entry.kind == .child and entry.inode_present;
    }

    pub fn planSimpleEmpty(entries: []const DirectoryEntry) DirectoryEmptinessPlan {
        const bounded_len = @min(entries.len, max_directory_entries);
        var plan = DirectoryEmptinessPlan{
            .anchor = descriptor().anchor,
            .examined_entries = bounded_len,
            .only_trivial_entries = true,
            .first_blocking_index = null,
            .saw_negative_child = false,
            .truncated = entries.len > max_directory_entries,
        };

        for (entries[0..bounded_len], 0..) |entry, i| {
            switch (entry.kind) {
                .dot, .dotdot => continue,
                .child => {
                    if (entry.inode_present) {
                        plan.only_trivial_entries = false;
                        plan.first_blocking_index = i;
                        return plan;
                    }
                    plan.saw_negative_child = true;
                },
            }
        }

        return plan;
    }

    pub fn planSimpleLookup(name_length: usize) LookupPlan {
        const addressable = name_length <= name_max;
        return .{
            .anchor = descriptor().anchor,
            .name_length = name_length,
            .mode = if (addressable) .negative_dentry_install else .name_too_long,
            .addressable = addressable,
            .installs_negative_dentry = addressable,
        };
    }

    pub fn simpleTransactionReleasePlan(private_data_present: bool) TransactionReleasePlan {
        return .{
            .anchor = descriptor().anchor,
            .private_data_present = private_data_present,
            .frees_page_backed_private_data = private_data_present,
            .clears_private_data = private_data_present,
            .returns_zero = true,
        };
    }

    pub fn planOffsetDirectorySeek(start_position: i64, requested_offset: i64, whence: OffsetSeekWhence) OffsetDirectorySeekPlan {
        const resolved_offset = switch (whence) {
            .set => requested_offset,
            .cur => start_position + requested_offset,
            .unsupported => null,
        };

        if (resolved_offset == null) {
            return .{
                .anchor = descriptor().anchor,
                .start_position = start_position,
                .requested_offset = requested_offset,
                .whence = whence,
                .resolved_offset = null,
                .status = .unsupported_whence,
                .points_at_real_entry_window = false,
                .points_at_end_of_directory = false,
            };
        }

        if (resolved_offset.? < 0) {
            return .{
                .anchor = descriptor().anchor,
                .start_position = start_position,
                .requested_offset = requested_offset,
                .whence = whence,
                .resolved_offset = null,
                .status = .negative_offset,
                .points_at_real_entry_window = false,
                .points_at_end_of_directory = false,
            };
        }

        return .{
            .anchor = descriptor().anchor,
            .start_position = start_position,
            .requested_offset = requested_offset,
            .whence = whence,
            .resolved_offset = resolved_offset,
            .status = .ok,
            .points_at_real_entry_window = resolved_offset.? >= dir_offset_first and resolved_offset.? < dir_offset_end_of_directory,
            .points_at_end_of_directory = resolved_offset.? == dir_offset_end_of_directory,
        };
    }
};

test "libfs helper descriptor stays anchored to fs/libfs.c" {
    const descriptor = LibfsHelperLab.descriptor();

    try std.testing.expectEqualStrings("libfs_helper_lab", descriptor.name);
    try std.testing.expectEqualStrings("fs/libfs.c", descriptor.anchor);
    try std.testing.expect(descriptor.provides_positive_entry_classification);
    try std.testing.expect(descriptor.provides_directory_emptiness_planning);
    try std.testing.expect(descriptor.provides_lookup_planning);
    try std.testing.expect(descriptor.provides_transaction_release_planning);
    try std.testing.expect(descriptor.provides_offset_seek_planning);
    try std.testing.expect(!descriptor.touches_live_dcache);
    try std.testing.expect(!descriptor.touches_live_inode_state);
}

test "simple_empty plan ignores trivial and negative children" {
    const entries = [_]DirectoryEntry{
        .{ .kind = .dot },
        .{ .kind = .dotdot },
        .{ .kind = .child, .inode_present = false },
    };

    const plan = LibfsHelperLab.planSimpleEmpty(&entries);
    try std.testing.expectEqualStrings("fs/libfs.c", plan.anchor);
    try std.testing.expectEqual(@as(usize, entries.len), plan.examined_entries);
    try std.testing.expect(plan.only_trivial_entries);
    try std.testing.expectEqual(@as(?usize, null), plan.first_blocking_index);
    try std.testing.expect(plan.saw_negative_child);
    try std.testing.expect(!plan.truncated);
}

test "simple_empty plan stops on first positive child" {
    const entries = [_]DirectoryEntry{
        .{ .kind = .dot },
        .{ .kind = .child, .inode_present = false },
        .{ .kind = .child, .inode_present = true },
        .{ .kind = .child, .inode_present = true },
    };

    const plan = LibfsHelperLab.planSimpleEmpty(&entries);
    try std.testing.expect(!plan.only_trivial_entries);
    try std.testing.expectEqual(@as(?usize, 2), plan.first_blocking_index);
    try std.testing.expect(plan.saw_negative_child);
}

test "simple_lookup plan keeps the negative-dentry handoff explicit for addressable names" {
    const plan = LibfsHelperLab.planSimpleLookup(name_max);

    try std.testing.expectEqualStrings("fs/libfs.c", plan.anchor);
    try std.testing.expectEqual(@as(usize, name_max), plan.name_length);
    try std.testing.expectEqual(LookupMode.negative_dentry_install, plan.mode);
    try std.testing.expect(plan.addressable);
    try std.testing.expect(plan.installs_negative_dentry);
}

test "simple_lookup plan rejects oversized names without claiming live dcache mutation" {
    const plan = LibfsHelperLab.planSimpleLookup(name_max + 1);

    try std.testing.expectEqual(@as(usize, name_max + 1), plan.name_length);
    try std.testing.expectEqual(LookupMode.name_too_long, plan.mode);
    try std.testing.expect(!plan.addressable);
    try std.testing.expect(!plan.installs_negative_dentry);
}

test "transaction release planner frees page-backed private data and returns zero" {
    const plan = LibfsHelperLab.simpleTransactionReleasePlan(true);

    try std.testing.expectEqualStrings("fs/libfs.c", plan.anchor);
    try std.testing.expect(plan.private_data_present);
    try std.testing.expect(plan.frees_page_backed_private_data);
    try std.testing.expect(plan.clears_private_data);
    try std.testing.expect(plan.returns_zero);
}

test "transaction release planner keeps the no-private-data path explicit" {
    const plan = LibfsHelperLab.simpleTransactionReleasePlan(false);

    try std.testing.expect(!plan.private_data_present);
    try std.testing.expect(!plan.frees_page_backed_private_data);
    try std.testing.expect(!plan.clears_private_data);
    try std.testing.expect(plan.returns_zero);
}

test "offset seek plan accepts SEEK_SET positions into the real-entry window" {
    const plan = LibfsHelperLab.planOffsetDirectorySeek(0, dir_offset_first + 3, .set);

    try std.testing.expectEqualStrings("fs/libfs.c", plan.anchor);
    try std.testing.expectEqual(OffsetSeekStatus.ok, plan.status);
    try std.testing.expectEqual(@as(?i64, dir_offset_first + 3), plan.resolved_offset);
    try std.testing.expect(plan.points_at_real_entry_window);
    try std.testing.expect(!plan.points_at_end_of_directory);
}

test "offset seek plan resolves SEEK_CUR relative movement and preserves dot positions" {
    const plan = LibfsHelperLab.planOffsetDirectorySeek(dir_offset_first, -1, .cur);

    try std.testing.expectEqual(OffsetSeekStatus.ok, plan.status);
    try std.testing.expectEqual(@as(?i64, 1), plan.resolved_offset);
    try std.testing.expect(!plan.points_at_real_entry_window);
    try std.testing.expect(!plan.points_at_end_of_directory);
}

test "offset seek plan rejects negative final positions" {
    const plan = LibfsHelperLab.planOffsetDirectorySeek(0, -1, .set);

    try std.testing.expectEqual(OffsetSeekStatus.negative_offset, plan.status);
    try std.testing.expectEqual(@as(?i64, null), plan.resolved_offset);
    try std.testing.expect(!plan.points_at_real_entry_window);
}

test "offset seek plan rejects unsupported whence values" {
    const plan = LibfsHelperLab.planOffsetDirectorySeek(dir_offset_first, 8, .unsupported);

    try std.testing.expectEqual(OffsetSeekStatus.unsupported_whence, plan.status);
    try std.testing.expectEqual(@as(?i64, null), plan.resolved_offset);
    try std.testing.expect(!plan.points_at_real_entry_window);
    try std.testing.expect(!plan.points_at_end_of_directory);
}

test "offset seek plan recognizes the end-of-directory sentinel" {
    const plan = LibfsHelperLab.planOffsetDirectorySeek(0, dir_offset_end_of_directory, .set);

    try std.testing.expectEqual(OffsetSeekStatus.ok, plan.status);
    try std.testing.expectEqual(@as(?i64, dir_offset_end_of_directory), plan.resolved_offset);
    try std.testing.expect(!plan.points_at_real_entry_window);
    try std.testing.expect(plan.points_at_end_of_directory);
}
