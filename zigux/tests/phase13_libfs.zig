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
    try std.testing.expect(descriptor.provides_offset_readdir_planning);
    try std.testing.expect(descriptor.provides_directory_emit_planning);
    try std.testing.expect(descriptor.provides_directory_cursor_preconditions);
    try std.testing.expect(descriptor.provides_directory_cursor_reposition_planning);
    try std.testing.expect(descriptor.provides_directory_close_planning);
    try std.testing.expect(descriptor.provides_transaction_buffer_planning);
    try std.testing.expect(descriptor.provides_transaction_read_release_planning);
    try std.testing.expect(descriptor.provides_open_private_data_planning);
    try std.testing.expect(descriptor.provides_addressability_planning);
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

test "phase13 libfs offset readdir planning gates dots and honors the terminal sentinel" {
    const blocked = try libfs.LibFsHelperLab.offsetReaddirPlan(libfs.dir_offset_first, false);
    try std.testing.expectEqualStrings("fs/libfs.c", blocked.anchor);
    try std.testing.expectEqual(libfs.OffsetReaddirMode.blocked_on_emit_dots, blocked.mode);
    try std.testing.expect(blocked.returns_zero);
    try std.testing.expect(blocked.requires_dir_emit_dots);
    try std.testing.expect(!blocked.enters_offset_iteration);
    try std.testing.expect(blocked.keeps_current_pos);
    try std.testing.expect(!blocked.treats_eod_as_terminal);

    const iterating = try libfs.LibFsHelperLab.offsetReaddirPlan(libfs.dir_offset_first, true);
    try std.testing.expectEqual(libfs.OffsetReaddirMode.ready_to_iterate, iterating.mode);
    try std.testing.expect(iterating.returns_zero);
    try std.testing.expect(iterating.requires_dir_emit_dots);
    try std.testing.expect(iterating.enters_offset_iteration);
    try std.testing.expect(!iterating.keeps_current_pos);
    try std.testing.expect(!iterating.treats_eod_as_terminal);

    const at_eod = try libfs.LibFsHelperLab.offsetReaddirPlan(libfs.dir_offset_eod, true);
    try std.testing.expectEqual(libfs.OffsetReaddirMode.ready_at_end_of_directory, at_eod.mode);
    try std.testing.expect(at_eod.returns_zero);
    try std.testing.expect(at_eod.requires_dir_emit_dots);
    try std.testing.expect(!at_eod.enters_offset_iteration);
    try std.testing.expect(at_eod.keeps_current_pos);
    try std.testing.expect(at_eod.treats_eod_as_terminal);

    try std.testing.expectError(error.InvalidOffset, libfs.LibFsHelperLab.offsetReaddirPlan(-1, true));
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

test "phase13 libfs cursor open planning stays in private-data reservation rules" {
    const ready = libfs.LibFsHelperLab.dcacheDirOpenPlan(true);
    try std.testing.expectEqualStrings("fs/libfs.c", ready.anchor);
    try std.testing.expectEqual(libfs.CursorOpenMode.ready, ready.mode);
    try std.testing.expect(ready.allocates_private_cursor);
    try std.testing.expect(ready.stores_private_data);

    const oom = libfs.LibFsHelperLab.dcacheDirOpenPlan(false);
    try std.testing.expectEqual(libfs.CursorOpenMode.out_of_memory, oom.mode);
    try std.testing.expect(!oom.allocates_private_cursor);
    try std.testing.expect(!oom.stores_private_data);
}

test "phase13 libfs cursor preconditions gate positive scans on dots and cursor presence" {
    const blocked = try libfs.LibFsHelperLab.dcacheReaddirCursorPreconditionsPlan(0, true, false);
    try std.testing.expectEqualStrings("fs/libfs.c", blocked.anchor);
    try std.testing.expectEqual(libfs.CursorPreconditionMode.blocked_on_emit_dots, blocked.mode);
    try std.testing.expectEqual(libfs.CursorResumeSource.none, blocked.resume_source);
    try std.testing.expect(blocked.requires_dir_emit_dots);
    try std.testing.expect(!blocked.can_scan_positives);
    try std.testing.expect(blocked.keeps_private_data);
    try std.testing.expect(!blocked.defers_cursor_reposition);

    const missing_cursor = try libfs.LibFsHelperLab.dcacheReaddirCursorPreconditionsPlan(3, false, true);
    try std.testing.expectEqual(libfs.CursorPreconditionMode.missing_private_cursor, missing_cursor.mode);
    try std.testing.expectEqual(libfs.CursorResumeSource.none, missing_cursor.resume_source);
    try std.testing.expect(missing_cursor.requires_dir_emit_dots);
    try std.testing.expect(!missing_cursor.can_scan_positives);
    try std.testing.expect(!missing_cursor.keeps_private_data);
    try std.testing.expect(!missing_cursor.defers_cursor_reposition);
}

test "phase13 libfs cursor preconditions choose first-child or cursor resume without claiming reposition" {
    const first_child = try libfs.LibFsHelperLab.dcacheReaddirCursorPreconditionsPlan(2, true, true);
    try std.testing.expectEqual(libfs.CursorPreconditionMode.ready, first_child.mode);
    try std.testing.expectEqual(libfs.CursorResumeSource.first_child, first_child.resume_source);
    try std.testing.expect(first_child.requires_dir_emit_dots);
    try std.testing.expect(first_child.can_scan_positives);
    try std.testing.expect(first_child.keeps_private_data);
    try std.testing.expect(first_child.defers_cursor_reposition);

    const resumed = try libfs.LibFsHelperLab.dcacheReaddirCursorPreconditionsPlan(7, true, true);
    try std.testing.expectEqual(libfs.CursorPreconditionMode.ready, resumed.mode);
    try std.testing.expectEqual(libfs.CursorResumeSource.stored_cursor_next, resumed.resume_source);
    try std.testing.expect(resumed.can_scan_positives);
    try std.testing.expect(resumed.keeps_private_data);
    try std.testing.expect(resumed.defers_cursor_reposition);

    try std.testing.expectError(error.InvalidOffset, libfs.LibFsHelperLab.dcacheReaddirCursorPreconditionsPlan(-1, true, true));
}

test "phase13 libfs seek cursor reposition planning keeps the post-scan relink bounded" {
    const found_target = libfs.LibFsHelperLab.dcacheDirSeekCursorRepositionPlan(true);
    try std.testing.expectEqualStrings("fs/libfs.c", found_target.anchor);
    try std.testing.expectEqual(libfs.CursorRepositionMode.reanchor_behind_found, found_target.mode);
    try std.testing.expect(found_target.unlinks_existing_cursor);
    try std.testing.expect(found_target.requires_parent_lock);
    try std.testing.expect(found_target.drops_found_reference);
    try std.testing.expect(found_target.keeps_private_data);

    const not_found = libfs.LibFsHelperLab.dcacheDirSeekCursorRepositionPlan(false);
    try std.testing.expectEqual(libfs.CursorRepositionMode.unhashed, not_found.mode);
    try std.testing.expect(not_found.unlinks_existing_cursor);
    try std.testing.expect(not_found.requires_parent_lock);
    try std.testing.expect(not_found.drops_found_reference);
    try std.testing.expect(not_found.keeps_private_data);
}

test "phase13 libfs readdir cursor reposition planning distinguishes before-next from unhashed" {
    const found_next = libfs.LibFsHelperLab.dcacheReaddirCursorRepositionPlan(true);
    try std.testing.expectEqualStrings("fs/libfs.c", found_next.anchor);
    try std.testing.expectEqual(libfs.CursorRepositionMode.reanchor_before_found, found_next.mode);
    try std.testing.expect(found_next.unlinks_existing_cursor);
    try std.testing.expect(found_next.requires_parent_lock);
    try std.testing.expect(found_next.drops_found_reference);
    try std.testing.expect(found_next.keeps_private_data);

    const end_of_scan = libfs.LibFsHelperLab.dcacheReaddirCursorRepositionPlan(false);
    try std.testing.expectEqual(libfs.CursorRepositionMode.unhashed, end_of_scan.mode);
    try std.testing.expect(end_of_scan.unlinks_existing_cursor);
    try std.testing.expect(end_of_scan.requires_parent_lock);
    try std.testing.expect(end_of_scan.drops_found_reference);
    try std.testing.expect(end_of_scan.keeps_private_data);
}

test "phase13 libfs close planning keeps release bookkeeping explicit without claiming teardown" {
    const release = libfs.LibFsHelperLab.dcacheDirClosePlan(true);
    try std.testing.expectEqualStrings("fs/libfs.c", release.anchor);
    try std.testing.expect(release.returns_zero);
    try std.testing.expect(release.calls_dput_on_private_data);
    try std.testing.expect(release.releases_private_cursor_reference);
    try std.testing.expect(release.tolerates_missing_private_data);

    const no_private_data = libfs.LibFsHelperLab.dcacheDirClosePlan(false);
    try std.testing.expect(no_private_data.returns_zero);
    try std.testing.expect(no_private_data.calls_dput_on_private_data);
    try std.testing.expect(!no_private_data.releases_private_cursor_reference);
    try std.testing.expect(no_private_data.tolerates_missing_private_data);
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

test "phase13 libfs transaction planners keep the get-versus-set boundary explicit at page size" {
    const max_get = libfs.LibFsHelperLab.simpleTransactionGetPlan(false, libfs.simple_transaction_limit - 1, true, 0);
    try std.testing.expectEqual(libfs.TransactionAcquireMode.ready, max_get.mode);
    try std.testing.expectEqual(libfs.simple_transaction_limit - 1, max_get.requested_size);
    try std.testing.expectEqual(libfs.simple_transaction_limit - 1, max_get.copied_size);
    try std.testing.expectEqual(libfs.simple_transaction_limit, max_get.staging_capacity);
    try std.testing.expect(max_get.reserves_private_data);
    try std.testing.expect(max_get.requires_release);
    try std.testing.expect(!max_get.keeps_private_data_on_failure);

    const max_set = try libfs.LibFsHelperLab.simpleTransactionSetPlan(libfs.simple_transaction_limit);
    try std.testing.expectEqual(libfs.simple_transaction_limit, max_set.published_size);
    try std.testing.expect(max_set.uses_release_barrier);
    try std.testing.expect(max_set.becomes_readable);
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

test "phase13 libfs simple open planning keeps inode-private handoff explicit" {
    const borrowed = libfs.LibFsHelperLab.simpleOpenPlan(true);
    try std.testing.expectEqualStrings("fs/libfs.c", borrowed.anchor);
    try std.testing.expectEqual(libfs.SimpleOpenPrivateDataSource.inode_private, borrowed.private_data_source);
    try std.testing.expect(borrowed.returns_zero);
    try std.testing.expect(borrowed.stores_inode_private_data);

    const untouched = libfs.LibFsHelperLab.simpleOpenPlan(false);
    try std.testing.expectEqual(libfs.SimpleOpenPrivateDataSource.unchanged, untouched.private_data_source);
    try std.testing.expect(untouched.returns_zero);
    try std.testing.expect(!untouched.stores_inode_private_data);
}

test "phase13 libfs generic_check_addressable planning keeps empty and valid filesystems explicit" {
    const empty = libfs.LibFsHelperLab.genericCheckAddressablePlan(libfs.sector_shift, 0, .{});
    try std.testing.expectEqualStrings("fs/libfs.c", empty.anchor);
    try std.testing.expectEqual(libfs.AddressabilityStatus.empty_filesystem, empty.status);
    try std.testing.expectEqual(@as(u64, 0), empty.last_fs_block);
    try std.testing.expectEqual(@as(u64, 0), empty.last_fs_page);

    const valid = libfs.LibFsHelperLab.genericCheckAddressablePlan(libfs.page_shift, 1024, .{});
    try std.testing.expectEqual(libfs.AddressabilityStatus.addressable, valid.status);
    try std.testing.expectEqual(@as(u64, 1023), valid.last_fs_block);
    try std.testing.expectEqual(@as(u64, 1023), valid.last_fs_page);
    try std.testing.expectEqual(std.math.maxInt(u64) >> 3, valid.sector_index_limit);
    try std.testing.expectEqual(std.math.maxInt(u64), valid.page_index_limit);
}

test "phase13 libfs generic_check_addressable planning rejects invalid bits and tiny synthetic limits" {
    const invalid_low = libfs.LibFsHelperLab.genericCheckAddressablePlan(8, 1, .{});
    try std.testing.expectEqual(libfs.AddressabilityStatus.invalid_blocksize, invalid_low.status);

    const invalid_high = libfs.LibFsHelperLab.genericCheckAddressablePlan(13, 1, .{});
    try std.testing.expectEqual(libfs.AddressabilityStatus.invalid_blocksize, invalid_high.status);

    const sector_overflow = libfs.LibFsHelperLab.genericCheckAddressablePlan(12, 8193, .{
        .sector_index_bits = 16,
        .page_index_bits = 16,
    });
    try std.testing.expectEqual(libfs.AddressabilityStatus.too_large_for_sector_index, sector_overflow.status);
    try std.testing.expectEqual(@as(u64, 8192), sector_overflow.last_fs_block);
    try std.testing.expectEqual(@as(u64, 8191), sector_overflow.sector_index_limit);

    const page_overflow = libfs.LibFsHelperLab.genericCheckAddressablePlan(9, 129, .{
        .sector_index_bits = 32,
        .page_index_bits = 4,
    });
    try std.testing.expectEqual(libfs.AddressabilityStatus.too_large_for_page_index, page_overflow.status);
    try std.testing.expectEqual(@as(u64, 128), page_overflow.last_fs_block);
    try std.testing.expectEqual(@as(u64, 16), page_overflow.last_fs_page);
    try std.testing.expectEqual(@as(u64, 15), page_overflow.page_index_limit);
}