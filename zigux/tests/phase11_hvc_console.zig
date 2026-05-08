const std = @import("std");
const hvc_console = @import("hvc_console");

test "phase11 hvc_console exposes the bounded descriptor and slot validation" {
    const descriptor = hvc_console.HvcConsoleLab.descriptor();
    try std.testing.expectEqualStrings("hvc_console_lab", descriptor.name);
    try std.testing.expectEqualStrings("drivers/tty/hvc/hvc_console.c", descriptor.anchor);
    try std.testing.expect(descriptor.provides_simple_driver_starter);
    try std.testing.expect(descriptor.touches_tty_registration);
    try std.testing.expect(descriptor.touches_polling_kthread);
    try std.testing.expect(!descriptor.touches_live_hypervisor_io);

    try std.testing.expectError(error.InvalidConsoleSlot, hvc_console.HvcConsoleLab.init(16));

    var console = try hvc_console.HvcConsoleLab.init(3);
    const slot = console.slotSnapshot();
    try std.testing.expectEqual(@as(usize, 3), slot.slot_index);
    try std.testing.expectEqual(hvc_console.removed_vtermno, slot.vtermno);
    try std.testing.expect(!slot.adapter_present);
    try std.testing.expect(!slot.usable_for_console);
    try std.testing.expectError(error.ConsoleUnavailable, console.stageWrite("boot\n", 5));
}

test "phase11 hvc console keeps open handoff boundaries reviewable" {
    var console = try hvc_console.HvcConsoleLab.init(12);
    _ = console.instantiate(0xc0);

    const first_open = try console.summarizeOpenHandoff(.{});
    try std.testing.expectEqual(@as(usize, 12), first_open.slot_index);
    try std.testing.expectEqual(@as(u32, 0xc0), first_open.vtermno);
    try std.testing.expect(first_open.adapter_present);
    try std.testing.expectEqual(@as(usize, 0), first_open.open_count_before_open);
    try std.testing.expectEqual(@as(usize, 1), first_open.open_count_after_open);
    try std.testing.expect(!first_open.already_open);
    try std.testing.expect(first_open.tty_port_tty_set_requested);
    try std.testing.expect(first_open.notifier_add_reviewable);
    try std.testing.expect(first_open.notifier_add_requested);
    try std.testing.expect(!first_open.notifier_add_failed);
    try std.testing.expect(first_open.dtr_rts_raise_requested);
    try std.testing.expect(first_open.port_initialized);
    try std.testing.expect(first_open.khvcd_wakeup_reviewable);
    try std.testing.expect(first_open.khvcd_wakeup_requested);
    try std.testing.expect(first_open.host_io_deferred);

    const already_open = try console.summarizeOpenHandoff(.{
        .open_count_before_open = 1,
    });
    try std.testing.expectEqual(@as(usize, 1), already_open.open_count_before_open);
    try std.testing.expectEqual(@as(usize, 2), already_open.open_count_after_open);
    try std.testing.expect(already_open.already_open);
    try std.testing.expect(!already_open.tty_port_tty_set_requested);
    try std.testing.expect(!already_open.notifier_add_requested);
    try std.testing.expect(!already_open.notifier_add_failed);
    try std.testing.expect(!already_open.dtr_rts_raise_requested);
    try std.testing.expect(!already_open.port_initialized);
    try std.testing.expect(already_open.khvcd_wakeup_requested);

    const failed_notifier = try console.summarizeOpenHandoff(.{
        .notifier_add_result = -16,
    });
    try std.testing.expect(!failed_notifier.already_open);
    try std.testing.expect(failed_notifier.tty_port_tty_set_requested);
    try std.testing.expect(failed_notifier.notifier_add_requested);
    try std.testing.expect(failed_notifier.notifier_add_failed);
    try std.testing.expect(!failed_notifier.dtr_rts_raise_requested);
    try std.testing.expect(!failed_notifier.port_initialized);
    try std.testing.expect(failed_notifier.khvcd_wakeup_requested);

    const notifierless = try console.summarizeOpenHandoff(.{
        .notifier_add_available = false,
    });
    try std.testing.expect(!notifierless.notifier_add_requested);
    try std.testing.expect(!notifierless.notifier_add_failed);
    try std.testing.expect(notifierless.dtr_rts_raise_requested);
    try std.testing.expect(notifierless.port_initialized);

    const no_baud = try console.summarizeOpenHandoff(.{
        .baud_configured = false,
    });
    try std.testing.expect(!no_baud.dtr_rts_raise_requested);
    try std.testing.expect(no_baud.port_initialized);

    const no_dtr_rts = try console.summarizeOpenHandoff(.{
        .dtr_rts_available = false,
    });
    try std.testing.expect(!no_dtr_rts.dtr_rts_raise_requested);
    try std.testing.expect(no_dtr_rts.port_initialized);

    try std.testing.expectError(error.NotifierAddResultWithoutNotifier, console.summarizeOpenHandoff(.{
        .notifier_add_available = false,
        .notifier_add_result = -1,
    }));

    _ = console.teardown();
    try std.testing.expectError(error.ConsoleUnavailable, console.summarizeOpenHandoff(.{}));
}

