const std = @import("std");

pub const completion_entry_bytes: u16 = 16;
pub const min_page_size: u32 = 4096;
pub const min_queue_depth: u16 = 2;
pub const max_queue_depth: u16 = 4095;
pub const min_sq_entry_bytes: u16 = 16;
pub const max_sq_entry_bytes: u16 = 128;
pub const admin_queue_id: u16 = 0;
pub const max_planned_io_queues: usize = 64;
pub const prp_list_entry_bytes: u32 = 8;

pub const QueueRole = enum {
    admin,
    io,
};

pub const RecoveryState = enum {
    running,
    reset_frozen,
};

pub const SglSupport = enum {
    unavailable,
    optional,
    forced,
};

pub const DataPointerPlan = enum {
    prp,
    sgl,
    blocked,
};

pub const ModuleDescriptor = struct {
    name: []const u8,
    anchor: []const u8,
    provides_lab_queue_planner: bool,
    provides_queue_count_helper: bool,
    provides_prp_shape_helper: bool,
    provides_prp_metadata_helper: bool,
    provides_pointer_selection_helper: bool,
    provides_doorbell_window_helper: bool,
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

pub const IoQueueCountPlanSummary = struct {
    anchor: []const u8,
    requested_io_queues: usize,
    controller_io_queue_limit: usize,
    planner_remaining_io_slots: usize,
    selected_io_queues: usize,
    first_queue_id: u16,
    last_queue_id: u16,
    queue_pairs_after_plan: usize,
    controller_limited: bool,
    planner_limited: bool,
    queues_frozen: bool,
    reset_generation: u32,
};

pub const RecoverySummary = struct {
    anchor: []const u8,
    state: RecoveryState,
    queues_frozen: bool,
    planned_io_queues: usize,
    reset_generation: u32,
    last_admin_queue_depth: u16,
};

pub const QueueRecoveryReplaySummary = struct {
    anchor: []const u8,
    controller_io_queue_limit: usize,
    planned_io_queues: usize,
    replay_io_queues: usize,
    dropped_io_queues: usize,
    total_queue_pairs: usize,
    first_io_queue_id: u16,
    last_io_queue_id: u16,
    admin_queue_depth: u16,
    admin_sq_entry_bytes: u16,
    admin_host_dma_bytes: u32,
    replay_io_host_dma_bytes: u32,
    total_host_dma_bytes: u32,
    replay_uses_cmb_io_queue: bool,
    controller_limited: bool,
    queues_frozen: bool,
    reset_generation: u32,
};

pub const PrpBufferShapeSummary = struct {
    anchor: []const u8,
    dma_address: u64,
    transfer_bytes: u32,
    first_page_offset: u32,
    spanned_bytes: u32,
    rounded_span_bytes: u32,
    spanned_pages: u16,
    uses_prp_list: bool,
    prp_list_entries: u16,
    prp_list_entries_per_page: u16,
    prp_list_pages: u16,
    fits_single_prp_list_page: bool,
    reset_generation: u32,
};

pub const PrpMetadataPlanSummary = struct {
    anchor: []const u8,
    dma_address: u64,
    transfer_bytes: u32,
    spanned_pages: u16,
    uses_prp_list: bool,
    command_data_prp_entries: u16,
    prp_list_covered_pages: u16,
    prp_list_pages: u16,
    metadata_dma_bytes: u32,
    total_dma_bytes: u32,
    requires_descriptor_rebuild_after_reset: bool,
    reset_generation: u32,
};

pub const DataPointerStrategySummary = struct {
    anchor: []const u8,
    queue_id: u16,
    transfer_bytes: u32,
    segment_count: u16,
    average_segment_bytes: u32,
    page_gap_mask: u32,
    controller_supports_sgl: bool,
    user_command: bool,
    integrity_segment_count: u16,
    sgl_threshold_bytes: u32,
    sgl_support: SglSupport,
    selected_pointer: DataPointerPlan,
    forced_by_page_gap: bool,
    forced_by_user_command: bool,
    forced_by_integrity_segments: bool,
    threshold_prefers_sgl: bool,
    forced_sgl_unavailable: bool,
    reset_generation: u32,
};

pub const DoorbellWindowSummary = struct {
    anchor: []const u8,
    planned_io_queues: usize,
    queue_pair_count: usize,
    doorbell_stride_bytes: u32,
    admin_sq_doorbell_offset: u32,
    admin_cq_doorbell_offset: u32,
    has_io_queues: bool,
    first_io_sq_doorbell_offset: u32,
    last_cq_doorbell_offset: u32,
    total_doorbell_window_bytes: u32,
    queues_frozen: bool,
    reset_generation: u32,
};

pub const NvmePciQueueLab = struct {
    const Self = @This();

    const QueueReplayTemplate = struct {
        queue_depth: u16 = 0,
        sq_entry_bytes: u16 = 0,
        uses_cmb: bool = false,
        host_dma_bytes: u32 = 0,
    };

    page_size: u32,
    doorbell_stride_bytes: u32,
    recovery_state: RecoveryState = .running,
    next_io_queue_id: u16 = 1,
    planned_io_queues: usize = 0,
    reset_generation: u32 = 0,
    admin_queue_planned: bool = false,
    last_admin_queue_depth: u16 = min_queue_depth,
    last_admin_sq_entry_bytes: u16 = min_sq_entry_bytes,
    last_admin_uses_cmb: bool = false,
    last_admin_host_dma_bytes: u32 = 0,
    io_queue_templates: [max_planned_io_queues]QueueReplayTemplate = [_]QueueReplayTemplate{.{}} ** max_planned_io_queues,

    pub fn descriptor() ModuleDescriptor {
        return .{
            .name = "nvme_pci_queue_lab",
            .anchor = "drivers/nvme/host/pci.c",
            .provides_lab_queue_planner = true,
            .provides_queue_count_helper = true,
            .provides_prp_shape_helper = true,
            .provides_prp_metadata_helper = true,
            .provides_pointer_selection_helper = true,
            .provides_doorbell_window_helper = true,
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
        self.admin_queue_planned = true;
        self.last_admin_queue_depth = summary.queue_depth;
        self.last_admin_sq_entry_bytes = summary.sq_entry_bytes;
        self.last_admin_uses_cmb = summary.uses_cmb;
        self.last_admin_host_dma_bytes = summary.host_dma_bytes;
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
        self.io_queue_templates[self.planned_io_queues] = .{
            .queue_depth = summary.queue_depth,
            .sq_entry_bytes = summary.sq_entry_bytes,
            .uses_cmb = summary.uses_cmb,
            .host_dma_bytes = summary.host_dma_bytes,
        };
        self.next_io_queue_id += 1;
        self.planned_io_queues += 1;
        return summary;
    }

    pub fn planIoQueueCount(
        self: *const Self,
        requested_io_queues: usize,
        controller_io_queue_limit: usize,
    ) !IoQueueCountPlanSummary {
        if (self.recovery_state != .running) return error.QueuePlanningBlockedByReset;
        if (requested_io_queues == 0) return error.InvalidRequestedIoQueues;
        if (controller_io_queue_limit == 0) return error.InvalidControllerQueueCount;

        const planner_remaining_io_slots = max_planned_io_queues - self.planned_io_queues;
        if (planner_remaining_io_slots == 0) return error.NoQueueIdsAvailable;

        const selected_io_queues = @min(requested_io_queues, @min(controller_io_queue_limit, planner_remaining_io_slots));
        const last_queue_delta = try checkedCastU16(selected_io_queues - 1);
        const last_queue_id = try checkedAddU16(self.next_io_queue_id, last_queue_delta);
        const queue_pairs_after_plan = try checkedAddUsize(self.planned_io_queues, selected_io_queues);

        return .{
            .anchor = descriptor().anchor,
            .requested_io_queues = requested_io_queues,
            .controller_io_queue_limit = controller_io_queue_limit,
            .planner_remaining_io_slots = planner_remaining_io_slots,
            .selected_io_queues = selected_io_queues,
            .first_queue_id = self.next_io_queue_id,
            .last_queue_id = last_queue_id,
            .queue_pairs_after_plan = try checkedAddUsize(queue_pairs_after_plan, 1),
            .controller_limited = controller_io_queue_limit < requested_io_queues,
            .planner_limited = planner_remaining_io_slots < requested_io_queues,
            .queues_frozen = false,
            .reset_generation = self.reset_generation,
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
        self.io_queue_templates = [_]QueueReplayTemplate{.{}} ** max_planned_io_queues;
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

    pub fn planQueueRecoveryReplay(
        self: *const Self,
        controller_io_queue_limit: usize,
    ) !QueueRecoveryReplaySummary {
        if (!self.admin_queue_planned) return error.AdminQueueNotPlanned;

        const replay_io_queues = @min(self.planned_io_queues, controller_io_queue_limit);
        const dropped_io_queues = self.planned_io_queues - replay_io_queues;
        const total_queue_pairs = try checkedAddUsize(replay_io_queues, 1);
        const first_io_queue_id: u16 = if (replay_io_queues == 0) 0 else 1;
        const last_io_queue_id: u16 = if (replay_io_queues == 0) 0 else try checkedCastU16(replay_io_queues);

        var replay_io_host_dma_bytes: u32 = 0;
        var replay_uses_cmb_io_queue = false;
        var index: usize = 0;
        while (index < replay_io_queues) : (index += 1) {
            const template = self.io_queue_templates[index];
            replay_io_host_dma_bytes = try checkedAddU32(replay_io_host_dma_bytes, template.host_dma_bytes);
            replay_uses_cmb_io_queue = replay_uses_cmb_io_queue or template.uses_cmb;
        }
        const total_host_dma_bytes = try checkedAddU32(self.last_admin_host_dma_bytes, replay_io_host_dma_bytes);

        return .{
            .anchor = descriptor().anchor,
            .controller_io_queue_limit = controller_io_queue_limit,
            .planned_io_queues = self.planned_io_queues,
            .replay_io_queues = replay_io_queues,
            .dropped_io_queues = dropped_io_queues,
            .total_queue_pairs = total_queue_pairs,
            .first_io_queue_id = first_io_queue_id,
            .last_io_queue_id = last_io_queue_id,
            .admin_queue_depth = self.last_admin_queue_depth,
            .admin_sq_entry_bytes = self.last_admin_sq_entry_bytes,
            .admin_host_dma_bytes = self.last_admin_host_dma_bytes,
            .replay_io_host_dma_bytes = replay_io_host_dma_bytes,
            .total_host_dma_bytes = total_host_dma_bytes,
            .replay_uses_cmb_io_queue = replay_uses_cmb_io_queue,
            .controller_limited = replay_io_queues < self.planned_io_queues,
            .queues_frozen = self.recovery_state != .running,
            .reset_generation = self.reset_generation,
        };
    }

    pub fn shapePrpBuffer(
        self: *const Self,
        dma_address: u64,
        transfer_bytes: u32,
    ) !PrpBufferShapeSummary {
        if (self.recovery_state != .running) return error.QueuePlanningBlockedByReset;
        if (transfer_bytes == 0) return error.InvalidTransferBytes;

        const first_page_offset = @as(u32, @intCast(dma_address & (self.page_size - 1)));
        const spanned_bytes = try checkedAddU32(first_page_offset, transfer_bytes);
        const rounded_span_bytes = try checkedRoundUpU32(spanned_bytes, self.page_size);
        const spanned_pages = try checkedDivCeilU16(spanned_bytes, self.page_size);
        const uses_prp_list = spanned_pages > 2;
        const prp_list_entries = if (uses_prp_list) spanned_pages - 1 else 0;
        const prp_list_entries_per_page = try checkedDivExactU16(self.page_size, prp_list_entry_bytes);
        const prp_list_pages = if (prp_list_entries == 0)
            0
        else
            try checkedDivCeilU16(prp_list_entries, prp_list_entries_per_page);

        return .{
            .anchor = descriptor().anchor,
            .dma_address = dma_address,
            .transfer_bytes = transfer_bytes,
            .first_page_offset = first_page_offset,
            .spanned_bytes = spanned_bytes,
            .rounded_span_bytes = rounded_span_bytes,
            .spanned_pages = spanned_pages,
            .uses_prp_list = uses_prp_list,
            .prp_list_entries = prp_list_entries,
            .prp_list_entries_per_page = prp_list_entries_per_page,
            .prp_list_pages = prp_list_pages,
            .fits_single_prp_list_page = prp_list_pages <= 1,
            .reset_generation = self.reset_generation,
        };
    }

    pub fn planPrpMetadata(
        self: *const Self,
        dma_address: u64,
        transfer_bytes: u32,
    ) !PrpMetadataPlanSummary {
        const shape = try self.shapePrpBuffer(dma_address, transfer_bytes);
        const command_data_prp_entries: u16 = if (shape.spanned_pages == 1)
            1
        else
            2;
        const prp_list_covered_pages: u16 = if (shape.uses_prp_list) shape.prp_list_entries else 0;
        const metadata_dma_bytes = try checkedMulU16ByU32(shape.prp_list_pages, self.page_size);
        const total_dma_bytes = try checkedAddU32(shape.rounded_span_bytes, metadata_dma_bytes);

        return .{
            .anchor = shape.anchor,
            .dma_address = shape.dma_address,
            .transfer_bytes = shape.transfer_bytes,
            .spanned_pages = shape.spanned_pages,
            .uses_prp_list = shape.uses_prp_list,
            .command_data_prp_entries = command_data_prp_entries,
            .prp_list_covered_pages = prp_list_covered_pages,
            .prp_list_pages = shape.prp_list_pages,
            .metadata_dma_bytes = metadata_dma_bytes,
            .total_dma_bytes = total_dma_bytes,
            .requires_descriptor_rebuild_after_reset = shape.uses_prp_list,
            .reset_generation = shape.reset_generation,
        };
    }

    pub fn planDataPointerStrategy(
        self: *const Self,
        queue_id: u16,
        transfer_bytes: u32,
        segment_count: u16,
        page_gap_mask: u32,
        controller_supports_sgl: bool,
        user_command: bool,
        integrity_segment_count: u16,
        sgl_threshold_bytes: u32,
    ) !DataPointerStrategySummary {
        if (self.recovery_state != .running) return error.QueuePlanningBlockedByReset;
        if (transfer_bytes == 0) return error.InvalidTransferBytes;
        if (segment_count == 0) return error.InvalidSegmentCount;

        const forced_by_page_gap = (page_gap_mask & (self.page_size - 1)) != 0;
        const forced_by_user_command = user_command;
        const forced_by_integrity_segments = integrity_segment_count > 1;
        const forced_sgl = forced_by_page_gap or forced_by_user_command or forced_by_integrity_segments;
        const average_segment_bytes = try checkedDivCeilU32ByU16(transfer_bytes, segment_count);
        const sgl_support: SglSupport = if (queue_id != admin_queue_id and controller_supports_sgl)
            (if (forced_sgl) .forced else .optional)
        else
            .unavailable;
        const threshold_prefers_sgl = sgl_support == .optional and
            sgl_threshold_bytes != 0 and
            average_segment_bytes >= sgl_threshold_bytes;
        const forced_sgl_unavailable = forced_sgl and sgl_support == .unavailable;
        const selected_pointer: DataPointerPlan = switch (sgl_support) {
            .forced => .sgl,
            .optional => if (threshold_prefers_sgl) .sgl else .prp,
            .unavailable => if (forced_sgl_unavailable) .blocked else .prp,
        };

        return .{
            .anchor = descriptor().anchor,
            .queue_id = queue_id,
            .transfer_bytes = transfer_bytes,
            .segment_count = segment_count,
            .average_segment_bytes = average_segment_bytes,
            .page_gap_mask = page_gap_mask,
            .controller_supports_sgl = controller_supports_sgl,
            .user_command = user_command,
            .integrity_segment_count = integrity_segment_count,
            .sgl_threshold_bytes = sgl_threshold_bytes,
            .sgl_support = sgl_support,
            .selected_pointer = selected_pointer,
            .forced_by_page_gap = forced_by_page_gap,
            .forced_by_user_command = forced_by_user_command,
            .forced_by_integrity_segments = forced_by_integrity_segments,
            .threshold_prefers_sgl = threshold_prefers_sgl,
            .forced_sgl_unavailable = forced_sgl_unavailable,
            .reset_generation = self.reset_generation,
        };
    }

    pub fn planDoorbellWindow(self: *const Self) !DoorbellWindowSummary {
        const queue_pair_count = try checkedAddUsize(self.planned_io_queues, 1);
        const has_io_queues = self.planned_io_queues != 0;
        const first_io_sq_doorbell_offset = if (has_io_queues)
            try checkedMulWideU32(2, self.doorbell_stride_bytes)
        else
            0;
        const last_queue_id = std.math.cast(u32, self.planned_io_queues) orelse return error.QueueBytesOverflow;
        const last_queue_slot = try checkedMulWideU32(last_queue_id, 2);
        const last_sq_doorbell_offset = try checkedMulWideU32(last_queue_slot, self.doorbell_stride_bytes);
        const last_cq_doorbell_offset = try checkedAddU32(last_sq_doorbell_offset, self.doorbell_stride_bytes);
        const total_doorbell_window_bytes = try checkedAddU32(last_cq_doorbell_offset, self.doorbell_stride_bytes);

        return .{
            .anchor = descriptor().anchor,
            .planned_io_queues = self.planned_io_queues,
            .queue_pair_count = queue_pair_count,
            .doorbell_stride_bytes = self.doorbell_stride_bytes,
            .admin_sq_doorbell_offset = 0,
            .admin_cq_doorbell_offset = self.doorbell_stride_bytes,
            .has_io_queues = has_io_queues,
            .first_io_sq_doorbell_offset = first_io_sq_doorbell_offset,
            .last_cq_doorbell_offset = last_cq_doorbell_offset,
            .total_doorbell_window_bytes = total_doorbell_window_bytes,
            .queues_frozen = self.recovery_state != .running,
            .reset_generation = self.reset_generation,
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

        const sq_bytes = try checkedMulU16ByU16(queue_depth, checked_sq_entry_bytes);
        const cq_bytes = try checkedMulU16ByU16(queue_depth, completion_entry_bytes);
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

    fn checkedCastU16(value: usize) !u16 {
        return std.math.cast(u16, value) orelse error.QueueBytesOverflow;
    }

    fn checkedAddU16(lhs: u16, rhs: u16) !u16 {
        return std.math.add(u16, lhs, rhs) catch error.QueueBytesOverflow;
    }

    fn checkedMulU16ByU16(lhs: u16, rhs: u16) !u32 {
        const value = @as(u64, lhs) * rhs;
        return std.math.cast(u32, value) orelse error.QueueBytesOverflow;
    }

    fn checkedMulU16ByU32(lhs: u16, rhs: u32) !u32 {
        const value = @as(u64, lhs) * rhs;
        return std.math.cast(u32, value) orelse error.QueueBytesOverflow;
    }

    fn checkedAddU32(lhs: u32, rhs: u32) !u32 {
        const value = @as(u64, lhs) + rhs;
        return std.math.cast(u32, value) orelse error.QueueBytesOverflow;
    }

    fn checkedAddUsize(lhs: usize, rhs: usize) !usize {
        return std.math.add(usize, lhs, rhs) catch error.QueueBytesOverflow;
    }

    fn checkedMulWideU32(lhs: u32, rhs: u32) !u32 {
        const value = @as(u64, lhs) * rhs;
        return std.math.cast(u32, value) orelse error.QueueBytesOverflow;
    }

    fn checkedRoundUpU32(value: u32, alignment: u32) !u32 {
        const remainder = value % alignment;
        if (remainder == 0) return value;
        return checkedAddU32(value, alignment - remainder);
    }

    fn checkedDivExactU16(lhs: u32, rhs: u32) !u16 {
        if (rhs == 0 or (lhs % rhs) != 0) return error.QueueBytesOverflow;
        return std.math.cast(u16, lhs / rhs) orelse error.QueueBytesOverflow;
    }

    fn checkedDivCeilU16(bytes: u32, page_size: u32) !u16 {
        const rounded = @as(u64, bytes) + page_size - 1;
        const pages = rounded / page_size;
        return std.math.cast(u16, pages) orelse error.QueueBytesOverflow;
    }

    fn checkedDivCeilU32ByU16(value: u32, divisor: u16) !u32 {
        const rounded = @as(u64, value) + divisor - 1;
        return std.math.cast(u32, rounded / divisor) orelse error.QueueBytesOverflow;
    }
};