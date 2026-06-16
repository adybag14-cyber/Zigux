const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE11_HVC_MODEM_CONTROL_PACKET_SELF_TEST=pass";

const REQUIRED_PACKET_FILES = [_][]const u8{
    "SURVEY_PATH",
    "COMPANION_PATH",
    "MATRIX_PATH",
    "DRIVER_PATH",
    "PROOF_PATH",
    "BUILD_PATH",
    "INVENTORY_PATH",
    "MAKEFILE_PATH",
};

const SURVEY_MARKERS = [_][]const u8{
    "`zigux/tests/phase11_hvc_modem_control_proof.zig`",
    "`zigux/tests/phase11_hvc_modem_control_proof_build.zig`",
    "dedicated modem-control proof pair",
    "focused adjunct route",
};

const COMPANION_MARKERS = [_][]const u8{
    "`zigux/tests/phase11_hvc_modem_control_proof.zig`",
    "`zigux/tests/phase11_hvc_modem_control_proof_build.zig`",
    "focused teardown-adjacent proof route",
    "dedicated modem-control proof pair",
};

const MATRIX_MARKERS = [_][]const u8{
    "`zigux/tests/phase11_hvc_modem_control_proof.zig`",
    "`zigux/tests/phase11_hvc_modem_control_proof_build.zig`",
    "keep the modem-control proof pair directly readable through its focused build route",
};

const DRIVER_MARKERS = [_][]const u8{
    "pub const ModemControlRequest = struct {",
    "pub const ModemControlSummary = struct {",
    "pub fn summarizeModemControlHandoff(request: ModemControlRequest) ModemControlSummary {",
    "test \"phase11 hvc console keeps modem-control helper surface reviewable\" {",
};

const PROOF_MARKERS = [_][]const u8{
    "test \"phase11 hvc console keeps full modem control callback surfaces reviewable\" {",
    "test \"phase11 hvc console masks tiocmset requests when hv_ops exposes only tiocmget\" {",
    "test \"phase11 hvc console keeps clear-only requests distinct from DTR assertion visibility\" {",
    "test \"phase11 hvc console keeps dedicated dtr_rts callbacks distinct from tiocmset masks\" {",
    "test \"phase11 hvc console keeps hupcl teardown distinct from callback-backed modem control\" {",
};

const BUILD_MARKERS = [_][]const u8{
    ".root_source_file = b.path(\"../../drivers/tty/hvc/hvc_console.zig\")",
    ".root_source_file = b.path(\"phase11_hvc_modem_control_proof.zig\")",
    "root_module.addImport(\"hvc_console\", hvc_console_module);",
    ".name = \"phase11-hvc-modem-control-proof\",",
    "const test_step = b.step(\"test\", \"Run the focused Phase 11 HVC modem-control proof.\");",
};

const INVENTORY_EXACT_CHECK = [_][]const u8{
    "zig build test --build-file zigux/tests/phase11_hvc_modem_control_proof_build.zig",
};

const MAKEFILE_MARKERS = [_][]const u8{
    "phase11-validate:",
    "cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build test --build-file zigux/tests/phase11_hvc_modem_control_proof_build.zig",
};

const INVENTORY_FOCUSED_REPLAY = [_][]const u8{
    "zigux/tests/phase11_hvc_modem_control_proof_build.zig",
};

pub fn checkText(text: []const u8) guard.GuardError!void {
    for (REQUIRED_PACKET_FILES) |marker| try guard.requireMarker(text, marker);
    for (SURVEY_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (COMPANION_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (MATRIX_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (DRIVER_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (PROOF_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (BUILD_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (INVENTORY_EXACT_CHECK) |marker| try guard.requireMarker(text, marker);
    for (MAKEFILE_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (INVENTORY_FOCUSED_REPLAY) |marker| try guard.requireMarker(text, marker);
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
