const std = @import("std");
const hvc_console = @import("hvc_console");

test "phase11 hvc_console exposes the bounded descriptor and slot validation" {
    const descriptor = hvc_console.HvcConsoleLab.descriptor();
    try std.testing.expectEqualStrings("hvc_console_lab", descriptor.name);
    try std.testing.expectEqualStrings("drivers/tty/hvc/hvc_console.c", descriptor.anchor);
    try std.testing.expect(descriptor.provides_simple_driver_starter);
    try std.testing.expect(!descriptor.touches_tty_registration);
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

test "phase11 hvc console keeps a bounded header parity snapshot for the exported hvc surface" {
    const header = hvc_console.headerParitySnapshot();
    try std.testing.expectEqualStrings("drivers/tty/hvc/hvc_console.h", header.anchor);
    try std.testing.expectEqual(@as(usize, 16), header.max_nr_hvc_consoles);
    try std.testing.expectEqual(@as(usize, 8), header.alloc_tty_adapters);
    try std.testing.expect(header.exports_instantiate);
    try std.testing.expect(header.exports_alloc);
    try std.testing.expect(header.exports_remove);
    try std.testing.expect(header.exports_poll);
    try std.testing.expect(header.exports_resize);
    try std.testing.expect(header.hv_ops.has_get_chars);
    try std.testing.expect(header.hv_ops.has_put_chars);
    try std.testing.expect(header.hv_ops.has_flush);
    try std.testing.expect(header.hv_ops.has_notifier_add);
    try std.testing.expect(header.hv_ops.has_notifier_del);
    try std.testing.expect(header.hv_ops.has_notifier_hangup);
    try std.testing.expect(header.hv_ops.has_tiocmget);
    try std.testing.expect(header.hv_ops.has_tiocmset);
    try std.testing.expect(header.hv_ops.has_dtr_rts);
    try std.testing.expect(header.keeps_tty_registration_out_of_scope);
    try std.testing.expect(header.keeps_live_hypervisor_io_out_of_scope);
}

test "phase11 hvc console summarizes final-close wait boundaries without claiming tty registration" {
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

test "phase11 hvc console keeps tty-registration handoff and khvcd boundaries reviewable" {
    var console = try hvc_console.HvcConsoleLab.init(4);
    _ = console.instantiate(0x77);

    const final_handoff = try console.summarizeTtyRegistrationHandoff(.{
        .port_initialized = true,
        .open_count_before_close = 1,
    });
    try std.testing.expectEqual(@as(usize, 4), final_handoff.slot_index);
    try std.testing.expectEqual(@as(u32, 0x77), final_handoff.vtermno);
    try std.testing.expect(final_handoff.adapter_present);
    try std.testing.expect(final_handoff.setup_hvc_console_pending);
    try std.testing.expect(final_handoff.tty_registration_pending);
    try std.testing.expect(final_handoff.final_close_wait_required);
    try std.testing.expect(final_handoff.clears_port_initialized_on_final_close);
    try std.testing.expect(final_handoff.keeps_console_binding);
    try std.testing.expect(final_handoff.khvcd_kick_on_open);
    try std.testing.expect(final_handoff.khvcd_kick_on_unthrottle);
    try std.testing.expect(final_handoff.khvcd_polling_pending);
    try std.testing.expect(final_handoff.notifier_callbacks_pending);
    try std.testing.expect(final_handoff.host_io_pending);

    const non_final_handoff = try console.summarizeTtyRegistrationHandoff(.{
        .port_initialized = true,
        .open_count_before_close = 2,
    });
    try std.testing.expect(!non_final_handoff.final_close_wait_required);
    try std.testing.expect(!non_final_handoff.clears_port_initialized_on_final_close);

    try std.testing.expectError(error.InvalidOpenCount, console.summarizeTtyRegistrationHandoff(.{
        .open_count_before_close = 0,
    }));
}

test "phase11 hvc console keeps khvcd polling wakeups and teardown boundaries reviewable" {
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
    try std.testing.expect(active_poll.khvcd_polling_pending);
    try std.testing.expect(active_poll.notifier_driven_wakeup);
    try std.testing.expect(active_poll.poll_driven_wakeup);
    try std.testing.expect(active_poll.khvcd_wakeup_required);
    try std.testing.expect(active_poll.reschedule_required);
    try std.testing.expect(active_poll.notifier_add_pending);
    try std.testing.expect(!active_poll.notifier_del_pending);
    try std.testing.expect(active_poll.notifier_hangup_pending);
    try std.testing.expect(active_poll.read_poll_pending);
    try std.testing.expect(active_poll.write_poll_pending);
    try std.testing.expect(active_poll.teardown_host_io_pending);

    const idle_poll = try console.summarizeKhvcdPollingContract(.{
        .close = .{
            .port_initialized = false,
            .open_count_before_close = 2,
        },
    });
    try std.testing.expect(!idle_poll.final_close_wait_required);
    try std.testing.expect(!idle_poll.clears_port_initialized_on_final_close);
    try std.testing.expect(!idle_poll.notifier_driven_wakeup);
    try std.testing.expect(!idle_poll.poll_driven_wakeup);
    try std.testing.expect(idle_poll.khvcd_wakeup_required);
    try std.testing.expect(!idle_poll.reschedule_required);
    try std.testing.expect(idle_poll.teardown_host_io_pending);

    try std.testing.expectError(error.InvalidOpenCount, console.summarizeKhvcdPollingContract(.{
        .close = .{
            .open_count_before_close = 0,
        },
    }));
}

test "phase11 hvc console keeps khvcd worker-entry sleep and backoff boundaries reviewable" {
    var console = try hvc_console.HvcConsoleLab.init(6);
    _ = console.instantiate(0x66);

    const active_worker = try console.summarizeKhvcdWorkerEntry(.{
        .contract = .{
            .close = .{
                .port_initialized = true,
                .open_count_before_close = 1,
            },
            .notifier_add_pending = true,
            .read_poll_pending = true,
            .write_poll_pending = true,
        },
        .timeout_ms = hvc_console.min_khvcd_timeout_ms,
    });
    try std.testing.expectEqual(@as(usize, 6), active_worker.slot_index);
    try std.testing.expectEqual(@as(u32, 0x66), active_worker.vtermno);
    try std.testing.expect(active_worker.adapter_present);
    try std.testing.expect(active_worker.final_close_wait_required);
    try std.testing.expect(active_worker.clears_port_initialized_on_final_close);
    try std.testing.expect(active_worker.keeps_console_binding);
    try std.testing.expect(active_worker.tty_registration_pending);
    try std.testing.expect(active_worker.khvcd_polling_pending);
    try std.testing.expect(active_worker.notifier_driven_wakeup);
    try std.testing.expect(active_worker.poll_driven_wakeup);
    try std.testing.expect(active_worker.checks_freezer_before_poll_walk);
    try std.testing.expect(active_worker.resets_kick_before_poll_walk);
    try std.testing.expect(active_worker.walks_hvc_structs_under_mutex);
    try std.testing.expect(!active_worker.xmon_forces_read_poll);
    try std.testing.expect(active_worker.poll_read_pending);
    try std.testing.expect(active_worker.poll_write_pending);
    try std.testing.expect(active_worker.wakeup_on_kick);
    try std.testing.expect(!active_worker.skip_sleep_due_to_kick);
    try std.testing.expect(!active_worker.sleeps_without_timeout);
    try std.testing.expect(active_worker.timeout_backoff_active);
    try std.testing.expectEqual(@as(u32, 11), active_worker.sleep_timeout_ms);
    try std.testing.expect(!active_worker.timeout_capped_at_max);
    try std.testing.expect(active_worker.backend_handoff_pending);

    const xmon_worker = try console.summarizeKhvcdWorkerEntry(.{
        .contract = .{
            .close = .{
                .port_initialized = false,
                .open_count_before_close = 2,
            },
        },
        .cpus_in_xmon = true,
        .timeout_ms = 1999,
    });
    try std.testing.expect(!xmon_worker.walks_hvc_structs_under_mutex);
    try std.testing.expect(xmon_worker.xmon_forces_read_poll);
    try std.testing.expect(xmon_worker.poll_read_pending);
    try std.testing.expect(!xmon_worker.poll_write_pending);
    try std.testing.expect(!xmon_worker.skip_sleep_due_to_kick);
    try std.testing.expect(!xmon_worker.sleeps_without_timeout);
    try std.testing.expect(xmon_worker.timeout_backoff_active);
    try std.testing.expectEqual(hvc_console.max_khvcd_timeout_ms, xmon_worker.sleep_timeout_ms);
    try std.testing.expect(xmon_worker.timeout_capped_at_max);

    const kicked_worker = try console.summarizeKhvcdWorkerEntry(.{
        .contract = .{
            .close = .{
                .open_count_before_close = 1,
            },
        },
        .kick_pending_after_walk = true,
    });
    try std.testing.expect(kicked_worker.skip_sleep_due_to_kick);
    try std.testing.expect(!kicked_worker.sleeps_without_timeout);
    try std.testing.expect(!kicked_worker.timeout_backoff_active);
    try std.testing.expectEqual(@as(u32, 0), kicked_worker.sleep_timeout_ms);

    try std.testing.expectError(error.InvalidOpenCount, console.summarizeKhvcdWorkerEntry(.{
        .contract = .{
            .close = .{
                .open_count_before_close = 0,
            },
        },
    }));
}

test "phase11 hvc console keeps khvcd sleep-and-reschedule handoff boundaries reviewable" {
    var console = try hvc_console.HvcConsoleLab.init(8);
    _ = console.instantiate(0x80);

    const timed_sleep = try console.summarizeKhvcdSleepHandoff(.{
        .entry = .{
            .contract = .{
                .close = .{
                    .port_initialized = true,
                    .open_count_before_close = 1,
                },
                .read_poll_pending = true,
                .write_poll_pending = true,
            },
            .timeout_ms = hvc_console.min_khvcd_timeout_ms,
        },
    });
    try std.testing.expectEqual(@as(usize, 8), timed_sleep.slot_index);
    try std.testing.expectEqual(@as(u32, 0x80), timed_sleep.vtermno);
    try std.testing.expect(timed_sleep.adapter_present);
    try std.testing.expect(timed_sleep.final_close_wait_required);
    try std.testing.expect(timed_sleep.clears_port_initialized_on_final_close);
    try std.testing.expect(timed_sleep.keeps_console_binding);
    try std.testing.expect(timed_sleep.tty_registration_pending);
    try std.testing.expect(timed_sleep.khvcd_polling_pending);
    try std.testing.expect(timed_sleep.poll_read_pending);
    try std.testing.expect(timed_sleep.poll_write_pending);
    try std.testing.expect(timed_sleep.checks_kick_before_sleep_state);
    try std.testing.expect(!timed_sleep.kick_short_circuits_before_sleep_state);
    try std.testing.expect(timed_sleep.sets_interruptible_before_sleep_recheck);
    try std.testing.expect(timed_sleep.checks_kick_after_interruptible_state);
    try std.testing.expect(!timed_sleep.skip_schedule_due_to_post_state_kick);
    try std.testing.expect(!timed_sleep.schedule_without_timeout);
    try std.testing.expect(timed_sleep.schedule_timeout_interruptible);
    try std.testing.expect(timed_sleep.timeout_backoff_grows_before_timed_sleep);
    try std.testing.expectEqual(@as(u32, 11), timed_sleep.sleep_timeout_ms);
    try std.testing.expect(!timed_sleep.timeout_capped_at_max);
    try std.testing.expect(timed_sleep.timed_sleep_uses_guard_tick);
    try std.testing.expect(timed_sleep.restores_running_state_after_handoff);
    try std.testing.expect(timed_sleep.backend_handoff_pending);

    const untimed_sleep = try console.summarizeKhvcdSleepHandoff(.{
        .entry = .{
            .contract = .{
                .close = .{
                    .port_initialized = false,
                    .open_count_before_close = 2,
                },
            },
        },
    });
    try std.testing.expect(!untimed_sleep.poll_read_pending);
    try std.testing.expect(!untimed_sleep.poll_write_pending);
    try std.testing.expect(!untimed_sleep.kick_short_circuits_before_sleep_state);
    try std.testing.expect(untimed_sleep.sets_interruptible_before_sleep_recheck);
    try std.testing.expect(untimed_sleep.checks_kick_after_interruptible_state);
    try std.testing.expect(!untimed_sleep.skip_schedule_due_to_post_state_kick);
    try std.testing.expect(untimed_sleep.schedule_without_timeout);
    try std.testing.expect(!untimed_sleep.schedule_timeout_interruptible);
    try std.testing.expect(!untimed_sleep.timeout_backoff_grows_before_timed_sleep);
    try std.testing.expectEqual(@as(u32, 0), untimed_sleep.sleep_timeout_ms);
    try std.testing.expect(!untimed_sleep.timeout_capped_at_max);
    try std.testing.expect(!untimed_sleep.timed_sleep_uses_guard_tick);
    try std.testing.expect(untimed_sleep.restores_running_state_after_handoff);
    try std.testing.expect(untimed_sleep.backend_handoff_pending);

    const pre_state_kick = try console.summarizeKhvcdSleepHandoff(.{
        .entry = .{
            .contract = .{
                .close = .{
                    .open_count_before_close = 1,
                },
            },
            .kick_pending_after_walk = true,
        },
    });
    try std.testing.expect(pre_state_kick.checks_kick_before_sleep_state);
    try std.testing.expect(pre_state_kick.kick_short_circuits_before_sleep_state);
    try std.testing.expect(!pre_state_kick.sets_interruptible_before_sleep_recheck);
    try std.testing.expect(!pre_state_kick.checks_kick_after_interruptible_state);
    try std.testing.expect(!pre_state_kick.skip_schedule_due_to_post_state_kick);
    try std.testing.expect(!pre_state_kick.schedule_without_timeout);
    try std.testing.expect(!pre_state_kick.schedule_timeout_interruptible);
    try std.testing.expectEqual(@as(u32, 0), pre_state_kick.sleep_timeout_ms);
    try std.testing.expect(!pre_state_kick.restores_running_state_after_handoff);

    const post_state_kick = try console.summarizeKhvcdSleepHandoff(.{
        .entry = .{
            .contract = .{
                .close = .{
                    .open_count_before_close = 1,
                },
            },
        },
        .kick_pending_after_interruptible_state = true,
    });
    try std.testing.expect(post_state_kick.checks_kick_before_sleep_state);
    try std.testing.expect(!post_state_kick.kick_short_circuits_before_sleep_state);
    try std.testing.expect(post_state_kick.sets_interruptible_before_sleep_recheck);
    try std.testing.expect(post_state_kick.checks_kick_after_interruptible_state);
    try std.testing.expect(post_state_kick.skip_schedule_due_to_post_state_kick);
    try std.testing.expect(!post_state_kick.schedule_without_timeout);
    try std.testing.expect(!post_state_kick.schedule_timeout_interruptible);
    try std.testing.expectEqual(@as(u32, 0), post_state_kick.sleep_timeout_ms);
    try std.testing.expect(post_state_kick.restores_running_state_after_handoff);

    try std.testing.expectError(error.InvalidOpenCount, console.summarizeKhvcdSleepHandoff(.{
        .entry = .{
            .contract = .{
                .close = .{
                    .open_count_before_close = 0,
                },
            },
        },
    }));
}

test "phase11 hvc console keeps __hvc_poll drain ordering and wakeup boundaries reviewable" {
    var console = try hvc_console.HvcConsoleLab.init(7);
    _ = console.instantiate(0x70);

    const active_drain = try console.summarizePollDrainOrder(.{
        .contract = .{
            .close = .{
                .port_initialized = true,
                .open_count_before_close = 1,
            },
            .read_poll_pending = true,
            .write_poll_pending = true,
        },
        .buffered_write_len = 6,
        .write_result = 0,
        .read_result = 3,
    });
    try std.testing.expectEqual(@as(usize, 7), active_drain.slot_index);
    try std.testing.expectEqual(@as(u32, 0x70), active_drain.vtermno);
    try std.testing.expect(active_drain.adapter_present);
    try std.testing.expect(active_drain.final_close_wait_required);
    try std.testing.expect(active_drain.clears_port_initialized_on_final_close);
    try std.testing.expect(active_drain.keeps_console_binding);
    try std.testing.expect(active_drain.tty_registration_pending);
    try std.testing.expect(active_drain.write_drain_precedes_read_path);
    try std.testing.expect(active_drain.write_drain_attempted);
    try std.testing.expectEqual(@as(usize, 6), active_drain.write_remaining_len);
    try std.testing.expect(active_drain.write_poll_pending_after_drain);
    try std.testing.expect(!active_drain.write_progress_resets_timeout);
    try std.testing.expect(active_drain.stalled_write_uses_min_timeout);
    try std.testing.expect(!active_drain.releases_lock_before_read_retry);
    try std.testing.expect(active_drain.tty_required_for_read_path);
    try std.testing.expect(!active_drain.throttled_read_skipped);
    try std.testing.expect(active_drain.read_poll_armed_without_irq);
    try std.testing.expect(active_drain.read_poll_pending_after_drain);
    try std.testing.expect(!active_drain.read_hangup_pending);
    try std.testing.expectEqual(@as(usize, 3), active_drain.read_bytes_drained);
    try std.testing.expect(active_drain.wakeup_before_unlock);
    try std.testing.expect(active_drain.flip_push_after_unlock);
    try std.testing.expect(active_drain.wakeup_precedes_flip_push);
    try std.testing.expect(active_drain.backend_handoff_pending);

    const throttled_drain = try console.summarizePollDrainOrder(.{
        .contract = .{
            .close = .{
                .open_count_before_close = 2,
            },
        },
        .may_sleep = true,
        .tty_throttled = true,
        .buffered_write_len = 4,
        .write_result = 4,
        .read_result = hvc_console.epipe,
        .preexisting_do_wakeup = true,
    });
    try std.testing.expect(!throttled_drain.final_close_wait_required);
    try std.testing.expect(!throttled_drain.clears_port_initialized_on_final_close);
    try std.testing.expect(!throttled_drain.write_poll_pending_after_drain);
    try std.testing.expect(!throttled_drain.write_progress_resets_timeout);
    try std.testing.expect(!throttled_drain.stalled_write_uses_min_timeout);
    try std.testing.expect(throttled_drain.releases_lock_before_read_retry);
    try std.testing.expect(throttled_drain.tty_required_for_read_path);
    try std.testing.expect(throttled_drain.throttled_read_skipped);
    try std.testing.expect(!throttled_drain.read_poll_armed_without_irq);
    try std.testing.expect(!throttled_drain.read_poll_pending_after_drain);
    try std.testing.expect(!throttled_drain.read_hangup_pending);
    try std.testing.expectEqual(@as(usize, 0), throttled_drain.read_bytes_drained);
    try std.testing.expect(throttled_drain.wakeup_before_unlock);
    try std.testing.expect(!throttled_drain.flip_push_after_unlock);
    try std.testing.expect(!throttled_drain.wakeup_precedes_flip_push);

    const detached_drain = try console.summarizePollDrainOrder(.{
        .contract = .{
            .close = .{
                .open_count_before_close = 1,
            },
        },
        .tty_attached = false,
        .buffered_write_len = 2,
        .write_result = -5,
        .preexisting_do_wakeup = true,
    });
    try std.testing.expect(!detached_drain.tty_required_for_read_path);
    try std.testing.expect(!detached_drain.throttled_read_skipped);
    try std.testing.expect(!detached_drain.read_poll_armed_without_irq);
    try std.testing.expect(!detached_drain.read_poll_pending_after_drain);
    try std.testing.expect(!detached_drain.read_hangup_pending);
    try std.testing.expectEqual(@as(usize, 0), detached_drain.read_bytes_drained);
    try std.testing.expect(!detached_drain.wakeup_before_unlock);
    try std.testing.expect(!detached_drain.flip_push_after_unlock);
    try std.testing.expect(!detached_drain.wakeup_precedes_flip_push);
    try std.testing.expect(detached_drain.backend_handoff_pending);
}

test "phase11 hvc console adds carriage returns and keeps final flush intent on successful writes" {
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
}

test "phase11 hvc console keeps retry intent on zero-progress writes and eagain, then clears the slot on teardown" {
    var console = try hvc_console.HvcConsoleLab.init(0);
    _ = console.instantiate(0x99);

    var write = try console.stageWrite("x\n", 0);
    try std.testing.expectEqual(@as(usize, 3), write.framed_len);
    try std.testing.expectEqualStrings("x\r\n", write.framed[0..write.framed_len]);
    try std.testing.expectEqual(@as(usize, 3), write.remaining_len);
    try std.testing.expectEqualStrings("x\r\n", write.remaining[0..write.remaining_len]);
    try std.testing.expectEqual(hvc_console.FlushIntent.retry_after_eagain, write.flush_intent);
    try std.testing.expectEqual(hvc_console.FlushProgress.no_progress, write.flush_progress);
    try std.testing.expect(write.final_flush);
    try std.testing.expect(!write.dropped_on_error);

    write = try console.stageWrite("x\n", hvc_console.eagain);
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

    const teardown = console.teardown();
    try std.testing.expectEqual(hvc_console.removed_vtermno, teardown.vtermno);
    try std.testing.expect(!teardown.adapter_present);
    try std.testing.expect(!teardown.usable_for_console);
    try std.testing.expectError(error.ConsoleUnavailable, console.stageWrite("gone\n", 6));
}