test "phase11 hvc_console summarizes final-close wait boundaries without claiming tty registration" {
    var console = try hvc_console.HvcConsoleLab.init(2);
    _ = console.instantiate(0x41);

    const final_close = try console.summarizeCloseBoundary(.{
        .port_initialized = true,
        .open_count_before_close = 1,
    });
    try std.testing.expectEqual(@as(usize, 2), final_close.slot_index);
    try std.testing.expectEqual(@as(u32, 0x41), final_close.vtermno);
    try std.testing.expect(final_close.final_close);
    try std.testing.expect(final_close.close_wait_required);
    try std.testing.expect(final_close.clears_port_initialized);
    try std.testing.expect(final_close.keeps_console_binding);
    try std.testing.expect(final_close.tty_registration_pending);
    try std.testing.expectEqual(@as(usize, 0), final_close.open_count_after_close);
    try std.testing.expectEqual(@as(usize, 100), final_close.close_wait_hz_divisor);

    const non_final_close = try console.summarizeCloseBoundary(.{
        .port_initialized = true,
        .open_count_before_close = 2,
    });
    try std.testing.expect(!non_final_close.close_skipped);
    try std.testing.expect(!non_final_close.final_close);
    try std.testing.expect(!non_final_close.close_wait_required);
    try std.testing.expect(!non_final_close.clears_port_initialized);
    try std.testing.expectEqual(@as(usize, 1), non_final_close.open_count_after_close);

    const uninitialized_close = try console.summarizeCloseBoundary(.{
        .port_initialized = false,
        .open_count_before_close = 1,
    });
    try std.testing.expect(uninitialized_close.final_close);
    try std.testing.expect(!uninitialized_close.close_wait_required);
    try std.testing.expect(!uninitialized_close.clears_port_initialized);

    const hung_up_close = try console.summarizeCloseBoundary(.{
        .hung_up = true,
        .port_initialized = true,
        .open_count_before_close = 1,
    });
    try std.testing.expect(hung_up_close.close_skipped);
    try std.testing.expect(!hung_up_close.final_close);
    try std.testing.expect(!hung_up_close.close_wait_required);
    try std.testing.expectEqual(@as(usize, 1), hung_up_close.open_count_after_close);

    try std.testing.expectError(error.InvalidOpenCount, console.summarizeCloseBoundary(.{
        .open_count_before_close = 0,
    }));

    _ = console.teardown();
    try std.testing.expectError(error.ConsoleUnavailable, console.summarizeCloseBoundary(.{}));
}

test "phase11 hvc console keeps remove-path teardown ordering reviewable" {
    var console = try hvc_console.HvcConsoleLab.init(9);
    _ = console.instantiate(0x90);

    const active_remove = try console.summarizeRemoveHandoff(.{});
    try std.testing.expectEqual(@as(usize, 9), active_remove.slot_index);
    try std.testing.expectEqual(@as(u32, 0x90), active_remove.vtermno);
    try std.testing.expect(active_remove.adapter_present);
    try std.testing.expect(active_remove.clears_console_slot_binding);
    try std.testing.expect(active_remove.keeps_irq_for_followup_hangup);
    try std.testing.expect(active_remove.drops_init_kref_port_reference);
    try std.testing.expect(active_remove.tty_vhangup_requested);
    try std.testing.expect(active_remove.tty_kref_put_after_vhangup);
    try std.testing.expect(active_remove.teardown_via_hangup_pending);
    try std.testing.expect(active_remove.host_io_pending);

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

    _ = console.teardown();
    try std.testing.expectError(error.ConsoleUnavailable, console.summarizeRemoveHandoff(.{}));
}

