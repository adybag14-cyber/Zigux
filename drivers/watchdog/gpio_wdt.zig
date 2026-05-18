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

pub const ProbeLineRequest = enum {
    input,
    output_low,
};

pub const DescriptorRequestFlags = enum {
    in,
    out_low,
};

pub const ProbeStartMode = enum {
    register_only,
    start_before_register,
};

pub const WatchdogOption = enum {
    magicclose,
    keepaliveping,
    settimeout,
};

pub const WatchdogOp = enum {
    start,
    stop,
    ping,
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

pub const ProbeSummary = struct {
    anchor: []const u8,
    hw_algo: HardwareAlgorithm,
    hw_margin_ms: u32,
    always_running: bool,
    nowayout: bool,
    requested_line: ProbeLineRequest,
    start_mode: ProbeStartMode,
    starts_during_probe: bool,
    pre_registration_running: bool,
    pre_registration_line_state: bool,
    pre_registration_line_is_output: bool,
    parent_attached: bool,
    stop_on_reboot: bool,
    timeout_init_requested: bool,
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

pub const StopDisposition = enum {
    blocked_by_nowayout,
    stopped,
    kept_running,
};

pub const StopSummary = struct {
    anchor: []const u8,
    hw_algo: HardwareAlgorithm,
    always_running: bool,
    nowayout: bool,
    disposition: StopDisposition,
    stop_allowed_by_watchdog_core: bool,
    driver_stop_invoked: bool,
    running: bool,
    line_state: bool,
    line_is_output: bool,
    disable_count: usize,
};

pub const RegistrationHandoffSummary = struct {
    anchor: []const u8,
    hw_algo: HardwareAlgorithm,
    always_running: bool,
    nowayout: bool,
    requested_line: ProbeLineRequest,
    start_mode: ProbeStartMode,
    reaches_registration_running: bool,
    reaches_registration_line_state: bool,
    reaches_registration_line_is_output: bool,
    stop_allowed_by_watchdog_core: bool,
    pre_registration_stop_disposition: StopDisposition,
    timeout_init_requested: bool,
    stop_on_reboot: bool,
    parent_attached: bool,
    module_owner_attached: bool,
    identity: []const u8,
    supported_options: [3]WatchdogOption,
    supported_ops: [3]WatchdogOp,
};

pub const DescriptorPreflightSummary = struct {
    anchor: []const u8,
    hw_algo: HardwareAlgorithm,
    requested_line: ProbeLineRequest,
    descriptor_flags: DescriptorRequestFlags,
    descriptor_lookup_required: bool,
    hw_algo_selected_before_lookup: bool,
    lookup_precedes_margin_validation: bool,
    lookup_precedes_always_running_read: bool,
    lookup_precedes_registration_handoff: bool,
    blocked_on_live_gpio_lookup: bool,
    blocked_on_platform_registration: bool,
};

pub const TimeoutPropertyCheckpointSummary = struct {
    anchor: []const u8,
    hw_algo: HardwareAlgorithm,
    hw_margin_ms: u32,
    timeout_property_name: []const u8,
    timeout_property_required: bool,
    descriptor_lookup_precedes_timeout_property: bool,
    timeout_property_precedes_always_running_read: bool,
    timeout_property_precedes_registration_handoff: bool,
    blocked_on_live_gpio_lookup: bool,
    blocked_on_platform_registration: bool,
};

pub const DrvdataOwnershipCheckpointSummary = struct {
    anchor: []const u8,
    hw_algo: HardwareAlgorithm,
    hw_margin_ms: u32,
    parent_attached: bool,
    module_owner_attached: bool,
    drvdata_owner_identity: []const u8,
    timeout_property_precedes_drvdata_binding: bool,
    drvdata_binding_precedes_registration_handoff: bool,
    drvdata_binding_reuses_parent_linkage: bool,
    blocked_on_live_gpio_lookup: bool,
    blocked_on_platform_registration: bool,
};

pub const RegistrationIntentCheckpointSummary = struct {
    anchor: []const u8,
    hw_algo: HardwareAlgorithm,
    always_running: bool,
    timeout_init_requested: bool,
    nowayout_from_module_param: bool,
    stop_on_reboot_requested: bool,
    pre_registration_start_requested: bool,
    timeout_init_stays_before_nowayout: bool,
    nowayout_stays_before_stop_on_reboot: bool,
    stop_on_reboot_stays_before_pre_registration_start: bool,
    pre_registration_start_stays_before_registration: bool,
    blocked_on_platform_registration: bool,
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

    pub fn probeSummary(self: *const Self, nowayout: bool) ProbeSummary {
        const starts_during_probe = self.always_running;

        return .{
            .anchor = descriptor().anchor,
            .hw_algo = self.hw_algo,
            .hw_margin_ms = self.hw_margin_ms,
            .always_running = self.always_running,
            .nowayout = nowayout,
            .requested_line = self.requestedLine(),
            .start_mode = if (starts_during_probe) .start_before_register else .register_only,
            .starts_during_probe = starts_during_probe,
            .pre_registration_running = starts_during_probe,
            .pre_registration_line_state = switch (self.hw_algo) {
                .toggle => starts_during_probe,
                .level => false,
            },
            .pre_registration_line_is_output = switch (self.hw_algo) {
                .toggle => starts_during_probe,
                .level => true,
            },
            .parent_attached = true,
            .stop_on_reboot = true,
            .timeout_init_requested = true,
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

    pub fn requestStop(self: *Self, nowayout: bool) StopSummary {
        if (nowayout) {
            return .{
                .anchor = descriptor().anchor,
                .hw_algo = self.hw_algo,
                .always_running = self.always_running,
                .nowayout = true,
                .disposition = .blocked_by_nowayout,
                .stop_allowed_by_watchdog_core = false,
                .driver_stop_invoked = false,
                .running = self.running,
                .line_state = self.line_state,
                .line_is_output = self.line_is_output,
                .disable_count = self.disable_count,
            };
        }

        const runtime = self.stop();
        return .{
            .anchor = descriptor().anchor,
            .hw_algo = self.hw_algo,
            .always_running = self.always_running,
            .nowayout = false,
            .disposition = if (self.always_running) .kept_running else .stopped,
            .stop_allowed_by_watchdog_core = true,
            .driver_stop_invoked = true,
            .running = runtime.running,
            .line_state = runtime.line_state,
            .line_is_output = runtime.line_is_output,
            .disable_count = runtime.disable_count,
        };
    }

    pub fn descriptorPreflightSummary(self: *const Self) DescriptorPreflightSummary {
        return .{
            .anchor = descriptor().anchor,
            .hw_algo = self.hw_algo,
            .requested_line = self.requestedLine(),
            .descriptor_flags = self.descriptorRequestFlags(),
            .descriptor_lookup_required = true,
            .hw_algo_selected_before_lookup = true,
            .lookup_precedes_margin_validation = true,
            .lookup_precedes_always_running_read = true,
            .lookup_precedes_registration_handoff = true,
            .blocked_on_live_gpio_lookup = true,
            .blocked_on_platform_registration = true,
        };
    }

    pub fn timeoutPropertyCheckpointSummary(self: *const Self) TimeoutPropertyCheckpointSummary {
        return .{
            .anchor = descriptor().anchor,
            .hw_algo = self.hw_algo,
            .hw_margin_ms = self.hw_margin_ms,
            .timeout_property_name = "hw_margin_ms",
            .timeout_property_required = true,
            .descriptor_lookup_precedes_timeout_property = true,
            .timeout_property_precedes_always_running_read = true,
            .timeout_property_precedes_registration_handoff = true,
            .blocked_on_live_gpio_lookup = true,
            .blocked_on_platform_registration = true,
        };
    }

    pub fn drvdataOwnershipCheckpointSummary(self: *const Self) DrvdataOwnershipCheckpointSummary {
        return .{
            .anchor = descriptor().anchor,
            .hw_algo = self.hw_algo,
            .hw_margin_ms = self.hw_margin_ms,
            .parent_attached = true,
            .module_owner_attached = true,
            .drvdata_owner_identity = "gpio_wdt_priv",
            .timeout_property_precedes_drvdata_binding = true,
            .drvdata_binding_precedes_registration_handoff = true,
            .drvdata_binding_reuses_parent_linkage = true,
            .blocked_on_live_gpio_lookup = true,
            .blocked_on_platform_registration = true,
        };
    }

    pub fn registrationIntentCheckpointSummary(self: *const Self, nowayout: bool) RegistrationIntentCheckpointSummary {
        const probe = self.probeSummary(nowayout);
        return .{
            .anchor = descriptor().anchor,
            .hw_algo = self.hw_algo,
            .always_running = self.always_running,
            .timeout_init_requested = probe.timeout_init_requested,
            .nowayout_from_module_param = nowayout,
            .stop_on_reboot_requested = probe.stop_on_reboot,
            .pre_registration_start_requested = probe.starts_during_probe,
            .timeout_init_stays_before_nowayout = true,
            .nowayout_stays_before_stop_on_reboot = true,
            .stop_on_reboot_stays_before_pre_registration_start = true,
            .pre_registration_start_stays_before_registration = true,
            .blocked_on_platform_registration = true,
        };
    }

    pub fn registrationHandoffSummary(self: *const Self, nowayout: bool) RegistrationHandoffSummary {
        const probe = self.probeSummary(nowayout);
        return .{
            .anchor = descriptor().anchor,
            .hw_algo = self.hw_algo,
            .always_running = self.always_running,
            .nowayout = nowayout,
            .requested_line = probe.requested_line,
            .start_mode = probe.start_mode,
            .reaches_registration_running = probe.pre_registration_running,
            .reaches_registration_line_state = probe.pre_registration_line_state,
            .reaches_registration_line_is_output = probe.pre_registration_line_is_output,
            .stop_allowed_by_watchdog_core = !nowayout,
            .pre_registration_stop_disposition = if (nowayout)
                .blocked_by_nowayout
            else if (self.always_running)
                .kept_running
            else
                .stopped,
            .timeout_init_requested = probe.timeout_init_requested,
            .stop_on_reboot = probe.stop_on_reboot,
            .parent_attached = probe.parent_attached,
            .module_owner_attached = true,
            .identity = "GPIO Watchdog",
            .supported_options = .{ .magicclose, .keepaliveping, .settimeout },
            .supported_ops = .{ .start, .stop, .ping },
        };
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

    fn requestedLine(self: *const Self) ProbeLineRequest {
        return switch (self.hw_algo) {
            .toggle => .input,
            .level => .output_low,
        };
    }

    fn descriptorRequestFlags(self: *const Self) DescriptorRequestFlags {
        return switch (self.hw_algo) {
            .toggle => .in,
            .level => .out_low,
        };
    }
};

fn validateHeartbeatMargin(hw_margin_ms: u32) !void {
    if (hw_margin_ms < min_hw_margin_ms) return error.HeartbeatMarginTooSmall;
    if (hw_margin_ms > max_hw_margin_ms) return error.HeartbeatMarginTooLarge;
}
