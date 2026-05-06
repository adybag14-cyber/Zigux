const std = @import("std");

pub const control_reg_offset: u32 = 0x00;
pub const control_reg_wdt_en_mask: u32 = 0x01;
pub const control_reg_resp_mode_mask: u32 = 0x02;
pub const timeout_range_reg_offset: u32 = 0x04;
pub const timeout_range_topinit_shift: u5 = 4;
pub const current_count_reg_offset: u32 = 0x08;
pub const counter_restart_reg_offset: u32 = 0x0c;
pub const counter_restart_kick_value: u32 = 0x76;
pub const interrupt_status_reg_offset: u32 = 0x10;
pub const interrupt_clear_reg_offset: u32 = 0x14;
pub const default_timeout_sec: u32 = 30;
pub const default_restart_priority: i32 = 128;
pub const num_tops: usize = 16;

pub const ResponseMode = enum(u2) {
    reset = 1,
    irq = 2,
};

pub const TopSource = enum {
    fixed,
    custom,
};

pub const ProbeTimeoutOrigin = enum {
    default_selection,
    imported_running_state,
};

pub const ModuleDescriptor = struct {
    name: []const u8,
    anchor: []const u8,
    provides_simple_driver_starter: bool,
    touches_platform_registration: bool,
    touches_live_mmio: bool,
    touches_irq_registration: bool,
};

pub const WatchdogInfoProfile = struct {
    identity: []const u8,
    supports_keepalive_ping: bool,
    supports_set_timeout: bool,
    supports_magic_close: bool,
    supports_pretimeout: bool,
};

pub const WatchdogOpsProfile = struct {
    start: bool,
    stop: bool,
    ping: bool,
    set_timeout: bool,
    set_pretimeout: bool,
    get_timeleft: bool,
    restart: bool,
};

pub const TimeoutWindow = struct {
    top_val: u32,
    sec: u32,
    msec: u32,
};

pub const RegisterImage = struct {
    control: u32 = 0,
    timeout_range: u32 = 0,
    current_count: u32 = 0,
    restart: u32 = 0,
    interrupt_status: u32 = 0,
};

pub const ConfigSnapshot = struct {
    anchor: []const u8,
    rate_hz: u32,
    response_mode: ResponseMode,
    timeout_sec: u32,
    pretimeout_sec: u32,
    min_timeout_sec: u32,
    max_hw_heartbeat_ms: u32,
    can_stop: bool,
};

pub const ProbeOptions = struct {
    nowayout: bool = true,
    restart_priority: i32 = default_restart_priority,
    requested_timeout_sec: ?u32 = null,
    stop_on_reboot: bool = true,
};

pub const ProbeSummary = struct {
    anchor: []const u8,
    top_source: TopSource,
    timeout_origin: ProbeTimeoutOrigin,
    rate_hz: u32,
    response_mode: ResponseMode,
    timeout_sec: u32,
    pretimeout_sec: u32,
    nowayout: bool,
    restart_priority: i32,
    stop_on_reboot: bool,
    can_stop: bool,
    already_running: bool,
    hardware_running: bool,
};

pub const RegistrationSummary = struct {
    anchor: []const u8,
    registration_call: []const u8,
    parent_anchor: []const u8,
    info: WatchdogInfoProfile,
    ops: WatchdogOpsProfile,
    timeout_origin: ProbeTimeoutOrigin,
    nowayout: bool,
    restart_priority: i32,
    stop_on_reboot: bool,
    can_stop: bool,
    min_timeout_sec: u32,
    max_hw_heartbeat_ms: u32,
    timeout_sec: u32,
    pretimeout_sec: u32,
    hardware_running: bool,
    imported_running_state: bool,
    needs_timeout_programming: bool,
};

pub const RemoveSummary = struct {
    anchor: []const u8,
    debugfs_clear_requested: bool,
    unregister_device_requested: bool,
    reset_control_available: bool,
    reset_assert_requested: bool,
    hardware_running_before_remove: bool,
    hardware_running_after_remove: bool,
    running_after_remove: bool,
    interrupt_pending_after_remove: bool,
    remove_leaves_hardware_running: bool,
};

