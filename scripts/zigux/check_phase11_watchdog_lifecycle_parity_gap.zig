const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE11_WATCHDOG_LIFECYCLE_PARITY_GAP_SELF_TEST=pass";

const PARITY_NOTE_MARKERS = [_][]const u8{
    "bounded current-driver-depth",
    "`zigux/tests/phase11_bcm2835_wdt_manifest.json` keeps the remaining",
    "blocked on current-head platform registration, shared",
    "poweroff-callback ownership, and hardware-backed validation",
    "returned driver, direct tests-root replay, restart helper, verify helper,",
    "registration scaffold, and bounded PM-helper packet explicit on current",
    "`phase11-build-gate` as a shared current-head gap",
    "`phase11-dw-wdt-live-mmio-validation` at `ready_next`",
    "bcm2835 reads as a bounded current-driver-depth closure",
    "DesignWare reads as a returned starter-plus-test",
    "next bounded step is still live MMIO validation",
};

const BCM_SURVEY_MARKERS = [_][]const u8{
    "the Phase 11 simple-driver roadmap gap is closed at bounded current-driver depth on `master`",
    "`zigux/tests/phase11_bcm2835_wdt_manifest.json`",
};

const BCM_MATRIX_MARKERS = [_][]const u8{
    "`drivers/watchdog/bcm2835_wdt.zig`",
    "`drivers/watchdog/bcm2835_wdt_verify.zig`",
    "`Documentation/zigux/phase11-bcm2835-wdt-teardown-note.md`",
};

const DW_SURVEY_MARKERS = [_][]const u8{
    "`drivers/watchdog/dw_wdt.zig`, `zigux/tests/phase11_dw_wdt.zig`,",
    "The next bounded same-lane step",
    "hardware-backed MMIO validation",
};

const DW_MATRIX_MARKERS = [_][]const u8{
    "`drivers/watchdog/dw_wdt.zig` now rematerializes on current `master`",
    "`drivers/watchdog/dw_wdt_restart.zig`, `drivers/watchdog/dw_wdt_verify.zig`,",
    "hardware-backed MMIO validation",
};

const REQUIRED_FILES = [_][]const u8{
    "parity_note",
    "Documentation/zigux/phase11-watchdog-lifecycle-parity-gap.md",
    "bcm_survey",
    "Documentation/zigux/phase11-bcm2835-wdt-survey.md",
    "bcm_matrix",
    "Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md",
    "bcm_manifest",
    "zigux/tests/phase11_bcm2835_wdt_manifest.json",
    "dw_survey",
    "Documentation/zigux/phase11-dw-wdt-survey.md",
    "dw_matrix",
    "Documentation/zigux/phase11-dw-wdt-validation-matrix.md",
    "dw_manifest",
    "zigux/tests/phase11_dw_wdt_manifest.json",
};

const EXPECTED_BCM_MANIFEST = [_][]const u8{
    "lane_key",
    "P11-L08",
    "blocked_gaps",
    "phase11-bcm2835-platform-registration",
    "blocked_current_head",
    "phase11-bcm2835-shared-poweroff-callback-ownership",
    "blocked_current_head",
    "phase11-bcm2835-hardware-backed-validation",
    "blocked_current_head",
};

const EXPECTED_DW_MANIFEST = [_][]const u8{
    "lane_key",
    "P11-L10",
    "starter_gaps",
    "phase11-dw-wdt-driver-starter",
    "starter_landed",
    "phase11-dw-wdt-driver-tests",
    "starter_landed",
    "phase11-dw-wdt-teardown-parity",
    "starter_landed",
    "phase11-dw-wdt-live-platform-pm",
    "starter_landed",
    "next_gap",
    "id",
    "phase11-dw-wdt-live-mmio-validation",
    "status",
    "ready_next",
    "shared_gap",
    "id",
    "phase11-build-gate",
    "status",
    "shared_gap_current_head",
};

pub fn checkText(text: []const u8) guard.GuardError!void {
    for (PARITY_NOTE_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (BCM_SURVEY_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (BCM_MATRIX_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (DW_SURVEY_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (DW_MATRIX_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (REQUIRED_FILES) |marker| try guard.requireMarker(text, marker);
    for (EXPECTED_BCM_MANIFEST) |marker| try guard.requireMarker(text, marker);
    for (EXPECTED_DW_MANIFEST) |marker| try guard.requireMarker(text, marker);
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
