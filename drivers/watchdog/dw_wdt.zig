const std = @import("std");

pub const anchor_path = "drivers/watchdog/dw_wdt.c";
pub const default_restart_priority: u32 = 128;

pub const TimerClockSelection = enum {
    named_tclk,
    unnamed_shared_fallback,
    blocked_no_timer_clock,
};

pub const ApbClockSelection = enum {
    optional_present,
    optional_absent,
};

pub const TimerClockPath = enum {
    named_tclk,
    unnamed_shared_fallback,
    blocked_missing_timer_clock,
};

pub const ApbClockPath = enum {
    optional_present,
    optional_absent,
};

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

pub const ProbeFailureStage = enum {
    missing_timer_clock,
    timeout_programming,
    import_running_state,
    register_device,
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
    apb_clock_path: ApbClockPath,
    probe_timeout_origin: ProbeTimeoutOrigin,
    timer_clock_available: bool,
    apb_clock_optional: bool,
    apb_clock_present: bool,
    reset_control_available: bool,
    pretimeout_irq_optional: bool,
    pretimeout_irq_present: bool,
    pretimeout_irq_call: []const u8,
    timeout_programming_requested: bool,
    imported_running_state: bool,
    reset_release_requested: bool,
    stop_on_reboot_requested: bool,
    restart_priority_value: u32,
    registration_ready: bool,
    blocked_on_live_platform_registration: bool,
    blocked_on_live_mmio: bool,
};

pub const PlatformRegistrationScaffoldSummary = struct {
    anchor: []const u8,
    state: RegistrationScaffoldState,
    timer_clock_path: TimerClockPath,
    apb_clock_path: ApbClockPath,
    probe_timeout_origin: ProbeTimeoutOrigin,
    registration_requested: bool,
    stop_on_reboot_requested: bool,
    restart_priority_value: u32,
    apb_clock_optional: bool,
    apb_clock_present: bool,
    apb_clock_get_call: []const u8,
    reset_release_ready: bool,
    reset_release_call: []const u8,
    reset_release_requested: bool,
    pretimeout_irq_optional: bool,
    pretimeout_irq_present: bool,
    pretimeout_irq_call: []const u8,
    blocked_on_live_platform_registration: bool,
    blocked_on_live_mmio: bool,
};

pub const RegistrationOrderRequest = struct {
    drvdata_published: bool,
    timeout_programmed: bool,
    imported_running: bool,
};

pub const RegistrationOrderSummary = struct {
    state: RegistrationScaffoldState,
    publishes_drvdata_before_register: bool,
    imports_running_state_before_register: bool,
    programs_timeout_before_register: bool,
    registration_requested: bool,
    stop_on_reboot_requested: bool,
    restart_priority_value: u32,
    register_call: []const u8,
    blocked_on_live_platform_registration: bool,
    blocked_on_live_mmio: bool,
};

pub const ProbeFailureCleanupRequest = struct {
    has_named_tclk: bool,
    has_shared_clock: bool,
    has_pclk: bool,
    has_reset_control: bool,
    has_pretimeout_irq: bool,
    drvdata_published: bool,
    timeout_programmed: bool,
    imported_running: bool,
    failure_stage: ProbeFailureStage,
};

pub const ProbeFailureCleanupSummary = struct {
    anchor: []const u8,
    failure_stage: ProbeFailureStage,
    state: RegistrationScaffoldState,
    timer_clock_path: TimerClockPath,
    apb_clock_path: ApbClockPath,
    probe_timeout_origin: ProbeTimeoutOrigin,
    registration_requested: bool,
    drvdata_cleanup_reviewable: bool,
    timeout_cleanup_reviewable: bool,
    pretimeout_irq_release_reviewable: bool,
    reset_assert_requested: bool,
    timer_clock_disable_requested: bool,
    apb_clock_disable_requested: bool,
    blocked_on_live_mmio_cleanup: bool,
    blocked_on_live_platform_cleanup: bool,
};

