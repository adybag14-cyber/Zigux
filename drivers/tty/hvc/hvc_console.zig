const std = @import("std");

pub const max_nr_hvc_consoles: usize = 16;
pub const alloc_tty_adapters: usize = 8;
pub const outbuf_capacity: usize = 16;
pub const removed_vtermno: u32 = std.math.maxInt(u32);
pub const eagain: isize = -11;
pub const close_wait_hz_divisor: usize = 100;
pub const min_khvcd_timeout_ms: u32 = 10;
pub const max_khvcd_timeout_ms: u32 = 2000;
pub const epipe: isize = -32;
pub const einval: c_int = -22;

pub const FlushIntent = enum {
    none,
    retry_after_eagain,
    final_drain,
};

pub const FlushProgress = enum {
    no_progress,
    partial_write,
    fully_written,
    dropped_on_error,
};

pub const ModuleDescriptor = struct {
    name: []const u8,
    anchor: []const u8,
    provides_simple_driver_starter: bool,
    touches_tty_registration: bool,
    touches_polling_kthread: bool,
    touches_live_hypervisor_io: bool,
};

pub const HvOpsHeaderSurface = struct {
    has_get_chars: bool,
    has_put_chars: bool,
    has_flush: bool,
    has_notifier_add: bool,
    has_notifier_del: bool,
    has_notifier_hangup: bool,
    has_tiocmget: bool,
    has_tiocmset: bool,
    has_dtr_rts: bool,
};

pub const HeaderParitySnapshot = struct {
    anchor: []const u8,
    max_nr_hvc_consoles: usize,
    alloc_tty_adapters: usize,
    exports_instantiate: bool,
    exports_alloc: bool,
    exports_remove: bool,
    exports_poll: bool,
    exports_resize: bool,
    exports_kick: bool,
    exports_notifier_add_irq: bool,
    exports_notifier_del_irq: bool,
    exports_notifier_hangup_irq: bool,
    hv_ops: HvOpsHeaderSurface,
    keeps_tty_registration_out_of_scope: bool,
    keeps_live_hypervisor_io_out_of_scope: bool,
};

pub const SlotSnapshot = struct {
    anchor: []const u8,
    slot_index: usize,
    vtermno: u32,
    adapter_present: bool,
    usable_for_console: bool,
};

pub const CloseRequest = struct {
    hung_up: bool = false,
    port_initialized: bool = false,
    open_count_before_close: usize = 1,
};

pub const CloseBoundarySnapshot = struct {
    anchor: []const u8,
    slot_index: usize,
    vtermno: u32,
    adapter_present: bool,
    hung_up: bool,
    close_skipped: bool,
    port_initialized: bool,
    open_count_before_close: usize,
    open_count_after_close: usize,
    final_close: bool,
    close_wait_required: bool,
    close_wait_hz_divisor: usize,
    clears_port_initialized: bool,
    keeps_console_binding: bool,
    tty_registration_pending: bool,
};

pub const CloseTeardownRequest = struct {
    close: CloseRequest = .{},
    hupcl: bool = false,
    dtr_rts_present: bool = false,
    notifier_del_present: bool = false,
};

pub const CloseTeardownSnapshot = struct {
    anchor: []const u8,
    slot_index: usize,
    vtermno: u32,
    adapter_present: bool,
    final_close: bool,
    close_skipped: bool,
    tty_detached: bool,
    dtr_rts_drop_requested: bool,
    notifier_del_pending: bool,
    cancel_resize_pending: bool,
    wait_until_sent_required: bool,
    close_wait_hz_divisor: usize,
    clears_port_initialized: bool,
    keeps_console_binding: bool,
};

pub const ModemControlRequest = struct {
    tiocmget_present: bool = false,
    tiocmget_result: c_int = 0,
    tiocmset_present: bool = false,
    tiocmset_result: c_int = 0,
    set_mask: c_uint = 0,
    clear_mask: c_uint = 0,
};

pub const ModemControlSnapshot = struct {
    anchor: []const u8,
    slot_index: usize,
    vtermno: u32,
    adapter_present: bool,
    tiocmget_present: bool,
    tiocmget_routes_hp_directly: bool,
    tiocmget_returns_einval_fallback: bool,
    tiocmget_result: c_int,
    tiocmset_present: bool,
    tiocmset_routes_hp_directly: bool,
    tiocmset_returns_einval_fallback: bool,
    tiocmset_result: c_int,
    set_mask: c_uint,
    clear_mask: c_uint,
    set_mask_passthrough: bool,
    clear_mask_passthrough: bool,
};

pub const TtyRegistrationHandoffSnapshot = struct {
    anchor: []const u8,
    slot_index: usize,
    vtermno: u32,
    adapter_present: bool,
    setup_hvc_console_pending: bool,
    tty_registration_pending: bool,
    final_close_wait_required: bool,
    clears_port_initialized_on_final_close: bool,
    keeps_console_binding: bool,
    khvcd_kick_on_open: bool,
    khvcd_kick_on_unthrottle: bool,
    khvcd_polling_pending: bool,
    notifier_callbacks_pending: bool,
    host_io_pending: bool,
};

