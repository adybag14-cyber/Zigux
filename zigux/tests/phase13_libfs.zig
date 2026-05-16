const std = @import("std");
const libfs = @import("libfs");
const manifest_text = @embedFile("phase13_libfs_manifest.json");

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

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

test "simple lookup planning keeps the negative-dentry install boundary explicit" {
    const addressable = libfs.LibfsHelperLab.planSimpleLookup(libfs.name_max);
    const oversized = libfs.LibfsHelperLab.planSimpleLookup(libfs.name_max + 1);

    try std.testing.expectEqualStrings("fs/libfs.c", addressable.anchor);
    try std.testing.expectEqual(libfs.LookupMode.negative_dentry_install, addressable.mode);
    try std.testing.expect(addressable.addressable);
    try std.testing.expect(addressable.installs_negative_dentry);

    try std.testing.expectEqual(libfs.LookupMode.name_too_long, oversized.mode);
    try std.testing.expect(!oversized.addressable);
    try std.testing.expect(!oversized.installs_negative_dentry);
}

test "transaction acquire planning bounds the staged write buffer and private-data handoff" {
    const full = try libfs.LibfsHelperLab.simpleTransactionGetPlan(libfs.simple_transaction_limit, false);
    try std.testing.expectEqualStrings("fs/libfs.c", full.anchor);
    try std.testing.expectEqual(libfs.simple_transaction_limit, full.requested_write_size);
    try std.testing.expectEqual(libfs.simple_transaction_limit, full.transaction_limit);
    try std.testing.expect(full.allocates_zeroed_page_backing);
    try std.testing.expect(full.stages_single_write_per_open);
    try std.testing.expect(full.copies_write_into_private_data);
    try std.testing.expect(full.returns_staged_private_data);

    const empty = try libfs.LibfsHelperLab.simpleTransactionGetPlan(0, false);
    try std.testing.expect(!empty.copies_write_into_private_data);

    try std.testing.expectError(error.InputTooLarge, libfs.LibfsHelperLab.simpleTransactionGetPlan(libfs.simple_transaction_limit + 1, false));
    try std.testing.expectError(error.PrivateDataAlreadyPresent, libfs.LibfsHelperLab.simpleTransactionGetPlan(8, true));
}

test "addressability planning keeps zero-block and bounded windows explicit" {
    const zero_blocks = libfs.LibfsHelperLab.genericCheckAddressablePlan(7, 0, .{
        .sector_bits = 16,
        .page_index_bits = 16,
    });
    const in_window = libfs.LibfsHelperLab.genericCheckAddressablePlan(12, 8, .{
        .sector_bits = 16,
        .page_index_bits = 8,
    });

    try std.testing.expectEqualStrings("fs/libfs.c", zero_blocks.anchor);
    try std.testing.expectEqual(libfs.AddressabilityStatus.ok, zero_blocks.status);
    try std.testing.expect(zero_blocks.short_circuits_on_zero_blocks);
    try std.testing.expectEqual(@as(?u64, null), zero_blocks.last_fs_block);
    try std.testing.expectEqual(@as(?u64, null), zero_blocks.last_fs_page);
    try std.testing.expect(zero_blocks.within_sector_window);
    try std.testing.expect(zero_blocks.within_page_window);

    try std.testing.expectEqual(libfs.AddressabilityStatus.ok, in_window.status);
    try std.testing.expectEqual(@as(?u64, 7), in_window.last_fs_block);
    try std.testing.expectEqual(@as(?u64, 7), in_window.last_fs_page);
    try std.testing.expectEqual(@as(?u64, 8191), in_window.sector_block_limit);
    try std.testing.expectEqual(@as(?u64, 255), in_window.max_page_index);
    try std.testing.expect(in_window.within_sector_window);
    try std.testing.expect(in_window.within_page_window);
}

