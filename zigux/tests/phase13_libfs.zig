const std = @import("std");
const libfs = @import("libfs");

test "phase13 libfs exposes the statfs starter anchored to libfs.c" {
    const descriptor = libfs.LibFsHelperLab.descriptor();
    try std.testing.expectEqualStrings("libfs_helper_lab", descriptor.name);
    try std.testing.expectEqualStrings("fs/libfs.c", descriptor.anchor);
    try std.testing.expect(descriptor.provides_statfs_defaults);
    try std.testing.expect(descriptor.provides_lookup_policy);
    try std.testing.expect(descriptor.provides_buffer_copy_helpers);
    try std.testing.expect(descriptor.provides_offset_seek_helpers);
    try std.testing.expect(descriptor.provides_directory_emit_planning);
    try std.testing.expect(descriptor.provides_transaction_buffer_planning);
    try std.testing.expect(descriptor.provides_transaction_read_release_planning);
    try std.testing.expect(!descriptor.touches_live_dcache);
    try std.testing.expect(!descriptor.touches_live_inode_state);

    const summary = libfs.LibFsHelperLab.simpleStatFs(0x12345678ABCDEF01, @as(u64, 0xBEEF));
    try std.testing.expectEqualStrings("fs/libfs.c", summary.anchor);
    try std.testing.expectEqual(@as(u32, 0xABCDEF01), summary.fsid.val[0]);
    try std.testing.expectEqual(@as(u32, 0x12345678), summary.fsid.val[1]);
    try std.testing.expectEqual(@as(u64, 0xBEEF), summary.fs_type);
    try std.testing.expectEqual(@as(u32, libfs.page_size), summary.block_size);
    try std.testing.expectEqual(@as(u32, libfs.name_max), summary.name_len_max);
}

test "phase13 libfs lookup policy marks negative dentries for immediate discard" {
    try std.testing.expect(libfs.LibFsHelperLab.alwaysDeleteDentry());

    const decision = try libfs.LibFsHelperLab.simpleLookup(.{
        .name_len = 12,
        .has_dentry_operations = false,
        .dont_cache_negative = false,
        .directory_is_casefolded = false,
    });
    try std.testing.expectEqualStrings("fs/libfs.c", decision.anchor);
    try std.testing.expect(decision.should_mark_dont_cache);
    try std.testing.expect(decision.should_add_negative_dentry);
    try std.testing.expect(decision.returns_null);
    try std.testing.expect(!decision.casefold_passthrough);
}

test "phase13 libfs lookup keeps casefold passthrough and rejects long names" {
    const casefolded = try libfs.LibFsHelperLab.simpleLookup(.{
        .name_len = libfs.name_max,
        .has_dentry_operations = true,
        .dont_cache_negative = true,
        .directory_is_casefolded = true,
    });
    try std.testing.expect(!casefolded.should_mark_dont_cache);
    try std.testing.expect(!casefolded.should_add_negative_dentry);
    try std.testing.expect(casefolded.returns_null);
    try std.testing.expect(casefolded.casefold_passthrough);

    try std.testing.expectError(error.NameTooLong, libfs.LibFsHelperLab.simpleLookup(.{
        .name_len = libfs.name_max + 1,
        .has_dentry_operations = false,
        .dont_cache_negative = false,
        .directory_is_casefolded = false,
    }));
}

test "phase13 libfs buffer helpers clamp to the available read window" {
    var pos: i64 = 2;
    var destination = [_]u8{ 0, 0, 0, 0, 0 };
    const source = "abcdef";

    const result = try libfs.LibFsHelperLab.simpleReadFromBuffer(destination[0..], &pos, source, 0);
    try std.testing.expectEqualStrings("fs/libfs.c", result.anchor);
    try std.testing.expectEqual(@as(usize, 4), result.copied);
    try std.testing.expectEqual(@as(i64, 6), result.new_pos);
    try std.testing.expectEqualSlices(u8, "cdef", destination[0..4]);
}

