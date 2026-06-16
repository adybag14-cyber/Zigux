const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE11_DW_WDT_PM_HELPER_PACKET_SELF_TEST=pass";

const PM_WHY_NOW = [_][]const u8{
    "The bounded PM helper now keeps suspend, resume, and shutdown handoff reviewable across missing-drvdata blocks, running-hardware suspend stop intent with stop-on-reboot unregister and restart-priority clear, idle suspend without teardown hooks, imported-running resume recovery plus stop-on-reboot and restart-priority restore, idle restore hooks, timeout-reprogram blocks, running shutdown stop intent with pretimeout-mask teardown, and idle shutdown cleanup before live MMIO-backed PM work lands.",
};

const SURVEY_MARKERS = [_][]const u8{
    "`drivers/watchdog/dw_wdt_restart.zig`, `drivers/watchdog/dw_wdt_pm.zig`,",
    "`drivers/watchdog/dw_wdt_pm_scaffold.zig`,",
    "the bounded PM-helper pair reviewable",
    "hardware-backed MMIO validation around",
    "suspend, resume, and platform-backed probe or remove execution",
};

const MATRIX_MARKERS = [_][]const u8{
    "`drivers/watchdog/dw_wdt_pm.zig` keeps the bounded PM-helper handoff",
    "hardware-backed MMIO validation around suspend, resume, and",
};

const PLAN_MARKERS = [_][]const u8{
    "- the bounded PM helper pair `drivers/watchdog/dw_wdt_pm.zig` and `drivers/watchdog/dw_wdt_pm_scaffold.zig`",
    "- suspend or resume behavior beyond the already-readable PM helper summaries",
};

const PM_MARKERS = [_][]const u8{
    "pub const anchor_path = \"drivers/watchdog/dw_wdt.c\";",
    "test \"phase11 dw_wdt pm suspend keeps missing drvdata explicit\" {",
    "try std.testing.expectEqual(PmSuspendState.blocked_missing_drvdata, summary.state);",
    "test \"phase11 dw_wdt pm suspend keeps running-hardware stop handoff explicit\" {",
    "try std.testing.expectEqual(PmSuspendState.running_suspend_requires_stop, summary.state);",
    "test \"phase11 dw_wdt pm resume keeps imported-running handoff explicit\" {",
    "PmResumeState.import_running_state_then_restore_hooks,",
    "test \"phase11 dw_wdt pm resume keeps timeout reprogram block explicit before idle restore\" {",
    "PmResumeState.blocked_live_mmio_timeout_reprogram,",
    "test \"phase11 dw_wdt pm shutdown keeps running pretimeout mask explicit\" {",
    "try std.testing.expect(summary.pretimeout_mask_requested);",
};

const PM_SCAFFOLD_MARKERS = [_][]const u8{
    "pub const anchor_path = \"drivers/watchdog/dw_wdt.c\";",
    "test \"phase11 dw_wdt pm scaffold keeps idle suspend and resume explicit\" {",
    "try std.testing.expectEqual(SuspendDisposition.idle_noop, suspend_report.disposition);",
    "test \"phase11 dw_wdt pm scaffold quiesces a stoppable watchdog before suspend\" {",
    "try std.testing.expectEqual(SuspendDisposition.quiesce_before_suspend, suspend_report.disposition);",
    "test \"phase11 dw_wdt pm scaffold keeps no-way-out hardware running across suspend and resume\" {",
    "try std.testing.expectEqual(ResumeDisposition.keep_running_without_restore, resume_report.disposition);",
    "test \"phase11 dw_wdt pm scaffold keeps live-mmio blocker explicit for running hardware\" {",
    "try std.testing.expectEqual(ResumeDisposition.blocked_on_live_mmio, resume_report.disposition);",
};

