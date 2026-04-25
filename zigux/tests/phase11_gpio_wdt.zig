const std = @import("std");
const gpio_wdt = @import("gpio_wdt");

test "phase11 gpio_wdt parses the bounded property surface and reports config limits" {
    const descriptor = gpio_wdt.GpioWatchdogLab.descriptor();
    try std.testing.expectEqualStrings("gpio_wdt_lab", descriptor.name);
    try std.testing.expectEqualStrings("drivers/watchdog/gpio_wdt.c", descriptor.anchor);
    try std.testing.expect(descriptor.provides_simple_driver_starter);
    try std.testing.expect(!descriptor.touches_platform_registration);
    try std.testing.expect(!descriptor.touches_live_gpio);

    try std.testing.expectError(
        error.InvalidHardwareAlgorithm,
        gpio_wdt.GpioWatchdogLab.initFromPropertyString("pulse", 50, false),
    );
    try std.testing.expectError(
        error.HeartbeatMarginTooSmall,
        gpio_wdt.GpioWatchdogLab.initFromPropertyString("toggle", 1, false),
    );
    try std.testing.expectError(
        error.HeartbeatMarginTooLarge,
        gpio_wdt.GpioWatchdogLab.initFromPropertyString("level", 65_536, true),
    );

    var watchdog = try gpio_wdt.GpioWatchdogLab.initFromPropertyString("toggle", 250, false);
    const config = watchdog.configSnapshot();
    try std.testing.expectEqual(gpio_wdt.HardwareAlgorithm.toggle, config.hw_algo);
    try std.testing.expectEqual(@as(u32, 250), config.hw_margin_ms);
    try std.testing.expect(!config.always_running);
    try std.testing.expectEqual(@as(u32, gpio_wdt.soft_timeout_min), config.min_timeout_sec);
    try std.testing.expectEqual(@as(u32, gpio_wdt.soft_timeout_default), config.default_timeout_sec);
    try std.testing.expectEqual(@as(u32, 250), config.max_hw_heartbeat_ms);
    try std.testing.expectError(error.WatchdogNotRunning, watchdog.ping());
}

test "phase11 gpio_wdt toggle mode mirrors start, ping, and stop transitions" {
    var watchdog = try gpio_wdt.GpioWatchdogLab.init(.toggle, 20, false);

    var runtime = try watchdog.start();
    try std.testing.expect(runtime.running);
    try std.testing.expect(runtime.line_is_output);
    try std.testing.expect(runtime.line_state);
    try std.testing.expectEqual(@as(usize, 1), runtime.ping_count);
    try std.testing.expectEqual(@as(usize, 0), runtime.pulse_count);
    try std.testing.expect(!runtime.last_ping_was_pulse);

    runtime = try watchdog.ping();
    try std.testing.expect(runtime.running);
    try std.testing.expect(!runtime.line_state);
    try std.testing.expectEqual(@as(usize, 2), runtime.ping_count);
    try std.testing.expectEqual(@as(usize, 0), runtime.pulse_count);

    runtime = watchdog.stop();
    try std.testing.expect(!runtime.running);
    try std.testing.expect(!runtime.line_is_output);
    try std.testing.expect(runtime.line_state);
    try std.testing.expectEqual(@as(usize, 1), runtime.disable_count);
}

test "phase11 gpio_wdt level mode records pulses and keeps always-running hardware active" {
    var watchdog = try gpio_wdt.GpioWatchdogLab.init(.level, 500, true);

    var runtime = try watchdog.start();
    try std.testing.expect(runtime.running);
    try std.testing.expect(runtime.line_is_output);
    try std.testing.expect(!runtime.line_state);
    try std.testing.expectEqual(@as(usize, 1), runtime.ping_count);
    try std.testing.expectEqual(@as(usize, 1), runtime.pulse_count);
    try std.testing.expect(runtime.last_ping_was_pulse);
    try std.testing.expectEqual(@as(u32, gpio_wdt.level_pulse_width_usec), runtime.last_pulse_width_usec);

    runtime = watchdog.stop();
    try std.testing.expect(runtime.running);
    try std.testing.expect(runtime.line_is_output);
    try std.testing.expect(!runtime.line_state);
    try std.testing.expectEqual(@as(usize, 0), runtime.disable_count);

    runtime = try watchdog.ping();
    try std.testing.expect(runtime.running);
    try std.testing.expectEqual(@as(usize, 2), runtime.ping_count);
    try std.testing.expectEqual(@as(usize, 2), runtime.pulse_count);
}
