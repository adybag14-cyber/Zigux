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

test "phase11 hvc_console adds carriage returns and keeps final flush intent on successful writes" {
    var console = try hvc_console.HvcConsoleLab.init(1);
    const slot = console.instantiate(0x41);
    try std.testing.expect(slot.adapter_present);
    try std.testing.expect(slot.usable_for_console);

    const write = try console.stageWrite("boot\nok\n", 9);
    try std.testing.expectEqual(@as(usize, 10), write.framed_len);
    try std.testing.expectEqualStrings("boot\r\nok\r\n", write.framed[0..write.framed_len]);
    try std.testing.expectEqual(@as(usize, 1), write.remaining_len);
    try std.testing.expectEqualStrings("\n", write.remaining[0..write.remaining_len]);
    try std.testing.expectEqual(hvc_console.FlushIntent.final_drain, write.flush_intent);
    try std.testing.expect(write.final_flush);
    try std.testing.expect(!write.dropped_on_error);
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
    try std.testing.expect(write.final_flush);
    try std.testing.expect(!write.dropped_on_error);

    write = try console.stageWrite("fatal\n", -5);
    try std.testing.expectEqual(@as(usize, 7), write.framed_len);
    try std.testing.expectEqual(@as(usize, 0), write.remaining_len);
    try std.testing.expectEqual(hvc_console.FlushIntent.none, write.flush_intent);
    try std.testing.expect(write.final_flush);
    try std.testing.expect(write.dropped_on_error);

    const teardown = console.teardown();
    try std.testing.expectEqual(hvc_console.removed_vtermno, teardown.vtermno);
    try std.testing.expect(!teardown.adapter_present);
    try std.testing.expect(!teardown.usable_for_console);
    try std.testing.expectError(error.ConsoleUnavailable, console.stageWrite("gone\n", 6));
}