pub const NotifierAddOutcomeRequest = struct {
    close: CloseRequest = .{},
    notifier_add_present: bool = false,
    notifier_add_result: isize = 0,
};

pub const NotifierAddOutcomeSnapshot = struct {
    anchor: []const u8,
    slot_index: usize,
    vtermno: u32,
    adapter_present: bool,
    tty_registration_pending: bool,
    final_close_wait_required: bool,
    clears_port_initialized_on_final_close: bool,
    keeps_console_binding: bool,
    notifier_add_present: bool,
    notifier_add_attempted: bool,
    notifier_add_succeeded: bool,
    notifier_add_failed: bool,
    irq_requested_after_open: bool,
    polling_fallback_required: bool,
    close_cleanup_required: bool,
    khvcd_kick_required: bool,
    host_io_pending: bool,
};

pub const KhvcdPollingContractRequest = struct {
    close: CloseRequest = .{},
    notifier_add_pending: bool = false,
    notifier_del_pending: bool = false,
    notifier_hangup_pending: bool = false,
    read_poll_pending: bool = false,
    write_poll_pending: bool = false,
};

pub const KhvcdPollingContractSnapshot = struct {
    anchor: []const u8,
    slot_index: usize,
    vtermno: u32,
    adapter_present: bool,
    final_close_wait_required: bool,
    clears_port_initialized_on_final_close: bool,
    keeps_console_binding: bool,
    tty_registration_pending: bool,
    khvcd_polling_pending: bool,
    notifier_driven_wakeup: bool,
    poll_driven_wakeup: bool,
    khvcd_wakeup_required: bool,
    reschedule_required: bool,
    notifier_add_pending: bool,
    notifier_del_pending: bool,
    notifier_hangup_pending: bool,
    read_poll_pending: bool,
    write_poll_pending: bool,
    teardown_host_io_pending: bool,
};

pub const KhvcdWorkerEntryRequest = struct {
    contract: KhvcdPollingContractRequest = .{},
    cpus_in_xmon: bool = false,
    kick_pending_after_walk: bool = false,
    timeout_ms: u32 = min_khvcd_timeout_ms,
};

pub const KhvcdWorkerEntrySnapshot = struct {
    anchor: []const u8,
    slot_index: usize,
    vtermno: u32,
    adapter_present: bool,
    final_close_wait_required: bool,
    clears_port_initialized_on_final_close: bool,
    keeps_console_binding: bool,
    tty_registration_pending: bool,
    khvcd_polling_pending: bool,
    notifier_driven_wakeup: bool,
    poll_driven_wakeup: bool,
    checks_freezer_before_poll_walk: bool,
    resets_kick_before_poll_walk: bool,
    walks_hvc_structs_under_mutex: bool,
    xmon_forces_read_poll: bool,
    poll_read_pending: bool,
    poll_write_pending: bool,
    wakeup_on_kick: bool,
    skip_sleep_due_to_kick: bool,
    sleeps_without_timeout: bool,
    timeout_backoff_active: bool,
    sleep_timeout_ms: u32,
    timeout_capped_at_max: bool,
    backend_handoff_pending: bool,
};

pub const KhvcdSleepHandoffRequest = struct {
    entry: KhvcdWorkerEntryRequest = .{},
    kick_pending_after_interruptible_state: bool = false,
};

pub const KhvcdSleepHandoffSnapshot = struct {
    anchor: []const u8,
    slot_index: usize,
    vtermno: u32,
    adapter_present: bool,
    final_close_wait_required: bool,
    clears_port_initialized_on_final_close: bool,
    keeps_console_binding: bool,
    tty_registration_pending: bool,
    khvcd_polling_pending: bool,
    poll_read_pending: bool,
    poll_write_pending: bool,
    checks_kick_before_sleep_state: bool,
    kick_short_circuits_before_sleep_state: bool,
    sets_interruptible_before_sleep_recheck: bool,
    checks_kick_after_interruptible_state: bool,
    skip_schedule_due_to_post_state_kick: bool,
    schedule_without_timeout: bool,
    schedule_timeout_interruptible: bool,
    timeout_backoff_grows_before_timed_sleep: bool,
    sleep_timeout_ms: u32,
    timeout_capped_at_max: bool,
    timed_sleep_uses_guard_tick: bool,
    restores_running_state_after_handoff: bool,
    backend_handoff_pending: bool,
};

pub const PollDrainOrderRequest = struct {
    contract: KhvcdPollingContractRequest = .{},
    may_sleep: bool = false,
    tty_attached: bool = true,
    tty_throttled: bool = false,
    irq_requested: bool = false,
    buffered_write_len: usize = 0,
    write_result: isize = 0,
    flip_room_available: bool = true,
    read_result: isize = 0,
    preexisting_do_wakeup: bool = false,
};