test "phase11 hvc console keeps tty-registration handoff boundaries reviewable" {
    var console = try hvc_console.HvcConsoleLab.init(4);
    _ = console.instantiate(0x54);

    const boot_console = try console.summarizeTtyRegistrationHandoff(.{});
    try std.testing.expectEqual(@as(usize, 4), boot_console.slot_index);
    try std.testing.expectEqual(@as(u32, 0x54), boot_console.vtermno);
    try std.testing.expect(boot_console.adapter_present);
    try std.testing.expect(boot_console.tty_driver_registration_requested);
    try std.testing.expect(boot_console.tty_device_registration_requested);
    try std.testing.expect(boot_console.console_registration_requested);
    try std.testing.expect(boot_console.keeps_console_binding_until_remove);
    try std.testing.expect(boot_console.close_wait_owned_by_hvc_close);
    try std.testing.expect(boot_console.khvcd_wakeup_reviewable);
    try std.testing.expect(boot_console.khvcd_worker_execution_deferred);
    try std.testing.expect(boot_console.notifier_target_present);
    try std.testing.expect(boot_console.notifier_callbacks_deferred);
    try std.testing.expect(boot_console.host_io_deferred);
    try std.testing.expect(boot_console.remove_handoff_still_required);

    const detached_console = try console.summarizeTtyRegistrationHandoff(.{
        .console_index_matches_boot_console = false,
        .notifier_target_present = false,
    });
    try std.testing.expect(detached_console.tty_driver_registration_requested);
    try std.testing.expect(detached_console.tty_device_registration_requested);
    try std.testing.expect(!detached_console.console_registration_requested);
    try std.testing.expect(!detached_console.keeps_console_binding_until_remove);
    try std.testing.expect(detached_console.close_wait_owned_by_hvc_close);
    try std.testing.expect(detached_console.khvcd_wakeup_reviewable);
    try std.testing.expect(detached_console.khvcd_worker_execution_deferred);
    try std.testing.expect(!detached_console.notifier_target_present);
    try std.testing.expect(!detached_console.notifier_callbacks_deferred);
    try std.testing.expect(detached_console.host_io_deferred);
    try std.testing.expect(detached_console.remove_handoff_still_required);

    _ = console.teardown();
    try std.testing.expectError(error.ConsoleUnavailable, console.summarizeTtyRegistrationHandoff(.{}));
}

test "phase11 hvc console keeps sysrq handoff boundaries reviewable" {
    var console = try hvc_console.HvcConsoleLab.init(6);
    _ = console.instantiate(0x66);

    const boot_sysrq = try console.summarizeSysrqHandoff(.{});
    try std.testing.expectEqual(@as(usize, 6), boot_sysrq.slot_index);
    try std.testing.expectEqual(@as(u32, 0x66), boot_sysrq.vtermno);
    try std.testing.expect(boot_sysrq.adapter_present);
    try std.testing.expect(boot_sysrq.console_index_matches_boot_console);
    try std.testing.expect(boot_sysrq.sysrq_break_seen);
    try std.testing.expect(boot_sysrq.sysrq_dispatch_reviewable);
    try std.testing.expect(boot_sysrq.sysrq_dispatch_requested);
    try std.testing.expect(boot_sysrq.notifier_target_present);
    try std.testing.expect(boot_sysrq.notifier_callbacks_deferred);
    try std.testing.expect(boot_sysrq.khvcd_worker_execution_deferred);
    try std.testing.expect(boot_sysrq.host_io_deferred);
    try std.testing.expect(boot_sysrq.remove_handoff_still_required);

    const detached_sysrq = try console.summarizeSysrqHandoff(.{
        .console_index_matches_boot_console = false,
        .sysrq_break_seen = true,
        .notifier_target_present = true,
    });
    try std.testing.expect(!detached_sysrq.console_index_matches_boot_console);
    try std.testing.expect(detached_sysrq.sysrq_break_seen);
    try std.testing.expect(detached_sysrq.sysrq_dispatch_reviewable);
    try std.testing.expect(!detached_sysrq.sysrq_dispatch_requested);
    try std.testing.expect(detached_sysrq.notifier_target_present);
    try std.testing.expect(!detached_sysrq.notifier_callbacks_deferred);
    try std.testing.expect(detached_sysrq.khvcd_worker_execution_deferred);
    try std.testing.expect(detached_sysrq.host_io_deferred);
    try std.testing.expect(detached_sysrq.remove_handoff_still_required);

    _ = console.teardown();
    try std.testing.expectError(error.ConsoleUnavailable, console.summarizeSysrqHandoff(.{}));
}

