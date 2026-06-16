const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE12_COMPILE_SMOKE_SCOPE_SELF_TEST=pass";

const REQUIRED_MARKERS = [_][]const u8{
    "const virtio_net_survey_root_module = b.createModule(.{",
    ".root_source_file = b.path(\"phase12_virtio_net_survey.zig\"),",
    "const phase12_virtio_net_survey_tests = b.addTest(.{",
    ".name = \"phase12-virtio-net-survey-tests\",",
    "const run_virtio_net_survey_tests = b.addRunArtifact(",
    "smoke_step.dependOn(&run_virtio_net_survey_tests.step);",
    "test_step.dependOn(&run_virtio_net_survey_tests.step);",
    "survey-gate smoke tests",
    "survey-gate tests",
};

const EXACT_COUNT_MARKERS = [_][]const u8{
    "b.createModule(.{",
    ".addImport(",
    "b.addTest(.{",
    "b.addRunArtifact(",
    "smoke_step.dependOn(",
    "test_step.dependOn(",
    "b.step(",
};

const FORBIDDEN_MARKERS = [_][]const u8{
    "\"phase12_virtio_net_syntax_lab.zig\"",
    "\"phase12_virtio_scsi_syntax_lab.zig\"",
    "\"phase12_virtio_scsi_survey.zig\"",
    "\"phase12_nvme_pci.zig\"",
};

const PHASE12_BUILD_PATH = [_][]const u8{
    "zigux/tests/phase12_build.zig",
};

pub fn checkText(text: []const u8) guard.GuardError!void {
    for (REQUIRED_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (EXACT_COUNT_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (FORBIDDEN_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (PHASE12_BUILD_PATH) |marker| try guard.requireMarker(text, marker);
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