pub const PollDrainOrderSnapshot = struct {
    anchor: []const u8,
    slot_index: usize,
    vtermno: u32,
    adapter_present: bool,
    final_close_wait_required: bool,
    clears_port_initialized_on_final_close: bool,
    keeps_console_binding: bool,
    tty_registration_pending: bool,
    write_drain_precedes_read_path: bool,
    write_drain_attempted: bool,
    write_remaining_len: usize,
    write_poll_pending_after_drain: bool,
    write_progress_resets_timeout: bool,
    stalled_write_uses_min_timeout: bool,
    releases_lock_before_read_retry: bool,
    tty_required_for_read_path: bool,
    throttled_read_skipped: bool,
    read_poll_armed_without_irq: bool,
    read_poll_pending_after_drain: bool,
    read_hangup_pending: bool,
    read_bytes_drained: usize,
    wakeup_before_unlock: bool,
    flip_push_after_unlock: bool,
    wakeup_precedes_flip_push: bool,
    backend_handoff_pending: bool,
};

pub const HangupDisconnectRequest = struct {
    port_count_before_hangup: usize = 1,
    notifier_hangup_present: bool = false,
    buffered_write_len: usize = 0,
};

pub const HangupDisconnectSnapshot = struct {
    anchor: []const u8,
    slot_index: usize,
    vtermno: u32,
    adapter_present: bool,
    cancel_resize_pending: bool,
    hangup_skipped: bool,
    port_count_before_hangup: usize,
    port_count_after_hangup: usize,
    tty_detached: bool,
    clears_outbuf: bool,
    buffered_write_len_before_hangup: usize,
    buffered_write_len_after_hangup: usize,
    notifier_hangup_pending: bool,
    keeps_console_binding: bool,
};

pub const RemoveHandoffRequest = struct {
    tty_attached: bool = true,
};

pub const RemoveHandoffSnapshot = struct {
    anchor: []const u8,
    slot_index: usize,
    vtermno: u32,
    adapter_present: bool,
    console_lock_brackets_slot_clear: bool,
    clears_vtermno_slot: bool,
    clears_cons_ops_slot: bool,
    keeps_irq_until_hangup: bool,
    tty_port_put_requested: bool,
    tty_port_put_precedes_tty_vhangup: bool,
    console_unlock_precedes_tty_vhangup: bool,
    tty_vhangup_requested: bool,
    tty_kref_put_after_vhangup: bool,
    teardown_deferred_to_hangup: bool,
};

pub const CleanupHandoffRequest = struct {
    close_skipped: bool = false,
    final_close: bool = true,
};

pub const CleanupHandoffSnapshot = struct {
    anchor: []const u8,
    slot_index: usize,
    vtermno: u32,
    adapter_present: bool,
    close_skipped: bool,
    final_close: bool,
    tty_port_put_requested: bool,
    drops_tty_port_reference: bool,
    defers_final_release_to_port_destruct: bool,
    keeps_console_binding: bool,
};

pub const WriteSnapshot = struct {
    anchor: []const u8,
    slot_index: usize,
    adapter_present: bool,
    framed_len: usize,
    framed: [outbuf_capacity * 2]u8,
    remaining_len: usize,
    remaining: [outbuf_capacity * 2]u8,
    flush_intent: FlushIntent,
    flush_progress: FlushProgress,
    final_flush: bool,
    dropped_on_error: bool,
};

