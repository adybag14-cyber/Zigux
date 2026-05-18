const std = @import("std");

pub const anchor_path = "drivers/watchdog/dw_wdt.c";

pub const SuspendDisposition = enum {
    idle_noop,
    quiesce_before_suspend,
    keep_running_across_suspend,
    blocked_on_live_mmio,
};

pub const ResumeDisposition = enum {
    idle_noop,
    restore_then_restart,
    keep_running_without_restore,
    blocked_on_live_mmio,
};

pub const PmTransitionRequest = struct {
    watchdog_running: bool,
    nowayout: bool,
    reset_control_available: bool,
    state_snapshot_available: bool,
    mmio_window_available: bool,
    pretimeout_irq_present: bool,
};

pub const SuspendSummary = struct {
    anchor: []const u8,
    disposition: SuspendDisposition,
    suspend_requested: bool,
    stop_requested: bool,
    reset_assert_requested: bool,
    register_snapshot_requested: bool,
    pretimeout_mask_requested: bool,
    enters_low_power_ready_state: bool,
    keeps_hardware_running: bool,
    blocked_on_live_mmio: bool,
};

pub const ResumeSummary = struct {
    anchor: []const u8,
    disposition: ResumeDisposition,
    resume_requested: bool,
    clock_enable_requested: bool,
    register_restore_requested: bool,
    restart_requested: bool,
    pretimeout_restore_requested: bool,
    returns_watchdog_to_running_state: bool,
    blocked_on_live_mmio: bool,
    preserves_running_hardware_without_restore: bool,
};

pub fn suspendSummary(request: PmTransitionRequest) SuspendSummary {
    const blocked_on_live_mmio = request.watchdog_running and !request.mmio_window_available;
    const keep_running = request.watchdog_running and request.nowayout and !request.reset_control_available;
    const can_quiesce = request.watchdog_running and !keep_running and request.mmio_window_available;

    return .{
        .anchor = anchor_path,
        .disposition = if (!request.watchdog_running)
            .idle_noop
        else if (blocked_on_live_mmio)
            .blocked_on_live_mmio
        else if (keep_running)
            .keep_running_across_suspend
        else
            .quiesce_before_suspend,
        .suspend_requested = true,
        .stop_requested = can_quiesce,
        .reset_assert_requested = can_quiesce and request.reset_control_available,
        .register_snapshot_requested = request.watchdog_running and request.mmio_window_available and request.state_snapshot_available,
        .pretimeout_mask_requested = request.watchdog_running and request.pretimeout_irq_present,
        .enters_low_power_ready_state = !request.watchdog_running or can_quiesce or keep_running,
        .keeps_hardware_running = keep_running,
        .blocked_on_live_mmio = blocked_on_live_mmio,
    };
}

pub fn resumeSummary(request: PmTransitionRequest) ResumeSummary {
    const blocked_on_live_mmio = request.watchdog_running and !request.mmio_window_available;
    const keep_running = request.watchdog_running and request.nowayout and !request.reset_control_available;
    const can_restore = request.watchdog_running and request.mmio_window_available and request.state_snapshot_available and !keep_running;

    return .{
        .anchor = anchor_path,
        .disposition = if (!request.watchdog_running)
            .idle_noop
        else if (blocked_on_live_mmio)
            .blocked_on_live_mmio
        else if (keep_running)
            .keep_running_without_restore
        else
            .restore_then_restart,
        .resume_requested = true,
        .clock_enable_requested = request.watchdog_running,
        .register_restore_requested = can_restore,
        .restart_requested = can_restore,
        .pretimeout_restore_requested = can_restore and request.pretimeout_irq_present,
        .returns_watchdog_to_running_state = keep_running or can_restore,
        .blocked_on_live_mmio = blocked_on_live_mmio,
        .preserves_running_hardware_without_restore = keep_running,
    };
}

