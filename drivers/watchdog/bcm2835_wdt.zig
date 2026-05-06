const std = @import("std");

pub const pm_password: u32 = 0x5a00_0000;
pub const pm_rsts_halt: u32 = 0x0000_0555;
pub const pm_wdog_time_set: u32 = 0x000f_ffff;
pub const pm_rstc_wrcfg_clr: u32 = 0xffff_ffcf;
pub const pm_rstc_wrcfg_full_reset: u32 = 0x0000_0020;
pub const pm_rstc_reset: u32 = 0x0000_0102;
pub const restart_ticks: u32 = 10;
pub const restart_priority: u32 = 128;
pub const min_timeout_sec: u32 = 1;
pub const max_timeout_sec: u32 = pm_wdog_time_set >> 16;
pub const max_hw_heartbeat_ms: u32 = ticksToMilliseconds(pm_wdog_time_set);

pub const ModuleDescriptor = struct {
    name: []const u8,
    anchor: []const u8,
    provides_simple_driver_starter: bool,
    touches_platform_registration: bool,
    touches_poweroff_plumbing: bool,
};

pub const RegisterImage = struct {
    rstc: u32 = 0,
    rsts: u32 = 0,
    wdog: u32 = 0,
};

pub const ConfigSnapshot = struct {
    anchor: []const u8,
    timeout_sec: u32,
    max_timeout_sec: u32,
    max_hw_heartbeat_ms: u32,
};

pub const ProbeSummary = struct {
    anchor: []const u8,
    timeout_sec: u32,
    max_timeout_sec: u32,
    max_hw_heartbeat_ms: u32,
    nowayout: bool,
    bootloader_running: bool,
    framework_marks_hw_running: bool,
    framework_ping_expected: bool,
    heartbeat_init_requested: bool,
    parent_attached: bool,
    stop_on_reboot: bool,
    restart_priority: u32,
    system_power_controller: bool,
};

pub const RegistrationSummary = struct {
    anchor: []const u8,
    bootloader_running: bool,
    framework_marks_hw_running: bool,
    register_device_requested: bool,
    stop_on_reboot: bool,
    restart_priority: u32,
    system_power_controller: bool,
    poweroff_handler_present: bool,
    poweroff_handler_claimed: bool,
    poweroff_handler_conflict: bool,
};

pub const RegistrationOutcomeSummary = struct {
    anchor: []const u8,
    system_power_controller: bool,
    registration_succeeded: bool,
    register_device_requested: bool,
    probe_error_returned: bool,
    poweroff_handler_present: bool,
    poweroff_handler_claimed: bool,
    poweroff_handler_conflict: bool,
    poweroff_handler_present_after_probe: bool,
    poweroff_handler_owned_by_driver: bool,
    poweroff_handler_left_in_place: bool,
};

pub const PlatformHandoffSummary = struct {
    anchor: []const u8,
    system_power_controller: bool,
    parent_attached: bool,
    pm_base_available: bool,
    drvdata_ready: bool,
    register_device_requested: bool,
    poweroff_handler_present: bool,
    poweroff_handler_claimed: bool,
    poweroff_handler_conflict: bool,
};

pub const PoweroffSummary = struct {
    anchor: []const u8,
    system_power_controller: bool,
    poweroff_handler_present: bool,
    poweroff_handler_owned_by_driver: bool,
    poweroff_path_ready: bool,
    halt_partition_requested: bool,
    restart_armed: bool,
};

pub const RemoveSummary = struct {
    anchor: []const u8,
    system_power_controller: bool,
    poweroff_handler_present: bool,
    poweroff_handler_owned_by_driver: bool,
    clear_poweroff_handler_requested: bool,
    poweroff_handler_left_in_place: bool,
};

pub const RuntimeSnapshot = struct {
    anchor: []const u8,
    running: bool,
    full_reset_requested: bool,
    restart_armed: bool,
    halt_partition_requested: bool,
    timeout_sec: u32,
    time_left_sec: u32,
    registers: RegisterImage,
};

