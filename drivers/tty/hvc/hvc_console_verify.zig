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

test "hvc_console verify keeps remove handoff explicit when tty teardown outlives console binding" {
    var console = try hvc_console.HvcConsoleLab.init(15);
    _ = console.instantiate(0xf1);

    const detached_binding = try console.summarizeRemoveHandoff(.{
        .console_index_registered = false,
        .tty_present = true,
    });
    try std.testing.expect(!detached_binding.clears_console_slot_binding);
    try std.testing.expect(detached_binding.keeps_irq_for_followup_hangup);
    try std.testing.expect(detached_binding.drops_init_kref_port_reference);
    try std.testing.expect(detached_binding.tty_vhangup_requested);
    try std.testing.expect(detached_binding.tty_kref_put_after_vhangup);
    try std.testing.expect(detached_binding.teardown_via_hangup_pending);
    try std.testing.expect(detached_binding.host_io_pending);
}

test "hvc_console verify keeps remove handoff explicit when tty is already absent" {
    var console = try hvc_console.HvcConsoleLab.init(11);
    _ = console.instantiate(0xb1);

    const tty_gone_remove = try console.summarizeRemoveHandoff(.{
        .console_index_registered = true,
        .tty_present = false,
    });
    try std.testing.expect(tty_gone_remove.clears_console_slot_binding);
    try std.testing.expect(!tty_gone_remove.keeps_irq_for_followup_hangup);
    try std.testing.expect(tty_gone_remove.drops_init_kref_port_reference);
    try std.testing.expect(!tty_gone_remove.tty_vhangup_requested);
    try std.testing.expect(!tty_gone_remove.tty_kref_put_after_vhangup);
    try std.testing.expect(!tty_gone_remove.teardown_via_hangup_pending);
    try std.testing.expect(!tty_gone_remove.host_io_pending);
}

