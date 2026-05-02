const std = @import("std");
const hvc_console = @import("hvc_console");
const hvc_console_sysrq = @import("../../drivers/tty/hvc/hvc_console_sysrq.zig");

test "phase11 hvc console keeps irq-backed drained reads distinct when __hvc_poll can or cannot sleep" {
    var console = try hvc_console.HvcConsoleLab.init(15);
    _ = console.instantiate(0xf0);

    const drained_without_sleep = try console.summarizePollDrainOrder(.{
        .contract = .{
            .close = .{
                .open_count_before_close = 1,
            },
        },
        .irq_requested = true,
        .read_result = 2,
    });
    try std.testing.expectEqual(@as(usize, 15), drained_without_sleep.slot_index);
    try std.testing.expectEqual(@as(u32, 0xf0), drained_without_sleep.vtermno);
    try std.testing.expect(drained_without_sleep.adapter_present);
    try std.testing.expect(!drained_without_sleep.releases_lock_before_read_retry);
    try std.testing.expect(!drained_without_sleep.read_poll_armed_without_irq);
    try std.testing.expect(drained_without_sleep.read_poll_pending_after_drain);
    try std.testing.expect(!drained_without_sleep.read_hangup_pending);
    try std.testing.expectEqual(@as(usize, 2), drained_without_sleep.read_bytes_drained);
    try std.testing.expect(!drained_without_sleep.wakeup_before_unlock);
    try std.testing.expect(drained_without_sleep.flip_push_after_unlock);
    try std.testing.expect(!drained_without_sleep.wakeup_precedes_flip_push);
    try std.testing.expect(drained_without_sleep.backend_handoff_pending);

    const drained_with_sleep = try console.summarizePollDrainOrder(.{
        .contract = .{
            .close = .{
                .open_count_before_close = 1,
            },
        },
        .may_sleep = true,
        .irq_requested = true,
        .read_result = 2,
    });
    try std.testing.expectEqual(@as(usize, 15), drained_with_sleep.slot_index);
    try std.testing.expectEqual(@as(u32, 0xf0), drained_with_sleep.vtermno);
    try std.testing.expect(drained_with_sleep.adapter_present);
    try std.testing.expect(drained_with_sleep.releases_lock_before_read_retry);
    try std.testing.expect(!drained_with_sleep.read_poll_armed_without_irq);
    try std.testing.expect(!drained_with_sleep.read_poll_pending_after_drain);
    try std.testing.expect(!drained_with_sleep.read_hangup_pending);
    try std.testing.expectEqual(@as(usize, 2), drained_with_sleep.read_bytes_drained);
    try std.testing.expect(!drained_with_sleep.wakeup_before_unlock);
    try std.testing.expect(drained_with_sleep.flip_push_after_unlock);
    try std.testing.expect(!drained_with_sleep.wakeup_precedes_flip_push);
    try std.testing.expect(drained_with_sleep.backend_handoff_pending);
}

test "phase11 hvc console keeps may-sleep drained reads retry-armed when irq delivery is unavailable" {
    var console = try hvc_console.HvcConsoleLab.init(4);
    _ = console.instantiate(0x44);

    const irq_free_drained = try console.summarizePollDrainOrder(.{
        .contract = .{
            .close = .{
                .open_count_before_close = 1,
            },
        },
        .may_sleep = true,
        .read_result = 2,
    });
    try std.testing.expectEqual(@as(usize, 4), irq_free_drained.slot_index);
    try std.testing.expectEqual(@as(u32, 0x44), irq_free_drained.vtermno);
    try std.testing.expect(irq_free_drained.adapter_present);
    try std.testing.expect(irq_free_drained.releases_lock_before_read_retry);
    try std.testing.expect(irq_free_drained.tty_required_for_read_path);
    try std.testing.expect(irq_free_drained.read_poll_armed_without_irq);
    try std.testing.expect(irq_free_drained.read_poll_pending_after_drain);
    try std.testing.expect(!irq_free_drained.read_hangup_pending);
    try std.testing.expectEqual(@as(usize, 2), irq_free_drained.read_bytes_drained);
    try std.testing.expect(!irq_free_drained.wakeup_before_unlock);
    try std.testing.expect(irq_free_drained.flip_push_after_unlock);
    try std.testing.expect(!irq_free_drained.wakeup_precedes_flip_push);
    try std.testing.expect(irq_free_drained.backend_handoff_pending);

    const irq_backed_drained = try console.summarizePollDrainOrder(.{
        .contract = .{
            .close = .{
                .open_count_before_close = 1,
            },
        },
        .may_sleep = true,
        .irq_requested = true,
        .read_result = 2,
    });
    try std.testing.expectEqual(@as(usize, 4), irq_backed_drained.slot_index);
    try std.testing.expectEqual(@as(u32, 0x44), irq_backed_drained.vtermno);
    try std.testing.expect(irq_backed_drained.adapter_present);
    try std.testing.expect(irq_backed_drained.releases_lock_before_read_retry);
    try std.testing.expect(irq_backed_drained.tty_required_for_read_path);
    try std.testing.expect(!irq_backed_drained.read_poll_armed_without_irq);
    try std.testing.expect(!irq_backed_drained.read_poll_pending_after_drain);
    try std.testing.expect(!irq_backed_drained.read_hangup_pending);
    try std.testing.expectEqual(@as(usize, 2), irq_backed_drained.read_bytes_drained);
    try std.testing.expect(!irq_backed_drained.wakeup_before_unlock);
    try std.testing.expect(irq_backed_drained.flip_push_after_unlock);
    try std.testing.expect(!irq_backed_drained.wakeup_precedes_flip_push);
    try std.testing.expect(irq_backed_drained.backend_handoff_pending);
}