pub const HvcConsoleLab = struct {
    const Self = @This();

    slot_index: usize,
    vtermno: u32 = removed_vtermno,
    adapter_present: bool = false,

    pub fn descriptor() ModuleDescriptor {
        return .{
            .name = "hvc_console_lab",
            .anchor = "drivers/tty/hvc/hvc_console.c",
            .provides_simple_driver_starter = true,
            .touches_tty_registration = false,
            .touches_polling_kthread = false,
            .touches_live_hypervisor_io = false,
        };
    }

    pub fn init(slot_index: usize) !Self {
        try validateConsoleSlot(slot_index);
        return .{ .slot_index = slot_index };
    }

    pub fn instantiate(self: *Self, vtermno: u32) SlotSnapshot {
        self.vtermno = vtermno;
        self.adapter_present = true;
        return self.slotSnapshot();
    }

    pub fn teardown(self: *Self) SlotSnapshot {
        self.vtermno = removed_vtermno;
        self.adapter_present = false;
        return self.slotSnapshot();
    }

    pub fn slotSnapshot(self: *const Self) SlotSnapshot {
        return .{
            .anchor = descriptor().anchor,
            .slot_index = self.slot_index,
            .vtermno = self.vtermno,
            .adapter_present = self.adapter_present,
            .usable_for_console = self.adapter_present and self.vtermno != removed_vtermno,
        };
    }

    pub fn summarizeCloseBoundary(self: *const Self, request: CloseRequest) !CloseBoundarySnapshot {
        const slot = self.slotSnapshot();
        if (!slot.usable_for_console) return error.ConsoleUnavailable;
        if (request.open_count_before_close == 0) return error.InvalidOpenCount;

        const close_skipped = request.hung_up;
        const open_count_after_close = if (close_skipped)
            request.open_count_before_close
        else
            request.open_count_before_close - 1;
        const final_close = !close_skipped and open_count_after_close == 0;
        const close_wait_required = final_close and request.port_initialized;

        return .{
            .anchor = descriptor().anchor,
            .slot_index = self.slot_index,
            .vtermno = self.vtermno,
            .adapter_present = self.adapter_present,
            .hung_up = request.hung_up,
            .close_skipped = close_skipped,
            .port_initialized = request.port_initialized,
            .open_count_before_close = request.open_count_before_close,
            .open_count_after_close = open_count_after_close,
            .final_close = final_close,
            .close_wait_required = close_wait_required,
            .close_wait_hz_divisor = close_wait_hz_divisor,
            .clears_port_initialized = close_wait_required,
            .keeps_console_binding = true,
            .tty_registration_pending = true,
        };
    }

    pub fn summarizeTtyRegistrationHandoff(self: *const Self, request: CloseRequest) !TtyRegistrationHandoffSnapshot {
        const close = try self.summarizeCloseBoundary(request);

        return .{
            .anchor = descriptor().anchor,
            .slot_index = close.slot_index,
            .vtermno = close.vtermno,
            .adapter_present = close.adapter_present,
            .setup_hvc_console_pending = true,
            .tty_registration_pending = true,
            .final_close_wait_required = close.close_wait_required,
            .clears_port_initialized_on_final_close = close.clears_port_initialized,
            .keeps_console_binding = close.keeps_console_binding,
            .khvcd_kick_on_open = true,
            .khvcd_kick_on_unthrottle = true,
            .khvcd_polling_pending = true,
            .notifier_callbacks_pending = true,
            .host_io_pending = true,
        };
    }

    pub fn summarizeNotifierAddOutcome(
        self: *const Self,
        request: NotifierAddOutcomeRequest,
    ) !NotifierAddOutcomeSnapshot {
        const handoff = try self.summarizeTtyRegistrationHandoff(request.close);
        const notifier_add_attempted = request.notifier_add_present;
        const notifier_add_succeeded = notifier_add_attempted and request.notifier_add_result >= 0;
        const notifier_add_failed = notifier_add_attempted and request.notifier_add_result < 0;

        return .{
            .anchor = descriptor().anchor,
            .slot_index = handoff.slot_index,
            .vtermno = handoff.vtermno,
            .adapter_present = handoff.adapter_present,
            .tty_registration_pending = handoff.tty_registration_pending,
            .final_close_wait_required = handoff.final_close_wait_required,
            .clears_port_initialized_on_final_close = handoff.clears_port_initialized_on_final_close,
            .keeps_console_binding = handoff.keeps_console_binding,
            .notifier_add_present = request.notifier_add_present,
            .notifier_add_attempted = notifier_add_attempted,
            .notifier_add_succeeded = notifier_add_succeeded,
            .notifier_add_failed = notifier_add_failed,
            .irq_requested_after_open = notifier_add_succeeded,
            .polling_fallback_required = !notifier_add_succeeded,
            .close_cleanup_required = notifier_add_failed,
            .khvcd_kick_required = handoff.khvcd_kick_on_open or !notifier_add_succeeded,
            .host_io_pending = handoff.host_io_pending,
        };
    }

    pub fn summarizeCloseTeardown(
        self: *const Self,
        request: CloseTeardownRequest,
    ) !CloseTeardownSnapshot {
        const close = try self.summarizeCloseBoundary(request.close);
        const teardown_active = close.final_close and close.port_initialized;

        return .{
            .anchor = descriptor().anchor,
            .slot_index = close.slot_index,
            .vtermno = close.vtermno,
            .adapter_present = close.adapter_present,
            .final_close = close.final_close,
            .close_skipped = close.close_skipped,
            .tty_detached = close.final_close and !close.close_skipped,
            .dtr_rts_drop_requested = teardown_active and request.hupcl and request.dtr_rts_present,
            .notifier_del_pending = teardown_active and request.notifier_del_present,
            .cancel_resize_pending = teardown_active,
            .wait_until_sent_required = teardown_active,
            .close_wait_hz_divisor = close.close_wait_hz_divisor,
            .clears_port_initialized = close.clears_port_initialized,
            .keeps_console_binding = close.keeps_console_binding,
        };
    }

    pub fn summarizeModemControl(
        self: *const Self,
        request: ModemControlRequest,
    ) !ModemControlSnapshot {
        const slot = self.slotSnapshot();
        if (!slot.usable_for_console) return error.ConsoleUnavailable;

        return .{
            .anchor = descriptor().anchor,
            .slot_index = slot.slot_index,
            .vtermno = slot.vtermno,
            .adapter_present = slot.adapter_present,
            .tiocmget_present = request.tiocmget_present,
            .tiocmget_routes_hp_directly = request.tiocmget_present,
            .tiocmget_returns_einval_fallback = !request.tiocmget_present,
            .tiocmget_result = if (request.tiocmget_present) request.tiocmget_result else einval,
            .tiocmset_present = request.tiocmset_present,
            .tiocmset_routes_hp_directly = request.tiocmset_present,
            .tiocmset_returns_einval_fallback = !request.tiocmset_present,
            .tiocmset_result = if (request.tiocmset_present) request.tiocmset_result else einval,
            .set_mask = request.set_mask,
            .clear_mask = request.clear_mask,
            .set_mask_passthrough = request.tiocmset_present,
            .clear_mask_passthrough = request.tiocmset_present,
        };
    }

    pub fn summarizeKhvcdPollingContract(
        self: *const Self,
        request: KhvcdPollingContractRequest,
    ) !KhvcdPollingContractSnapshot {
        const handoff = try self.summarizeTtyRegistrationHandoff(request.close);
        const notifier_driven_wakeup = request.notifier_add_pending or
            request.notifier_del_pending or
            request.notifier_hangup_pending;
        const poll_driven_wakeup = request.read_poll_pending or request.write_poll_pending;

        return .{
            .anchor = descriptor().anchor,
            .slot_index = handoff.slot_index,
            .vtermno = handoff.vtermno,
            .adapter_present = handoff.adapter_present,
            .final_close_wait_required = handoff.final_close_wait_required,
            .clears_port_initialized_on_final_close = handoff.clears_port_initialized_on_final_close,
            .keeps_console_binding = handoff.keeps_console_binding,
            .tty_registration_pending = handoff.tty_registration_pending,
            .khvcd_polling_pending = handoff.khvcd_polling_pending,
            .notifier_driven_wakeup = notifier_driven_wakeup,
            .poll_driven_wakeup = poll_driven_wakeup,
            .khvcd_wakeup_required = handoff.khvcd_kick_on_open or
                handoff.khvcd_kick_on_unthrottle or
                notifier_driven_wakeup or
                poll_driven_wakeup,
            .reschedule_required = poll_driven_wakeup,
            .notifier_add_pending = request.notifier_add_pending,
            .notifier_del_pending = request.notifier_del_pending,
            .notifier_hangup_pending = request.notifier_hangup_pending,
            .read_poll_pending = request.read_poll_pending,
            .write_poll_pending = request.write_poll_pending,
            .teardown_host_io_pending = handoff.host_io_pending or poll_driven_wakeup,
        };
    }

    pub fn summarizeKhvcdWorkerEntry(
        self: *const Self,
        request: KhvcdWorkerEntryRequest,
    ) !KhvcdWorkerEntrySnapshot {
        const contract = try self.summarizeKhvcdPollingContract(request.contract);
        const xmon_forces_read_poll = request.cpus_in_xmon;
        const poll_read_pending = contract.read_poll_pending or xmon_forces_read_poll;
        const poll_write_pending = contract.write_poll_pending;
        const poll_mask_pending = poll_read_pending or poll_write_pending;
        const skip_sleep_due_to_kick = request.kick_pending_after_walk;
        const sleeps_without_timeout = !skip_sleep_due_to_kick and !poll_mask_pending;
        const timeout_backoff_active = !skip_sleep_due_to_kick and poll_mask_pending;
        const sleep_timeout_ms = if (timeout_backoff_active)
            growKhvcdTimeout(request.timeout_ms)
        else
            0;

        return .{
            .anchor = descriptor().anchor,
            .slot_index = contract.slot_index,
            .vtermno = contract.vtermno,
            .adapter_present = contract.adapter_present,
            .final_close_wait_required = contract.final_close_wait_required,
            .clears_port_initialized_on_final_close = contract.clears_port_initialized_on_final_close,
            .keeps_console_binding = contract.keeps_console_binding,
            .tty_registration_pending = contract.tty_registration_pending,
            .khvcd_polling_pending = contract.khvcd_polling_pending,
            .notifier_driven_wakeup = contract.notifier_driven_wakeup,
            .poll_driven_wakeup = contract.poll_driven_wakeup,
            .checks_freezer_before_poll_walk = true,
            .resets_kick_before_poll_walk = true,
            .walks_hvc_structs_under_mutex = !request.cpus_in_xmon,
            .xmon_forces_read_poll = xmon_forces_read_poll,
            .poll_read_pending = poll_read_pending,
            .poll_write_pending = poll_write_pending,
            .wakeup_on_kick = true,
            .skip_sleep_due_to_kick = skip_sleep_due_to_kick,
            .sleeps_without_timeout = sleeps_without_timeout,
            .timeout_backoff_active = timeout_backoff_active,
            .sleep_timeout_ms = sleep_timeout_ms,
            .timeout_capped_at_max = timeout_backoff_active and sleep_timeout_ms == max_khvcd_timeout_ms,
            .backend_handoff_pending = contract.teardown_host_io_pending or poll_mask_pending,
        };
    }

    pub fn summarizeKhvcdSleepHandoff(
        self: *const Self,
        request: KhvcdSleepHandoffRequest,
    ) !KhvcdSleepHandoffSnapshot {
        const entry = try self.summarizeKhvcdWorkerEntry(request.entry);
        const kick_short_circuits_before_sleep_state = request.entry.kick_pending_after_walk;
        const sets_interruptible_before_sleep_recheck = !kick_short_circuits_before_sleep_state;
        const checks_kick_after_interruptible_state = sets_interruptible_before_sleep_recheck;
        const skipScheduleDueToPostStateKick = checks_kick_after_interruptible_state and
            request.kick_pending_after_interruptible_state;
        const schedule_without_timeout = checks_kick_after_interruptible_state and
            !request.kick_pending_after_interruptible_state and
            entry.sleeps_without_timeout;
        const schedule_timeout_interruptible = checks_kick_after_interruptible_state and
            !request.kick_pending_after_interruptible_state and
            entry.timeout_backoff_active;

        return .{
            .anchor = descriptor().anchor,
            .slot_index = entry.slot_index,
            .vtermno = entry.vtermno,
            .adapter_present = entry.adapter_present,
            .final_close_wait_required = entry.final_close_wait_required,
            .clears_port_initialized_on_final_close = entry.clears_port_initialized_on_final_close,
            .keeps_console_binding = entry.keeps_console_binding,
            .tty_registration_pending = entry.tty_registration_pending,
            .khvcd_polling_pending = entry.khvcd_polling_pending,
            .poll_read_pending = entry.poll_read_pending,
            .poll_write_pending = entry.poll_write_pending,
            .checks_kick_before_sleep_state = true,
            .kick_short_circuits_before_sleep_state = kick_short_circuits_before_sleep_state,
            .sets_interruptible_before_sleep_recheck = sets_interruptible_before_sleep_recheck,
            .checks_kick_after_interruptible_state = checks_kick_after_interruptible_state,
            .skip_schedule_due_to_post_state_kick = skipScheduleDueToPostStateKick,
            .schedule_without_timeout = schedule_without_timeout,
            .schedule_timeout_interruptible = schedule_timeout_interruptible,
            .timeout_backoff_grows_before_timed_sleep = schedule_timeout_interruptible,
            .sleep_timeout_ms = if (schedule_timeout_interruptible) entry.sleep_timeout_ms else 0,
            .timeout_capped_at_max = schedule_timeout_interruptible and entry.timeout_capped_at_max,
            .timed_sleep_uses_guard_tick = schedule_timeout_interruptible,
            .restores_running_state_after_handoff = !kick_short_circuits_before_sleep_state,
            .backend_handoff_pending = entry.backend_handoff_pending,
        };
    }

    pub fn summarizePollDrainOrder(
        self: *const Self,
        request: PollDrainOrderRequest,
    ) !PollDrainOrderSnapshot {
        const contract = try self.summarizeKhvcdPollingContract(request.contract);
        const write_drain = summarizePollWriteDrain(
            request.buffered_write_len,
            request.write_result,
            request.preexisting_do_wakeup,
        );

        const tty_required_for_read_path = request.tty_attached;
        const throttled_read_skipped = tty_required_for_read_path and request.tty_throttled;
        const read_poll_armed_without_irq = tty_required_for_read_path and
            !request.tty_throttled and
            !request.irq_requested;
        const read_bytes_drained = if (request.read_result > 0)
            @as(usize, @intCast(request.read_result))
        else
            0;
        const read_hangup_pending = tty_required_for_read_path and
            !request.tty_throttled and
            request.read_result == epipe;
        const read_poll_pending_after_drain = read_poll_armed_without_irq or
            (tty_required_for_read_path and !request.tty_throttled and !request.flip_room_available) or
            (tty_required_for_read_path and !request.tty_throttled and request.read_result == eagain) or
            (tty_required_for_read_path and !request.tty_throttled and !request.may_sleep and read_bytes_drained > 0);
        const wakeup_before_unlock = tty_required_for_read_path and write_drain.do_wakeup;
        const flip_push_after_unlock = read_bytes_drained > 0;

        return .{
            .anchor = descriptor().anchor,
            .slot_index = contract.slot_index,
            .vtermno = contract.vtermno,
            .adapter_present = contract.adapter_present,
            .final_close_wait_required = contract.final_close_wait_required,
            .clears_port_initialized_on_final_close = contract.clears_port_initialized_on_final_close,
            .keeps_console_binding = contract.keeps_console_binding,
            .tty_registration_pending = contract.tty_registration_pending,
            .write_drain_precedes_read_path = true,
            .write_drain_attempted = request.buffered_write_len > 0,
            .write_remaining_len = write_drain.remaining_len,
            .write_poll_pending_after_drain = write_drain.remaining_len > 0,
            .write_progress_resets_timeout = write_drain.progress_resets_timeout,
            .stalled_write_uses_min_timeout = write_drain.stalled_write_uses_min_timeout,
            .releases_lock_before_read_retry = request.may_sleep,
            .tty_required_for_read_path = tty_required_for_read_path,
            .throttled_read_skipped = throttled_read_skipped,
            .read_poll_armed_without_irq = read_poll_armed_without_irq,
            .read_poll_pending_after_drain = read_poll_pending_after_drain,
            .read_hangup_pending = read_hangup_pending,
            .read_bytes_drained = read_bytes_drained,
            .wakeup_before_unlock = wakeup_before_unlock,
            .flip_push_after_unlock = flip_push_after_unlock,
            .wakeup_precedes_flip_push = wakeup_before_unlock and flip_push_after_unlock,
            .backend_handoff_pending = contract.teardown_host_io_pending or
                write_drain.remaining_len > 0 or
                read_poll_pending_after_drain or
                read_hangup_pending or
                flip_push_after_unlock,
        };
    }

    pub fn summarizeHangupDisconnect(
        self: *const Self,
        request: HangupDisconnectRequest,
    ) !HangupDisconnectSnapshot {
        const slot = self.slotSnapshot();
        if (!slot.usable_for_console) return error.ConsoleUnavailable;

        const hangup_skipped = request.port_count_before_hangup == 0;
        return .{
            .anchor = descriptor().anchor,
            .slot_index = slot.slot_index,
            .vtermno = slot.vtermno,
            .adapter_present = slot.adapter_present,
            .cancel_resize_pending = true,
            .hangup_skipped = hangup_skipped,
            .port_count_before_hangup = request.port_count_before_hangup,
            .port_count_after_hangup = 0,
            .tty_detached = !hangup_skipped,
            .clears_outbuf = !hangup_skipped,
            .buffered_write_len_before_hangup = request.buffered_write_len,
            .buffered_write_len_after_hangup = if (hangup_skipped) request.buffered_write_len else 0,
            .notifier_hangup_pending = !hangup_skipped and request.notifier_hangup_present,
            .keeps_console_binding = true,
        };
    }

    pub fn summarizeRemoveHandoff(
        self: *const Self,
        request: RemoveHandoffRequest,
    ) !RemoveHandoffSnapshot {
        const slot = self.slotSnapshot();
        if (!slot.usable_for_console) return error.ConsoleUnavailable;

        return .{
            .anchor = descriptor().anchor,
            .slot_index = slot.slot_index,
            .vtermno = slot.vtermno,
            .adapter_present = slot.adapter_present,
            .console_lock_brackets_slot_clear = true,
            .clears_vtermno_slot = true,
            .clears_cons_ops_slot = true,
            .keeps_irq_until_hangup = true,
            .tty_port_put_requested = true,
            .tty_port_put_precedes_tty_vhangup = request.tty_attached,
            .console_unlock_precedes_tty_vhangup = request.tty_attached,
            .tty_vhangup_requested = request.tty_attached,
            .tty_kref_put_after_vhangup = request.tty_attached,
            .teardown_deferred_to_hangup = request.tty_attached,
        };
    }

    pub fn summarizeCleanupHandoff(
        self: *const Self,
        request: CleanupHandoffRequest,
    ) !CleanupHandoffSnapshot {
        const slot = self.slotSnapshot();
        if (!slot.usable_for_console) return error.ConsoleUnavailable;

        return .{
            .anchor = descriptor().anchor,
            .slot_index = slot.slot_index,
            .vtermno = slot.vtermno,
            .adapter_present = slot.adapter_present,
            .close_skipped = request.close_skipped,
            .final_close = request.final_close,
            .tty_port_put_requested = true,
            .drops_tty_port_reference = true,
            .defers_final_release_to_port_destruct = true,
            .keeps_console_binding = true,
        };
    }

    pub fn stageWrite(self: *const Self, input: []const u8, put_result: isize) !WriteSnapshot {
        if (!self.slotSnapshot().usable_for_console) return error.ConsoleUnavailable;

        var framed: [outbuf_capacity * 2]u8 = undefined;
        const framed_len = try frameConsoleWrite(input, &framed);

        var remaining: [outbuf_capacity * 2]u8 = undefined;
        @memset(&remaining, 0);

        const summary = summarizeFlushProgress(framed[0..framed_len], put_result, &remaining);

        return .{
            .anchor = descriptor().anchor,
            .slot_index = self.slot_index,
            .adapter_present = self.adapter_present,
            .framed_len = framed_len,
            .framed = framed,
            .remaining_len = summary.remaining_len,
            .remaining = remaining,
            .flush_intent = summary.flush_intent,
            .flush_progress = summary.flush_progress,
            .final_flush = true,
            .dropped_on_error = summary.dropped_on_error,
        };
    }
};

