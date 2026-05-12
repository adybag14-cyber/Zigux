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
    try expectContains(manifest_text, "\"lane_key\": \"P13-L01\"");
    try expectContains(manifest_text, "\"surveyed_commit\": \"master-readback-2026-05-12\"");
    try expectContains(manifest_text, "\"current_libfs_zig_present\": true");
    try expectContains(manifest_text, "\"current_phase13_libfs_test_present\": true");
    try expectContains(manifest_text, "\"current_phase13_libfs_reviewability_present\": true");
    try expectContains(manifest_text, "\"id\": \"phase13-libfs-helper-starter\"");
    try expectContains(manifest_text, "\"id\": \"phase13-libfs-offset-rename-planner\"");
    try expectContains(manifest_text, "\"id\": \"phase13-libfs-reviewability-gate\"");
    try expectContains(manifest_text, "\"id\": \"phase13-build-gate\"");
    try expectContains(manifest_text, "\"id\": \"phase13-libfs-live-dcache-mutation\"");
    try expectContains(manifest_text, "\"id\": \"phase13-libfs-live-inode-state\"");
    try expectContains(manifest_text, "\"status\": \"starter_landed\"");
    try expectContains(manifest_text, "\"status\": \"blocked_on_shared_build_surface\"");
    try expectContains(manifest_text, "simple directory emptiness");
    try expectContains(manifest_text, "offset-based rename planning");
    try expectContains(manifest_text, "live dcache entry insertion");
}
