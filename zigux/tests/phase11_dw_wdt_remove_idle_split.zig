const std = @import("std");
const dw_wdt = @import("dw_wdt");

test "phase11 dw_wdt keeps idle remove-time pending interrupts distinct when reset control is available or absent" {
    var resetless = try dw_wdt.DwWdtLab.initFixedTops(65_536, false);
    const resetless_summary = try resetless.summarizeRemoveHandoff(.{
        .watchdog_running_before_remove = false,
        .remove_interrupt_pending = true,
    });
    try std.testing.expectEqualStrings("drivers/watchdog/dw_wdt.c", resetless_summary.anchor);
    try std.testing.expect(!resetless_summary.reset_control_available);
    try std.testing.expect(resetless_summary.debugfs_clear_requested);
    try std.testing.expect(resetless_summary.unregister_device_requested);
    try std.testing.expect(!resetless_summary.remove_path_running_before_remove);
    try std.testing.expect(!resetless_summary.remove_path_running_after_remove);
    try std.testing.expect(!resetless_summary.remove_path_hardware_running_after_remove);
    try std.testing.expect(!resetless_summary.remove_clears_enable_bit);
    try std.testing.expect(!resetless_summary.remove_clears_interrupt_status);
    try std.testing.expect(!resetless_summary.remove_asserts_reset_control);
    try std.testing.expect(!resetless_summary.remove_preserves_running_marker_without_reset);
    try std.testing.expect(resetless_summary.remove_preserves_pending_interrupt_without_reset);

    var reset_available = try dw_wdt.DwWdtLab.initFixedTops(65_536, true);
    const reset_available_summary = try reset_available.summarizeRemoveHandoff(.{
        .watchdog_running_before_remove = false,
        .remove_interrupt_pending = true,
    });
    try std.testing.expectEqualStrings("drivers/watchdog/dw_wdt.c", reset_available_summary.anchor);
    try std.testing.expect(reset_available_summary.reset_control_available);
    try std.testing.expect(reset_available_summary.debugfs_clear_requested);
    try std.testing.expect(reset_available_summary.unregister_device_requested);
    try std.testing.expect(!reset_available_summary.remove_path_running_before_remove);
    try std.testing.expect(!reset_available_summary.remove_path_running_after_remove);
    try std.testing.expect(!reset_available_summary.remove_path_hardware_running_after_remove);
    try std.testing.expect(!reset_available_summary.remove_clears_enable_bit);
    try std.testing.expect(reset_available_summary.remove_clears_interrupt_status);
    try std.testing.expect(reset_available_summary.remove_asserts_reset_control);
    try std.testing.expect(!reset_available_summary.remove_preserves_running_marker_without_reset);
    try std.testing.expect(!reset_available_summary.remove_preserves_pending_interrupt_without_reset);

    var reset_available_quiet = try dw_wdt.DwWdtLab.initFixedTops(65_536, true);
    const reset_available_quiet_summary = try reset_available_quiet.summarizeRemoveHandoff(.{
        .watchdog_running_before_remove = false,
        .remove_interrupt_pending = false,
    });
    try std.testing.expectEqualStrings("drivers/watchdog/dw_wdt.c", reset_available_quiet_summary.anchor);
    try std.testing.expect(reset_available_quiet_summary.reset_control_available);
    try std.testing.expect(reset_available_quiet_summary.debugfs_clear_requested);
    try std.testing.expect(reset_available_quiet_summary.unregister_device_requested);
    try std.testing.expect(!reset_available_quiet_summary.remove_path_running_before_remove);
    try std.testing.expect(!reset_available_quiet_summary.remove_path_running_after_remove);
    try std.testing.expect(!reset_available_quiet_summary.remove_path_hardware_running_after_remove);
    try std.testing.expect(!reset_available_quiet_summary.remove_clears_enable_bit);
    try std.testing.expect(!reset_available_quiet_summary.remove_clears_interrupt_status);
    try std.testing.expect(reset_available_quiet_summary.remove_asserts_reset_control);
    try std.testing.expect(!reset_available_quiet_summary.remove_preserves_running_marker_without_reset);
    try std.testing.expect(!reset_available_quiet_summary.remove_preserves_pending_interrupt_without_reset);
}

