const std = @import("std");
const gpio_wdt = @import("gpio_wdt");

test "phase11 gpio watchdog keeps platform cleanup checkpoint explicit before remove handoff" {
    var stoppable = try gpio_wdt.GpioWatchdogLab.init(.toggle, 250, false);
    _ = try stoppable.start();
    const cleanup = stoppable.platformCleanupCheckpointSummary(false);

    try std.testing.expectEqualStrings("drivers/watchdog/gpio_wdt.c", cleanup.anchor);
    try std.testing.expectEqual(gpio_wdt.HardwareAlgorithm.toggle, cleanup.hw_algo);
    try std.testing.expect(!cleanup.always_running);
    try std.testing.expect(!cleanup.nowayout);
    try std.testing.expectEqual(gpio_wdt.StopDisposition.stopped, cleanup.stop_disposition);
    try std.testing.expectEqualStrings("gpio_wdt_priv", cleanup.platform_drvdata_owner_identity);
    try std.testing.expectEqualStrings("gpio_wdt_priv", cleanup.watchdog_drvdata_owner_identity);
    try std.testing.expectEqualStrings("devm_watchdog_register_device", cleanup.register_device_failure_stage);
    try std.testing.expect(cleanup.request_stop_reviewable);
    try std.testing.expect(cleanup.register_device_failure_reviewable);
    try std.testing.expect(cleanup.reboot_glue_checkpoint_reviewable);
    try std.testing.expect(cleanup.platform_cleanup_precedes_driver_remove);
    try std.testing.expect(cleanup.driver_remove_precedes_watchdog_unregister);
    try std.testing.expect(cleanup.cleanup_reuses_parent_linkage);
    try std.testing.expect(cleanup.blocked_on_platform_cleanup_callback);
    try std.testing.expect(cleanup.blocked_on_platform_driver_remove);
    try std.testing.expect(cleanup.blocked_on_watchdog_core_unregister);
    try std.testing.expect(cleanup.blocked_on_host_shutdown_execution);

    var guarded = try gpio_wdt.GpioWatchdogLab.init(.level, 400, true);
    _ = try guarded.start();
    const guarded_cleanup = guarded.platformCleanupCheckpointSummary(true);

    try std.testing.expectEqual(gpio_wdt.HardwareAlgorithm.level, guarded_cleanup.hw_algo);
    try std.testing.expect(guarded_cleanup.always_running);
    try std.testing.expect(guarded_cleanup.nowayout);
    try std.testing.expectEqual(gpio_wdt.StopDisposition.blocked_by_nowayout, guarded_cleanup.stop_disposition);
    try std.testing.expect(guarded_cleanup.request_stop_reviewable);
    try std.testing.expect(guarded_cleanup.register_device_failure_reviewable);
    try std.testing.expect(guarded_cleanup.reboot_glue_checkpoint_reviewable);
    try std.testing.expect(guarded_cleanup.platform_cleanup_precedes_driver_remove);
    try std.testing.expect(guarded_cleanup.driver_remove_precedes_watchdog_unregister);
    try std.testing.expect(guarded_cleanup.cleanup_reuses_parent_linkage);
    try std.testing.expect(guarded_cleanup.blocked_on_platform_cleanup_callback);
    try std.testing.expect(guarded_cleanup.blocked_on_platform_driver_remove);
    try std.testing.expect(guarded_cleanup.blocked_on_watchdog_core_unregister);
    try std.testing.expect(guarded_cleanup.blocked_on_host_shutdown_execution);
}

