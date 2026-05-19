const std = @import("std");

pub const MAX_NR_HVC_CONSOLES: u32 = 16;
pub const HVC_ALLOC_TTY_ADAPTERS: u32 = 0x01;

pub const Winsize = extern struct {
    ws_row: u16,
    ws_col: u16,
    ws_xpixel: u16,
    ws_ypixel: u16,
};

pub const HvcStruct = opaque {};

pub const HvOps = extern struct {
    get_chars: ?*const fn (u32, [*]u8, usize) callconv(.c) isize = null,
    put_chars: ?*const fn (u32, [*]const u8, usize) callconv(.c) isize = null,
    flush: ?*const fn (u32, bool) callconv(.c) c_int = null,
    notifier_add: ?*const fn (*HvcStruct, c_int) callconv(.c) c_int = null,
    notifier_del: ?*const fn (*HvcStruct, c_int) callconv(.c) void = null,
    notifier_hangup: ?*const fn (*HvcStruct, c_int) callconv(.c) void = null,
    tiocmget: ?*const fn (*HvcStruct) callconv(.c) c_int = null,
    tiocmset: ?*const fn (*HvcStruct, c_uint, c_uint) callconv(.c) c_int = null,
    dtr_rts: ?*const fn (*HvcStruct, bool) callconv(.c) void = null,
};

pub const CrLfWriteRequest = struct {
    payload_len: usize,
    newline_seen: bool,
    already_crlf: bool,
    can_sleep: bool,
};

pub const CrLfWriteSummary = struct {
    payload_len: usize,
    inserts_carriage_return: bool,
    preserves_existing_crlf: bool,
    can_sleep: bool,
};

pub fn summarizeCrLfWrite(request: CrLfWriteRequest) CrLfWriteSummary {
    return .{
        .payload_len = request.payload_len,
        .inserts_carriage_return = request.newline_seen and !request.already_crlf,
        .preserves_existing_crlf = request.already_crlf,
        .can_sleep = request.can_sleep,
    };
}

pub const FlushIntentRequest = struct {
    flush_callback_present: bool,
    buffered_write_pending: bool,
    close_wait_ownership: bool,
    final_close: bool,
};

pub const FlushIntentSummary = struct {
    flush_callback_present: bool,
    explicit_flush_intent: bool,
    close_wait_ownership: bool,
    final_close: bool,
};

pub fn summarizeFlushIntent(request: FlushIntentRequest) FlushIntentSummary {
    return .{
        .flush_callback_present = request.flush_callback_present,
        .explicit_flush_intent = request.flush_callback_present and (request.buffered_write_pending or request.final_close),
        .close_wait_ownership = request.close_wait_ownership,
        .final_close = request.final_close,
    };
}

pub const CloseTeardownRequest = struct {
    tty_detached: bool,
    hupcl: bool,
    notifier_owned: bool,
    resize_work_cancelled: bool,
    wait_until_sent_intent: bool,
    close_wait_ownership: bool,
    port_initialized_before_close: bool,
};

pub const CloseTeardownSummary = struct {
    tty_detached: bool,
    dtr_rts_shutdown: bool,
    notifier_del_owned: bool,
    resize_work_cancelled: bool,
    wait_until_sent_intent: bool,
    close_wait_ownership: bool,
    port_initialized_cleared: bool,
};

pub fn summarizeCloseTeardown(request: CloseTeardownRequest) CloseTeardownSummary {
    return .{
        .tty_detached = request.tty_detached,
        .dtr_rts_shutdown = request.hupcl,
        .notifier_del_owned = request.notifier_owned,
        .resize_work_cancelled = request.resize_work_cancelled,
        .wait_until_sent_intent = request.wait_until_sent_intent,
        .close_wait_ownership = request.close_wait_ownership,
        .port_initialized_cleared = request.port_initialized_before_close,
    };
}

pub const TtyRegistrationRequest = struct {
    tty_driver_allocated: bool,
    tty_operations_registered: bool,
    tty_port_linked: bool,
    open_time_irq_request_ready: bool,
    wakeup_after_registration: bool,
};

pub const TtyRegistrationSummary = struct {
    tty_driver_allocated: bool,
    tty_operations_registered: bool,
    tty_port_linked: bool,
    open_time_irq_request_ready: bool,
    wakeup_after_registration: bool,
};

pub fn summarizeTtyRegistrationHandoff(request: TtyRegistrationRequest) TtyRegistrationSummary {
    return .{
        .tty_driver_allocated = request.tty_driver_allocated,
        .tty_operations_registered = request.tty_operations_registered,
        .tty_port_linked = request.tty_port_linked,
        .open_time_irq_request_ready = request.open_time_irq_request_ready,
        .wakeup_after_registration = request.wakeup_after_registration,
    };
}

