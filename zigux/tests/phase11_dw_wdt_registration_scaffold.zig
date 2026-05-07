const std = @import("std");
const dw_wdt = @import("dw_wdt");

test "platform handoff marks imported running state as ready-to-register when drvdata exists" {
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

    try std.testing.expect(handoff.registration_ready);
    try std.testing.expectEqual(dw_wdt.RegistrationScaffoldState.import_running_state_then_register, handoff.registration_state);
    try std.testing.expect(handoff.preserves_pretimeout_irq);
    try std.testing.expect(handoff.imported_running_state);
    try std.testing.expect(!handoff.needs_timeout_programming);
    try std.testing.expectEqual(@as(u32, 8), handoff.pretimeout_sec);
}

test "platform handoff stays registration-ready when irq wiring is absent but pretimeout is flattened" {
    var watchdog = try dw_wdt.DwWdtLab.initFixedTops(65_536, true);
    _ = watchdog.loadRegisters(.{
        .control = dw_wdt.control_reg_wdt_en_mask | dw_wdt.control_reg_resp_mode_mask,
        .timeout_range = 0x33,
        .current_count = 2 * 65_536,
    });

    const handoff = try watchdog.platformHandoffSummary(.{
        .nowayout = false,
        .stop_on_reboot = true,
    }, true, false, true);

    try std.testing.expect(handoff.registration_ready);
    try std.testing.expectEqual(dw_wdt.RegistrationScaffoldState.import_running_state_then_register, handoff.registration_state);
    try std.testing.expect(!handoff.preserves_pretimeout_irq);
    try std.testing.expect(handoff.imported_running_state);
    try std.testing.expectEqual(@as(u32, 0), handoff.pretimeout_sec);
}

test "platform handoff marks default-selection path as timeout-programming before registration" {
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
    }, true, false, true);

    try std.testing.expect(handoff.registration_ready);
    try std.testing.expectEqual(dw_wdt.RegistrationScaffoldState.program_timeout_then_register, handoff.registration_state);
    try std.testing.expect(!handoff.preserves_pretimeout_irq);
    try std.testing.expect(!handoff.imported_running_state);
    try std.testing.expect(handoff.needs_timeout_programming);
    try std.testing.expectEqual(@as(u32, 12), handoff.timeout_sec);
}

test "platform handoff stays blocked when drvdata publication is missing" {
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

    try std.testing.expect(!handoff.registration_ready);
    try std.testing.expectEqual(dw_wdt.RegistrationScaffoldState.blocked_missing_drvdata, handoff.registration_state);
    try std.testing.expect(!handoff.preserves_pretimeout_irq);
    try std.testing.expect(!handoff.drvdata_ready);
    try std.testing.expect(handoff.needs_timeout_programming);
}
