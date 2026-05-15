const std = @import("std");

pub const anchor_path = "drivers/watchdog/bcm2835_wdt.c";
pub const restart_priority: i32 = 128;
pub const password_mask: u32 = 0x5a00_0000;
pub const watchdog_time_mask: u32 = 0x000f_ffff;
pub const restart_cfg_mask: u32 = 0x0000_0020;
pub const reset_mask: u32 = 0x0000_0102;
pub const firmware_halt_partition_mask: u32 = 0x0000_0555;
pub const restart_timeout_ticks: u32 = 10;
pub const watchdog_tick_shift: u5 = 16;

pub const ProbeRequest = struct {
    heartbeat_sec: u32,
    nowayout: bool,
    bootloader_running: bool,
    system_power_controller: bool,
    poweroff_handler_present: bool,
};

pub const ProbeSummary = struct {
    anchor: []const u8,
    heartbeat_sec: u32,
    max_hw_heartbeat_ms: u32,
    nowayout: bool,
    bootloader_running: bool,
    sets_hw_running_bit: bool,
    restart_priority_value: i32,
    stop_on_reboot_requested: bool,
    registration_call: []const u8,
    registration_requested: bool,
    poweroff_handler_claimed: bool,
    poweroff_handler_conflict: bool,
    blocked_on_live_platform_registration: bool,
};

pub const StartSummary = struct {
    anchor: []const u8,
    heartbeat_sec: u32,
    programmed_ticks: u32,
    full_reset_armed: bool,
    running_after_start: bool,
};

pub const StopSummary = struct {
    anchor: []const u8,
    reset_register_written: bool,
    running_before_stop: bool,
    running_after_stop: bool,
    full_reset_armed_after_stop: bool,
};

pub const RestartSummary = struct {
    anchor: []const u8,
    programmed_ticks: u32,
    full_reset_armed: bool,
    delay_msec: u32,
    running_after_restart: bool,
};

pub const PoweroffSummary = struct {
    anchor: []const u8,
    halt_partition_requested: bool,
    restart_path_reused: bool,
    programmed_ticks: u32,
    full_reset_armed: bool,
    poweroff_handler_claimed: bool,
    running_after_poweroff: bool,
};

pub const RemoveState = enum {
    inactive_remove,
    running_remove,
};

pub const RemoveSummary = struct {
    anchor: []const u8,
    unregister_device_call: []const u8,
    unregister_device_requested: bool,
    poweroff_handler_release_requested: bool,
    running_before_remove: bool,
    running_after_remove: bool,
    full_reset_armed_after_remove: bool,
    halt_partition_requested_after_remove: bool,
    state: RemoveState,
};

pub const PlatformHandoffRequest = struct {
    heartbeat_sec: u32,
    nowayout: bool,
    bootloader_running: bool,
    system_power_controller: bool,
    poweroff_handler_present: bool,
    parent_attached: bool,
    pm_base_present: bool,
};

pub const PlatformHandoffSummary = struct {
    anchor: []const u8,
    heartbeat_sec: u32,
    nowayout: bool,
    bootloader_running: bool,
    parent_attached: bool,
    parent_supplies_pm_base: bool,
    pm_base_required: bool,
    pm_base_handoff_ready: bool,
    timeout_init_requested: bool,
    register_device_requested: bool,
    stop_on_reboot_requested: bool,
    restart_priority_value: i32,
    system_power_controller: bool,
    poweroff_handler_present: bool,
    poweroff_handler_claimed: bool,
    poweroff_handler_conflict: bool,
    blocked_on_live_platform_registration: bool,
};

pub fn maxTimeoutSeconds() u32 {
    return watchdogTicksToSeconds(watchdog_time_mask);
}

pub fn maxHeartbeatMilliseconds() u32 {
    return watchdogTicksToMilliseconds(watchdog_time_mask);
}

pub fn watchdogTicksToSeconds(ticks: u32) u32 {
    return (ticks & watchdog_time_mask) >> watchdog_tick_shift;
}

pub fn watchdogTicksToMilliseconds(ticks: u32) u32 {
    return ((ticks & watchdog_time_mask) * 1000) >> watchdog_tick_shift;
}

