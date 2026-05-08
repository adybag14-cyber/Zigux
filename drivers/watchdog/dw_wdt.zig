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

pub const RegistrationScaffoldState = enum {
    blocked_missing_drvdata,
    program_timeout_then_register,
    import_running_state_then_register,
};

pub const TimerClockPath = enum {
    dedicated_tclk,
    shared_clk_fallback,
};

pub const TimerClockSelection = enum {
    named_tclk,
    unnamed_shared_fallback,
    blocked_no_timer_clock,
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

pub const PlatformHandoffSummary = struct {
    anchor: []const u8,
    registration_call: []const u8,
    parent_anchor: []const u8,
    drvdata_anchor: []const u8,
    top_source: TopSource,
    timeout_origin: ProbeTimeoutOrigin,
    rate_hz: u32,
    reset_control_available: bool,
    irq_registration_ready: bool,
    drvdata_ready: bool,
    registration_state: RegistrationScaffoldState,
    registration_ready: bool,
    preserves_pretimeout_irq: bool,
    nowayout: bool,
    restart_priority: i32,
    stop_on_reboot: bool,
    can_stop: bool,
    timeout_sec: u32,
    pretimeout_sec: u32,
    imported_running_state: bool,
    needs_timeout_programming: bool,
};

pub const RegistrationOrderSummary = struct {
    anchor: []const u8,
    registration_call: []const u8,
    drvdata_anchor: []const u8,
    timer_clock_path: TimerClockPath,
    apb_clock_optional: bool,
    apb_clock_present: bool,
    reset_control_available: bool,
    irq_registration_ready: bool,
    drvdata_ready: bool,
    timeout_origin: ProbeTimeoutOrigin,
    timeout_programmed_before_register: bool,
    imported_running_state_before_register: bool,
    watchdog_info_supports_pretimeout: bool,
    nowayout: bool,
    restart_priority: i32,
    stop_on_reboot: bool,
    register_device_requested: bool,
    reset_deassert_precedes_timeout_init: bool,
    timeout_init_precedes_drvdata: bool,
    drvdata_precedes_restart_priority: bool,
    restart_priority_precedes_stop_on_reboot: bool,
    stop_on_reboot_precedes_register_device: bool,
    blocked_on_live_platform_registration: bool,
    blocked_on_live_mmio: bool,
};

pub const PlatformRegistrationScaffoldSummary = struct {
    anchor: []const u8,
    platform_driver_anchor: []const u8,
    probe_anchor: []const u8,
    remove_anchor: []const u8,
    shutdown_anchor: []const u8,
    registration_call: []const u8,
    drvdata_anchor: []const u8,
    timer_clock_path: TimerClockPath,
    apb_clock_optional: bool,
    apb_clock_present: bool,
    reset_control_available: bool,
    irq_registration_ready: bool,
    drvdata_ready: bool,
    registration_state: RegistrationScaffoldState,
    timeout_origin: ProbeTimeoutOrigin,
    timeout_programmed_before_register: bool,
    imported_running_state_before_register: bool,
    watchdog_info_supports_pretimeout: bool,
    nowayout: bool,
    restart_priority: i32,
    stop_on_reboot: bool,
    register_device_requested: bool,
    probe_path_reviewable: bool,
    remove_path_reviewable: bool,
    shutdown_path_reviewable: bool,
    blocked_on_live_platform_registration: bool,
    blocked_on_live_mmio: bool,
};

pub const PlatformResourcePreflightOptions = struct {
    has_named_tclk: bool = false,
    has_shared_clock: bool = true,
    has_pclk: bool = false,
    has_reset_control: bool = false,
    has_pretimeout_irq: bool = false,
};

pub const PlatformResourcePreflightSummary = struct {
    anchor: []const u8,
    timer_clock_selection: TimerClockSelection,
    uses_shared_clock_fallback: bool,
    timer_clock_available: bool,
    timer_clock_get_call: []const u8,
    apb_clock_optional: bool,
    apb_clock_present: bool,
    apb_clock_get_call: []const u8,
    reset_control_available: bool,
    reset_control_get_call: []const u8,
    pretimeout_irq_optional: bool,
    pretimeout_irq_present: bool,
    pretimeout_irq_call: []const u8,
    blocked_on_missing_timer_clock: bool,
    keeps_platform_registration_blocked: bool,
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

pub const TeardownOutcome = enum {
    reset_control_stop,
    continued_heartbeat,
    idle_noop,
};

pub const TeardownSummary = struct {
    anchor: []const u8,
    can_stop: bool,
    running_before_teardown: bool,
    timeout_sec: u32,
    response_mode: ResponseMode,
    outcome: TeardownOutcome,
    stop_invoked: bool,
    enable_bit_cleared: bool,
    interrupt_cleared: bool,
    running_after_teardown: bool,
    hardware_running_after_teardown: bool,
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
            .touches_platform_registration = true,
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

    pub fn platformHandoffSummary(
        self: *Self,
        options: ProbeOptions,
        has_pretimeout_irq: bool,
        irq_registration_ready: bool,
        drvdata_ready: bool,
    ) !PlatformHandoffSummary {
        const registration = try self.registrationSummary(
            options,
            has_pretimeout_irq and irq_registration_ready,
        );
        const registration_state: RegistrationScaffoldState = if (!drvdata_ready)
            .blocked_missing_drvdata
        else if (registration.imported_running_state)
            .import_running_state_then_register
        else
            .program_timeout_then_register;
        return .{
            .anchor = descriptor().anchor,
            .registration_call = registration.registration_call,
            .parent_anchor = registration.parent_anchor,
            .drvdata_anchor = "platform_set_drvdata",
            .top_source = self.top_source,
            .timeout_origin = registration.timeout_origin,
            .rate_hz = self.rate_hz,
            .reset_control_available = self.has_reset_control,
            .irq_registration_ready = irq_registration_ready,
            .drvdata_ready = drvdata_ready,
            .registration_state = registration_state,
            .registration_ready = drvdata_ready,
            .preserves_pretimeout_irq = registration.pretimeout_sec != 0,
            .nowayout = registration.nowayout,
            .restart_priority = registration.restart_priority,
            .stop_on_reboot = registration.stop_on_reboot,
            .can_stop = registration.can_stop,
            .timeout_sec = registration.timeout_sec,
            .pretimeout_sec = registration.pretimeout_sec,
            .imported_running_state = registration.imported_running_state,
            .needs_timeout_programming = registration.needs_timeout_programming,
        };
    }

    pub fn registrationOrderSummary(
        self: *Self,
        options: ProbeOptions,
        has_pretimeout_irq: bool,
        irq_registration_ready: bool,
        drvdata_ready: bool,
        uses_dedicated_tclk: bool,
        has_pclk: bool,
    ) !RegistrationOrderSummary {
        const handoff = try self.platformHandoffSummary(
            options,
            has_pretimeout_irq,
            irq_registration_ready,
            drvdata_ready,
        );
        return .{
            .anchor = handoff.anchor,
            .registration_call = handoff.registration_call,
            .drvdata_anchor = handoff.drvdata_anchor,
            .timer_clock_path = if (uses_dedicated_tclk) .dedicated_tclk else .shared_clk_fallback,
            .apb_clock_optional = true,
            .apb_clock_present = has_pclk,
            .reset_control_available = handoff.reset_control_available,
            .irq_registration_ready = handoff.irq_registration_ready,
            .drvdata_ready = handoff.drvdata_ready,
            .timeout_origin = handoff.timeout_origin,
            .timeout_programmed_before_register = handoff.needs_timeout_programming,
            .imported_running_state_before_register = handoff.imported_running_state,
            .watchdog_info_supports_pretimeout = handoff.pretimeout_sec != 0,
            .nowayout = handoff.nowayout,
            .restart_priority = handoff.restart_priority,
            .stop_on_reboot = handoff.stop_on_reboot,
            .register_device_requested = handoff.registration_ready,
            .reset_deassert_precedes_timeout_init = handoff.reset_control_available,
            .timeout_init_precedes_drvdata = true,
            .drvdata_precedes_restart_priority = true,
            .restart_priority_precedes_stop_on_reboot = true,
            .stop_on_reboot_precedes_register_device = true,
            .blocked_on_live_platform_registration = true,
            .blocked_on_live_mmio = true,
        };
    }

    pub fn platformRegistrationScaffoldSummary(
        self: *Self,
        options: ProbeOptions,
        has_pretimeout_irq: bool,
        irq_registration_ready: bool,
        drvdata_ready: bool,
        uses_dedicated_tclk: bool,
        has_pclk: bool,
    ) !PlatformRegistrationScaffoldSummary {
        const handoff = try self.platformHandoffSummary(
            options,
            has_pretimeout_irq,
            irq_registration_ready,
            drvdata_ready,
        );
        const order = try self.registrationOrderSummary(
            options,
            has_pretimeout_irq,
            irq_registration_ready,
            drvdata_ready,
            uses_dedicated_tclk,
            has_pclk,
        );
        return .{
            .anchor = handoff.anchor,
            .platform_driver_anchor = "module_platform_driver",
            .probe_anchor = "dw_wdt_drv_probe",
            .remove_anchor = "dw_wdt_drv_remove",
            .shutdown_anchor = "dw_wdt_drv_shutdown",
            .registration_call = order.registration_call,
            .drvdata_anchor = order.drvdata_anchor,
            .timer_clock_path = order.timer_clock_path,
            .apb_clock_optional = order.apb_clock_optional,
            .apb_clock_present = order.apb_clock_present,
            .reset_control_available = order.reset_control_available,
            .irq_registration_ready = order.irq_registration_ready,
            .drvdata_ready = order.drvdata_ready,
            .registration_state = handoff.registration_state,
            .timeout_origin = order.timeout_origin,
            .timeout_programmed_before_register = order.timeout_programmed_before_register,
            .imported_running_state_before_register = order.imported_running_state_before_register,
            .watchdog_info_supports_pretimeout = order.watchdog_info_supports_pretimeout,
            .nowayout = order.nowayout,
            .restart_priority = order.restart_priority,
            .stop_on_reboot = order.stop_on_reboot,
            .register_device_requested = order.register_device_requested,
            .probe_path_reviewable = true,
            .remove_path_reviewable = true,
            .shutdown_path_reviewable = true,
            .blocked_on_live_platform_registration = order.blocked_on_live_platform_registration,
            .blocked_on_live_mmio = order.blocked_on_live_mmio,
        };
    }

    pub fn platformResourcePreflightSummary(
        options: PlatformResourcePreflightOptions,
    ) PlatformResourcePreflightSummary {
        const selection: TimerClockSelection = if (options.has_named_tclk)
            .named_tclk
        else if (options.has_shared_clock)
            .unnamed_shared_fallback
        else
            .blocked_no_timer_clock;
        return .{
            .anchor = descriptor().anchor,
            .timer_clock_selection = selection,
            .uses_shared_clock_fallback = !options.has_named_tclk and options.has_shared_clock,
            .timer_clock_available = options.has_named_tclk or options.has_shared_clock,
            .timer_clock_get_call = "devm_clk_get_enabled",
            .apb_clock_optional = true,
            .apb_clock_present = options.has_pclk,
            .apb_clock_get_call = "devm_clk_get_optional_enabled",
            .reset_control_available = options.has_reset_control,
            .reset_control_get_call = "devm_reset_control_get_optional_shared",
            .pretimeout_irq_optional = true,
            .pretimeout_irq_present = options.has_pretimeout_irq,
            .pretimeout_irq_call = "platform_get_irq_optional",
            .blocked_on_missing_timer_clock = selection == .blocked_no_timer_clock,
            .keeps_platform_registration_blocked = true,
        };
    }

    pub fn teardownSummary(self: *Self) !TeardownSummary {
        const running_before_teardown = self.isEnabled();
        const runtime = if (running_before_teardown)
            self.stop()
        else blk: {
            self.registers.current_count = 0;
            self.registers.restart = 0;
            self.registers.interrupt_status = 0;
            self.hardware_running = false;
            break :blk self.runtimeSnapshot();
        };
        return .{
            .anchor = descriptor().anchor,
            .can_stop = self.has_reset_control,
            .running_before_teardown = running_before_teardown,
            .timeout_sec = self.actual_timeout_sec,
            .response_mode = self.response_mode,
            .outcome = if (!running_before_teardown)
                .idle_noop
            else if (self.has_reset_control)
                .reset_control_stop
            else
                .continued_heartbeat,
            .stop_invoked = running_before_teardown,
            .enable_bit_cleared = !running_before_teardown or
                (runtime.registers.control & control_reg_wdt_en_mask) == 0,
            .interrupt_cleared = !running_before_teardown or runtime.registers.interrupt_status == 0,
            .running_after_teardown = runtime.running,
            .hardware_running_after_teardown = runtime.hardware_running,
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
        } else {
            self.registers.current_count = 0;
            self.registers.restart = 0;
            self.registers.interrupt_status = 0;
            self.hardware_running = false;
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

test "platform handoff keeps the bounded drvdata handoff explicit when irq wiring is ready" {
    var watchdog = try DwWdtLab.initFixedTops(65_536, true);
    _ = watchdog.loadRegisters(.{
        .control = control_reg_wdt_en_mask | control_reg_resp_mode_mask,
        .timeout_range = 0x33,
        .current_count = 2 * 65_536,
    });

    const handoff = try watchdog.platformHandoffSummary(.{
        .nowayout = false,
        .stop_on_reboot = true,
    }, true, true, true);

    try std.testing.expectEqualStrings("platform_set_drvdata", handoff.drvdata_anchor);
    try std.testing.expect(handoff.irq_registration_ready);
    try std.testing.expect(handoff.drvdata_ready);
    try std.testing.expectEqual(@as(u32, 16), handoff.timeout_sec);
    try std.testing.expectEqual(@as(u32, 8), handoff.pretimeout_sec);
}

test "platform handoff keeps the same drvdata anchor when irq or drvdata are still blocked" {
    var watchdog = try DwWdtLab.initCustomTops(1_000, false, [_]u32{
        20_000, 4_000,  8_000,  12_000,
        16_000, 24_000, 28_000, 32_000,
        36_000, 40_000, 44_000, 48_000,
        52_000, 56_000, 60_000, 64_000,
    });

    const handoff = try watchdog.platformHandoffSummary(.{
        .nowayout = true,
        .requested_timeout_sec = 11,
        .stop_on_reboot = true,
    }, true, false, false);

    try std.testing.expectEqualStrings("platform_set_drvdata", handoff.drvdata_anchor);
    try std.testing.expect(!handoff.irq_registration_ready);
    try std.testing.expect(!handoff.drvdata_ready);
    try std.testing.expectEqual(TopSource.custom, handoff.top_source);
    try std.testing.expectEqual(@as(u32, 12), handoff.timeout_sec);
    try std.testing.expectEqual(@as(u32, 0), handoff.pretimeout_sec);
}

test "registration order summary keeps timeout programming and policy ordering explicit before registration" {
    var watchdog = try DwWdtLab.initCustomTops(1_000, false, [_]u32{
        20_000, 4_000,  8_000,  12_000,
        16_000, 24_000, 28_000, 32_000,
        36_000, 40_000, 44_000, 48_000,
        52_000, 56_000, 60_000, 64_000,
    });

    const summary = try watchdog.registrationOrderSummary(.{
        .nowayout = true,
        .requested_timeout_sec = 11,
        .stop_on_reboot = true,
    }, true, false, true, false, false);

    try std.testing.expectEqualStrings("drivers/watchdog/dw_wdt.c", summary.anchor);
    try std.testing.expectEqualStrings("watchdog_register_device", summary.registration_call);
    try std.testing.expectEqualStrings("platform_set_drvdata", summary.drvdata_anchor);
    try std.testing.expectEqual(TimerClockPath.shared_clk_fallback, summary.timer_clock_path);
    try std.testing.expect(summary.apb_clock_optional);
    try std.testing.expect(!summary.apb_clock_present);
    try std.testing.expect(!summary.reset_control_available);
    try std.testing.expect(!summary.irq_registration_ready);
    try std.testing.expect(summary.drvdata_ready);
    try std.testing.expectEqual(ProbeTimeoutOrigin.default_selection, summary.timeout_origin);
    try std.testing.expect(summary.timeout_programmed_before_register);
    try std.testing.expect(!summary.imported_running_state_before_register);
    try std.testing.expect(!summary.watchdog_info_supports_pretimeout);
    try std.testing.expectEqual(default_restart_priority, summary.restart_priority);
    try std.testing.expect(summary.stop_on_reboot);
    try std.testing.expect(summary.register_device_requested);
    try std.testing.expect(!summary.reset_deassert_precedes_timeout_init);
    try std.testing.expect(summary.timeout_init_precedes_drvdata);
    try std.testing.expect(summary.drvdata_precedes_restart_priority);
    try std.testing.expect(summary.restart_priority_precedes_stop_on_reboot);
    try std.testing.expect(summary.stop_on_reboot_precedes_register_device);
    try std.testing.expect(summary.blocked_on_live_platform_registration);
    try std.testing.expect(summary.blocked_on_live_mmio);
}

test "registration order summary keeps imported running state and pretimeout readiness explicit" {
    var watchdog = try DwWdtLab.initFixedTops(65_536, true);
    _ = watchdog.loadRegisters(.{
        .control = control_reg_wdt_en_mask | control_reg_resp_mode_mask,
        .timeout_range = 0x33,
        .current_count = 2 * 65_536,
    });

    const summary = try watchdog.registrationOrderSummary(.{
        .nowayout = false,
        .stop_on_reboot = true,
    }, true, true, true, true, true);

    try std.testing.expectEqual(TimerClockPath.dedicated_tclk, summary.timer_clock_path);
    try std.testing.expect(summary.apb_clock_optional);
    try std.testing.expect(summary.apb_clock_present);
    try std.testing.expect(summary.reset_control_available);
    try std.testing.expect(summary.irq_registration_ready);
    try std.testing.expect(summary.drvdata_ready);
    try std.testing.expectEqual(ProbeTimeoutOrigin.imported_running_state, summary.timeout_origin);
    try std.testing.expect(!summary.timeout_programmed_before_register);
    try std.testing.expect(summary.imported_running_state_before_register);
    try std.testing.expect(summary.watchdog_info_supports_pretimeout);
    try std.testing.expect(!summary.nowayout);
    try std.testing.expect(summary.stop_on_reboot);
    try std.testing.expect(summary.register_device_requested);
    try std.testing.expect(!summary.reset_deassert_precedes_timeout_init);
    try std.testing.expect(summary.timeout_init_precedes_drvdata);
    try std.testing.expect(summary.drvdata_precedes_restart_priority);
    try std.testing.expect(summary.restart_priority_precedes_stop_on_reboot);
    try std.testing.expect(summary.stop_on_reboot_precedes_register_device);
}

test "platform registration scaffold keeps the bounded driver anchors explicit when imported state is ready" {
    var watchdog = try DwWdtLab.initFixedTops(65_536, true);
    _ = watchdog.loadRegisters(.{
        .control = control_reg_wdt_en_mask | control_reg_resp_mode_mask,
        .timeout_range = 0x33,
        .current_count = 2 * 65_536,
    });

    const summary = try watchdog.platformRegistrationScaffoldSummary(.{
        .nowayout = false,
        .stop_on_reboot = true,
    }, true, true, true, true, true);

    try std.testing.expectEqualStrings("drivers/watchdog/dw_wdt.c", summary.anchor);
    try std.testing.expectEqualStrings("module_platform_driver", summary.platform_driver_anchor);
    try std.testing.expectEqualStrings("dw_wdt_drv_probe", summary.probe_anchor);
    try std.testing.expectEqualStrings("dw_wdt_drv_remove", summary.remove_anchor);
    try std.testing.expectEqualStrings("dw_wdt_drv_shutdown", summary.shutdown_anchor);
    try std.testing.expectEqualStrings("watchdog_register_device", summary.registration_call);
    try std.testing.expectEqualStrings("platform_set_drvdata", summary.drvdata_anchor);
    try std.testing.expectEqual(TimerClockPath.dedicated_tclk, summary.timer_clock_path);
    try std.testing.expect(summary.apb_clock_optional);
    try std.testing.expect(summary.apb_clock_present);
    try std.testing.expect(summary.reset_control_available);
    try std.testing.expect(summary.irq_registration_ready);
    try std.testing.expect(summary.drvdata_ready);
    try std.testing.expectEqual(RegistrationScaffoldState.import_running_state_then_register, summary.registration_state);
    try std.testing.expectEqual(ProbeTimeoutOrigin.imported_running_state, summary.timeout_origin);
    try std.testing.expect(!summary.timeout_programmed_before_register);
    try std.testing.expect(summary.imported_running_state_before_register);
    try std.testing.expect(summary.watchdog_info_supports_pretimeout);
    try std.testing.expect(!summary.nowayout);
    try std.testing.expectEqual(default_restart_priority, summary.restart_priority);
    try std.testing.expect(summary.stop_on_reboot);
    try std.testing.expect(summary.register_device_requested);
    try std.testing.expect(summary.probe_path_reviewable);
    try std.testing.expect(summary.remove_path_reviewable);
    try std.testing.expect(summary.shutdown_path_reviewable);
    try std.testing.expect(summary.blocked_on_live_platform_registration);
    try std.testing.expect(summary.blocked_on_live_mmio);
}

test "platform registration scaffold keeps timeout programming explicit when drvdata publication is still missing" {
    var watchdog = try DwWdtLab.initCustomTops(1_000, false, [_]u32{
        20_000, 4_000,  8_000,  12_000,
        16_000, 24_000, 28_000, 32_000,
        36_000, 40_000, 44_000, 48_000,
        52_000, 56_000, 60_000, 64_000,
    });

    const summary = try watchdog.platformRegistrationScaffoldSummary(.{
        .nowayout = true,
        .requested_timeout_sec = 11,
        .stop_on_reboot = true,
    }, true, false, false, false, false);

    try std.testing.expectEqualStrings("module_platform_driver", summary.platform_driver_anchor);
    try std.testing.expectEqual(TimerClockPath.shared_clk_fallback, summary.timer_clock_path);
    try std.testing.expect(summary.apb_clock_optional);
    try std.testing.expect(!summary.apb_clock_present);
    try std.testing.expect(!summary.reset_control_available);
    try std.testing.expect(!summary.irq_registration_ready);
    try std.testing.expect(!summary.drvdata_ready);
    try std.testing.expectEqual(RegistrationScaffoldState.blocked_missing_drvdata, summary.registration_state);
    try std.testing.expectEqual(ProbeTimeoutOrigin.default_selection, summary.timeout_origin);
    try std.testing.expect(summary.timeout_programmed_before_register);
    try std.testing.expect(!summary.imported_running_state_before_register);
    try std.testing.expect(!summary.watchdog_info_supports_pretimeout);
    try std.testing.expect(summary.nowayout);
    try std.testing.expectEqual(default_restart_priority, summary.restart_priority);
    try std.testing.expect(summary.stop_on_reboot);
    try std.testing.expect(!summary.register_device_requested);
    try std.testing.expect(summary.probe_path_reviewable);
    try std.testing.expect(summary.remove_path_reviewable);
    try std.testing.expect(summary.shutdown_path_reviewable);
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

test "idle remove without reset control clears stale bookkeeping once hardware is already stopped" {
    var lab = try DwWdtLab.initFixedTops(65_536, false);
    _ = lab.setCurrentCount(5 * 65_536);
    _ = lab.setInterruptPending(true);

    const summary = lab.removeSummary();
    try std.testing.expect(summary.debugfs_clear_requested);
    try std.testing.expect(summary.unregister_device_requested);
    try std.testing.expect(!summary.reset_control_available);
    try std.testing.expect(!summary.reset_assert_requested);
    try std.testing.expect(!summary.hardware_running_before_remove);
    try std.testing.expect(!summary.hardware_running_after_remove);
    try std.testing.expect(!summary.running_after_remove);
    try std.testing.expect(!summary.interrupt_pending_after_remove);
    try std.testing.expect(!summary.remove_leaves_hardware_running);

    const runtime = lab.runtimeSnapshot();
    try std.testing.expectEqual(@as(u32, 0), runtime.registers.current_count);
    try std.testing.expectEqual(@as(u32, 0), runtime.registers.restart);
    try std.testing.expect(!runtime.interrupt_pending);
    try std.testing.expectError(error.WatchdogNotRunning, lab.ping());
}

test "teardown summary records idle no-op plus active stop-backed outcomes" {
    var unstoppable = try DwWdtLab.initFixedTops(65_536, false);
    _ = unstoppable.setCurrentCount(5 * 65_536);
    _ = unstoppable.setInterruptPending(true);
    const idle_unstoppable_teardown = try unstoppable.teardownSummary();
    try std.testing.expectEqualStrings("drivers/watchdog/dw_wdt.c", idle_unstoppable_teardown.anchor);
    try std.testing.expect(!idle_unstoppable_teardown.can_stop);
    try std.testing.expect(!idle_unstoppable_teardown.running_before_teardown);
    try std.testing.expectEqual(@as(u32, 32), idle_unstoppable_teardown.timeout_sec);
    try std.testing.expectEqual(ResponseMode.reset, idle_unstoppable_teardown.response_mode);
    try std.testing.expectEqual(TeardownOutcome.idle_noop, idle_unstoppable_teardown.outcome);
    try std.testing.expect(!idle_unstoppable_teardown.stop_invoked);
    try std.testing.expect(idle_unstoppable_teardown.enable_bit_cleared);
    try std.testing.expect(idle_unstoppable_teardown.interrupt_cleared);
    try std.testing.expect(!idle_unstoppable_teardown.running_after_teardown);
    try std.testing.expect(!idle_unstoppable_teardown.hardware_running_after_teardown);
    const idle_unstoppable_runtime = unstoppable.runtimeSnapshot();
    try std.testing.expectEqual(@as(u32, 0), idle_unstoppable_runtime.registers.current_count);
    try std.testing.expectEqual(@as(u32, 0), idle_unstoppable_runtime.registers.restart);
    try std.testing.expect(!idle_unstoppable_runtime.interrupt_pending);

    _ = try unstoppable.start();
    const unstoppable_teardown = try unstoppable.teardownSummary();
    try std.testing.expectEqualStrings("drivers/watchdog/dw_wdt.c", unstoppable_teardown.anchor);
    try std.testing.expect(!unstoppable_teardown.can_stop);
    try std.testing.expect(unstoppable_teardown.running_before_teardown);
    try std.testing.expectEqual(@as(u32, 32), unstoppable_teardown.timeout_sec);
    try std.testing.expectEqual(ResponseMode.reset, unstoppable_teardown.response_mode);
    try std.testing.expectEqual(TeardownOutcome.continued_heartbeat, unstoppable_teardown.outcome);
    try std.testing.expect(unstoppable_teardown.stop_invoked);
    try std.testing.expect(!unstoppable_teardown.enable_bit_cleared);
    try std.testing.expect(unstoppable_teardown.interrupt_cleared);
    try std.testing.expect(unstoppable_teardown.running_after_teardown);
    try std.testing.expect(unstoppable_teardown.hardware_running_after_teardown);

    var stoppable = try DwWdtLab.initFixedTops(65_536, true);
    _ = stoppable.setCurrentCount(3 * 65_536);
    _ = stoppable.setInterruptPending(true);
    const idle_stoppable_teardown = try stoppable.teardownSummary();
    try std.testing.expect(idle_stoppable_teardown.can_stop);
    try std.testing.expect(!idle_stoppable_teardown.running_before_teardown);
    try std.testing.expectEqual(@as(u32, 32), idle_stoppable_teardown.timeout_sec);
    try std.testing.expectEqual(ResponseMode.reset, idle_stoppable_teardown.response_mode);
    try std.testing.expectEqual(TeardownOutcome.idle_noop, idle_stoppable_teardown.outcome);
    try std.testing.expect(!idle_stoppable_teardown.stop_invoked);
    try std.testing.expect(idle_stoppable_teardown.enable_bit_cleared);
    try std.testing.expect(idle_stoppable_teardown.interrupt_cleared);
    try std.testing.expect(!idle_stoppable_teardown.running_after_teardown);
    try std.testing.expect(!idle_stoppable_teardown.hardware_running_after_teardown);
    const idle_stoppable_runtime = stoppable.runtimeSnapshot();
    try std.testing.expectEqual(@as(u32, 0), idle_stoppable_runtime.registers.current_count);
    try std.testing.expectEqual(@as(u32, 0), idle_stoppable_runtime.registers.restart);
    try std.testing.expect(!idle_stoppable_runtime.interrupt_pending);

    _ = try stoppable.start();
    const stoppable_teardown = try stoppable.teardownSummary();
    try std.testing.expect(stoppable_teardown.can_stop);
    try std.testing.expect(stoppable_teardown.running_before_teardown);
    try std.testing.expectEqual(@as(u32, 32), stoppable_teardown.timeout_sec);
    try std.testing.expectEqual(ResponseMode.reset, stoppable_teardown.response_mode);
    try std.testing.expectEqual(TeardownOutcome.reset_control_stop, stoppable_teardown.outcome);
    try std.testing.expect(stoppable_teardown.stop_invoked);
    try std.testing.expect(stoppable_teardown.enable_bit_cleared);
    try std.testing.expect(stoppable_teardown.interrupt_cleared);
    try std.testing.expect(!stoppable_teardown.running_after_teardown);
    try std.testing.expect(!stoppable_teardown.hardware_running_after_teardown);
}
