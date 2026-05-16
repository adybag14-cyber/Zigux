const std = @import("std");
const libfs = @import("libfs");

test "descriptor keeps the current bounded helper surface explicit" {
    const descriptor = libfs.LibfsHelperLab.descriptor();

    try std.testing.expectEqualStrings("libfs_helper_lab", descriptor.name);
    try std.testing.expectEqualStrings("fs/libfs.c", descriptor.anchor);
    try std.testing.expect(descriptor.provides_positive_entry_classification);
    try std.testing.expect(descriptor.provides_directory_emptiness_planning);
    try std.testing.expect(descriptor.provides_lookup_planning);
    try std.testing.expect(descriptor.provides_transaction_acquire_planning);
    try std.testing.expect(descriptor.provides_transaction_release_planning);
    try std.testing.expect(descriptor.provides_transaction_publish_planning);
    try std.testing.expect(descriptor.provides_addressability_planning);
    try std.testing.expect(descriptor.provides_offset_seek_planning);
    try std.testing.expect(descriptor.provides_offset_readdir_planning);
    try std.testing.expect(descriptor.provides_offset_add_planning);
    try std.testing.expect(descriptor.provides_offset_remove_planning);
    try std.testing.expect(descriptor.provides_offset_rename_planning);
    try std.testing.expect(descriptor.provides_cursor_reposition_planning);
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

test "lookup offset seek and offset readdir helpers stay reviewable without implying live VFS mutation" {
    const addressable_lookup = libfs.LibfsHelperLab.planSimpleLookup(libfs.name_max);
    const oversized_lookup = libfs.LibfsHelperLab.planSimpleLookup(libfs.name_max + 1);
    const relative_seek = libfs.LibfsHelperLab.planOffsetDirectorySeek(libfs.dir_offset_first, -1, .cur);
    const unsupported_seek = libfs.LibfsHelperLab.planOffsetDirectorySeek(libfs.dir_offset_first, 8, .unsupported);
    const negative_readdir = libfs.LibfsHelperLab.planOffsetReaddir(-1, true);
    const blocked_readdir = libfs.LibfsHelperLab.planOffsetReaddir(libfs.dir_offset_first + 1, false);
    const terminal_readdir = libfs.LibfsHelperLab.planOffsetReaddir(libfs.dir_offset_end_of_directory, true);

    try std.testing.expectEqualStrings("fs/libfs.c", addressable_lookup.anchor);
    try std.testing.expect(addressable_lookup.installs_negative_dentry);
    try std.testing.expectEqual(libfs.LookupMode.name_too_long, oversized_lookup.mode);
    try std.testing.expect(!oversized_lookup.installs_negative_dentry);

    try std.testing.expectEqual(libfs.OffsetSeekStatus.ok, relative_seek.status);
    try std.testing.expectEqual(@as(?i64, 1), relative_seek.resolved_offset);
    try std.testing.expect(!relative_seek.points_at_real_entry_window);
    try std.testing.expectEqual(libfs.OffsetSeekStatus.unsupported_whence, unsupported_seek.status);
    try std.testing.expectEqual(@as(?i64, null), unsupported_seek.resolved_offset);

    try std.testing.expectEqual(libfs.OffsetReaddirStatus.negative_position, negative_readdir.status);
    try std.testing.expectEqual(@as(?libfs.OffsetReaddirMode, null), negative_readdir.mode);
    try std.testing.expect(!negative_readdir.returns_zero);
    try std.testing.expect(!negative_readdir.keeps_current_pos);
    try std.testing.expect(!negative_readdir.treats_end_of_directory_as_terminal);

    try std.testing.expectEqual(libfs.OffsetReaddirStatus.ok, blocked_readdir.status);
    try std.testing.expectEqual(libfs.OffsetReaddirMode.blocked_on_emit_dots, blocked_readdir.mode.?);
    try std.testing.expect(!blocked_readdir.enters_offset_iteration);
    try std.testing.expect(blocked_readdir.keeps_current_pos);

    try std.testing.expectEqual(libfs.OffsetReaddirStatus.ok, terminal_readdir.status);
    try std.testing.expectEqual(libfs.OffsetReaddirMode.ready_at_end_of_directory, terminal_readdir.mode.?);
    try std.testing.expect(!terminal_readdir.enters_offset_iteration);
    try std.testing.expect(terminal_readdir.treats_end_of_directory_as_terminal);
}

test "cursor-open and cursor-precondition helpers stay reviewable without implying live cursor ownership" {
    const open_ready = libfs.LibfsHelperLab.dcacheDirOpenPlan(true);
    try std.testing.expectEqualStrings("fs/libfs.c", open_ready.anchor);
    try std.testing.expectEqual(libfs.CursorOpenStatus.ok, open_ready.status);
    try std.testing.expect(open_ready.allocates_private_cursor);
    try std.testing.expect(open_ready.stores_private_cursor);
    try std.testing.expect(open_ready.zeroes_cursor_position);
    try std.testing.expect(open_ready.returns_zero);

    const open_oom = libfs.LibfsHelperLab.dcacheDirOpenPlan(false);
    try std.testing.expectEqual(libfs.CursorOpenStatus.out_of_memory, open_oom.status);
    try std.testing.expect(!open_oom.allocates_private_cursor);
    try std.testing.expect(!open_oom.stores_private_cursor);
    try std.testing.expect(!open_oom.zeroes_cursor_position);
    try std.testing.expect(!open_oom.returns_zero);

    const blocked = libfs.LibfsHelperLab.dcacheReaddirCursorPreconditionsPlan(libfs.dir_offset_first + 2, false, false);
    try std.testing.expectEqual(libfs.CursorPreconditionStatus.ok, blocked.status);
    try std.testing.expectEqual(libfs.CursorResumeMode.blocked_on_emit_dots, blocked.mode.?);
    try std.testing.expect(blocked.returns_zero);
    try std.testing.expect(!blocked.enters_positive_scan);
    try std.testing.expect(blocked.keeps_current_pos);
    try std.testing.expect(!blocked.requires_private_cursor);

    const first_child = libfs.LibfsHelperLab.dcacheReaddirCursorPreconditionsPlan(libfs.dir_offset_first, true, false);
    try std.testing.expectEqual(libfs.CursorResumeMode.resume_at_first_child, first_child.mode.?);
    try std.testing.expect(first_child.enters_positive_scan);
    try std.testing.expect(!first_child.requires_private_cursor);

    const missing_cursor = libfs.LibfsHelperLab.dcacheReaddirCursorPreconditionsPlan(libfs.dir_offset_first + 3, true, false);
    try std.testing.expectEqual(libfs.CursorResumeMode.missing_private_cursor, missing_cursor.mode.?);
    try std.testing.expect(!missing_cursor.enters_positive_scan);
    try std.testing.expect(missing_cursor.keeps_current_pos);
    try std.testing.expect(missing_cursor.requires_private_cursor);

    const resumed = libfs.LibfsHelperLab.dcacheReaddirCursorPreconditionsPlan(libfs.dir_offset_first + 3, true, true);
    try std.testing.expectEqual(libfs.CursorResumeMode.resume_from_private_cursor, resumed.mode.?);
    try std.testing.expect(resumed.enters_positive_scan);
    try std.testing.expect(!resumed.keeps_current_pos);
    try std.testing.expect(resumed.requires_private_cursor);

    const invalid = libfs.LibfsHelperLab.dcacheReaddirCursorPreconditionsPlan(-1, true, true);
    try std.testing.expectEqual(libfs.CursorPreconditionStatus.negative_position, invalid.status);
    try std.testing.expectEqual(@as(?libfs.CursorResumeMode, null), invalid.mode);
}

test "cursor reposition planner stays reviewable without implying live sibling-list mutation" {
    const unhashed = libfs.LibfsHelperLab.planDcacheCursorReposition(false, .none);
    try std.testing.expectEqualStrings("fs/libfs.c", unhashed.anchor);
    try std.testing.expectEqual(libfs.CursorRepositionStatus.ok, unhashed.status);
    try std.testing.expect(unhashed.uses_hlist_del_init);
    try std.testing.expect(!unhashed.uses_hlist_add_before);
    try std.testing.expect(!unhashed.uses_hlist_add_behind);
    try std.testing.expect(!unhashed.reinserts_cursor);
    try std.testing.expect(unhashed.keeps_private_cursor);
    try std.testing.expect(!unhashed.releases_scan_reference);

    const before = libfs.LibfsHelperLab.planDcacheCursorReposition(true, .before_scan_result);
    try std.testing.expectEqual(libfs.CursorRepositionStatus.ok, before.status);
    try std.testing.expect(before.uses_hlist_del_init);
    try std.testing.expect(before.uses_hlist_add_before);
    try std.testing.expect(!before.uses_hlist_add_behind);
    try std.testing.expect(before.reinserts_cursor);
    try std.testing.expect(before.keeps_private_cursor);
    try std.testing.expect(before.releases_scan_reference);

    const behind = libfs.LibfsHelperLab.planDcacheCursorReposition(true, .behind_scan_result);
    try std.testing.expectEqual(libfs.CursorRepositionStatus.ok, behind.status);
    try std.testing.expect(behind.uses_hlist_del_init);
    try std.testing.expect(!behind.uses_hlist_add_before);
    try std.testing.expect(behind.uses_hlist_add_behind);
    try std.testing.expect(behind.reinserts_cursor);
    try std.testing.expect(behind.keeps_private_cursor);
    try std.testing.expect(behind.releases_scan_reference);

    const missing_placement = libfs.LibfsHelperLab.planDcacheCursorReposition(true, .none);
    try std.testing.expectEqual(libfs.CursorRepositionStatus.missing_reposition_placement, missing_placement.status);
    try std.testing.expect(!missing_placement.reinserts_cursor);
    try std.testing.expect(!missing_placement.releases_scan_reference);

    const missing_target = libfs.LibfsHelperLab.planDcacheCursorReposition(false, .before_scan_result);
    try std.testing.expectEqual(libfs.CursorRepositionStatus.missing_reposition_target, missing_target.status);
    try std.testing.expect(!missing_target.reinserts_cursor);
    try std.testing.expect(!missing_target.releases_scan_reference);
}

test "addressability planner stays reviewable without implying live page-cache ownership" {
    const zero_blocks = libfs.LibfsHelperLab.genericCheckAddressablePlan(7, 0, .{
        .sector_bits = 16,
        .page_index_bits = 16,
    });
    const in_window = libfs.LibfsHelperLab.genericCheckAddressablePlan(12, 8, .{
        .sector_bits = 16,
        .page_index_bits = 8,
    });
    const sector_overflow = libfs.LibfsHelperLab.genericCheckAddressablePlan(10, 2049, .{
        .sector_bits = 12,
        .page_index_bits = 16,
    });

    try std.testing.expectEqualStrings("fs/libfs.c", zero_blocks.anchor);
    try std.testing.expectEqual(libfs.AddressabilityStatus.ok, zero_blocks.status);
    try std.testing.expect(zero_blocks.short_circuits_on_zero_blocks);
    try std.testing.expectEqual(@as(?u64, null), zero_blocks.last_fs_block);
    try std.testing.expectEqual(@as(?u64, null), zero_blocks.last_fs_page);

    try std.testing.expectEqual(libfs.AddressabilityStatus.ok, in_window.status);
    try std.testing.expectEqual(@as(?u64, 7), in_window.last_fs_block);
    try std.testing.expectEqual(@as(?u64, 7), in_window.last_fs_page);
    try std.testing.expectEqual(@as(?u64, 8191), in_window.sector_block_limit);
    try std.testing.expectEqual(@as(?u64, 255), in_window.max_page_index);
    try std.testing.expect(in_window.within_sector_window);
    try std.testing.expect(in_window.within_page_window);

    try std.testing.expectEqual(libfs.AddressabilityStatus.exceeds_sector_window, sector_overflow.status);
    try std.testing.expectEqual(@as(?u64, 2048), sector_overflow.last_fs_block);
    try std.testing.expectEqual(@as(?u64, 512), sector_overflow.last_fs_page);
    try std.testing.expectEqual(@as(?u64, 2047), sector_overflow.sector_block_limit);
    try std.testing.expect(!sector_overflow.within_sector_window);
    try std.testing.expect(sector_overflow.within_page_window);
}

test "offset add and rename helpers stay reviewable as managed-slot planners rather than live directory mutation" {
    try std.testing.expectEqual(libfs.OffsetSlotClass.missing, libfs.LibfsHelperLab.classifyOffsetSlot(null));
    try std.testing.expectEqual(libfs.OffsetSlotClass.out_of_range, libfs.LibfsHelperLab.classifyOffsetSlot(-1));
    try std.testing.expectEqual(libfs.OffsetSlotClass.dot_entry_window, libfs.LibfsHelperLab.classifyOffsetSlot(0));
    try std.testing.expectEqual(libfs.OffsetSlotClass.first_real_entry, libfs.LibfsHelperLab.classifyOffsetSlot(libfs.dir_offset_first));
    try std.testing.expectEqual(libfs.OffsetSlotClass.managed_entry, libfs.LibfsHelperLab.classifyOffsetSlot(libfs.dir_offset_min));
    try std.testing.expectEqual(libfs.OffsetSlotClass.end_of_directory, libfs.LibfsHelperLab.classifyOffsetSlot(libfs.dir_offset_end_of_directory));
    try std.testing.expectEqual(libfs.OffsetSlotClass.out_of_range, libfs.LibfsHelperLab.classifyOffsetSlot(libfs.dir_offset_end_of_directory + 1));

    const add_ok = libfs.LibfsHelperLab.planSimpleOffsetAdd(0, .{ .allocated = libfs.dir_offset_min + 5 });
    const add_busy = libfs.LibfsHelperLab.planSimpleOffsetAdd(0, .busy);
    const add_prepopulated = libfs.LibfsHelperLab.planSimpleOffsetAdd(libfs.dir_offset_min + 2, .{ .allocated = libfs.dir_offset_min + 6 });
    const add_out_of_range = libfs.LibfsHelperLab.planSimpleOffsetAdd(0, .{ .allocated = libfs.dir_offset_first });
    const add_failure = libfs.LibfsHelperLab.planSimpleOffsetAdd(0, .failure);
    const rename_ok = libfs.LibfsHelperLab.planSimpleOffsetRename(libfs.dir_offset_min + 4, libfs.dir_offset_min + 9);
    const rename_missing_destination = libfs.LibfsHelperLab.planSimpleOffsetRename(libfs.dir_offset_min + 5, null);
    const rename_reserved = libfs.LibfsHelperLab.planSimpleOffsetRename(libfs.dir_offset_min + 1, libfs.dir_offset_first);
    const exchange_ok = libfs.LibfsHelperLab.planSimpleOffsetRenameExchange(libfs.dir_offset_min + 2, libfs.dir_offset_min + 8);
    const exchange_missing_source = libfs.LibfsHelperLab.planSimpleOffsetRenameExchange(null, libfs.dir_offset_min + 6);
    const exchange_reserved_source = libfs.LibfsHelperLab.planSimpleOffsetRenameExchange(0, libfs.dir_offset_min + 7);
    const exchange_reserved = libfs.LibfsHelperLab.planSimpleOffsetRenameExchange(libfs.dir_offset_min + 3, libfs.dir_offset_end_of_directory);

    try std.testing.expectEqualStrings("fs/libfs.c", add_ok.anchor);
    try std.testing.expectEqual(libfs.OffsetAddStatus.ok, add_ok.status);
    try std.testing.expect(add_ok.records_offset_in_dentry);
    try std.testing.expect(add_ok.stores_dentry_in_map);
    try std.testing.expect(!add_ok.remaps_allocator_busy_to_no_space);

    try std.testing.expectEqual(libfs.OffsetAddStatus.no_space, add_busy.status);
    try std.testing.expectEqual(@as(?i64, null), add_busy.allocated_offset);
    try std.testing.expect(!add_busy.records_offset_in_dentry);
    try std.testing.expect(!add_busy.stores_dentry_in_map);
    try std.testing.expect(add_busy.remaps_allocator_busy_to_no_space);

    try std.testing.expectEqual(libfs.OffsetAddStatus.dentry_already_has_offset, add_prepopulated.status);
    try std.testing.expectEqual(@as(?i64, null), add_prepopulated.allocated_offset);
    try std.testing.expect(!add_prepopulated.records_offset_in_dentry);
    try std.testing.expect(!add_prepopulated.stores_dentry_in_map);

    try std.testing.expectEqual(libfs.OffsetAddStatus.allocated_offset_out_of_range, add_out_of_range.status);
    try std.testing.expectEqual(@as(?i64, null), add_out_of_range.allocated_offset);
    try std.testing.expect(!add_out_of_range.records_offset_in_dentry);
    try std.testing.expect(!add_out_of_range.stores_dentry_in_map);

    try std.testing.expectEqual(libfs.OffsetAddStatus.allocator_failure, add_failure.status);
    try std.testing.expectEqual(@as(?i64, null), add_failure.allocated_offset);
    try std.testing.expect(!add_failure.records_offset_in_dentry);
    try std.testing.expect(!add_failure.stores_dentry_in_map);

    try std.testing.expectEqualStrings("fs/libfs.c", rename_ok.anchor);
    try std.testing.expectEqual(libfs.OffsetRenameStatus.ok, rename_ok.status);
    try std.testing.expect(rename_ok.clears_destination_offset_before_replace);
    try std.testing.expect(rename_ok.preserves_destination_offset_value);

    try std.testing.expectEqual(libfs.OffsetRenameStatus.missing_destination_offset, rename_missing_destination.status);
    try std.testing.expectEqual(libfs.OffsetSlotClass.missing, rename_missing_destination.destination_slot_class);
    try std.testing.expect(!rename_missing_destination.clears_destination_offset_before_replace);
    try std.testing.expect(!rename_missing_destination.installs_source_at_destination_offset);
    try std.testing.expect(!rename_missing_destination.preserves_destination_offset_value);

    try std.testing.expectEqual(libfs.OffsetRenameStatus.reserved_destination_offset, rename_reserved.status);
    try std.testing.expectEqual(libfs.OffsetSlotClass.first_real_entry, rename_reserved.destination_slot_class);
    try std.testing.expect(!rename_reserved.installs_source_at_destination_offset);

    try std.testing.expectEqual(libfs.OffsetRenameExchangeStatus.ok, exchange_ok.status);
    try std.testing.expect(exchange_ok.swaps_recorded_offsets);
    try std.testing.expect(exchange_ok.rolls_back_destination_store_on_second_store_failure);

    try std.testing.expectEqual(libfs.OffsetRenameExchangeStatus.missing_source_offset, exchange_missing_source.status);
    try std.testing.expectEqual(libfs.OffsetSlotClass.missing, exchange_missing_source.source_slot_class);
    try std.testing.expect(!exchange_missing_source.stores_source_in_destination_map);
    try std.testing.expect(!exchange_missing_source.stores_destination_in_source_map);
    try std.testing.expect(!exchange_missing_source.swaps_recorded_offsets);

    try std.testing.expectEqual(libfs.OffsetRenameExchangeStatus.reserved_source_offset, exchange_reserved_source.status);
    try std.testing.expectEqual(libfs.OffsetSlotClass.dot_entry_window, exchange_reserved_source.source_slot_class);
    try std.testing.expect(!exchange_reserved_source.stores_source_in_destination_map);
    try std.testing.expect(!exchange_reserved_source.stores_destination_in_source_map);
    try std.testing.expect(!exchange_reserved_source.swaps_recorded_offsets);

    try std.testing.expectEqual(libfs.OffsetRenameExchangeStatus.reserved_destination_offset, exchange_reserved.status);
    try std.testing.expectEqual(libfs.OffsetSlotClass.end_of_directory, exchange_reserved.destination_slot_class);
    try std.testing.expect(!exchange_reserved.stores_destination_in_source_map);
}

test "offset remove planning stays reviewable as erase-only lifecycle bookkeeping" {
    const missing = libfs.LibfsHelperLab.planSimpleOffsetRemove(0);
    const managed = libfs.LibfsHelperLab.planSimpleOffsetRemove(libfs.dir_offset_min + 6);
    const reserved = libfs.LibfsHelperLab.planSimpleOffsetRemove(libfs.dir_offset_first);

    try std.testing.expectEqualStrings("fs/libfs.c", missing.anchor);
    try std.testing.expectEqual(libfs.OffsetRemoveStatus.missing_offset, missing.status);
    try std.testing.expectEqual(@as(?libfs.OffsetSlotClass, null), missing.recorded_slot_class);
    try std.testing.expect(!missing.erases_map_entry);
    try std.testing.expect(!missing.clears_recorded_offset);

    try std.testing.expectEqual(libfs.OffsetRemoveStatus.ok, managed.status);
    try std.testing.expectEqual(@as(?libfs.OffsetSlotClass, .managed_entry), managed.recorded_slot_class);
    try std.testing.expect(managed.erases_map_entry);
    try std.testing.expect(managed.clears_recorded_offset);

    try std.testing.expectEqual(libfs.OffsetRemoveStatus.ok, reserved.status);
    try std.testing.expectEqual(@as(?libfs.OffsetSlotClass, .first_real_entry), reserved.recorded_slot_class);
    try std.testing.expect(reserved.erases_map_entry);
    try std.testing.expect(reserved.clears_recorded_offset);
}

test "transaction acquire planner stays helper-only and page-bounded" {
    const acquire = try libfs.LibfsHelperLab.simpleTransactionGetPlan(libfs.simple_transaction_limit, false);
    const empty_acquire = try libfs.LibfsHelperLab.simpleTransactionGetPlan(0, false);

    try std.testing.expectEqualStrings("fs/libfs.c", acquire.anchor);
    try std.testing.expectEqual(libfs.simple_transaction_limit, acquire.requested_write_size);
    try std.testing.expectEqual(libfs.simple_transaction_limit, acquire.transaction_limit);
    try std.testing.expect(acquire.allocates_zeroed_page_backing);
    try std.testing.expect(acquire.stages_single_write_per_open);
    try std.testing.expect(acquire.copies_write_into_private_data);
    try std.testing.expect(acquire.returns_staged_private_data);

    try std.testing.expect(!empty_acquire.copies_write_into_private_data);

    try std.testing.expectError(error.InputTooLarge, libfs.LibfsHelperLab.simpleTransactionGetPlan(libfs.simple_transaction_limit + 1, false));
    try std.testing.expectError(error.PrivateDataAlreadyPresent, libfs.LibfsHelperLab.simpleTransactionGetPlan(4, true));
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

test "transaction publish planner stays helper-only and barrier-ordered" {
    const publish = try libfs.LibfsHelperLab.simpleTransactionSetPlan(libfs.simple_transaction_limit, true);
    const empty_publish = try libfs.LibfsHelperLab.simpleTransactionSetPlan(0, true);

    try std.testing.expectEqualStrings("fs/libfs.c", publish.anchor);
    try std.testing.expectEqual(libfs.simple_transaction_limit, publish.requested_response_size);
    try std.testing.expectEqual(libfs.simple_transaction_limit, publish.transaction_limit);
    try std.testing.expect(publish.requires_private_data);
    try std.testing.expect(publish.publishes_after_barrier);
    try std.testing.expect(publish.reuses_staged_private_data);
    try std.testing.expectEqual(libfs.simple_transaction_limit, publish.published_response_size);
    try std.testing.expectEqual(@as(usize, 0), empty_publish.published_response_size);

    try std.testing.expectError(error.InputTooLarge, libfs.LibfsHelperLab.simpleTransactionSetPlan(libfs.simple_transaction_limit + 1, true));
    try std.testing.expectError(error.MissingPrivateData, libfs.LibfsHelperLab.simpleTransactionSetPlan(4, false));
}
