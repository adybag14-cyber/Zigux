const std = @import("std");

pub const anchor_path = "drivers/watchdog/dw_wdt.c";
pub const default_restart_priority: i32 = 128;

pub const TimerClockSelection = enum {
    named_tclk,
    unnamed_shared_fallback,
    blocked_no_timer_clock,
};

pub const ApbClockSelection = enum {
    optional_present,
    optional_absent,
};

pub const TimerClockPath = TimerClockSelection;
pub const ApbClockPath = ApbClockSelection;

pub const ProbeTimeoutOrigin = enum {
    programmed_top_window,
    imported_running_counter,
    blocked_missing_timer_clock,
    blocked_on_live_mmio,
};

pub const RegistrationScaffoldState = enum {
    blocked_missing_drvdata,
    blocked_missing_timer_clock,
    blocked_on_live_mmio,
    import_running_state_then_register,
    ready_to_register,
};

pub const PlatformResourcePreflightRequest = struct {
    has_named_tclk: bool,
    has_shared_clock: bool,
    has_pclk: bool,
    has_reset_control: bool,
    has_pretimeout_irq: bool,
};

pub const PlatformResourcePreflightSummary = struct {
    anchor: []const u8,
    timer_clock_selection: TimerClockSelection,
    uses_shared_clock_fallback: bool,
    timer_clock_available: bool,
    timer_clock_get_call: []const u8,
    apb_clock_selection: ApbClockSelection,
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

pub fn platformResourcePreflightSummary(
    request: PlatformResourcePreflightRequest,
) PlatformResourcePreflightSummary {
    const timer_clock_selection: TimerClockSelection = if (request.has_named_tclk)
        .named_tclk
    else if (request.has_shared_clock)
        .unnamed_shared_fallback
    else
        .blocked_no_timer_clock;
    const apb_clock_selection: ApbClockSelection = if (request.has_pclk)
        .optional_present
    else
        .optional_absent;

    const timer_clock_available = timer_clock_selection != .blocked_no_timer_clock;

    return .{
        .anchor = anchor_path,
        .timer_clock_selection = timer_clock_selection,
        .uses_shared_clock_fallback = timer_clock_selection == .unnamed_shared_fallback,
        .timer_clock_available = timer_clock_available,
        .timer_clock_get_call = "devm_clk_get_enabled",
        .apb_clock_selection = apb_clock_selection,
        .apb_clock_optional = true,
        .apb_clock_present = apb_clock_selection == .optional_present,
        .apb_clock_get_call = "devm_clk_get_optional_enabled",
        .reset_control_available = request.has_reset_control,
        .reset_control_get_call = "devm_reset_control_get_optional_shared",
        .pretimeout_irq_optional = true,
        .pretimeout_irq_present = request.has_pretimeout_irq,
        .pretimeout_irq_call = "platform_get_irq_optional",
        .blocked_on_missing_timer_clock = !timer_clock_available,
        .keeps_platform_registration_blocked = true,
    };
}

pub const PlatformHandoffRequest = struct {
    has_named_tclk: bool,
    has_shared_clock: bool,
    has_pclk: bool,
    has_reset_control: bool,
    has_pretimeout_irq: bool,
    drvdata_published: bool,
    timeout_programmed: bool,
    imported_running: bool,
};

pub const PlatformHandoffSummary = struct {
    anchor: []const u8,
    state: RegistrationScaffoldState,
    timer_clock_path: TimerClockPath,
    probe_timeout_origin: ProbeTimeoutOrigin,
    timer_clock_available: bool,
    apb_clock_path: ApbClockPath,
    apb_clock_present: bool,
    reset_control_available: bool,
    reset_release_call: []const u8,
    reset_release_requested: bool,
    pretimeout_irq_optional: bool,
    pretimeout_irq_present: bool,
    pretimeout_irq_call: []const u8,
    drvdata_published: bool,
    timeout_programming_requested: bool,
    imported_running_state: bool,
    stop_on_reboot_requested: bool,
    restart_priority_value: i32,
    registration_ready: bool,
    blocked_on_live_platform_registration: bool,
    blocked_on_live_mmio: bool,
};

pub fn platformHandoffSummary(request: PlatformHandoffRequest) PlatformHandoffSummary {
    const preflight = platformResourcePreflightSummary(.{
        .has_named_tclk = request.has_named_tclk,
        .has_shared_clock = request.has_shared_clock,
        .has_pclk = request.has_pclk,
        .has_reset_control = request.has_reset_control,
        .has_pretimeout_irq = request.has_pretimeout_irq,
    });

    const reset_release_requested = request.drvdata_published and
        preflight.timer_clock_available and
        preflight.reset_control_available;

    if (!request.drvdata_published) {
        return .{
            .anchor = anchor_path,
            .state = .blocked_missing_drvdata,
            .timer_clock_path = preflight.timer_clock_selection,
            .probe_timeout_origin = .blocked_on_live_mmio,
            .timer_clock_available = preflight.timer_clock_available,
            .apb_clock_path = preflight.apb_clock_selection,
            .apb_clock_present = preflight.apb_clock_present,
            .reset_control_available = preflight.reset_control_available,
            .reset_release_call = "reset_control_deassert",
            .reset_release_requested = false,
            .pretimeout_irq_optional = preflight.pretimeout_irq_optional,
            .pretimeout_irq_present = preflight.pretimeout_irq_present,
            .pretimeout_irq_call = preflight.pretimeout_irq_call,
            .drvdata_published = false,
            .timeout_programming_requested = false,
            .imported_running_state = request.imported_running,
            .stop_on_reboot_requested = false,
            .restart_priority_value = default_restart_priority,
            .registration_ready = false,
            .blocked_on_live_platform_registration = true,
            .blocked_on_live_mmio = false,
        };
    }

    if (!preflight.timer_clock_available) {
        return .{
            .anchor = anchor_path,
            .state = .blocked_missing_timer_clock,
            .timer_clock_path = preflight.timer_clock_selection,
            .probe_timeout_origin = .blocked_missing_timer_clock,
            .timer_clock_available = false,
            .apb_clock_path = preflight.apb_clock_selection,
            .apb_clock_present = preflight.apb_clock_present,
            .reset_control_available = preflight.reset_control_available,
            .reset_release_call = "reset_control_deassert",
            .reset_release_requested = false,
            .pretimeout_irq_optional = preflight.pretimeout_irq_optional,
            .pretimeout_irq_present = preflight.pretimeout_irq_present,
            .pretimeout_irq_call = preflight.pretimeout_irq_call,
            .drvdata_published = true,
            .timeout_programming_requested = false,
            .imported_running_state = false,
            .stop_on_reboot_requested = false,
            .restart_priority_value = default_restart_priority,
            .registration_ready = false,
            .blocked_on_live_platform_registration = true,
            .blocked_on_live_mmio = false,
        };
    }

    if (request.imported_running) {
        return .{
            .anchor = anchor_path,
            .state = .import_running_state_then_register,
            .timer_clock_path = preflight.timer_clock_selection,
            .probe_timeout_origin = .imported_running_counter,
            .timer_clock_available = true,
            .apb_clock_path = preflight.apb_clock_selection,
            .apb_clock_present = preflight.apb_clock_present,
            .reset_control_available = preflight.reset_control_available,
            .reset_release_call = "reset_control_deassert",
            .reset_release_requested = reset_release_requested,
            .pretimeout_irq_optional = preflight.pretimeout_irq_optional,
            .pretimeout_irq_present = preflight.pretimeout_irq_present,
            .pretimeout_irq_call = preflight.pretimeout_irq_call,
            .drvdata_published = true,
            .timeout_programming_requested = false,
            .imported_running_state = true,
            .stop_on_reboot_requested = true,
            .restart_priority_value = default_restart_priority,
            .registration_ready = true,
            .blocked_on_live_platform_registration = true,
            .blocked_on_live_mmio = false,
        };
    }

    if (!request.timeout_programmed) {
        return .{
            .anchor = anchor_path,
            .state = .blocked_on_live_mmio,
            .timer_clock_path = preflight.timer_clock_selection,
            .probe_timeout_origin = .blocked_on_live_mmio,
            .timer_clock_available = true,
            .apb_clock_path = preflight.apb_clock_selection,
            .apb_clock_present = preflight.apb_clock_present,
            .reset_control_available = preflight.reset_control_available,
            .reset_release_call = "reset_control_deassert",
            .reset_release_requested = reset_release_requested,
            .pretimeout_irq_optional = preflight.pretimeout_irq_optional,
            .pretimeout_irq_present = preflight.pretimeout_irq_present,
            .pretimeout_irq_call = preflight.pretimeout_irq_call,
            .drvdata_published = true,
            .timeout_programming_requested = true,
            .imported_running_state = false,
            .stop_on_reboot_requested = false,
            .restart_priority_value = default_restart_priority,
            .registration_ready = false,
            .blocked_on_live_platform_registration = true,
            .blocked_on_live_mmio = true,
        };
    }

    return .{
        .anchor = anchor_path,
        .state = .ready_to_register,
        .timer_clock_path = preflight.timer_clock_selection,
        .probe_timeout_origin = .programmed_top_window,
        .timer_clock_available = true,
        .apb_clock_path = preflight.apb_clock_selection,
        .apb_clock_present = preflight.apb_clock_present,
        .reset_control_available = preflight.reset_control_available,
        .reset_release_call = "reset_control_deassert",
        .reset_release_requested = reset_release_requested,
        .pretimeout_irq_optional = preflight.pretimeout_irq_optional,
        .pretimeout_irq_present = preflight.pretimeout_irq_present,
        .pretimeout_irq_call = preflight.pretimeout_irq_call,
        .drvdata_published = true,
        .timeout_programming_requested = true,
        .imported_running_state = false,
        .stop_on_reboot_requested = true,
        .restart_priority_value = default_restart_priority,
        .registration_ready = true,
        .blocked_on_live_platform_registration = true,
        .blocked_on_live_mmio = false,
    };
}

pub const RegistrationOrderRequest = struct {
    drvdata_published: bool,
    timeout_programmed: bool,
    imported_running: bool,
};

pub const RegistrationOrderSummary = struct {
    anchor: []const u8,
    state: RegistrationScaffoldState,
    publishes_drvdata_before_register: bool,
    imports_running_state_before_register: bool,
    programs_timeout_before_register: bool,
    stop_on_reboot_requested: bool,
    restart_priority_value: i32,
    register_call: []const u8,
    registration_requested: bool,
    blocked_on_live_platform_registration: bool,
    blocked_on_live_mmio: bool,
};

pub fn registrationOrderSummary(request: RegistrationOrderRequest) RegistrationOrderSummary {
    if (!request.drvdata_published) {
        return .{
            .anchor = anchor_path,
            .state = .blocked_missing_drvdata,
            .publishes_drvdata_before_register = false,
            .imports_running_state_before_register = false,
            .programs_timeout_before_register = false,
            .stop_on_reboot_requested = false,
            .restart_priority_value = default_restart_priority,
            .register_call = "watchdog_register_device",
            .registration_requested = false,
            .blocked_on_live_platform_registration = true,
            .blocked_on_live_mmio = false,
        };
    }

    const imported_running = request.imported_running;
    const timeout_programmed = request.timeout_programmed;
    const ready = imported_running or timeout_programmed;

    return .{
        .anchor = anchor_path,
        .state = if (imported_running)
            .import_running_state_then_register
        else if (timeout_programmed)
            .ready_to_register
        else
            .blocked_on_live_mmio,
        .publishes_drvdata_before_register = true,
        .imports_running_state_before_register = imported_running,
        .programs_timeout_before_register = timeout_programmed,
        .stop_on_reboot_requested = ready,
        .restart_priority_value = default_restart_priority,
        .register_call = "watchdog_register_device",
        .registration_requested = ready,
        .blocked_on_live_platform_registration = true,
        .blocked_on_live_mmio = !ready,
    };
}

pub const PlatformRegistrationScaffoldRequest = struct {
    has_named_tclk: bool,
    has_shared_clock: bool,
    has_pclk: bool,
    has_reset_control: bool,
    has_pretimeout_irq: bool,
    drvdata_published: bool,
    timeout_programmed: bool,
    imported_running: bool,
};

pub const PlatformRegistrationScaffoldSummary = struct {
    anchor: []const u8,
    state: RegistrationScaffoldState,
    timer_clock_path: TimerClockPath,
    apb_clock_path: ApbClockPath,
    probe_timeout_origin: ProbeTimeoutOrigin,
    registration_requested: bool,
    stop_on_reboot_requested: bool,
    restart_priority_value: i32,
    reset_release_ready: bool,
    reset_release_call: []const u8,
    reset_release_requested: bool,
    pretimeout_irq_optional: bool,
    pretimeout_irq_present: bool,
    pretimeout_irq_call: []const u8,
    blocked_on_live_platform_registration: bool,
    blocked_on_live_mmio: bool,
};

pub fn platformRegistrationScaffoldSummary(
    request: PlatformRegistrationScaffoldRequest,
) PlatformRegistrationScaffoldSummary {
    const handoff = platformHandoffSummary(.{
        .has_named_tclk = request.has_named_tclk,
        .has_shared_clock = request.has_shared_clock,
        .has_pclk = request.has_pclk,
        .has_reset_control = request.has_reset_control,
        .has_pretimeout_irq = request.has_pretimeout_irq,
        .drvdata_published = request.drvdata_published,
        .timeout_programmed = request.timeout_programmed,
        .imported_running = request.imported_running,
    });
    const order = registrationOrderSummary(.{
        .drvdata_published = request.drvdata_published,
        .timeout_programmed = request.timeout_programmed,
        .imported_running = request.imported_running,
    });

    return .{
        .anchor = anchor_path,
        .state = handoff.state,
        .timer_clock_path = handoff.timer_clock_path,
        .apb_clock_path = handoff.apb_clock_path,
        .probe_timeout_origin = handoff.probe_timeout_origin,
        .registration_requested = order.registration_requested and handoff.timer_clock_available,
        .stop_on_reboot_requested = handoff.stop_on_reboot_requested,
        .restart_priority_value = handoff.restart_priority_value,
        .reset_release_ready = request.has_reset_control,
        .reset_release_call = handoff.reset_release_call,
        .reset_release_requested = handoff.reset_release_requested,
        .pretimeout_irq_optional = handoff.pretimeout_irq_optional,
        .pretimeout_irq_present = handoff.pretimeout_irq_present,
        .pretimeout_irq_call = handoff.pretimeout_irq_call,
        .blocked_on_live_platform_registration = handoff.blocked_on_live_platform_registration,
        .blocked_on_live_mmio = handoff.blocked_on_live_mmio,
    };
}

pub const TeardownOutcome = enum {
    idle_noop,
    continued_heartbeat,
    reset_control_stop,
};

pub const TeardownSummary = struct {
    outcome: TeardownOutcome,
    can_stop: bool,
    running_before_teardown: bool,
    stop_invoked: bool,
    enable_bit_cleared: bool,
    interrupt_cleared: bool,
    running_after_teardown: bool,
    hardware_running_after_teardown: bool,
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

pub const DwWdtLab = struct {
    top_init: u32,
    reset_control_available: bool,
    running: bool = false,
    interrupt_pending: bool = false,

    pub fn initFixedTops(top_init: u32, reset_control_available: bool) !DwWdtLab {
        if (top_init == 0) return error.InvalidTopInit;
        return .{
            .top_init = top_init,
            .reset_control_available = reset_control_available,
        };
    }

    pub fn start(self: *DwWdtLab) !u32 {
        self.running = true;
        return self.top_init;
    }

    pub fn setInterruptPending(self: *DwWdtLab, pending: bool) !void {
        self.interrupt_pending = pending;
    }

    pub fn teardownSummary(self: *DwWdtLab) !TeardownSummary {
        const running_before_teardown = self.running;
        const can_stop = self.reset_control_available and running_before_teardown;
        const stop_invoked = running_before_teardown;

        self.interrupt_pending = false;
        if (can_stop) self.running = false;

        return .{
            .outcome = if (!running_before_teardown)
                .idle_noop
            else if (can_stop)
                .reset_control_stop
            else
                .continued_heartbeat,
            .can_stop = can_stop,
            .running_before_teardown = running_before_teardown,
            .stop_invoked = stop_invoked,
            .enable_bit_cleared = can_stop,
            .interrupt_cleared = true,
            .running_after_teardown = self.running,
            .hardware_running_after_teardown = self.running,
        };
    }

    pub fn removeSummary(self: *DwWdtLab) RemoveSummary {
        const hardware_running_before_remove = self.running;
        const reset_assert_requested = self.reset_control_available and hardware_running_before_remove;

        if (reset_assert_requested) self.running = false;
        self.interrupt_pending = false;

        return .{
            .anchor = anchor_path,
            .debugfs_clear_requested = true,
            .unregister_device_requested = true,
            .reset_control_available = self.reset_control_available,
            .reset_assert_requested = reset_assert_requested,
            .hardware_running_before_remove = hardware_running_before_remove,
            .hardware_running_after_remove = self.running,
            .running_after_remove = self.running,
            .interrupt_pending_after_remove = self.interrupt_pending,
            .remove_leaves_hardware_running = self.running,
        };
    }
};

test "phase11 dw_wdt registration order summary keeps blocked registration explicit" {
    const blocked = registrationOrderSummary(.{
        .drvdata_published = false,
        .timeout_programmed = true,
        .imported_running = false,
    });

    try std.testing.expectEqualStrings(anchor_path, blocked.anchor);
    try std.testing.expectEqual(RegistrationScaffoldState.blocked_missing_drvdata, blocked.state);
    try std.testing.expect(!blocked.registration_requested);
    try std.testing.expect(blocked.blocked_on_live_platform_registration);
    try std.testing.expect(!blocked.blocked_on_live_mmio);
}

test "phase11 dw_wdt platform handoff keeps reset-release intent explicit" {
    const blocked = platformHandoffSummary(.{
        .has_named_tclk = true,
        .has_shared_clock = false,
        .has_pclk = true,
        .has_reset_control = true,
        .has_pretimeout_irq = false,
        .drvdata_published = false,
        .timeout_programmed = false,
        .imported_running = false,
    });
    try std.testing.expectEqual(ApbClockPath.optional_present, blocked.apb_clock_path);
    try std.testing.expectEqualStrings("reset_control_deassert", blocked.reset_release_call);
    try std.testing.expect(!blocked.reset_release_requested);
    try std.testing.expect(blocked.pretimeout_irq_optional);
    try std.testing.expect(!blocked.pretimeout_irq_present);
    try std.testing.expectEqualStrings("platform_get_irq_optional", blocked.pretimeout_irq_call);

    const ready = platformHandoffSummary(.{
        .has_named_tclk = true,
        .has_shared_clock = false,
        .has_pclk = true,
        .has_reset_control = true,
        .has_pretimeout_irq = true,
        .drvdata_published = true,
        .timeout_programmed = false,
        .imported_running = false,
    });
    try std.testing.expectEqual(ApbClockPath.optional_present, ready.apb_clock_path);
    try std.testing.expectEqualStrings("reset_control_deassert", ready.reset_release_call);
    try std.testing.expect(ready.reset_release_requested);
    try std.testing.expect(ready.pretimeout_irq_optional);
    try std.testing.expect(ready.pretimeout_irq_present);
    try std.testing.expectEqualStrings("platform_get_irq_optional", ready.pretimeout_irq_call);
    try std.testing.expect(ready.blocked_on_live_mmio);
}

test "phase11 dw_wdt platform handoff keeps missing timer-clock acquisition explicit" {
    const summary = platformHandoffSummary(.{
        .has_named_tclk = false,
        .has_shared_clock = false,
        .has_pclk = true,
        .has_reset_control = true,
        .has_pretimeout_irq = false,
        .drvdata_published = true,
        .timeout_programmed = false,
        .imported_running = false,
    });

    try std.testing.expectEqual(
        RegistrationScaffoldState.blocked_missing_timer_clock,
        summary.state,
    );
    try std.testing.expectEqual(
        ProbeTimeoutOrigin.blocked_missing_timer_clock,
        summary.probe_timeout_origin,
    );
    try std.testing.expectEqual(ApbClockPath.optional_present, summary.apb_clock_path);
    try std.testing.expect(!summary.timer_clock_available);
    try std.testing.expect(!summary.timeout_programming_requested);
    try std.testing.expect(!summary.registration_ready);
    try std.testing.expect(!summary.stop_on_reboot_requested);
    try std.testing.expect(summary.pretimeout_irq_optional);
    try std.testing.expect(!summary.pretimeout_irq_present);
    try std.testing.expectEqualStrings("platform_get_irq_optional", summary.pretimeout_irq_call);
    try std.testing.expect(!summary.reset_release_requested);
    try std.testing.expect(summary.blocked_on_live_platform_registration);
    try std.testing.expect(!summary.blocked_on_live_mmio);
}

test "phase11 dw_wdt platform registration scaffold keeps shared-clock fallback and reset release explicit" {
    const ready = platformRegistrationScaffoldSummary(.{
        .has_named_tclk = false,
        .has_shared_clock = true,
        .has_pclk = false,
        .has_reset_control = true,
        .has_pretimeout_irq = true,
        .drvdata_published = true,
        .timeout_programmed = true,
        .imported_running = false,
    });

    try std.testing.expectEqualStrings(anchor_path, ready.anchor);
    try std.testing.expectEqual(RegistrationScaffoldState.ready_to_register, ready.state);
    try std.testing.expectEqual(TimerClockPath.unnamed_shared_fallback, ready.timer_clock_path);
    try std.testing.expectEqual(ApbClockPath.optional_absent, ready.apb_clock_path);
    try std.testing.expectEqual(ProbeTimeoutOrigin.programmed_top_window, ready.probe_timeout_origin);
    try std.testing.expect(ready.registration_requested);
    try std.testing.expect(ready.stop_on_reboot_requested);
    try std.testing.expectEqual(default_restart_priority, ready.restart_priority_value);
    try std.testing.expect(ready.reset_release_ready);
    try std.testing.expectEqualStrings("reset_control_deassert", ready.reset_release_call);
    try std.testing.expect(ready.reset_release_requested);
    try std.testing.expect(ready.pretimeout_irq_optional);
    try std.testing.expect(ready.pretimeout_irq_present);
    try std.testing.expectEqualStrings("platform_get_irq_optional", ready.pretimeout_irq_call);
    try std.testing.expect(ready.blocked_on_live_platform_registration);
    try std.testing.expect(!ready.blocked_on_live_mmio);

    const blocked = platformRegistrationScaffoldSummary(.{
        .has_named_tclk = false,
        .has_shared_clock = false,
        .has_pclk = true,
        .has_reset_control = true,
        .has_pretimeout_irq = true,
        .drvdata_published = true,
        .timeout_programmed = true,
        .imported_running = false,
    });

    try std.testing.expectEqual(RegistrationScaffoldState.blocked_missing_timer_clock, blocked.state);
    try std.testing.expectEqual(TimerClockPath.blocked_no_timer_clock, blocked.timer_clock_path);
    try std.testing.expectEqual(ApbClockPath.optional_present, blocked.apb_clock_path);
    try std.testing.expectEqual(ProbeTimeoutOrigin.blocked_missing_timer_clock, blocked.probe_timeout_origin);
    try std.testing.expect(!blocked.registration_requested);
    try std.testing.expect(!blocked.stop_on_reboot_requested);
    try std.testing.expect(blocked.pretimeout_irq_optional);
    try std.testing.expect(blocked.pretimeout_irq_present);
    try std.testing.expectEqualStrings("platform_get_irq_optional", blocked.pretimeout_irq_call);
    try std.testing.expect(!blocked.reset_release_requested);
    try std.testing.expect(blocked.blocked_on_live_platform_registration);
    try std.testing.expect(!blocked.blocked_on_live_mmio);
}

test "phase11 dw_wdt teardown summary keeps idle, stoppable, and unstoppable paths distinct" {
    var idle = try DwWdtLab.initFixedTops(7, true);
    try idle.setInterruptPending(true);
    const idle_summary = try idle.teardownSummary();
    try std.testing.expectEqual(TeardownOutcome.idle_noop, idle_summary.outcome);
    try std.testing.expect(!idle_summary.can_stop);
    try std.testing.expect(!idle_summary.running_before_teardown);
    try std.testing.expect(!idle_summary.stop_invoked);
    try std.testing.expect(!idle_summary.enable_bit_cleared);
    try std.testing.expect(idle_summary.interrupt_cleared);
    try std.testing.expect(!idle_summary.running_after_teardown);
    try std.testing.expect(!idle_summary.hardware_running_after_teardown);

    var unstoppable = try DwWdtLab.initFixedTops(7, false);
    _ = try unstoppable.start();
    try unstoppable.setInterruptPending(true);
    const unstoppable_summary = try unstoppable.teardownSummary();
    try std.testing.expectEqual(TeardownOutcome.continued_heartbeat, unstoppable_summary.outcome);
    try std.testing.expect(!unstoppable_summary.can_stop);
    try std.testing.expect(unstoppable_summary.running_before_teardown);
    try std.testing.expect(unstoppable_summary.stop_invoked);
    try std.testing.expect(!unstoppable_summary.enable_bit_cleared);
    try std.testing.expect(unstoppable_summary.interrupt_cleared);
    try std.testing.expect(unstoppable_summary.running_after_teardown);
    try std.testing.expect(!unstoppable_summary.hardware_running_after_teardown);

    var stoppable = try DwWdtLab.initFixedTops(7, true);
    _ = try stoppable.start();
    try stoppable.setInterruptPending(true);
    const stoppable_summary = try stoppable.teardownSummary();
    try std.testing.expectEqual(TeardownOutcome.reset_control_stop, stoppable_summary.outcome);
    try std.testing.expect(stoppable_summary.can_stop);
    try std.testing.expect(stoppable_summary.running_before_teardown);
    try std.testing.expect(stoppable_summary.stop_invoked);
    try std.testing.expect(stoppable_summary.enable_bit_cleared);
    try std.testing.expect(stoppable_summary.interrupt_cleared);
    try std.testing.expect(!stoppable_summary.running_after_teardown);
    try std.testing.expect(!stoppable_summary.hardware_running_after_teardown);
}

test "phase11 dw_wdt remove summary clears interrupts while distinguishing reset-backed shutdown" {
    var unstoppable = try DwWdtLab.initFixedTops(7, false);
    _ = try unstoppable.start();
    try unstoppable.setInterruptPending(true);
    const unstoppable_summary = unstoppable.removeSummary();

    try std.testing.expectEqualStrings(anchor_path, unstoppable_summary.anchor);
    try std.testing.expect(unstoppable_summary.debugfs_clear_requested);
    try std.testing.expect(unstoppable_summary.unregister_device_requested);
    try std.testing.expect(!unstoppable_summary.reset_control_available);
    try std.testing.expect(!unstoppable_summary.reset_assert_requested);
    try std.testing.expect(unstoppable_summary.hardware_running_before_remove);
    try std.testing.expect(unstoppable_summary.hardware_running_after_remove);
    try std.testing.expect(unstoppable_summary.running_after_remove);
    try std.testing.expect(!unstoppable_summary.interrupt_pending_after_remove);
    try std.testing.expect(unstoppable_summary.remove_leaves_hardware_running);

    var stoppable = try DwWdtLab.initFixedTops(7, true);
    _ = try stoppable.start();
    try stoppable.setInterruptPending(true);
    const stoppable_summary = stoppable.removeSummary();

    try std.testing.expect(stoppable_summary.reset_control_available);
    try std.testing.expect(stoppable_summary.reset_assert_requested);
    try std.testing.expect(stoppable_summary.hardware_running_before_remove);
    try std.testing.expect(!stoppable_summary.hardware_running_after_remove);
    try std.testing.expect(!stoppable_summary.running_after_remove);
    try std.testing.expect(!stoppable_summary.interrupt_pending_after_remove);
    try std.testing.expect(!stoppable_summary.remove_leaves_hardware_running);
}

test "phase11 dw_wdt remove summary keeps idle removal distinct from reset-backed shutdown" {
    var idle = try DwWdtLab.initFixedTops(7, true);
    try idle.setInterruptPending(true);
    const summary = idle.removeSummary();

    try std.testing.expectEqualStrings(anchor_path, summary.anchor);
    try std.testing.expect(summary.debugfs_clear_requested);
    try std.testing.expect(summary.unregister_device_requested);
    try std.testing.expect(summary.reset_control_available);
    try std.testing.expect(!summary.reset_assert_requested);
    try std.testing.expect(!summary.hardware_running_before_remove);
    try std.testing.expect(!summary.hardware_running_after_remove);
    try std.testing.expect(!summary.running_after_remove);
    try std.testing.expect(!summary.interrupt_pending_after_remove);
    try std.testing.expect(!summary.remove_leaves_hardware_running);
}
