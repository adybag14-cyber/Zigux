const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "{CHECK_NAME}_SELF_TEST=pass";

const EXPECTED_TARGETS = [_][]const u8{
    "x86_64-linux-musl",
    "aarch64-linux-musl",
    "riscv64-linux-musl",
};

const NOTE_MARKERS = [_][]const u8{
    "roadmap scope: keep existing Phase 12 `virtio_net`, `nvme_pci`, `virtio_scsi`, and bounded libbpf reviewability surfaces parse-valid across approved non-native musl targets without claiming new runtime parity",
    "compile entrypoint: `zig run scripts/zigux/check_phase12_cross.zig -- --zig `",
    "build file: `zigux/tests/phase12_cross_build.zig`",
    "approved targets: `x86_64-linux-musl`, `aarch64-linux-musl`, `riscv64-linux-musl`",
    "phase12_virtio_net_syntax_lab.zig",
    "phase12_virtio_scsi_syntax_lab.zig",
    "phase12_raw_github_coverage_survey.zig",
    "rollback posture: if this packet drifts, repair the cross-build wiring or remove the stale claim before widening any Phase 12 driver implementation work",
};

const BUILD_MARKERS = [_][]const u8{
    "const cross_step = b.step(\"cross\", \"Compile the bounded Phase 12 packet for approved non-native musl targets\");",
    ".root_source_file = b.path(\"phase12_virtio_net_syntax_lab.zig\")",
    ".name = \"phase12-cross-virtio-net-syntax-lab-tests\"",
    ".root_source_file = b.path(\"phase12_virtio_scsi_syntax_lab.zig\")",
    ".name = \"phase12-cross-virtio-scsi-syntax-lab-tests\"",
    ".root_source_file = b.path(\"phase12_raw_github_coverage_survey.zig\")",
    ".name = \"phase12-cross-raw-github-coverage-survey-tests\"",
    ".name = \"phase12-cross-libbpf-reviewability-tests\"",
    "cross_step.dependOn(&phase12_virtio_net_syntax_lab_tests.step);",
    "cross_step.dependOn(&phase12_virtio_scsi_syntax_lab_tests.step);",
    "cross_step.dependOn(&phase12_raw_github_coverage_survey_tests.step);",
    "cross_step.dependOn(&phase12_libbpf_reviewability_tests.step);",
};

const VIRTIO_NET_SYNTAX_MARKERS = [_][]const u8{
    "test \"phase12 virtio net syntax lab keeps queue-topology, refill, recovery, control recovery, and payload shape exports reachable\"",
    "test \"phase12 virtio net syntax lab keeps control queue payload shaping separate from runtime commands\"",
    "test \"phase12 virtio net syntax lab clears stale control queue and mergeable refill state across a second recovery cycle\"",
};

const VIRTIO_SCSI_SYNTAX_MARKERS = [_][]const u8{
    "test \"phase12 virtio scsi syntax lab keeps transport-reset recovery exports reachable\"",
    "freezeForTransportReset",
};

const RAW_GITHUB_COVERAGE_MARKERS = [_][]const u8{
    "test \"phase12 raw GitHub coverage manifest keeps the shared fallback split reviewable\"",
    "Documentation/zigux/phase12-raw-github-coverage-survey.md",
    "Documentation/zigux/phase12-release-coordination-matrix.md",
};

pub fn checkText(text: []const u8) guard.GuardError!void {
    for (EXPECTED_TARGETS) |marker| try guard.requireMarker(text, marker);
    for (NOTE_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (BUILD_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (VIRTIO_NET_SYNTAX_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (VIRTIO_SCSI_SYNTAX_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (RAW_GITHUB_COVERAGE_MARKERS) |marker| try guard.requireMarker(text, marker);
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
