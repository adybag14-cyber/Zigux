const std = @import("std");
const hvc_console = @import("../../drivers/tty/hvc/hvc_console.zig");
const hvc_console_sysrq = @import("../../drivers/tty/hvc/hvc_console_sysrq.zig");

test "phase11 hvc console keeps irq-backed drained reads distinct when __hvc_poll can or cannot sleep" {
    const can_sleep = hvc_console.summarizeKhvcdSleepHandoff(.{
        .pre_sleep_kick_check = true,
        .interruptible_state_recheck = true,
        .guard_tick_timed_sleep = true,
    });
    const cannot_sleep = hvc_console.summarizeKhvcdSleepHandoff(.{
        .pre_sleep_kick_check = true,
        .interruptible_state_recheck = true,
        .guard_tick_timed_sleep = false,
    });
    const drained = hvc_console.summarizePollDrainOrder(.{
        .irq_backed_drained_reads = true,
        .partial_write_progress = false,
        .stalled_retry_path = false,
        .pending_sysrq_dispatch_separate = false,
        .tty_wakeup_pending = true,
        .read_activity_detected = true,
    });

    try std.testing.expect(can_sleep.guard_tick_timed_sleep);
    try std.testing.expect(!cannot_sleep.guard_tick_timed_sleep);
    try std.testing.expect(drained.irq_backed_drained_reads);
    try std.testing.expect(drained.tty_wakeup_precedes_flip_push);
    try std.testing.expect(drained.read_activity_resets_timeout);
}

test "phase11 hvc console keeps partial write progress distinct from stalled __hvc_poll retries" {
    const partial = hvc_console.summarizePollDrainOrder(.{
        .irq_backed_drained_reads = false,
        .partial_write_progress = true,
        .stalled_retry_path = false,
        .pending_sysrq_dispatch_separate = false,
        .tty_wakeup_pending = true,
        .read_activity_detected = true,
    });
    const stalled = hvc_console.summarizePollDrainOrder(.{
        .irq_backed_drained_reads = false,
        .partial_write_progress = false,
        .stalled_retry_path = true,
        .pending_sysrq_dispatch_separate = false,
        .tty_wakeup_pending = true,
        .read_activity_detected = false,
    });

    try std.testing.expect(partial.partial_write_progress);
    try std.testing.expect(!partial.stalled_retry_path);
    try std.testing.expect(partial.read_activity_resets_timeout);
    try std.testing.expect(!stalled.partial_write_progress);
    try std.testing.expect(stalled.stalled_retry_path);
    try std.testing.expect(!stalled.read_activity_resets_timeout);
}

test "phase11 hvc console keeps sysrq toggle handoff distinct from literal fallback on the primary console" {
    const handoff = hvc_console_sysrq.summarizeSysrqHandoff(.{
        .target_vtermno = 0,
        .byte = 0x0f,
        .toggles_sysrq_mode = true,
        .invokes_sysrq_handler = true,
        .is_kernel_console = true,
    });
    const literal = hvc_console_sysrq.summarizeSysrqHandoff(.{
        .target_vtermno = null,
        .byte = 0x0f,
        .toggles_sysrq_mode = false,
        .invokes_sysrq_handler = true,
        .is_kernel_console = true,
    });

    try std.testing.expect(handoff.toggles_sysrq_mode);
    try std.testing.expect(handoff.invokes_sysrq_handler);
    try std.testing.expect(!handoff.falls_back_to_literal);
    try std.testing.expect(!literal.toggles_sysrq_mode);
    try std.testing.expect(!literal.invokes_sysrq_handler);
    try std.testing.expect(literal.falls_back_to_literal);
}

test "phase11 hvc console keeps pending sysrq dispatch separate from ordinary poll bytes" {
    const pending_dispatch = hvc_console.summarizePollDrainOrder(.{
        .irq_backed_drained_reads = false,
        .partial_write_progress = false,
        .stalled_retry_path = false,
        .pending_sysrq_dispatch_separate = true,
        .tty_wakeup_pending = true,
        .read_activity_detected = false,
    });
    const ordinary_poll = hvc_console.summarizePollDrainOrder(.{
        .irq_backed_drained_reads = false,
        .partial_write_progress = false,
        .stalled_retry_path = false,
        .pending_sysrq_dispatch_separate = false,
        .tty_wakeup_pending = true,
        .read_activity_detected = true,
    });

    try std.testing.expect(pending_dispatch.pending_sysrq_dispatch_separate);
    try std.testing.expect(!pending_dispatch.read_activity_resets_timeout);
    try std.testing.expect(!ordinary_poll.pending_sysrq_dispatch_separate);
    try std.testing.expect(ordinary_poll.tty_wakeup_precedes_flip_push);
    try std.testing.expect(ordinary_poll.read_activity_resets_timeout);
}

test "phase11 hvc console keeps non-kernel ^O as a literal byte without toggling sysrq state" {
    const literal = hvc_console_sysrq.summarizeSysrqHandoff(.{
        .target_vtermno = 0,
        .byte = 0x0f,
        .toggles_sysrq_mode = false,
        .invokes_sysrq_handler = true,
        .is_kernel_console = false,
    });

    try std.testing.expect(!literal.toggles_sysrq_mode);
    try std.testing.expect(!literal.invokes_sysrq_handler);
    try std.testing.expect(literal.falls_back_to_literal);
}

test "phase11 hvc console keeps sysrq handoff unavailable after teardown" {
    const teardown = hvc_console.summarizeCloseTeardown(.{
        .tty_detached = true,
        .hupcl = true,
        .notifier_owned = true,
        .resize_work_cancelled = true,
        .wait_until_sent_intent = true,
        .close_wait_ownership = true,
        .port_initialized_before_close = true,
    });
    const cleanup = hvc_console.summarizeCleanupHandoff(.{
        .tty_port_release_handoff = true,
        .cleanup_time_tty_port_ownership = true,
        .port_reference_drop_timing = true,
    });
    const post_teardown = hvc_console_sysrq.summarizeSysrqHandoff(.{
        .target_vtermno = null,
        .byte = 0x0f,
        .toggles_sysrq_mode = true,
        .invokes_sysrq_handler = true,
        .is_kernel_console = true,
    });

    try std.testing.expect(teardown.tty_detached);
    try std.testing.expect(teardown.notifier_del_owned);
    try std.testing.expect(teardown.wait_until_sent_intent);
    try std.testing.expect(teardown.close_wait_ownership);
    try std.testing.expect(teardown.port_initialized_cleared);
    try std.testing.expect(cleanup.tty_port_release_handoff);
    try std.testing.expect(cleanup.cleanup_time_tty_port_ownership);
    try std.testing.expect(cleanup.port_reference_drop_timing);
    try std.testing.expect(!post_teardown.invokes_sysrq_handler);
    try std.testing.expect(post_teardown.falls_back_to_literal);
    try std.testing.expect(post_teardown.keeps_live_sysrq_execution_out_of_scope);
}