test "phase13 libfs buffer helpers preserve short-copy accounting" {
    var read_pos: i64 = 1;
    var read_destination = [_]u8{ 0, 0, 0, 0 };
    const read_result = try libfs.LibFsHelperLab.simpleReadFromBuffer(read_destination[0..], &read_pos, "abcdef", 2);
    try std.testing.expectEqual(@as(usize, 2), read_result.copied);
    try std.testing.expectEqual(@as(i64, 3), read_result.new_pos);
    try std.testing.expectEqualSlices(u8, "bc", read_destination[0..2]);

    var write_pos: i64 = 2;
    var write_destination = [_]u8{ '_', '_', '_', '_', '_', '_' };
    const write_result = try libfs.LibFsHelperLab.simpleWriteToBuffer(write_destination[0..], &write_pos, "wxyz", 1);
    try std.testing.expectEqual(@as(usize, 3), write_result.copied);
    try std.testing.expectEqual(@as(i64, 5), write_result.new_pos);
    try std.testing.expectEqualSlices(u8, "__wxy_", write_destination[0..]);
}

test "phase13 libfs memory reads and invalid offsets match the bounded C helper rules" {
    var memory_pos: i64 = 4;
    var memory_destination = [_]u8{ 0, 0, 0, 0 };
    const memory_result = try libfs.LibFsHelperLab.memoryReadFromBuffer(memory_destination[0..], &memory_pos, "abcdef");
    try std.testing.expectEqual(@as(usize, 2), memory_result.copied);
    try std.testing.expectEqual(@as(i64, 6), memory_result.new_pos);
    try std.testing.expectEqualSlices(u8, "ef", memory_destination[0..2]);

    var eof_pos: i64 = 6;
    var eof_destination = [_]u8{ 1, 2, 3 };
    const eof_result = try libfs.LibFsHelperLab.memoryReadFromBuffer(eof_destination[0..], &eof_pos, "abcdef");
    try std.testing.expectEqual(@as(usize, 0), eof_result.copied);
    try std.testing.expectEqual(@as(i64, 6), eof_result.new_pos);

    var invalid_pos: i64 = -1;
    var invalid_destination = [_]u8{ 0, 0, 0 };
    try std.testing.expectError(error.InvalidOffset, libfs.LibFsHelperLab.simpleReadFromBuffer(invalid_destination[0..], &invalid_pos, "abc", 0));

    var fault_pos: i64 = 0;
    var fault_destination = [_]u8{ 0, 0 };
    try std.testing.expectError(error.CopyFault, libfs.LibFsHelperLab.simpleWriteToBuffer(fault_destination[0..], &fault_pos, "xy", 2));
}

test "phase13 libfs buffer helpers keep no-op offset windows stable" {
    var read_pos: i64 = 6;
    var read_destination = [_]u8{ 9, 9, 9 };
    const read_result = try libfs.LibFsHelperLab.simpleReadFromBuffer(read_destination[0..], &read_pos, "abcdef", 0);
    try std.testing.expectEqual(@as(usize, 0), read_result.copied);
    try std.testing.expectEqual(@as(i64, 6), read_result.new_pos);
    try std.testing.expectEqual(@as(i64, 6), read_pos);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 9, 9, 9 }, read_destination[0..]);

    var write_pos: i64 = 4;
    var write_destination = [_]u8{ 'a', 'b', 'c', 'd' };
    const write_result = try libfs.LibFsHelperLab.simpleWriteToBuffer(write_destination[0..], &write_pos, "xy", 0);
    try std.testing.expectEqual(@as(usize, 0), write_result.copied);
    try std.testing.expectEqual(@as(i64, 4), write_result.new_pos);
    try std.testing.expectEqual(@as(i64, 4), write_pos);
    try std.testing.expectEqualSlices(u8, "abcd", write_destination[0..]);

    var memory_pos: i64 = 3;
    var memory_destination = [_]u8{ 7, 8 };
    const memory_result = try libfs.LibFsHelperLab.memoryReadFromBuffer(memory_destination[0..], &memory_pos, "abc");
    try std.testing.expectEqual(@as(usize, 0), memory_result.copied);
    try std.testing.expectEqual(@as(i64, 3), memory_result.new_pos);
    try std.testing.expectEqual(@as(i64, 3), memory_pos);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 7, 8 }, memory_destination[0..]);
}

