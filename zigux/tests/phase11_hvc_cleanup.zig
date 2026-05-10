const std = @import("std");
const hvc_console = @import("hvc_console");

test "phase11 hvc console keeps hvc_cleanup tty-port release boundaries reviewable" {
    var console = try hvc_console.HvcConsoleLab.init(5);
    _ = console.instantiate(0x55);

    const final_cleanup = try console.summarizeCleanupHandoff(.{});
    try std.testing.expectEqual(@as(usize, 5), final_cleanup.slot_index);
    try std.testing.expectEqual(@as(u32, 0x55), final_cleanup.vtermno);
    try std.testing.expect(final_cleanup.adapter_present);
    try std.testing.expect(!final_cleanup.close_skipped);
    try std.testing.expect(final_cleanup.final_close);
    try std.testing.expect(final_cleanup.tty_port_reference_live);
    try std.testing.expect(final_cleanup.tty_port_put_requested);
    try std.testing.expect(final_cleanup.drops_tty_port_reference);
    try std.testing.expect(final_cleanup.deferred_final_release);

    const hangup_cleanup = try console.summarizeCleanupHandoff(.{
        .hung_up = true,
    });
    try std.testing.expect(hangup_cleanup.close_skipped);
    try std.testing.expect(!hangup_cleanup.final_close);
    try std.testing.expect(hangup_cleanup.tty_port_reference_live);
    try std.testing.expect(hangup_cleanup.tty_port_put_requested);
    try std.testing.expect(hangup_cleanup.drops_tty_port_reference);
    try std.testing.expect(hangup_cleanup.deferred_final_release);

    try std.testing.expectError(error.CleanupRequiresFinalCloseOrHangup, console.summarizeCleanupHandoff(.{
        .final_close = false,
    }));
    try std.testing.expectError(error.CleanupRequiresTtyPortReference, console.summarizeCleanupHandoff(.{
        .tty_port_reference_live = false,
    }));
    try std.testing.expectError(error.CleanupRequiresTtyPortReference, console.summarizeCleanupHandoff(.{
        .hung_up = true,
        .tty_port_reference_live = false,
    }));

    _ = console.teardown();
    try std.testing.expectError(error.ConsoleUnavailable, console.summarizeCleanupHandoff(.{}));
}

test "phase11 hvc console keeps write-teardown hangup buffering split reviewable" {
    var console = try hvc_console.HvcConsoleLab.init(6);
    _ = console.instantiate(0x66);

    const active_hangup = try console.summarizeWriteTeardownHandoff(.{
        .input = "ok\n",
        .put_result = hvc_console.eagain,
        .hangup = .{
            .port_count_before_hangup = 1,
            .notifier_hangup_present = true,
        },
    });
    try std.testing.expectEqual(@as(usize, 4), active_hangup.framed_len);
    try std.testing.expectEqual(@as(usize, 4), active_hangup.remaining_len_before_hangup);
    try std.testing.expectEqual(hvc_console.FlushIntent.retry_after_eagain, active_hangup.flush_intent);
    try std.testing.expectEqual(hvc_console.FlushProgress.no_progress, active_hangup.flush_progress);
    try std.testing.expect(!active_hangup.dropped_on_error);
    try std.testing.expect(!active_hangup.hangup_skipped);
    try std.testing.expect(active_hangup.tty_detached);
    try std.testing.expect(active_hangup.clears_buffered_write);
    try std.testing.expectEqual(@as(usize, 0), active_hangup.buffered_write_len_after_hangup);
    try std.testing.expect(active_hangup.notifier_hangup_pending);
    try std.testing.expect(active_hangup.keeps_console_binding);

    const stale_hangup = try console.summarizeWriteTeardownHandoff(.{
        .input = "a\n",
        .put_result = 1,
        .hangup = .{
            .port_count_before_hangup = 0,
            .notifier_hangup_present = true,
        },
    });
    try std.testing.expectEqual(@as(usize, 3), stale_hangup.framed_len);
    try std.testing.expectEqual(@as(usize, 2), stale_hangup.remaining_len_before_hangup);
    try std.testing.expectEqual(hvc_console.FlushIntent.final_drain, stale_hangup.flush_intent);
    try std.testing.expectEqual(hvc_console.FlushProgress.partial_write, stale_hangup.flush_progress);
    try std.testing.expect(!stale_hangup.dropped_on_error);
    try std.testing.expect(stale_hangup.hangup_skipped);
    try std.testing.expect(!stale_hangup.tty_detached);
    try std.testing.expect(!stale_hangup.clears_buffered_write);
    try std.testing.expectEqual(@as(usize, 2), stale_hangup.buffered_write_len_after_hangup);
    try std.testing.expect(!stale_hangup.notifier_hangup_pending);
    try std.testing.expect(stale_hangup.keeps_console_binding);

    const fatal_write = try console.summarizeWriteTeardownHandoff(.{
        .input = "panic",
        .put_result = -5,
        .hangup = .{
            .port_count_before_hangup = 1,
            .notifier_hangup_present = false,
        },
    });
    try std.testing.expectEqual(@as(usize, 5), fatal_write.framed_len);
    try std.testing.expectEqual(@as(usize, 0), fatal_write.remaining_len_before_hangup);
    try std.testing.expectEqual(hvc_console.FlushIntent.none, fatal_write.flush_intent);
    try std.testing.expectEqual(hvc_console.FlushProgress.dropped_on_error, fatal_write.flush_progress);
    try std.testing.expect(fatal_write.dropped_on_error);
    try std.testing.expect(!fatal_write.hangup_skipped);
    try std.testing.expect(fatal_write.tty_detached);
    try std.testing.expect(fatal_write.clears_buffered_write);
    try std.testing.expectEqual(@as(usize, 0), fatal_write.buffered_write_len_after_hangup);
    try std.testing.expect(!fatal_write.notifier_hangup_pending);
    try std.testing.expect(fatal_write.keeps_console_binding);

    _ = console.teardown();
    try std.testing.expectError(error.ConsoleUnavailable, console.summarizeWriteTeardownHandoff(.{
        .input = "gone\n",
        .put_result = hvc_console.eagain,
    }));
}

test "phase11 hvc console keeps oversized buffered-write rejection reviewable" {
    var console = try hvc_console.HvcConsoleLab.init(7);
    _ = console.instantiate(0x67);

    const bounded_hangup = try console.summarizeHangupDisconnect(.{
        .port_count_before_hangup = 0,
        .buffered_write_len = hvc_console.outbuf_capacity * 2,
    });
    try std.testing.expect(bounded_hangup.hangup_skipped);
    try std.testing.expectEqual(@as(usize, hvc_console.outbuf_capacity * 2), bounded_hangup.buffered_write_len_after_hangup);

    try std.testing.expectError(error.BufferedWriteTooLarge, console.summarizeHangupDisconnect(.{
        .buffered_write_len = hvc_console.outbuf_capacity * 2 + 1,
    }));

    _ = console.teardown();
    try std.testing.expectError(error.ConsoleUnavailable, console.summarizeHangupDisconnect(.{}));
}
