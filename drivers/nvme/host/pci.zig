const std = @import("std");

pub const completion_entry_bytes: u16 = 16;
pub const min_page_size: u32 = 4096;
pub const min_queue_depth: u16 = 2;
pub const max_queue_depth: u16 = 4095;
pub const min_sq_entry_bytes: u16 = 16;
pub const max_sq_entry_bytes: u16 = 128;
pub const admin_queue_id: u16 = 0;
pub const max_planned_io_queues: usize = 64;

pub const QueueRole = enum {
    admin,
    io,
};

pub const RecoveryState = enum {
    running,
    reset_frozen,
};

pub const ModuleDescriptor = struct {
    name: []const u8,
    anchor: []const u8,
    provides_lab_queue_planner: bool,
    touches_live_dma: bool,
    touches_pci_probe: bool,
    touches_irq_recovery: bool,
};

pub const QueuePairPlanSummary = struct {
    anchor: []const u8,
    role: QueueRole,
    queue_id: u16,
    queue_depth: u16,
    sq_entry_bytes: u16,
    sq_bytes: u32,
    cq_bytes: u32,
    queue_memory_bytes: u32,
    host_dma_bytes: u32,
    required_host_dma_pages: u16,
    sq_doorbell_offset: u32,
    cq_doorbell_offset: u32,
    uses_cmb: bool,
    reset_generation: u32,
};

pub const PrpBufferShapeSummary = struct {
    anchor: []const u8,
    total_transfer_bytes: u32,
    first_page_offset: u32,
    first_prp_bytes: u32,
    rounded_span_bytes: u32,
    spanned_pages: u16,
    tail_page_count: u16,
    uses_prp_list: bool,
    prp_list_entries: u16,
    prp_list_capacity: u16,
};

pub const RecoverySummary = struct {
    anchor: []const u8,
    state: RecoveryState,
    queues_frozen: bool,
    planned_io_queues: usize,
    reset_generation: u32,
    last_admin_queue_depth: u16,
};

pub const QueueRecoveryPlanSummary = struct {
    anchor: []const u8,
    state: RecoveryState,
    reset_generation: u32,
    admin_queue_depth: u16,
    admin_host_dma_pages: u16,
    io_queue_count: usize,
    io_host_dma_pages: u32,
    total_host_dma_pages: u32,
    restores_admin_first: bool,
    restores_io_after_admin: bool,
};