test "phase11 hvc console keeps notifier handoff boundaries reviewable" {
    var console = try hvc_console.HvcConsoleLab.init(8);
    _ = console.instantiate(0x88);

    const live_notifier = try console.summarizeNotifierHandoff(.{});
    try std.testing.expectEqual(@as(usize, 8), live_notifier.slot_index);
    try std.testing.expectEqual(@as(u32, 0x88), live_notifier.vtermno);
    try std.testing.expect(live_notifier.adapter_present);
    try std.testing.expect(live_notifier.tty_registration_ready);
    try std.testing.expect(live_notifier.sysrq_dispatch_requested);
    try std.testing.expect(live_notifier.notifier_target_present);
    try std.testing.expect(live_notifier.notifier_registration_reviewable);
    try std.testing.expect(live_notifier.notifier_registration_requested);
    try std.testing.expect(live_notifier.notifier_callbacks_deferred);
    try std.testing.expect(live_notifier.notifier_unregister_deferred);
    try std.testing.expect(live_notifier.khvcd_worker_execution_deferred);
    try std.testing.expect(live_notifier.host_io_deferred);
    try std.testing.expect(live_notifier.remove_handoff_still_required);

    const registered_without_sysrq = try console.summarizeNotifierHandoff(.{
        .tty_registration_ready = true,
        .sysrq_dispatch_requested = false,
        .notifier_target_present = true,
    });
    try std.testing.expect(registered_without_sysrq.tty_registration_ready);
    try std.testing.expect(!registered_without_sysrq.sysrq_dispatch_requested);
    try std.testing.expect(registered_without_sysrq.notifier_target_present);
    try std.testing.expect(registered_without_sysrq.notifier_registration_reviewable);
    try std.testing.expect(registered_without_sysrq.notifier_registration_requested);
    try std.testing.expect(!registered_without_sysrq.notifier_callbacks_deferred);
    try std.testing.expect(registered_without_sysrq.notifier_unregister_deferred);
    try std.testing.expect(registered_without_sysrq.khvcd_worker_execution_deferred);
    try std.testing.expect(registered_without_sysrq.host_io_deferred);
    try std.testing.expect(registered_without_sysrq.remove_handoff_still_required);

    const missing_target = try console.summarizeNotifierHandoff(.{
        .tty_registration_ready = false,
        .sysrq_dispatch_requested = false,
        .notifier_target_present = false,
    });
    try std.testing.expect(!missing_target.tty_registration_ready);
    try std.testing.expect(!missing_target.sysrq_dispatch_requested);
    try std.testing.expect(!missing_target.notifier_target_present);
    try std.testing.expect(missing_target.notifier_registration_reviewable);
    try std.testing.expect(!missing_target.notifier_registration_requested);
    try std.testing.expect(!missing_target.notifier_callbacks_deferred);
    try std.testing.expect(!missing_target.notifier_unregister_deferred);
    try std.testing.expect(missing_target.khvcd_worker_execution_deferred);
    try std.testing.expect(missing_target.host_io_deferred);
    try std.testing.expect(missing_target.remove_handoff_still_required);

    try std.testing.expectError(error.NotifierDispatchRequiresTtyRegistration, console.summarizeNotifierHandoff(.{
        .tty_registration_ready = false,
        .sysrq_dispatch_requested = true,
        .notifier_target_present = true,
    }));

    _ = console.teardown();
    try std.testing.expectError(error.ConsoleUnavailable, console.summarizeNotifierHandoff(.{}));
}