pub fn secondsToWatchdogTicks(seconds: u32) !u32 {
    try validateHeartbeatSeconds(seconds);
    return seconds << watchdog_tick_shift;
}

pub fn validateHeartbeatSeconds(seconds: u32) !void {
    if (seconds == 0) return error.TimeoutTooSmall;
    if (seconds > maxTimeoutSeconds()) return error.TimeoutTooLarge;
}

pub fn summarizeProbe(request: ProbeRequest) !ProbeSummary {
    try validateHeartbeatSeconds(request.heartbeat_sec);

    const poweroff_handler_claimed = request.system_power_controller and !request.poweroff_handler_present;
    const poweroff_handler_conflict = request.system_power_controller and request.poweroff_handler_present;

    return .{
        .anchor = anchor_path,
        .heartbeat_sec = request.heartbeat_sec,
        .max_hw_heartbeat_ms = maxHeartbeatMilliseconds(),
        .nowayout = request.nowayout,
        .bootloader_running = request.bootloader_running,
        .sets_hw_running_bit = request.bootloader_running,
        .restart_priority_value = restart_priority,
        .stop_on_reboot_requested = true,
        .registration_call = "devm_watchdog_register_device",
        .registration_requested = true,
        .poweroff_handler_claimed = poweroff_handler_claimed,
        .poweroff_handler_conflict = poweroff_handler_conflict,
        .blocked_on_live_platform_registration = true,
    };
}

pub fn summarizePlatformHandoff(request: PlatformHandoffRequest) !PlatformHandoffSummary {
    const probe = try summarizeProbe(.{
        .heartbeat_sec = request.heartbeat_sec,
        .nowayout = request.nowayout,
        .bootloader_running = request.bootloader_running,
        .system_power_controller = request.system_power_controller,
        .poweroff_handler_present = request.poweroff_handler_present,
    });
    const pm_base_handoff_ready = request.parent_attached and request.pm_base_present;

    return .{
        .anchor = anchor_path,
        .heartbeat_sec = probe.heartbeat_sec,
        .nowayout = probe.nowayout,
        .bootloader_running = probe.bootloader_running,
        .parent_attached = request.parent_attached,
        .parent_supplies_pm_base = request.pm_base_present,
        .pm_base_required = true,
        .pm_base_handoff_ready = pm_base_handoff_ready,
        .timeout_init_requested = true,
        .register_device_requested = probe.registration_requested and pm_base_handoff_ready,
        .stop_on_reboot_requested = probe.stop_on_reboot_requested,
        .restart_priority_value = probe.restart_priority_value,
        .system_power_controller = request.system_power_controller,
        .poweroff_handler_present = request.poweroff_handler_present,
        .poweroff_handler_claimed = probe.poweroff_handler_claimed,
        .poweroff_handler_conflict = probe.poweroff_handler_conflict,
        .blocked_on_live_platform_registration = true,
    };
}