pub const RemoveTeardownRequest = struct {
    has_named_tclk: bool,
    has_shared_clock: bool,
    has_pclk: bool,
    has_reset_control: bool,
    has_pretimeout_irq: bool,
    drvdata_published: bool,
    timeout_programmed: bool,
    imported_running: bool,
    nowayout: bool,
    restart_handler_registered: bool,
};

pub const RemoveTeardownSummary = struct {
    anchor: []const u8,
    state: RegistrationScaffoldState,
    timer_clock_path: TimerClockPath,
    apb_clock_path: ApbClockPath,
    running_state_visible: bool,
    watchdog_stop_requested: bool,
    restart_handler_unregistered: bool,
    pretimeout_irq_release_reviewable: bool,
    reset_assert_requested: bool,
    timer_clock_disable_requested: bool,
    apb_clock_disable_requested: bool,
    blocked_on_live_mmio_stop: bool,
    blocked_on_live_remove_callback: bool,
};

fn selectTimerClockPath(has_named_tclk: bool, has_shared_clock: bool) TimerClockPath {
    if (has_named_tclk) return .named_tclk;
    if (has_shared_clock) return .unnamed_shared_fallback;
    return .blocked_missing_timer_clock;
}

fn selectApbClockPath(has_pclk: bool) ApbClockPath {
    return if (has_pclk) .optional_present else .optional_absent;
}

pub fn platformResourcePreflightSummary(
    request: PlatformResourcePreflightRequest,
) PlatformResourcePreflightSummary {
    const timer_clock_selection: TimerClockSelection = if (request.has_named_tclk)
        .named_tclk
    else if (request.has_shared_clock)
        .unnamed_shared_fallback
    else
        .blocked_no_timer_clock;

    return .{
        .anchor = anchor_path,
        .timer_clock_selection = timer_clock_selection,
        .uses_shared_clock_fallback = !request.has_named_tclk and request.has_shared_clock,
        .timer_clock_available = request.has_named_tclk or request.has_shared_clock,
        .timer_clock_get_call = "devm_clk_get_enabled",
        .apb_clock_selection = if (request.has_pclk) .optional_present else .optional_absent,
        .apb_clock_optional = true,
        .apb_clock_present = request.has_pclk,
        .apb_clock_get_call = "devm_clk_get_optional_enabled",
        .reset_control_available = request.has_reset_control,
        .reset_control_get_call = "devm_reset_control_get_optional_shared",
        .pretimeout_irq_optional = true,
        .pretimeout_irq_present = request.has_pretimeout_irq,
        .pretimeout_irq_call = "platform_get_irq_optional",
        .blocked_on_missing_timer_clock = !request.has_named_tclk and !request.has_shared_clock,
        .keeps_platform_registration_blocked = true,
    };
}

pub fn platformHandoffSummary(request: PlatformHandoffRequest) PlatformHandoffSummary {
    const timer_clock_path = selectTimerClockPath(request.has_named_tclk, request.has_shared_clock);
    const apb_clock_path = selectApbClockPath(request.has_pclk);
    const missing_timer_clock = timer_clock_path == .blocked_missing_timer_clock;
    const blocked_on_live_mmio = !missing_timer_clock and
        request.drvdata_published and
        !request.imported_running and
        !request.timeout_programmed;

    const state: RegistrationScaffoldState = if (missing_timer_clock)
        .blocked_missing_timer_clock
    else if (!request.drvdata_published)
        .blocked_missing_drvdata
    else if (request.imported_running)
        .import_running_state_then_register
    else if (request.timeout_programmed)
        .ready_to_register
    else
        .blocked_on_live_mmio;

    return .{
        .anchor = anchor_path,
        .state = state,
        .timer_clock_path = timer_clock_path,
        .apb_clock_path = apb_clock_path,
        .probe_timeout_origin = if (missing_timer_clock)
            .blocked_missing_timer_clock
        else if (request.imported_running)
            .imported_running_counter
        else if (request.timeout_programmed)
            .programmed_top_window
        else
            .blocked_on_live_mmio,
        .timer_clock_available = !missing_timer_clock,
        .apb_clock_optional = true,
        .apb_clock_present = request.has_pclk,
        .reset_control_available = request.has_reset_control,
        .pretimeout_irq_optional = true,
        .pretimeout_irq_present = request.has_pretimeout_irq,
        .pretimeout_irq_call = "platform_get_irq_optional",
        .timeout_programming_requested = !missing_timer_clock and request.drvdata_published and !request.imported_running,
        .imported_running_state = request.imported_running,
        .reset_release_requested = request.has_reset_control and request.imported_running,
        .stop_on_reboot_requested = !missing_timer_clock and request.drvdata_published and (request.imported_running or request.timeout_programmed),
        .restart_priority_value = default_restart_priority,
        .registration_ready = state == .import_running_state_then_register or state == .ready_to_register,
        .blocked_on_live_platform_registration = true,
        .blocked_on_live_mmio = blocked_on_live_mmio,
    };
}