pub const NvmePciQueueLab = struct {
    const Self = @This();

    page_size: u32,
    doorbell_stride_bytes: u32,
    recovery_state: RecoveryState = .running,
    next_io_queue_id: u16 = 1,
    planned_io_queues: usize = 0,
    reset_generation: u32 = 0,
    last_admin_queue_depth: u16 = min_queue_depth,
    last_admin_host_dma_pages: u16 = 0,
    planned_io_host_dma_pages: u32 = 0,

    pub fn descriptor() ModuleDescriptor {
        return .{
            .name = "nvme_pci_queue_lab",
            .anchor = "drivers/nvme/host/pci.c",
            .provides_lab_queue_planner = true,
            .touches_live_dma = false,
            .touches_pci_probe = false,
            .touches_irq_recovery = false,
        };
    }

    pub fn init(page_size: u32, doorbell_stride_bytes: u32) !Self {
        if (page_size < min_page_size or !std.math.isPowerOfTwo(page_size)) {
            return error.InvalidPageSize;
        }
        if (doorbell_stride_bytes < 4 or (doorbell_stride_bytes % 4) != 0) {
            return error.InvalidDoorbellStride;
        }
        return .{
            .page_size = page_size,
            .doorbell_stride_bytes = doorbell_stride_bytes,
        };
    }

    pub fn planAdminQueue(
        self: *Self,
        requested_depth: u16,
        sq_entry_bytes: u16,
        uses_cmb: bool,
    ) !QueuePairPlanSummary {
        const summary = try self.planQueue(.admin, admin_queue_id, requested_depth, sq_entry_bytes, uses_cmb);
        self.last_admin_queue_depth = summary.queue_depth;
        self.last_admin_host_dma_pages = summary.required_host_dma_pages;
        return summary;
    }

    pub fn planIoQueue(
        self: *Self,
        requested_depth: u16,
        sq_entry_bytes: u16,
        uses_cmb: bool,
    ) !QueuePairPlanSummary {
        if (self.recovery_state != .running) return error.QueuePlanningBlockedByReset;
        if (self.planned_io_queues >= max_planned_io_queues) return error.TooManyPlannedIoQueues;

        const summary = try self.planQueue(.io, self.next_io_queue_id, requested_depth, sq_entry_bytes, uses_cmb);
        self.next_io_queue_id += 1;
        self.planned_io_queues += 1;
        self.planned_io_host_dma_pages = try checkedAddU32(
            self.planned_io_host_dma_pages,
            @as(u32, summary.required_host_dma_pages),
        );
        return summary;
    }

    pub fn planPrpBufferShape(
        self: *const Self,
        total_transfer_bytes: u32,
        first_page_offset: u32,
    ) !PrpBufferShapeSummary {
        if (total_transfer_bytes == 0) return error.InvalidTransferSize;
        if (first_page_offset >= self.page_size) return error.InvalidPrpOffset;

        const covered_by_first_prp = self.page_size - first_page_offset;
        const first_prp_bytes = @min(total_transfer_bytes, covered_by_first_prp);
        const end_offset = try checkedAddU32(first_page_offset, total_transfer_bytes);
        const rounded_span_bytes = try checkedAlignForwardU32(end_offset, self.page_size);
        const spanned_pages_u32 = rounded_span_bytes / self.page_size;
        const spanned_pages = std.math.cast(u16, spanned_pages_u32) orelse return error.PrpShapeOverflow;
        const tail_page_count = spanned_pages - 1;
        const uses_prp_list = tail_page_count > 1;
        const prp_list_entries = if (uses_prp_list) tail_page_count - 1 else 0;
        const prp_list_capacity_u32 = self.page_size / @sizeOf(u64);
        const prp_list_capacity = std.math.cast(u16, prp_list_capacity_u32) orelse return error.PrpShapeOverflow;
        if (prp_list_entries > prp_list_capacity) return error.PrpListTooLong;

        return .{
            .anchor = descriptor().anchor,
            .total_transfer_bytes = total_transfer_bytes,
            .first_page_offset = first_page_offset,
            .first_prp_bytes = first_prp_bytes,
            .rounded_span_bytes = rounded_span_bytes,
            .spanned_pages = spanned_pages,
            .tail_page_count = tail_page_count,
            .uses_prp_list = uses_prp_list,
            .prp_list_entries = prp_list_entries,
            .prp_list_capacity = prp_list_capacity,
        };
    }

    pub fn beginReset(self: *Self) RecoverySummary {
        self.recovery_state = .reset_frozen;
        self.reset_generation += 1;
        return self.recoverySummary();
    }

    pub fn completeReset(self: *Self) RecoverySummary {
        self.recovery_state = .running;
        self.next_io_queue_id = 1;
        self.planned_io_queues = 0;
        self.planned_io_host_dma_pages = 0;
        return self.recoverySummary();
    }

    pub fn recoverySummary(self: *const Self) RecoverySummary {
        return .{
            .anchor = descriptor().anchor,
            .state = self.recovery_state,
            .queues_frozen = self.recovery_state != .running,
            .planned_io_queues = self.planned_io_queues,
            .reset_generation = self.reset_generation,
            .last_admin_queue_depth = self.last_admin_queue_depth,
        };
    }

    pub fn recoveryQueueRestoreSummary(self: *const Self) !QueueRecoveryPlanSummary {
        if (self.recovery_state != .reset_frozen) return error.ResetNotFrozen;

        return .{
            .anchor = descriptor().anchor,
            .state = self.recovery_state,
            .reset_generation = self.reset_generation,
            .admin_queue_depth = self.last_admin_queue_depth,
            .admin_host_dma_pages = self.last_admin_host_dma_pages,
            .io_queue_count = self.planned_io_queues,
            .io_host_dma_pages = self.planned_io_host_dma_pages,
            .total_host_dma_pages = try checkedAddU32(
                @as(u32, self.last_admin_host_dma_pages),
                self.planned_io_host_dma_pages,
            ),
            .restores_admin_first = true,
            .restores_io_after_admin = self.planned_io_queues != 0,
        };
    }

    fn planQueue(
        self: *const Self,
        role: QueueRole,
        queue_id: u16,
        requested_depth: u16,
        sq_entry_bytes: u16,
        uses_cmb: bool,
    ) !QueuePairPlanSummary {
        if (self.recovery_state != .running) return error.QueuePlanningBlockedByReset;

        const queue_depth = try checkedQueueDepth(requested_depth);
        const checked_sq_entry_bytes = try checkedSqEntryBytes(sq_entry_bytes);
        const sq_bytes = try checkedMulU32(queue_depth, checked_sq_entry_bytes);
        const cq_bytes = try checkedMulU32(queue_depth, completion_entry_bytes);
        const queue_memory_bytes = try checkedAddU32(sq_bytes, cq_bytes);
        const host_dma_bytes = if (uses_cmb) cq_bytes else queue_memory_bytes;
        const required_host_dma_pages = try checkedDivCeilU16(host_dma_bytes, self.page_size);
        const sq_doorbell_offset = try checkedMulWideU32(@as(u32, queue_id) * 2, self.doorbell_stride_bytes);
        const cq_doorbell_offset = try checkedAddU32(sq_doorbell_offset, self.doorbell_stride_bytes);

        return .{
            .anchor = descriptor().anchor,
            .role = role,
            .queue_id = queue_id,
            .queue_depth = queue_depth,
            .sq_entry_bytes = checked_sq_entry_bytes,
            .sq_bytes = sq_bytes,
            .cq_bytes = cq_bytes,
            .queue_memory_bytes = queue_memory_bytes,
            .host_dma_bytes = host_dma_bytes,
            .required_host_dma_pages = required_host_dma_pages,
            .sq_doorbell_offset = sq_doorbell_offset,
            .cq_doorbell_offset = cq_doorbell_offset,
            .uses_cmb = uses_cmb,
            .reset_generation = self.reset_generation,
        };
    }

    fn checkedQueueDepth(queue_depth: u16) !u16 {
        if (queue_depth < min_queue_depth or queue_depth > max_queue_depth) {
            return error.QueueDepthOutOfRange;
        }
        return queue_depth;
    }

    fn checkedSqEntryBytes(sq_entry_bytes: u16) !u16 {
        if (sq_entry_bytes < min_sq_entry_bytes or sq_entry_bytes > max_sq_entry_bytes) {
            return error.InvalidSqEntryBytes;
        }
        if (!std.math.isPowerOfTwo(sq_entry_bytes)) {
            return error.InvalidSqEntryBytes;
        }
        return sq_entry_bytes;
    }

    fn checkedMulU32(lhs: u16, rhs: u16) !u32 {
        const value = @as(u64, lhs) * rhs;
        return std.math.cast(u32, value) orelse error.QueueBytesOverflow;
    }

    fn checkedAddU32(lhs: u32, rhs: u32) !u32 {
        const value = @as(u64, lhs) + rhs;
        return std.math.cast(u32, value) orelse error.QueueBytesOverflow;
    }

    fn checkedMulWideU32(lhs: u32, rhs: u32) !u32 {
        const value = @as(u64, lhs) * rhs;
        return std.math.cast(u32, value) orelse error.QueueBytesOverflow;
    }

    fn checkedDivCeilU16(bytes: u32, page_size: u32) !u16 {
        const rounded = @as(u64, bytes) + page_size - 1;
        const pages = rounded / page_size;
        return std.math.cast(u16, pages) orelse error.QueueBytesOverflow;
    }

    fn checkedAlignForwardU32(value: u32, alignment: u32) !u32 {
        if (alignment == 0 or !std.math.isPowerOfTwo(alignment)) return error.InvalidPageSize;

        const addend = alignment - 1;
        const rounded = try checkedAddU32(value, addend);
        return rounded & ~addend;
    }
};