pub const AllocSlotSelection = enum {
    matched_console_slot,
    empty_console_slot,
    hotplug_extension,
};

pub const AllocSlotRequest = struct {
    matched_registered_console: bool,
    empty_console_slot_available: bool,
    hvc_struct_list_linked: bool,
    rechecks_kernel_console: bool,
};

pub const AllocSlotSummary = struct {
    selection: AllocSlotSelection,
    claims_console_slot: bool,
    hvc_struct_list_linked: bool,
    rechecks_kernel_console: bool,
};

pub fn summarizeAllocSlotHandoff(request: AllocSlotRequest) AllocSlotSummary {
    const selection: AllocSlotSelection = if (request.matched_registered_console)
        .matched_console_slot
    else if (request.empty_console_slot_available)
        .empty_console_slot
    else
        .hotplug_extension;

    return .{
        .selection = selection,
        .claims_console_slot = selection != .hotplug_extension,
        .hvc_struct_list_linked = request.hvc_struct_list_linked,
        .rechecks_kernel_console = request.rechecks_kernel_console,
    };
}

pub const ResizeHandoffRequest = struct {
    tty_present: bool,
    winsize: Winsize,
    keeps_live_resize_execution_out_of_scope: bool = true,
};

pub const ResizeHandoffSummary = struct {
    tty_present: bool,
    geometry_visible: bool,
    keeps_live_resize_execution_out_of_scope: bool,
};

pub fn summarizeResizeHandoff(request: ResizeHandoffRequest) ResizeHandoffSummary {
    const geometry_visible =
        request.winsize.ws_row != 0 or
        request.winsize.ws_col != 0 or
        request.winsize.ws_xpixel != 0 or
        request.winsize.ws_ypixel != 0;

    return .{
        .tty_present = request.tty_present,
        .geometry_visible = geometry_visible,
        .keeps_live_resize_execution_out_of_scope = request.keeps_live_resize_execution_out_of_scope,
    };
}

pub const NotifierAddRequest = struct {
    notifier_add_success: bool,
    polling_fallback: bool,
    failed_open_close_cleanup: bool,
    open_time_irq_request: bool,
    kick_after_open: bool,
};

pub const NotifierAddSummary = struct {
    notifier_add_success: bool,
    polling_fallback: bool,
    failed_open_close_cleanup: bool,
    open_time_irq_request_boundaries: bool,
    khvcd_kick_follow_through: bool,
};

pub fn summarizeNotifierAddOutcome(request: NotifierAddRequest) NotifierAddSummary {
    return .{
        .notifier_add_success = request.notifier_add_success,
        .polling_fallback = request.polling_fallback or !request.notifier_add_success,
        .failed_open_close_cleanup = request.failed_open_close_cleanup and !request.notifier_add_success,
        .open_time_irq_request_boundaries = request.open_time_irq_request,
        .khvcd_kick_follow_through = request.kick_after_open,
    };
}

pub const KhvcdPollingContractRequest = struct {
    final_close_wait_carryover: bool,
    notifier_driven_wakeup: bool,
    polling_driven_wakeup: bool,
    khvcd_polling_visible: bool,
    bounded_reschedule_intent: bool,
    teardown_host_io_pressure: bool,
};

pub const KhvcdPollingContractSummary = struct {
    final_close_wait_carryover: bool,
    notifier_driven_wakeup: bool,
    polling_driven_wakeup: bool,
    khvcd_polling_visible: bool,
    bounded_reschedule_intent: bool,
    teardown_host_io_pressure: bool,
};

pub fn summarizeKhvcdPollingContract(request: KhvcdPollingContractRequest) KhvcdPollingContractSummary {
    return .{
        .final_close_wait_carryover = request.final_close_wait_carryover,
        .notifier_driven_wakeup = request.notifier_driven_wakeup,
        .polling_driven_wakeup = request.polling_driven_wakeup,
        .khvcd_polling_visible = request.khvcd_polling_visible,
        .bounded_reschedule_intent = request.bounded_reschedule_intent,
        .teardown_host_io_pressure = request.teardown_host_io_pressure,
    };
}

pub const KhvcdWorkerEntryRequest = struct {
    initial_poll_attempt: bool,
    wakeup_kick_ready: bool,
    sleep_handoff_ready: bool,
};

pub const KhvcdWorkerEntrySummary = struct {
    initial_poll_attempt: bool,
    wakeup_kick_ready: bool,
    sleep_handoff_ready: bool,
};

pub fn summarizeKhvcdWorkerEntry(request: KhvcdWorkerEntryRequest) KhvcdWorkerEntrySummary {
    return .{
        .initial_poll_attempt = request.initial_poll_attempt,
        .wakeup_kick_ready = request.wakeup_kick_ready,
        .sleep_handoff_ready = request.sleep_handoff_ready,
    };
}