pub fn platformRegistrationScaffoldSummary(
    request: PlatformHandoffRequest,
) PlatformRegistrationScaffoldSummary {
    const handoff = platformHandoffSummary(request);
    return .{
        .anchor = handoff.anchor,
        .state = handoff.state,
        .timer_clock_path = handoff.timer_clock_path,
        .apb_clock_path = handoff.apb_clock_path,
        .probe_timeout_origin = handoff.probe_timeout_origin,
        .registration_requested = handoff.registration_ready,
        .stop_on_reboot_requested = handoff.registration_ready,
        .restart_priority_value = default_restart_priority,
        .apb_clock_optional = true,
        .apb_clock_present = request.has_pclk,
        .apb_clock_get_call = "devm_clk_get_optional_enabled",
        .reset_release_ready = request.has_reset_control,
        .reset_release_call = "reset_control_deassert",
        .reset_release_requested = request.has_reset_control and handoff.registration_ready,
        .pretimeout_irq_optional = true,
        .pretimeout_irq_present = request.has_pretimeout_irq,
        .pretimeout_irq_call = "platform_get_irq_optional",
        .blocked_on_live_platform_registration = true,
        .blocked_on_live_mmio = handoff.blocked_on_live_mmio,
    };
}

pub fn registrationOrderSummary(request: RegistrationOrderRequest) RegistrationOrderSummary {
    const state: RegistrationScaffoldState = if (!request.drvdata_published)
        .blocked_missing_drvdata
    else if (request.imported_running)
        .import_running_state_then_register
    else if (request.timeout_programmed)
        .ready_to_register
    else
        .blocked_on_live_mmio;

    const registration_requested = state == .import_running_state_then_register or
        state == .ready_to_register;

    return .{
        .state = state,
        .publishes_drvdata_before_register = request.drvdata_published,
        .imports_running_state_before_register = request.drvdata_published and request.imported_running,
        .programs_timeout_before_register = request.drvdata_published and request.timeout_programmed and !request.imported_running,
        .registration_requested = registration_requested,
        .stop_on_reboot_requested = registration_requested,
        .restart_priority_value = default_restart_priority,
        .register_call = "watchdog_register_device",
        .blocked_on_live_platform_registration = true,
        .blocked_on_live_mmio = state == .blocked_on_live_mmio,
    };
}