pub const Bcm2835WatchdogLab = struct {
    const Self = @This();

    timeout_sec: u32,
    registers: RegisterImage = .{},

    pub fn descriptor() ModuleDescriptor {
        return .{
            .name = "bcm2835_wdt_lab",
            .anchor = "drivers/watchdog/bcm2835_wdt.c",
            .provides_simple_driver_starter = true,
            .touches_platform_registration = false,
            .touches_poweroff_plumbing = false,
        };
    }

    pub fn init(timeout_sec: u32) !Self {
        try validateTimeout(timeout_sec);
        return .{ .timeout_sec = timeout_sec };
    }

    pub fn configSnapshot(self: *const Self) ConfigSnapshot {
        return .{
            .anchor = descriptor().anchor,
            .timeout_sec = self.timeout_sec,
            .max_timeout_sec = max_timeout_sec,
            .max_hw_heartbeat_ms = max_hw_heartbeat_ms,
        };
    }

    pub fn probeSummary(
        self: *const Self,
        bootloader_running: bool,
        nowayout: bool,
        system_power_controller: bool,
    ) ProbeSummary {
        return .{
            .anchor = descriptor().anchor,
            .timeout_sec = self.timeout_sec,
            .max_timeout_sec = max_timeout_sec,
            .max_hw_heartbeat_ms = max_hw_heartbeat_ms,
            .nowayout = nowayout,
            .bootloader_running = bootloader_running,
            .framework_marks_hw_running = bootloader_running,
            .framework_ping_expected = bootloader_running,
            .heartbeat_init_requested = true,
            .parent_attached = true,
            .stop_on_reboot = true,
            .restart_priority = restart_priority,
            .system_power_controller = system_power_controller,
        };
    }

    pub fn registrationSummary(
        self: *const Self,
        bootloader_running: bool,
        system_power_controller: bool,
        poweroff_handler_present: bool,
    ) RegistrationSummary {
        _ = self;
        return .{
            .anchor = descriptor().anchor,
            .bootloader_running = bootloader_running,
            .framework_marks_hw_running = bootloader_running,
            .register_device_requested = true,
            .stop_on_reboot = true,
            .restart_priority = restart_priority,
            .system_power_controller = system_power_controller,
            .poweroff_handler_present = poweroff_handler_present,
            .poweroff_handler_claimed = system_power_controller and !poweroff_handler_present,
            .poweroff_handler_conflict = system_power_controller and poweroff_handler_present,
        };
    }

    pub fn registrationOutcomeSummary(
        self: *const Self,
        system_power_controller: bool,
        poweroff_handler_present: bool,
        registration_succeeded: bool,
    ) RegistrationOutcomeSummary {
        _ = self;
        const poweroff_handler_claimed =
            registration_succeeded and system_power_controller and !poweroff_handler_present;
        const poweroff_handler_owned_by_driver = poweroff_handler_claimed;
        const poweroff_handler_present_after_probe =
            poweroff_handler_present or poweroff_handler_owned_by_driver;
        return .{
            .anchor = descriptor().anchor,
            .system_power_controller = system_power_controller,
            .registration_succeeded = registration_succeeded,
            .register_device_requested = true,
            .probe_error_returned = !registration_succeeded,
            .poweroff_handler_present = poweroff_handler_present,
            .poweroff_handler_claimed = poweroff_handler_claimed,
            .poweroff_handler_conflict = system_power_controller and poweroff_handler_present,
            .poweroff_handler_present_after_probe = poweroff_handler_present_after_probe,
            .poweroff_handler_owned_by_driver = poweroff_handler_owned_by_driver,
            .poweroff_handler_left_in_place = poweroff_handler_present_after_probe and !poweroff_handler_owned_by_driver,
        };
    }

    pub fn platformHandoffSummary(
        self: *const Self,
        system_power_controller: bool,
        pm_base_available: bool,
        poweroff_handler_present: bool,
    ) PlatformHandoffSummary {
        _ = self;
        return .{
            .anchor = descriptor().anchor,
            .system_power_controller = system_power_controller,
            .parent_attached = true,
            .pm_base_available = pm_base_available,
            .drvdata_ready = pm_base_available,
            .register_device_requested = true,
            .poweroff_handler_present = poweroff_handler_present,
            .poweroff_handler_claimed = system_power_controller and !poweroff_handler_present,
            .poweroff_handler_conflict = system_power_controller and poweroff_handler_present,
        };
    }

    pub fn poweroffSummary(
        self: *const Self,
        system_power_controller: bool,
        poweroff_handler_present: bool,
        poweroff_handler_owned_by_driver: bool,
    ) PoweroffSummary {
        _ = self;
        const poweroff_path_ready =
            system_power_controller and poweroff_handler_present and poweroff_handler_owned_by_driver;
        return .{
            .anchor = descriptor().anchor,
            .system_power_controller = system_power_controller,
            .poweroff_handler_present = poweroff_handler_present,
            .poweroff_handler_owned_by_driver = poweroff_handler_owned_by_driver,
            .poweroff_path_ready = poweroff_path_ready,
            .halt_partition_requested = poweroff_path_ready,
            .restart_armed = poweroff_path_ready,
        };
    }

    pub fn removeSummary(
        self: *const Self,
        system_power_controller: bool,
        poweroff_handler_present: bool,
        poweroff_handler_owned_by_driver: bool,
    ) RemoveSummary {
        _ = self;
        const clear_poweroff_handler_requested =
            system_power_controller and poweroff_handler_present and poweroff_handler_owned_by_driver;
        return .{
            .anchor = descriptor().anchor,
            .system_power_controller = system_power_controller,
            .poweroff_handler_present = poweroff_handler_present,
            .poweroff_handler_owned_by_driver = poweroff_handler_owned_by_driver,
            .clear_poweroff_handler_requested = clear_poweroff_handler_requested,
            .poweroff_handler_left_in_place = poweroff_handler_present and !clear_poweroff_handler_requested,
        };
    }

    pub fn removeAfterRegistrationSummary(
        self: *const Self,
        system_power_controller: bool,
        poweroff_handler_present: bool,
        registration_succeeded: bool,
    ) RemoveSummary {
        const registration = self.registrationOutcomeSummary(
            system_power_controller,
            poweroff_handler_present,
            registration_succeeded,
        );
        return self.removeSummary(
            system_power_controller,
            registration.poweroff_handler_present_after_probe,
            registration.poweroff_handler_owned_by_driver,
        );
    }

    pub fn loadRegisters(self: *Self, registers: RegisterImage) RuntimeSnapshot {
        self.registers = registers;
        return self.runtimeSnapshot();
    }

    pub fn isRunning(self: *const Self) bool {
        return (self.registers.rstc & pm_rstc_wrcfg_full_reset) != 0;
    }

    pub fn getTimeleft(self: *const Self) u32 {
        if (!self.isRunning()) return 0;
        return ticksToSeconds(self.registers.wdog & pm_wdog_time_set);
    }

    pub fn start(self: *Self) RuntimeSnapshot {
        self.registers.wdog = pm_password | (secondsToTicks(self.timeout_sec) & pm_wdog_time_set);
        self.registers.rstc = pm_password | (self.registers.rstc & pm_rstc_wrcfg_clr) | pm_rstc_wrcfg_full_reset;
        return self.runtimeSnapshot();
    }

    pub fn stop(self: *Self) RuntimeSnapshot {
        self.registers.rstc = pm_password | pm_rstc_reset;
        return self.runtimeSnapshot();
    }

    pub fn armRestart(self: *Self) RuntimeSnapshot {
        self.registers.wdog = pm_password | restart_ticks;
        self.registers.rstc = pm_password | (self.registers.rstc & pm_rstc_wrcfg_clr) | pm_rstc_wrcfg_full_reset;
        return self.runtimeSnapshot();
    }

    pub fn runtimeSnapshot(self: *const Self) RuntimeSnapshot {
        const running = self.isRunning();
        return .{
            .anchor = descriptor().anchor,
            .running = running,
            .full_reset_requested = running,
            .restart_armed = running and (self.registers.wdog & pm_wdog_time_set) == restart_ticks,
            .halt_partition_requested = (self.registers.rsts & pm_rsts_halt) == pm_rsts_halt,
            .timeout_sec = self.timeout_sec,
            .time_left_sec = self.getTimeleft(),
            .registers = self.registers,
        };
    }
};

