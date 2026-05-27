const std = @import("std");

pub const dir_offset_first: i64 = 2;
pub const dir_offset_end_of_directory: i64 = std.math.maxInt(i64);

pub const DcacheCursorPacketDescriptor = struct {
    anchor: []const u8,
    provides_dcache_dir_open_planning: bool,
    provides_dcache_readdir_preconditions: bool,
    keeps_cursor_private: bool,
    claims_live_cursor_dentry_traversal: bool,
    claims_lock_ordering: bool,
};

pub const descriptor = DcacheCursorPacketDescriptor{
    .anchor = "fs/libfs.c",
    .provides_dcache_dir_open_planning = true,
    .provides_dcache_readdir_preconditions = true,
    .keeps_cursor_private = true,
    .claims_live_cursor_dentry_traversal = false,
    .claims_lock_ordering = false,
};

pub const DcacheDirOpenStatus = enum {
    ok,
    missing_shared_inode,
};

pub const DcacheDirOpenPlan = struct {
    anchor: []const u8,
    shared_inode_present: bool,
    caller_supplies_private_cursor: bool,
    status: DcacheDirOpenStatus,
    installs_private_cursor: bool,
    may_reuse_existing_cursor: bool,
    keeps_cursor_private: bool,
    claims_lock_ordering: bool,
    mutates_dcache_siblings: bool,
};

pub const DcacheReaddirStatus = enum {
    ok,
    negative_position,
    missing_private_cursor,
};

pub const DcacheReaddirMode = enum {
    blocked_on_emit_dots,
    ready_to_scan,
    ready_at_end_of_directory,
};

pub const DcacheReaddirPlan = struct {
    anchor: []const u8,
    current_pos: i64,
    emit_dots_completed: bool,
    private_cursor_present: bool,
    status: DcacheReaddirStatus,
    mode: ?DcacheReaddirMode,
    requires_dir_emit_dots: bool,
    enters_cursor_scan: bool,
    keeps_current_pos: bool,
    points_at_end_of_directory: bool,
    claims_sibling_traversal: bool,
    claims_lock_ordering: bool,
};

pub fn planDcacheDirOpen(shared_inode_present: bool, caller_supplies_private_cursor: bool) DcacheDirOpenPlan {
    if (!shared_inode_present) {
        return .{
            .anchor = descriptor.anchor,
            .shared_inode_present = false,
            .caller_supplies_private_cursor = caller_supplies_private_cursor,
            .status = .missing_shared_inode,
            .installs_private_cursor = false,
            .may_reuse_existing_cursor = false,
            .keeps_cursor_private = true,
            .claims_lock_ordering = false,
            .mutates_dcache_siblings = false,
        };
    }

    return .{
        .anchor = descriptor.anchor,
        .shared_inode_present = true,
        .caller_supplies_private_cursor = caller_supplies_private_cursor,
        .status = .ok,
        .installs_private_cursor = !caller_supplies_private_cursor,
        .may_reuse_existing_cursor = caller_supplies_private_cursor,
        .keeps_cursor_private = true,
        .claims_lock_ordering = false,
        .mutates_dcache_siblings = false,
    };
}

pub fn planDcacheReaddir(current_pos: i64, emit_dots_completed: bool, private_cursor_present: bool) DcacheReaddirPlan {
    if (current_pos < 0) {
        return .{
            .anchor = descriptor.anchor,
            .current_pos = current_pos,
            .emit_dots_completed = emit_dots_completed,
            .private_cursor_present = private_cursor_present,
            .status = .negative_position,
            .mode = null,
            .requires_dir_emit_dots = false,
            .enters_cursor_scan = false,
            .keeps_current_pos = true,
            .points_at_end_of_directory = false,
            .claims_sibling_traversal = false,
            .claims_lock_ordering = false,
        };
    }

    if (!private_cursor_present) {
        return .{
            .anchor = descriptor.anchor,
            .current_pos = current_pos,
            .emit_dots_completed = emit_dots_completed,
            .private_cursor_present = false,
            .status = .missing_private_cursor,
            .mode = null,
            .requires_dir_emit_dots = false,
            .enters_cursor_scan = false,
            .keeps_current_pos = true,
            .points_at_end_of_directory = false,
            .claims_sibling_traversal = false,
            .claims_lock_ordering = false,
        };
    }

    if (!emit_dots_completed) {
        return .{
            .anchor = descriptor.anchor,
            .current_pos = current_pos,
            .emit_dots_completed = false,
            .private_cursor_present = true,
            .status = .ok,
            .mode = .blocked_on_emit_dots,
            .requires_dir_emit_dots = true,
            .enters_cursor_scan = false,
            .keeps_current_pos = true,
            .points_at_end_of_directory = false,
            .claims_sibling_traversal = false,
            .claims_lock_ordering = false,
        };
    }

    if (current_pos == dir_offset_end_of_directory) {
        return .{
            .anchor = descriptor.anchor,
            .current_pos = current_pos,
            .emit_dots_completed = true,
            .private_cursor_present = true,
            .status = .ok,
            .mode = .ready_at_end_of_directory,
            .requires_dir_emit_dots = false,
            .enters_cursor_scan = false,
            .keeps_current_pos = true,
            .points_at_end_of_directory = true,
            .claims_sibling_traversal = false,
            .claims_lock_ordering = false,
        };
    }

    return .{
        .anchor = descriptor.anchor,
        .current_pos = current_pos,
        .emit_dots_completed = true,
        .private_cursor_present = true,
        .status = .ok,
        .mode = .ready_to_scan,
        .requires_dir_emit_dots = false,
        .enters_cursor_scan = current_pos >= dir_offset_first,
        .keeps_current_pos = false,
        .points_at_end_of_directory = false,
        .claims_sibling_traversal = false,
        .claims_lock_ordering = false,
    };
}