test "phase11 hvc console keeps notifier unregister timing false before tty registration" {
    var console = try hvc_console.HvcConsoleLab.init(7);
    _ = console.instantiate(0x77);

    const never_registered = try console.summarizeNotifierHandoff(.{
        .tty_registration_ready = false,
        .sysrq_dispatch_requested = false,
        .notifier_target_present = true,
    });
    try std.testing.expectEqual(@as(usize, 7), never_registered.slot_index);
    try std.testing.expectEqual(@as(u32, 0x77), never_registered.vtermno);
    try std.testing.expect(never_registered.adapter_present);
    try std.testing.expect(!never_registered.tty_registration_ready);
    try std.testing.expect(!never_registered.sysrq_dispatch_requested);
    try std.testing.expect(never_registered.notifier_target_present);
    try std.testing.expect(never_registered.notifier_registration_reviewable);
    try std.testing.expect(!never_registered.notifier_registration_requested);
    try std.testing.expect(!never_registered.notifier_callbacks_deferred);
    try std.testing.expect(!never_registered.notifier_unregister_deferred);
    try std.testing.expect(never_registered.khvcd_worker_execution_deferred);
    try std.testing.expect(never_registered.host_io_deferred);
    try std.testing.expect(never_registered.remove_handoff_still_required);

    _ = console.teardown();
    try std.testing.expectError(error.ConsoleUnavailable, console.summarizeNotifierHandoff(.{}));
}

test "phase11 hvc console keeps notifier unregister timing false without a notifier target" {
    var console = try hvc_console.HvcConsoleLab.init(10);
    _ = console.instantiate(0xaa);

    const targetless = try console.summarizeNotifierHandoff(.{
        .tty_registration_ready = true,
        .sysrq_dispatch_requested = false,
        .notifier_target_present = false,
    });
    try std.testing.expectEqual(@as(usize, 10), targetless.slot_index);
    try std.testing.expectEqual(@as(u32, 0xaa), targetless.vtermno);
    try std.testing.expect(targetless.adapter_present);
    try std.testing.expect(targetless.tty_registration_ready);
    try std.testing.expect(!targetless.sysrq_dispatch_requested);
    try std.testing.expect(!targetless.notifier_target_present);
    try std.testing.expect(targetless.notifier_registration_reviewable);
    try std.testing.expect(!targetless.notifier_registration_requested);
    try std.testing.expect(!targetless.notifier_callbacks_deferred);
    try std.testing.expect(!targetless.notifier_unregister_deferred);
    try std.testing.expect(targetless.khvcd_worker_execution_deferred);
    try std.testing.expect(targetless.host_io_deferred);
    try std.testing.expect(targetless.remove_handoff_still_required);

    _ = console.teardown();
    try std.testing.expectError(error.ConsoleUnavailable, console.summarizeNotifierHandoff(.{}));
}

test "phase11 hvc console keeps notifier unregister timing false for targetless sysrq handoff" {
    var console = try hvc_console.HvcConsoleLab.init(11);
    _ = console.instantiate(0xbb);

    const targetless_sysrq = try console.summarizeNotifierHandoff(.{
        .tty_registration_ready = true,
        .sysrq_dispatch_requested = true,
        .notifier_target_present = false,
    });
    try std.testing.expectEqual(@as(usize, 11), targetless_sysrq.slot_index);
    try std.testing.expectEqual(@as(u32, 0xbb), targetless_sysrq.vtermno);
    try std.testing.expect(targetless_sysrq.adapter_present);
    try std.testing.expect(targetless_sysrq.tty_registration_ready);
    try std.testing.expect(targetless_sysrq.sysrq_dispatch_requested);
    try std.testing.expect(!targetless_sysrq.notifier_target_present);
    try std.testing.expect(targetless_sysrq.notifier_registration_reviewable);
    try std.testing.expect(!targetless_sysrq.notifier_registration_requested);
    try std.testing.expect(!targetless_sysrq.notifier_callbacks_deferred);
    try std.testing.expect(!targetless_sysrq.notifier_unregister_deferred);
    try std.testing.expect(targetless_sysrq.khvcd_worker_execution_deferred);
    try std.testing.expect(targetless_sysrq.host_io_deferred);
    try std.testing.expect(targetless_sysrq.remove_handoff_still_required);

    _ = console.teardown();
    try std.testing.expectError(error.ConsoleUnavailable, console.summarizeNotifierHandoff(.{}));
}