pub fn probeFailureCleanupSummary(
    request: ProbeFailureCleanupRequest,
) ProbeFailureCleanupSummary {
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
    const registration = registrationOrderSummary(.{
        .drvdata_published = request.drvdata_published,
        .timeout_programmed = request.timeout_programmed,
        .imported_running = request.imported_running,
    });

    return .{
        .anchor = anchor_path,
        .failure_stage = request.failure_stage,
        .state = handoff.state,
        .timer_clock_path = handoff.timer_clock_path,
        .apb_clock_path = handoff.apb_clock_path,
        .probe_timeout_origin = handoff.probe_timeout_origin,
        .registration_requested = request.failure_stage == .register_device and registration.registration_requested,
        .drvdata_cleanup_reviewable = request.drvdata_published,
        .timeout_cleanup_reviewable = request.timeout_programmed or request.imported_running,
        .pretimeout_irq_release_reviewable = request.has_pretimeout_irq and request.drvdata_published,
        .reset_assert_requested = request.has_reset_control and request.drvdata_published,
        .timer_clock_disable_requested = request.drvdata_published and handoff.timer_clock_available,
        .apb_clock_disable_requested = request.drvdata_published and request.has_pclk,
        .blocked_on_live_mmio_cleanup = handoff.blocked_on_live_mmio or
            request.failure_stage == .timeout_programming or
            request.failure_stage == .import_running_state,
        .blocked_on_live_platform_cleanup = true,
    };
}

pub fn removeTeardownSummary(request: RemoveTeardownRequest) RemoveTeardownSummary {
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

    return .{
        .anchor = anchor_path,
        .state = handoff.state,
        .timer_clock_path = handoff.timer_clock_path,
        .apb_clock_path = handoff.apb_clock_path,
        .running_state_visible = request.imported_running,
        .watchdog_stop_requested = handoff.registration_ready and !request.nowayout,
        .restart_handler_unregistered = request.restart_handler_registered and handoff.registration_ready,
        .pretimeout_irq_release_reviewable = request.has_pretimeout_irq and request.drvdata_published,
        .reset_assert_requested = request.has_reset_control and request.drvdata_published,
        .timer_clock_disable_requested = request.drvdata_published and handoff.timer_clock_available,
        .apb_clock_disable_requested = request.drvdata_published and request.has_pclk,
        .blocked_on_live_mmio_stop = handoff.registration_ready,
        .blocked_on_live_remove_callback = true,
    };
}

test "dw_wdt preflight keeps named and shared timer clock paths explicit" {
    const named = platformResourcePreflightSummary(.{
        .has_named_tclk = true,
        .has_shared_clock = false,
        .has_pclk = true,
        .has_reset_control = true,
        .has_pretimeout_irq = true,
    });
    try std.testing.expectEqualStrings(anchor_path, named.anchor);
    try std.testing.expectEqual(TimerClockSelection.named_tclk, named.timer_clock_selection);
    try std.testing.expect(named.timer_clock_available);
    try std.testing.expect(!named.uses_shared_clock_fallback);
    try std.testing.expectEqual(ApbClockSelection.optional_present, named.apb_clock_selection);
    try std.testing.expect(named.apb_clock_present);
    try std.testing.expect(named.reset_control_available);
    try std.testing.expect(named.pretimeout_irq_present);

    const shared = platformResourcePreflightSummary(.{
        .has_named_tclk = false,
        .has_shared_clock = true,
        .has_pclk = false,
        .has_reset_control = false,
        .has_pretimeout_irq = false,
    });
    try std.testing.expectEqual(
        TimerClockSelection.unnamed_shared_fallback,
        shared.timer_clock_selection,
    );
    try std.testing.expect(shared.timer_clock_available);
    try std.testing.expect(shared.uses_shared_clock_fallback);
    try std.testing.expectEqual(ApbClockSelection.optional_absent, shared.apb_clock_selection);
    try std.testing.expect(!shared.apb_clock_present);
}

test "dw_wdt preflight keeps missing timer clock blocked without inventing registration readiness" {
    const summary = platformResourcePreflightSummary(.{
        .has_named_tclk = false,
        .has_shared_clock = false,
        .has_pclk = false,
        .has_reset_control = true,
        .has_pretimeout_irq = false,
    });

    try std.testing.expectEqual(
        TimerClockSelection.blocked_no_timer_clock,
        summary.timer_clock_selection,
    );
    try std.testing.expect(!summary.timer_clock_available);
    try std.testing.expect(summary.blocked_on_missing_timer_clock);
    try std.testing.expect(summary.keeps_platform_registration_blocked);
}

