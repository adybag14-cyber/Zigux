const std = @import("std");
const dw_wdt = @import("dw_wdt.zig");

test "dw_wdt platform handoff keeps registration scaffolding explicit when irq wiring is ready" {
    var watchdog = try dw_wdt.DwWdtLab.initFixedTops(65_536, true);
    _ = watchdog.loadRegisters(.{
        .control = dw_wdt.control_reg_wdt_en_mask | dw_wdt.control_reg_resp_mode_mask,
        .timeout_range = 0x33,
        .current_count = 2 * 65_536,
    });

    const handoff = try watchdog.platformHandoffSummary(.{
        .nowayout = false,
        .stop_on_reboot = true,
    }, true, true, true);

    try std.testing.expectEqualStrings("drivers/watchdog/dw_wdt.c", handoff.anchor);
    try std.testing.expectEqualStrings("watchdog_register_device", handoff.registration_call);
    try std.testing.expectEqualStrings("platform_device.dev", handoff.parent_anchor);
    try std.testing.expectEqualStrings("platform_set_drvdata", handoff.drvdata_anchor);
    try std.testing.expectEqual(dw_wdt.TopSource.fixed, handoff.top_source);
    try std.testing.expectEqual(dw_wdt.ProbeTimeoutOrigin.imported_running_state, handoff.timeout_origin);
    try std.testing.expectEqual(@as(u32, 65_536), handoff.rate_hz);
    try std.testing.expect(handoff.reset_control_available);
    try std.testing.expect(handoff.irq_registration_ready);
    try std.testing.expect(handoff.drvdata_ready);
    try std.testing.expect(!handoff.nowayout);
    try std.testing.expectEqual(dw_wdt.default_restart_priority, handoff.restart_priority);
    try std.testing.expect(handoff.stop_on_reboot);
    try std.testing.expect(handoff.can_stop);
    try std.testing.expectEqual(@as(u32, 16), handoff.timeout_sec);
    try std.testing.expectEqual(@as(u32, 8), handoff.pretimeout_sec);
    try std.testing.expect(handoff.imported_running_state);
    try std.testing.expect(!handoff.needs_timeout_programming);
}

test "dw_wdt platform handoff stays blocked-but-reviewable when drvdata or irq wiring is absent" {
    var watchdog = try dw_wdt.DwWdtLab.initCustomTops(1_000, false, [_]u32{
        20_000, 4_000,  8_000,  12_000,
        16_000, 24_000, 28_000, 32_000,
        36_000, 40_000, 44_000, 48_000,
        52_000, 56_000, 60_000, 64_000,
    });

    const handoff = try watchdog.platformHandoffSummary(.{
        .nowayout = true,
        .requested_timeout_sec = 11,
        .stop_on_reboot = true,
    }, true, false, false);

    try std.testing.expectEqual(dw_wdt.TopSource.custom, handoff.top_source);
    try std.testing.expectEqual(dw_wdt.ProbeTimeoutOrigin.default_selection, handoff.timeout_origin);
    try std.testing.expectEqual(@as(u32, 1_000), handoff.rate_hz);
    try std.testing.expect(!handoff.reset_control_available);
    try std.testing.expect(!handoff.irq_registration_ready);
    try std.testing.expect(!handoff.drvdata_ready);
    try std.testing.expect(handoff.nowayout);
    try std.testing.expect(handoff.stop_on_reboot);
    try std.testing.expect(!handoff.can_stop);
    try std.testing.expectEqual(@as(u32, 12), handoff.timeout_sec);
    try std.testing.expectEqual(@as(u32, 0), handoff.pretimeout_sec);
    try std.testing.expect(!handoff.imported_running_state);
    try std.testing.expect(handoff.needs_timeout_programming);
}