pub const KhvcdSleepRequest = struct {
    pre_sleep_kick_check: bool,
    interruptible_state_recheck: bool,
    guard_tick_timed_sleep: bool,
};

pub const KhvcdSleepSummary = struct {
    pre_sleep_kick_check: bool,
    interruptible_state_recheck: bool,
    guard_tick_timed_sleep: bool,
};

pub fn summarizeKhvcdSleepHandoff(request: KhvcdSleepRequest) KhvcdSleepSummary {
    return .{
        .pre_sleep_kick_check = request.pre_sleep_kick_check,
        .interruptible_state_recheck = request.interruptible_state_recheck,
        .guard_tick_timed_sleep = request.guard_tick_timed_sleep,
    };
}

pub const PollDrainOrderRequest = struct {
    irq_backed_drained_reads: bool,
    partial_write_progress: bool,
    stalled_retry_path: bool,
    pending_sysrq_dispatch_separate: bool,
    tty_wakeup_pending: bool,
    read_activity_detected: bool,
};

pub const PollDrainOrderSummary = struct {
    irq_backed_drained_reads: bool,
    partial_write_progress: bool,
    stalled_retry_path: bool,
    pending_sysrq_dispatch_separate: bool,
    tty_wakeup_precedes_flip_push: bool,
    read_activity_resets_timeout: bool,
};

pub fn summarizePollDrainOrder(request: PollDrainOrderRequest) PollDrainOrderSummary {
    return .{
        .irq_backed_drained_reads = request.irq_backed_drained_reads,
        .partial_write_progress = request.partial_write_progress,
        .stalled_retry_path = request.stalled_retry_path,
        .pending_sysrq_dispatch_separate = request.pending_sysrq_dispatch_separate,
        .tty_wakeup_precedes_flip_push = request.tty_wakeup_pending and request.read_activity_detected,
        .read_activity_resets_timeout = request.read_activity_detected,
    };
}

pub const HangupDisconnectRequest = struct {
    tty_resize_cancelled: bool,
    stale_count_short_circuit: bool,
    buffered_write_cleared: bool,
    notifier_hangup_boundary: bool,
};

pub const HangupDisconnectSummary = struct {
    tty_resize_cancelled: bool,
    stale_count_short_circuit: bool,
    buffered_write_cleared: bool,
    notifier_hangup_boundary: bool,
};

pub fn summarizeHangupDisconnect(request: HangupDisconnectRequest) HangupDisconnectSummary {
    const stale_count_short_circuit = request.stale_count_short_circuit;

    return .{
        .tty_resize_cancelled = request.tty_resize_cancelled,
        .stale_count_short_circuit = stale_count_short_circuit,
        .buffered_write_cleared = request.buffered_write_cleared and !stale_count_short_circuit,
        .notifier_hangup_boundary = request.notifier_hangup_boundary and !stale_count_short_circuit,
    };
}

pub const RemoveHandoffRequest = struct {
    console_lock_slot_cleared: bool,
    vtermno_and_cons_ops_released: bool,
    tty_port_put_ordered: bool,
    tty_vhangup_follow_through: bool,
    tty_kref_put_release: bool,
    keep_irq_until_hangup: bool,
};

pub const RemoveHandoffSummary = struct {
    console_lock_slot_cleared: bool,
    vtermno_and_cons_ops_released: bool,
    slot_release_ownership: bool,
    tty_port_put_ordered: bool,
    tty_vhangup_follow_through: bool,
    tty_kref_put_release: bool,
    keep_irq_until_hangup: bool,
};

pub fn summarizeRemoveHandoff(request: RemoveHandoffRequest) RemoveHandoffSummary {
    return .{
        .console_lock_slot_cleared = request.console_lock_slot_cleared,
        .vtermno_and_cons_ops_released = request.vtermno_and_cons_ops_released,
        .slot_release_ownership = request.console_lock_slot_cleared and request.vtermno_and_cons_ops_released,
        .tty_port_put_ordered = request.tty_port_put_ordered,
        .tty_vhangup_follow_through = request.tty_vhangup_follow_through,
        .tty_kref_put_release = request.tty_kref_put_release,
        .keep_irq_until_hangup = request.keep_irq_until_hangup,
    };
}

pub const CleanupHandoffRequest = struct {
    tty_port_release_handoff: bool,
    cleanup_time_tty_port_ownership: bool,
    port_reference_drop_timing: bool,
};

pub const CleanupHandoffSummary = struct {
    tty_port_release_handoff: bool,
    cleanup_time_tty_port_ownership: bool,
    port_reference_drop_timing: bool,
};

pub fn summarizeCleanupHandoff(request: CleanupHandoffRequest) CleanupHandoffSummary {
    return .{
        .tty_port_release_handoff = request.tty_port_release_handoff,
        .cleanup_time_tty_port_ownership = request.cleanup_time_tty_port_ownership,
        .port_reference_drop_timing = request.port_reference_drop_timing,
    };
}