test "hvc_console verify keeps cleanup prerequisite failures explicit" {
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

test "hvc_console verify keeps open notifier-state failures explicit" {
    var console = try hvc_console.HvcConsoleLab.init(8);
    _ = console.instantiate(0x81);

    const notifierless = try console.summarizeOpenHandoff(.{
        .notifier_add_available = false,
    });
    try std.testing.expect(!notifierless.already_open);
    try std.testing.expect(notifierless.tty_port_tty_set_requested);
    try std.testing.expect(!notifierless.notifier_add_requested);
    try std.testing.expect(!notifierless.notifier_add_failed);
    try std.testing.expect(notifierless.dtr_rts_raise_requested);
    try std.testing.expect(notifierless.port_initialized);
    try std.testing.expect(notifierless.khvcd_wakeup_requested);
    try std.testing.expect(notifierless.host_io_deferred);

    try std.testing.expectError(error.NotifierAddResultWithoutNotifier, console.summarizeOpenHandoff(.{
        .notifier_add_available = false,
        .notifier_add_result = -1,
    }));
}

test "hvc_console verify keeps notifier prerequisite failures explicit" {
    var console = try hvc_console.HvcConsoleLab.init(10);
    _ = console.instantiate(0xa1);

    try std.testing.expectError(error.NotifierDispatchRequiresTtyRegistration, console.summarizeNotifierHandoff(.{
        .tty_registration_ready = false,
        .sysrq_dispatch_requested = true,
        .notifier_target_present = true,
    }));
}

test "hvc_console verify keeps notifier unregister timing false for never-registered and targetless surfaces" {
    var console = try hvc_console.HvcConsoleLab.init(5);
    _ = console.instantiate(0x51);

    const never_registered = try console.summarizeNotifierHandoff(.{
        .tty_registration_ready = false,
        .sysrq_dispatch_requested = false,
        .notifier_target_present = true,
    });
    try std.testing.expect(!never_registered.tty_registration_ready);
    try std.testing.expect(!never_registered.sysrq_dispatch_requested);
    try std.testing.expect(never_registered.notifier_target_present);
    try std.testing.expect(!never_registered.notifier_registration_requested);
    try std.testing.expect(!never_registered.notifier_callbacks_deferred);
    try std.testing.expect(!never_registered.notifier_unregister_deferred);
    try std.testing.expect(never_registered.khvcd_worker_execution_deferred);
    try std.testing.expect(never_registered.host_io_deferred);
    try std.testing.expect(never_registered.remove_handoff_still_required);

    const targetless_sysrq = try console.summarizeNotifierHandoff(.{
        .tty_registration_ready = true,
        .sysrq_dispatch_requested = true,
        .notifier_target_present = false,
    });
    try std.testing.expect(targetless_sysrq.tty_registration_ready);
    try std.testing.expect(targetless_sysrq.sysrq_dispatch_requested);
    try std.testing.expect(!targetless_sysrq.notifier_target_present);
    try std.testing.expect(!targetless_sysrq.notifier_registration_requested);
    try std.testing.expect(!targetless_sysrq.notifier_callbacks_deferred);
    try std.testing.expect(!targetless_sysrq.notifier_unregister_deferred);
    try std.testing.expect(targetless_sysrq.khvcd_worker_execution_deferred);
    try std.testing.expect(targetless_sysrq.host_io_deferred);
    try std.testing.expect(targetless_sysrq.remove_handoff_still_required);
}

test "hvc_console verify keeps targetless sysrq dispatch from implying notifier callbacks" {
    var console = try hvc_console.HvcConsoleLab.init(7);
    _ = console.instantiate(0xa6);

    const targetless_sysrq = try console.summarizeSysrqHandoff(.{
        .console_index_matches_boot_console = true,
        .sysrq_break_seen = true,
        .notifier_target_present = false,
    });
    try std.testing.expect(targetless_sysrq.console_index_matches_boot_console);
    try std.testing.expect(targetless_sysrq.sysrq_break_seen);
    try std.testing.expect(targetless_sysrq.sysrq_dispatch_requested);
    try std.testing.expect(!targetless_sysrq.notifier_target_present);
    try std.testing.expect(!targetless_sysrq.notifier_callbacks_deferred);
    try std.testing.expect(targetless_sysrq.khvcd_worker_execution_deferred);
    try std.testing.expect(targetless_sysrq.host_io_deferred);
    try std.testing.expect(targetless_sysrq.remove_handoff_still_required);
}

test "hvc_console verify keeps sysrq notifier deferral false without dispatch" {
    var console = try hvc_console.HvcConsoleLab.init(9);
    _ = console.instantiate(0x91);

    const detached_sysrq = try console.summarizeSysrqHandoff(.{
        .console_index_matches_boot_console = false,
        .sysrq_break_seen = true,
        .notifier_target_present = true,
    });
    try std.testing.expect(!detached_sysrq.console_index_matches_boot_console);
    try std.testing.expect(detached_sysrq.sysrq_break_seen);
    try std.testing.expect(!detached_sysrq.sysrq_dispatch_requested);
    try std.testing.expect(detached_sysrq.notifier_target_present);
    try std.testing.expect(!detached_sysrq.notifier_callbacks_deferred);
    try std.testing.expect(detached_sysrq.khvcd_worker_execution_deferred);
    try std.testing.expect(detached_sysrq.host_io_deferred);
    try std.testing.expect(detached_sysrq.remove_handoff_still_required);

    const no_break_sysrq = try console.summarizeSysrqHandoff(.{
        .console_index_matches_boot_console = true,
        .sysrq_break_seen = false,
        .notifier_target_present = true,
    });
    try std.testing.expect(no_break_sysrq.console_index_matches_boot_console);
    try std.testing.expect(!no_break_sysrq.sysrq_break_seen);
    try std.testing.expect(!no_break_sysrq.sysrq_dispatch_requested);
    try std.testing.expect(no_break_sysrq.notifier_target_present);
    try std.testing.expect(!no_break_sysrq.notifier_callbacks_deferred);
    try std.testing.expect(no_break_sysrq.khvcd_worker_execution_deferred);
    try std.testing.expect(no_break_sysrq.host_io_deferred);
    try std.testing.expect(no_break_sysrq.remove_handoff_still_required);
}