pub fn secondsToTicks(seconds: u32) u32 {
    return seconds << 16;
}

pub fn ticksToSeconds(ticks: u32) u32 {
    return ticks >> 16;
}

pub fn ticksToMilliseconds(ticks: u32) u32 {
    return (ticks * 1000) >> 16;
}

fn validateTimeout(timeout_sec: u32) !void {
    if (timeout_sec < min_timeout_sec) return error.TimeoutTooSmall;
    if (timeout_sec > max_timeout_sec) return error.TimeoutTooLarge;
}

test "registration outcome exposes claimed poweroff ownership" {
    const lab = try Bcm2835WatchdogLab.init(8);
    const outcome = lab.registrationOutcomeSummary(true, false, true);

    try std.testing.expect(outcome.poweroff_handler_claimed);
    try std.testing.expect(outcome.poweroff_handler_owned_by_driver);
    try std.testing.expect(outcome.poweroff_handler_present_after_probe);
    try std.testing.expect(!outcome.poweroff_handler_left_in_place);
}

test "registration outcome keeps conflicting poweroff handler in place" {
    const lab = try Bcm2835WatchdogLab.init(8);
    const outcome = lab.registrationOutcomeSummary(true, true, true);

    try std.testing.expect(!outcome.poweroff_handler_claimed);
    try std.testing.expect(outcome.poweroff_handler_conflict);
    try std.testing.expect(outcome.poweroff_handler_present_after_probe);
    try std.testing.expect(!outcome.poweroff_handler_owned_by_driver);
    try std.testing.expect(outcome.poweroff_handler_left_in_place);
}

test "remove after registration clears only driver-owned poweroff handler" {
    const lab = try Bcm2835WatchdogLab.init(8);

    const claimed_remove = lab.removeAfterRegistrationSummary(true, false, true);
    try std.testing.expect(claimed_remove.clear_poweroff_handler_requested);
    try std.testing.expect(!claimed_remove.poweroff_handler_left_in_place);

    const conflicted_remove = lab.removeAfterRegistrationSummary(true, true, true);
    try std.testing.expect(!conflicted_remove.clear_poweroff_handler_requested);
    try std.testing.expect(conflicted_remove.poweroff_handler_left_in_place);

    const failed_remove = lab.removeAfterRegistrationSummary(true, false, false);
    try std.testing.expect(!failed_remove.clear_poweroff_handler_requested);
    try std.testing.expect(!failed_remove.poweroff_handler_left_in_place);
}
