const std = @import("std");
const hvc_console = @import("hvc_console");

fn slotTable(index: usize, vtermno: u32) [hvc_console.max_nr_hvc_consoles]hvc_console.ConsoleSlot {
    var slots = [_]hvc_console.ConsoleSlot{.{}} ** hvc_console.max_nr_hvc_consoles;
    slots[index] = .{
        .adapter_present = true,
        .vtermno = vtermno,
    };
    return slots;
}

test "phase11 hvc_console exposes the bounded descriptor and validates console slots" {
    const descriptor = hvc_console.HvcConsoleLab.descriptor();
    try std.testing.expectEqualStrings("hvc_console_lab", descriptor.name);
    try std.testing.expectEqualStrings("drivers/tty/hvc/hvc_console.c", descriptor.anchor);
    try std.testing.expect(descriptor.provides_simple_driver_starter);
    try std.testing.expect(!descriptor.touches_tty_registration);
    try std.testing.expect(!descriptor.touches_polling_kthread);
    try std.testing.expect(!descriptor.touches_live_hypervisor_io);

    var slots = slotTable(2, 0x2002);
    const snapshot = try hvc_console.HvcConsoleLab.validateConsoleSlot(2, slots[0..]);
    try std.testing.expectEqual(@as(usize, 2), snapshot.index);
    try std.testing.expect(snapshot.adapter_present);
    try std.testing.expectEqual(@as(u32, 0x2002), snapshot.vtermno);

    try std.testing.expectError(
        error.ConsoleIndexOutOfRange,
        hvc_console.HvcConsoleLab.validateConsoleSlot(-1, slots[0..]),
    );

    slots[2] = .{};
    try std.testing.expectError(
        error.ConsoleAdapterUnavailable,
        hvc_console.HvcConsoleLab.validateConsoleSlot(2, slots[0..]),
    );
}

test "phase11 hvc_console inserts carriage returns only where the Linux console path would" {
    const slots = slotTable(0, 7);
    var trace = try hvc_console.HvcConsoleLab.writeConsoleMessage(
        std.testing.allocator,
        0,
        slots[0..],
        "hello\nworld\r\n",
        &.{},
    );
    defer trace.deinit(std.testing.allocator);

    try std.testing.expectEqualStrings("hello\r\nworld\r\n", trace.framed_output);
    try std.testing.expectEqual(@as(usize, 14), trace.written_bytes);
    try std.testing.expectEqual(@as(usize, 0), trace.dropped_bytes);
    try std.testing.expectEqual(@as(usize, 1), trace.chunk_count);
    try std.testing.expectEqual(@as(usize, 1), trace.flush_calls);
    try std.testing.expectEqual(@as(usize, 0), trace.retry_flushes);
}

test "phase11 hvc_console records retry flush intent when put_chars would return EAGAIN" {
    const slots = slotTable(1, 0x44);
    var trace = try hvc_console.HvcConsoleLab.writeConsoleMessage(
        std.testing.allocator,
        1,
        slots[0..],
        "123456789012345\nZ",
        &.{ hvc_console.eagain, 16, 2 },
    );
    defer trace.deinit(std.testing.allocator);

    try std.testing.expectEqualStrings("123456789012345\r\nZ", trace.framed_output);
    try std.testing.expectEqual(@as(usize, 2), trace.chunk_count);
    try std.testing.expectEqual(@as(usize, 18), trace.written_bytes);
    try std.testing.expectEqual(@as(usize, 0), trace.dropped_bytes);
    try std.testing.expectEqual(@as(usize, 2), trace.flush_calls);
    try std.testing.expectEqual(@as(usize, 1), trace.retry_flushes);
}

test "phase11 hvc_console keeps adapter gating ahead of write framing" {
    const slots = [_]hvc_console.ConsoleSlot{.{}} ** hvc_console.max_nr_hvc_consoles;
    try std.testing.expectError(
        error.ConsoleAdapterUnavailable,
        hvc_console.HvcConsoleLab.writeConsoleMessage(
            std.testing.allocator,
            0,
            slots[0..],
            "ignored\n",
            &.{},
        ),
    );
}
