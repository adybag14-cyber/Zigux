const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE12_CROSS_BUILD_PACKET_SELF_TEST=pass";

const EXPECTED_BUILD_MARKERS = [_][]const u8{
    "b.path(\"phase12_virtio_net.zig\")",
    "b.path(\"phase12_virtio_net_survey.zig\")",
    "b.path(\"phase12_virtio_net_syntax_lab.zig\")",
    "b.path(\"phase12_virtio_scsi.zig\")",
    "b.path(\"phase12_virtio_scsi_survey.zig\")",
    "b.path(\"phase12_virtio_scsi_syntax_lab.zig\")",
    "b.path(\"phase12_nvme_pci.zig\")",
    "b.path(\"phase12_nvme_pci_survey.zig\")",
    "b.path(\"phase12_raw_github_coverage_survey.zig\")",
    "b.path(\"phase12_libbpf_segments.zig\")",
    "b.path(\"phase12_libbpf_reviewability.zig\")",
    ".name = \"phase12-cross-virtio-net-tests\"",
    ".name = \"phase12-cross-virtio-net-survey-tests\"",
    ".name = \"phase12-cross-virtio-net-syntax-lab-tests\"",
    ".name = \"phase12-cross-virtio-scsi-tests\"",
    ".name = \"phase12-cross-virtio-scsi-survey-tests\"",
    ".name = \"phase12-cross-virtio-scsi-syntax-lab-tests\"",
    ".name = \"phase12-cross-nvme-pci-tests\"",
    ".name = \"phase12-cross-nvme-pci-survey-tests\"",
    ".name = \"phase12-cross-raw-github-coverage-survey-tests\"",
    ".name = \"phase12-cross-libbpf-segment-survey-tests\"",
    ".name = \"phase12-cross-libbpf-reviewability-tests\"",
    "const cross_step = b.step(\"cross\", \"Compile the bounded Phase 12 packet for approved non-native musl targets\");",
    "cross_step.dependOn(&phase12_virtio_net_tests.step);",
    "cross_step.dependOn(&phase12_virtio_net_survey_tests.step);",
    "cross_step.dependOn(&phase12_virtio_net_syntax_lab_tests.step);",
    "cross_step.dependOn(&phase12_virtio_scsi_tests.step);",
    "cross_step.dependOn(&phase12_virtio_scsi_survey_tests.step);",
    "cross_step.dependOn(&phase12_virtio_scsi_syntax_lab_tests.step);",
    "cross_step.dependOn(&phase12_nvme_pci_tests.step);",
    "cross_step.dependOn(&phase12_nvme_pci_survey_tests.step);",
    "cross_step.dependOn(&phase12_raw_github_coverage_survey_tests.step);",
    "cross_step.dependOn(&phase12_libbpf_segments_tests.step);",
    "cross_step.dependOn(&phase12_libbpf_reviewability_tests.step);",
};

const EXPECTED_FIXTURE = [_][]const u8{
    "phase",
    "Phase 12",
    "lane_key",
    "P12-L02",
    "build_file",
    "build_step",
    "cross",
    "target_count",
    "targets",
    "x86_64-linux-musl",
    "aarch64-linux-musl",
    "riscv64-linux-musl",
};

pub fn checkText(text: []const u8) guard.GuardError!void {
    for (EXPECTED_BUILD_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (EXPECTED_FIXTURE) |marker| try guard.requireMarker(text, marker);
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
