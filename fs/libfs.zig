const std = @import("std");

pub const page_size: u32 = 4096;
pub const name_max: u32 = 255;
pub const simple_transaction_limit: usize = page_size;

pub const max_directory_entries: usize = 128;

pub const ModuleDescriptor = struct {
    name: []const u8,
    anchor: []const u8,
    provides_positive_entry_classification: bool,
    provides_directory_emptiness_planning: bool,
    provides_lookup_planning: bool,
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

pub const LibfsHelperLab = struct {
    pub fn descriptor() ModuleDescriptor {
        return .{
            .name = "libfs_helper_lab",
            .anchor = "fs/libfs.c",
            .provides_positive_entry_classification = true,
            .provides_directory_emptiness_planning = true,
            .provides_lookup_planning = true,
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
};

test "libfs helper descriptor stays anchored to fs/libfs.c" {
    const descriptor = LibfsHelperLab.descriptor();

    try std.testing.expectEqualStrings("libfs_helper_lab", descriptor.name);
    try std.testing.expectEqualStrings("fs/libfs.c", descriptor.anchor);
    try std.testing.expect(descriptor.provides_positive_entry_classification);
    try std.testing.expect(descriptor.provides_directory_emptiness_planning);
    try std.testing.expect(descriptor.provides_lookup_planning);
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
