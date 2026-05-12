const std = @import("std");

pub const page_size: u32 = 4096;
pub const name_max: u32 = 255;
pub const simple_transaction_limit: usize = page_size;

pub const max_directory_entries: usize = 128;
pub const dir_offset_first: i64 = 2;
pub const dir_offset_end_of_directory: i64 = std.math.maxInt(i32);
pub const dir_offset_min: i64 = dir_offset_first + 1;
pub const dir_offset_max: i64 = dir_offset_end_of_directory - 1;

pub const ModuleDescriptor = struct {
    name: []const u8,
    anchor: []const u8,
    provides_positive_entry_classification: bool,
    provides_directory_emptiness_planning: bool,
    provides_lookup_planning: bool,
    provides_transaction_acquire_planning: bool,
    provides_transaction_publish_planning: bool,
    provides_transaction_release_planning: bool,
    provides_offset_seek_planning: bool,
    provides_offset_readdir_planning: bool,
    provides_offset_rename_planning: bool,
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

pub const TransactionBufferAcquirePlan = struct {
    anchor: []const u8,
    requested_write_size: usize,
    transaction_limit: usize,
    allocates_zeroed_page_backing: bool,
    stages_single_write_per_open: bool,
    copies_write_into_private_data: bool,
    returns_staged_private_data: bool,
};

pub const TransactionBufferPublishPlan = struct {
    anchor: []const u8,
    requested_response_size: usize,
    transaction_limit: usize,
    requires_private_data: bool,
    publishes_after_barrier: bool,
    reuses_staged_private_data: bool,
    published_response_size: usize,
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

pub const OffsetReaddirStatus = enum {
    ok,
    negative_position,
};

pub const OffsetReaddirMode = enum {
    blocked_on_emit_dots,
    ready_to_iterate,
    ready_at_end_of_directory,
};

pub const OffsetReaddirPlan = struct {
    anchor: []const u8,
    current_position: i64,
    emit_dots_result: bool,
    status: OffsetReaddirStatus,
    mode: ?OffsetReaddirMode,
    returns_zero: bool,
    requires_dir_emit_dots: bool,
    enters_offset_iteration: bool,
    keeps_current_pos: bool,
    treats_end_of_directory_as_terminal: bool,
};

pub const OffsetSlotClass = enum {
    missing,
    dot_entry_window,
    first_real_entry,
    managed_entry,
    end_of_directory,
    out_of_range,
};

pub const OffsetRenameStatus = enum {
    ok,
    missing_destination_offset,
    reserved_destination_offset,
};

pub const OffsetRenamePlan = struct {
    anchor: []const u8,
    source_offset: ?i64,
    destination_offset: ?i64,
    source_slot_class: OffsetSlotClass,
    destination_slot_class: OffsetSlotClass,
    status: OffsetRenameStatus,
    removes_source_from_old_map: bool,
    clears_destination_offset_before_replace: bool,
    installs_source_at_destination_offset: bool,
    preserves_destination_offset_value: bool,
};

pub const OffsetRenameExchangeStatus = enum {
    ok,
    missing_source_offset,
    reserved_source_offset,
    missing_destination_offset,
    reserved_destination_offset,
};

pub const OffsetRenameExchangePlan = struct {
    anchor: []const u8,
    source_offset: ?i64,
    destination_offset: ?i64,
    source_slot_class: OffsetSlotClass,
    destination_slot_class: OffsetSlotClass,
    status: OffsetRenameExchangeStatus,
    stores_source_in_destination_map: bool,
    stores_destination_in_source_map: bool,
    swaps_recorded_offsets: bool,
    preserves_existing_offset_values: bool,
    rolls_back_destination_store_on_second_store_failure: bool,
};

pub const LibfsHelperLab = struct {
    pub fn descriptor() ModuleDescriptor {
        return .{
            .name = "libfs_helper_lab",
            .anchor = "fs/libfs.c",
            .provides_positive_entry_classification = true,
            .provides_directory_emptiness_planning = true,
            .provides_lookup_planning = true,
            .provides_transaction_acquire_planning = true,
            .provides_transaction_publish_planning = true,
            .provides_transaction_release_planning = true,
            .provides_offset_seek_planning = true,
            .provides_offset_readdir_planning = true,
            .provides_offset_rename_planning = true,
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

    pub fn simpleTransactionGetPlan(requested_write_size: usize, private_data_present: bool) !TransactionBufferAcquirePlan {
        if (private_data_present) {
            return error.PrivateDataAlreadyPresent;
        }
        if (requested_write_size > simple_transaction_limit) {
            return error.InputTooLarge;
        }

        return .{
            .anchor = descriptor().anchor,
            .requested_write_size = requested_write_size,
            .transaction_limit = simple_transaction_limit,
            .allocates_zeroed_page_backing = true,
            .stages_single_write_per_open = true,
            .copies_write_into_private_data = requested_write_size != 0,
            .returns_staged_private_data = true,
        };
    }

    pub fn simpleTransactionSetPlan(requested_response_size: usize, private_data_present: bool) !TransactionBufferPublishPlan {
        if (!private_data_present) {
            return error.MissingPrivateData;
        }
        if (requested_response_size > simple_transaction_limit) {
            return error.InputTooLarge;
        }

        return .{
            .anchor = descriptor().anchor,
            .requested_response_size = requested_response_size,
            .transaction_limit = simple_transaction_limit,
            .requires_private_data = true,
            .publishes_after_barrier = true,
            .reuses_staged_private_data = true,
            .published_response_size = requested_response_size,
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

    pub fn planOffsetReaddir(current_position: i64, emit_dots_result: bool) OffsetReaddirPlan {
        if (current_position < 0) {
            return .{
                .anchor = descriptor().anchor,
                .current_position = current_position,
                .emit_dots_result = emit_dots_result,
                .status = .negative_position,
                .mode = null,
                .returns_zero = false,
                .requires_dir_emit_dots = true,
                .enters_offset_iteration = false,
                .keeps_current_pos = false,
                .treats_end_of_directory_as_terminal = false,
            };
        }

        if (!emit_dots_result) {
            return .{
                .anchor = descriptor().anchor,
                .current_position = current_position,
                .emit_dots_result = emit_dots_result,
                .status = .ok,
                .mode = .blocked_on_emit_dots,
                .returns_zero = true,
                .requires_dir_emit_dots = true,
                .enters_offset_iteration = false,
                .keeps_current_pos = true,
                .treats_end_of_directory_as_terminal = false,
            };
        }

        const terminal = current_position == dir_offset_end_of_directory;
        return .{
            .anchor = descriptor().anchor,
            .current_position = current_position,
            .emit_dots_result = emit_dots_result,
            .status = .ok,
            .mode = if (terminal) .ready_at_end_of_directory else .ready_to_iterate,
            .returns_zero = true,
            .requires_dir_emit_dots = true,
            .enters_offset_iteration = !terminal,
            .keeps_current_pos = terminal,
            .treats_end_of_directory_as_terminal = terminal,
        };
    }

    pub fn classifyOffsetSlot(offset: ?i64) OffsetSlotClass {
        if (offset == null) {
            return .missing;
        }

        const value = offset.?;
        if (value < 0) {
            return .out_of_range;
        }
        if (value < dir_offset_first) {
            return .dot_entry_window;
        }
        if (value == dir_offset_first) {
            return .first_real_entry;
        }
        if (value >= dir_offset_min and value <= dir_offset_max) {
            return .managed_entry;
        }
        if (value == dir_offset_end_of_directory) {
            return .end_of_directory;
        }
        return .out_of_range;
    }

    pub fn planSimpleOffsetRename(source_offset: ?i64, destination_offset: ?i64) OffsetRenamePlan {
        const source_slot_class = classifyOffsetSlot(source_offset);
        const destination_slot_class = classifyOffsetSlot(destination_offset);
        const status: OffsetRenameStatus = switch (destination_slot_class) {
            .managed_entry => .ok,
            .missing => .missing_destination_offset,
            else => .reserved_destination_offset,
        };

        return .{
            .anchor = descriptor().anchor,
            .source_offset = source_offset,
            .destination_offset = destination_offset,
            .source_slot_class = source_slot_class,
            .destination_slot_class = destination_slot_class,
            .status = status,
            .removes_source_from_old_map = source_slot_class == .managed_entry,
            .clears_destination_offset_before_replace = status == .ok,
            .installs_source_at_destination_offset = status == .ok,
            .preserves_destination_offset_value = status == .ok,
        };
    }

    pub fn planSimpleOffsetRenameExchange(source_offset: ?i64, destination_offset: ?i64) OffsetRenameExchangePlan {
        const source_slot_class = classifyOffsetSlot(source_offset);
        const destination_slot_class = classifyOffsetSlot(destination_offset);
        const status: OffsetRenameExchangeStatus = switch (source_slot_class) {
            .missing => .missing_source_offset,
            .managed_entry => switch (destination_slot_class) {
                .missing => .missing_destination_offset,
                .managed_entry => .ok,
                else => .reserved_destination_offset,
            },
            else => .reserved_source_offset,
        };

        return .{
            .anchor = descriptor().anchor,
            .source_offset = source_offset,
            .destination_offset = destination_offset,
            .source_slot_class = source_slot_class,
            .destination_slot_class = destination_slot_class,
            .status = status,
            .stores_source_in_destination_map = status == .ok,
            .stores_destination_in_source_map = status == .ok,
            .swaps_recorded_offsets = status == .ok,
            .preserves_existing_offset_values = status == .ok,
            .rolls_back_destination_store_on_second_store_failure = status == .ok,
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
    try std.testing.expect(descriptor.provides_transaction_acquire_planning);
    try std.testing.expect(descriptor.provides_transaction_publish_planning);
    try std.testing.expect(descriptor.provides_transaction_release_planning);
    try std.testing.expect(descriptor.provides_offset_seek_planning);
    try std.testing.expect(descriptor.provides_offset_readdir_planning);
    try std.testing.expect(descriptor.provides_offset_rename_planning);
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

test "transaction acquire planner bounds the staged write buffer and enforces one-write-per-open" {
    const plan = try LibfsHelperLab.simpleTransactionGetPlan(simple_transaction_limit, false);

    try std.testing.expectEqualStrings("fs/libfs.c", plan.anchor);
    try std.testing.expectEqual(simple_transaction_limit, plan.requested_write_size);
    try std.testing.expectEqual(simple_transaction_limit, plan.transaction_limit);
    try std.testing.expect(plan.allocates_zeroed_page_backing);
    try std.testing.expect(plan.stages_single_write_per_open);
    try std.testing.expect(plan.copies_write_into_private_data);
    try std.testing.expect(plan.returns_staged_private_data);

    const empty = try LibfsHelperLab.simpleTransactionGetPlan(0, false);
    try std.testing.expect(!empty.copies_write_into_private_data);

    try std.testing.expectError(error.InputTooLarge, LibfsHelperLab.simpleTransactionGetPlan(simple_transaction_limit + 1, false));
    try std.testing.expectError(error.PrivateDataAlreadyPresent, LibfsHelperLab.simpleTransactionGetPlan(8, true));
}

test "transaction publish planner validates response size and publish bookkeeping" {
    const plan = try LibfsHelperLab.simpleTransactionSetPlan(simple_transaction_limit, true);

    try std.testing.expectEqualStrings("fs/libfs.c", plan.anchor);
    try std.testing.expectEqual(simple_transaction_limit, plan.requested_response_size);
    try std.testing.expectEqual(simple_transaction_limit, plan.transaction_limit);
    try std.testing.expect(plan.requires_private_data);
    try std.testing.expect(plan.publishes_after_barrier);
    try std.testing.expect(plan.reuses_staged_private_data);
    try std.testing.expectEqual(simple_transaction_limit, plan.published_response_size);

    const empty = try LibfsHelperLab.simpleTransactionSetPlan(0, true);
    try std.testing.expectEqual(@as(usize, 0), empty.published_response_size);

    try std.testing.expectError(error.InputTooLarge, LibfsHelperLab.simpleTransactionSetPlan(simple_transaction_limit + 1, true));
    try std.testing.expectError(error.MissingPrivateData, LibfsHelperLab.simpleTransactionSetPlan(8, false));
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
    try std.testing.expect(!plan.points_atEndOfDirectory);
}

test "offset seek plan recognizes the end-of-directory sentinel" {
    const plan = LibfsHelperLab.planOffsetDirectorySeek(0, dir_offset_end_of_directory, .set);

    try std.testing.expectEqual(OffsetSeekStatus.ok, plan.status);
    try std.testing.expectEqual(@as(?i64, dir_offset_end_of_directory), plan.resolved_offset);
    try std.testing.expect(!plan.points_at_real_entry_window);
    try std.testing.expect(plan.points_at_end_of_directory);
}

test "offset readdir plan gates offset iteration on emit_dots and eod state" {
    const blocked = LibfsHelperLab.planOffsetReaddir(dir_offset_first + 4, false);
    try std.testing.expectEqualStrings("fs/libfs.c", blocked.anchor);
    try std.testing.expectEqual(OffsetReaddirStatus.ok, blocked.status);
    try std.testing.expectEqual(OffsetReaddirMode.blocked_on_emit_dots, blocked.mode.?);
    try std.testing.expect(blocked.returns_zero);
    try std.testing.expect(blocked.requires_dir_emit_dots);
    try std.testing.expect(!blocked.enters_offset_iteration);
    try std.testing.expect(blocked.keeps_current_pos);
    try std.testing.expect(!blocked.treats_end_of_directory_as_terminal);

    const active = LibfsHelperLab.planOffsetReaddir(dir_offset_first + 4, true);
    try std.testing.expectEqual(OffsetReaddirStatus.ok, active.status);
    try std.testing.expectEqual(OffsetReaddirMode.ready_to_iterate, active.mode.?);
    try std.testing.expect(active.enters_offset_iteration);
    try std.testing.expect(!active.keeps_current_pos);
    try std.testing.expect(!active.treats_end_of_directory_as_terminal);

    const terminal = LibfsHelperLab.planOffsetReaddir(dir_offset_end_of_directory, true);
    try std.testing.expectEqual(OffsetReaddirStatus.ok, terminal.status);
    try std.testing.expectEqual(OffsetReaddirMode.ready_at_end_of_directory, terminal.mode.?);
    try std.testing.expect(!terminal.enters_offset_iteration);
    try std.testing.expect(terminal.keeps_current_pos);
    try std.testing.expect(terminal.treats_end_of_directory_as_terminal);

    const invalid = LibfsHelperLab.planOffsetReaddir(-1, true);
    try std.testing.expectEqual(OffsetReaddirStatus.negative_position, invalid.status);
    try std.testing.expectEqual(@as(?OffsetReaddirMode, null), invalid.mode);
    try std.testing.expect(!invalid.returns_zero);
}

test "offset slot classification distinguishes managed entries from reserved sentinels" {
    try std.testing.expectEqual(OffsetSlotClass.missing, LibfsHelperLab.classifyOffsetSlot(null));
    try std.testing.expectEqual(OffsetSlotClass.dot_entry_window, LibfsHelperLab.classifyOffsetSlot(0));
    try std.testing.expectEqual(OffsetSlotClass.first_real_entry, LibfsHelperLab.classifyOffsetSlot(dir_offset_first));
    try std.testing.expectEqual(OffsetSlotClass.managed_entry, LibfsHelperLab.classifyOffsetSlot(dir_offset_min));
    try std.testing.expectEqual(OffsetSlotClass.end_of_directory, LibfsHelperLab.classifyOffsetSlot(dir_offset_end_of_directory));
}

test "offset rename plan preserves destination slot value for managed entries" {
    const plan = LibfsHelperLab.planSimpleOffsetRename(dir_offset_min + 4, dir_offset_min + 9);

    try std.testing.expectEqualStrings("fs/libfs.c", plan.anchor);
    try std.testing.expectEqual(OffsetSlotClass.managed_entry, plan.source_slot_class);
    try std.testing.expectEqual(OffsetSlotClass.managed_entry, plan.destination_slot_class);
    try std.testing.expectEqual(OffsetRenameStatus.ok, plan.status);
    try std.testing.expect(plan.removes_source_from_old_map);
    try std.testing.expect(plan.clears_destination_offset_before_replace);
    try std.testing.expect(plan.installs_source_at_destination_offset);
    try std.testing.expect(plan.preserves_destination_offset_value);
}

test "offset rename plan rejects missing or reserved destination slots" {
    const missing = LibfsHelperLab.planSimpleOffsetRename(dir_offset_min + 1, null);
    try std.testing.expectEqual(OffsetRenameStatus.missing_destination_offset, missing.status);
    try std.testing.expect(!missing.clears_destination_offset_before_replace);
    try std.testing.expect(!missing.installs_source_at_destination_offset);

    const reserved = LibfsHelperLab.planSimpleOffsetRename(dir_offset_min + 1, dir_offset_first);
    try std.testing.expectEqual(OffsetRenameStatus.reserved_destination_offset, reserved.status);
    try std.testing.expectEqual(OffsetSlotClass.first_real_entry, reserved.destination_slot_class);
    try std.testing.expect(!reserved.preserves_destination_offset_value);
}

test "offset rename exchange plan swaps managed offsets and records rollback expectations" {
    const plan = LibfsHelperLab.planSimpleOffsetRenameExchange(dir_offset_min + 2, dir_offset_min + 8);

    try std.testing.expectEqualStrings("fs/libfs.c", plan.anchor);
    try std.testing.expectEqual(OffsetRenameExchangeStatus.ok, plan.status);
    try std.testing.expectEqual(OffsetSlotClass.managed_entry, plan.source_slot_class);
    try std.testing.expectEqual(OffsetSlotClass.managed_entry, plan.destination_slot_class);
    try std.testing.expect(plan.stores_source_in_destination_map);
    try std.testing.expect(plan.stores_destination_in_source_map);
    try std.testing.expect(plan.swaps_recorded_offsets);
    try std.testing.expect(plan.preserves_existing_offset_values);
    try std.testing.expect(plan.rolls_back_destination_store_on_second_store_failure);
}

test "offset rename exchange plan requires both managed offsets" {
    const missing_source = LibfsHelperLab.planSimpleOffsetRenameExchange(null, dir_offset_min + 3);
    try std.testing.expectEqual(OffsetRenameExchangeStatus.missing_source_offset, missing_source.status);
    try std.testing.expect(!missing_source.stores_source_in_destination_map);

    const reserved_destination = LibfsHelperLab.planSimpleOffsetRenameExchange(dir_offset_min + 3, dir_offset_end_of_directory);
    try std.testing.expectEqual(OffsetRenameExchangeStatus.reserved_destination_offset, reserved_destination.status);
    try std.testing.expectEqual(OffsetSlotClass.end_of_directory, reserved_destination.destination_slot_class);
    try std.testing.expect(!reserved_destination.swaps_recorded_offsets);
}