test "phase13 libfs dcache seek planning keeps dots stable and flags positive scans" {
    const dots = try libfs.LibFsHelperLab.dcacheDirSeekPlan(2, 0, .set);
    try std.testing.expectEqualStrings("fs/libfs.c", dots.anchor);
    try std.testing.expectEqual(@as(i64, 0), dots.new_pos);
    try std.testing.expect(dots.changed);
    try std.testing.expect(!dots.requires_positive_scan);
    try std.testing.expect(dots.stays_in_dots_window);

    const scan = try libfs.LibFsHelperLab.dcacheDirSeekPlan(1, 4, .cur);
    try std.testing.expectEqual(@as(i64, 5), scan.new_pos);
    try std.testing.expect(scan.changed);
    try std.testing.expect(scan.requires_positive_scan);
    try std.testing.expect(!scan.stays_in_dots_window);

    const stable = try libfs.LibFsHelperLab.dcacheDirSeekPlan(5, 5, .set);
    try std.testing.expectEqual(@as(i64, 5), stable.new_pos);
    try std.testing.expect(!stable.changed);
    try std.testing.expect(!stable.requires_positive_scan);

    try std.testing.expectError(error.InvalidOffset, libfs.LibFsHelperLab.dcacheDirSeekPlan(1, -3, .set));
    try std.testing.expectError(error.InvalidOffset, libfs.LibFsHelperLab.dcacheDirSeekPlan(1, -2, .cur));
    try std.testing.expectError(error.UnsupportedWhence, libfs.LibFsHelperLab.dcacheDirSeekPlan(1, 0, .end));
}

test "phase13 libfs offset seek planning stays bounded by vfs-style max positions" {
    const within_range = try libfs.LibFsHelperLab.offsetDirSeekPlan(3, 4, .cur, 16);
    try std.testing.expectEqualStrings("fs/libfs.c", within_range.anchor);
    try std.testing.expectEqual(@as(i64, 7), within_range.new_pos);
    try std.testing.expect(within_range.changed);
    try std.testing.expect(!within_range.requires_positive_scan);
    try std.testing.expect(!within_range.stays_in_dots_window);

    const dots = try libfs.LibFsHelperLab.offsetDirSeekPlan(0, 2, .set, 16);
    try std.testing.expectEqual(@as(i64, 2), dots.new_pos);
    try std.testing.expect(dots.stays_in_dots_window);

    try std.testing.expectError(error.PositionOutOfRange, libfs.LibFsHelperLab.offsetDirSeekPlan(3, 20, .set, 16));
    try std.testing.expectError(error.UnsupportedWhence, libfs.LibFsHelperLab.offsetDirSeekPlan(3, 0, .hole, 16));
}

test "phase13 libfs directory emit planning stops cleanly before positive scan starts" {
    const blocked = try libfs.LibFsHelperLab.dcacheReaddirEmitPlan(0, false, 0);
    try std.testing.expectEqualStrings("fs/libfs.c", blocked.anchor);
    try std.testing.expectEqual(@as(i64, 0), blocked.new_pos);
    try std.testing.expect(!blocked.entered_positive_scan);
    try std.testing.expect(!blocked.emitted_any_entries);
    try std.testing.expect(blocked.stays_in_dots_window);
    try std.testing.expect(blocked.should_stop);
}

test "phase13 libfs directory emit planning advances after dots and tracks empty scans" {
    const emitted = try libfs.LibFsHelperLab.dcacheReaddirEmitPlan(0, true, 3);
    try std.testing.expectEqual(@as(i64, 5), emitted.new_pos);
    try std.testing.expect(emitted.entered_positive_scan);
    try std.testing.expect(emitted.emitted_any_entries);
    try std.testing.expect(!emitted.stays_in_dots_window);
    try std.testing.expect(!emitted.should_stop);

    const empty_scan = try libfs.LibFsHelperLab.dcacheReaddirEmitPlan(4, true, 0);
    try std.testing.expectEqual(@as(i64, 4), empty_scan.new_pos);
    try std.testing.expect(empty_scan.entered_positive_scan);
    try std.testing.expect(!empty_scan.emitted_any_entries);
    try std.testing.expect(!empty_scan.stays_in_dots_window);
    try std.testing.expect(empty_scan.should_stop);

    try std.testing.expectError(error.InvalidOffset, libfs.LibFsHelperLab.dcacheReaddirEmitPlan(-1, true, 0));
    try std.testing.expectError(error.PositionOutOfRange, libfs.LibFsHelperLab.dcacheReaddirEmitPlan(std.math.maxInt(i64), true, 1));
}

