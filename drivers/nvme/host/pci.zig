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

pub const OwnershipBoundary = enum {
    starter_packet,
    dma_transport_substrate,
};

pub const ModuleDescriptor = struct {
    name: []const u8,
    anchor: []const u8,
    provides_lab_queue_planner: bool,
    provides_queue_count_helper: bool,
    provides_queue_count_reservation_helper: bool,
    provides_prp_metadata_helper: bool,
    provides_recovery_replay_helper: bool,
    provides_recovery_reservation_helper: bool,
    touches_live_dma: bool,
    touches_pci_probe: bool,
    touches_irq_recovery: bool,
};

pub const OwnershipSummary = struct {
    anchor: []const u8,
    owner_lane: []const u8,
    queue_planning_owner: OwnershipBoundary,
    prp_shape_owner: OwnershipBoundary,
    live_dma_owner: OwnershipBoundary,
    recovery_transport_owner: OwnershipBoundary,
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

pub const IoQueueReservationSummary = struct {
    anchor: []const u8,
    requested_io_queues: usize,
    controller_io_queue_limit: usize,
    planner_remaining_io_slots: usize,
    reserved_io_queues: usize,
    first_queue_id: u16,
    last_queue_id: u16,
    planned_io_queues_after_reserve: usize,
    controller_limited: bool,
    planner_limited: bool,
    queues_frozen: bool,
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

pub const PrpMetadataPlanSummary = struct {
    anchor: []const u8,
    total_transfer_bytes: u32,
    first_page_offset: u32,
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

pub const RecoverySummary = struct {
    anchor: []const u8,
    state: RecoveryState,
    queues_frozen: bool,
    planned_io_queues: usize,
    reset_generation: u32,
    last_admin_queue_depth: u16,
};

pub const RecoveryReplayRequest = struct {
    cached_prp_metadata_generation: u32,
    had_prp_metadata_plan: bool,
    had_admin_queue_plan: bool,
    cached_descriptor_dma_bytes: u32 = 0,
    cached_requires_descriptor_rebuild: bool = false,
    cached_queue_reservation_generation: u32 = 0,
    had_io_queue_reservation: bool = false,
    cached_reserved_io_queues: usize = 0,
};

pub const RecoveryReplaySummary = struct {
    anchor: []const u8,
    state: RecoveryState,
    reset_generation: u32,
    queue_planning_blocked: bool,
    cached_prp_metadata_stale: bool,
    descriptor_rebuild_required: bool,
    descriptor_rebuild_dma_bytes: u32,
    cached_queue_reservation_stale: bool,
    queue_reservation_replay_required: bool,
    reserved_io_queues_to_renegotiate: usize,
    admin_queue_must_be_replanned: bool,
    io_queues_must_be_rebuilt: bool,
    io_queues_dropped_by_reset: usize,
    next_io_queue_id: u16,
    last_admin_queue_depth: u16,
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
    last_reset_io_queue_count: usize = 0,

    pub fn descriptor() ModuleDescriptor {
        return .{
            .name = "nvme_pci_queue_lab",
            .anchor = "drivers/nvme/host/pci.c",
            .provides_lab_queue_planner = true,
            .provides_queue_count_helper = true,
            .provides_queue_count_reservation_helper = true,
            .provides_prp_metadata_helper = true,
            .provides_recovery_replay_helper = true,
            .provides_recovery_reservation_helper = true,
            .touches_live_dma = false,
            .touches_pci_probe = false,
            .touches_irq_recovery = false,
        };
    }

    pub fn ownershipSummary() OwnershipSummary {
        return .{
            .anchor = descriptor().anchor,
            .owner_lane = "P12-L05",
            .queue_planning_owner = .starter_packet,
            .prp_shape_owner = .starter_packet,
            .live_dma_owner = .dma_transport_substrate,
            .recovery_transport_owner = .dma_transport_substrate,
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

    pub fn reserveIoQueues(
        self: *Self,
        requested_io_queues: usize,
        controller_io_queue_limit: usize,
    ) !IoQueueReservationSummary {
        const plan = try self.planIoQueueCount(requested_io_queues, controller_io_queue_limit);
        const reservation_delta = try checkedCastU16(plan.selected_io_queues);

        self.next_io_queue_id = try checkedAddU16(self.next_io_queue_id, reservation_delta);
        self.planned_io_queues = try checkedAddUsize(self.planned_io_queues, plan.selected_io_queues);

        return .{
            .anchor = plan.anchor,
            .requested_io_queues = plan.requested_io_queues,
            .controller_io_queue_limit = plan.controller_io_queue_limit,
            .planner_remaining_io_slots = plan.planner_remaining_io_slots,
            .reserved_io_queues = plan.selected_io_queues,
            .first_queue_id = plan.first_queue_id,
            .last_queue_id = plan.last_queue_id,
            .planned_io_queues_after_reserve = self.planned_io_queues,
            .controller_limited = plan.controller_limited,
            .planner_limited = plan.planner_limited,
            .queues_frozen = plan.queues_frozen,
            .reset_generation = plan.reset_generation,
        };
    }

    pub fn replayReservedIoQueues(
        self: *Self,
        request: RecoveryReplayRequest,
        controller_io_queue_limit: usize,
    ) !IoQueueReservationSummary {
        if (self.recovery_state != .running) return error.QueuePlanningBlockedByReset;
        if (!request.had_io_queue_reservation or request.cached_reserved_io_queues == 0) {
            return error.NoQueueReservationToReplay;
        }
        if (request.cached_queue_reservation_generation == self.reset_generation) {
            return error.QueueReservationAlreadyCurrent;
        }
        return self.reserveIoQueues(request.cached_reserved_io_queues, controller_io_queue_limit);
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

    pub fn planPrpMetadata(
        self: *const Self,
        total_transfer_bytes: u32,
        first_page_offset: u32,
    ) !PrpMetadataPlanSummary {
        if (self.recovery_state != .running) return error.QueuePlanningBlockedByReset;

        const shape = try self.planPrpBufferShape(total_transfer_bytes, first_page_offset);
        const command_data_prp_entries: u16 = if (shape.spanned_pages == 1)
            1
        else if (shape.uses_prp_list)
            1
        else
            2;
        const prp_list_covered_pages: u16 = if (shape.uses_prp_list) shape.tail_page_count else 0;
        const prp_list_pages: u16 = if (shape.uses_prp_list) 1 else 0;
        const metadata_dma_bytes = try checkedMulU16ByU32(prp_list_pages, self.page_size);
        const total_dma_bytes = try checkedAddU32(shape.rounded_span_bytes, metadata_dma_bytes);
        return .{
            .anchor = shape.anchor,
            .total_transfer_bytes = shape.total_transfer_bytes,
            .first_page_offset = shape.first_page_offset,
            .spanned_pages = shape.spanned_pages,
            .uses_prp_list = shape.uses_prp_list,
            .command_data_prp_entries = command_data_prp_entries,
            .prp_list_covered_pages = prp_list_covered_pages,
            .prp_list_pages = prp_list_pages,
            .metadata_dma_bytes = metadata_dma_bytes,
            .total_dma_bytes = total_dma_bytes,
            .requires_descriptor_rebuild_after_reset = shape.uses_prp_list,
            .reset_generation = self.reset_generation,
        };
    }

    pub fn beginReset(self: *Self) RecoverySummary {
        self.last_reset_io_queue_count = self.planned_io_queues;
        self.recovery_state = .reset_frozen;
        self.reset_generation += 1;
        return self.recoverySummary();
    }

    pub fn completeReset(self: *Self) RecoverySummary {
        self.recovery_state = .running;
        self.next_io_queue_id = 1;
        self.planned_io_queues = 0;
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

    pub fn summarizeRecoveryReplay(
        self: *const Self,
        request: RecoveryReplayRequest,
    ) RecoveryReplaySummary {
        const io_queues_dropped_by_reset = if (self.recovery_state == .reset_frozen)
            self.planned_io_queues
        else
            self.last_reset_io_queue_count;
        const cached_prp_metadata_stale = request.had_prp_metadata_plan and
            request.cached_prp_metadata_generation != self.reset_generation;
        const descriptor_rebuild_required = cached_prp_metadata_stale and
            request.cached_requires_descriptor_rebuild;
        const descriptor_rebuild_dma_bytes = if (descriptor_rebuild_required)
            request.cached_descriptor_dma_bytes
        else
            0;
        const cached_queue_reservation_stale = request.had_io_queue_reservation and
            request.cached_queue_reservation_generation != self.reset_generation;
        const reserved_io_queues_to_renegotiate = if (cached_queue_reservation_stale)
            request.cached_reserved_io_queues
        else
            0;

        return .{
            .anchor = descriptor().anchor,
            .state = self.recovery_state,
            .reset_generation = self.reset_generation,
            .queue_planning_blocked = self.recovery_state != .running,
            .cached_prp_metadata_stale = cached_prp_metadata_stale,
            .descriptor_rebuild_required = descriptor_rebuild_required,
            .descriptor_rebuild_dma_bytes = descriptor_rebuild_dma_bytes,
            .cached_queue_reservation_stale = cached_queue_reservation_stale,
            .queue_reservation_replay_required = reserved_io_queues_to_renegotiate != 0,
            .reserved_io_queues_to_renegotiate = reserved_io_queues_to_renegotiate,
            .admin_queue_must_be_replanned = request.had_admin_queue_plan and self.reset_generation != 0,
            .io_queues_must_be_rebuilt = io_queues_dropped_by_reset != 0 and self.reset_generation != 0,
            .io_queues_dropped_by_reset = io_queues_dropped_by_reset,
            .next_io_queue_id = self.next_io_queue_id,
            .last_admin_queue_depth = self.last_admin_queue_depth,
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

    fn checkedCastU16(value: usize) !u16 {
        return std.math.cast(u16, value) orelse error.QueueBytesOverflow;
    }

    fn checkedAddU16(lhs: u16, rhs: u16) !u16 {
        return std.math.add(u16, lhs, rhs) catch error.QueueBytesOverflow;
    }

    fn checkedMulU32(lhs: u16, rhs: u16) !u32 {
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