test "addressability planning keeps invalid block sizes and page overflow reviewable" {
    const too_small = libfs.LibfsHelperLab.genericCheckAddressablePlan(8, 1, libfs.native_addressability_window);
    const too_large = libfs.LibfsHelperLab.genericCheckAddressablePlan(libfs.page_shift + 1, 1, libfs.native_addressability_window);
    const page_overflow = libfs.LibfsHelperLab.genericCheckAddressablePlan(12, 9, .{
        .sector_bits = 16,
        .page_index_bits = 3,
    });

    try std.testing.expectEqual(libfs.AddressabilityStatus.invalid_blocksize_bits, too_small.status);
    try std.testing.expectEqual(libfs.AddressabilityStatus.invalid_blocksize_bits, too_large.status);
    try std.testing.expect(!too_small.within_sector_window);
    try std.testing.expect(!too_small.within_page_window);
    try std.testing.expect(!too_large.within_sector_window);
    try std.testing.expect(!too_large.within_page_window);

    try std.testing.expectEqual(libfs.AddressabilityStatus.exceeds_page_window, page_overflow.status);
    try std.testing.expectEqual(@as(?u64, 8), page_overflow.last_fs_block);
    try std.testing.expectEqual(@as(?u64, 8), page_overflow.last_fs_page);
    try std.testing.expect(page_overflow.within_sector_window);
    try std.testing.expect(!page_overflow.within_page_window);
    try std.testing.expectEqual(@as(?u64, 7), page_overflow.max_page_index);
}

test "offset seek planning keeps the bounded window and sentinel paths explicit" {
    const window_plan = libfs.LibfsHelperLab.planOffsetDirectorySeek(0, libfs.dir_offset_first + 4, .set);
    const sentinel_plan = libfs.LibfsHelperLab.planOffsetDirectorySeek(0, libfs.dir_offset_end_of_directory, .set);
    const invalid_plan = libfs.LibfsHelperLab.planOffsetDirectorySeek(0, -1, .set);

    try std.testing.expectEqual(libfs.OffsetSeekStatus.ok, window_plan.status);
    try std.testing.expect(window_plan.points_at_real_entry_window);
    try std.testing.expect(!window_plan.points_at_end_of_directory);

    try std.testing.expectEqual(libfs.OffsetSeekStatus.ok, sentinel_plan.status);
    try std.testing.expect(!sentinel_plan.points_at_real_entry_window);
    try std.testing.expect(sentinel_plan.points_at_end_of_directory);

    try std.testing.expectEqual(libfs.OffsetSeekStatus.negative_offset, invalid_plan.status);
    try std.testing.expectEqual(@as(?i64, null), invalid_plan.resolved_offset);
}

test "offset readdir planning keeps emit-dots gating and eod handoff explicit" {
    const blocked = libfs.LibfsHelperLab.planOffsetReaddir(libfs.dir_offset_first + 4, false);
    try std.testing.expectEqualStrings("fs/libfs.c", blocked.anchor);
    try std.testing.expectEqual(libfs.OffsetReaddirStatus.ok, blocked.status);
    try std.testing.expectEqual(libfs.OffsetReaddirMode.blocked_on_emit_dots, blocked.mode.?);
    try std.testing.expect(blocked.returns_zero);
    try std.testing.expect(blocked.requires_dir_emit_dots);
    try std.testing.expect(!blocked.enters_offset_iteration);
    try std.testing.expect(blocked.keeps_current_pos);
    try std.testing.expect(!blocked.treats_end_of_directory_as_terminal);

    const active = libfs.LibfsHelperLab.planOffsetReaddir(libfs.dir_offset_first + 4, true);
    try std.testing.expectEqual(libfs.OffsetReaddirMode.ready_to_iterate, active.mode.?);
    try std.testing.expect(active.enters_offset_iteration);

    const terminal = libfs.LibfsHelperLab.planOffsetReaddir(libfs.dir_offset_end_of_directory, true);
    try std.testing.expectEqual(libfs.OffsetReaddirMode.ready_at_end_of_directory, terminal.mode.?);
    try std.testing.expect(!terminal.enters_offset_iteration);
    try std.testing.expect(terminal.keeps_current_pos);
    try std.testing.expect(terminal.treats_end_of_directory_as_terminal);

    const invalid = libfs.LibfsHelperLab.planOffsetReaddir(-1, true);
    try std.testing.expectEqual(libfs.OffsetReaddirStatus.negative_position, invalid.status);
    try std.testing.expectEqual(@as(?libfs.OffsetReaddirMode, null), invalid.mode);
}