pub fn validateConsoleSlot(slot_index: usize) !void {
    if (slot_index >= max_nr_hvc_consoles) return error.InvalidConsoleSlot;
}

pub fn headerParitySnapshot() HeaderParitySnapshot {
    return .{
        .anchor = "drivers/tty/hvc/hvc_console.h",
        .max_nr_hvc_consoles = max_nr_hvc_consoles,
        .alloc_tty_adapters = alloc_tty_adapters,
        .exports_instantiate = true,
        .exports_alloc = true,
        .exports_remove = true,
        .exports_poll = true,
        .exports_resize = true,
        .exports_kick = true,
        .exports_notifier_add_irq = true,
        .exports_notifier_del_irq = true,
        .exports_notifier_hangup_irq = true,
        .hv_ops = .{
            .has_get_chars = true,
            .has_put_chars = true,
            .has_flush = true,
            .has_notifier_add = true,
            .has_notifier_del = true,
            .has_notifier_hangup = true,
            .has_tiocmget = true,
            .has_tiocmset = true,
            .has_dtr_rts = true,
        },
        .keeps_tty_registration_out_of_scope = true,
        .keeps_live_hypervisor_io_out_of_scope = true,
    };
}

const FlushProgressSummary = struct {
    remaining_len: usize,
    flush_intent: FlushIntent,
    flush_progress: FlushProgress,
    dropped_on_error: bool,
};

