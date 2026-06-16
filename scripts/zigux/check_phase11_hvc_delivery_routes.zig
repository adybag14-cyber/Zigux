const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE11_HVC_DELIVERY_ROUTES_SELF_TEST=pass";

const REQUIRED_MAKEFILE_MARKERS = [_][]const u8{
    "phase11-contract:",
    "phase11-test:",
    "phase11-hvc-survey:",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check_phase11_hvc_survey_packet.zig --self-test",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check_phase11_hvc_survey_packet.zig",
    "cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build hvc-console-survey --build-file zigux/tests/phase11_build.zig --summary all",
    "phase11: phase11-contract phase11-test phase11-hvc-survey",
};

const REQUIRED_BUILD_MARKERS = [_][]const u8{
    "const test_step = b.step(\"test\", \"Run the shared Phase 11 starter packet\");",
    "test_step.dependOn(&run_phase11_uapi_header_parity_survey_tests.step);",
    "test_step.dependOn(&run_phase11_hvc_console_tests.step);",
    "test_step.dependOn(&run_hvc_console_verify_tests.step);",
    "test_step.dependOn(&run_phase11_hvc_cleanup_tests.step);",
    "const hvc_console_survey_step = b.step(\"hvc-console-survey\", \"Run the dedicated Phase 11 hvc_console archival survey\");",
    "hvc_console_survey_step.dependOn(&run_phase11_hvc_console_survey_tests.step);",
};

const REQUIRED_SHARED_DOC_MARKERS = [_][]const u8{
    "make -C zigux phase11-hvc-survey",
    "make -C zigux phase11",
    "zig build test --build-file zigux/tests/phase11_build.zig --summary all",
};

const REQUIRED_DEDICATED_DOC_MARKERS = [_][]const u8{
    "make -C zigux phase11-hvc-survey",
    "scripts/zigux/check_phase11_hvc_survey_packet.zig",
    ".github/workflows/zigux-bootstrap.yml",
};

const REQUIRED_WORKFLOW_SHARED_MARKERS = [_][]const u8{
    "run: make -C zigux phase11-contract",
    "run: make -C zigux phase11-test",
};

const WORKFLOW_DEDICATED_MARKERS = [_][]const u8{
    "run: make -C zigux phase11-hvc-survey",
    "run: make -C zigux phase11",
};

pub fn checkText(text: []const u8) guard.GuardError!void {
    for (REQUIRED_MAKEFILE_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (REQUIRED_BUILD_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (REQUIRED_SHARED_DOC_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (REQUIRED_DEDICATED_DOC_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (REQUIRED_WORKFLOW_SHARED_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (WORKFLOW_DEDICATED_MARKERS) |marker| try guard.requireMarker(text, marker);
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