test "phase11 dw_wdt keeps active remove-time cleanup distinct when reset control is available or absent" {
    var resetless = try dw_wdt.DwWdtLab.initFixedTops(65_536, false);
    const resetless_summary = try resetless.summarizeRemoveHandoff(.{
        .watchdog_running_before_remove = true,
        .remove_interrupt_pending = false,
    });
    try std.testing.expectEqualStrings("drivers/watchdog/dw_wdt.c", resetless_summary.anchor);
    try std.testing.expect(!resetless_summary.reset_control_available);
    try std.testing.expect(resetless_summary.debugfs_clear_requested);
    try std.testing.expect(resetless_summary.unregister_device_requested);
    try std.testing.expect(resetless_summary.remove_path_running_before_remove);
    try std.testing.expect(resetless_summary.remove_path_running_after_remove);
    try std.testing.expect(resetless_summary.remove_path_hardware_running_after_remove);
    try std.testing.expect(!resetless_summary.remove_clears_enable_bit);
    try std.testing.expect(!resetless_summary.remove_clears_interrupt_status);
    try std.testing.expect(!resetless_summary.remove_asserts_reset_control);
    try std.testing.expect(resetless_summary.remove_preserves_running_marker_without_reset);
    try std.testing.expect(!resetless_summary.remove_preserves_pending_interrupt_without_reset);

    var reset_available = try dw_wdt.DwWdtLab.initFixedTops(65_536, true);
    const reset_available_summary = try reset_available.summarizeRemoveHandoff(.{
        .watchdog_running_before_remove = true,
        .remove_interrupt_pending = false,
    });
    try std.testing.expectEqualStrings("drivers/watchdog/dw_wdt.c", reset_available_summary.anchor);
    try std.testing.expect(reset_available_summary.reset_control_available);
    try std.testing.expect(reset_available_summary.debugfs_clear_requested);
    try std.testing.expect(reset_available_summary.unregister_device_requested);
    try std.testing.expect(reset_available_summary.remove_path_running_before_remove);
    try std.testing.expect(!reset_available_summary.remove_path_running_after_remove);
    try std.testing.expect(!reset_available_summary.remove_path_hardware_running_after_remove);
    try std.testing.expect(reset_available_summary.remove_clears_enable_bit);
    try std.testing.expect(!reset_available_summary.remove_clears_interrupt_status);
    try std.testing.expect(reset_available_summary.remove_asserts_reset_control);
    try std.testing.expect(!reset_available_summary.remove_preserves_running_marker_without_reset);
    try std.testing.expect(!reset_available_summary.remove_preserves_pending_interrupt_without_reset);
}

test "phase11 dw_wdt keeps the minimum normal timeout distinct from restart arming" {
    var watchdog = try dw_wdt.DwWdtLab.initFixedTops(65_536, false);
    const config = try watchdog.setTimeout(1);
    try std.testing.expectEqual(@as(u32, 1), config.timeout_sec);
    try std.testing.expectEqual(@as(u32, 0), config.pretimeout_sec);

    const shortest_timeout = try watchdog.start();
    try std.testing.expect(shortest_timeout.running);
    try std.testing.expectEqual(@as(u32, 0), shortest_timeout.registers.timeout_range);
    try std.testing.expect(!shortest_timeout.restart_armed);

    const imported_shortest_timeout = watchdog.loadRegisters(.{
        .control = dw_wdt.control_reg_wdt_en_mask,
        .timeout_range = 0,
    });
    try std.testing.expect(imported_shortest_timeout.running);
    try std.testing.expectEqual(@as(u32, 0), imported_shortest_timeout.registers.timeout_range);
    try std.testing.expect(!imported_shortest_timeout.restart_armed);

    const restart_runtime = watchdog.armRestart();
    try std.testing.expect(restart_runtime.running);
    try std.testing.expect(restart_runtime.restart_armed);
}
