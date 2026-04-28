const std = @import("std");

pub const page_size: u32 = 4096;
pub const name_max: u32 = 255;
pub const simple_transaction_limit: usize = page_size;

pub const ModuleDescriptor = struct {
    name: []const u8,
    anchor: []const u8,
    provides_statfs_defaults: bool,
    provides_lookup_policy: bool,
    provides_buffer_copy_helpers: bool,
    provides_offset_seek_helpers: bool,
    provides_directory_emit_planning: bool,
    provides_directory_cursor_preconditions: bool,
    provides_directory_cursor_reposition_planning: bool,
    provides_transaction_buffer_planning: bool,
    provides_transaction_read_release_planning: bool,
    touches_live_dcache: bool,
    touches_live_inode_state: bool,
};

pub const FsId = struct {
    val: [2]u32,

    pub fn fromU64(value: u64) FsId {
        return .{
            .val = .{
                @intCast(value & std.math.maxInt(u32)),
                @intCast(value >> 32),
            },
        };
    }
};

pub const StatFsSummary = struct {
    anchor: []const u8,
    fsid: FsId,
    fs_type: u64,
    block_size: u32,
    name_len_max: u32,
};

pub const LookupInput = struct {
    name_len: usize,
    has_dentry_operations: bool,
    dont_cache_negative: bool,
    directory_is_casefolded: bool,
};

pub const LookupDecision = struct {
    anchor: []const u8,
    should_mark_dont_cache: bool,
    should_add_negative_dentry: bool,
    returns_null: bool,
    casefold_passthrough: bool,
};

pub const BufferWindow = struct {
    anchor: []const u8,
    start: usize,
    len: usize,
};

pub const BufferTransfer = struct {
    anchor: []const u8,
    copied: usize,
    new_pos: i64,
};

pub const SeekWhence = enum(i32) {
    set = 0,
    cur = 1,
    end = 2,
    data = 3,
    hole = 4,
};

pub const DirectorySeekPlan = struct {
    anchor: []const u8,
    new_pos: i64,
    changed: bool,
    requires_positive_scan: bool,
    stays_in_dots_window: bool,
};

pub const DirectoryEmitPlan = struct {
    anchor: []const u8,
    new_pos: i64,
    entered_positive_scan: bool,
    emitted_any_entries: bool,
    stays_in_dots_window: bool,
    should_stop: bool,
};

pub const CursorOpenMode = enum {
    ready,
    out_of_memory,
};

pub const CursorOpenPlan = struct {
    anchor: []const u8,
    mode: CursorOpenMode,
    allocates_private_cursor: bool,
    stores_private_data: bool,
};

pub const CursorResumeSource = enum {
    none,
    first_child,
    stored_cursor_next,
};

pub const CursorPreconditionMode = enum {
    ready,
    blocked_on_emit_dots,
    missing_private_cursor,
};

pub const CursorPreconditionsPlan = struct {
    anchor: []const u8,
    mode: CursorPreconditionMode,
    resume_source: CursorResumeSource,
    requires_dir_emit_dots: bool,
    can_scan_positives: bool,
    keeps_private_data: bool,
    defers_cursor_reposition: bool,
};

pub const CursorRepositionPlacement = enum {
    none,
    before_scan_result,
    behind_scan_result,
};

pub const CursorRepositionPlan = struct {
    anchor: []const u8,
    placement: CursorRepositionPlacement,
    uses_hlist_del_init: bool,
    reinserts_cursor: bool,
    keeps_private_data: bool,
    releases_scan_reference: bool,
};

pub const TransactionAcquireMode = enum {
    ready,
    request_too_large,
    out_of_memory,
    already_open,
    copy_fault,
};

pub const TransactionAcquirePlan = struct {
    anchor: []const u8,
    mode: TransactionAcquireMode,
    requested_size: usize,
    copied_size: usize,
    staging_capacity: usize,
    reserves_private_data: bool,
    requires_release: bool,
    keeps_private_data_on_failure: bool,
};

pub const TransactionPublishPlan = struct {
    anchor: []const u8,
    published_size: usize,
    uses_release_barrier: bool,
    becomes_readable: bool,
};