pub const TargetlessNotifierEdgeRequest = struct {
    target_present: bool,
    notifier_registered: bool,
    unregister_requested: bool,
    keeps_live_notifier_execution_out_of_scope: bool = true,
};

pub const TargetlessNotifierEdgeSummary = struct {
    target_present: bool,
    notifier_registered: bool,
    targetless_no_unregister_edge: bool,
    unregister_requested: bool,
    keeps_live_notifier_execution_out_of_scope: bool,
};

pub fn summarizeTargetlessNotifierEdge(request: TargetlessNotifierEdgeRequest) TargetlessNotifierEdgeSummary {
    return .{
        .target_present = request.target_present,
        .notifier_registered = request.notifier_registered,
        .targetless_no_unregister_edge = request.notifier_registered and !request.target_present and !request.unregister_requested,
        .unregister_requested = request.unregister_requested and request.target_present and request.notifier_registered,
        .keeps_live_notifier_execution_out_of_scope = request.keeps_live_notifier_execution_out_of_scope,
    };
}

pub const KickWakeupCueRequest = struct {
    registration_handoff_visible: bool,
    notifier_add_handoff_visible: bool,
    khvcd_polling_contract_visible: bool,
    keeps_live_khvcd_execution_out_of_scope: bool = true,
};

pub const KickWakeupCueSummary = struct {
    registration_handoff_visible: bool,
    notifier_add_handoff_visible: bool,
    khvcd_polling_contract_visible: bool,
    keeps_live_khvcd_execution_out_of_scope: bool,
};

pub fn summarizeKickWakeupCue(request: KickWakeupCueRequest) KickWakeupCueSummary {
    return .{
        .registration_handoff_visible = request.registration_handoff_visible,
        .notifier_add_handoff_visible = request.notifier_add_handoff_visible,
        .khvcd_polling_contract_visible = request.khvcd_polling_contract_visible,
        .keeps_live_khvcd_execution_out_of_scope = request.keeps_live_khvcd_execution_out_of_scope,
    };
}

pub const NotifierIrqHelperRequest = struct {
    irq: c_int,
    notifier_registered: bool,
    target_present: bool,
    hangup_requested: bool,
    keeps_live_notifier_execution_out_of_scope: bool = true,
};

pub const NotifierIrqHelperSummary = struct {
    irq_valid: bool,
    add_result: c_int,
    del_surface_visible: bool,
    hangup_surface_visible: bool,
    targetless_hangup_short_circuit: bool,
    keeps_live_notifier_execution_out_of_scope: bool,
};

pub fn summarizeNotifierIrqHelper(request: NotifierIrqHelperRequest) NotifierIrqHelperSummary {
    const irq_valid = request.irq >= 0;
    const targetless_hangup_short_circuit = request.notifier_registered and
        !request.target_present and
        request.hangup_requested;

    return .{
        .irq_valid = irq_valid,
        .add_result = if (irq_valid) 0 else -1,
        .del_surface_visible = request.notifier_registered,
        .hangup_surface_visible = request.notifier_registered and
            request.target_present and
            request.hangup_requested,
        .targetless_hangup_short_circuit = targetless_hangup_short_circuit,
        .keeps_live_notifier_execution_out_of_scope = request.keeps_live_notifier_execution_out_of_scope,
    };
}

pub const ModemControlRequest = struct {
    tiocmget_available: bool,
    tiocmset_available: bool,
    dtr_rts_available: bool,
    set_mask_requested: bool,
    clear_mask_requested: bool,
    dtr_rts_asserted: bool,
    keeps_live_modem_control_execution_out_of_scope: bool = true,
};

pub const ModemControlSummary = struct {
    get_surface_visible: bool,
    set_surface_visible: bool,
    dtr_rts_surface_visible: bool,
    set_mask_requested: bool,
    clear_mask_requested: bool,
    dtr_rts_asserted: bool,
    keeps_live_modem_control_execution_out_of_scope: bool,
};

pub fn summarizeModemControlHandoff(request: ModemControlRequest) ModemControlSummary {
    return .{
        .get_surface_visible = request.tiocmget_available,
        .set_surface_visible = request.tiocmset_available and (request.set_mask_requested or request.clear_mask_requested),
        .dtr_rts_surface_visible = request.dtr_rts_available,
        .set_mask_requested = request.set_mask_requested and request.tiocmset_available,
        .clear_mask_requested = request.clear_mask_requested and request.tiocmset_available,
        .dtr_rts_asserted = request.dtr_rts_available and request.dtr_rts_asserted,
        .keeps_live_modem_control_execution_out_of_scope = request.keeps_live_modem_control_execution_out_of_scope,
    };
}

pub fn hvc_kick() void {}