test "phase11 hvc console keeps khvcd polling wakeups and teardown pressure reviewable" {
    var console = try hvc_console.HvcConsoleLab.init(5);
    _ = console.instantiate(0x55);

    const active_poll = try console.summarizeKhvcdPollingContract(.{
        .close = .{
            .port_initialized = true,
            .open_count_before_close = 1,
        },
        .notifier_add_pending = true,
        .notifier_hangup_pending = true,
        .read_poll_pending = true,
        .write_poll_pending = true,
    });
    try std.testing.expectEqual(@as(usize, 5), active_poll.slot_index);
    try std.testing.expectEqual(@as(u32, 0x55), active_poll.vtermno);
    try std.testing.expect(active_poll.adapter_present);
    try std.testing.expect(active_poll.final_close_wait_required);
    try std.testing.expect(active_poll.clears_port_initialized_on_final_close);
    try std.testing.expect(active_poll.keeps_console_binding);
    try std.testing.expect(active_poll.tty_registration_pending);
    try std.testing.expect(active_poll.notifier_add_pending);
    try std.testing.expect(active_poll.notifier_hangup_pending);
    try std.testing.expect(active_poll.notifier_driven_wakeup_pending);
    try std.testing.expect(active_poll.read_poll_pending);
    try std.testing.expect(active_poll.write_poll_pending);
    try std.testing.expect(active_poll.poll_driven_wakeup_pending);
    try std.testing.expect(active_poll.khvcd_polling_pending);
    try std.testing.expect(active_poll.bounded_reschedule_pending);
    try std.testing.expect(active_poll.teardown_host_io_pending);

    const notifier_only = try console.summarizeKhvcdPollingContract(.{
        .close = .{
            .port_initialized = false,
            .open_count_before_close = 2,
        },
        .notifier_add_pending = true,
    });
    try std.testing.expect(!notifier_only.final_close_wait_required);
    try std.testing.expect(!notifier_only.clears_port_initialized_on_final_close);
    try std.testing.expect(notifier_only.notifier_add_pending);
    try std.testing.expect(!notifier_only.notifier_hangup_pending);
    try std.testing.expect(notifier_only.notifier_driven_wakeup_pending);
    try std.testing.expect(!notifier_only.read_poll_pending);
    try std.testing.expect(!notifier_only.write_poll_pending);
    try std.testing.expect(!notifier_only.poll_driven_wakeup_pending);
    try std.testing.expect(notifier_only.khvcd_polling_pending);
    try std.testing.expect(notifier_only.bounded_reschedule_pending);
    try std.testing.expect(!notifier_only.teardown_host_io_pending);

    const hangup_only = try console.summarizeKhvcdPollingContract(.{
        .close = .{
            .port_initialized = false,
            .open_count_before_close = 2,
        },
        .notifier_hangup_pending = true,
    });
    try std.testing.expect(!hangup_only.final_close_wait_required);
    try std.testing.expect(!hangup_only.clears_port_initialized_on_final_close);
    try std.testing.expect(!hangup_only.notifier_add_pending);
    try std.testing.expect(hangup_only.notifier_hangup_pending);
    try std.testing.expect(hangup_only.notifier_driven_wakeup_pending);
    try std.testing.expect(!hangup_only.read_poll_pending);
    try std.testing.expect(!hangup_only.write_poll_pending);
    try std.testing.expect(!hangup_only.poll_driven_wakeup_pending);
    try std.testing.expect(hangup_only.khvcd_polling_pending);
    try std.testing.expect(hangup_only.bounded_reschedule_pending);
    try std.testing.expect(hangup_only.teardown_host_io_pending);

    _ = console.teardown();
    try std.testing.expectError(error.ConsoleUnavailable, console.summarizeKhvcdPollingContract(.{}));
}