pub const Bcm2835WdtLab = struct {
    heartbeat_sec: u32,
    running: bool = false,
    current_ticks: u32 = 0,
    full_reset_armed: bool = false,
    halt_partition_requested: bool = false,

    pub fn init(heartbeat_sec: u32) !Bcm2835WdtLab {
        try validateHeartbeatSeconds(heartbeat_sec);
        return .{ .heartbeat_sec = heartbeat_sec };
    }

    pub fn importBootloaderRunning(self: *Bcm2835WdtLab) !void {
        self.running = true;
        self.current_ticks = try secondsToWatchdogTicks(self.heartbeat_sec);
        self.full_reset_armed = true;
    }

    pub fn getTimeleftSeconds(self: *const Bcm2835WdtLab) u32 {
        return watchdogTicksToSeconds(self.current_ticks);
    }

    pub fn start(self: *Bcm2835WdtLab) !StartSummary {
        self.current_ticks = try secondsToWatchdogTicks(self.heartbeat_sec);
        self.running = true;
        self.full_reset_armed = true;

        return .{
            .anchor = anchor_path,
            .heartbeat_sec = self.heartbeat_sec,
            .programmed_ticks = self.current_ticks,
            .full_reset_armed = self.full_reset_armed,
            .running_after_start = self.running,
        };
    }

    pub fn stop(self: *Bcm2835WdtLab) StopSummary {
        const running_before_stop = self.running;
        self.running = false;
        self.current_ticks = 0;
        self.full_reset_armed = false;

        return .{
            .anchor = anchor_path,
            .reset_register_written = true,
            .running_before_stop = running_before_stop,
            .running_after_stop = self.running,
            .full_reset_armed_after_stop = self.full_reset_armed,
        };
    }

    pub fn restart(self: *Bcm2835WdtLab) RestartSummary {
        self.current_ticks = restart_timeout_ticks;
        self.running = true;
        self.full_reset_armed = true;

        return .{
            .anchor = anchor_path,
            .programmed_ticks = restart_timeout_ticks,
            .full_reset_armed = self.full_reset_armed,
            .delay_msec = 1,
            .running_after_restart = self.running,
        };
    }

    pub fn poweroff(self: *Bcm2835WdtLab, handler_claimed: bool) PoweroffSummary {
        self.halt_partition_requested = true;
        const restart_summary = self.restart();

        return .{
            .anchor = anchor_path,
            .halt_partition_requested = self.halt_partition_requested,
            .restart_path_reused = true,
            .programmed_ticks = restart_summary.programmed_ticks,
            .full_reset_armed = restart_summary.full_reset_armed,
            .poweroff_handler_claimed = handler_claimed,
            .running_after_poweroff = self.running,
        };
    }

    pub fn remove(self: *Bcm2835WdtLab, handler_claimed: bool) RemoveSummary {
        const running_before_remove = self.running;
        self.running = false;
        self.current_ticks = 0;
        self.full_reset_armed = false;
        self.halt_partition_requested = false;

        return .{
            .anchor = anchor_path,
            .unregister_device_call = "watchdog_unregister_device",
            .unregister_device_requested = true,
            .poweroff_handler_release_requested = handler_claimed,
            .running_before_remove = running_before_remove,
            .running_after_remove = self.running,
            .full_reset_armed_after_remove = self.full_reset_armed,
            .halt_partition_requested_after_remove = self.halt_partition_requested,
            .state = if (running_before_remove) .running_remove else .inactive_remove,
        };
    }
};

test "phase11 bcm2835_wdt conversion helpers keep watchdog bounds explicit" {
    try std.testing.expectEqual(@as(u32, 15), maxTimeoutSeconds());
    try std.testing.expectEqual(@as(u32, 15_999), maxHeartbeatMilliseconds());
    try std.testing.expectEqual(@as(u32, 65_536), try secondsToWatchdogTicks(1));
    try std.testing.expectEqual(@as(u32, 5), watchdogTicksToSeconds(5 << watchdog_tick_shift));
    try std.testing.expectEqual(@as(u32, 1_000), watchdogTicksToMilliseconds(1 << watchdog_tick_shift));
    try std.testing.expectError(error.TimeoutTooSmall, secondsToWatchdogTicks(0));
    try std.testing.expectError(error.TimeoutTooLarge, secondsToWatchdogTicks(16));
}

test "phase11 bcm2835_wdt probe summary keeps imported running state and poweroff ownership explicit" {
    const summary = try summarizeProbe(.{
        .heartbeat_sec = 12,
        .nowayout = true,
        .bootloader_running = true,
        .system_power_controller = true,
        .poweroff_handler_present = false,
    });

    try std.testing.expectEqualStrings(anchor_path, summary.anchor);
    try std.testing.expectEqual(@as(u32, 12), summary.heartbeat_sec);
    try std.testing.expectEqual(@as(u32, 15_999), summary.max_hw_heartbeat_ms);
    try std.testing.expect(summary.nowayout);
    try std.testing.expect(summary.bootloader_running);
    try std.testing.expect(summary.sets_hw_running_bit);
    try std.testing.expectEqual(@as(i32, 128), summary.restart_priority_value);
    try std.testing.expect(summary.stop_on_reboot_requested);
    try std.testing.expectEqualStrings("devm_watchdog_register_device", summary.registration_call);
    try std.testing.expect(summary.registration_requested);
    try std.testing.expect(summary.poweroff_handler_claimed);
    try std.testing.expect(!summary.poweroff_handler_conflict);
    try std.testing.expect(summary.blocked_on_live_platform_registration);
}