pub fn __hvc_resize(hp: *HvcStruct, ws: Winsize) void {
    _ = hp;
    _ = ws;
}

pub fn notifier_add_irq(hp: *HvcStruct, irq: c_int) c_int {
    _ = hp;
    return summarizeNotifierIrqHelper(.{
        .irq = irq,
        .notifier_registered = false,
        .target_present = false,
        .hangup_requested = false,
    }).add_result;
}

pub fn notifier_del_irq(hp: *HvcStruct, irq: c_int) void {
    _ = hp;
    _ = irq;
}

pub fn notifier_hangup_irq(hp: *HvcStruct, irq: c_int) void {
    _ = hp;
    _ = irq;
}

test "phase11 hvc console keeps CRLF framing summary reviewable" {
    const summary = summarizeCrLfWrite(.{
        .payload_len = 4,
        .newline_seen = true,
        .already_crlf = false,
        .can_sleep = true,
    });

    try std.testing.expectEqual(@as(usize, 4), summary.payload_len);
    try std.testing.expect(summary.inserts_carriage_return);
    try std.testing.expect(!summary.preserves_existing_crlf);
    try std.testing.expect(summary.can_sleep);
}

test "phase11 hvc console keeps flush intent summary reviewable" {
    const summary = summarizeFlushIntent(.{
        .flush_callback_present = true,
        .buffered_write_pending = true,
        .close_wait_ownership = true,
        .final_close = true,
    });

    try std.testing.expect(summary.flush_callback_present);
    try std.testing.expect(summary.explicit_flush_intent);
    try std.testing.expect(summary.close_wait_ownership);
    try std.testing.expect(summary.final_close);
}

test "phase11 hvc console keeps final-close teardown ownership summary reviewable" {
    const summary = summarizeCloseTeardown(.{
        .tty_detached = true,
        .hupcl = true,
        .notifier_owned = true,
        .resize_work_cancelled = true,
        .wait_until_sent_intent = true,
        .close_wait_ownership = true,
        .port_initialized_before_close = true,
    });

    try std.testing.expect(summary.tty_detached);
    try std.testing.expect(summary.dtr_rts_shutdown);
    try std.testing.expect(summary.notifier_del_owned);
    try std.testing.expect(summary.resize_work_cancelled);
    try std.testing.expect(summary.wait_until_sent_intent);
    try std.testing.expect(summary.close_wait_ownership);
    try std.testing.expect(summary.port_initialized_cleared);
}

test "phase11 hvc console keeps tty-registration handoff summary reviewable" {
    const summary = summarizeTtyRegistrationHandoff(.{
        .tty_driver_allocated = true,
        .tty_operations_registered = true,
        .tty_port_linked = true,
        .open_time_irq_request_ready = true,
        .wakeup_after_registration = true,
    });

    try std.testing.expect(summary.tty_driver_allocated);
    try std.testing.expect(summary.tty_operations_registered);
    try std.testing.expect(summary.tty_port_linked);
    try std.testing.expect(summary.open_time_irq_request_ready);
    try std.testing.expect(summary.wakeup_after_registration);
}

test "phase11 hvc console keeps hvc_alloc slot-match handoff reviewable" {
    const summary = summarizeAllocSlotHandoff(.{
        .matched_registered_console = true,
        .empty_console_slot_available = true,
        .hvc_struct_list_linked = true,
        .rechecks_kernel_console = true,
    });

    try std.testing.expectEqual(AllocSlotSelection.matched_console_slot, summary.selection);
    try std.testing.expect(summary.claims_console_slot);
    try std.testing.expect(summary.hvc_struct_list_linked);
    try std.testing.expect(summary.rechecks_kernel_console);
}

test "phase11 hvc console keeps hvc_alloc empty-slot fallback reviewable" {
    const summary = summarizeAllocSlotHandoff(.{
        .matched_registered_console = false,
        .empty_console_slot_available = true,
        .hvc_struct_list_linked = true,
        .rechecks_kernel_console = true,
    });

    try std.testing.expectEqual(AllocSlotSelection.empty_console_slot, summary.selection);
    try std.testing.expect(summary.claims_console_slot);
    try std.testing.expect(summary.hvc_struct_list_linked);
    try std.testing.expect(summary.rechecks_kernel_console);
}

test "phase11 hvc console keeps hvc_alloc hotplug extension distinct from console slot claims" {
    const summary = summarizeAllocSlotHandoff(.{
        .matched_registered_console = false,
        .empty_console_slot_available = false,
        .hvc_struct_list_linked = true,
        .rechecks_kernel_console = true,
    });

    try std.testing.expectEqual(AllocSlotSelection.hotplug_extension, summary.selection);
    try std.testing.expect(!summary.claims_console_slot);
    try std.testing.expect(summary.hvc_struct_list_linked);
    try std.testing.expect(summary.rechecks_kernel_console);
}

