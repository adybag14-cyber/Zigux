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

pub const TeardownSummary = struct {
    anchor: []const u8,
    hw_algo: HardwareAlgorithm,
    always_running: bool,
    nowayout: bool,
    running_before_teardown: bool,
    line_state_before_teardown: bool,
    line_is_output_before_teardown: bool,
    disposition: StopDisposition,
    stop_allowed_by_watchdog_core: bool,
    driver_stop_invoked: bool,
    running_after_teardown: bool,
    line_state_after_teardown: bool,
    line_is_output_after_teardown: bool,
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
    requested_line: ProbeLineRequest,
    timeout_property_required: bool,
    descriptor_lookup_precedes_timeout_property: bool,
    timeout_property_bounds_checked: bool,
    timeout_property_precedes_always_running_read: bool,
    timeout_property_precedes_watchdog_drvdata_handoff: bool,
    timeout_property_precedes_registration_handoff: bool,
    invalid_timeout_blocks_later_handoffs: bool,
    blocked_on_live_property_read: bool,
    blocked_on_platform_registration: bool,
};

pub const PlatformDrvdataCheckpointSummary = struct {
    anchor: []const u8,
    hw_algo: HardwareAlgorithm,
    hw_margin_ms: u32,
    requested_line: ProbeLineRequest,
    descriptor_flags: DescriptorRequestFlags,
    platform_drvdata_attachment_required: bool,
    allocation_precedes_platform_drvdata: bool,
    platform_drvdata_precedes_hw_algo_read: bool,
    platform_drvdata_precedes_descriptor_lookup: bool,
    platform_drvdata_precedes_timeout_property: bool,
    platform_drvdata_precedes_watchdog_drvdata_handoff: bool,
    invalid_hw_algo_blocks_later_handoffs: bool,
    blocked_on_live_platform_probe: bool,
    blocked_on_platform_registration: bool,
};

pub const DrvdataCheckpointSummary = struct {
    anchor: []const u8,
    hw_algo: HardwareAlgorithm,
    hw_margin_ms: u32,
    requested_line: ProbeLineRequest,
    descriptor_flags: DescriptorRequestFlags,
    drvdata_attachment_required: bool,
    descriptor_lookup_precedes_drvdata_handoff: bool,
    timeout_property_precedes_drvdata_handoff: bool,
    drvdata_handoff_precedes_registration_handoff: bool,
    drvdata_handoff_precedes_register_device_request: bool,
    invalid_timeout_blocks_drvdata_handoff: bool,
    blocked_on_live_gpio_lookup: bool,
    blocked_on_platform_registration: bool,
};

pub const RebootGlueCheckpointSummary = struct {
    anchor: []const u8,
    hw_algo: HardwareAlgorithm,
    always_running: bool,
    nowayout: bool,
    requested_line: ProbeLineRequest,
    descriptor_flags: DescriptorRequestFlags,
    start_mode: ProbeStartMode,
    timeout_init_requested: bool,
    nowayout_applied: bool,
    stop_on_reboot_requested: bool,
    nowayout_precedes_stop_on_reboot: bool,
    stop_on_reboot_precedes_pre_registration_start: bool,
    stop_on_reboot_precedes_register_device_request: bool,
    pre_registration_start_precedes_register_device_request: bool,
    blocked_on_live_reboot_registration: bool,
    blocked_on_platform_registration: bool,
};