test "phase11 dw_wdt pm scaffold quiesces a stoppable watchdog before suspend" {
    const request = PmTransitionRequest{
        .watchdog_running = true,
        .nowayout = false,
        .reset_control_available = true,
        .state_snapshot_available = true,
        .mmio_window_available = true,
        .pretimeout_irq_present = true,
    };

    const suspend_report = suspendSummary(request);
    try std.testing.expectEqualStrings(anchor_path, suspend_report.anchor);
    try std.testing.expectEqual(SuspendDisposition.quiesce_before_suspend, suspend_report.disposition);
    try std.testing.expect(suspend_report.stop_requested);
    try std.testing.expect(suspend_report.reset_assert_requested);
    try std.testing.expect(suspend_report.register_snapshot_requested);
    try std.testing.expect(suspend_report.pretimeout_mask_requested);
    try std.testing.expect(suspend_report.enters_low_power_ready_state);
    try std.testing.expect(!suspend_report.keeps_hardware_running);
    try std.testing.expect(!suspend_report.blocked_on_live_mmio);

    const resume_report = resumeSummary(request);
    try std.testing.expectEqualStrings(anchor_path, resume_report.anchor);
    try std.testing.expectEqual(ResumeDisposition.restore_then_restart, resume_report.disposition);
    try std.testing.expect(resume_report.clock_enable_requested);
    try std.testing.expect(resume_report.register_restore_requested);
    try std.testing.expect(resume_report.restart_requested);
    try std.testing.expect(resume_report.pretimeout_restore_requested);
    try std.testing.expect(resume_report.returns_watchdog_to_running_state);
    try std.testing.expect(!resume_report.blocked_on_live_mmio);
    try std.testing.expect(!resume_report.preserves_running_hardware_without_restore);
}

test "phase11 dw_wdt pm scaffold keeps no-way-out hardware running across suspend and resume" {
    const request = PmTransitionRequest{
        .watchdog_running = true,
        .nowayout = true,
        .reset_control_available = false,
        .state_snapshot_available = false,
        .mmio_window_available = true,
        .pretimeout_irq_present = false,
    };

    const suspend_report = suspendSummary(request);
    try std.testing.expectEqual(SuspendDisposition.keep_running_across_suspend, suspend_report.disposition);
    try std.testing.expect(!suspend_report.stop_requested);
    try std.testing.expect(!suspend_report.reset_assert_requested);
    try std.testing.expect(!suspend_report.register_snapshot_requested);
    try std.testing.expect(!suspend_report.pretimeout_mask_requested);
    try std.testing.expect(suspend_report.enters_low_power_ready_state);
    try std.testing.expect(suspend_report.keeps_hardware_running);
    try std.testing.expect(!suspend_report.blocked_on_live_mmio);

    const resume_report = resumeSummary(request);
    try std.testing.expectEqual(ResumeDisposition.keep_running_without_restore, resume_report.disposition);
    try std.testing.expect(resume_report.clock_enable_requested);
    try std.testing.expect(!resume_report.register_restore_requested);
    try std.testing.expect(!resume_report.restart_requested);
    try std.testing.expect(!resume_report.pretimeout_restore_requested);
    try std.testing.expect(resume_report.returns_watchdog_to_running_state);
    try std.testing.expect(!resume_report.blocked_on_live_mmio);
    try std.testing.expect(resume_report.preserves_running_hardware_without_restore);
}

test "phase11 dw_wdt pm scaffold keeps live-mmio blocker explicit for running hardware" {
    const request = PmTransitionRequest{
        .watchdog_running = true,
        .nowayout = false,
        .reset_control_available = true,
        .state_snapshot_available = false,
        .mmio_window_available = false,
        .pretimeout_irq_present = true,
    };

    const suspend_report = suspendSummary(request);
    try std.testing.expectEqual(SuspendDisposition.blocked_on_live_mmio, suspend_report.disposition);
    try std.testing.expect(!suspend_report.stop_requested);
    try std.testing.expect(!suspend_report.reset_assert_requested);
    try std.testing.expect(!suspend_report.register_snapshot_requested);
    try std.testing.expect(suspend_report.pretimeout_mask_requested);
    try std.testing.expect(!suspend_report.keeps_hardware_running);
    try std.testing.expect(suspend_report.blocked_on_live_mmio);

    const resume_report = resumeSummary(request);
    try std.testing.expectEqual(ResumeDisposition.blocked_on_live_mmio, resume_report.disposition);
    try std.testing.expect(resume_report.clock_enable_requested);
    try std.testing.expect(!resume_report.register_restore_requested);
    try std.testing.expect(!resume_report.restart_requested);
    try std.testing.expect(!resume_report.pretimeout_restore_requested);
    try std.testing.expect(!resume_report.returns_watchdog_to_running_state);
    try std.testing.expect(resume_report.blocked_on_live_mmio);
    try std.testing.expect(!resume_report.preserves_running_hardware_without_restore);
}
