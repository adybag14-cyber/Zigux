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
    try std.testing.expect(descriptor.provides_offset_seek_planning);
    try std.testing.expect(descriptor.provides_offset_readdir_planning);
    try std.testing.expect(descriptor.provides_offset_rename_planning);
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

test "offset rename helpers stay reviewable as managed-slot planners rather than live directory mutation" {
    try std.testing.expectEqual(libfs.OffsetSlotClass.missing, libfs.LibfsHelperLab.classifyOffsetSlot(null));
    try std.testing.expectEqual(libfs.OffsetSlotClass.out_of_range, libfs.LibfsHelperLab.classifyOffsetSlot(-1));
    try std.testing.expectEqual(libfs.OffsetSlotClass.dot_entry_window, libfs.LibfsHelperLab.classifyOffsetSlot(0));
    try std.testing.expectEqual(libfs.OffsetSlotClass.first_real_entry, libfs.LibfsHelperLab.classifyOffsetSlot(libfs.dir_offset_first));
    try std.testing.expectEqual(libfs.OffsetSlotClass.managed_entry, libfs.LibfsHelperLab.classifyOffsetSlot(libfs.dir_offset_min));
    try std.testing.expectEqual(libfs.OffsetSlotClass.end_of_directory, libfs.LibfsHelperLab.classifyOffsetSlot(libfs.dir_offset_end_of_directory));
    try std.testing.expectEqual(libfs.OffsetSlotClass.out_of_range, libfs.LibfsHelperLab.classifyOffsetSlot(libfs.dir_offset_end_of_directory + 1));

    const rename_ok = libfs.LibfsHelperLab.planSimpleOffsetRename(libfs.dir_offset_min + 4, libfs.dir_offset_min + 9);
    const rename_missing_destination = libfs.LibfsHelperLab.planSimpleOffsetRename(libfs.dir_offset_min + 5, null);
    const rename_reserved = libfs.LibfsHelperLab.planSimpleOffsetRename(libfs.dir_offset_min + 1, libfs.dir_offset_first);
    const exchange_ok = libfs.LibfsHelperLab.planSimpleOffsetRenameExchange(libfs.dir_offset_min + 2, libfs.dir_offset_min + 8);
    const exchange_missing_source = libfs.LibfsHelperLab.planSimpleOffsetRenameExchange(null, libfs.dir_offset_min + 6);
    const exchange_reserved_source = libfs.LibfsHelperLab.planSimpleOffsetRenameExchange(0, libfs.dir_offset_min + 7);
    const exchange_reserved = libfs.LibfsHelperLab.planSimpleOffsetRenameExchange(libfs.dir_offset_min + 3, libfs.dir_offset_end_of_directory);

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
    try std.testing.expectEqual(libfs.simple_transaction_limit, publish.published_response_size);
    try std.testing.expectEqual(@as(usize, 0), empty_publish.published_response_size);

    try std.testing.expectError(error.InputTooLarge, libfs.LibfsHelperLab.simpleTransactionSetPlan(libfs.simple_transaction_limit + 1, true));
    try std.testing.expectError(error.MissingPrivateData, libfs.LibfsHelperLab.simpleTransactionSetPlan(4, false));
}