test "phase11 hvc console keeps resize handoff summary reviewable" {
    const summary = summarizeResizeHandoff(.{
        .tty_present = true,
        .winsize = .{
            .ws_row = 40,
            .ws_col = 120,
            .ws_xpixel = 800,
            .ws_ypixel = 600,
        },
    });
    const fake_hp: *HvcStruct = @ptrFromInt(1);

    try std.testing.expect(summary.tty_present);
    try std.testing.expect(summary.geometry_visible);
    try std.testing.expect(summary.keeps_live_resize_execution_out_of_scope);

    __hvc_resize(fake_hp, .{
        .ws_row = 25,
        .ws_col = 80,
        .ws_xpixel = 0,
        .ws_ypixel = 0,
    });
}

test "phase11 hvc console keeps zeroed resize geometry explicit" {
    const summary = summarizeResizeHandoff(.{
        .tty_present = false,
        .winsize = .{
            .ws_row = 0,
            .ws_col = 0,
            .ws_xpixel = 0,
            .ws_ypixel = 0,
        },
    });

    try std.testing.expect(!summary.tty_present);
    try std.testing.expect(!summary.geometry_visible);
    try std.testing.expect(summary.keeps_live_resize_execution_out_of_scope);
}

test "phase11 hvc console keeps notifier-add open handoff summary reviewable" {
    const summary = summarizeNotifierAddOutcome(.{
        .notifier_add_success = false,
        .polling_fallback = false,
        .failed_open_close_cleanup = true,
        .open_time_irq_request = true,
        .kick_after_open = false,
    });

    try std.testing.expect(!summary.notifier_add_success);
    try std.testing.expect(summary.polling_fallback);
    try std.testing.expect(summary.failed_open_close_cleanup);
    try std.testing.expect(summary.open_time_irq_request_boundaries);
    try std.testing.expect(!summary.khvcd_kick_follow_through);
}

test "phase11 hvc console keeps khvcd polling-contract summary reviewable" {
    const summary = summarizeKhvcdPollingContract(.{
        .final_close_wait_carryover = true,
        .notifier_driven_wakeup = true,
        .polling_driven_wakeup = false,
        .khvcd_polling_visible = true,
        .bounded_reschedule_intent = true,
        .teardown_host_io_pressure = false,
    });

    try std.testing.expect(summary.final_close_wait_carryover);
    try std.testing.expect(summary.notifier_driven_wakeup);
    try std.testing.expect(!summary.polling_driven_wakeup);
    try std.testing.expect(summary.khvcd_polling_visible);
    try std.testing.expect(summary.bounded_reschedule_intent);
    try std.testing.expect(!summary.teardown_host_io_pressure);
}

test "phase11 hvc console keeps khvcd worker-entry handoff reviewable" {
    const summary = summarizeKhvcdWorkerEntry(.{
        .initial_poll_attempt = true,
        .wakeup_kick_ready = true,
        .sleep_handoff_ready = true,
    });

    try std.testing.expect(summary.initial_poll_attempt);
    try std.testing.expect(summary.wakeup_kick_ready);
    try std.testing.expect(summary.sleep_handoff_ready);
}

test "phase11 hvc console keeps khvcd sleep-and-reschedule handoff reviewable" {
    const summary = summarizeKhvcdSleepHandoff(.{
        .pre_sleep_kick_check = true,
        .interruptible_state_recheck = true,
        .guard_tick_timed_sleep = true,
    });

    try std.testing.expect(summary.pre_sleep_kick_check);
    try std.testing.expect(summary.interruptible_state_recheck);
    try std.testing.expect(summary.guard_tick_timed_sleep);
}

test "phase11 hvc console keeps __hvc_poll drain-order summary reviewable" {
    const summary = summarizePollDrainOrder(.{
        .irq_backed_drained_reads = true,
        .partial_write_progress = true,
        .stalled_retry_path = false,
        .pending_sysrq_dispatch_separate = true,
        .tty_wakeup_pending = true,
        .read_activity_detected = true,
    });

    try std.testing.expect(summary.irq_backed_drained_reads);
    try std.testing.expect(summary.partial_write_progress);
    try std.testing.expect(!summary.stalled_retry_path);
    try std.testing.expect(summary.pending_sysrq_dispatch_separate);
    try std.testing.expect(summary.tty_wakeup_precedes_flip_push);
    try std.testing.expect(summary.read_activity_resets_timeout);
}

