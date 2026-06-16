const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE11_BCM2835_SHARED_REPLAY_SURFACE_SELF_TEST=pass";

const SURVEY_MARKERS = [_][]const u8{
    "PHASE11_BCM2835_WDT_SURVEY_STATUS=survey_gate_landed",
    "archival packet identity remains `P11-L08`",
    "`Documentation/zigux/phase11-bcm2835-wdt-platform-validation-plan.md`",
    "`Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md`",
    "`zigux/tests/phase11_bcm2835_wdt_manifest_packet_survey.zig`",
    "`zigux/tests/phase11_bcm2835_wdt_manifest_packet_survey_build.zig`",
    "`drivers/watchdog/bcm2835_wdt.zig`",
    "`drivers/watchdog/bcm2835_wdt_verify.zig`",
    "`zigux/tests/phase11_bcm2835_wdt.zig`",
    "driver-return proof plus a coupled verify helper",
    "current-head validation matrix",
    "manifest-backed closure or teardown-note step",
};

const PLAN_MARKERS = [_][]const u8{
    "PHASE11_BCM2835_WDT_PLATFORM_VALIDATION_PLAN=starter_boundary_recorded",
    "`Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md`",
    "`drivers/watchdog/bcm2835_wdt.zig`, `drivers/watchdog/bcm2835_wdt_verify.zig`, and `zigux/tests/phase11_bcm2835_wdt.zig`",
    "minimal driver-return proof, driver-backed verify helper, and focused tests-root replay",
    "Do not fabricate current-head proof for a manifest-backed closure packet, slice note, teardown note",
    "Do not use it to reopen `gpio_wdt`, `dw_wdt`, HVC, or shared Phase 11 wording.",
    "The next honest bcm2835-only follow-through is one explicit manifest-backed closure or teardown-note step",
};

const MATRIX_MARKERS = [_][]const u8{
    "PHASE11_BCM2835_WDT_STATUS=driver_proof_and_matrix_packet_truthful",
    "lane: `P11-L08`",
    "`drivers/watchdog/bcm2835_wdt.zig`",
    "`drivers/watchdog/bcm2835_wdt_verify.zig`",
    "`zigux/tests/phase11_bcm2835_wdt.zig`",
    "`Documentation/zigux/phase11-bcm2835-wdt-platform-validation-plan.md`",
    "`zigux/tests/phase11_bcm2835_wdt_manifest_packet_survey.zig`",
    "`zigux/tests/phase11_bcm2835_wdt_manifest_packet_survey_build.zig`",
    "compile anchor: `zigux/tests/phase11_bcm2835_wdt.zig`",
    "verify-helper anchor: `drivers/watchdog/bcm2835_wdt_verify.zig`",
    "does not treat absent wider replay, manifest, slice, or teardown-note files as current-head evidence.",
};

const DRIVER_TEST_MARKERS = [_][]const u8{
    "test \"phase11 bcm2835 watchdog starter keeps timeout and restart constants reviewable\" {",
    "test \"phase11 bcm2835 watchdog verify keeps PM-base readiness and ownership explicit\" {",
    "test \"phase11 bcm2835 watchdog verify keeps poweroff ownership distinct\" {",
};

const PACKET_SURVEY_MARKERS = [_][]const u8{
    "test \"phase11 bcm2835 manifest packet survey keeps the returned driver proof truthful\" {",
    "test \"phase11 bcm2835 manifest packet survey keeps the blocker plan aligned with current master\" {",
    "test \"phase11 bcm2835 manifest packet survey keeps the validation matrix aligned with the current driver packet\" {",
    "test \"phase11 bcm2835 manifest packet survey keeps the dedicated build route pointed at the current reminder packet\" {",
    "try expectContains(build_file, \".name = \\\"phase11-bcm2835-wdt-manifest-packet-survey-tests\\\"\");",
};

const PACKET_BUILD_MARKERS = [_][]const u8{
    ".root_source_file = b.path(\"phase11_bcm2835_wdt_manifest_packet_survey.zig\")",
    ".name = \"phase11-bcm2835-wdt-manifest-packet-survey-tests\"",
    "Run the focused Phase 11 bcm2835 watchdog manifest packet survey",
};

const REQUIRED_FILES = [_][]const u8{
    "survey",
    "Documentation/zigux/phase11-bcm2835-wdt-survey.md",
    "plan",
    "Documentation/zigux/phase11-bcm2835-wdt-platform-validation-plan.md",
    "matrix",
    "Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md",
    "driver_tests",
    "zigux/tests/phase11_bcm2835_wdt.zig",
    "packet_survey",
    "zigux/tests/phase11_bcm2835_wdt_manifest_packet_survey.zig",
    "packet_build",
    "zigux/tests/phase11_bcm2835_wdt_manifest_packet_survey_build.zig",
};

const MARKERS_BY_LABEL = [_][]const u8{
    "survey",
    "plan",
    "matrix",
    "driver_tests",
    "packet_survey",
    "packet_build",
};

pub fn checkText(text: []const u8) guard.GuardError!void {
    for (SURVEY_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (PLAN_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (MATRIX_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (DRIVER_TEST_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (PACKET_SURVEY_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (PACKET_BUILD_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (REQUIRED_FILES) |marker| try guard.requireMarker(text, marker);
    for (MARKERS_BY_LABEL) |marker| try guard.requireMarker(text, marker);
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