test "cursor open and cursor precondition planning stay helper-only and explicit" {
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

test "cursor reposition planning keeps the shared del-init plus add-before and add-behind bookkeeping explicit" {
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
}

test "cursor reposition planning flags placement drift while keeping the helper boundary explicit" {
    const missing_placement = libfs.LibfsHelperLab.planDcacheCursorReposition(true, .none);
    try std.testing.expectEqual(libfs.CursorRepositionStatus.missing_reposition_placement, missing_placement.status);
    try std.testing.expect(missing_placement.uses_hlist_del_init);
    try std.testing.expect(!missing_placement.uses_hlist_add_before);
    try std.testing.expect(!missing_placement.uses_hlist_add_behind);
    try std.testing.expect(!missing_placement.reinserts_cursor);
    try std.testing.expect(missing_placement.keeps_private_cursor);
    try std.testing.expect(!missing_placement.releases_scan_reference);

    const missing_target = libfs.LibfsHelperLab.planDcacheCursorReposition(false, .behind_scan_result);
    try std.testing.expectEqual(libfs.CursorRepositionStatus.missing_reposition_target, missing_target.status);
    try std.testing.expect(missing_target.uses_hlist_del_init);
    try std.testing.expect(!missing_target.uses_hlist_add_before);
    try std.testing.expect(!missing_target.uses_hlist_add_behind);
    try std.testing.expect(!missing_target.reinserts_cursor);
    try std.testing.expect(missing_target.keeps_private_cursor);
    try std.testing.expect(!missing_target.releases_scan_reference);
}

test "offset add planning keeps busy-remap and managed-offset boundaries explicit" {
    const ok_plan = libfs.LibfsHelperLab.planSimpleOffsetAdd(0, .{ .allocated = libfs.dir_offset_min + 3 });
    const busy_plan = libfs.LibfsHelperLab.planSimpleOffsetAdd(0, .busy);
    const already_set = libfs.LibfsHelperLab.planSimpleOffsetAdd(libfs.dir_offset_min + 1, .{ .allocated = libfs.dir_offset_min + 4 });
    const out_of_range = libfs.LibfsHelperLab.planSimpleOffsetAdd(0, .{ .allocated = libfs.dir_offset_first });

    try std.testing.expectEqualStrings("fs/libfs.c", ok_plan.anchor);
    try std.testing.expectEqual(libfs.OffsetAddStatus.ok, ok_plan.status);
    try std.testing.expectEqual(@as(?i64, libfs.dir_offset_min + 3), ok_plan.allocated_offset);
    try std.testing.expect(ok_plan.records_offset_in_dentry);
    try std.testing.expect(ok_plan.stores_dentry_in_map);
    try std.testing.expect(!ok_plan.remaps_allocator_busy_to_no_space);

    try std.testing.expectEqual(libfs.OffsetAddStatus.no_space, busy_plan.status);
    try std.testing.expectEqual(@as(?i64, null), busy_plan.allocated_offset);
    try std.testing.expect(busy_plan.remaps_allocator_busy_to_no_space);

    try std.testing.expectEqual(libfs.OffsetAddStatus.dentry_already_has_offset, already_set.status);
    try std.testing.expectEqual(@as(?i64, null), already_set.allocated_offset);
    try std.testing.expect(!already_set.records_offset_in_dentry);
    try std.testing.expect(!already_set.stores_dentry_in_map);

    try std.testing.expectEqual(libfs.OffsetAddStatus.allocated_offset_out_of_range, out_of_range.status);
    try std.testing.expectEqual(@as(?i64, null), out_of_range.allocated_offset);
    try std.testing.expect(!out_of_range.records_offset_in_dentry);
}

test "offset remove planning keeps zero-offset noop and managed-slot erase explicit" {
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

test "transaction publish planning validates response size and publish bookkeeping" {
    const plan = try libfs.LibfsHelperLab.simpleTransactionSetPlan(libfs.simple_transaction_limit, true);
    try std.testing.expectEqualStrings("fs/libfs.c", plan.anchor);
    try std.testing.expectEqual(libfs.simple_transaction_limit, plan.requested_response_size);
    try std.testing.expectEqual(libfs.simple_transaction_limit, plan.transaction_limit);
    try std.testing.expect(plan.requires_private_data);
    try std.testing.expect(plan.publishes_after_barrier);
    try std.testing.expectEqual(libfs.simple_transaction_limit, plan.published_response_size);

    const empty = try libfs.LibfsHelperLab.simpleTransactionSetPlan(0, true);
    try std.testing.expectEqual(@as(usize, 0), empty.published_response_size);

    try std.testing.expectError(error.InputTooLarge, libfs.LibfsHelperLab.simpleTransactionSetPlan(libfs.simple_transaction_limit + 1, true));
    try std.testing.expectError(error.MissingPrivateData, libfs.LibfsHelperLab.simpleTransactionSetPlan(8, false));
}

test "offset rename planning keeps managed destinations and sentinel rejection explicit" {
    const ok_plan = libfs.LibfsHelperLab.planSimpleOffsetRename(libfs.dir_offset_min + 1, libfs.dir_offset_min + 7);
    const missing_destination = libfs.LibfsHelperLab.planSimpleOffsetRename(libfs.dir_offset_min + 1, null);
    const reserved_destination = libfs.LibfsHelperLab.planSimpleOffsetRename(libfs.dir_offset_min + 1, libfs.dir_offset_first);

    try std.testing.expectEqualStrings("fs/libfs.c", ok_plan.anchor);
    try std.testing.expectEqual(libfs.OffsetRenameStatus.ok, ok_plan.status);
    try std.testing.expect(ok_plan.removes_source_from_old_map);
    try std.testing.expect(ok_plan.clears_destination_offset_before_replace);
    try std.testing.expect(ok_plan.installs_source_at_destination_offset);
    try std.testing.expect(ok_plan.preserves_destination_offset_value);

    try std.testing.expectEqual(libfs.OffsetRenameStatus.missing_destination_offset, missing_destination.status);
    try std.testing.expect(!missing_destination.clears_destination_offset_before_replace);
    try std.testing.expect(!missing_destination.installs_source_at_destination_offset);

    try std.testing.expectEqual(libfs.OffsetRenameStatus.reserved_destination_offset, reserved_destination.status);
    try std.testing.expectEqual(libfs.OffsetSlotClass.first_real_entry, reserved_destination.destination_slot_class);
    try std.testing.expect(!reserved_destination.preserves_destination_offset_value);
}

test "offset rename exchange planning keeps managed-slot swap and rollback expectations explicit" {
    const ok_plan = libfs.LibfsHelperLab.planSimpleOffsetRenameExchange(libfs.dir_offset_min + 2, libfs.dir_offset_min + 8);
    const missing_source = libfs.LibfsHelperLab.planSimpleOffsetRenameExchange(null, libfs.dir_offset_min + 3);
    const reserved_destination = libfs.LibfsHelperLab.planSimpleOffsetRenameExchange(libfs.dir_offset_min + 3, libfs.dir_offset_end_of_directory);

    try std.testing.expectEqualStrings("fs/libfs.c", ok_plan.anchor);
    try std.testing.expectEqual(libfs.OffsetRenameExchangeStatus.ok, ok_plan.status);
    try std.testing.expect(ok_plan.stores_source_in_destination_map);
    try std.testing.expect(ok_plan.stores_destination_in_source_map);
    try std.testing.expect(ok_plan.swaps_recorded_offsets);
    try std.testing.expect(ok_plan.preserves_existing_offset_values);
    try std.testing.expect(ok_plan.rolls_back_destination_store_on_second_store_failure);

    try std.testing.expectEqual(libfs.OffsetRenameExchangeStatus.missing_source_offset, missing_source.status);
    try std.testing.expect(!missing_source.stores_source_in_destination_map);

    try std.testing.expectEqual(libfs.OffsetRenameExchangeStatus.reserved_destination_offset, reserved_destination.status);
    try std.testing.expectEqual(libfs.OffsetSlotClass.end_of_directory, reserved_destination.destination_slot_class);
    try std.testing.expect(!reserved_destination.swaps_recorded_offsets);
}

test "phase13 libfs manifest records the current helper-first filesystem packet" {
    try expectContains(manifest_text, "\"lane_key\": \"P13-L04\"");
    try expectContains(manifest_text, "\"surveyed_commit\": \"master-readback-2026-05-15\"");
    try expectContains(manifest_text, "\"current_libfs_zig_present\": true");
    try expectContains(manifest_text, "\"current_phase13_libfs_test_present\": true");
    try expectContains(manifest_text, "\"current_phase13_libfs_reviewability_present\": true");
    try expectContains(manifest_text, "\"id\": \"phase13-libfs-helper-starter\"");
    try expectContains(manifest_text, "\"id\": \"phase13-libfs-offset-add-planner\"");
    try expectContains(manifest_text, "\"id\": \"phase13-libfs-offset-remove-planner\"");
    try expectContains(manifest_text, "\"id\": \"phase13-libfs-offset-rename-planner\"");
    try expectContains(manifest_text, "\"id\": \"phase13-libfs-transaction-acquire-helper\"");
    try expectContains(manifest_text, "\"id\": \"phase13-libfs-transaction-release-helper\"");
    try expectContains(manifest_text, "\"id\": \"phase13-libfs-transaction-publish-helper\"");
    try expectContains(manifest_text, "\"id\": \"phase13-libfs-addressability-helper\"");
    try expectContains(manifest_text, "\"id\": \"phase13-libfs-dcache-cursor-preconditions\"");
    try expectContains(manifest_text, "\"id\": \"phase13-libfs-dcache-cursor-reposition-bookkeeping\"");
    try expectContains(manifest_text, "\"id\": \"phase13-libfs-reviewability-gate\"");
    try expectContains(manifest_text, "\"id\": \"phase13-build-gate\"");
    try expectContains(manifest_text, "\"id\": \"phase13-libfs-live-dcache-mutation\"");
    try expectContains(manifest_text, "\"id\": \"phase13-libfs-live-inode-state\"");
    try expectContains(manifest_text, "\"status\": \"starter_landed\"");
    try expectContains(manifest_text, "\"status\": \"blocked_on_shared_build_surface\"");
    try expectContains(manifest_text, "simple directory emptiness");
    try expectContains(manifest_text, "transaction acquire planning");
    try expectContains(manifest_text, "simple_transaction_release()");
    try expectContains(manifest_text, "transaction publish planning");
    try expectContains(manifest_text, "generic_check_addressable()");
    try expectContains(manifest_text, "simple_offset_add()");
    try expectContains(manifest_text, "simple_offset_remove()");
    try expectContains(manifest_text, "offset-add planning");
    try expectContains(manifest_text, "offset-remove planning");
    try expectContains(manifest_text, "simple_transaction_get()");
    try expectContains(manifest_text, "offset-based rename planning");
    try expectContains(manifest_text, "dcache_dir_open()");
    try expectContains(manifest_text, "dcache_readdir()");
    try expectContains(manifest_text, "hlist_del_init()");
    try expectContains(manifest_text, "hlist_add_before()");
    try expectContains(manifest_text, "hlist_add_behind()");
    try expectContains(manifest_text, "live dcache entry insertion");
}