test "phase13 libfs transaction staging planner models one-write reservation and copy-fault retention" {
    const ready = libfs.LibFsHelperLab.simpleTransactionGetPlan(false, 32, true, 0);
    try std.testing.expectEqualStrings("fs/libfs.c", ready.anchor);
    try std.testing.expectEqual(libfs.TransactionAcquireMode.ready, ready.mode);
    try std.testing.expectEqual(@as(usize, 32), ready.requested_size);
    try std.testing.expectEqual(@as(usize, 32), ready.copied_size);
    try std.testing.expectEqual(libfs.simple_transaction_limit, ready.staging_capacity);
    try std.testing.expect(ready.reserves_private_data);
    try std.testing.expect(ready.requires_release);
    try std.testing.expect(!ready.keeps_private_data_on_failure);

    const copy_fault = libfs.LibFsHelperLab.simpleTransactionGetPlan(false, 32, true, 5);
    try std.testing.expectEqual(libfs.TransactionAcquireMode.copy_fault, copy_fault.mode);
    try std.testing.expectEqual(@as(usize, 27), copy_fault.copied_size);
    try std.testing.expect(copy_fault.reserves_private_data);
    try std.testing.expect(copy_fault.requires_release);
    try std.testing.expect(copy_fault.keeps_private_data_on_failure);
}

test "phase13 libfs transaction staging planner rejects oversize, duplicate writers, oom, and publish overflow" {
    const too_large = libfs.LibFsHelperLab.simpleTransactionGetPlan(false, libfs.simple_transaction_limit, true, 0);
    try std.testing.expectEqual(libfs.TransactionAcquireMode.request_too_large, too_large.mode);
    try std.testing.expect(!too_large.reserves_private_data);
    try std.testing.expect(!too_large.requires_release);

    const out_of_memory = libfs.LibFsHelperLab.simpleTransactionGetPlan(false, 8, false, 0);
    try std.testing.expectEqual(libfs.TransactionAcquireMode.out_of_memory, out_of_memory.mode);
    try std.testing.expect(!out_of_memory.reserves_private_data);

    const already_open = libfs.LibFsHelperLab.simpleTransactionGetPlan(true, 8, true, 0);
    try std.testing.expectEqual(libfs.TransactionAcquireMode.already_open, already_open.mode);
    try std.testing.expect(!already_open.reserves_private_data);

    const publish = try libfs.LibFsHelperLab.simpleTransactionSetPlan(17);
    try std.testing.expectEqualStrings("fs/libfs.c", publish.anchor);
    try std.testing.expectEqual(@as(usize, 17), publish.published_size);
    try std.testing.expect(publish.uses_release_barrier);
    try std.testing.expect(publish.becomes_readable);

    try std.testing.expectError(error.TransactionTooLarge, libfs.LibFsHelperLab.simpleTransactionSetPlan(libfs.simple_transaction_limit + 1));
}

test "phase13 libfs transaction read planning stays pure around private-data presence" {
    const closed = libfs.LibFsHelperLab.simpleTransactionReadPlan(false, 64);
    try std.testing.expectEqualStrings("fs/libfs.c", closed.anchor);
    try std.testing.expectEqual(@as(usize, 0), closed.readable_size);
    try std.testing.expect(closed.returns_eof);
    try std.testing.expect(!closed.delegates_to_simple_read_from_buffer);
    try std.testing.expect(!closed.keeps_private_data);
    try std.testing.expect(closed.leaves_pos_unchanged);

    const readable = libfs.LibFsHelperLab.simpleTransactionReadPlan(true, 19);
    try std.testing.expectEqual(@as(usize, 19), readable.readable_size);
    try std.testing.expect(!readable.returns_eof);
    try std.testing.expect(readable.delegates_to_simple_read_from_buffer);
    try std.testing.expect(readable.keeps_private_data);
    try std.testing.expect(!readable.leaves_pos_unchanged);
}

test "phase13 libfs transaction release planning only frees reserved private data" {
    const no_private_data = libfs.LibFsHelperLab.simpleTransactionReleasePlan(false);
    try std.testing.expectEqualStrings("fs/libfs.c", no_private_data.anchor);
    try std.testing.expect(no_private_data.returns_zero);
    try std.testing.expect(!no_private_data.frees_private_data);
    try std.testing.expect(!no_private_data.had_private_data);

    const release = libfs.LibFsHelperLab.simpleTransactionReleasePlan(true);
    try std.testing.expect(release.returns_zero);
    try std.testing.expect(release.frees_private_data);
    try std.testing.expect(release.had_private_data);
}
