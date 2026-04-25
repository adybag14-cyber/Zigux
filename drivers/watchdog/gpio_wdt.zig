const std = @import("std");

pub const soft_timeout_min: u32 = 1;
pub const soft_timeout_default: u32 = 60;
pub const min_hw_margin_ms: u32 = 2;
pub const max_hw_margin_ms: u32 = 65_535;
pub const level_pulse_width_usec: u32 = 1;

pub const HardwareAlgorithm = enum {
    toggle,
    level,
};

pub const ModuleDescriptor = struct {
    name: []const u8,
    anchor: []const u8,
    provides_simple_driver_starter: bool,
    touches_platform_registration: bool,
    touches_live_gpio: bool,
};

pub const ConfigSnapshot = struct {
    anchor: []const u8,
    hw_algo: HardwareAlgorithm,
    hw_margin_ms: u32,
    always_running: bool,
    min_timeout_sec: u32,
    default_timeout_sec: u32,
    max_hw_heartbeat_ms: u32,
};

pub const RuntimeSnapshot = struct {
    anchor: []const u8,
    hw_algo: HardwareAlgorithm,
    always_running: bool,
    running: bool,
    line_state: bool,
    line_is_output: bool,
    ping_count: usize,
    pulse_count: usize,
    disable_count: usize,
    last_ping_was_pulse: bool,
    last_pulse_width_usec: u32,
};

pub const GpioWatchdogLab = struct {
    const Self = @This();

    hw_algo: HardwareAlgorithm,
    hw_margin_ms: u32,
    always_running: bool,
    line_state: bool = false,
    line_is_output: bool = false,
    running: bool = false,
    ping_count: usize = 0,
    pulse_count: usize = 0,
    disable_count: usize = 0,
    last_ping_was_pulse: bool = false,
    last_pulse_width_usec: u32 = 0,

    pub fn descriptor() ModuleDescriptor {
        return .{
            .name = "gpio_wdt_lab",
            .anchor = "drivers/watchdog/gpio_wdt.c",
            .provides_simple_driver_starter = true,
            .touches_platform_registration = false,
            .touches_live_gpio = false,
        };
    }

    pub fn parseHardwareAlgorithm(algo: []const u8) !HardwareAlgorithm {
        if (std.mem.eql(u8, algo, "toggle")) return .toggle;
        if (std.mem.eql(u8, algo, "level")) return .level;
        return error.InvalidHardwareAlgorithm;
    }

    pub fn initFromPropertyString(
        algo: []const u8,
        hw_margin_ms: u32,
        always_running: bool,
    ) !Self {
        return init(try parseHardwareAlgorithm(algo), hw_margin_ms, always_running);
    }

    pub fn init(
        hw_algo: HardwareAlgorithm,
        hw_margin_ms: u32,
        always_running: bool,
    ) !Self {
        try validateHeartbeatMargin(hw_margin_ms);

        return .{
            .hw_algo = hw_algo,
            .hw_margin_ms = hw_margin_ms,
            .always_running = always_running,
        };
    }

    pub fn configSnapshot(self: *const Self) ConfigSnapshot {
        return .{
            .anchor = descriptor().anchor,
            .hw_algo = self.hw_algo,
            .hw_margin_ms = self.hw_margin_ms,
            .always_running = self.always_running,
            .min_timeout_sec = soft_timeout_min,
            .default_timeout_sec = soft_timeout_default,
            .max_hw_heartbeat_ms = self.hw_margin_ms,
        };
    }

    pub fn runtimeSnapshot(self: *const Self) RuntimeSnapshot {
        return .{
            .anchor = descriptor().anchor,
            .hw_algo = self.hw_algo,
            .always_running = self.always_running,
            .running = self.running,
            .line_state = self.line_state,
            .line_is_output = self.line_is_output,
            .ping_count = self.ping_count,
            .pulse_count = self.pulse_count,
            .disable_count = self.disable_count,
            .last_ping_was_pulse = self.last_ping_was_pulse,
            .last_pulse_width_usec = self.last_pulse_width_usec,
        };
    }

    pub fn start(self: *Self) !RuntimeSnapshot {
        self.line_state = false;
        self.line_is_output = true;
        self.running = true;
        return self.ping();
    }

    pub fn ping(self: *Self) !RuntimeSnapshot {
        if (!self.running) return error.WatchdogNotRunning;

        self.ping_count += 1;
        self.last_ping_was_pulse = false;
        self.last_pulse_width_usec = 0;

        switch (self.hw_algo) {
            .toggle => {
                self.line_state = !self.line_state;
            },
            .level => {
                self.line_state = true;
                self.pulse_count += 1;
                self.last_ping_was_pulse = true;
                self.last_pulse_width_usec = level_pulse_width_usec;
                self.line_state = false;
            },
        }

        return self.runtimeSnapshot();
    }

    pub fn stop(self: *Self) RuntimeSnapshot {
        if (!self.always_running) {
            self.disable();
        } else {
            self.running = true;
        }

        return self.runtimeSnapshot();
    }

    fn disable(self: *Self) void {
        self.disable_count += 1;
        self.line_state = true;
        self.running = false;
        self.last_ping_was_pulse = false;
        self.last_pulse_width_usec = 0;

        if (self.hw_algo == .toggle) {
            self.line_is_output = false;
        }
    }
};

fn validateHeartbeatMargin(hw_margin_ms: u32) !void {
    if (hw_margin_ms < min_hw_margin_ms) return error.HeartbeatMarginTooSmall;
    if (hw_margin_ms > max_hw_margin_ms) return error.HeartbeatMarginTooLarge;
}
