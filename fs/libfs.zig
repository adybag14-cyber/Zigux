const std = @import("std");

pub const page_size: u32 = 4096;
pub const name_max: u32 = 255;
pub const simple_transaction_limit: usize = @as(usize, page_size) - @sizeOf(isize);

pub const ModuleDescriptor = struct {
    name: []const u8,
    anchor: []const u8,
    provides_statfs_defaults: bool,
    provides_lookup_policy: bool,
    provides_buffer_copy_helpers: bool,
    provides_offset_seek_helpers: bool,
    provides_directory_emit_planning: bool,
    provides_transaction_buffer_planning: bool,
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

pub const TransactionBufferAcquirePlan = struct {
    anchor: []const u8,
    requested_size: usize,
    transaction_limit: usize,
    allocates_zeroed_page: bool,
    requires_empty_private_data: bool,
    response_size: usize,
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
            .provides_transaction_buffer_planning = true,
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

    pub fn simpleTransactionGetPlan(request_size: usize, private_data_already_set: bool) !TransactionBufferAcquirePlan {
        if (request_size > simple_transaction_limit - 1) {
            return error.InputTooLarge;
        }
        if (private_data_already_set) {
            return error.Busy;
        }

        return .{
            .anchor = descriptor().anchor,
            .requested_size = request_size,
            .transaction_limit = simple_transaction_limit,
            .allocates_zeroed_page = true,
            .requires_empty_private_data = true,
            .response_size = 0,
        };
    }
};