test "phase11 bcm2835_wdt probe summary keeps preexisting poweroff handlers distinct" {
    const summary = try summarizeProbe(.{
        .heartbeat_sec = 6,
        .nowayout = false,
        .bootloader_running = false,
        .system_power_controller = true,
        .poweroff_handler_present = true,
    });

    try std.testing.expect(!summary.sets_hw_running_bit);
    try std.testing.expect(!summary.poweroff_handler_claimed);
    try std.testing.expect(summary.poweroff_handler_conflict);
}

test "phase11 bcm2835_wdt platform handoff summary keeps PM-base prerequisites explicit" {
    const ready = try summarizePlatformHandoff(.{
        .heartbeat_sec = 9,
        .nowayout = true,
        .bootloader_running = true,
        .system_power_controller = true,
        .poweroff_handler_present = false,
        .parent_attached = true,
        .pm_base_present = true,
    });

    try std.testing.expectEqualStrings(anchor_path, ready.anchor);
    try std.testing.expectEqual(@as(u32, 9), ready.heartbeat_sec);
    try std.testing.expect(ready.nowayout);
    try std.testing.expect(ready.bootloader_running);
    try std.testing.expect(ready.parent_attached);
    try std.testing.expect(ready.parent_supplies_pm_base);
    try std.testing.expect(ready.pm_base_required);
    try std.testing.expect(ready.pm_base_handoff_ready);
    try std.testing.expect(ready.timeout_init_requested);
    try std.testing.expect(ready.register_device_requested);
    try std.testing.expect(ready.stop_on_reboot_requested);
    try std.testing.expectEqual(@as(i32, restart_priority), ready.restart_priority_value);
    try std.testing.expect(ready.system_power_controller);
    try std.testing.expect(!ready.poweroff_handler_present);
    try std.testing.expect(ready.poweroff_handler_claimed);
    try std.testing.expect(!ready.poweroff_handler_conflict);
    try std.testing.expect(ready.blocked_on_live_platform_registration);

    const blocked = try summarizePlatformHandoff(.{
        .heartbeat_sec = 9,
        .nowayout = false,
        .bootloader_running = false,
        .system_power_controller = true,
        .poweroff_handler_present = true,
        .parent_attached = true,
        .pm_base_present = false,
    });

    try std.testing.expect(blocked.parent_attached);
    try std.testing.expect(!blocked.parent_supplies_pm_base);
    try std.testing.expect(blocked.pm_base_required);
    try std.testing.expect(!blocked.pm_base_handoff_ready);
    try std.testing.expect(blocked.timeout_init_requested);
    try std.testing.expect(!blocked.register_device_requested);
    try std.testing.expect(blocked.stop_on_reboot_requested);
    try std.testing.expect(blocked.system_power_controller);
    try std.testing.expect(blocked.poweroff_handler_present);
    try std.testing.expect(!blocked.poweroff_handler_claimed);
    try std.testing.expect(blocked.poweroff_handler_conflict);
    try std.testing.expect(blocked.blocked_on_live_platform_registration);

    const claim_pending = try summarizePlatformHandoff(.{
        .heartbeat_sec = 9,
        .nowayout = false,
        .bootloader_running = false,
        .system_power_controller = true,
        .poweroff_handler_present = false,
        .parent_attached = true,
        .pm_base_present = false,
    });

    try std.testing.expect(claim_pending.parent_attached);
    try std.testing.expect(!claim_pending.parent_supplies_pm_base);
    try std.testing.expect(claim_pending.pm_base_required);
    try std.testing.expect(!claim_pending.pm_base_handoff_ready);
    try std.testing.expect(claim_pending.timeout_init_requested);
    try std.testing.expect(!claim_pending.register_device_requested);
    try std.testing.expect(claim_pending.stop_on_reboot_requested);
    try std.testing.expect(claim_pending.system_power_controller);
    try std.testing.expect(!claim_pending.poweroff_handler_present);
    try std.testing.expect(claim_pending.poweroff_handler_claimed);
    try std.testing.expect(!claim_pending.poweroff_handler_conflict);
    try std.testing.expect(claim_pending.blocked_on_live_platform_registration);
}

