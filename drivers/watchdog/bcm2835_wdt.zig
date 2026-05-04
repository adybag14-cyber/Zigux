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

pub const WatchdogMetadataSummary = struct {
    anchor: []const u8,
    identity: []const u8,
    supports_set_timeout: bool,
    supports_magic_close: bool,
    supports_keepalive_ping: bool,
    start_op_ready: bool,
    stop_op_ready: bool,
    get_timeleft_op_ready: bool,
    restart_op_ready: bool,
    min_timeout_sec: u32,
    default_timeout_sec: u32,
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
    register_device_requested: bool,
    register_device_succeeded: bool,
    register_device_failed: bool,
    system_power_controller: bool,
    poweroff_handler_present: bool,
    poweroff_handler_claimed: bool,
    poweroff_handler_conflict: bool,
    poweroff_handler_claim_blocked_by_registration_failure: bool,
    probe_returns_error: bool,
};

pub const PlatformHandoffSummary = struct {
    anchor: []const u8,
    bootloader_running: bool,
    nowayout: bool,
    parent_attached: bool,
    parent_supplies_pm_base: bool,
    pm_base_required: bool,
    pm_base_handoff_ready: bool,
    watchdog_drvdata_set: bool,
    watchdog_parent_set: bool,
    timeout_init_requested: bool,
    register_device_requested: bool,
    register_device_blocked_by_missing_pm_base: bool,
    stop_on_reboot: bool,
    restart_priority: u32,
    system_power_controller: bool,
    poweroff_handler_present: bool,
    poweroff_handler_claimed: bool,
    poweroff_handler_conflict: bool,
};

pub const RemoveSummary = struct {
    anchor: []const u8,
    system_power_controller: bool,
    poweroff_handler_present: bool,
    poweroff_handler_owned_by_driver: bool,
    remove_callback_ready: bool,
    watchdog_teardown_managed_by_devm: bool,
    remove_callback_scope_limited_to_poweroff_owner: bool,
    clear_poweroff_handler_requested: bool,
    clear_poweroff_handler_blocked_by_conflict: bool,
    clear_poweroff_handler_skipped_without_system_power_controller: bool,
    clear_poweroff_handler_skipped_without_handler: bool,
    poweroff_handler_left_in_place: bool,
};