test "phase11 hvc console keeps partial write progress distinct from stalled __hvc_poll retries" {
    var console = try hvc_console.HvcConsoleLab.init(14);
    _ = console.instantiate(0xe0);

    const partial_write = try console.summarizePollDrainOrder(.{
        .contract = .{
            .close = .{
                .open_count_before_close = 1,
            },
        },
        .irq_requested = true,
        .buffered_write_len = 6,
        .write_result = 2,
    });
    try std.testing.expectEqual(@as(usize, 14), partial_write.slot_index);
    try std.testing.expectEqual(@as(u32, 0xe0), partial_write.vtermno);
    try std.testing.expect(partial_write.adapter_present);
    try std.testing.expect(partial_write.write_drain_attempted);
    try std.testing.expectEqual(@as(usize, 4), partial_write.write_remaining_len);
    try std.testing.expect(partial_write.write_poll_pending_after_drain);
    try std.testing.expect(partial_write.write_progress_resets_timeout);
    try std.testing.expect(!partial_write.stalled_write_uses_min_timeout);
    try std.testing.expect(!partial_write.releases_lock_before_read_retry);
    try std.testing.expect(partial_write.tty_required_for_read_path);
    try std.testing.expect(!partial_write.read_poll_armed_without_irq);
    try std.testing.expect(!partial_write.read_poll_pending_after_drain);
    try std.testing.expect(!partial_write.read_hangup_pending);
    try std.testing.expectEqual(@as(usize, 0), partial_write.read_bytes_drained);
    try std.testing.expect(!partial_write.wakeup_before_unlock);
    try std.testing.expect(!partial_write.flip_push_after_unlock);
    try std.testing.expect(!partial_write.wakeup_precedes_flip_push);
    try std.testing.expect(partial_write.backend_handoff_pending);

    const stalled_write = try console.summarizePollDrainOrder(.{
        .contract = .{
            .close = .{
                .open_count_before_close = 1,
            },
        },
        .irq_requested = true,
        .buffered_write_len = 6,
        .write_result = 0,
    });
    try std.testing.expectEqual(@as(usize, 6), stalled_write.write_remaining_len);
    try std.testing.expect(stalled_write.write_poll_pending_after_drain);
    try std.testing.expect(!stalled_write.write_progress_resets_timeout);
    try std.testing.expect(stalled_write.stalled_write_uses_min_timeout);
    try std.testing.expect(stalled_write.wakeup_before_unlock);
    try std.testing.expect(stalled_write.backend_handoff_pending);
}

