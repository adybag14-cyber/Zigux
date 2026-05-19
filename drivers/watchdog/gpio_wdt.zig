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

pub const StopDisposition = enum {
    blocked_by_nowayout,
    stopped,
    kept_running,
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

pub const PlatformDriverIdentitySummary = struct {
    anchor: []const u8,
    module_name: []const u8,
    identity: []const u8,
    provides_simple_driver_starter: bool,
    blocked_on_platform_registration: bool,
};

pub const WatchdogMetadataSummary = struct {
    anchor: []const u8,
    identity: []const u8,
    timeout_init_requested: bool,
    stop_on_reboot: bool,
    parent_attached: bool,
    module_owner_attached: bool,
    supported_options: [3]WatchdogOption,
    supported_ops: [3]WatchdogOp,
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

pub const DescriptorRequestSummary = struct {
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

pub const PlatformDrvdataCheckpointSummary = struct {
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

pub const NowayoutPolicySummary = struct {
    anchor: []const u8,
    hw_algo: HardwareAlgorithm,
    always_running: bool,
    nowayout: bool,
    stop_allowed_by_watchdog_core: bool,
    disposition_if_stop_requested: StopDisposition,
    driver_stop_invoked: bool,
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

pub const RegistrationPlanSummary = struct {
    anchor: []const u8,
    hw_algo: HardwareAlgorithm,
    requested_line: ProbeLineRequest,
    descriptor_flags: DescriptorRequestFlags,
    start_mode: ProbeStartMode,
    reaches_registration_running: bool,
    reaches_registration_line_state: bool,
    reaches_registration_line_is_output: bool,
    timeout_init_requested: bool,
    stop_on_reboot: bool,
    parent_attached: bool,
    module_owner_attached: bool,
    register_device_requested: bool,
    blocked_on_live_gpio_lookup: bool,
    blocked_on_platform_registration: bool,
};

pub const RegisterDeviceCallSummary = struct {
    anchor: []const u8,
    register_call: []const u8,
    hw_algo: HardwareAlgorithm,
    requested_line: ProbeLineRequest,
    descriptor_flags: DescriptorRequestFlags,
    start_mode: ProbeStartMode,
    reaches_registration_running: bool,
    reaches_registration_line_state: bool,
    reaches_registration_line_is_output: bool,
    nowayout_applied: bool,
    max_hw_heartbeat_ms: u32,
    register_device_requested: bool,
    blocked_on_live_gpio_lookup: bool,
    blocked_on_platform_registration: bool,
    blocked_on_reboot_glue: bool,
};

pub const RegisterDeviceFailureSummary = struct {
    anchor: []const u8,
    register_call: []const u8,
    failure_stage: []const u8,
    register_device_requested: bool,
    blocked_on_live_gpio_lookup: bool,
    blocked_on_platform_registration: bool,
    blocked_on_reboot_glue: bool,
    keeps_runtime_reviewable: bool,
};

pub const TeardownSummary = struct {
    anchor: []const u8,
    hw_algo: HardwareAlgorithm,
    always_running: bool,
    stop_disposition: StopDisposition,
    line_state: bool,
    line_is_output: bool,
    disable_count: usize,
    request_stop_reviewable: bool,
    register_device_failure_reviewable: bool,
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

    pub fn platformDriverIdentitySummary(self: *const Self) PlatformDriverIdentitySummary {
        _ = self;
        return .{
            .anchor = descriptor().anchor,
            .module_name = descriptor().name,
            .identity = "GPIO Watchdog",
            .provides_simple_driver_starter = true,
            .blocked_on_platform_registration = true,
        };
    }

    pub fn watchdogMetadataSummary(self: *const Self) WatchdogMetadataSummary {
        _ = self;
        return .{
            .anchor = descriptor().anchor,
            .identity = "GPIO Watchdog",
            .timeout_init_requested = true,
            .stop_on_reboot = true,
            .parent_attached = true,
            .module_owner_attached = true,
            .supported_options = .{ .magicclose, .keepaliveping, .settimeout },
            .supported_ops = .{ .start, .stop, .ping },
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

    pub fn descriptorRequestSummary(self: *const Self) DescriptorRequestSummary {
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

    pub fn descriptorPreflightSummary(self: *const Self) DescriptorRequestSummary {
        return self.descriptorRequestSummary();
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

    pub fn platformDrvdataCheckpointSummary(self: *const Self) PlatformDrvdataCheckpointSummary {
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

    pub fn drvdataOwnershipCheckpointSummary(self: *const Self) PlatformDrvdataCheckpointSummary {
        return self.platformDrvdataCheckpointSummary();
    }

    pub fn nowayoutPolicySummary(self: *const Self, nowayout: bool) NowayoutPolicySummary {
        const disposition: StopDisposition = if (nowayout)
            .blocked_by_nowayout
        else if (self.always_running)
            .kept_running
        else
            .stopped;
        return .{
            .anchor = descriptor().anchor,
            .hw_algo = self.hw_algo,
            .always_running = self.always_running,
            .nowayout = nowayout,
            .stop_allowed_by_watchdog_core = !nowayout,
            .disposition_if_stop_requested = disposition,
            .driver_stop_invoked = !nowayout,
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

    pub fn registrationPlanSummary(self: *const Self, nowayout: bool) RegistrationPlanSummary {
        const handoff = self.registrationHandoffSummary(nowayout);
        const descriptor_request = self.descriptorRequestSummary();
        return .{
            .anchor = descriptor().anchor,
            .hw_algo = self.hw_algo,
            .requested_line = handoff.requested_line,
            .descriptor_flags = descriptor_request.descriptor_flags,
            .start_mode = handoff.start_mode,
            .reaches_registration_running = handoff.reaches_registration_running,
            .reaches_registration_line_state = handoff.reaches_registration_line_state,
            .reaches_registration_line_is_output = handoff.reaches_registration_line_is_output,
            .timeout_init_requested = handoff.timeout_init_requested,
            .stop_on_reboot = handoff.stop_on_reboot,
            .parent_attached = handoff.parent_attached,
            .module_owner_attached = handoff.module_owner_attached,
            .register_device_requested = true,
            .blocked_on_live_gpio_lookup = true,
            .blocked_on_platform_registration = true,
        };
    }

    pub fn registerDeviceCallSummary(self: *const Self, nowayout: bool) RegisterDeviceCallSummary {
        const plan = self.registrationPlanSummary(nowayout);
        return .{
            .anchor = plan.anchor,
            .register_call = "devm_watchdog_register_device",
            .hw_algo = self.hw_algo,
            .requested_line = plan.requested_line,
            .descriptor_flags = plan.descriptor_flags,
            .start_mode = plan.start_mode,
            .reaches_registration_running = plan.reaches_registration_running,
            .reaches_registration_line_state = plan.reaches_registration_line_state,
            .reaches_registration_line_is_output = plan.reaches_registration_line_is_output,
            .nowayout_applied = nowayout,
            .max_hw_heartbeat_ms = self.hw_margin_ms,
            .register_device_requested = true,
            .blocked_on_live_gpio_lookup = true,
            .blocked_on_platform_registration = true,
            .blocked_on_reboot_glue = true,
        };
    }

    pub fn registerDeviceFailureSummary(self: *const Self, nowayout: bool) RegisterDeviceFailureSummary {
        const call = self.registerDeviceCallSummary(nowayout);
        return .{
            .anchor = call.anchor,
            .register_call = call.register_call,
            .failure_stage = "devm_watchdog_register_device",
            .register_device_requested = call.register_device_requested,
            .blocked_on_live_gpio_lookup = call.blocked_on_live_gpio_lookup,
            .blocked_on_platform_registration = call.blocked_on_platform_registration,
            .blocked_on_reboot_glue = call.blocked_on_reboot_glue,
            .keeps_runtime_reviewable = true,
        };
    }

    pub fn summarizeTeardown(self: *Self, nowayout: bool) TeardownSummary {
        const stop_summary = self.requestStop(nowayout);
        _ = self.registerDeviceFailureSummary(nowayout);
        return .{
            .anchor = descriptor().anchor,
            .hw_algo = self.hw_algo,
            .always_running = self.always_running,
            .stop_disposition = stop_summary.disposition,
            .line_state = stop_summary.line_state,
            .line_is_output = stop_summary.line_is_output,
            .disable_count = stop_summary.disable_count,
            .request_stop_reviewable = true,
            .register_device_failure_reviewable = true,
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