pub const PoweroffSummary = struct {
    anchor: []const u8,
    system_power_controller: bool,
    poweroff_handler_present: bool,
    poweroff_handler_owned_by_driver: bool,
    poweroff_callback_ready: bool,
    poweroff_path_available: bool,
    blocked_without_system_power_controller: bool,
    blocked_without_poweroff_handler: bool,
    blocked_by_poweroff_handler_conflict: bool,
    full_reset_requested: bool,
    restart_armed: bool,
    halt_partition_requested: bool,
    registers: RegisterImage,
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

    pub fn watchdogMetadataSummary(self: *const Self) WatchdogMetadataSummary {
        _ = self;
        return .{
            .anchor = descriptor().anchor,
            .identity = "Broadcom BCM2835 Watchdog timer",
            .supports_set_timeout = true,
            .supports_magic_close = true,
            .supports_keepalive_ping = true,
            .start_op_ready = true,
            .stop_op_ready = true,
            .get_timeleft_op_ready = true,
            .restart_op_ready = true,
            .min_timeout_sec = min_timeout_sec,
            .default_timeout_sec = max_timeout_sec,
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
        register_device_succeeded: bool,
        poweroff_handler_present: bool,
    ) RegistrationOutcomeSummary {
        _ = self;
        const register_device_requested = true;
        const register_device_failed = register_device_requested and !register_device_succeeded;
        return .{
            .anchor = descriptor().anchor,
            .register_device_requested = register_device_requested,
            .register_device_succeeded = register_device_succeeded,
            .register_device_failed = register_device_failed,
            .system_power_controller = system_power_controller,
            .poweroff_handler_present = poweroff_handler_present,
            .poweroff_handler_claimed = register_device_succeeded and system_power_controller and !poweroff_handler_present,
            .poweroff_handler_conflict = register_device_succeeded and system_power_controller and poweroff_handler_present,
            .poweroff_handler_claim_blocked_by_registration_failure = register_device_failed and system_power_controller,
            .probe_returns_error = register_device_failed,
        };
    }

    pub fn platformHandoffSummary(
        self: *const Self,
        bootloader_running: bool,
        nowayout: bool,
        system_power_controller: bool,
        pm_base_present: bool,
        poweroff_handler_present: bool,
    ) PlatformHandoffSummary {
        const probe = self.probeSummary(bootloader_running, nowayout, system_power_controller);
        const registration = self.registrationSummary(
            bootloader_running,
            system_power_controller,
            poweroff_handler_present,
        );
        const pm_base_handoff_ready = probe.parent_attached and pm_base_present;
        return .{
            .anchor = descriptor().anchor,
            .bootloader_running = probe.bootloader_running,
            .nowayout = probe.nowayout,
            .parent_attached = probe.parent_attached,
            .parent_supplies_pm_base = pm_base_present,
            .pm_base_required = true,
            .pm_base_handoff_ready = pm_base_handoff_ready,
            .watchdog_drvdata_set = pm_base_handoff_ready,
            .watchdog_parent_set = probe.parent_attached,
            .timeout_init_requested = probe.heartbeat_init_requested,
            .register_device_requested = registration.register_device_requested and pm_base_handoff_ready,
            .register_device_blocked_by_missing_pm_base = registration.register_device_requested and !pm_base_handoff_ready,
            .stop_on_reboot = registration.stop_on_reboot,
            .restart_priority = registration.restart_priority,
            .system_power_controller = system_power_controller,
            .poweroff_handler_present = poweroff_handler_present,
            .poweroff_handler_claimed = registration.poweroff_handler_claimed and pm_base_handoff_ready,
            .poweroff_handler_conflict = registration.poweroff_handler_conflict,
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
        const clear_poweroff_handler_blocked_by_conflict =
            system_power_controller and poweroff_handler_present and !poweroff_handler_owned_by_driver;
        const clear_poweroff_handler_skipped_without_system_power_controller =
            !system_power_controller and poweroff_handler_present;
        const clear_poweroff_handler_skipped_without_handler =
            system_power_controller and !poweroff_handler_present;
        return .{
            .anchor = descriptor().anchor,
            .system_power_controller = system_power_controller,
            .poweroff_handler_present = poweroff_handler_present,
            .poweroff_handler_owned_by_driver = poweroff_handler_owned_by_driver,
            .remove_callback_ready = true,
            .watchdog_teardown_managed_by_devm = true,
            .remove_callback_scope_limited_to_poweroff_owner = true,
            .clear_poweroff_handler_requested = clear_poweroff_handler_requested,
            .clear_poweroff_handler_blocked_by_conflict = clear_poweroff_handler_blocked_by_conflict,
            .clear_poweroff_handler_skipped_without_system_power_controller = clear_poweroff_handler_skipped_without_system_power_controller,
            .clear_poweroff_handler_skipped_without_handler = clear_poweroff_handler_skipped_without_handler,
            .poweroff_handler_left_in_place = poweroff_handler_present and !clear_poweroff_handler_requested,
        };
    }

    pub fn poweroffSummary(
        self: *Self,
        system_power_controller: bool,
        poweroff_handler_present: bool,
        poweroff_handler_owned_by_driver: bool,
    ) PoweroffSummary {
        const poweroff_path_available =
            system_power_controller and poweroff_handler_present and poweroff_handler_owned_by_driver;
        const blocked_without_system_power_controller = !system_power_controller;
        const blocked_without_poweroff_handler = system_power_controller and !poweroff_handler_present;
        const blocked_by_poweroff_handler_conflict =
            system_power_controller and poweroff_handler_present and !poweroff_handler_owned_by_driver;

        if (!poweroff_path_available) {
            const runtime = self.runtimeSnapshot();
            return .{
                .anchor = descriptor().anchor,
                .system_power_controller = system_power_controller,
                .poweroff_handler_present = poweroff_handler_present,
                .poweroff_handler_owned_by_driver = poweroff_handler_owned_by_driver,
                .poweroff_callback_ready = false,
                .poweroff_path_available = false,
                .blocked_without_system_power_controller = blocked_without_system_power_controller,
                .blocked_without_poweroff_handler = blocked_without_poweroff_handler,
                .blocked_by_poweroff_handler_conflict = blocked_by_poweroff_handler_conflict,
                .full_reset_requested = runtime.full_reset_requested,
                .restart_armed = runtime.restart_armed,
                .halt_partition_requested = runtime.halt_partition_requested,
                .registers = runtime.registers,
            };
        }

        self.registers.rsts |= pm_password | pm_rsts_halt;
        const runtime = self.armRestart();
        return .{
            .anchor = descriptor().anchor,
            .system_power_controller = system_power_controller,
            .poweroff_handler_present = poweroff_handler_present,
            .poweroff_handler_owned_by_driver = poweroff_handler_owned_by_driver,
            .poweroff_callback_ready = true,
            .poweroff_path_available = true,
            .blocked_without_system_power_controller = false,
            .blocked_without_poweroff_handler = false,
            .blocked_by_poweroff_handler_conflict = false,
            .full_reset_requested = runtime.full_reset_requested,
            .restart_armed = runtime.restart_armed,
            .halt_partition_requested = runtime.halt_partition_requested,
            .registers = runtime.registers,
        };
    }

    pub fn loadRegisters(self: *Self, registers: RegisterImage) RuntimeSnapshot {
        self.registers = registers;
        return self.runtimeSnapshot();
    }

    pub fn isRunning(self: *const Self) bool {
        return (self.registers.rstc & pm_rstc_wrcfg_full_reset) != 0;
    }

    pub fn start(self: *Self) RuntimeSnapshot {
        self.registers.wdog = pm_password | (secondsToTicks(self.timeout_sec) & pm_wdog_time_set);
        self.registers.rstc = pm_password | (self.registers.rstc & pm_rstc_wrcfg_clr) | pm_rstc_wrcfg_full_reset;
        return self.runtimeSnapshot();
    }

    pub fn ping(self: *Self) RuntimeSnapshot {
        return self.start();
    }

    pub fn setTimeout(self: *Self, timeout_sec: u32) !RuntimeSnapshot {
        try validateTimeout(timeout_sec);
        self.timeout_sec = timeout_sec;
        return self.ping();
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
        const raw_ticks = self.registers.wdog & pm_wdog_time_set;
        return .{
            .anchor = descriptor().anchor,
            .running = running,
            .full_reset_requested = running,
            .restart_armed = running and raw_ticks == restart_ticks,
            .halt_partition_requested = (self.registers.rsts & pm_rsts_halt) == pm_rsts_halt,
            .timeout_sec = self.timeout_sec,
            .time_left_sec = if (running) ticksToSeconds(raw_ticks) else 0,
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
