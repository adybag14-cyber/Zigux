const std = @import("std");
const hvc_console = @import("hvc_console.zig");

test "hvc_console verify keeps final-close teardown handoff ordering explicit" {
    var console = try hvc_console.HvcConsoleLab.init(12);
    const slot = console.instantiate(0xc1);
    try std.testing.expect(slot.usable_for_console);

    const close = try console.summarizeCloseBoundary(.{
        .port_initialized = true,
        .open_count_before_close = 1,
    });
    try std.testing.expect(close.final_close);
    try std.testing.expect(close.close_wait_required);
    try std.testing.expect(close.clears_port_initialized);
    try std.testing.expect(close.keeps_console_binding);
    try std.testing.expect(close.tty_registration_pending);
    try std.testing.expectEqual(hvc_console.close_wait_hz_divisor, close.close_wait_hz_divisor);

    const cleanup = try console.summarizeCleanupHandoff(.{
        .final_close = close.final_close,
    });
    try std.testing.expect(!cleanup.close_skipped);
    try std.testing.expect(cleanup.final_close);
    try std.testing.expect(cleanup.tty_port_put_requested);
    try std.testing.expect(cleanup.drops_tty_port_reference);
    try std.testing.expect(cleanup.deferred_final_release);

    const remove = try console.summarizeRemoveHandoff(.{
        .console_index_registered = close.keeps_console_binding,
        .tty_present = true,
    });
    try std.testing.expect(remove.clears_console_slot_binding);
    try std.testing.expect(remove.keeps_irq_for_followup_hangup);
    try std.testing.expect(remove.drops_init_kref_port_reference);
    try std.testing.expect(remove.tty_vhangup_requested);
    try std.testing.expect(remove.tty_kref_put_after_vhangup);
    try std.testing.expect(remove.teardown_via_hangup_pending);
    try std.testing.expect(remove.host_io_pending);

    const torn_down = console.teardown();
    try std.testing.expect(!torn_down.usable_for_console);
    try std.testing.expectError(error.ConsoleUnavailable, console.summarizeCleanupHandoff(.{}));
    try std.testing.expectError(error.ConsoleUnavailable, console.summarizeRemoveHandoff(.{}));
}

test "hvc_console verify keeps hung-up and detached teardown matrix truthful" {
    var console = try hvc_console.HvcConsoleLab.init(13);
    _ = console.instantiate(0xd1);

    const hung_up_close = try console.summarizeCloseBoundary(.{
        .hung_up = true,
        .port_initialized = true,
        .open_count_before_close = 2,
    });
    try std.testing.expect(hung_up_close.close_skipped);
    try std.testing.expect(!hung_up_close.final_close);
    try std.testing.expect(!hung_up_close.close_wait_required);
    try std.testing.expectEqual(@as(usize, 2), hung_up_close.open_count_after_close);

    const hung_up_cleanup = try console.summarizeCleanupHandoff(.{
        .hung_up = true,
        .final_close = false,
    });
    try std.testing.expect(hung_up_cleanup.close_skipped);
    try std.testing.expect(!hung_up_cleanup.final_close);
    try std.testing.expect(hung_up_cleanup.tty_port_put_requested);
    try std.testing.expect(hung_up_cleanup.drops_tty_port_reference);

    const detached_remove = try console.summarizeRemoveHandoff(.{
        .console_index_registered = false,
        .tty_present = false,
    });
    try std.testing.expect(!detached_remove.clears_console_slot_binding);
    try std.testing.expect(!detached_remove.keeps_irq_for_followup_hangup);
    try std.testing.expect(detached_remove.drops_init_kref_port_reference);
    try std.testing.expect(!detached_remove.tty_vhangup_requested);
    try std.testing.expect(!detached_remove.tty_kref_put_after_vhangup);
    try std.testing.expect(!detached_remove.teardown_via_hangup_pending);
    try std.testing.expect(!detached_remove.host_io_pending);
}

test "hvc_console verify keeps cleanup missing-reference failures explicit" {
    var console = try hvc_console.HvcConsoleLab.init(14);
    _ = console.instantiate(0xe1);

    try std.testing.expectError(error.CleanupRequiresFinalCloseOrHangup, console.summarizeCleanupHandoff(.{
        .final_close = false,
    }));
    try std.testing.expectError(error.CleanupRequiresTtyPortReference, console.summarizeCleanupHandoff(.{
        .tty_port_reference_live = false,
    }));
    try std.testing.expectError(error.CleanupRequiresTtyPortReference, console.summarizeCleanupHandoff(.{
        .hung_up = true,
        .final_close = false,
        .tty_port_reference_live = false,
    }));
}
