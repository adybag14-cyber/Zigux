const std = @import("std");

pub const max_directory_entries: usize = 128;

pub const ModuleDescriptor = struct {
    name: []const u8,
    anchor: []const u8,
    provides_positive_entry_classification: bool,
    provides_directory_emptiness_planning: bool,
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

pub const LibfsHelperLab = struct {
    pub fn descriptor() ModuleDescriptor {
        return .{
            .name = "libfs_helper_lab",
            .anchor = "fs/libfs.c",
            .provides_positive_entry_classification = true,
            .provides_directory_emptiness_planning = true,
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
};

test "libfs helper descriptor stays anchored to fs/libfs.c" {
    const descriptor = LibfsHelperLab.descriptor();

    try std.testing.expectEqualStrings("libfs_helper_lab", descriptor.name);
    try std.testing.expectEqualStrings("fs/libfs.c", descriptor.anchor);
    try std.testing.expect(descriptor.provides_positive_entry_classification);
    try std.testing.expect(descriptor.provides_directory_emptiness_planning);
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
