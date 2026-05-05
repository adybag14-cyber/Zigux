const std = @import("std");
const hvc_console = @import("hvc_console");

test "phase11 hvc_console exposes the bounded descriptor and slot validation" {
    const descriptor = hvc_console.HvcConsoleLab.descriptor();
    try std.testing.expectEqualStrings("hvc_console_lab", descriptor.name);
    try std.testing.expectEqualStrings("drivers/tty/hvc/hvc_console.c", descriptor.anchor);
    try std.testing.expect(descriptor.provides_simple_driver_starter);
    try std.testing.expect(descriptor.touches_tty_registration);
    try std.testing.expect(!descriptor.touches_polling_kthread);
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

    const unregistered_target = try console.summarizeNotifierHandoff(.{
        .tty_registration_ready = false,
        .sysrq_dispatch_requested = false,
        .notifier_target_present = true,
    });
    try std.testing.expect(!unregistered_target.tty_registration_ready);
    try std.testing.expect(!unregistered_target.sysrq_dispatch_requested);
    try std.testing.expect(unregistered_target.notifier_target_present);
    try std.testing.expect(unregistered_target.notifier_registration_reviewable);
    try std.testing.expect(!unregistered_target.notifier_registration_requested);
    try std.testing.expect(!unregistered_target.notifier_callbacks_deferred);
    try std.testing.expect(!unregistered_target.notifier_unregister_deferred);
    try std.testing.expect(unregistered_target.khvcd_worker_execution_deferred);
    try std.testing.expect(unregistered_target.host_io_deferred);
    try std.testing.expect(unregistered_target.remove_handoff_still_required);

    try std.testing.expectError(error.NotifierDispatchRequiresTtyRegistration, console.summarizeNotifierHandoff(.{
        .tty_registration_ready = false,
        .sysrq_dispatch_requested = true,
        .notifier_target_present = true,
    }));

    _ = console.teardown();
    try std.testing.expectError(error.ConsoleUnavailable, console.summarizeNotifierHandoff(.{}));
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