test "nvme pci recovery restore summary snapshots frozen queue DMA budget" {
    var lab = try NvmePciQueueLab.init(4096, 8);

    const admin = try lab.planAdminQueue(64, 64, false);
    try std.testing.expectEqual(@as(u16, 2), admin.required_host_dma_pages);

    const first_io = try lab.planIoQueue(128, 64, true);
    try std.testing.expectEqual(@as(u16, 1), first_io.required_host_dma_pages);

    const second_io = try lab.planIoQueue(128, 64, true);
    try std.testing.expectEqual(@as(u16, 1), second_io.required_host_dma_pages);

    const frozen = lab.beginReset();
    try std.testing.expectEqual(RecoveryState.reset_frozen, frozen.state);

    const summary = try lab.recoveryQueueRestoreSummary();
    try std.testing.expectEqualStrings("drivers/nvme/host/pci.c", summary.anchor);
    try std.testing.expectEqual(RecoveryState.reset_frozen, summary.state);
    try std.testing.expectEqual(@as(u32, 1), summary.reset_generation);
    try std.testing.expectEqual(@as(u16, 64), summary.admin_queue_depth);
    try std.testing.expectEqual(@as(u16, 2), summary.admin_host_dma_pages);
    try std.testing.expectEqual(@as(usize, 2), summary.io_queue_count);
    try std.testing.expectEqual(@as(u32, 2), summary.io_host_dma_pages);
    try std.testing.expectEqual(@as(u32, 4), summary.total_host_dma_pages);
    try std.testing.expect(summary.restores_admin_first);
    try std.testing.expect(summary.restores_io_after_admin);
}

test "nvme pci recovery restore summary requires a frozen reset and clears after completion" {
    var lab = try NvmePciQueueLab.init(4096, 4);

    _ = try lab.planAdminQueue(32, 64, false);
    _ = try lab.planIoQueue(32, 64, false);
    try std.testing.expectError(error.ResetNotFrozen, lab.recoveryQueueRestoreSummary());

    _ = lab.beginReset();
    const first = try lab.recoveryQueueRestoreSummary();
    try std.testing.expectEqual(@as(usize, 1), first.io_queue_count);
    try std.testing.expectEqual(@as(u32, 2), first.total_host_dma_pages);

    _ = lab.completeReset();
    try std.testing.expectError(error.ResetNotFrozen, lab.recoveryQueueRestoreSummary());

    _ = try lab.planAdminQueue(16, 64, true);
    _ = lab.beginReset();
    const second = try lab.recoveryQueueRestoreSummary();
    try std.testing.expectEqual(@as(u16, 16), second.admin_queue_depth);
    try std.testing.expectEqual(@as(usize, 0), second.io_queue_count);
    try std.testing.expectEqual(@as(u32, 1), second.total_host_dma_pages);
    try std.testing.expect(!second.restores_io_after_admin);
}