test "phase11 hvc console keeps poll-only khvcd wakeups reviewable without notifier carryover" {
    var console = try hvc_console.HvcConsoleLab.init(13);
    _ = console.instantiate(0xd5);

    const read_only = try console.summarizeKhvcdPollingContract(.{
        .close = .{
            .port_initialized = false,
            .open_count_before_close = 2,
        },
        .read_poll_pending = true,
    });
    try std.testing.expect(!read_only.final_close_wait_required);
    try std.testing.expect(!read_only.clears_port_initialized_on_final_close);
    try std.testing.expect(!read_only.notifier_add_pending);
    try std.testing.expect(!read_only.notifier_hangup_pending);
    try std.testing.expect(!read_only.notifier_driven_wakeup_pending);
    try std.testing.expect(read_only.read_poll_pending);
    try std.testing.expect(!read_only.write_poll_pending);
    try std.testing.expect(read_only.poll_driven_wakeup_pending);
    try std.testing.expect(read_only.khvcd_polling_pending);
    try std.testing.expect(read_only.bounded_reschedule_pending);
    try std.testing.expect(read_only.teardown_host_io_pending);

    const write_only = try console.summarizeKhvcdPollingContract(.{
        .close = .{
            .port_initialized = false,
            .open_count_before_close = 2,
        },
        .write_poll_pending = true,
    });
    try std.testing.expect(!write_only.final_close_wait_required);
    try std.testing.expect(!write_only.clears_port_initialized_on_final_close);
    try std.testing.expect(!write_only.notifier_add_pending);
    try std.testing.expect(!write_only.notifier_hangup_pending);
    try std.testing.expect(!write_only.notifier_driven_wakeup_pending);
    try std.testing.expect(!write_only.read_poll_pending);
    try std.testing.expect(write_only.write_poll_pending);
    try std.testing.expect(write_only.poll_driven_wakeup_pending);
    try std.testing.expect(write_only.khvcd_polling_pending);
    try std.testing.expect(write_only.bounded_reschedule_pending);
    try std.testing.expect(write_only.teardown_host_io_pending);

    _ = console.teardown();
    try std.testing.expectError(error.ConsoleUnavailable, console.summarizeKhvcdPollingContract(.{}));
}

test "phase11 hvc console keeps hangup disconnect teardown boundaries reviewable" {
    var console = try hvc_console.HvcConsoleLab.init(9);
    _ = console.instantiate(0x90);

    const active_hangup = try console.summarizeHangupDisconnect(.{
        .port_count_before_hangup = 2,
        .notifier_hangup_present = true,
        .buffered_write_len = 5,
    });
    try std.testing.expectEqual(@as(usize, 9), active_hangup.slot_index);
    try std.testing.expectEqual(@as(u32, 0x90), active_hangup.vtermno);
    try std.testing.expect(active_hangup.adapter_present);
    try std.testing.expect(active_hangup.cancel_resize_pending);
    try std.testing.expect(!active_hangup.hangup_skipped);
    try std.testing.expectEqual(@as(usize, 2), active_hangup.port_count_before_hangup);
    try std.testing.expectEqual(@as(usize, 0), active_hangup.port_count_after_hangup);
    try std.testing.expect(active_hangup.tty_detached);
    try std.testing.expect(active_hangup.clears_outbuf);
    try std.testing.expectEqual(@as(usize, 5), active_hangup.buffered_write_len_before_hangup);
    try std.testing.expectEqual(@as(usize, 0), active_hangup.buffered_write_len_after_hangup);
    try std.testing.expect(active_hangup.notifier_hangup_pending);
    try std.testing.expect(active_hangup.keeps_console_binding);

    const stale_hangup = try console.summarizeHangupDisconnect(.{
        .port_count_before_hangup = 0,
        .notifier_hangup_present = true,
        .buffered_write_len = 3,
    });
    try std.testing.expect(stale_hangup.cancel_resize_pending);
    try std.testing.expect(stale_hangup.hangup_skipped);
    try std.testing.expectEqual(@as(usize, 0), stale_hangup.port_count_after_hangup);
    try std.testing.expect(!stale_hangup.tty_detached);
    try std.testing.expect(!stale_hangup.clears_outbuf);
    try std.testing.expectEqual(@as(usize, 3), stale_hangup.buffered_write_len_after_hangup);
    try std.testing.expect(!stale_hangup.notifier_hangup_pending);
    try std.testing.expect(stale_hangup.keeps_console_binding);

    _ = console.teardown();
    try std.testing.expectError(error.ConsoleUnavailable, console.summarizeHangupDisconnect(.{}));
}