test "phase11 hvc console keeps wakeup-only poll retries distinct from read-driven timeout reset" {
    const summary = summarizePollDrainOrder(.{
        .irq_backed_drained_reads = false,
        .partial_write_progress = false,
        .stalled_retry_path = true,
        .pending_sysrq_dispatch_separate = false,
        .tty_wakeup_pending = true,
        .read_activity_detected = false,
    });

    try std.testing.expect(!summary.irq_backed_drained_reads);
    try std.testing.expect(!summary.partial_write_progress);
    try std.testing.expect(summary.stalled_retry_path);
    try std.testing.expect(!summary.pending_sysrq_dispatch_separate);
    try std.testing.expect(!summary.tty_wakeup_precedes_flip_push);
    try std.testing.expect(!summary.read_activity_resets_timeout);
}

test "phase11 hvc console keeps active hangup and cleanup ownership handoffs reviewable" {
    const hangup = summarizeHangupDisconnect(.{
        .tty_resize_cancelled = true,
        .stale_count_short_circuit = false,
        .buffered_write_cleared = true,
        .notifier_hangup_boundary = true,
    });
    const cleanup = summarizeCleanupHandoff(.{
        .tty_port_release_handoff = true,
        .cleanup_time_tty_port_ownership = true,
        .port_reference_drop_timing = true,
    });

    try std.testing.expect(hangup.tty_resize_cancelled);
    try std.testing.expect(!hangup.stale_count_short_circuit);
    try std.testing.expect(hangup.buffered_write_cleared);
    try std.testing.expect(hangup.notifier_hangup_boundary);
    try std.testing.expect(cleanup.tty_port_release_handoff);
    try std.testing.expect(cleanup.cleanup_time_tty_port_ownership);
    try std.testing.expect(cleanup.port_reference_drop_timing);
}

test "phase11 hvc console keeps stale hangup short-circuit ownership reviewable" {
    const hangup = summarizeHangupDisconnect(.{
        .tty_resize_cancelled = true,
        .stale_count_short_circuit = true,
        .buffered_write_cleared = true,
        .notifier_hangup_boundary = true,
    });

    try std.testing.expect(hangup.tty_resize_cancelled);
    try std.testing.expect(hangup.stale_count_short_circuit);
    try std.testing.expect(!hangup.buffered_write_cleared);
    try std.testing.expect(!hangup.notifier_hangup_boundary);
}

test "phase11 hvc console keeps remove handoff summary reviewable" {
    const summary = summarizeRemoveHandoff(.{
        .console_lock_slot_cleared = true,
        .vtermno_and_cons_ops_released = true,
        .tty_port_put_ordered = true,
        .tty_vhangup_follow_through = true,
        .tty_kref_put_release = true,
        .keep_irq_until_hangup = true,
    });

    try std.testing.expect(summary.console_lock_slot_cleared);
    try std.testing.expect(summary.vtermno_and_cons_ops_released);
    try std.testing.expect(summary.slot_release_ownership);
    try std.testing.expect(summary.tty_port_put_ordered);
    try std.testing.expect(summary.tty_vhangup_follow_through);
    try std.testing.expect(summary.tty_kref_put_release);
    try std.testing.expect(summary.keep_irq_until_hangup);
}

test "phase11 hvc console keeps incomplete remove ownership out of handoff summary" {
    const summary = summarizeRemoveHandoff(.{
        .console_lock_slot_cleared = true,
        .vtermno_and_cons_ops_released = false,
        .tty_port_put_ordered = true,
        .tty_vhangup_follow_through = false,
        .tty_kref_put_release = false,
        .keep_irq_until_hangup = true,
    });

    try std.testing.expect(summary.console_lock_slot_cleared);
    try std.testing.expect(!summary.vtermno_and_cons_ops_released);
    try std.testing.expect(!summary.slot_release_ownership);
    try std.testing.expect(summary.tty_port_put_ordered);
    try std.testing.expect(!summary.tty_vhangup_follow_through);
    try std.testing.expect(!summary.tty_kref_put_release);
    try std.testing.expect(summary.keep_irq_until_hangup);
}

test "phase11 hvc console keeps targetless notifier no-unregister edge reviewable" {
    const targetless = summarizeTargetlessNotifierEdge(.{
        .target_present = false,
        .notifier_registered = true,
        .unregister_requested = false,
    });
    const targeted = summarizeTargetlessNotifierEdge(.{
        .target_present = true,
        .notifier_registered = true,
        .unregister_requested = true,
    });

    try std.testing.expect(!targetless.target_present);
    try std.testing.expect(targetless.notifier_registered);
    try std.testing.expect(targetless.targetless_no_unregister_edge);
    try std.testing.expect(!targetless.unregister_requested);
    try std.testing.expect(targetless.keeps_live_notifier_execution_out_of_scope);

    try std.testing.expect(targeted.target_present);
    try std.testing.expect(targeted.notifier_registered);
    try std.testing.expect(!targeted.targetless_no_unregister_edge);
    try std.testing.expect(targeted.unregister_requested);
    try std.testing.expect(targeted.keeps_live_notifier_execution_out_of_scope);
}

