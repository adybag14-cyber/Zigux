const std = @import("std");
const hvc_console = @import("hvc_console");

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
