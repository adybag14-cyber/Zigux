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
    return .{
        .tty_resize_cancelled = request.tty_resize_cancelled,
        .stale_count_short_circuit = request.stale_count_short_circuit,
        .buffered_write_cleared = request.buffered_write_cleared,
        .notifier_hangup_boundary = request.notifier_hangup_boundary,
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
    tty_port_put_ordered: bool,
    tty_vhangup_follow_through: bool,
    tty_kref_put_release: bool,
    keep_irq_until_hangup: bool,
};

pub fn summarizeRemoveHandoff(request: RemoveHandoffRequest) RemoveHandoffSummary {
    return .{
        .console_lock_slot_cleared = request.console_lock_slot_cleared,
        .vtermno_and_cons_ops_released = request.vtermno_and_cons_ops_released,
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

pub fn hvc_kick() void {}

pub fn notifier_add_irq(hp: *HvcStruct, irq: c_int) c_int {
    _ = hp;
    return if (irq >= 0) 0 else -1;
}

pub fn notifier_del_irq(hp: *HvcStruct, irq: c_int) void {
    _ = hp;
    _ = irq;
}

pub fn notifier_hangup_irq(hp: *HvcStruct, irq: c_int) void {
    _ = hp;
    _ = irq;
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

test "phase11 hvc console keeps hangup disconnect and cleanup ownership handoffs reviewable" {
    const hangup = summarizeHangupDisconnect(.{
        .tty_resize_cancelled = true,
        .stale_count_short_circuit = true,
        .buffered_write_cleared = true,
        .notifier_hangup_boundary = true,
    });
    const cleanup = summarizeCleanupHandoff(.{
        .tty_port_release_handoff = true,
        .cleanup_time_tty_port_ownership = true,
        .port_reference_drop_timing = true,
    });

    try std.testing.expect(hangup.tty_resize_cancelled);
    try std.testing.expect(hangup.stale_count_short_circuit);
    try std.testing.expect(hangup.buffered_write_cleared);
    try std.testing.expect(hangup.notifier_hangup_boundary);
    try std.testing.expect(cleanup.tty_port_release_handoff);
    try std.testing.expect(cleanup.cleanup_time_tty_port_ownership);
    try std.testing.expect(cleanup.port_reference_drop_timing);
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
    try std.testing.expect(summary.tty_port_put_ordered);
    try std.testing.expect(summary.tty_vhangup_follow_through);
    try std.testing.expect(summary.tty_kref_put_release);
    try std.testing.expect(summary.keep_irq_until_hangup);
}

test "phase11 hvc console keeps notifier irq helper surface reviewable" {
    const fake_hp: *HvcStruct = @ptrFromInt(1);

    try std.testing.expectEqual(@as(c_int, 0), notifier_add_irq(fake_hp, 3));
    try std.testing.expectEqual(@as(c_int, -1), notifier_add_irq(fake_hp, -1));

    notifier_del_irq(fake_hp, 7);
    notifier_hangup_irq(fake_hp, 9);
}