test "phase11 hvc console keeps attached fatal write drops distinct from detached fatal drains" {
    var console = try hvc_console.HvcConsoleLab.init(2);
    _ = console.instantiate(0x22);

    const attached_drop = try console.summarizePollDrainOrder(.{
        .contract = .{
            .close = .{
                .open_count_before_close = 1,
            },
        },
        .buffered_write_len = 4,
        .write_result = -5,
    });
    try std.testing.expectEqual(@as(usize, 2), attached_drop.slot_index);
    try std.testing.expectEqual(@as(u32, 0x22), attached_drop.vtermno);
    try std.testing.expect(attached_drop.adapter_present);
    try std.testing.expect(attached_drop.write_drain_attempted);
    try std.testing.expectEqual(@as(usize, 0), attached_drop.write_remaining_len);
    try std.testing.expect(!attached_drop.write_poll_pending_after_drain);
    try std.testing.expect(!attached_drop.write_progress_resets_timeout);
    try std.testing.expect(!attached_drop.stalled_write_uses_min_timeout);
    try std.testing.expect(attached_drop.tty_required_for_read_path);
    try std.testing.expect(attached_drop.read_poll_armed_without_irq);
    try std.testing.expect(attached_drop.read_poll_pending_after_drain);
    try std.testing.expect(!attached_drop.read_hangup_pending);
    try std.testing.expectEqual(@as(usize, 0), attached_drop.read_bytes_drained);
    try std.testing.expect(attached_drop.wakeup_before_unlock);
    try std.testing.expect(!attached_drop.flip_push_after_unlock);
    try std.testing.expect(!attached_drop.wakeup_precedes_flip_push);
    try std.testing.expect(attached_drop.backend_handoff_pending);

    const detached_drop = try console.summarizePollDrainOrder(.{
        .contract = .{
            .close = .{
                .open_count_before_close = 1,
            },
        },
        .tty_attached = false,
        .buffered_write_len = 4,
        .write_result = -5,
    });
    try std.testing.expectEqual(@as(usize, 2), detached_drop.slot_index);
    try std.testing.expectEqual(@as(u32, 0x22), detached_drop.vtermno);
    try std.testing.expect(detached_drop.adapter_present);
    try std.testing.expect(detached_drop.write_drain_attempted);
    try std.testing.expectEqual(@as(usize, 0), detached_drop.write_remaining_len);
    try std.testing.expect(!detached_drop.write_poll_pending_after_drain);
    try std.testing.expect(!detached_drop.write_progress_resets_timeout);
    try std.testing.expect(!detached_drop.stalled_write_uses_min_timeout);
    try std.testing.expect(!detached_drop.tty_required_for_read_path);
    try std.testing.expect(!detached_drop.read_poll_armed_without_irq);
    try std.testing.expect(!detached_drop.read_poll_pending_after_drain);
    try std.testing.expect(!detached_drop.read_hangup_pending);
    try std.testing.expectEqual(@as(usize, 0), detached_drop.read_bytes_drained);
    try std.testing.expect(!detached_drop.wakeup_before_unlock);
    try std.testing.expect(!detached_drop.flip_push_after_unlock);
    try std.testing.expect(!detached_drop.wakeup_precedes_flip_push);
    try std.testing.expect(detached_drop.backend_handoff_pending);
}

test "phase11 hvc console keeps fully drained writes waking the tty without a preexisting wakeup flag" {
    var console = try hvc_console.HvcConsoleLab.init(3);
    _ = console.instantiate(0x33);

    const drained_write = try console.summarizePollDrainOrder(.{
        .contract = .{
            .close = .{
                .open_count_before_close = 1,
            },
        },
        .irq_requested = true,
        .buffered_write_len = 5,
        .write_result = 5,
    });
    try std.testing.expectEqual(@as(usize, 3), drained_write.slot_index);
    try std.testing.expectEqual(@as(u32, 0x33), drained_write.vtermno);
    try std.testing.expect(drained_write.adapter_present);
    try std.testing.expect(drained_write.write_drain_precedes_read_path);
    try std.testing.expect(drained_write.write_drain_attempted);
    try std.testing.expectEqual(@as(usize, 0), drained_write.write_remaining_len);
    try std.testing.expect(!drained_write.write_poll_pending_after_drain);
    try std.testing.expect(!drained_write.write_progress_resets_timeout);
    try std.testing.expect(!drained_write.stalled_write_uses_min_timeout);
    try std.testing.expect(!drained_write.releases_lock_before_read_retry);
    try std.testing.expect(drained_write.tty_required_for_read_path);
    try std.testing.expect(!drained_write.read_poll_armed_without_irq);
    try std.testing.expect(!drained_write.read_poll_pending_after_drain);
    try std.testing.expect(!drained_write.read_hangup_pending);
    try std.testing.expectEqual(@as(usize, 0), drained_write.read_bytes_drained);
    try std.testing.expect(drained_write.wakeup_before_unlock);
    try std.testing.expect(!drained_write.flip_push_after_unlock);
    try std.testing.expect(!drained_write.wakeup_precedes_flip_push);
    try std.testing.expect(drained_write.backend_handoff_pending);
}