pub const TransactionReadPlan = struct {
    anchor: []const u8,
    readable_size: usize,
    returns_eof: bool,
    delegates_to_simple_read_from_buffer: bool,
    keeps_private_data: bool,
    leaves_pos_unchanged: bool,
};

pub const TransactionReleasePlan = struct {
    anchor: []const u8,
    returns_zero: bool,
    frees_private_data: bool,
    had_private_data: bool,
};

pub const LibFsHelperLab = struct {
    pub fn descriptor() ModuleDescriptor {
        return .{
            .name = "libfs_helper_lab",
            .anchor = "fs/libfs.c",
            .provides_statfs_defaults = true,
            .provides_lookup_policy = true,
            .provides_buffer_copy_helpers = true,
            .provides_offset_seek_helpers = true,
            .provides_directory_emit_planning = true,
            .provides_directory_cursor_preconditions = true,
            .provides_directory_cursor_reposition_planning = true,
            .provides_transaction_buffer_planning = true,
            .provides_transaction_read_release_planning = true,
            .touches_live_dcache = false,
            .touches_live_inode_state = false,
        };
    }

    pub fn simpleStatFs(encoded_device_id: u64, magic: u64) StatFsSummary {
        return .{
            .anchor = descriptor().anchor,
            .fsid = FsId.fromU64(encoded_device_id),
            .fs_type = magic,
            .block_size = page_size,
            .name_len_max = name_max,
        };
    }

    pub fn alwaysDeleteDentry() bool {
        return true;
    }

    pub fn simpleLookup(input: LookupInput) !LookupDecision {
        if (input.name_len > name_max) {
            return error.NameTooLong;
        }

        const should_mark_dont_cache = !input.has_dentry_operations and !input.dont_cache_negative;
        const casefold_passthrough = input.directory_is_casefolded;

        return .{
            .anchor = descriptor().anchor,
            .should_mark_dont_cache = should_mark_dont_cache,
            .should_add_negative_dentry = !casefold_passthrough,
            .returns_null = true,
            .casefold_passthrough = casefold_passthrough,
        };
    }

    fn clampBufferWindow(pos: i64, count: usize, available: usize) !BufferWindow {
        if (pos < 0) {
            return error.InvalidOffset;
        }

        const start: usize = @intCast(pos);
        if (start >= available or count == 0) {
            return .{
                .anchor = descriptor().anchor,
                .start = start,
                .len = 0,
            };
        }

        return .{
            .anchor = descriptor().anchor,
            .start = start,
            .len = @min(count, available - start),
        };
    }

    pub fn simpleReadFromBuffer(destination: []u8, pos: *i64, source: []const u8, uncopied_tail: usize) !BufferTransfer {
        const window = try clampBufferWindow(pos.*, destination.len, source.len);
        if (window.len == 0) {
            return .{
                .anchor = window.anchor,
                .copied = 0,
                .new_pos = pos.*,
            };
        }

        const uncopied = @min(uncopied_tail, window.len);
        if (uncopied == window.len) {
            return error.CopyFault;
        }

        const copied = window.len - uncopied;
        @memcpy(destination[0..copied], source[window.start .. window.start + copied]);
        pos.* += @intCast(copied);
        return .{
            .anchor = window.anchor,
            .copied = copied,
            .new_pos = pos.*,
        };
    }

    pub fn simpleWriteToBuffer(destination: []u8, pos: *i64, source: []const u8, uncopied_tail: usize) !BufferTransfer {
        const window = try clampBufferWindow(pos.*, source.len, destination.len);
        if (window.len == 0) {
            return .{
                .anchor = window.anchor,
                .copied = 0,
                .new_pos = pos.*,
            };
        }

        const uncopied = @min(uncopied_tail, window.len);
        if (uncopied == window.len) {
            return error.CopyFault;
        }

        const copied = window.len - uncopied;
        @memcpy(destination[window.start .. window.start + copied], source[0..copied]);
        pos.* += @intCast(copied);
        return .{
            .anchor = window.anchor,
            .copied = copied,
            .new_pos = pos.*,
        };
    }

    pub fn memoryReadFromBuffer(destination: []u8, pos: *i64, source: []const u8) !BufferTransfer {
        const window = try clampBufferWindow(pos.*, destination.len, source.len);
        if (window.len == 0) {
            return .{
                .anchor = window.anchor,
                .copied = 0,
                .new_pos = pos.*,
            };
        }

        @memcpy(destination[0..window.len], source[window.start .. window.start + window.len]);
        pos.* += @intCast(window.len);
        return .{
            .anchor = window.anchor,
            .copied = window.len,
            .new_pos = pos.*,
        };
    }

    fn resolveSeekTarget(current_pos: i64, offset: i64, whence: SeekWhence) !i64 {
        return switch (whence) {
            .set => if (offset < 0) error.InvalidOffset else offset,
            .cur => blk: {
                const target = std.math.add(i64, current_pos, offset) catch return error.InvalidOffset;
                if (target < 0) {
                    return error.InvalidOffset;
                }
                break :blk target;
            },
            else => error.UnsupportedWhence,
        };
    }

    pub fn dcacheDirSeekPlan(current_pos: i64, offset: i64, whence: SeekWhence) !DirectorySeekPlan {
        const target = try resolveSeekTarget(current_pos, offset, whence);
        return .{
            .anchor = descriptor().anchor,
            .new_pos = target,
            .changed = target != current_pos,
            .requires_positive_scan = target != current_pos and target > 2,
            .stays_in_dots_window = target <= 2,
        };
    }

    pub fn offsetDirSeekPlan(current_pos: i64, offset: i64, whence: SeekWhence, max_pos: i64) !DirectorySeekPlan {
        const target = try resolveSeekTarget(current_pos, offset, whence);
        if (target > max_pos) {
            return error.PositionOutOfRange;
        }

        return .{
            .anchor = descriptor().anchor,
            .new_pos = target,
            .changed = target != current_pos,
            .requires_positive_scan = false,
            .stays_in_dots_window = target <= 2,
        };
    }

    pub fn dcacheReaddirEmitPlan(current_pos: i64, emit_dots_result: bool, emitted_entries: usize) !DirectoryEmitPlan {
        if (current_pos < 0) {
            return error.InvalidOffset;
        }

        if (current_pos < 2 and !emit_dots_result) {
            return .{
                .anchor = descriptor().anchor,
                .new_pos = current_pos,
                .entered_positive_scan = false,
                .emitted_any_entries = false,
                .stays_in_dots_window = true,
                .should_stop = true,
            };
        }

        const base_pos: i64 = if (current_pos < 2) 2 else current_pos;
        const entry_advance: i64 = std.math.cast(i64, emitted_entries) orelse return error.PositionOutOfRange;
        const new_pos = std.math.add(i64, base_pos, entry_advance) catch return error.PositionOutOfRange;

        return .{
            .anchor = descriptor().anchor,
            .new_pos = new_pos,
            .entered_positive_scan = true,
            .emitted_any_entries = emitted_entries != 0,
            .stays_in_dots_window = new_pos <= 2,
            .should_stop = emitted_entries == 0,
        };
    }

    pub fn dcacheDirOpenPlan(allocation_succeeds: bool) CursorOpenPlan {
        return .{
            .anchor = descriptor().anchor,
            .mode = if (allocation_succeeds) .ready else .out_of_memory,
            .allocates_private_cursor = allocation_succeeds,
            .stores_private_data = allocation_succeeds,
        };
    }

    pub fn dcacheReaddirCursorPreconditionsPlan(current_pos: i64, has_private_cursor: bool, emit_dots_result: bool) !CursorPreconditionsPlan {
        if (current_pos < 0) {
            return error.InvalidOffset;
        }

        if (!has_private_cursor) {
            return .{
                .anchor = descriptor().anchor,
                .mode = .missing_private_cursor,
                .resume_source = .none,
                .requires_dir_emit_dots = true,
                .can_scan_positives = false,
                .keeps_private_data = false,
                .defers_cursor_reposition = false,
            };
        }

        if (current_pos < 2 and !emit_dots_result) {
            return .{
                .anchor = descriptor().anchor,
                .mode = .blocked_on_emit_dots,
                .resume_source = .none,
                .requires_dir_emit_dots = true,
                .can_scan_positives = false,
                .keeps_private_data = true,
                .defers_cursor_reposition = false,
            };
        }

        return .{
            .anchor = descriptor().anchor,
            .mode = .ready,
            .resume_source = if (current_pos <= 2) .first_child else .stored_cursor_next,
            .requires_dir_emit_dots = true,
            .can_scan_positives = true,
            .keeps_private_data = true,
            .defers_cursor_reposition = true,
        };
    }

    pub fn dcacheCursorRepositionPlan(has_scan_result: bool, placement: CursorRepositionPlacement) !CursorRepositionPlan {
        if (has_scan_result and placement == .none) {
            return error.MissingRepositionPlacement;
        }

        if (!has_scan_result and placement != .none) {
            return error.MissingRepositionTarget;
        }

        return .{
            .anchor = descriptor().anchor,
            .placement = placement,
            .uses_hlist_del_init = true,
            .reinserts_cursor = has_scan_result,
            .keeps_private_data = true,
            .releases_scan_reference = has_scan_result,
        };
    }

    pub fn simpleTransactionGetPlan(has_private_data: bool, request_size: usize, allocation_succeeds: bool, uncopied_tail: usize) TransactionAcquirePlan {
        const uncopied = @min(uncopied_tail, request_size);

        if (request_size > simple_transaction_limit - 1) {
            return .{
                .anchor = descriptor().anchor,
                .mode = .request_too_large,
                .requested_size = request_size,
                .copied_size = 0,
                .staging_capacity = simple_transaction_limit,
                .reserves_private_data = false,
                .requires_release = false,
                .keeps_private_data_on_failure = false,
            };
        }

        if (!allocation_succeeds) {
            return .{
                .anchor = descriptor().anchor,
                .mode = .out_of_memory,
                .requested_size = request_size,
                .copied_size = 0,
                .staging_capacity = simple_transaction_limit,
                .reserves_private_data = false,
                .requires_release = false,
                .keeps_private_data_on_failure = false,
            };
        }

        if (has_private_data) {
            return .{
                .anchor = descriptor().anchor,
                .mode = .already_open,
                .requested_size = request_size,
                .copied_size = 0,
                .staging_capacity = simple_transaction_limit,
                .reserves_private_data = false,
                .requires_release = false,
                .keeps_private_data_on_failure = false,
            };
        }

        if (uncopied != 0) {
            return .{
                .anchor = descriptor().anchor,
                .mode = .copy_fault,
                .requested_size = request_size,
                .copied_size = request_size - uncopied,
                .staging_capacity = simple_transaction_limit,
                .reserves_private_data = true,
                .requires_release = true,
                .keeps_private_data_on_failure = true,
            };
        }

        return .{
            .anchor = descriptor().anchor,
            .mode = .ready,
            .requested_size = request_size,
            .copied_size = request_size,
            .staging_capacity = simple_transaction_limit,
            .reserves_private_data = true,
            .requires_release = true,
            .keeps_private_data_on_failure = false,
        };
    }

    pub fn simpleTransactionSetPlan(published_size: usize) !TransactionPublishPlan {
        if (published_size > simple_transaction_limit) {
            return error.TransactionTooLarge;
        }

        return .{
            .anchor = descriptor().anchor,
            .published_size = published_size,
            .uses_release_barrier = true,
            .becomes_readable = true,
        };
    }

    pub fn simpleTransactionReadPlan(has_private_data: bool, readable_size: usize) TransactionReadPlan {
        return .{
            .anchor = descriptor().anchor,
            .readable_size = if (has_private_data) readable_size else 0,
            .returns_eof = !has_private_data,
            .delegates_to_simple_read_from_buffer = has_private_data,
            .keeps_private_data = has_private_data,
            .leaves_pos_unchanged = !has_private_data,
        };
    }

    pub fn simpleTransactionReleasePlan(has_private_data: bool) TransactionReleasePlan {
        return .{
            .anchor = descriptor().anchor,
            .returns_zero = true,
            .frees_private_data = has_private_data,
            .had_private_data = has_private_data,
        };
    }
};