pub const RuntimeSnapshot = struct {
    anchor: []const u8,
    running: bool,
    hardware_running: bool,
    response_mode: ResponseMode,
    timeout_sec: u32,
    pretimeout_sec: u32,
    interrupt_pending: bool,
    restart_armed: bool,
    time_left_sec: u32,
    registers: RegisterImage,
};

pub const DwWdtLab = struct {
    const Self = @This();

    rate_hz: u32,
    has_reset_control: bool,
    top_source: TopSource = .fixed,
    response_mode: ResponseMode = .reset,
    requested_timeout_sec: u32 = default_timeout_sec,
    actual_timeout_sec: u32 = default_timeout_sec,
    pretimeout_sec: u32 = 0,
    hardware_running: bool = false,
    timeouts: [num_tops]TimeoutWindow,
    registers: RegisterImage = .{},

    pub fn descriptor() ModuleDescriptor {
        return .{
            .name = "dw_wdt_lab",
            .anchor = "drivers/watchdog/dw_wdt.c",
            .provides_simple_driver_starter = true,
            .touches_platform_registration = false,
            .touches_live_mmio = false,
            .touches_irq_registration = false,
        };
    }

    pub fn infoProfile(has_pretimeout_irq: bool) WatchdogInfoProfile {
        return .{
            .identity = "Synopsys DesignWare Watchdog",
            .supports_keepalive_ping = true,
            .supports_set_timeout = true,
            .supports_magic_close = true,
            .supports_pretimeout = has_pretimeout_irq,
        };
    }

    pub fn opsProfile() WatchdogOpsProfile {
        return .{
            .start = true,
            .stop = true,
            .ping = true,
            .set_timeout = true,
            .set_pretimeout = true,
            .get_timeleft = true,
            .restart = true,
        };
    }

    pub fn initFixedTops(rate_hz: u32, has_reset_control: bool) !Self {
        if (rate_hz == 0) return error.InvalidClockRate;

        var self = Self{
            .rate_hz = rate_hz,
            .has_reset_control = has_reset_control,
            .top_source = .fixed,
            .timeouts = calculateFixedTimeouts(rate_hz),
        };
        if (self.timeouts[num_tops - 1].sec == 0 and self.timeouts[num_tops - 1].msec == 0) {
            return error.NoValidTop;
        }

        _ = try self.setTimeout(default_timeout_sec);
        return self;
    }

    pub fn initCustomTops(rate_hz: u32, has_reset_control: bool, tops: [num_tops]u32) !Self {
        if (rate_hz == 0) return error.InvalidClockRate;

        var self = Self{
            .rate_hz = rate_hz,
            .has_reset_control = has_reset_control,
            .top_source = .custom,
            .timeouts = calculateCustomTimeouts(rate_hz, tops),
        };
        if (self.timeouts[num_tops - 1].sec == 0 and self.timeouts[num_tops - 1].msec == 0) {
            return error.NoValidTop;
        }

        _ = try self.setTimeout(default_timeout_sec);
        return self;
    }

    pub fn configSnapshot(self: *const Self) ConfigSnapshot {
        return .{
            .anchor = descriptor().anchor,
            .rate_hz = self.rate_hz,
            .response_mode = self.response_mode,
            .timeout_sec = self.actual_timeout_sec,
            .pretimeout_sec = self.pretimeout_sec,
            .min_timeout_sec = self.getMinTimeout(),
            .max_hw_heartbeat_ms = self.getMaxTimeoutMs(),
            .can_stop = self.has_reset_control,
        };
    }

    pub fn probeSummary(self: *Self, options: ProbeOptions) !ProbeSummary {
        const already_running = self.isEnabled();
        const timeout_origin: ProbeTimeoutOrigin = if (already_running) blk: {
            self.syncStateFromRegisters();
            break :blk .imported_running_state;
        } else blk: {
            _ = try self.setTimeout(options.requested_timeout_sec orelse self.requested_timeout_sec);
            break :blk .default_selection;
        };

        return .{
            .anchor = descriptor().anchor,
            .top_source = self.top_source,
            .timeout_origin = timeout_origin,
            .rate_hz = self.rate_hz,
            .response_mode = self.response_mode,
            .timeout_sec = self.actual_timeout_sec,
            .pretimeout_sec = self.pretimeout_sec,
            .nowayout = options.nowayout,
            .restart_priority = options.restart_priority,
            .stop_on_reboot = options.stop_on_reboot,
            .can_stop = self.has_reset_control,
            .already_running = already_running,
            .hardware_running = self.hardware_running,
        };
    }

    pub fn registrationSummary(
        self: *Self,
        options: ProbeOptions,
        has_pretimeout_irq: bool,
    ) !RegistrationSummary {
        const probe = try self.probeSummary(options);
        return .{
            .anchor = descriptor().anchor,
            .registration_call = "watchdog_register_device",
            .parent_anchor = "platform_device.dev",
            .info = infoProfile(has_pretimeout_irq),
            .ops = opsProfile(),
            .timeout_origin = probe.timeout_origin,
            .nowayout = probe.nowayout,
            .restart_priority = probe.restart_priority,
            .stop_on_reboot = probe.stop_on_reboot,
            .can_stop = probe.can_stop,
            .min_timeout_sec = self.getMinTimeout(),
            .max_hw_heartbeat_ms = self.getMaxTimeoutMs(),
            .timeout_sec = probe.timeout_sec,
            .pretimeout_sec = if (has_pretimeout_irq) probe.pretimeout_sec else 0,
            .hardware_running = probe.hardware_running,
            .imported_running_state = probe.timeout_origin == .imported_running_state,
            .needs_timeout_programming = probe.timeout_origin == .default_selection,
        };
    }

    pub fn timeoutWindows(self: *const Self) []const TimeoutWindow {
        return self.timeouts[0..];
    }

    pub fn loadRegisters(self: *Self, registers: RegisterImage) RuntimeSnapshot {
        self.registers = registers;
        self.syncStateFromRegisters();
        return self.runtimeSnapshot();
    }

    pub fn setCurrentCount(self: *Self, current_count: u32) RuntimeSnapshot {
        self.registers.current_count = current_count;
        return self.runtimeSnapshot();
    }

    pub fn setInterruptPending(self: *Self, pending: bool) RuntimeSnapshot {
        self.registers.interrupt_status = if (pending) 1 else 0;
        return self.runtimeSnapshot();
    }

    pub fn setResponseMode(self: *Self, response_mode: ResponseMode) !ConfigSnapshot {
        self.response_mode = response_mode;
        return self.setTimeout(self.requested_timeout_sec);
    }

    pub fn setTimeout(self: *Self, requested_timeout_sec: u32) !ConfigSnapshot {
        self.requested_timeout_sec = requested_timeout_sec;

        const requested_stage_timeout = divCeil(
            requested_timeout_sec,
            @intFromEnum(self.response_mode),
        );
        const selected = self.findBestTop(requested_stage_timeout);

        self.actual_timeout_sec = selected.sec * @intFromEnum(self.response_mode);
        self.pretimeout_sec = if (self.response_mode == .irq) selected.sec else 0;
        self.registers.timeout_range =
            selected.top_val | (selected.top_val << timeout_range_topinit_shift);

        return self.configSnapshot();
    }

    pub fn ping(self: *Self) !RuntimeSnapshot {
        if (!self.isEnabled()) return error.WatchdogNotRunning;
        self.registers.restart = counter_restart_kick_value;
        self.hardware_running = true;
        return self.runtimeSnapshot();
    }

    pub fn start(self: *Self) !RuntimeSnapshot {
        _ = try self.setTimeout(self.requested_timeout_sec);
        self.registers.restart = counter_restart_kick_value;

        var control = self.registers.control;
        if (self.response_mode == .irq) {
            control |= control_reg_resp_mode_mask;
        } else {
            control &= ~control_reg_resp_mode_mask;
        }
        control |= control_reg_wdt_en_mask;
        self.registers.control = control;
        self.hardware_running = true;

        return self.runtimeSnapshot();
    }

    pub fn stop(self: *Self) RuntimeSnapshot {
        if (!self.has_reset_control) {
            if (self.isEnabled()) self.hardware_running = true;
            return self.runtimeSnapshot();
        }

        self.registers.control &= ~control_reg_wdt_en_mask;
        self.registers.current_count = 0;
        self.registers.interrupt_status = 0;
        self.hardware_running = false;
        return self.runtimeSnapshot();
    }

    pub fn removeSummary(self: *Self) RemoveSummary {
        const before = self.runtimeSnapshot();

        if (self.has_reset_control) {
            self.registers.control = 0;
            self.registers.timeout_range = 0;
            self.registers.current_count = 0;
            self.registers.restart = 0;
            self.registers.interrupt_status = 0;
            self.hardware_running = false;
        } else if (self.isEnabled()) {
            self.hardware_running = true;
        }

        const after = self.runtimeSnapshot();
        return .{
            .anchor = descriptor().anchor,
            .debugfs_clear_requested = true,
            .unregister_device_requested = true,
            .reset_control_available = self.has_reset_control,
            .reset_assert_requested = self.has_reset_control,
            .hardware_running_before_remove = before.hardware_running,
            .hardware_running_after_remove = after.hardware_running,
            .running_after_remove = after.running,
            .interrupt_pending_after_remove = after.interrupt_pending,
            .remove_leaves_hardware_running = after.hardware_running,
        };
    }

    pub fn armRestart(self: *Self) RuntimeSnapshot {
        self.response_mode = .reset;
        self.pretimeout_sec = 0;
        self.registers.timeout_range = 0;

        if (self.isEnabled()) {
            self.registers.restart = counter_restart_kick_value;
        } else {
            self.registers.control &= ~control_reg_resp_mode_mask;
            self.registers.control |= control_reg_wdt_en_mask;
        }

        self.hardware_running = true;
        return self.runtimeSnapshot();
    }

    pub fn runtimeSnapshot(self: *const Self) RuntimeSnapshot {
        const running = self.isEnabled();
        return .{
            .anchor = descriptor().anchor,
            .running = running,
            .hardware_running = self.hardware_running,
            .response_mode = self.response_mode,
            .timeout_sec = self.actual_timeout_sec,
            .pretimeout_sec = self.pretimeout_sec,
            .interrupt_pending = self.registers.interrupt_status != 0,
            .restart_armed = running and (self.registers.timeout_range & 0xf) == 0,
            .time_left_sec = if (running) self.getTimeLeftSeconds() else 0,
            .registers = self.registers,
        };
    }

    pub fn getMinTimeout(self: *const Self) u32 {
        for (self.timeouts) |timeout| {
            if (timeout.sec != 0 or timeout.msec != 0) return timeout.sec;
        }
        return 0;
    }

    pub fn getMaxTimeoutMs(self: *const Self) u32 {
        const timeout = self.timeouts[num_tops - 1];
        const total = @as(u64, timeout.sec) * std.time.ms_per_s + timeout.msec;
        return if (total > std.math.maxInt(u32)) std.math.maxInt(u32) else @intCast(total);
    }

    fn isEnabled(self: *const Self) bool {
        return (self.registers.control & control_reg_wdt_en_mask) != 0;
    }

    fn syncStateFromRegisters(self: *Self) void {
        self.hardware_running = self.isEnabled();
        self.response_mode = if ((self.registers.control & control_reg_resp_mode_mask) != 0) .irq else .reset;

        const timeout = self.timeouts[self.registers.timeout_range & 0xf];
        self.actual_timeout_sec = timeout.sec * @intFromEnum(self.response_mode);
        self.pretimeout_sec = if (self.response_mode == .irq) timeout.sec else 0;
    }

    fn getTimeLeftSeconds(self: *const Self) u32 {
        var seconds = self.registers.current_count / self.rate_hz;
        if (self.response_mode == .irq and self.registers.interrupt_status == 0) {
            seconds += self.pretimeout_sec;
        }
        return seconds;
    }

    fn findBestTop(self: *const Self, requested_timeout_sec: u32) TimeoutWindow {
        for (self.timeouts) |timeout| {
            if (timeout.sec >= requested_timeout_sec) return timeout;
        }
        return self.timeouts[num_tops - 1];
    }
};

