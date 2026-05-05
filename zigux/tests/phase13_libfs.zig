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
    try std.testing.expect(descriptor.provides_transaction_publish_planning);
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

test "phase13 libfs transaction acquire planning stays page-bounded and single-write" {
    const plan = try libfs.LibFsHelperLab.simpleTransactionGetPlan(libfs.simple_transaction_limit - 1, false);
    try std.testing.expectEqualStrings("fs/libfs.c", plan.anchor);
    try std.testing.expectEqual(libfs.simple_transaction_limit - 1, plan.requested_size);
    try std.testing.expectEqual(libfs.simple_transaction_limit, plan.transaction_limit);
    try std.testing.expect(plan.allocates_zeroed_page);
    try std.testing.expect(plan.requires_empty_private_data);
    try std.testing.expectEqual(@as(usize, 0), plan.response_size);

    const empty = try libfs.LibFsHelperLab.simpleTransactionGetPlan(0, false);
    try std.testing.expectEqual(@as(usize, 0), empty.requested_size);

    try std.testing.expectError(error.InputTooLarge, libfs.LibFsHelperLab.simpleTransactionGetPlan(libfs.simple_transaction_limit, false));
    try std.testing.expectError(error.Busy, libfs.LibFsHelperLab.simpleTransactionGetPlan(8, true));
}

test "phase13 libfs transaction publish planning stays response-bounded and publish-only" {
    const plan = try libfs.LibFsHelperLab.simpleTransactionSetPlan(libfs.simple_transaction_limit, true);
    try std.testing.expectEqualStrings("fs/libfs.c", plan.anchor);
    try std.testing.expectEqual(libfs.simple_transaction_limit, plan.response_size);
    try std.testing.expectEqual(libfs.simple_transaction_limit, plan.transaction_limit);
    try std.testing.expect(plan.requires_private_data);
    try std.testing.expect(plan.uses_publish_barrier);
    try std.testing.expect(plan.keeps_size_zero_until_ready);

    const empty = try libfs.LibFsHelperLab.simpleTransactionSetPlan(0, true);
    try std.testing.expectEqual(@as(usize, 0), empty.response_size);

    try std.testing.expectError(error.InputTooLarge, libfs.LibFsHelperLab.simpleTransactionSetPlan(libfs.simple_transaction_limit + 1, true));
    try std.testing.expectError(error.MissingTransactionBuffer, libfs.LibFsHelperLab.simpleTransactionSetPlan(8, false));
}
