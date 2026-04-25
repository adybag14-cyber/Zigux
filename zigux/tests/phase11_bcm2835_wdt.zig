const std = @import("std");
const bcm2835_wdt = @import("bcm2835_wdt");

test "phase11 bcm2835_wdt reports bounded timeout limits and descriptor state" {
    const descriptor = bcm2835_wdt.Bcm2835WatchdogLab.descriptor();
    try std.testing.expectEqualStrings("bcm2835_wdt_lab", descriptor.name);
    try std.testing.expectEqualStrings("drivers/watchdog/bcm2835_wdt.c", descriptor.anchor);
    try std.testing.expect(descriptor.provides_simple_driver_starter);
    try std.testing.expect(!descriptor.touches_platform_registration);
    try std.testing.expect(!descriptor.touches_poweroff_plumbing);

    try std.testing.expectEqual(@as(u32, 15), bcm2835_wdt.max_timeout_sec);
    try std.testing.expectEqual(@as(u32, 15_999), bcm2835_wdt.max_hw_heartbeat_ms);
    try std.testing.expectError(error.TimeoutTooSmall, bcm2835_wdt.Bcm2835WatchdogLab.init(0));
    try std.testing.expectError(error.TimeoutTooLarge, bcm2835_wdt.Bcm2835WatchdogLab.init(16));

    var watchdog = try bcm2835_wdt.Bcm2835WatchdogLab.init(12);
    const config = watchdog.configSnapshot();
    try std.testing.expectEqual(@as(u32, 12), config.timeout_sec);
    try std.testing.expectEqual(@as(u32, 15), config.max_timeout_sec);
    try std.testing.expectEqual(@as(u32, 15_999), config.max_hw_heartbeat_ms);
}

test "phase11 bcm2835_wdt mirrors running-state detection and start or stop register writes" {
    var watchdog = try bcm2835_wdt.Bcm2835WatchdogLab.init(9);

    var runtime = watchdog.loadRegisters(.{
        .rstc = bcm2835_wdt.pm_rstc_wrcfg_full_reset,
        .wdog = bcm2835_wdt.secondsToTicks(7),
    });
    try std.testing.expect(runtime.running);
    try std.testing.expectEqual(@as(u32, 7), runtime.time_left_sec);
    try std.testing.expect(runtime.full_reset_requested);

    runtime = watchdog.loadRegisters(.{
        .rstc = 0x1234_5608,
        .wdog = 0,
    });
    try std.testing.expect(!runtime.running);

    runtime = watchdog.start();
    try std.testing.expect(runtime.running);
    try std.testing.expectEqual(
        bcm2835_wdt.pm_password | bcm2835_wdt.secondsToTicks(9),
        runtime.registers.wdog,
    );
    try std.testing.expectEqual(
        bcm2835_wdt.pm_password |
            (0x1234_5608 & bcm2835_wdt.pm_rstc_wrcfg_clr) |
            bcm2835_wdt.pm_rstc_wrcfg_full_reset,
        runtime.registers.rstc,
    );
    try std.testing.expectEqual(@as(u32, 9), runtime.time_left_sec);

    runtime = watchdog.stop();
    try std.testing.expect(!runtime.running);
    try std.testing.expectEqual(
        bcm2835_wdt.pm_password | bcm2835_wdt.pm_rstc_reset,
        runtime.registers.rstc,
    );
    try std.testing.expectEqual(@as(u32, 0), runtime.time_left_sec);
}

test "phase11 bcm2835_wdt restart path uses the short reset timeout and preserves halt partition state" {
    var watchdog = try bcm2835_wdt.Bcm2835WatchdogLab.init(5);
    _ = watchdog.loadRegisters(.{
        .rstc = 0xabcd_1234,
        .rsts = bcm2835_wdt.pm_rsts_halt,
    });

    const runtime = watchdog.armRestart();
    try std.testing.expect(runtime.running);
    try std.testing.expect(runtime.restart_armed);
    try std.testing.expect(runtime.halt_partition_requested);
    try std.testing.expectEqual(
        bcm2835_wdt.pm_password | bcm2835_wdt.restart_ticks,
        runtime.registers.wdog,
    );
    try std.testing.expectEqual(
        bcm2835_wdt.pm_password |
            (0xabcd_1234 & bcm2835_wdt.pm_rstc_wrcfg_clr) |
            bcm2835_wdt.pm_rstc_wrcfg_full_reset,
        runtime.registers.rstc,
    );
    try std.testing.expectEqual(@as(u32, 0), runtime.time_left_sec);
}