fn calculateFixedTimeouts(rate_hz: u32) [num_tops]TimeoutWindow {
    var timeouts: [num_tops]TimeoutWindow = undefined;
    for (0..num_tops) |index| {
        timeouts[index] = timeoutWindowFromCycles(index, fixedTopCycles(index), rate_hz);
    }
    return timeouts;
}

fn calculateCustomTimeouts(rate_hz: u32, tops: [num_tops]u32) [num_tops]TimeoutWindow {
    var timeouts: [num_tops]TimeoutWindow = undefined;
    var inserted: usize = 0;

    for (tops, 0..) |cycles, index| {
        const next = timeoutWindowFromCycles(index, cycles, rate_hz);
        var insert_at = inserted;
        while (insert_at > 0) : (insert_at -= 1) {
            const previous = timeouts[insert_at - 1];
            if (previous.sec < next.sec or
                (previous.sec == next.sec and previous.msec <= next.msec))
            {
                break;
            }
            timeouts[insert_at] = previous;
        }
        timeouts[insert_at] = next;
        inserted += 1;
    }

    return timeouts;
}

fn timeoutWindowFromCycles(index: usize, cycles: u64, rate_hz: u32) TimeoutWindow {
    const total_msec = (cycles * std.time.ms_per_s) / rate_hz;
    return .{
        .top_val = @intCast(index),
        .sec = @intCast(total_msec / std.time.ms_per_s),
        .msec = @intCast(total_msec % std.time.ms_per_s),
    };
}

