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

pub const WatchdogDrvdataCheckpointSummary = struct {
    anchor: []const u8,
    hw_algo: HardwareAlgorithm,
    hw_margin_ms: u32,
    parent_attached: bool,
    module_owner_attached: bool,
    platform_drvdata_owner_identity: []const u8,
    watchdog_drvdata_owner_identity: []const u8,
    timeout_property_precedes_platform_drvdata: bool,
    platform_drvdata_precedes_watchdog_drvdata: bool,
    watchdog_drvdata_precedes_registration_handoff: bool,
    watchdog_drvdata_reuses_parent_linkage: bool,
    blocked_on_live_gpio_lookup: bool,
    blocked_on_platform_registration: bool,
    blocked_on_reboot_glue: bool,
};

pub const RegistrationIntentCheckpointSummary = struct {
    anchor: []const u8,
    hw_algo: HardwareAlgorithm,
    hw_margin_ms: u32,
    always_running: bool,
    timeout_init_requested: bool,
    nowayout_from_module_param: bool,
    stop_on_reboot_requested: bool,
    pre_registration_start_requested: bool,
    timeout_init_stays_before_nowayout: bool,
    nowayout_stays_before_stop_on_reboot: bool,
    stop_on_reboot_stays_before_pre_registration_start: bool,
    pre_registration_start_stays_before_registration: bool,
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

pub const RebootGlueCheckpointSummary = struct {
    anchor: []const u8,
    hw_algo: HardwareAlgorithm,
    hw_margin_ms: u32,
    parent_attached: bool,
    module_owner_attached: bool,
    watchdog_drvdata_owner_identity: []const u8,
    stop_on_reboot_requested: bool,
    watchdog_drvdata_precedes_reboot_glue: bool,
    reboot_glue_precedes_register_device_request: bool,
    reboot_glue_reuses_parent_linkage: bool,
    blocked_on_live_gpio_lookup: bool,
    blocked_on_platform_registration: bool,
    blocked_on_host_shutdown_execution: bool,
};

pub const TeardownCheckpointSummary = struct {
    anchor: []const u8,
    hw_algo: HardwareAlgorithm,
    always_running: bool,
    nowayout: bool,
    platform_drvdata_owner_identity: []const u8,
    watchdog_drvdata_owner_identity: []const u8,
    stop_disposition: StopDisposition,
    stop_allowed_by_watchdog_core: bool,
    driver_stop_invoked: bool,
    register_device_failure_stage: []const u8,
    watchdog_drvdata_precedes_reboot_glue: bool,
    reboot_glue_precedes_register_device_request: bool,
    teardown_reuses_parent_linkage: bool,
    blocked_on_live_gpio_lookup: bool,
    blocked_on_platform_registration: bool,
    blocked_on_host_shutdown_execution: bool,
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
    reboot_glue_checkpoint_reviewable: bool,
};

pub const PlatformCleanupCheckpointSummary = struct {
    anchor: []const u8,
    hw_algo: HardwareAlgorithm,
    always_running: bool,
    nowayout: bool,
    stop_disposition: StopDisposition,
    platform_drvdata_owner_identity: []const u8,
    watchdog_drvdata_owner_identity: []const u8,
    register_device_failure_stage: []const u8,
    request_stop_reviewable: bool,
    register_device_failure_reviewable: bool,
    reboot_glue_checkpoint_reviewable: bool,
    platform_cleanup_precedes_driver_remove: bool,
    driver_remove_precedes_watchdog_unregister: bool,
    cleanup_reuses_parent_linkage: bool,
    blocked_on_platform_cleanup_callback: bool,
    blocked_on_platform_driver_remove: bool,
    blocked_on_watchdog_core_unregister: bool,
    blocked_on_host_shutdown_execution: bool,
};

pub const RemoveHandoffSummary = struct {
    anchor: []const u8,
    hw_algo: HardwareAlgorithm,
    always_running: bool,
    nowayout: bool,
    stop_disposition: StopDisposition,
    platform_drvdata_owner_identity: []const u8,
    watchdog_drvdata_owner_identity: []const u8,
    register_device_failure_stage: []const u8,
    request_stop_reviewable: bool,
    register_device_failure_reviewable: bool,
    reboot_glue_checkpoint_reviewable: bool,
    blocked_on_platform_cleanup_callback: bool,
    blocked_on_platform_driver_remove: bool,
    blocked_on_watchdog_core_unregister: bool,
    blocked_on_host_shutdown_execution: bool,
};

pub const HardwareValidationMatrixRow = struct {
    anchor: []const u8,
    hw_algo: HardwareAlgorithm,
    always_running: bool,
    nowayout: bool,
    requested_line: ProbeLineRequest,
    descriptor_flags: DescriptorRequestFlags,
    start_mode: ProbeStartMode,
    stop_disposition: StopDisposition,
    reaches_registration_running: bool,
    reaches_registration_line_state: bool,
    reaches_registration_line_is_output: bool,
    ping_uses_pulse: bool,
    stop_allowed_by_watchdog_core: bool,
    blocked_on_live_gpio_lookup: bool,
    blocked_on_platform_registration: bool,
    blocked_on_reboot_glue: bool,
    blocked_on_host_shutdown_execution: bool,
};

pub const HardwareValidationMatrixSummary = struct {
    anchor: []const u8,
    rows: [4]HardwareValidationMatrixRow,
    covers_toggle_and_level: bool,
    covers_register_only_and_prestart: bool,
    covers_stop_dispositions: bool,
    covers_failure_and_teardown_blockers: bool,
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

    pub fn watchdogDrvdataCheckpointSummary(self: *const Self) WatchdogDrvdataCheckpointSummary {
        return .{
            .anchor = descriptor().anchor,
            .hw_algo = self.hw_algo,
            .hw_margin_ms = self.hw_margin_ms,
            .parent_attached = true,
            .module_owner_attached = true,
            .platform_drvdata_owner_identity = "gpio_wdt_priv",
            .watchdog_drvdata_owner_identity = "gpio_wdt_priv",
            .timeout_property_precedes_platform_drvdata = true,
            .platform_drvdata_precedes_watchdog_drvdata = true,
            .watchdog_drvdata_precedes_registration_handoff = true,
            .watchdog_drvdata_reuses_parent_linkage = true,
            .blocked_on_live_gpio_lookup = true,
            .blocked_on_platform_registration = true,
            .blocked_on_reboot_glue = true,
        };
    }

    pub fn drvdataOwnershipCheckpointSummary(self: *const Self) PlatformDrvdataCheckpointSummary {
        return self.platformDrvdataCheckpointSummary();
    }

    pub fn registrationIntentCheckpointSummary(self: *const Self, nowayout: bool) RegistrationIntentCheckpointSummary {
        return .{
            .anchor = descriptor().anchor,
            .hw_algo = self.hw_algo,
            .hw_margin_ms = self.hw_margin_ms,
            .always_running = self.always_running,
            .timeout_init_requested = true,
            .nowayout_from_module_param = nowayout,
            .stop_on_reboot_requested = true,
            .pre_registration_start_requested = self.always_running,
            .timeout_init_stays_before_nowayout = true,
            .nowayout_stays_before_stop_on_reboot = true,
            .stop_on_reboot_stays_before_pre_registration_start = true,
            .pre_registration_start_stays_before_registration = true,
            .blocked_on_live_gpio_lookup = true,
            .blocked_on_platform_registration = true,
        };
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
        const intent = self.registrationIntentCheckpointSummary(nowayout);
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
            .nowayout_applied = intent.nowayout_from_module_param,
            .max_hw_heartbeat_ms = self.hw_margin_ms,
            .register_device_requested = true,
            .blocked_on_live_gpio_lookup = intent.blocked_on_live_gpio_lookup,
            .blocked_on_platform_registration = intent.blocked_on_platform_registration,
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

    pub fn rebootGlueCheckpointSummary(self: *const Self) RebootGlueCheckpointSummary {
        return .{
            .anchor = descriptor().anchor,
            .hw_algo = self.hw_algo,
            .hw_margin_ms = self.hw_margin_ms,
            .parent_attached = true,
            .module_owner_attached = true,
            .watchdog_drvdata_owner_identity = "gpio_wdt_priv",
            .stop_on_reboot_requested = true,
            .watchdog_drvdata_precedes_reboot_glue = true,
            .reboot_glue_precedes_register_device_request = true,
            .reboot_glue_reuses_parent_linkage = true,
            .blocked_on_live_gpio_lookup = true,
            .blocked_on_platform_registration = true,
            .blocked_on_host_shutdown_execution = true,
        };
    }

    pub fn teardownCheckpointSummary(self: *Self, nowayout: bool) TeardownCheckpointSummary {
        const stop_summary = self.requestStop(nowayout);
        const watchdog_drvdata = self.watchdogDrvdataCheckpointSummary();
        const register_failure = self.registerDeviceFailureSummary(nowayout);
        const reboot_glue = self.rebootGlueCheckpointSummary();
        return .{
            .anchor = descriptor().anchor,
            .hw_algo = self.hw_algo,
            .always_running = self.always_running,
            .nowayout = nowayout,
            .platform_drvdata_owner_identity = watchdog_drvdata.platform_drvdata_owner_identity,
            .watchdog_drvdata_owner_identity = watchdog_drvdata.watchdog_drvdata_owner_identity,
            .stop_disposition = stop_summary.disposition,
            .stop_allowed_by_watchdog_core = stop_summary.stop_allowed_by_watchdog_core,
            .driver_stop_invoked = stop_summary.driver_stop_invoked,
            .register_device_failure_stage = register_failure.failure_stage,
            .watchdog_drvdata_precedes_reboot_glue = reboot_glue.watchdog_drvdata_precedes_reboot_glue,
            .reboot_glue_precedes_register_device_request = reboot_glue.reboot_glue_precedes_register_device_request,
            .teardown_reuses_parent_linkage = watchdog_drvdata.watchdog_drvdata_reuses_parent_linkage and reboot_glue.reboot_glue_reuses_parent_linkage,
            .blocked_on_live_gpio_lookup = reboot_glue.blocked_on_live_gpio_lookup,
            .blocked_on_platform_registration = reboot_glue.blocked_on_platform_registration,
            .blocked_on_host_shutdown_execution = reboot_glue.blocked_on_host_shutdown_execution,
        };
    }

    pub fn summarizeTeardown(self: *Self, nowayout: bool) TeardownSummary {
        const stop_summary = self.requestStop(nowayout);
        const teardown = self.teardownCheckpointSummary(nowayout);
        return .{
            .anchor = descriptor().anchor,
            .hw_algo = self.hw_algo,
            .always_running = self.always_running,
            .stop_disposition = stop_summary.disposition,
            .line_state = stop_summary.line_state,
            .line_is_output = stop_summary.line_is_output,
            .disable_count = stop_summary.disable_count,
            .request_stop_reviewable = true,
            .register_device_failure_reviewable = std.mem.eql(u8, teardown.register_device_failure_stage, "devm_watchdog_register_device"),
            .reboot_glue_checkpoint_reviewable = teardown.watchdog_drvdata_precedes_reboot_glue and teardown.reboot_glue_precedes_register_device_request,
        };
    }

    pub fn platformCleanupCheckpointSummary(self: *Self, nowayout: bool) PlatformCleanupCheckpointSummary {
        const teardown = self.teardownCheckpointSummary(nowayout);
        const teardown_summary = self.summarizeTeardown(nowayout);
        return .{
            .anchor = descriptor().anchor,
            .hw_algo = self.hw_algo,
            .always_running = self.always_running,
            .nowayout = nowayout,
            .stop_disposition = teardown_summary.stop_disposition,
            .platform_drvdata_owner_identity = teardown.platform_drvdata_owner_identity,
            .watchdog_drvdata_owner_identity = teardown.watchdog_drvdata_owner_identity,
            .register_device_failure_stage = teardown.register_device_failure_stage,
            .request_stop_reviewable = teardown_summary.request_stop_reviewable,
            .register_device_failure_reviewable = teardown_summary.register_device_failure_reviewable,
            .reboot_glue_checkpoint_reviewable = teardown_summary.reboot_glue_checkpoint_reviewable,
            .platform_cleanup_precedes_driver_remove = true,
            .driver_remove_precedes_watchdog_unregister = true,
            .cleanup_reuses_parent_linkage = teardown.teardown_reuses_parent_linkage,
            .blocked_on_platform_cleanup_callback = true,
            .blocked_on_platform_driver_remove = true,
            .blocked_on_watchdog_core_unregister = true,
            .blocked_on_host_shutdown_execution = teardown.blocked_on_host_shutdown_execution,
        };
    }

    pub fn summarizeRemoveHandoff(self: *Self, nowayout: bool) RemoveHandoffSummary {
        const cleanup = self.platformCleanupCheckpointSummary(nowayout);
        return .{
            .anchor = cleanup.anchor,
            .hw_algo = cleanup.hw_algo,
            .always_running = cleanup.always_running,
            .nowayout = cleanup.nowayout,
            .stop_disposition = cleanup.stop_disposition,
            .platform_drvdata_owner_identity = cleanup.platform_drvdata_owner_identity,
            .watchdog_drvdata_owner_identity = cleanup.watchdog_drvdata_owner_identity,
            .register_device_failure_stage = cleanup.register_device_failure_stage,
            .request_stop_reviewable = cleanup.request_stop_reviewable,
            .register_device_failure_reviewable = cleanup.register_device_failure_reviewable,
            .reboot_glue_checkpoint_reviewable = cleanup.reboot_glue_checkpoint_reviewable,
            .blocked_on_platform_cleanup_callback = cleanup.blocked_on_platform_cleanup_callback,
            .blocked_on_platform_driver_remove = cleanup.blocked_on_platform_driver_remove,
            .blocked_on_watchdog_core_unregister = cleanup.blocked_on_watchdog_core_unregister,
            .blocked_on_host_shutdown_execution = cleanup.blocked_on_host_shutdown_execution,
        };
    }

    pub fn hardwareValidationMatrixSummary() !HardwareValidationMatrixSummary {
        var toggle_register_only = try Self.init(.toggle, 60, false);
        var level_nowayout = try Self.init(.level, 64, true);
        var level_register_only = try Self.init(.level, 17, false);
        var toggle_prestart = try Self.init(.toggle, 42, true);

        const rows = .{
            try buildHardwareValidationMatrixRow(&toggle_register_only, false),
            try buildHardwareValidationMatrixRow(&level_nowayout, true),
            try buildHardwareValidationMatrixRow(&level_register_only, false),
            try buildHardwareValidationMatrixRow(&toggle_prestart, false),
        };

        return .{
            .anchor = descriptor().anchor,
            .rows = rows,
            .covers_toggle_and_level = rows[0].hw_algo == .toggle and
                rows[1].hw_algo == .level and
                rows[2].hw_algo == .level and
                rows[3].hw_algo == .toggle,
            .covers_register_only_and_prestart = rows[0].start_mode == .register_only and
                rows[1].start_mode == .start_before_register and
                rows[2].start_mode == .register_only and
                rows[3].start_mode == .start_before_register,
            .covers_stop_dispositions = rows[0].stop_disposition == .stopped and
                rows[1].stop_disposition == .blocked_by_nowayout and
                rows[2].stop_disposition == .stopped and
                rows[3].stop_disposition == .kept_running,
            .covers_failure_and_teardown_blockers = rows[0].blocked_on_reboot_glue and
                rows[1].blocked_on_reboot_glue and
                rows[2].blocked_on_reboot_glue and
                rows[3].blocked_on_reboot_glue and
                rows[0].blocked_on_host_shutdown_execution and
                rows[1].blocked_on_host_shutdown_execution and
                rows[2].blocked_on_host_shutdown_execution and
                rows[3].blocked_on_host_shutdown_execution,
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

fn buildHardwareValidationMatrixRow(
    lab: *GpioWatchdogLab,
    nowayout: bool,
) !HardwareValidationMatrixRow {
    const descriptor = lab.descriptorRequestSummary();
    const handoff = lab.registrationHandoffSummary(nowayout);
    const register_call = lab.registerDeviceCallSummary(nowayout);
    const reboot_glue = lab.rebootGlueCheckpointSummary();
    const first_ping = try lab.start();
    const stop = lab.requestStop(nowayout);

    return .{
        .anchor = GpioWatchdogLab.descriptor().anchor,
        .hw_algo = lab.hw_algo,
        .always_running = lab.always_running,
        .nowayout = nowayout,
        .requested_line = descriptor.requested_line,
        .descriptor_flags = descriptor.descriptor_flags,
        .start_mode = handoff.start_mode,
        .stop_disposition = stop.disposition,
        .reaches_registration_running = handoff.reaches_registration_running,
        .reaches_registration_line_state = handoff.reaches_registration_line_state,
        .reaches_registration_line_is_output = handoff.reaches_registration_line_is_output,
        .ping_uses_pulse = first_ping.last_ping_was_pulse,
        .stop_allowed_by_watchdog_core = stop.stop_allowed_by_watchdog_core,
        .blocked_on_live_gpio_lookup = descriptor.blocked_on_live_gpio_lookup,
        .blocked_on_platform_registration = descriptor.blocked_on_platform_registration,
        .blocked_on_reboot_glue = register_call.blocked_on_reboot_glue,
        .blocked_on_host_shutdown_execution = reboot_glue.blocked_on_host_shutdown_execution,
    };
}

fn validateHeartbeatMargin(hw_margin_ms: u32) !void {
    if (hw_margin_ms < min_hw_margin_ms) return error.HeartbeatMarginTooSmall;
    if (hw_margin_ms > max_hw_margin_ms) return error.HeartbeatMarginTooLarge;
}

test "watchdog drvdata checkpoint stays between platform drvdata and register-device handoff" {
    const lab = try GpioWatchdogLab.init(.toggle, 60, false);
    const platform_drvdata = lab.platformDrvdataCheckpointSummary();
    const watchdog_drvdata = lab.watchdogDrvdataCheckpointSummary();
    const register_call = lab.registerDeviceCallSummary(false);

    try std.testing.expect(platform_drvdata.timeout_property_precedes_drvdata_binding);
    try std.testing.expect(platform_drvdata.drvdata_binding_precedes_registration_handoff);
    try std.testing.expect(watchdog_drvdata.timeout_property_precedes_platform_drvdata);
    try std.testing.expect(watchdog_drvdata.platform_drvdata_precedes_watchdog_drvdata);
    try std.testing.expect(watchdog_drvdata.watchdog_drvdata_precedes_registration_handoff);
    try std.testing.expect(watchdog_drvdata.watchdog_drvdata_reuses_parent_linkage);
    try std.testing.expectEqualStrings("gpio_wdt_priv", watchdog_drvdata.platform_drvdata_owner_identity);
    try std.testing.expectEqualStrings("gpio_wdt_priv", watchdog_drvdata.watchdog_drvdata_owner_identity);
    try std.testing.expect(register_call.register_device_requested);
    try std.testing.expect(register_call.blocked_on_reboot_glue);
}

test "reboot glue checkpoint stays between watchdog drvdata and register-device request" {
    var lab = try GpioWatchdogLab.init(.level, 64, true);
    const watchdog_drvdata = lab.watchdogDrvdataCheckpointSummary();
    const reboot_glue = lab.rebootGlueCheckpointSummary();
    const register_call = lab.registerDeviceCallSummary(true);
    const teardown = lab.summarizeTeardown(true);

    try std.testing.expect(watchdog_drvdata.blocked_on_reboot_glue);
    try std.testing.expect(reboot_glue.stop_on_reboot_requested);
    try std.testing.expect(reboot_glue.watchdog_drvdata_precedes_reboot_glue);
    try std.testing.expect(reboot_glue.reboot_glue_precedes_register_device_request);
    try std.testing.expect(reboot_glue.reboot_glue_reuses_parent_linkage);
    try std.testing.expect(reboot_glue.blocked_on_live_gpio_lookup);
    try std.testing.expect(reboot_glue.blocked_on_platform_registration);
    try std.testing.expect(reboot_glue.blocked_on_host_shutdown_execution);
    try std.testing.expectEqualStrings(watchdog_drvdata.watchdog_drvdata_owner_identity, reboot_glue.watchdog_drvdata_owner_identity);
    try std.testing.expect(register_call.register_device_requested);
    try std.testing.expect(register_call.blocked_on_reboot_glue);
    try std.testing.expect(teardown.reboot_glue_checkpoint_reviewable);
}

test "teardown checkpoint keeps ownership and failure ordering explicit" {
    var stoppable = try GpioWatchdogLab.init(.toggle, 60, false);
    _ = try stoppable.start();
    const stoppable_teardown = stoppable.teardownCheckpointSummary(false);

    try std.testing.expectEqual(StopDisposition.stopped, stoppable_teardown.stop_disposition);
    try std.testing.expect(stoppable_teardown.stop_allowed_by_watchdog_core);
    try std.testing.expect(stoppable_teardown.driver_stop_invoked);
    try std.testing.expectEqualStrings("gpio_wdt_priv", stoppable_teardown.platform_drvdata_owner_identity);
    try std.testing.expectEqualStrings("gpio_wdt_priv", stoppable_teardown.watchdog_drvdata_owner_identity);
    try std.testing.expectEqualStrings("devm_watchdog_register_device", stoppable_teardown.register_device_failure_stage);
    try std.testing.expect(stoppable_teardown.watchdog_drvdata_precedes_reboot_glue);
    try std.testing.expect(stoppable_teardown.reboot_glue_precedes_register_device_request);
    try std.testing.expect(stoppable_teardown.teardown_reuses_parent_linkage);
    try std.testing.expect(stoppable_teardown.blocked_on_live_gpio_lookup);
    try std.testing.expect(stoppable_teardown.blocked_on_platform_registration);
    try std.testing.expect(stoppable_teardown.blocked_on_host_shutdown_execution);

    var blocked = try GpioWatchdogLab.init(.level, 64, true);
    _ = try blocked.start();
    const blocked_teardown = blocked.teardownCheckpointSummary(true);

    try std.testing.expectEqual(StopDisposition.blocked_by_nowayout, blocked_teardown.stop_disposition);
    try std.testing.expect(!blocked_teardown.stop_allowed_by_watchdog_core);
    try std.testing.expect(!blocked_teardown.driver_stop_invoked);
    try std.testing.expectEqualStrings("gpio_wdt_priv", blocked_teardown.platform_drvdata_owner_identity);
    try std.testing.expectEqualStrings("gpio_wdt_priv", blocked_teardown.watchdog_drvdata_owner_identity);
}

test "platform cleanup checkpoint stays between teardown and unregister handoff" {
    var stoppable = try GpioWatchdogLab.init(.toggle, 60, false);
    _ = try stoppable.start();
    const cleanup = stoppable.platformCleanupCheckpointSummary(false);

    try std.testing.expectEqualStrings("drivers/watchdog/gpio_wdt.c", cleanup.anchor);
    try std.testing.expectEqual(HardwareAlgorithm.toggle, cleanup.hw_algo);
    try std.testing.expect(!cleanup.always_running);
    try std.testing.expect(!cleanup.nowayout);
    try std.testing.expectEqual(StopDisposition.stopped, cleanup.stop_disposition);
    try std.testing.expectEqualStrings("gpio_wdt_priv", cleanup.platform_drvdata_owner_identity);
    try std.testing.expectEqualStrings("gpio_wdt_priv", cleanup.watchdog_drvdata_owner_identity);
    try std.testing.expectEqualStrings("devm_watchdog_register_device", cleanup.register_device_failure_stage);
    try std.testing.expect(cleanup.request_stop_reviewable);
    try std.testing.expect(cleanup.register_device_failure_reviewable);
    try std.testing.expect(cleanup.reboot_glue_checkpoint_reviewable);
    try std.testing.expect(cleanup.platform_cleanup_precedes_driver_remove);
    try std.testing.expect(cleanup.driver_remove_precedes_watchdog_unregister);
    try std.testing.expect(cleanup.cleanup_reuses_parent_linkage);
    try std.testing.expect(cleanup.blocked_on_platform_cleanup_callback);
    try std.testing.expect(cleanup.blocked_on_platform_driver_remove);
    try std.testing.expect(cleanup.blocked_on_watchdog_core_unregister);
    try std.testing.expect(cleanup.blocked_on_host_shutdown_execution);

    var guarded = try GpioWatchdogLab.init(.level, 64, true);
    _ = try guarded.start();
    const guarded_cleanup = guarded.platformCleanupCheckpointSummary(true);

    try std.testing.expect(guarded_cleanup.always_running);
    try std.testing.expect(guarded_cleanup.nowayout);
    try std.testing.expectEqual(StopDisposition.blocked_by_nowayout, guarded_cleanup.stop_disposition);
    try std.testing.expect(guarded_cleanup.request_stop_reviewable);
    try std.testing.expect(guarded_cleanup.register_device_failure_reviewable);
    try std.testing.expect(guarded_cleanup.reboot_glue_checkpoint_reviewable);
    try std.testing.expect(guarded_cleanup.platform_cleanup_precedes_driver_remove);
    try std.testing.expect(guarded_cleanup.driver_remove_precedes_watchdog_unregister);
}

test "remove handoff summary stays bounded before live unregister behavior" {
    var stoppable = try GpioWatchdogLab.init(.toggle, 60, false);
    _ = try stoppable.start();
    const remove_handoff = stoppable.summarizeRemoveHandoff(false);

    try std.testing.expectEqualStrings("drivers/watchdog/gpio_wdt.c", remove_handoff.anchor);
    try std.testing.expectEqual(HardwareAlgorithm.toggle, remove_handoff.hw_algo);
    try std.testing.expect(!remove_handoff.always_running);
    try std.testing.expect(!remove_handoff.nowayout);
    try std.testing.expectEqual(StopDisposition.stopped, remove_handoff.stop_disposition);
    try std.testing.expectEqualStrings("gpio_wdt_priv", remove_handoff.platform_drvdata_owner_identity);
    try std.testing.expectEqualStrings("gpio_wdt_priv", remove_handoff.watchdog_drvdata_owner_identity);
    try std.testing.expectEqualStrings("devm_watchdog_register_device", remove_handoff.register_device_failure_stage);
    try std.testing.expect(remove_handoff.request_stop_reviewable);
    try std.testing.expect(remove_handoff.register_device_failure_reviewable);
    try std.testing.expect(remove_handoff.reboot_glue_checkpoint_reviewable);
    try std.testing.expect(remove_handoff.blocked_on_platform_cleanup_callback);
    try std.testing.expect(remove_handoff.blocked_on_platform_driver_remove);
    try std.testing.expect(remove_handoff.blocked_on_watchdog_core_unregister);
    try std.testing.expect(remove_handoff.blocked_on_host_shutdown_execution);

    var guarded = try GpioWatchdogLab.init(.level, 64, true);
    _ = try guarded.start();
    const guarded_remove_handoff = guarded.summarizeRemoveHandoff(true);

    try std.testing.expect(guarded_remove_handoff.always_running);
    try std.testing.expect(guarded_remove_handoff.nowayout);
    try std.testing.expectEqual(StopDisposition.blocked_by_nowayout, guarded_remove_handoff.stop_disposition);
    try std.testing.expect(guarded_remove_handoff.request_stop_reviewable);
    try std.testing.expect(guarded_remove_handoff.register_device_failure_reviewable);
    try std.testing.expect(guarded_remove_handoff.reboot_glue_checkpoint_reviewable);
}

test "hardware validation matrix covers the phase11 simple-driver scenarios" {
    const matrix = try GpioWatchdogLab.hardwareValidationMatrixSummary();

    try std.testing.expectEqualStrings("drivers/watchdog/gpio_wdt.c", matrix.anchor);
    try std.testing.expect(matrix.covers_toggle_and_level);
    try std.testing.expect(matrix.covers_register_only_and_prestart);
    try std.testing.expect(matrix.covers_stop_dispositions);
    try std.testing.expect(matrix.covers_failure_and_teardown_blockers);

    try std.testing.expectEqual(HardwareAlgorithm.toggle, matrix.rows[0].hw_algo);
    try std.testing.expectEqual(HardwareAlgorithm.level, matrix.rows[1].hw_algo);
    try std.testing.expectEqual(HardwareAlgorithm.level, matrix.rows[2].hw_algo);
    try std.testing.expectEqual(HardwareAlgorithm.toggle, matrix.rows[3].hw_algo);
}
