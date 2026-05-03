const std = @import("std");
const hvc_console = @import("hvc_console");

test "phase11 hvc console keeps tiocmget and tiocmset fallback on missing hv_ops callbacks" {
    var console = try hvc_console.HvcConsoleLab.init(6);
    _ = console.instantiate(0x66);

    const summary = try console.summarizeModemControl(.{
        .set_mask = 0x10,
        .clear_mask = 0x20,
    });
    try std.testing.expectEqual(@as(usize, 6), summary.slot_index);
    try std.testing.expectEqual(@as(u32, 0x66), summary.vtermno);
    try std.testing.expect(summary.adapter_present);
    try std.testing.expect(!summary.tiocmget_present);
    try std.testing.expect(!summary.tiocmget_routes_hp_directly);
    try std.testing.expect(summary.tiocmget_returns_einval_fallback);
    try std.testing.expectEqual(hvc_console.einval, summary.tiocmget_result);
    try std.testing.expect(!summary.tiocmset_present);
    try std.testing.expect(!summary.tiocmset_routes_hp_directly);
    try std.testing.expect(summary.tiocmset_returns_einval_fallback);
    try std.testing.expectEqual(hvc_console.einval, summary.tiocmset_result);
    try std.testing.expectEqual(@as(c_uint, 0x10), summary.set_mask);
    try std.testing.expectEqual(@as(c_uint, 0x20), summary.clear_mask);
    try std.testing.expect(!summary.set_mask_passthrough);
    try std.testing.expect(!summary.clear_mask_passthrough);
}

test "phase11 hvc console keeps tiocmset masks and callback results reviewable" {
    var console = try hvc_console.HvcConsoleLab.init(7);
    _ = console.instantiate(0x77);

    const summary = try console.summarizeModemControl(.{
        .tiocmget_present = true,
        .tiocmget_result = 0x1234,
        .tiocmset_present = true,
        .tiocmset_result = 0,
        .set_mask = 0x55,
        .clear_mask = 0xaa,
    });
    try std.testing.expect(summary.tiocmget_present);
    try std.testing.expect(summary.tiocmget_routes_hp_directly);
    try std.testing.expect(!summary.tiocmget_returns_einval_fallback);
    try std.testing.expectEqual(@as(c_int, 0x1234), summary.tiocmget_result);
    try std.testing.expect(summary.tiocmset_present);
    try std.testing.expect(summary.tiocmset_routes_hp_directly);
    try std.testing.expect(!summary.tiocmset_returns_einval_fallback);
    try std.testing.expectEqual(@as(c_int, 0), summary.tiocmset_result);
    try std.testing.expectEqual(@as(c_uint, 0x55), summary.set_mask);
    try std.testing.expectEqual(@as(c_uint, 0xaa), summary.clear_mask);
    try std.testing.expect(summary.set_mask_passthrough);
    try std.testing.expect(summary.clear_mask_passthrough);
}

test "phase11 hvc console keeps tiocmget direct while tiocmset falls back independently" {
    var console = try hvc_console.HvcConsoleLab.init(8);
    _ = console.instantiate(0x88);

    const summary = try console.summarizeModemControl(.{
        .tiocmget_present = true,
        .tiocmget_result = 0x44,
        .set_mask = 0x40,
        .clear_mask = 0x04,
    });
    try std.testing.expect(summary.tiocmget_present);
    try std.testing.expect(summary.tiocmget_routes_hp_directly);
    try std.testing.expect(!summary.tiocmget_returns_einval_fallback);
    try std.testing.expectEqual(@as(c_int, 0x44), summary.tiocmget_result);
    try std.testing.expect(!summary.tiocmset_present);
    try std.testing.expect(!summary.tiocmset_routes_hp_directly);
    try std.testing.expect(summary.tiocmset_returns_einval_fallback);
    try std.testing.expectEqual(hvc_console.einval, summary.tiocmset_result);
    try std.testing.expectEqual(@as(c_uint, 0x40), summary.set_mask);
    try std.testing.expectEqual(@as(c_uint, 0x04), summary.clear_mask);
    try std.testing.expect(!summary.set_mask_passthrough);
    try std.testing.expect(!summary.clear_mask_passthrough);
}

test "phase11 hvc console keeps tiocmset masks live when tiocmget falls back" {
    var console = try hvc_console.HvcConsoleLab.init(9);
    _ = console.instantiate(0x99);

    const summary = try console.summarizeModemControl(.{
        .tiocmset_present = true,
        .tiocmset_result = -7,
        .set_mask = 0x0f,
        .clear_mask = 0xf0,
    });
    try std.testing.expect(!summary.tiocmget_present);
    try std.testing.expect(!summary.tiocmget_routes_hp_directly);
    try std.testing.expect(summary.tiocmget_returns_einval_fallback);
    try std.testing.expectEqual(hvc_console.einval, summary.tiocmget_result);
    try std.testing.expect(summary.tiocmset_present);
    try std.testing.expect(summary.tiocmset_routes_hp_directly);
    try std.testing.expect(!summary.tiocmset_returns_einval_fallback);
    try std.testing.expectEqual(@as(c_int, -7), summary.tiocmset_result);
    try std.testing.expectEqual(@as(c_uint, 0x0f), summary.set_mask);
    try std.testing.expectEqual(@as(c_uint, 0xf0), summary.clear_mask);
    try std.testing.expect(summary.set_mask_passthrough);
    try std.testing.expect(summary.clear_mask_passthrough);
}

test "phase11 hvc console keeps modem-control teardown fallout unavailable after slot removal" {
    var console = try hvc_console.HvcConsoleLab.init(10);
    _ = console.instantiate(0xaa);

    const teardown = console.teardown();
    try std.testing.expectEqual(hvc_console.removed_vtermno, teardown.vtermno);
    try std.testing.expect(!teardown.adapter_present);
    try std.testing.expect(!teardown.usable_for_console);
    try std.testing.expectError(error.ConsoleUnavailable, console.summarizeModemControl(.{
        .tiocmget_present = true,
        .tiocmget_result = 1,
        .tiocmset_present = true,
        .tiocmset_result = 0,
        .set_mask = 0x01,
        .clear_mask = 0x02,
    }));
}