pub const RegisterDeviceCallSummary = struct {
    anchor: []const u8,
    register_call: []const u8,
    hw_algo: HardwareAlgorithm,
    always_running: bool,
    nowayout: bool,
    requested_line: ProbeLineRequest,
    descriptor_flags: DescriptorRequestFlags,
    start_mode: ProbeStartMode,
    reaches_registration_running: bool,
    reaches_registration_line_state: bool,
    reaches_registration_line_is_output: bool,
    watchdog_info_ready: bool,
    watchdog_ops_ready: bool,
    watchdog_device_ready: bool,
    watchdog_drvdata_set: bool,
    module_owner_attached: bool,
    descriptor_request_ready: bool,
    timeout_init_requested: bool,
    nowayout_applied: bool,
    parent_attached: bool,
    stop_on_reboot: bool,
    min_timeout_sec: u32,
    default_timeout_sec: u32,
    max_hw_heartbeat_ms: u32,
    register_device_requested: bool,
    blocked_on_live_gpio_lookup: bool,
    blocked_on_platform_registration: bool,
    blocked_on_reboot_glue: bool,
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
            .disposition = if (self.always_running)
                .kept_running
            else
                .stopped,
            .stop_allowed_by_watchdog_core = true,
            .driver_stop_invoked = true,
            .running = runtime.running,
            .line_state = runtime.line_state,
            .line_is_output = runtime.line_is_output,
            .disable_count = runtime.disable_count,
        };
    }

    pub fn teardownSummary(self: *Self, nowayout: bool) !TeardownSummary {
        if (!self.running) _ = try self.start();

        const running_before_teardown = self.running;
        const line_state_before_teardown = self.line_state;
        const line_is_output_before_teardown = self.line_is_output;
        const stop_summary = self.requestStop(nowayout);

        return .{
            .anchor = descriptor().anchor,
            .hw_algo = self.hw_algo,
            .always_running = self.always_running,
            .nowayout = nowayout,
            .running_before_teardown = running_before_teardown,
            .line_state_before_teardown = line_state_before_teardown,
            .line_is_output_before_teardown = line_is_output_before_teardown,
            .disposition = stop_summary.disposition,
            .stop_allowed_by_watchdog_core = stop_summary.stop_allowed_by_watchdog_core,
            .driver_stop_invoked = stop_summary.driver_stop_invoked,
            .running_after_teardown = stop_summary.running,
            .line_state_after_teardown = stop_summary.line_state,
            .line_is_output_after_teardown = stop_summary.line_is_output,
            .disable_count = stop_summary.disable_count,
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
            .requested_line = self.requestedLine(),
            .timeout_property_required = true,
            .descriptor_lookup_precedes_timeout_property = true,
            .timeout_property_bounds_checked = true,
            .timeout_property_precedes_always_running_read = true,
            .timeout_property_precedes_watchdog_drvdata_handoff = true,
            .timeout_property_precedes_registration_handoff = true,
            .invalid_timeout_blocks_later_handoffs = true,
            .blocked_on_live_property_read = true,
            .blocked_on_platform_registration = true,
        };
    }

    pub fn platformDrvdataCheckpointSummary(self: *const Self) PlatformDrvdataCheckpointSummary {
        const descriptor_preflight = self.descriptorPreflightSummary();

        return .{
            .anchor = descriptor().anchor,
            .hw_algo = self.hw_algo,
            .hw_margin_ms = self.hw_margin_ms,
            .requested_line = descriptor_preflight.requested_line,
            .descriptor_flags = descriptor_preflight.descriptor_flags,
            .platform_drvdata_attachment_required = true,
            .allocation_precedes_platform_drvdata = true,
            .platform_drvdata_precedes_hw_algo_read = true,
            .platform_drvdata_precedes_descriptor_lookup = true,
            .platform_drvdata_precedes_timeout_property = true,
            .platform_drvdata_precedes_watchdog_drvdata_handoff = true,
            .invalid_hw_algo_blocks_later_handoffs = true,
            .blocked_on_live_platform_probe = true,
            .blocked_on_platform_registration = true,
        };
    }

    pub fn drvdataCheckpointSummary(self: *const Self) DrvdataCheckpointSummary {
        const descriptor_preflight = self.descriptorPreflightSummary();
        const timeout_checkpoint = self.timeoutPropertyCheckpointSummary();
        const platform_drvdata_checkpoint = self.platformDrvdataCheckpointSummary();

        return .{
            .anchor = descriptor().anchor,
            .hw_algo = self.hw_algo,
            .hw_margin_ms = self.hw_margin_ms,
            .requested_line = descriptor_preflight.requested_line,
            .descriptor_flags = descriptor_preflight.descriptor_flags,
            .drvdata_attachment_required = true,
            .descriptor_lookup_precedes_drvdata_handoff = true,
            .timeout_property_precedes_drvdata_handoff = timeout_checkpoint.timeout_property_precedes_watchdog_drvdata_handoff,
            .drvdata_handoff_precedes_registration_handoff = true,
            .drvdata_handoff_precedes_register_device_request = true,
            .invalid_timeout_blocks_drvdata_handoff = timeout_checkpoint.invalid_timeout_blocks_later_handoffs,
            .blocked_on_live_gpio_lookup = descriptor_preflight.blocked_on_live_gpio_lookup,
            .blocked_on_platform_registration = platform_drvdata_checkpoint.blocked_on_platform_registration,
        };
    }

    pub fn rebootGlueCheckpointSummary(self: *const Self, nowayout: bool) RebootGlueCheckpointSummary {
        const probe = self.probeSummary(nowayout);
        const descriptor_preflight = self.descriptorPreflightSummary();

        return .{
            .anchor = descriptor().anchor,
            .hw_algo = self.hw_algo,
            .always_running = self.always_running,
            .nowayout = nowayout,
            .requested_line = descriptor_preflight.requested_line,
            .descriptor_flags = descriptor_preflight.descriptor_flags,
            .start_mode = probe.start_mode,
            .timeout_init_requested = probe.timeout_init_requested,
            .nowayout_applied = nowayout,
            .stop_on_reboot_requested = probe.stop_on_reboot,
            .nowayout_precedes_stop_on_reboot = true,
            .stop_on_reboot_precedes_pre_registration_start = probe.starts_during_probe,
            .stop_on_reboot_precedes_register_device_request = true,
            .pre_registration_start_precedes_register_device_request = probe.starts_during_probe,
            .blocked_on_live_reboot_registration = true,
            .blocked_on_platform_registration = descriptor_preflight.blocked_on_platform_registration,
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

    pub fn registerDeviceCallSummary(self: *const Self, nowayout: bool) RegisterDeviceCallSummary {
        const handoff = self.registrationHandoffSummary(nowayout);
        const descriptor_preflight = self.descriptorPreflightSummary();
        const drvdata_checkpoint = self.drvdataCheckpointSummary();
        const reboot_glue_checkpoint = self.rebootGlueCheckpointSummary(nowayout);

        return .{
            .anchor = descriptor().anchor,
            .register_call = "devm_watchdog_register_device",
            .hw_algo = self.hw_algo,
            .always_running = self.always_running,
            .nowayout = nowayout,
            .requested_line = reboot_glue_checkpoint.requested_line,
            .descriptor_flags = reboot_glue_checkpoint.descriptor_flags,
            .start_mode = reboot_glue_checkpoint.start_mode,
            .reaches_registration_running = handoff.reaches_registration_running,
            .reaches_registration_line_state = handoff.reaches_registration_line_state,
            .reaches_registration_line_is_output = handoff.reaches_registration_line_is_output,
            .watchdog_info_ready = true,
            .watchdog_ops_ready = true,
            .watchdog_device_ready = true,
            .watchdog_drvdata_set = drvdata_checkpoint.drvdata_attachment_required,
            .module_owner_attached = handoff.module_owner_attached,
            .descriptor_request_ready = descriptor_preflight.descriptor_lookup_required,
            .timeout_init_requested = reboot_glue_checkpoint.timeout_init_requested,
            .nowayout_applied = reboot_glue_checkpoint.nowayout_applied,
            .parent_attached = handoff.parent_attached,
            .stop_on_reboot = reboot_glue_checkpoint.stop_on_reboot_requested,
            .min_timeout_sec = soft_timeout_min,
            .default_timeout_sec = soft_timeout_default,
            .max_hw_heartbeat_ms = self.hw_margin_ms,
            .register_device_requested = true,
            .blocked_on_live_gpio_lookup = drvdata_checkpoint.blocked_on_live_gpio_lookup,
            .blocked_on_platform_registration = reboot_glue_checkpoint.blocked_on_platform_registration,
            .blocked_on_reboot_glue = reboot_glue_checkpoint.blocked_on_live_reboot_registration,
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

test "reboot glue checkpoint keeps watchdog_stop_on_reboot ordering explicit" {
    const prestarted = try GpioWatchdogLab.init(.toggle, 20, true);
    const prestarted_checkpoint = prestarted.rebootGlueCheckpointSummary(true);

    try std.testing.expectEqualStrings("drivers/watchdog/gpio_wdt.c", prestarted_checkpoint.anchor);
    try std.testing.expectEqual(HardwareAlgorithm.toggle, prestarted_checkpoint.hw_algo);
    try std.testing.expect(prestarted_checkpoint.always_running);
    try std.testing.expect(prestarted_checkpoint.nowayout);
    try std.testing.expectEqual(ProbeLineRequest.input, prestarted_checkpoint.requested_line);
    try std.testing.expectEqual(DescriptorRequestFlags.in, prestarted_checkpoint.descriptor_flags);
    try std.testing.expectEqual(ProbeStartMode.start_before_register, prestarted_checkpoint.start_mode);
    try std.testing.expect(prestarted_checkpoint.timeout_init_requested);
    try std.testing.expect(prestarted_checkpoint.nowayout_applied);
    try std.testing.expect(prestarted_checkpoint.stop_on_reboot_requested);
    try std.testing.expect(prestarted_checkpoint.nowayout_precedes_stop_on_reboot);
    try std.testing.expect(prestarted_checkpoint.stop_on_reboot_precedes_pre_registration_start);
    try std.testing.expect(prestarted_checkpoint.stop_on_reboot_precedes_register_device_request);
    try std.testing.expect(prestarted_checkpoint.pre_registration_start_precedes_register_device_request);
    try std.testing.expect(prestarted_checkpoint.blocked_on_live_reboot_registration);
    try std.testing.expect(prestarted_checkpoint.blocked_on_platform_registration);

    const dormant = try GpioWatchdogLab.init(.level, 500, false);
    const dormant_checkpoint = dormant.rebootGlueCheckpointSummary(false);
    try std.testing.expectEqual(HardwareAlgorithm.level, dormant_checkpoint.hw_algo);
    try std.testing.expect(!dormant_checkpoint.always_running);
    try std.testing.expect(!dormant_checkpoint.nowayout);
    try std.testing.expectEqual(ProbeLineRequest.output_low, dormant_checkpoint.requested_line);
    try std.testing.expectEqual(DescriptorRequestFlags.out_low, dormant_checkpoint.descriptor_flags);
    try std.testing.expectEqual(ProbeStartMode.register_only, dormant_checkpoint.start_mode);
    try std.testing.expect(dormant_checkpoint.timeout_init_requested);
    try std.testing.expect(!dormant_checkpoint.nowayout_applied);
    try std.testing.expect(dormant_checkpoint.stop_on_reboot_requested);
    try std.testing.expect(dormant_checkpoint.nowayout_precedes_stop_on_reboot);
    try std.testing.expect(!dormant_checkpoint.stop_on_reboot_precedes_pre_registration_start);
    try std.testing.expect(dormant_checkpoint.stop_on_reboot_precedes_register_device_request);
    try std.testing.expect(!dormant_checkpoint.pre_registration_start_precedes_register_device_request);
    try std.testing.expect(dormant_checkpoint.blocked_on_live_reboot_registration);
    try std.testing.expect(dormant_checkpoint.blocked_on_platform_registration);
}

test "register device call summary keeps toggle handoff and descriptor checkpoints aligned" {
    const lab = try GpioWatchdogLab.init(.toggle, 250, false);
    const summary = lab.registerDeviceCallSummary(false);

    try std.testing.expectEqualStrings("drivers/watchdog/gpio_wdt.c", summary.anchor);
    try std.testing.expectEqualStrings("devm_watchdog_register_device", summary.register_call);
    try std.testing.expectEqual(HardwareAlgorithm.toggle, summary.hw_algo);
    try std.testing.expectEqual(ProbeLineRequest.input, summary.requested_line);
    try std.testing.expectEqual(DescriptorRequestFlags.in, summary.descriptor_flags);
    try std.testing.expectEqual(ProbeStartMode.register_only, summary.start_mode);
    try std.testing.expect(!summary.reaches_registration_running);
    try std.testing.expect(!summary.reaches_registration_line_state);
    try std.testing.expect(!summary.reaches_registration_line_is_output);
    try std.testing.expect(summary.watchdog_info_ready);
    try std.testing.expect(summary.watchdog_ops_ready);
    try std.testing.expect(summary.watchdog_device_ready);
    try std.testing.expect(summary.watchdog_drvdata_set);
    try std.testing.expect(summary.module_owner_attached);
    try std.testing.expect(summary.descriptor_request_ready);
    try std.testing.expect(summary.timeout_init_requested);
    try std.testing.expect(!summary.nowayout_applied);
    try std.testing.expect(summary.parent_attached);
    try std.testing.expect(summary.stop_on_reboot);
    try std.testing.expectEqual(soft_timeout_min, summary.min_timeout_sec);
    try std.testing.expectEqual(soft_timeout_default, summary.default_timeout_sec);
    try std.testing.expectEqual(@as(u32, 250), summary.max_hw_heartbeat_ms);
    try std.testing.expect(summary.register_device_requested);
    try std.testing.expect(summary.blocked_on_live_gpio_lookup);
    try std.testing.expect(summary.blocked_on_platform_registration);
    try std.testing.expect(summary.blocked_on_reboot_glue);
}

test "always-running level teardown keeps heartbeat active after stop-backed teardown" {
    var lab = try GpioWatchdogLab.init(.level, 500, true);
    const summary = try lab.teardownSummary(false);

    try std.testing.expectEqualStrings("drivers/watchdog/gpio_wdt.c", summary.anchor);
    try std.testing.expectEqual(HardwareAlgorithm.level, summary.hw_algo);
    try std.testing.expect(summary.always_running);
    try std.testing.expect(!summary.nowayout);
    try std.testing.expect(summary.running_before_teardown);
    try std.testing.expect(summary.line_is_output_before_teardown);
    try std.testing.expectEqual(StopDisposition.kept_running, summary.disposition);
    try std.testing.expect(summary.stop_allowed_by_watchdog_core);
    try std.testing.expect(summary.driver_stop_invoked);
    try std.testing.expect(summary.running_after_teardown);
    try std.testing.expect(!summary.line_state_after_teardown);
    try std.testing.expect(summary.line_is_output_after_teardown);
    try std.testing.expectEqual(@as(usize, 0), summary.disable_count);
}

test "toggle stop disables line ownership and clears running state when stop is allowed" {
    var lab = try GpioWatchdogLab.init(.toggle, 250, false);
    _ = try lab.start();

    const stop = lab.requestStop(false);
    try std.testing.expectEqualStrings("drivers/watchdog/gpio_wdt.c", stop.anchor);
    try std.testing.expectEqual(HardwareAlgorithm.toggle, stop.hw_algo);
    try std.testing.expect(!stop.always_running);
    try std.testing.expect(!stop.nowayout);
    try std.testing.expectEqual(StopDisposition.stopped, stop.disposition);
    try std.testing.expect(stop.stop_allowed_by_watchdog_core);
    try std.testing.expect(stop.driver_stop_invoked);
    try std.testing.expect(!stop.running);
    try std.testing.expect(stop.line_state);
    try std.testing.expect(!stop.line_is_output);
    try std.testing.expectEqual(@as(usize, 1), stop.disable_count);
}