test "dw_wdt registration scaffold keeps optional reset absence ready when timeout image is already programmed" {
    const summary = platformRegistrationScaffoldSummary(.{
        .has_named_tclk = true,
        .has_shared_clock = false,
        .has_pclk = true,
        .has_reset_control = false,
        .has_pretimeout_irq = true,
        .drvdata_published = true,
        .timeout_programmed = true,
        .imported_running = false,
    });

    try std.testing.expectEqual(RegistrationScaffoldState.ready_to_register, summary.state);
    try std.testing.expect(summary.registration_requested);
    try std.testing.expect(summary.stop_on_reboot_requested);
    try std.testing.expectEqual(default_restart_priority, summary.restart_priority_value);
    try std.testing.expect(!summary.reset_release_ready);
    try std.testing.expect(!summary.reset_release_requested);
    try std.testing.expect(summary.pretimeout_irq_present);
    try std.testing.expect(!summary.blocked_on_live_mmio);
}

test "dw_wdt registration order keeps imported running handoff distinct from timeout programming" {
    const summary = registrationOrderSummary(.{
        .drvdata_published = true,
        .timeout_programmed = false,
        .imported_running = true,
    });

    try std.testing.expectEqual(
        RegistrationScaffoldState.import_running_state_then_register,
        summary.state,
    );
    try std.testing.expect(summary.publishes_drvdata_before_register);
    try std.testing.expect(summary.imports_running_state_before_register);
    try std.testing.expect(!summary.programs_timeout_before_register);
    try std.testing.expect(summary.registration_requested);
    try std.testing.expect(summary.stop_on_reboot_requested);
    try std.testing.expectEqual(default_restart_priority, summary.restart_priority_value);
    try std.testing.expectEqualStrings("watchdog_register_device", summary.register_call);
    try std.testing.expect(!summary.blocked_on_live_mmio);
}

test "dw_wdt probe-failure cleanup keeps missing timer clock from claiming unwind work" {
    const summary = probeFailureCleanupSummary(.{
        .has_named_tclk = false,
        .has_shared_clock = false,
        .has_pclk = true,
        .has_reset_control = true,
        .has_pretimeout_irq = true,
        .drvdata_published = false,
        .timeout_programmed = false,
        .imported_running = false,
        .failure_stage = .missing_timer_clock,
    });

    try std.testing.expectEqualStrings(anchor_path, summary.anchor);
    try std.testing.expectEqual(ProbeFailureStage.missing_timer_clock, summary.failure_stage);
    try std.testing.expectEqual(RegistrationScaffoldState.blocked_missing_timer_clock, summary.state);
    try std.testing.expectEqual(TimerClockPath.blocked_missing_timer_clock, summary.timer_clock_path);
    try std.testing.expectEqual(ApbClockPath.optional_present, summary.apb_clock_path);
    try std.testing.expectEqual(ProbeTimeoutOrigin.blocked_missing_timer_clock, summary.probe_timeout_origin);
    try std.testing.expect(!summary.registration_requested);
    try std.testing.expect(!summary.drvdata_cleanup_reviewable);
    try std.testing.expect(!summary.timeout_cleanup_reviewable);
    try std.testing.expect(!summary.pretimeout_irq_release_reviewable);
    try std.testing.expect(!summary.reset_assert_requested);
    try std.testing.expect(!summary.timer_clock_disable_requested);
    try std.testing.expect(!summary.apb_clock_disable_requested);
    try std.testing.expect(!summary.blocked_on_live_mmio_cleanup);
    try std.testing.expect(summary.blocked_on_live_platform_cleanup);
}

