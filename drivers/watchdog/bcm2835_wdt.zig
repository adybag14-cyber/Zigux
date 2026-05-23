pub const anchor_path = "drivers/watchdog/bcm2835_wdt.c";

pub const pm_password: u32 = 0x5a00_0000;
pub const pm_rsts_halt: u32 = 0x0000_0555;
pub const pm_wdog_time_set: u32 = 0x000f_ffff;
pub const pm_rstc_wrcfg_clr: u32 = 0xffff_ffcf;
pub const pm_rstc_wrcfg_full_reset: u32 = 0x0000_0020;
pub const pm_rstc_reset: u32 = 0x0000_0102;
pub const restart_timeout_ticks: u32 = 10;
pub const restart_priority: i32 = 128;
pub const min_timeout_sec: u32 = 1;
pub const max_timeout_sec: u32 = pm_wdog_time_set >> 16;

pub const RegisterImage = struct {
    rstc: u32 = 0,
    rsts: u32 = 0,
    wdog: u32 = 0,
};

pub const RuntimeSnapshot = struct {
    anchor: []const u8,
    running_before_stop: bool,
    running_after_stop: bool,
    running_after_poweroff: bool,
    full_reset_armed: bool,
    full_reset_armed_after_stop: bool,
    halt_partition_requested: bool,
    reset_register_written: bool,
    programmed_ticks: u32,
    restart_path_reused: bool,
    registers: RegisterImage,
};

pub const PlatformHandoffInput = struct {
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
    parent_attached: bool,
    parent_supplies_pm_base: bool,
    pm_base_required: bool,
    pm_base_handoff_ready: bool,
    timeout_init_requested: bool,
    register_device_requested: bool,
    stop_on_reboot_requested: bool,
    restart_priority_value: i32,
    poweroff_handler_claimed: bool,
    poweroff_handler_conflict: bool,
    blocked_on_live_platform_registration: bool,
};

pub fn summarizePlatformHandoff(input: PlatformHandoffInput) !PlatformHandoffSummary {
    validateTimeout(input.heartbeat_sec) catch |err| return err;

    const pm_base_handoff_ready = input.parent_attached and input.pm_base_present;
    const can_consider_poweroff = pm_base_handoff_ready and input.system_power_controller;

    return .{
        .anchor = anchor_path,
        .parent_attached = input.parent_attached,
        .parent_supplies_pm_base = input.pm_base_present,
        .pm_base_required = true,
        .pm_base_handoff_ready = pm_base_handoff_ready,
        .timeout_init_requested = true,
        .register_device_requested = pm_base_handoff_ready,
        .stop_on_reboot_requested = true,
        .restart_priority_value = restart_priority,
        .poweroff_handler_claimed = can_consider_poweroff and !input.poweroff_handler_present,
        .poweroff_handler_conflict = can_consider_poweroff and input.poweroff_handler_present,
        .blocked_on_live_platform_registration = true,
    };
}

pub const Bcm2835WdtLab = struct {
    const Self = @This();

    heartbeat_sec: u32,
    bootloader_running: bool = false,
    registers: RegisterImage = .{},

    pub fn init(heartbeat_sec: u32) !Self {
        try validateTimeout(heartbeat_sec);
        return .{ .heartbeat_sec = heartbeat_sec };
    }

    pub fn importBootloaderRunning(self: *Self) void {
        self.bootloader_running = true;
    }

    pub fn start(self: *Self) void {
        self.registers.wdog = pm_password | secondsToTicks(self.heartbeat_sec);
        self.registers.rstc = pm_password | (self.registers.rstc & pm_rstc_wrcfg_clr) | pm_rstc_wrcfg_full_reset;
    }

    pub fn stop(self: *Self) RuntimeSnapshot {
        const running_before_stop = self.isRunning();
        self.registers.rstc = pm_password | pm_rstc_reset;
        return .{
            .anchor = anchor_path,
            .running_before_stop = running_before_stop,
            .running_after_stop = self.isRunning(),
            .running_after_poweroff = false,
            .full_reset_armed = false,
            .full_reset_armed_after_stop = self.isRunning(),
            .halt_partition_requested = hasHaltPartition(self.registers),
            .reset_register_written = self.registers.rstc == (pm_password | pm_rstc_reset),
            .programmed_ticks = self.registers.wdog & pm_wdog_time_set,
            .restart_path_reused = false,
            .registers = self.registers,
        };
    }

    pub fn poweroff(self: *Self, owns_poweroff_handler: bool) RuntimeSnapshot {
        if (owns_poweroff_handler) {
            self.registers.rsts |= pm_password | pm_rsts_halt;
            self.registers.wdog = pm_password | restart_timeout_ticks;
            self.registers.rstc = pm_password | (self.registers.rstc & pm_rstc_wrcfg_clr) | pm_rstc_wrcfg_full_reset;
        }

        return .{
            .anchor = anchor_path,
            .running_before_stop = false,
            .running_after_stop = false,
            .running_after_poweroff = self.isRunning(),
            .full_reset_armed = self.isRunning(),
            .full_reset_armed_after_stop = false,
            .halt_partition_requested = hasHaltPartition(self.registers),
            .reset_register_written = false,
            .programmed_ticks = self.registers.wdog & pm_wdog_time_set,
            .restart_path_reused = true,
            .registers = self.registers,
        };
    }

    fn isRunning(self: *const Self) bool {
        return (self.registers.rstc & pm_rstc_wrcfg_full_reset) != 0;
    }
};

pub fn secondsToTicks(seconds: u32) u32 {
    return seconds << 16;
}

fn hasHaltPartition(registers: RegisterImage) bool {
    return (registers.rsts & pm_rsts_halt) == pm_rsts_halt;
}

fn validateTimeout(timeout_sec: u32) !void {
    if (timeout_sec < min_timeout_sec) return error.TimeoutTooSmall;
    if (timeout_sec > max_timeout_sec) return error.TimeoutTooLarge;
}
