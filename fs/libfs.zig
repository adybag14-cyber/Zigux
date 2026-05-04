const std = @import("std");

pub const page_size: u32 = 4096;
pub const name_max: u32 = 255;
pub const simple_transaction_limit: usize = page_size;
pub const dir_offset_first: i64 = 2;
pub const dir_offset_eod: i64 = std.math.maxInt(i32);
pub const sector_shift: u6 = 9;
pub const page_shift: u6 = 12;

pub const ModuleDescriptor = struct {
    name: []const u8,
    anchor: []const u8,
    provides_statfs_defaults: bool,
    provides_lookup_policy: bool,
    provides_buffer_copy_helpers: bool,
    provides_offset_seek_helpers: bool,
    provides_offset_readdir_planning: bool,
    provides_directory_emit_planning: bool,
    provides_directory_cursor_preconditions: bool,
    provides_directory_cursor_reposition_planning: bool,
    provides_directory_scan_resched_planning: bool,
    provides_directory_close_planning: bool,
    provides_transaction_buffer_planning: bool,
    provides_transaction_read_release_planning: bool,
    provides_open_private_data_planning: bool,
    provides_addressability_planning: bool,
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

pub const OffsetReaddirMode = enum {
    blocked_on_emit_dots,
    ready_to_iterate,
    ready_at_end_of_directory,
};

pub const OffsetReaddirPlan = struct {
    anchor: []const u8,
    mode: OffsetReaddirMode,
    returns_zero: bool,
    requires_dir_emit_dots: bool,
    enters_offset_iteration: bool,
    keeps_current_pos: bool,
    treats_eod_as_terminal: bool,
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

pub const CursorRepositionMode = enum {
    unhashed,
    reanchor_before_found,
    reanchor_behind_found,
};

pub const CursorRepositionPlan = struct {
    anchor: []const u8,
    mode: CursorRepositionMode,
    unlinks_existing_cursor: bool,
    requires_parent_lock: bool,
    drops_found_reference: bool,
    keeps_private_data: bool,
};

pub const ScanReschedMode = enum {
    continue_scan,
    requeue_cursor_behind_current,
};

pub const ScanReschedPlan = struct {
    anchor: []const u8,
    mode: ScanReschedMode,
    unlinks_existing_cursor: bool,
    reinserts_cursor_behind_current: bool,
    resumes_from_cursor_next: bool,
    drops_parent_lock_for_cond_resched: bool,
    relocks_parent_after_cond_resched: bool,
};

pub const DirectoryClosePlan = struct {
    anchor: []const u8,
    returns_zero: bool,
    calls_dput_on_private_data: bool,
    releases_private_cursor_reference: bool,
    tolerates_missing_private_data: bool,
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

pub const SimpleOpenPrivateDataSource = enum {
    unchanged,
    inode_private,
};

pub const SimpleOpenPlan = struct {
    anchor: []const u8,
    private_data_source: SimpleOpenPrivateDataSource,
    returns_zero: bool,
    stores_inode_private_data: bool,
};

pub const AddressabilityStatus = enum {
    empty_filesystem,
    invalid_blocksize,
    too_large_for_sector_index,
    too_large_for_page_index,
    addressable,
};

pub const AddressabilityLimits = struct {
    sector_shift: u6 = 9,
    page_shift: u6 = 12,
    sector_index_bits: u7 = 64,
    page_index_bits: u7 = 64,
};

pub const AddressabilityPlan = struct {
    anchor: []const u8,
    status: AddressabilityStatus,
    blocksize_bits: u6,
    num_blocks: u64,
    last_fs_block: u64,
    last_fs_page: u64,
    sector_index_limit: u64,
    page_index_limit: u64,
};

pub const LibFsHelperLab = struct {
    fn maxValueForBits(bit_count: u7) u64 {
        if (bit_count >= 64) {
            return std.math.maxInt(u64);
        }
        return (@as(u64, 1) << @intCast(bit_count)) - 1;
    }

    pub fn descriptor() ModuleDescriptor {
        return .{
            .name = "libfs_helper_lab",
            .anchor = "fs/libfs.c",
            .provides_statfs_defaults = true,
            .provides_lookup_policy = true,
            .provides_buffer_copy_helpers = true,
            .provides_offset_seek_helpers = true,
            .provides_offset_readdir_planning = true,
            .provides_directory_emit_planning = true,
            .provides_directory_cursor_preconditions = true,
            .provides_directory_cursor_reposition_planning = true,
            .provides_directory_scan_resched_planning = true,
            .provides_directory_close_planning = true,
            .provides_transaction_buffer_planning = true,
            .provides_transaction_read_release_planning = true,
            .provides_open_private_data_planning = true,
            .provides_addressability_planning = true,
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

    pub fn offsetReaddirPlan(current_pos: i64, emit_dots_result: bool) !OffsetReaddirPlan {
        if (current_pos < 0) {
            return error.InvalidOffset;
        }

        if (!emit_dots_result) {
            return .{
                .anchor = descriptor().anchor,
                .mode = .blocked_on_emit_dots,
                .returns_zero = true,
                .requires_dir_emit_dots = true,
                .enters_offset_iteration = false,
                .keeps_current_pos = true,
                .treats_eod_as_terminal = false,
            };
        }

        const at_end_of_directory = current_pos == dir_offset_eod;
        return .{
            .anchor = descriptor().anchor,
            .mode = if (at_end_of_directory) .ready_at_end_of_directory else .ready_to_iterate,
            .returns_zero = true,
            .requires_dir_emit_dots = true,
            .enters_offset_iteration = !at_end_of_directory,
            .keeps_current_pos = at_end_of_directory,
            .treats_eod_as_terminal = at_end_of_directory,
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

    pub fn dcacheDirSeekCursorRepositionPlan(found_target: bool) CursorRepositionPlan {
        return .{
            .anchor = descriptor().anchor,
            .mode = if (found_target) .reanchor_behind_found else .unhashed,
            .unlinks_existing_cursor = true,
            .requires_parent_lock = true,
            .drops_found_reference = true,
            .keeps_private_data = true,
        };
    }

    pub fn dcacheReaddirCursorRepositionPlan(found_next: bool) CursorRepositionPlan {
        return .{
            .anchor = descriptor().anchor,
            .mode = if (found_next) .reanchor_before_found else .unhashed,
            .unlinks_existing_cursor = true,
            .requires_parent_lock = true,
            .drops_found_reference = true,
            .keeps_private_data = true,
        };
    }

    pub fn scanPositivesReschedPlan(cursor_is_hashed: bool, resched_requested: bool) ScanReschedPlan {
        return .{
            .anchor = descriptor().anchor,
            .mode = if (resched_requested) .requeue_cursor_behind_current else .continue_scan,
            .unlinks_existing_cursor = resched_requested and cursor_is_hashed,
            .reinserts_cursor_behind_current = resched_requested,
            .resumes_from_cursor_next = resched_requested,
            .drops_parent_lock_for_cond_resched = resched_requested,
            .relocks_parent_after_cond_resched = resched_requested,
        };
    }

    pub fn dcacheDirClosePlan(has_private_data: bool) DirectoryClosePlan {
        return .{
            .anchor = descriptor().anchor,
            .returns_zero = true,
            .calls_dput_on_private_data = true,
            .releases_private_cursor_reference = has_private_data,
            .tolerates_missing_private_data = true,
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

    pub fn simpleOpenPlan(inode_has_private_data: bool) SimpleOpenPlan {
        return .{
            .anchor = descriptor().anchor,
            .private_data_source = if (inode_has_private_data) .inode_private else .unchanged,
            .returns_zero = true,
            .stores_inode_private_data = inode_has_private_data,
        };
    }

    pub fn genericCheckAddressablePlan(blocksize_bits: u6, num_blocks: u64, limits: AddressabilityLimits) AddressabilityPlan {
        const blocksize_valid = blocksize_bits >= limits.sector_shift and blocksize_bits <= limits.page_shift;
        const sector_index_limit = if (blocksize_valid)
            maxValueForBits(limits.sector_index_bits) >> @intCast(blocksize_bits - limits.sector_shift)
        else
            0;
        const page_index_limit = maxValueForBits(limits.page_index_bits);

        if (num_blocks == 0) {
            return .{
                .anchor = descriptor().anchor,
                .status = .empty_filesystem,
                .blocksize_bits = blocksize_bits,
                .num_blocks = num_blocks,
                .last_fs_block = 0,
                .last_fs_page = 0,
                .sector_index_limit = sector_index_limit,
                .page_index_limit = page_index_limit,
            };
        }

        if (!blocksize_valid) {
            return .{
                .anchor = descriptor().anchor,
                .status = .invalid_blocksize,
                .blocksize_bits = blocksize_bits,
                .num_blocks = num_blocks,
                .last_fs_block = num_blocks - 1,
                .last_fs_page = 0,
                .sector_index_limit = 0,
                .page_index_limit = page_index_limit,
            };
        }

        const last_fs_block = num_blocks - 1;
        const last_fs_page = last_fs_block >> @intCast(limits.page_shift - blocksize_bits);
        const status: AddressabilityStatus = if (last_fs_block > sector_index_limit)
            .too_large_for_sector_index
        else if (last_fs_page > page_index_limit)
            .too_large_for_page_index
        else
            .addressable;

        return .{
            .anchor = descriptor().anchor,
            .status = status,
            .blocksize_bits = blocksize_bits,
            .num_blocks = num_blocks,
            .last_fs_block = last_fs_block,
            .last_fs_page = last_fs_page,
            .sector_index_limit = sector_index_limit,
            .page_index_limit = page_index_limit,
        };
    }
};