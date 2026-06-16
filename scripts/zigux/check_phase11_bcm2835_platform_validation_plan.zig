const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE11_BCM2835_PLATFORM_PLAN_SELF_TEST=pass";

const PLAN_MARKERS = [_][]const u8{
    "PHASE11_BCM2835_WDT_PLATFORM_PLAN_STATUS=plan_landed",
    "lane family: `P11-L02`",
    "Several existing bcm2835 reminder notes now point at one explicit validation plan as the",
    "PM-base absence, PM-base readiness, and blocked-on-live-platform-registration outcomes explicit",
    "register-device intent from successful live watchdog-core registration",
    "claimed-versus-conflicting ownership remains explicit across poweroff and remove paths",
    "Keep the next bcm2835 move bcm2835-only.",
};

const SURVEY_MARKERS = [_][]const u8{
    "explicit validation plan",
    "manifest-backed archival reminder packet",
    "drivers/watchdog/bcm2835_wdt_verify.zig",
};

const TEARDOWN_MARKERS = [_][]const u8{
    "explicit validation plan",
    "drivers/watchdog/bcm2835_wdt_verify.zig",
    "archival manifest-backed reminder packet",
};

const MATRIX_MARKERS = [_][]const u8{
    "explicit validation plan",
    "drivers/watchdog/bcm2835_wdt_verify.zig",
    "zigux/tests/phase11_bcm2835_wdt_survey.zig",
};

const MANIFEST_MARKERS = [_][]const u8{
    "\"lane_key\": \"P11-L08\"",
    "\"id\": \"phase11-bcm2835-wdt-live-platform-registration\"",
    "\"status\": \"blocked_on_driver_scaffold\"",
};

const SURVEY_GATE_MARKERS = [_][]const u8{
    "phase11 bcm2835 survey keeps direct handoff and lifecycle helpers explicit",
    "phase11 bcm2835 survey keeps survey, teardown, manifest, and matrix notes aligned",
    "phase11 bcm2835 survey keeps the replay and verify helpers reviewable",
};

const DRIVER_MARKERS = [_][]const u8{
    "pub fn summarizePlatformHandoff(request: PlatformHandoffRequest) !PlatformHandoffSummary",
    ".blocked_on_live_platform_registration = true,",
    "pub fn poweroff(self: *Bcm2835WdtLab, handler_claimed: bool) PoweroffSummary",
};

const VERIFY_MARKERS = [_][]const u8{
    "phase11 bcm2835 watchdog verify keeps PM-base readiness and ownership explicit",
    "phase11 bcm2835 watchdog verify keeps poweroff ownership distinct",
};

const REPLAY_MARKERS = [_][]const u8{
    "phase11 bcm2835 watchdog replay keeps platform handoff readiness and poweroff claim blocking explicit",
    "phase11 bcm2835 watchdog replay keeps start stop restart and poweroff lifecycle explicit",
};

const FILES = [_][]const u8{
    "plan",
    "Documentation/zigux/phase11-bcm2835-wdt-platform-validation-plan.md",
    "survey",
    "Documentation/zigux/phase11-bcm2835-wdt-survey.md",
    "teardown",
    "Documentation/zigux/phase11-bcm2835-wdt-teardown-note.md",
    "matrix",
    "Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md",
    "manifest",
    "zigux/tests/phase11_bcm2835_wdt_manifest.json",
    "survey_gate",
    "zigux/tests/phase11_bcm2835_wdt_survey.zig",
    "driver",
    "drivers/watchdog/bcm2835_wdt.zig",
    "verify",
    "drivers/watchdog/bcm2835_wdt_verify.zig",
    "replay",
    "zigux/tests/phase11_bcm2835_wdt.zig",
};

pub fn checkText(text: []const u8) guard.GuardError!void {
    for (PLAN_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (SURVEY_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (TEARDOWN_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (MATRIX_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (MANIFEST_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (SURVEY_GATE_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (DRIVER_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (VERIFY_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (REPLAY_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (FILES) |marker| try guard.requireMarker(text, marker);
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
