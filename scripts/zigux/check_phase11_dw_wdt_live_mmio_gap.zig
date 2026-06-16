const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE11_DW_WDT_LIVE_MMIO_GAP_SELF_TEST=pass";

const NEXT_WHY_NOW = [_][]const u8{
    "With the PM handoff helper, direct restart summary, and returned verify helper parked in-tree, the next real gap is hardware-backed MMIO validation around suspend, resume, and platform-backed probe or remove execution, still without widening into unrelated driver behavior.",
};

const MATRIX_MARKERS = [_][]const u8{
    "- `PHASE11_DW_WDT_STATUS=hardware_validation_matrix_landed`",
    "- active watchdog continuity for this matrix and its coupled survey packet is",
    "- `zigux/tests/phase11_dw_wdt_manifest.json` and",
    "- `zigux/tests/phase11_dw_wdt_registration_scaffold.zig` keeps timer-clock",
    "- `drivers/watchdog/dw_wdt.zig` now rematerializes on current `master` and",
    "- The next bounded same-lane follow-up remains the manifest-marked ready-next",
    "hardware-backed MMIO validation around suspend, resume, and",
};

const SURVEY_MARKERS = [_][]const u8{
    "The current lane-local packet is `P11-L10`.",
    "`Documentation/zigux/phase11-dw-wdt-validation-matrix.md`,",
    "`drivers/watchdog/dw_wdt.zig`, `zigux/tests/phase11_dw_wdt.zig`,",
    "`zigux/tests/phase11_dw_wdt_registration_scaffold.zig`,",
    "`drivers/watchdog/dw_wdt_restart.zig`, `drivers/watchdog/dw_wdt_pm.zig`,",
    "The next bounded same-lane step is still the ready-next manifest gap:",
};

const PLATFORM_PLAN_MARKERS = [_][]const u8{
    "The preferred next packet is:",
    "keep timer-clock acquisition and optional APB clock acquisition explicit as outcome-bearing scaffold steps",
    "keep reset-control availability and reset-release intent explicit as outcome-bearing scaffold steps while preserving the already-readable ready-to-register branch when reset control is absent",
    "leave imported-running-state handoff reviewable inside the scaffold without widening into live platform registration, MMIO execution, or survey-only overclaiming",
};

const REGISTRATION_SCAFFOLD_MARKERS = [_][]const u8{
    "test \"platform registration scaffold summary keeps blocked timeout-programming branch explicit\" {",
    "dw_wdt.RegistrationScaffoldState.blocked_on_live_mmio,",
    "dw_wdt.ProbeTimeoutOrigin.blocked_on_live_mmio,",
    "test \"platform registration scaffold summary keeps optional reset-control absence explicit\" {",
    "dw_wdt.RegistrationScaffoldState.ready_to_register,",
};

const DRIVER_MARKERS = [_][]const u8{
    "pub const ProbeTimeoutOrigin = enum {",
    "blocked_on_live_mmio,",
    "pub const RegistrationScaffoldState = enum {",
    "pub fn platformHandoffSummary(request: PlatformHandoffRequest) PlatformHandoffSummary {",
    "const blocked_on_live_mmio = !missing_timer_clock and",
    "elsen            .blocked_on_live_mmio,",
    "test \"dw_wdt registration scaffold keeps optional reset absence ready when timeout image is already programmed\" {",
};

const PM_MARKERS = [_][]const u8{
    "test \"phase11 dw_wdt pm resume keeps timeout reprogram block explicit before idle restore\" {",
    "PmResumeState.blocked_live_mmio_timeout_reprogram,",
    "test \"phase11 dw_wdt pm shutdown keeps running teardown stop and hook removal explicit\" {",
    "test \"phase11 dw_wdt pm shutdown keeps running pretimeout mask explicit\" {",
};

const FILES = [_][]const u8{
    "matrix",
    "Documentation/zigux/phase11-dw-wdt-validation-matrix.md",
    "survey",
    "Documentation/zigux/phase11-dw-wdt-survey.md",
    "platform_plan",
    "Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md",
    "manifest",
    "zigux/tests/phase11_dw_wdt_manifest.json",
    "registration_scaffold",
    "zigux/tests/phase11_dw_wdt_registration_scaffold.zig",
    "driver",
    "drivers/watchdog/dw_wdt.zig",
    "pm",
    "drivers/watchdog/dw_wdt_pm.zig",
};

const MARKERS = [_][]const u8{
    "matrix",
    "survey",
    "platform_plan",
    "registration_scaffold",
    "driver",
    "pm",
};

const EXPECTED_PIN = [_][]const u8{
    "75f8336c4305beed127d7abfae37d3999b7cc57c",
};

const NEXT_GAP_ID = [_][]const u8{
    "phase11-dw-wdt-live-mmio-validation",
};

const NEXT_DESTINATION = [_][]const u8{
    "zigux/tests/phase11_dw_wdt.zig",
};

pub fn checkText(text: []const u8) guard.GuardError!void {
    for (NEXT_WHY_NOW) |marker| try guard.requireMarker(text, marker);
    for (MATRIX_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (SURVEY_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (PLATFORM_PLAN_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (REGISTRATION_SCAFFOLD_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (DRIVER_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (PM_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (FILES) |marker| try guard.requireMarker(text, marker);
    for (MARKERS) |marker| try guard.requireMarker(text, marker);
    for (EXPECTED_PIN) |marker| try guard.requireMarker(text, marker);
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