const PollWriteDrainSummary = struct {
    remaining_len: usize,
    do_wakeup: bool,
    progress_resets_timeout: bool,
    stalled_write_uses_min_timeout: bool,
};

fn summarizePollWriteDrain(
    buffered_write_len: usize,
    write_result: isize,
    preexisting_do_wakeup: bool,
) PollWriteDrainSummary {
    if (buffered_write_len == 0) {
        return .{
            .remaining_len = 0,
            .do_wakeup = preexisting_do_wakeup,
            .progress_resets_timeout = false,
            .stalled_write_uses_min_timeout = false,
        };
    }

    if (write_result <= 0) {
        if (write_result == 0 or write_result == eagain) {
            return .{
                .remaining_len = buffered_write_len,
                .do_wakeup = true,
                .progress_resets_timeout = false,
                .stalled_write_uses_min_timeout = true,
            };
        }

        return .{
            .remaining_len = 0,
            .do_wakeup = true,
            .progress_resets_timeout = false,
            .stalled_write_uses_min_timeout = false,
        };
    }

    const written = @min(@as(usize, @intCast(write_result)), buffered_write_len);
    const remaining_len = buffered_write_len - written;
    return .{
        .remaining_len = remaining_len,
        .do_wakeup = preexisting_do_wakeup or remaining_len == 0,
        .progress_resets_timeout = remaining_len > 0,
        .stalled_write_uses_min_timeout = false,
    };
}