test "phase11 hvc_console adds carriage returns and keeps final flush intent on successful writes" {
    var console = try hvc_console.HvcConsoleLab.init(1);
    const slot = console.instantiate(0x41);
    try std.testing.expect(slot.adapter_present);
    try std.testing.expect(slot.usable_for_console);

    var write = try console.stageWrite("boot\nok\n", 9);
    try std.testing.expectEqual(@as(usize, 10), write.framed_len);
    try std.testing.expectEqualStrings("boot\r\nok\r\n", write.framed[0..write.framed_len]);
    try std.testing.expectEqual(@as(usize, 1), write.remaining_len);
    try std.testing.expectEqualStrings("\n", write.remaining[0..write.remaining_len]);
    try std.testing.expectEqual(hvc_console.FlushIntent.final_drain, write.flush_intent);
    try std.testing.expectEqual(hvc_console.FlushProgress.partial_write, write.flush_progress);
    try std.testing.expect(write.final_flush);
    try std.testing.expect(!write.dropped_on_error);

    write = try console.stageWrite("ok\n", 4);
    try std.testing.expectEqual(@as(usize, 4), write.framed_len);
    try std.testing.expectEqual(@as(usize, 0), write.remaining_len);
    try std.testing.expectEqual(hvc_console.FlushIntent.final_drain, write.flush_intent);
    try std.testing.expectEqual(hvc_console.FlushProgress.fully_written, write.flush_progress);
    try std.testing.expect(!write.dropped_on_error);

    write = try console.stageWrite("a\n\nb", 6);
    try std.testing.expectEqual(@as(usize, 6), write.framed_len);
    try std.testing.expectEqualStrings("a\r\n\r\nb", write.framed[0..write.framed_len]);
    try std.testing.expectEqual(@as(usize, 0), write.remaining_len);
    try std.testing.expectEqual(hvc_console.FlushIntent.final_drain, write.flush_intent);
    try std.testing.expectEqual(hvc_console.FlushProgress.fully_written, write.flush_progress);

    write = try console.stageWrite("a\r\nb", 4);
    try std.testing.expectEqual(@as(usize, 4), write.framed_len);
    try std.testing.expectEqualStrings("a\r\nb", write.framed[0..write.framed_len]);
    try std.testing.expectEqual(@as(usize, 0), write.remaining_len);
    try std.testing.expectEqual(hvc_console.FlushIntent.final_drain, write.flush_intent);
    try std.testing.expectEqual(hvc_console.FlushProgress.fully_written, write.flush_progress);
}

test "phase11 hvc_console keeps retry intent on eagain and clears the slot on teardown" {
    var console = try hvc_console.HvcConsoleLab.init(0);
    _ = console.instantiate(0x99);

    var write = try console.stageWrite("x\n", hvc_console.eagain);
    try std.testing.expectEqual(@as(usize, 3), write.framed_len);
    try std.testing.expectEqualStrings("x\r\n", write.framed[0..write.framed_len]);
    try std.testing.expectEqual(@as(usize, 3), write.remaining_len);
    try std.testing.expectEqualStrings("x\r\n", write.remaining[0..write.remaining_len]);
    try std.testing.expectEqual(hvc_console.FlushIntent.retry_after_eagain, write.flush_intent);
    try std.testing.expectEqual(hvc_console.FlushProgress.no_progress, write.flush_progress);
    try std.testing.expect(write.final_flush);
    try std.testing.expect(!write.dropped_on_error);

    write = try console.stageWrite("z\n", 0);
    try std.testing.expectEqual(@as(usize, 3), write.framed_len);
    try std.testing.expectEqualStrings("z\r\n", write.framed[0..write.framed_len]);
    try std.testing.expectEqual(@as(usize, 0), write.remaining_len);
    try std.testing.expectEqual(hvc_console.FlushIntent.none, write.flush_intent);
    try std.testing.expectEqual(hvc_console.FlushProgress.dropped_on_error, write.flush_progress);
    try std.testing.expect(write.final_flush);
    try std.testing.expect(write.dropped_on_error);

    write = try console.stageWrite("fatal\n", -5);
    try std.testing.expectEqual(@as(usize, 7), write.framed_len);
    try std.testing.expectEqual(@as(usize, 0), write.remaining_len);
    try std.testing.expectEqual(hvc_console.FlushIntent.none, write.flush_intent);
    try std.testing.expectEqual(hvc_console.FlushProgress.dropped_on_error, write.flush_progress);
    try std.testing.expect(write.final_flush);
    try std.testing.expect(write.dropped_on_error);

    try std.testing.expectError(
        error.InputTooLarge,
        console.stageWrite("0123456789abcdefg", 17),
    );

    const teardown = console.teardown();
    try std.testing.expectEqual(hvc_console.removed_vtermno, teardown.vtermno);
    try std.testing.expect(!teardown.adapter_present);
    try std.testing.expect(!teardown.usable_for_console);
    try std.testing.expectError(error.ConsoleUnavailable, console.stageWrite("gone\n", 6));
}