const PM_BUILD_MARKERS = [_][]const u8{
    ".root_source_file = b.path(\"../../drivers/watchdog/dw_wdt_pm.zig\"),",
    ".root_source_file = b.path(\"../../drivers/watchdog/dw_wdt_pm_scaffold.zig\"),",
    ".name = \"phase11-dw-wdt-pm-tests\",",
    ".name = \"phase11-dw-wdt-pm-scaffold-tests\",",
    "const test_step = b.step(",
    "\"Run the focused Phase 11 DesignWare watchdog PM helper pair replay\"",
    "\"phase11-dw-wdt-pm-test\"",
};

const VALIDATE_MARKERS = [_][]const u8{
    "\"scripts/zigux/check_phase11_dw_wdt_pm_helper_packet.zig\",",
    "\"phase11-dw-wdt-pm-helper-packet-self-test\",",
    "(\"zig\", \"run\", \"scripts/zigux/check_phase11_dw_wdt_pm_helper_packet.zig\", \"--\", \"--self-test\")",
    "\"phase11-dw-wdt-pm-helper-packet\",",
    "(\"zig\", \"run\", \"scripts/zigux/check_phase11_dw_wdt_pm_helper_packet.zig\", \"--\")",
    "(\"zig\", \"build\", \"test\", \"--build-file\", \"zigux/tests/phase11_dw_wdt_pm_build.zig\")",
};

const FIXTURE_CHECK_NAMES = [_][]const u8{
    "phase11-dw-wdt-pm-helper-packet-self-test",
    "phase11-dw-wdt-pm-helper-packet",
};

const EXPECTED_SURVEYED_COMMIT = [_][]const u8{
    "75f8336c4305beed127d7abfae37d3999b7cc57c",
};

const PM_GAP_ID = [_][]const u8{
    "phase11-dw-wdt-live-platform-pm",
};

const PM_DESTINATION = [_][]const u8{
    "drivers/watchdog/dw_wdt_pm.zig",
};

const NEXT_GAP_ID = [_][]const u8{
    "phase11-dw-wdt-live-mmio-validation",
};

const NEXT_DESTINATION = [_][]const u8{
    "zigux/tests/phase11_dw_wdt.zig",
};

pub fn checkText(text: []const u8) guard.GuardError!void {
    for (PM_WHY_NOW) |marker| try guard.requireMarker(text, marker);
    for (SURVEY_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (MATRIX_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (PLAN_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (PM_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (PM_SCAFFOLD_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (PM_BUILD_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (VALIDATE_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (FIXTURE_CHECK_NAMES) |marker| try guard.requireMarker(text, marker);
    for (EXPECTED_SURVEYED_COMMIT) |marker| try guard.requireMarker(text, marker);
    for (PM_GAP_ID) |marker| try guard.requireMarker(text, marker);
    for (PM_DESTINATION) |marker| try guard.requireMarker(text, marker);
    for (NEXT_GAP_ID) |marker| try guard.requireMarker(text, marker);
    for (NEXT_DESTINATION) |marker| try guard.requireMarker(text, marker);
}

pub fn main() !void {
    var gpa = std.heap.GeneralPurposeAllocator(.{}){};
    defer _ = gpa.deinit();
    const allocator = gpa.allocator();
    const io = std.Io.Threaded.init(allocator, .{});
    defer io.deinit();
    const args = try std.process.argsAlloc(allocator);
    defer std.process.argsFree(allocator, args);

    var self_test = false;
    for (args[1..]) |arg| {
        if (std.mem.eql(u8, arg, "--self-test")) self_test = true;
    }

    if (self_test) {
        try checkText("");
        try guard.printLine(io, "{s}", .{pass_marker});
        return;
    }

    const root = try guard.repoRootFromScript(allocator);
    defer allocator.free(root);
    const workflow_rel = ".github/workflows/zigux-bootstrap.yml";
    const workflow_path = try std.fmt.allocPrint(allocator, "{s}/{s}", .{ root, workflow_rel });
    defer allocator.free(workflow_path);
    const text = try guard.readUtf8File(io, allocator, workflow_path);
    defer allocator.free(text);
    try checkText(text);
    try guard.printLine(io, "{s}", .{pass_marker});
}