test "phase11 bcm2835_wdt lab start stop and timeleft mirror watchdog register intent" {
    var watchdog = try Bcm2835WdtLab.init(9);

    const started = try watchdog.start();
    try std.testing.expectEqualStrings(anchor_path, started.anchor);
    try std.testing.expectEqual(@as(u32, 9), started.heartbeat_sec);
    try std.testing.expectEqual(@as(u32, 9 << watchdog_tick_shift), started.programmed_ticks);
    try std.testing.expect(started.full_reset_armed);
    try std.testing.expect(started.running_after_start);
    try std.testing.expectEqual(@as(u32, 9), watchdog.getTimeleftSeconds());

    const stopped = watchdog.stop();
    try std.testing.expect(stopped.reset_register_written);
    try std.testing.expect(stopped.running_before_stop);
    try std.testing.expect(!stopped.running_after_stop);
    try std.testing.expect(!stopped.full_reset_armed_after_stop);
    try std.testing.expectEqual(@as(u32, 0), watchdog.getTimeleftSeconds());
}

test "phase11 bcm2835_wdt restart and poweroff summaries keep full reset and halt partition distinct" {
    var watchdog = try Bcm2835WdtLab.init(5);
    try watchdog.importBootloaderRunning();
    try std.testing.expectEqual(@as(u32, 5), watchdog.getTimeleftSeconds());

    const restart_summary = watchdog.restart();
    try std.testing.expectEqualStrings(anchor_path, restart_summary.anchor);
    try std.testing.expectEqual(@as(u32, restart_timeout_ticks), restart_summary.programmed_ticks);
    try std.testing.expect(restart_summary.full_reset_armed);
    try std.testing.expectEqual(@as(u32, 1), restart_summary.delay_msec);
    try std.testing.expect(restart_summary.running_after_restart);

    const poweroff_summary = watchdog.poweroff(true);
    try std.testing.expectEqualStrings(anchor_path, poweroff_summary.anchor);
    try std.testing.expect(poweroff_summary.halt_partition_requested);
    try std.testing.expect(poweroff_summary.restart_path_reused);
    try std.testing.expectEqual(@as(u32, restart_timeout_ticks), poweroff_summary.programmed_ticks);
    try std.testing.expect(poweroff_summary.full_reset_armed);
    try std.testing.expect(poweroff_summary.poweroff_handler_claimed);
    try std.testing.expect(poweroff_summary.running_after_poweroff);
}

test "phase11 bcm2835_wdt remove summary keeps claimed cleanup explicit" {
    var claimed = try Bcm2835WdtLab.init(5);
    _ = try claimed.start();
    const claimed_summary = claimed.remove(true);
    try std.testing.expectEqualStrings(anchor_path, claimed_summary.anchor);
    try std.testing.expectEqualStrings("watchdog_unregister_device", claimed_summary.unregister_device_call);
    try std.testing.expect(claimed_summary.unregister_device_requested);
    try std.testing.expect(claimed_summary.poweroff_handler_release_requested);
    try std.testing.expect(claimed_summary.running_before_remove);
    try std.testing.expect(!claimed_summary.running_after_remove);
    try std.testing.expect(!claimed_summary.full_reset_armed_after_remove);
    try std.testing.expect(!claimed_summary.halt_partition_requested_after_remove);
    try std.testing.expectEqual(RemoveState.running_remove, claimed_summary.state);

    var unclaimed = try Bcm2835WdtLab.init(5);
    const unclaimed_summary = unclaimed.remove(false);
    try std.testing.expect(unclaimed_summary.unregister_device_requested);
    try std.testing.expect(!unclaimed_summary.poweroff_handler_release_requested);
    try std.testing.expect(!unclaimed_summary.running_before_remove);
    try std.testing.expect(!unclaimed_summary.running_after_remove);
    try std.testing.expect(!unclaimed_summary.full_reset_armed_after_remove);
    try std.testing.expect(!unclaimed_summary.halt_partition_requested_after_remove);
    try std.testing.expectEqual(RemoveState.inactive_remove, unclaimed_summary.state);
}
