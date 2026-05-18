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

pub const RecoveryRollbackBlocker = enum {
    none,
    reset_frozen,
    admin_queue_replay,
    queue_count_parity,
    dma_page_parity,
};

pub const ModuleDescriptor = struct {
    name: []const u8,
    anchor: []const u8,
    provides_lab_queue_planner: bool,
    provides_dropped_io_retirement_helper: bool,
    provides_recovery_rollback_gate_helper: bool,
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

pub const RecoveryReservationReplayPlanSummary = struct {
    anchor: []const u8,
    state: RecoveryState,
    reset_generation: u32,
    requested_reserved_io_queues: usize,
    controller_io_queue_limit: usize,
    planner_remaining_io_slots: usize,
    replayable_reserved_io_queues: usize,
    first_queue_id: u16,
    last_queue_id: u16,
    planned_io_queues_after_replay: usize,
    next_io_queue_id_after_replay: u16,
    queue_numbering_restarted: bool,
    controller_limited: bool,
    planner_limited: bool,
    queue_planning_blocked: bool,
    queues_frozen: bool,
    cached_queue_reservation_stale: bool,
    cached_prp_metadata_stale: bool,
    descriptor_rebuild_required: bool,
    admin_queue_must_be_replanned: bool,
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
    uses_prp_list: bool,
    prp_list_entries: u16,
    prp_list_capacity: u16,
    prp_list_descriptor_bytes: u32,
    metadata_host_dma_bytes: u32,
    metadata_host_dma_pages: u16,
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

pub const DroppedIoRetirementSummary = struct {
    anchor: []const u8,
    state: RecoveryState,
    reset_generation: u32,
    admin_queue_replayed_after_reset: bool,
    admin_queue_must_be_replayed: bool,
    dropped_io_queue_count: usize,
    rebuilt_io_queue_count: usize,
    remaining_io_queue_count: usize,
    queue_numbering_restarted: bool,
    can_retire_dropped_io_backlog: bool,
};

pub const RecoveryRollbackGateSummary = struct {
    anchor: []const u8,
    state: RecoveryState,
    reset_generation: u32,
    admin_queue_replayed_after_reset: bool,
    queue_count_parity_recovered: bool,
    host_dma_parity_recovered: bool,
    queue_numbering_restarted: bool,
    dropped_io_queue_count: usize,
    rebuilt_io_queue_count: usize,
    remaining_io_queue_count: usize,
    dropped_io_host_dma_pages: u32,
    rebuilt_io_host_dma_pages: u32,
    remaining_io_host_dma_pages: u32,
    rollback_blocker: RecoveryRollbackBlocker,
    can_clear_rollback_gate: bool,
};

pub const IoQueueCountPlanSummary = struct {
    anchor: []const u8,
    requested_io_queues: usize,
    controller_io_queue_limit: usize,
    planner_remaining_io_slots: usize,
    selected_io_queues: usize,
    first_queue_id: u16,
    last_queue_id: u16,
    controller_limited: bool,
    planner_limited: bool,
    queues_frozen: bool,
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

pub const RecoveryReplayRequest = struct {
    cached_prp_metadata_generation: u32 = 0,
    had_prp_metadata_plan: bool = false,
    had_admin_queue_plan: bool = false,
    cached_queue_reservation_generation: u32 = 0,
    had_io_queue_reservation: bool = false,
    cached_reserved_io_queues: usize = 0,
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
    last_admin_queue_generation: u32 = 0,
    last_admin_host_dma_pages: u16 = 0,
    planned_io_host_dma_pages: u32 = 0,
    last_reset_io_queue_count: usize = 0,
    last_reset_io_host_dma_pages: u32 = 0,

    pub fn descriptor() ModuleDescriptor {
        return .{
            .name = "nvme_pci_queue_lab",
            .anchor = "drivers/nvme/host/pci.c",
            .provides_lab_queue_planner = true,
            .provides_dropped_io_retirement_helper = true,
            .provides_recovery_rollback_gate_helper = true,
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
        self.last_admin_queue_generation = summary.reset_generation;
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
            .reset_generation = self.reset_generation,
        };
    }

    pub fn planRecoveryReservationReplay(
        self: *const Self,
        request: RecoveryReplayRequest,
        controller_io_queue_limit: usize,
    ) !RecoveryReservationReplayPlanSummary {
        if (self.recovery_state != .running) return error.QueuePlanningBlockedByReset;
        if (!request.had_io_queue_reservation or request.cached_reserved_io_queues == 0) {
            return error.NoQueueReservationToReplay;
        }

        const cached_queue_reservation_stale = request.cached_queue_reservation_generation != self.reset_generation;
        if (!cached_queue_reservation_stale) {
            return error.QueueReservationAlreadyCurrent;
        }

        const admin_queue_must_be_replanned = request.had_admin_queue_plan and
            self.last_admin_queue_generation != self.reset_generation;
        if (admin_queue_must_be_replanned) {
            return error.AdminQueueReplayRequired;
        }

        const cached_prp_metadata_stale = request.had_prp_metadata_plan and
            request.cached_prp_metadata_generation != self.reset_generation;

        const plan = try self.planIoQueueCount(request.cached_reserved_io_queues, controller_io_queue_limit);
        return .{
            .anchor = plan.anchor,
            .state = self.recovery_state,
            .reset_generation = self.reset_generation,
            .requested_reserved_io_queues = request.cached_reserved_io_queues,
            .controller_io_queue_limit = controller_io_queue_limit,
            .planner_remaining_io_slots = plan.planner_remaining_io_slots,
            .replayable_reserved_io_queues = plan.selected_io_queues,
            .first_queue_id = plan.first_queue_id,
            .last_queue_id = plan.last_queue_id,
            .planned_io_queues_after_replay = try checkedAddUsize(self.planned_io_queues, plan.selected_io_queues),
            .next_io_queue_id_after_replay = try checkedAddU16(plan.last_queue_id, 1),
            .queue_numbering_restarted = self.reset_generation != 0 and plan.first_queue_id == 1,
            .controller_limited = plan.controller_limited,
            .planner_limited = plan.planner_limited,
            .queue_planning_blocked = false,
            .queues_frozen = plan.queues_frozen,
            .cached_queue_reservation_stale = true,
            .cached_prp_metadata_stale = cached_prp_metadata_stale,
            .descriptor_rebuild_required = cached_prp_metadata_stale,
            .admin_queue_must_be_replanned = false,
        };
    }

    pub fn replayReservedIoQueues(
        self: *Self,
        request: RecoveryReplayRequest,
        controller_io_queue_limit: usize,
    ) !IoQueueReservationSummary {
        const plan = try self.planRecoveryReservationReplay(request, controller_io_queue_limit);
        const reservation_delta = try checkedCastU16(plan.replayable_reserved_io_queues);

        self.next_io_queue_id = try checkedAddU16(self.next_io_queue_id, reservation_delta);
        self.planned_io_queues = try checkedAddUsize(self.planned_io_queues, plan.replayable_reserved_io_queues);

        return .{
            .anchor = plan.anchor,
            .requested_io_queues = plan.requested_reserved_io_queues,
            .controller_io_queue_limit = plan.controller_io_queue_limit,
            .planner_remaining_io_slots = plan.planner_remaining_io_slots,
            .reserved_io_queues = plan.replayable_reserved_io_queues,
            .first_queue_id = plan.first_queue_id,
            .last_queue_id = plan.last_queue_id,
            .planned_io_queues_after_reserve = self.planned_io_queues,
            .controller_limited = plan.controller_limited,
            .planner_limited = plan.planner_limited,
            .queues_frozen = plan.queues_frozen,
            .reset_generation = plan.reset_generation,
        };
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

    pub fn planPrpMetadataBudget(
        self: *const Self,
        total_transfer_bytes: u32,
        first_page_offset: u32,
    ) !PrpMetadataPlanSummary {
        const shape = try self.planPrpBufferShape(total_transfer_bytes, first_page_offset);
        const prp_list_descriptor_bytes = try checkedMulWideU32(
            @as(u32, shape.prp_list_entries),
            @as(u32, @sizeOf(u64)),
        );
        const metadata_host_dma_bytes = if (shape.uses_prp_list) self.page_size else 0;
        const metadata_host_dma_pages = try checkedDivCeilU16(metadata_host_dma_bytes, self.page_size);

        return .{
            .anchor = shape.anchor,
            .total_transfer_bytes = total_transfer_bytes,
            .first_page_offset = first_page_offset,
            .uses_prp_list = shape.uses_prp_list,
            .prp_list_entries = shape.prp_list_entries,
            .prp_list_capacity = shape.prp_list_capacity,
            .prp_list_descriptor_bytes = prp_list_descriptor_bytes,
            .metadata_host_dma_bytes = metadata_host_dma_bytes,
            .metadata_host_dma_pages = metadata_host_dma_pages,
        };
    }

    pub fn beginReset(self: *Self) RecoverySummary {
        self.last_reset_io_queue_count = self.planned_io_queues;
        self.last_reset_io_host_dma_pages = self.planned_io_host_dma_pages;
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

    pub fn summarizeDroppedIoRetirement(self: *const Self) DroppedIoRetirementSummary {
        const admin_queue_replayed_after_reset = self.last_admin_queue_generation == self.reset_generation;
        const dropped_io_queue_count = if (self.recovery_state == .reset_frozen)
            self.planned_io_queues
        else
            self.last_reset_io_queue_count;
        const rebuilt_io_queue_count = if (self.recovery_state == .running)
            self.planned_io_queues
        else
            0;
        const remaining_io_queue_count = if (rebuilt_io_queue_count >= dropped_io_queue_count)
            0
        else
            dropped_io_queue_count - rebuilt_io_queue_count;
        const admin_queue_must_be_replayed = self.reset_generation != 0 and !admin_queue_replayed_after_reset;
        const queue_numbering_restarted = self.reset_generation != 0 and
            self.recovery_state == .running and
            self.next_io_queue_id == @as(u16, @intCast(rebuilt_io_queue_count + 1));

        return .{
            .anchor = descriptor().anchor,
            .state = self.recovery_state,
            .reset_generation = self.reset_generation,
            .admin_queue_replayed_after_reset = admin_queue_replayed_after_reset,
            .admin_queue_must_be_replayed = admin_queue_must_be_replayed,
            .dropped_io_queue_count = dropped_io_queue_count,
            .rebuilt_io_queue_count = rebuilt_io_queue_count,
            .remaining_io_queue_count = remaining_io_queue_count,
            .queue_numbering_restarted = queue_numbering_restarted,
            .can_retire_dropped_io_backlog = self.recovery_state == .running and
                dropped_io_queue_count != 0 and
                !admin_queue_must_be_replayed and
                remaining_io_queue_count == 0,
        };
    }

    pub fn recoveryRollbackGateSummary(self: *const Self) RecoveryRollbackGateSummary {
        const retirement = self.summarizeDroppedIoRetirement();
        const dropped_io_host_dma_pages = if (self.recovery_state == .reset_frozen)
            self.planned_io_host_dma_pages
        else
            self.last_reset_io_host_dma_pages;
        const rebuilt_io_host_dma_pages = if (self.recovery_state == .running)
            self.planned_io_host_dma_pages
        else
            0;
        const remaining_io_host_dma_pages = if (rebuilt_io_host_dma_pages >= dropped_io_host_dma_pages)
            0
        else
            dropped_io_host_dma_pages - rebuilt_io_host_dma_pages;
        const queue_count_parity_recovered = !retirement.admin_queue_must_be_replayed and
            retirement.dropped_io_queue_count != 0 and
            retirement.remaining_io_queue_count == 0;
        const host_dma_parity_recovered = queue_count_parity_recovered and
            remaining_io_host_dma_pages == 0;

        const rollback_blocker: RecoveryRollbackBlocker = blk: {
            if (self.recovery_state == .reset_frozen) break :blk .reset_frozen;
            if (retirement.admin_queue_must_be_replayed) break :blk .admin_queue_replay;
            if (retirement.remaining_io_queue_count != 0) break :blk .queue_count_parity;
            if (remaining_io_host_dma_pages != 0) break :blk .dma_page_parity;
            break :blk .none;
        };

        return .{
            .anchor = descriptor().anchor,
            .state = self.recovery_state,
            .reset_generation = self.reset_generation,
            .admin_queue_replayed_after_reset = retirement.admin_queue_replayed_after_reset,
            .queue_count_parity_recovered = queue_count_parity_recovered,
            .host_dma_parity_recovered = host_dma_parity_recovered,
            .queue_numbering_restarted = retirement.queue_numbering_restarted,
            .dropped_io_queue_count = retirement.dropped_io_queue_count,
            .rebuilt_io_queue_count = retirement.rebuilt_io_queue_count,
            .remaining_io_queue_count = retirement.remaining_io_queue_count,
            .dropped_io_host_dma_pages = dropped_io_host_dma_pages,
            .rebuilt_io_host_dma_pages = rebuilt_io_host_dma_pages,
            .remaining_io_host_dma_pages = remaining_io_host_dma_pages,
            .rollback_blocker = rollback_blocker,
            .can_clear_rollback_gate = rollback_blocker == .none and
                retirement.dropped_io_queue_count != 0 and
                retirement.queue_numbering_restarted,
        };
    }

    fn planIoQueueCount(
        self: *const Self,
        requested_io_queues: usize,
        controller_io_queue_limit: usize,
    ) !IoQueueCountPlanSummary {
        if (self.recovery_state != .running) return error.QueuePlanningBlockedByReset;
        if (requested_io_queues == 0) return error.NoQueueReservationRequested;

        const planner_remaining_io_slots = max_planned_io_queues - self.planned_io_queues;
        if (planner_remaining_io_slots == 0) return error.TooManyPlannedIoQueues;

        const selected_io_queues = @min(requested_io_queues, @min(controller_io_queue_limit, planner_remaining_io_slots));
        if (selected_io_queues == 0) return error.NoControllerIoQueuesAvailable;

        const first_queue_id = self.next_io_queue_id;
        const last_queue_id = try checkedAddU16(
            first_queue_id,
            try checkedCastU16(selected_io_queues - 1),
        );

        return .{
            .anchor = descriptor().anchor,
            .requested_io_queues = requested_io_queues,
            .controller_io_queue_limit = controller_io_queue_limit,
            .planner_remaining_io_slots = planner_remaining_io_slots,
            .selected_io_queues = selected_io_queues,
            .first_queue_id = first_queue_id,
            .last_queue_id = last_queue_id,
            .controller_limited = selected_io_queues != requested_io_queues and
                controller_io_queue_limit <= planner_remaining_io_slots,
            .planner_limited = selected_io_queues != requested_io_queues and
                planner_remaining_io_slots < controller_io_queue_limit,
            .queues_frozen = false,
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

    fn checkedCastU16(value: usize) !u16 {
        return std.math.cast(u16, value) orelse error.QueueCountOverflow;
    }

    fn checkedAddU16(lhs: u16, rhs: u16) !u16 {
        const value = @as(u32, lhs) + rhs;
        return std.math.cast(u16, value) orelse error.QueueCountOverflow;
    }

    fn checkedAddUsize(lhs: usize, rhs: usize) !usize {
        return std.math.add(usize, lhs, rhs) catch error.QueueCountOverflow;
    }
};

test "nvme pci PRP metadata budget stays empty when inline PRP pointers cover the transfer" {
    var lab = try NvmePciQueueLab.init(4096, 8);

    const summary = try lab.planPrpMetadataBudget(4096 * 2 - 128, 128);
    try std.testing.expectEqualStrings("drivers/nvme/host/pci.c", summary.anchor);
    try std.testing.expectEqual(@as(u32, 4096 * 2 - 128), summary.total_transfer_bytes);
    try std.testing.expectEqual(@as(u32, 128), summary.first_page_offset);
    try std.testing.expect(!summary.uses_prp_list);
    try std.testing.expectEqual(@as(u16, 0), summary.prp_list_entries);
    try std.testing.expectEqual(@as(u16, 512), summary.prp_list_capacity);
    try std.testing.expectEqual(@as(u32, 0), summary.prp_list_descriptor_bytes);
    try std.testing.expectEqual(@as(u32, 0), summary.metadata_host_dma_bytes);
    try std.testing.expectEqual(@as(u16, 0), summary.metadata_host_dma_pages);
}

test "nvme pci PRP metadata budget reserves one metadata page once a PRP list is needed" {
    var lab = try NvmePciQueueLab.init(4096, 8);

    const summary = try lab.planPrpMetadataBudget(4096 * 5, 0);
    try std.testing.expect(summary.uses_prp_list);
    try std.testing.expectEqual(@as(u16, 3), summary.prp_list_entries);
    try std.testing.expectEqual(@as(u16, 512), summary.prp_list_capacity);
    try std.testing.expectEqual(@as(u32, 24), summary.prp_list_descriptor_bytes);
    try std.testing.expectEqual(@as(u32, 4096), summary.metadata_host_dma_bytes);
    try std.testing.expectEqual(@as(u16, 1), summary.metadata_host_dma_pages);

    const shape = try lab.planPrpBufferShape(4096 * 5, 0);
    try std.testing.expect(shape.uses_prp_list);
    try std.testing.expectEqual(shape.prp_list_entries, summary.prp_list_entries);
}

test "nvme pci recovery reservation replay marks stale PRP metadata as descriptor rebuild debt" {
    var lab = try NvmePciQueueLab.init(4096, 8);
    _ = try lab.planAdminQueue(32, 64, false);
    const reservation = try lab.reserveIoQueues(6, 6);
    _ = try lab.planPrpBufferShape(4096 * 3, 128);

    _ = lab.beginReset();
    _ = lab.completeReset();
    _ = try lab.planAdminQueue(32, 64, false);

    const stale = try lab.planRecoveryReservationReplay(.{
        .cached_prp_metadata_generation = reservation.reset_generation,
        .had_prp_metadata_plan = true,
        .had_admin_queue_plan = true,
        .cached_queue_reservation_generation = reservation.reset_generation,
        .had_io_queue_reservation = true,
        .cached_reserved_io_queues = reservation.reserved_io_queues,
    }, 3);
    try std.testing.expect(stale.cached_queue_reservation_stale);
    try std.testing.expect(stale.cached_prp_metadata_stale);
    try std.testing.expect(stale.descriptor_rebuild_required);

    const current = try lab.planRecoveryReservationReplay(.{
        .cached_prp_metadata_generation = stale.reset_generation,
        .had_prp_metadata_plan = true,
        .had_admin_queue_plan = true,
        .cached_queue_reservation_generation = reservation.reset_generation,
        .had_io_queue_reservation = true,
        .cached_reserved_io_queues = reservation.reserved_io_queues,
    }, 3);
    try std.testing.expect(current.cached_queue_reservation_stale);
    try std.testing.expect(!current.cached_prp_metadata_stale);
    try std.testing.expect(!current.descriptor_rebuild_required);
}

test "nvme pci recovery rollback gate waits for queue count and DMA parity after reset replay" {
    var lab = try NvmePciQueueLab.init(4096, 8);
    const descriptor = NvmePciQueueLab.descriptor();
    try std.testing.expect(descriptor.provides_recovery_rollback_gate_helper);

    _ = try lab.planAdminQueue(48, 64, false);
    _ = try lab.planIoQueue(64, 64, false);
    _ = try lab.planIoQueue(128, 64, false);

    _ = lab.beginReset();
    const frozen = lab.recoveryRollbackGateSummary();
    try std.testing.expectEqual(RecoveryRollbackBlocker.reset_frozen, frozen.rollback_blocker);
    try std.testing.expect(!frozen.can_clear_rollback_gate);

    _ = lab.completeReset();
    const replay_blocked = lab.recoveryRollbackGateSummary();
    try std.testing.expectEqual(RecoveryRollbackBlocker.admin_queue_replay, replay_blocked.rollback_blocker);
    try std.testing.expect(!replay_blocked.can_clear_rollback_gate);

    _ = try lab.planAdminQueue(48, 64, false);
    _ = try lab.planIoQueue(16, 64, true);
    const queue_blocked = lab.recoveryRollbackGateSummary();
    try std.testing.expectEqual(RecoveryRollbackBlocker.queue_count_parity, queue_blocked.rollback_blocker);
    try std.testing.expectEqual(@as(usize, 1), queue_blocked.remaining_io_queue_count);
    try std.testing.expect(!queue_blocked.can_clear_rollback_gate);

    _ = try lab.planIoQueue(32, 64, true);
    const dma_blocked = lab.recoveryRollbackGateSummary();
    try std.testing.expectEqual(RecoveryRollbackBlocker.dma_page_parity, dma_blocked.rollback_blocker);
    try std.testing.expectEqual(@as(u32, 3), dma_blocked.remaining_io_host_dma_pages);
    try std.testing.expect(!dma_blocked.can_clear_rollback_gate);

    var parity_lab = try NvmePciQueueLab.init(4096, 8);
    _ = try parity_lab.planAdminQueue(48, 64, false);
    _ = try parity_lab.planIoQueue(16, 64, false);
    _ = try parity_lab.planIoQueue(32, 64, true);
    _ = parity_lab.beginReset();
    _ = parity_lab.completeReset();
    _ = try parity_lab.planAdminQueue(48, 64, false);
    _ = try parity_lab.planIoQueue(16, 64, false);
    _ = try parity_lab.planIoQueue(32, 64, true);
    const ready = parity_lab.recoveryRollbackGateSummary();
    try std.testing.expectEqual(RecoveryRollbackBlocker.none, ready.rollback_blocker);
    try std.testing.expect(ready.queue_count_parity_recovered);
    try std.testing.expect(ready.host_dma_parity_recovered);
    try std.testing.expect(ready.queue_numbering_restarted);
    try std.testing.expect(ready.can_clear_rollback_gate);
}

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

test "nvme pci recovery reservation replay summary keeps post-replay queue numbering explicit" {
    var lab = try NvmePciQueueLab.init(4096, 8);
    _ = try lab.planAdminQueue(32, 64, false);
    const reservation = try lab.reserveIoQueues(8, 6);

    _ = lab.beginReset();
    _ = lab.completeReset();
    _ = try lab.planAdminQueue(32, 64, false);

    const summary = try lab.planRecoveryReservationReplay(.{
        .cached_prp_metadata_generation = 0,
        .had_prp_metadata_plan = false,
        .had_admin_queue_plan = true,
        .cached_queue_reservation_generation = reservation.reset_generation,
        .had_io_queue_reservation = true,
        .cached_reserved_io_queues = reservation.reserved_io_queues,
    }, 3);
    try std.testing.expectEqual(@as(usize, 3), summary.replayable_reserved_io_queues);
    try std.testing.expectEqual(@as(usize, 3), summary.planned_io_queues_after_replay);
    try std.testing.expectEqual(@as(u16, 4), summary.next_io_queue_id_after_replay);
    try std.testing.expect(summary.queue_numbering_restarted);

    const recovery = lab.recoverySummary();
    try std.testing.expectEqual(@as(usize, 0), recovery.planned_io_queues);
}

test "nvme pci dropped backlog retirement waits for admin replay and rebuilt queues" {
    var lab = try NvmePciQueueLab.init(4096, 8);
    _ = try lab.planAdminQueue(48, 64, false);
    _ = try lab.planIoQueue(16, 64, false);
    _ = try lab.planIoQueue(32, 64, true);

    _ = lab.beginReset();
    const frozen = lab.summarizeDroppedIoRetirement();
    try std.testing.expectEqualStrings("drivers/nvme/host/pci.c", frozen.anchor);
    try std.testing.expectEqual(RecoveryState.reset_frozen, frozen.state);
    try std.testing.expectEqual(@as(u32, 1), frozen.reset_generation);
    try std.testing.expect(!frozen.admin_queue_replayed_after_reset);
    try std.testing.expect(frozen.admin_queue_must_be_replayed);
    try std.testing.expectEqual(@as(usize, 2), frozen.dropped_io_queue_count);
    try std.testing.expectEqual(@as(usize, 0), frozen.rebuilt_io_queue_count);
    try std.testing.expectEqual(@as(usize, 2), frozen.remaining_io_queue_count);
    try std.testing.expect(!frozen.queue_numbering_restarted);
    try std.testing.expect(!frozen.can_retire_dropped_io_backlog);

    _ = lab.completeReset();
    const pending = lab.summarizeDroppedIoRetirement();
    try std.testing.expectEqual(RecoveryState.running, pending.state);
    try std.testing.expect(!pending.admin_queue_replayed_after_reset);
    try std.testing.expect(pending.admin_queue_must_be_replayed);
    try std.testing.expectEqual(@as(usize, 2), pending.dropped_io_queue_count);
    try std.testing.expectEqual(@as(usize, 0), pending.rebuilt_io_queue_count);
    try std.testing.expectEqual(@as(usize, 2), pending.remaining_io_queue_count);
    try std.testing.expect(pending.queue_numbering_restarted);
    try std.testing.expect(!pending.can_retire_dropped_io_backlog);

    _ = try lab.planAdminQueue(48, 64, false);
    _ = try lab.planIoQueue(16, 64, false);
    const partial = lab.summarizeDroppedIoRetirement();
    try std.testing.expect(partial.admin_queue_replayed_after_reset);
    try std.testing.expect(!partial.admin_queue_must_be_replayed);
    try std.testing.expectEqual(@as(usize, 1), partial.rebuilt_io_queue_count);
    try std.testing.expectEqual(@as(usize, 1), partial.remaining_io_queue_count);
    try std.testing.expect(partial.queue_numbering_restarted);
    try std.testing.expect(!partial.can_retire_dropped_io_backlog);

    _ = try lab.planIoQueue(32, 64, true);
    const ready = lab.summarizeDroppedIoRetirement();
    try std.testing.expect(ready.admin_queue_replayed_after_reset);
    try std.testing.expectEqual(@as(usize, 2), ready.dropped_io_queue_count);
    try std.testing.expectEqual(@as(usize, 2), ready.rebuilt_io_queue_count);
    try std.testing.expectEqual(@as(usize, 0), ready.remaining_io_queue_count);
    try std.testing.expect(ready.queue_numbering_restarted);
    try std.testing.expect(ready.can_retire_dropped_io_backlog);
}

test "nvme pci dropped backlog retirement stays idle before any reset backlog exists" {
    var lab = try NvmePciQueueLab.init(4096, 8);
    _ = try lab.planAdminQueue(24, 64, false);
    _ = try lab.planIoQueue(8, 64, false);

    const summary = lab.summarizeDroppedIoRetirement();
    try std.testing.expectEqual(RecoveryState.running, summary.state);
    try std.testing.expectEqual(@as(u32, 0), summary.reset_generation);
    try std.testing.expect(summary.admin_queue_replayed_after_reset);
    try std.testing.expect(!summary.admin_queue_must_be_replayed);
    try std.testing.expectEqual(@as(usize, 0), summary.dropped_io_queue_count);
    try std.testing.expectEqual(@as(usize, 1), summary.rebuilt_io_queue_count);
    try std.testing.expectEqual(@as(usize, 0), summary.remaining_io_queue_count);
    try std.testing.expect(!summary.queue_numbering_restarted);
    try std.testing.expect(!summary.can_retire_dropped_io_backlog);
}