test "phase11 gpio watchdog keeps dedicated remove handoff replay aligned with cleanup checkpoint" {
    var stoppable = try gpio_wdt.GpioWatchdogLab.init(.toggle, 250, false);
    _ = try stoppable.start();
    const cleanup = stoppable.platformCleanupCheckpointSummary(false);
    const handoff = stoppable.summarizeRemoveHandoff(false);

    try std.testing.expectEqualStrings(cleanup.anchor, handoff.anchor);
    try std.testing.expectEqual(cleanup.hw_algo, handoff.hw_algo);
    try std.testing.expectEqual(cleanup.always_running, handoff.always_running);
    try std.testing.expectEqual(cleanup.nowayout, handoff.nowayout);
    try std.testing.expectEqual(cleanup.stop_disposition, handoff.stop_disposition);
    try std.testing.expectEqualStrings(cleanup.platform_drvdata_owner_identity, handoff.platform_drvdata_owner_identity);
    try std.testing.expectEqualStrings(cleanup.watchdog_drvdata_owner_identity, handoff.watchdog_drvdata_owner_identity);
    try std.testing.expectEqualStrings(cleanup.register_device_failure_stage, handoff.register_device_failure_stage);
    try std.testing.expectEqual(cleanup.request_stop_reviewable, handoff.request_stop_reviewable);
    try std.testing.expectEqual(cleanup.register_device_failure_reviewable, handoff.register_device_failure_reviewable);
    try std.testing.expectEqual(cleanup.reboot_glue_checkpoint_reviewable, handoff.reboot_glue_checkpoint_reviewable);
    try std.testing.expectEqual(cleanup.blocked_on_platform_cleanup_callback, handoff.blocked_on_platform_cleanup_callback);
    try std.testing.expectEqual(cleanup.blocked_on_platform_driver_remove, handoff.blocked_on_platform_driver_remove);
    try std.testing.expectEqual(cleanup.blocked_on_watchdog_core_unregister, handoff.blocked_on_watchdog_core_unregister);
    try std.testing.expectEqual(cleanup.blocked_on_host_shutdown_execution, handoff.blocked_on_host_shutdown_execution);

    var guarded = try gpio_wdt.GpioWatchdogLab.init(.level, 400, true);
    _ = try guarded.start();
    const guarded_cleanup = guarded.platformCleanupCheckpointSummary(true);
    const guarded_handoff = guarded.summarizeRemoveHandoff(true);

    try std.testing.expectEqualStrings(guarded_cleanup.anchor, guarded_handoff.anchor);
    try std.testing.expectEqual(guarded_cleanup.hw_algo, guarded_handoff.hw_algo);
    try std.testing.expectEqual(guarded_cleanup.always_running, guarded_handoff.always_running);
    try std.testing.expectEqual(guarded_cleanup.nowayout, guarded_handoff.nowayout);
    try std.testing.expectEqual(guarded_cleanup.stop_disposition, guarded_handoff.stop_disposition);
    try std.testing.expectEqualStrings(guarded_cleanup.platform_drvdata_owner_identity, guarded_handoff.platform_drvdata_owner_identity);
    try std.testing.expectEqualStrings(guarded_cleanup.watchdog_drvdata_owner_identity, guarded_handoff.watchdog_drvdata_owner_identity);
    try std.testing.expectEqualStrings(guarded_cleanup.register_device_failure_stage, guarded_handoff.register_device_failure_stage);
    try std.testing.expectEqual(guarded_cleanup.request_stop_reviewable, guarded_handoff.request_stop_reviewable);
    try std.testing.expectEqual(guarded_cleanup.register_device_failure_reviewable, guarded_handoff.register_device_failure_reviewable);
    try std.testing.expectEqual(guarded_cleanup.reboot_glue_checkpoint_reviewable, guarded_handoff.reboot_glue_checkpoint_reviewable);
    try std.testing.expectEqual(guarded_cleanup.blocked_on_platform_cleanup_callback, guarded_handoff.blocked_on_platform_cleanup_callback);
    try std.testing.expectEqual(guarded_cleanup.blocked_on_platform_driver_remove, guarded_handoff.blocked_on_platform_driver_remove);
    try std.testing.expectEqual(guarded_cleanup.blocked_on_watchdog_core_unregister, guarded_handoff.blocked_on_watchdog_core_unregister);
    try std.testing.expectEqual(guarded_cleanup.blocked_on_host_shutdown_execution, guarded_handoff.blocked_on_host_shutdown_execution);
}