test "phase11 hvc console keeps sysrq toggle handoff distinct from literal fallback on the primary console" {
    var console = try hvc_console.HvcConsoleLab.init(5);
    _ = console.instantiate(0x55);

    const enter_sysrq = try hvc_console_sysrq.summarizeSysrqHandoff(&console, .{
        .is_kernel_console = true,
        .sysrq_pressed_before = false,
        .input_char = 0x0f,
    });
    try std.testing.expectEqual(@as(usize, 5), enter_sysrq.slot_index);
    try std.testing.expectEqual(@as(u32, 0x55), enter_sysrq.vtermno);
    try std.testing.expect(enter_sysrq.adapter_present);
    try std.testing.expect(enter_sysrq.is_kernel_console);
    try std.testing.expect(!enter_sysrq.sysrq_pressed_before);
    try std.testing.expectEqual(@as(u8, 0x0f), enter_sysrq.input_char);
    try std.testing.expect(enter_sysrq.toggles_sysrq_mode);
    try std.testing.expect(enter_sysrq.sysrq_pressed_after);
    try std.testing.expect(!enter_sysrq.invokes_sysrq_handler);
    try std.testing.expect(!enter_sysrq.clears_sysrq_after_handler);
    try std.testing.expect(!enter_sysrq.emits_literal_char);
    try std.testing.expect(enter_sysrq.consumes_input_without_flip);
    try std.testing.expect(enter_sysrq.keeps_tty_registration_out_of_scope);
    try std.testing.expect(enter_sysrq.keeps_live_hypervisor_io_out_of_scope);
    try std.testing.expect(enter_sysrq.keeps_live_sysrq_execution_out_of_scope);

    const exit_sysrq = try hvc_console_sysrq.summarizeSysrqHandoff(&console, .{
        .is_kernel_console = true,
        .sysrq_pressed_before = true,
        .input_char = 0x0f,
    });
    try std.testing.expect(exit_sysrq.toggles_sysrq_mode);
    try std.testing.expect(!exit_sysrq.sysrq_pressed_after);
    try std.testing.expect(!exit_sysrq.invokes_sysrq_handler);
    try std.testing.expect(!exit_sysrq.clears_sysrq_after_handler);
    try std.testing.expect(exit_sysrq.emits_literal_char);
    try std.testing.expect(!exit_sysrq.consumes_input_without_flip);
}

test "phase11 hvc console keeps pending sysrq dispatch separate from ordinary poll bytes" {
    var console = try hvc_console.HvcConsoleLab.init(6);
    _ = console.instantiate(0x66);

    const dispatch = try hvc_console_sysrq.summarizeSysrqHandoff(&console, .{
        .is_kernel_console = true,
        .sysrq_pressed_before = true,
        .input_char = 'x',
    });
    try std.testing.expect(dispatch.is_kernel_console);
    try std.testing.expect(dispatch.sysrq_pressed_before);
    try std.testing.expectEqual(@as(u8, 'x'), dispatch.input_char);
    try std.testing.expect(!dispatch.toggles_sysrq_mode);
    try std.testing.expect(!dispatch.sysrq_pressed_after);
    try std.testing.expect(dispatch.invokes_sysrq_handler);
    try std.testing.expect(dispatch.clears_sysrq_after_handler);
    try std.testing.expect(!dispatch.emits_literal_char);
    try std.testing.expect(dispatch.consumes_input_without_flip);

    const ordinary = try hvc_console_sysrq.summarizeSysrqHandoff(&console, .{
        .is_kernel_console = false,
        .sysrq_pressed_before = true,
        .input_char = 'x',
    });
    try std.testing.expect(!ordinary.is_kernel_console);
    try std.testing.expect(ordinary.sysrq_pressed_before);
    try std.testing.expectEqual(@as(u8, 'x'), ordinary.input_char);
    try std.testing.expect(!ordinary.toggles_sysrq_mode);
    try std.testing.expect(ordinary.sysrq_pressed_after);
    try std.testing.expect(!ordinary.invokes_sysrq_handler);
    try std.testing.expect(!ordinary.clears_sysrq_after_handler);
    try std.testing.expect(ordinary.emits_literal_char);
    try std.testing.expect(!ordinary.consumes_input_without_flip);
}