test "phase11 hvc console keeps unregistered targeted notifier-unregister request sanitized" {
    const summary = summarizeTargetlessNotifierEdge(.{
        .target_present = true,
        .notifier_registered = false,
        .unregister_requested = true,
    });

    try std.testing.expect(summary.target_present);
    try std.testing.expect(!summary.notifier_registered);
    try std.testing.expect(!summary.targetless_no_unregister_edge);
    try std.testing.expect(!summary.unregister_requested);
    try std.testing.expect(summary.keeps_live_notifier_execution_out_of_scope);
}

test "phase11 hvc console keeps hvc_kick wakeup cue reviewable" {
    const summary = summarizeKickWakeupCue(.{
        .registration_handoff_visible = true,
        .notifier_add_handoff_visible = true,
        .khvcd_polling_contract_visible = true,
    });

    try std.testing.expect(summary.registration_handoff_visible);
    try std.testing.expect(summary.notifier_add_handoff_visible);
    try std.testing.expect(summary.khvcd_polling_contract_visible);
    try std.testing.expect(summary.keeps_live_khvcd_execution_out_of_scope);

    hvc_kick();
}

test "phase11 hvc console keeps notifier irq helper surface reviewable" {
    const active = summarizeNotifierIrqHelper(.{
        .irq = 3,
        .notifier_registered = true,
        .target_present = true,
        .hangup_requested = true,
    });
    const targetless = summarizeNotifierIrqHelper(.{
        .irq = 7,
        .notifier_registered = true,
        .target_present = false,
        .hangup_requested = true,
    });
    const invalid = summarizeNotifierIrqHelper(.{
        .irq = -1,
        .notifier_registered = false,
        .target_present = false,
        .hangup_requested = false,
    });
    const fake_hp: *HvcStruct = @ptrFromInt(1);

    try std.testing.expect(active.irq_valid);
    try std.testing.expectEqual(@as(c_int, 0), active.add_result);
    try std.testing.expect(active.del_surface_visible);
    try std.testing.expect(active.hangup_surface_visible);
    try std.testing.expect(!active.targetless_hangup_short_circuit);
    try std.testing.expect(active.keeps_live_notifier_execution_out_of_scope);

    try std.testing.expect(targetless.irq_valid);
    try std.testing.expectEqual(@as(c_int, 0), targetless.add_result);
    try std.testing.expect(targetless.del_surface_visible);
    try std.testing.expect(!targetless.hangup_surface_visible);
    try std.testing.expect(targetless.targetless_hangup_short_circuit);
    try std.testing.expect(targetless.keeps_live_notifier_execution_out_of_scope);

    try std.testing.expect(!invalid.irq_valid);
    try std.testing.expectEqual(@as(c_int, -1), invalid.add_result);
    try std.testing.expect(!invalid.del_surface_visible);
    try std.testing.expect(!invalid.hangup_surface_visible);
    try std.testing.expect(!invalid.targetless_hangup_short_circuit);
    try std.testing.expect(invalid.keeps_live_notifier_execution_out_of_scope);

    try std.testing.expectEqual(active.add_result, notifier_add_irq(fake_hp, 3));
    try std.testing.expectEqual(invalid.add_result, notifier_add_irq(fake_hp, -1));

    notifier_del_irq(fake_hp, 7);
    notifier_hangup_irq(fake_hp, 9);
}

test "phase11 hvc console keeps modem-control helper surface reviewable" {
    const active = summarizeModemControlHandoff(.{
        .tiocmget_available = true,
        .tiocmset_available = true,
        .dtr_rts_available = true,
        .set_mask_requested = true,
        .clear_mask_requested = true,
        .dtr_rts_asserted = true,
    });
    const read_only = summarizeModemControlHandoff(.{
        .tiocmget_available = true,
        .tiocmset_available = false,
        .dtr_rts_available = false,
        .set_mask_requested = true,
        .clear_mask_requested = false,
        .dtr_rts_asserted = true,
    });

    try std.testing.expect(active.get_surface_visible);
    try std.testing.expect(active.set_surface_visible);
    try std.testing.expect(active.dtr_rts_surface_visible);
    try std.testing.expect(active.set_mask_requested);
    try std.testing.expect(active.clear_mask_requested);
    try std.testing.expect(active.dtr_rts_asserted);
    try std.testing.expect(active.keeps_live_modem_control_execution_out_of_scope);

    try std.testing.expect(read_only.get_surface_visible);
    try std.testing.expect(!read_only.set_surface_visible);
    try std.testing.expect(!read_only.dtr_rts_surface_visible);
    try std.testing.expect(!read_only.set_mask_requested);
    try std.testing.expect(!read_only.clear_mask_requested);
    try std.testing.expect(!read_only.dtr_rts_asserted);
    try std.testing.expect(read_only.keeps_live_modem_control_execution_out_of_scope);
}