test "dw_wdt probe-failure cleanup keeps post-drvdata mmio unwind reviewable" {
    const summary = probeFailureCleanupSummary(.{
        .has_named_tclk = true,
        .has_shared_clock = false,
        .has_pclk = true,
        .has_reset_control = true,
        .has_pretimeout_irq = true,
        .drvdata_published = true,
        .timeout_programmed = false,
        .imported_running = false,
        .failure_stage = .timeout_programming,
    });

    try std.testing.expectEqual(ProbeFailureStage.timeout_programming, summary.failure_stage);
    try std.testing.expectEqual(RegistrationScaffoldState.blocked_on_live_mmio, summary.state);
    try std.testing.expectEqual(TimerClockPath.named_tclk, summary.timer_clock_path);
    try std.testing.expectEqual(ApbClockPath.optional_present, summary.apb_clock_path);
    try std.testing.expectEqual(ProbeTimeoutOrigin.blocked_on_live_mmio, summary.probe_timeout_origin);
    try std.testing.expect(!summary.registration_requested);
    try std.testing.expect(summary.drvdata_cleanup_reviewable);
    try std.testing.expect(!summary.timeout_cleanup_reviewable);
    try std.testing.expect(summary.pretimeout_irq_release_reviewable);
    try std.testing.expect(summary.reset_assert_requested);
    try std.testing.expect(summary.timer_clock_disable_requested);
    try std.testing.expect(summary.apb_clock_disable_requested);
    try std.testing.expect(summary.blocked_on_live_mmio_cleanup);
    try std.testing.expect(summary.blocked_on_live_platform_cleanup);
}

test "dw_wdt remove teardown keeps imported-running unregister ownership reviewable" {
    const summary = removeTeardownSummary(.{
        .has_named_tclk = false,
        .has_shared_clock = true,
        .has_pclk = true,
        .has_reset_control = true,
        .has_pretimeout_irq = true,
        .drvdata_published = true,
        .timeout_programmed = false,
        .imported_running = true,
        .nowayout = false,
        .restart_handler_registered = true,
    });

    try std.testing.expectEqualStrings(anchor_path, summary.anchor);
    try std.testing.expectEqual(RegistrationScaffoldState.import_running_state_then_register, summary.state);
    try std.testing.expectEqual(TimerClockPath.unnamed_shared_fallback, summary.timer_clock_path);
    try std.testing.expectEqual(ApbClockPath.optional_present, summary.apb_clock_path);
    try std.testing.expect(summary.running_state_visible);
    try std.testing.expect(summary.watchdog_stop_requested);
    try std.testing.expect(summary.restart_handler_unregistered);
    try std.testing.expect(summary.pretimeout_irq_release_reviewable);
    try std.testing.expect(summary.reset_assert_requested);
    try std.testing.expect(summary.timer_clock_disable_requested);
    try std.testing.expect(summary.apb_clock_disable_requested);
    try std.testing.expect(summary.blocked_on_live_mmio_stop);
    try std.testing.expect(summary.blocked_on_live_remove_callback);
}

test "dw_wdt remove teardown keeps nowayout from claiming a stop call" {
    const summary = removeTeardownSummary(.{
        .has_named_tclk = true,
        .has_shared_clock = false,
        .has_pclk = false,
        .has_reset_control = false,
        .has_pretimeout_irq = false,
        .drvdata_published = true,
        .timeout_programmed = true,
        .imported_running = false,
        .nowayout = true,
        .restart_handler_registered = true,
    });

    try std.testing.expectEqual(RegistrationScaffoldState.ready_to_register, summary.state);
    try std.testing.expectEqual(TimerClockPath.named_tclk, summary.timer_clock_path);
    try std.testing.expectEqual(ApbClockPath.optional_absent, summary.apb_clock_path);
    try std.testing.expect(!summary.running_state_visible);
    try std.testing.expect(!summary.watchdog_stop_requested);
    try std.testing.expect(summary.restart_handler_unregistered);
    try std.testing.expect(!summary.pretimeout_irq_release_reviewable);
    try std.testing.expect(!summary.reset_assert_requested);
    try std.testing.expect(summary.timer_clock_disable_requested);
    try std.testing.expect(!summary.apb_clock_disable_requested);
    try std.testing.expect(summary.blocked_on_live_mmio_stop);
    try std.testing.expect(summary.blocked_on_live_remove_callback);
}