fn summarizeFlushProgress(
    framed: []const u8,
    put_result: isize,
    remaining: *[outbuf_capacity * 2]u8,
) FlushProgressSummary {
    if (put_result <= 0) {
        if (put_result == 0 or put_result == eagain) {
            std.mem.copyForwards(u8, remaining[0..framed.len], framed);
            return .{
                .remaining_len = framed.len,
                .flush_intent = .retry_after_eagain,
                .flush_progress = .no_progress,
                .dropped_on_error = false,
            };
        }

        return .{
            .remaining_len = 0,
            .flush_intent = .none,
            .flush_progress = .dropped_on_error,
            .dropped_on_error = true,
        };
    }

    const written = @min(@as(usize, @intCast(put_result)), framed.len);
    const remaining_len = framed.len - written;
    if (remaining_len > 0) {
        std.mem.copyForwards(u8, remaining[0..remaining_len], framed[written..]);
    }

    return .{
        .remaining_len = remaining_len,
        .flush_intent = .final_drain,
        .flush_progress = if (remaining_len == 0) .fully_written else .partial_write,
        .dropped_on_error = false,
    };
}

fn frameConsoleWrite(input: []const u8, output: *[outbuf_capacity * 2]u8) !usize {
    if (input.len > outbuf_capacity) return error.InputTooLarge;

    var index: usize = 0;
    var previous_was_cr = false;

    for (input) |char| {
        if (char == '\n' and !previous_was_cr) {
            output[index] = '\r';
            index += 1;
        }

        output[index] = char;
        index += 1;
        previous_was_cr = char == '\r';
    }

    return index;
}

fn normalizeKhvcdTimeout(timeout_ms: u32) u32 {
    var normalized = timeout_ms;
    if (normalized < min_khvcd_timeout_ms) normalized = min_khvcd_timeout_ms;
    if (normalized > max_khvcd_timeout_ms) normalized = max_khvcd_timeout_ms;
    return normalized;
}

fn growKhvcdTimeout(timeout_ms: u32) u32 {
    const normalized = normalizeKhvcdTimeout(timeout_ms);
    const widened = normalized + (normalized >> 6) + 1;
    return if (widened > max_khvcd_timeout_ms) max_khvcd_timeout_ms else widened;
}