fn fixedTopCycles(index: usize) u64 {
    return @as(u64, 1) << @intCast(16 + index);
}

fn divCeil(value: u32, divisor: u32) u32 {
    return @intCast((@as(u64, value) + divisor - 1) / divisor);
}

test "remove with reset control quiesces hardware and clears pending irq state" {
    var lab = try DwWdtLab.initFixedTops(1_000_000, true);
    _ = try lab.start();
    _ = lab.setInterruptPending(true);

    const summary = lab.removeSummary();
    try std.testing.expect(summary.debugfs_clear_requested);
    try std.testing.expect(summary.unregister_device_requested);
    try std.testing.expect(summary.reset_control_available);
    try std.testing.expect(summary.reset_assert_requested);
    try std.testing.expect(summary.hardware_running_before_remove);
    try std.testing.expect(!summary.hardware_running_after_remove);
    try std.testing.expect(!summary.running_after_remove);
    try std.testing.expect(!summary.interrupt_pending_after_remove);
    try std.testing.expect(!summary.remove_leaves_hardware_running);
}

test "remove without reset control leaves active hardware running after unregister" {
    var lab = try DwWdtLab.initFixedTops(1_000_000, false);
    _ = try lab.start();

    const summary = lab.removeSummary();
    try std.testing.expect(summary.debugfs_clear_requested);
    try std.testing.expect(summary.unregister_device_requested);
    try std.testing.expect(!summary.reset_control_available);
    try std.testing.expect(!summary.reset_assert_requested);
    try std.testing.expect(summary.hardware_running_before_remove);
    try std.testing.expect(summary.hardware_running_after_remove);
    try std.testing.expect(summary.running_after_remove);
    try std.testing.expect(summary.remove_leaves_hardware_running);
}
