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

pub const RestartSummary = struct {
    anchor: []const u8,
    running_before_restart: bool,
    running_after_restart: bool,
    full_reset_armed_after_restart: bool,
    halt_partition_requested: bool,
    restart_register_written: bool,
    programmed_ticks: u32,
    registers: RegisterImage,
};

pub const PlatformHandoffInput = struct {
    heartbeat_sec: u32,
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

pub const PoweroffOwner = enum {
    none,
    bcm2835,
    foreign,
};

pub const TeardownRequest = struct {
    nowayout: bool,
    system_power_controller: bool,
    poweroff_owner: PoweroffOwner,
    restart_handler_registered: bool,
};

pub const TeardownSummary = struct {
    anchor: []const u8,
    nowayout: bool,
    running_before_teardown: bool,
    running_after_teardown: bool,
    full_reset_armed_before_teardown: bool,
    full_reset_armed_after_teardown: bool,
    poweroff_owner: PoweroffOwner,
    poweroff_handler_released: bool,
    foreign_poweroff_handler_preserved: bool,
    restart_handler_unregistered: bool,
    reset_register_written: bool,
    blocked_on_live_remove_callback: bool,
};

pub fn summarizePlatformHandoff(input: PlatformHandoffInput) !PlatformHandoffSummary {
    validateTimeout(input.heartbeat_sec) catch |err| return err;

    const pm_base_handoff_ready = input.parent_attached and input.pm_base_present;
    const can_consider_poweroff = pm_base_handoff_ready and input.system_power_controller;

    return .{
        .anchor = anchor_path,
        .parent_attached = input.parent_attached,
        .parent_supplies_pm_base = input.parent_attached and input.pm_base_present,
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
    registers: RegisterImage = .{},

    pub fn init(heartbeat_sec: u32) !Self {
        try validateTimeout(heartbeat_sec);
        return .{ .heartbeat_sec = heartbeat_sec };
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

    pub fn restart(self: *Self) RestartSummary {
        const running_before_restart = self.isRunning();
        const restart_control = pm_password | (self.registers.rstc & pm_rstc_wrcfg_clr) | pm_rstc_wrcfg_full_reset;

        self.registers.wdog = pm_password | restart_timeout_ticks;
        self.registers.rstc = restart_control;

        return .{
            .anchor = anchor_path,
            .running_before_restart = running_before_restart,
            .running_after_restart = self.isRunning(),
            .full_reset_armed_after_restart = self.isRunning(),
            .halt_partition_requested = hasHaltPartition(self.registers),
            .restart_register_written = self.registers.rstc == restart_control,
            .programmed_ticks = self.registers.wdog & pm_wdog_time_set,
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

    pub fn summarizeTeardown(self: *Self, request: TeardownRequest) TeardownSummary {
        const running_before_teardown = self.isRunning();
        const full_reset_armed_before_teardown = running_before_teardown;

        if (!request.nowayout and running_before_teardown) {
            self.registers.rstc = pm_password | pm_rstc_reset;
        }

        return .{
            .anchor = anchor_path,
            .nowayout = request.nowayout,
            .running_before_teardown = running_before_teardown,
            .running_after_teardown = self.isRunning(),
            .full_reset_armed_before_teardown = full_reset_armed_before_teardown,
            .full_reset_armed_after_teardown = self.isRunning(),
            .poweroff_owner = request.poweroff_owner,
            .poweroff_handler_released = request.system_power_controller and request.poweroff_owner == .bcm2835,
            .foreign_poweroff_handler_preserved = request.poweroff_owner == .foreign,
            .restart_handler_unregistered = request.restart_handler_registered,
            .reset_register_written = !request.nowayout and running_before_teardown,
            .blocked_on_live_remove_callback = true,
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

test "bcm2835 restart summary keeps restart timeout programming explicit" {
    var running = try Bcm2835WdtLab.init(8);
    running.start();

    const restarted = running.restart();
    try @import("std").testing.expectEqualStrings(anchor_path, restarted.anchor);
    try @import("std").testing.expect(restarted.running_before_restart);
    try @import("std").testing.expect(restarted.running_after_restart);
    try @import("std").testing.expect(restarted.full_reset_armed_after_restart);
    try @import("std").testing.expect(!restarted.halt_partition_requested);
    try @import("std").testing.expect(restarted.restart_register_written);
    try @import("std").testing.expectEqual(@as(u32, restart_timeout_ticks), restarted.programmed_ticks);

    var idle = try Bcm2835WdtLab.init(8);
    const idle_restart = idle.restart();
    try @import("std").testing.expect(!idle_restart.running_before_restart);
    try @import("std").testing.expect(idle_restart.running_after_restart);
    try @import("std").testing.expect(idle_restart.full_reset_armed_after_restart);
    try @import("std").testing.expect(idle_restart.restart_register_written);
    try @import("std").testing.expectEqual(@as(u32, restart_timeout_ticks), idle_restart.programmed_ticks);
}

test "bcm2835 teardown summary releases bcm-owned poweroff handler after stop" {
    var lab = try Bcm2835WdtLab.init(8);
    lab.start();

    const teardown = lab.summarizeTeardown(.{
        .nowayout = false,
        .system_power_controller = true,
        .poweroff_owner = .bcm2835,
        .restart_handler_registered = true,
    });

    try @import("std").testing.expectEqualStrings(anchor_path, teardown.anchor);
    try @import("std").testing.expect(!teardown.nowayout);
    try @import("std").testing.expect(teardown.running_before_teardown);
    try @import("std").testing.expect(!teardown.running_after_teardown);
    try @import("std").testing.expect(teardown.full_reset_armed_before_teardown);
    try @import("std").testing.expect(!teardown.full_reset_armed_after_teardown);
    try @import("std").testing.expectEqual(PoweroffOwner.bcm2835, teardown.poweroff_owner);
    try @import("std").testing.expect(teardown.poweroff_handler_released);
    try @import("std").testing.expect(!teardown.foreign_poweroff_handler_preserved);
    try @import("std").testing.expect(teardown.restart_handler_unregistered);
    try @import("std").testing.expect(teardown.reset_register_written);
    try @import("std").testing.expect(teardown.blocked_on_live_remove_callback);
}

test "bcm2835 teardown summary preserves foreign ownership during nowayout remove" {
    var lab = try Bcm2835WdtLab.init(8);
    lab.start();

    const teardown = lab.summarizeTeardown(.{
        .nowayout = true,
        .system_power_controller = true,
        .poweroff_owner = .foreign,
        .restart_handler_registered = false,
    });

    try @import("std").testing.expect(teardown.nowayout);
    try @import("std").testing.expect(teardown.running_before_teardown);
    try @import("std").testing.expect(teardown.running_after_teardown);
    try @import("std").testing.expect(teardown.full_reset_armed_before_teardown);
    try @import("std").testing.expect(teardown.full_reset_armed_after_teardown);
    try @import("std").testing.expectEqual(PoweroffOwner.foreign, teardown.poweroff_owner);
    try @import("std").testing.expect(!teardown.poweroff_handler_released);
    try @import("std").testing.expect(teardown.foreign_poweroff_handler_preserved);
    try @import("std").testing.expect(!teardown.restart_handler_unregistered);
    try @import("std").testing.expect(!teardown.reset_register_written);
    try @import("std").testing.expect(teardown.blocked_on_live_remove_callback);
}

test "bcm2835 teardown summary keeps non-controller teardown from claiming release" {
    var lab = try Bcm2835WdtLab.init(8);
    lab.start();

    const teardown = lab.summarizeTeardown(.{
        .nowayout = false,
        .system_power_controller = false,
        .poweroff_owner = .bcm2835,
        .restart_handler_registered = true,
    });

    try @import("std").testing.expect(!teardown.nowayout);
    try @import("std").testing.expect(teardown.running_before_teardown);
    try @import("std").testing.expect(!teardown.running_after_teardown);
    try @import("std").testing.expectEqual(PoweroffOwner.bcm2835, teardown.poweroff_owner);
    try @import("std").testing.expect(!teardown.poweroff_handler_released);
    try @import("std").testing.expect(!teardown.foreign_poweroff_handler_preserved);
    try @import("std").testing.expect(teardown.restart_handler_unregistered);
    try @import("std").testing.expect(teardown.reset_register_written);
}
