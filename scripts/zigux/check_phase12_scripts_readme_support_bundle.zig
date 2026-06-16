const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE12_SCRIPTS_README_SUPPORT_BUNDLE_SELF_TEST=pass";

const EXPECTED_PHASE12_MARKERS = [_][]const u8{
    "(- Phase 12 flow - the current scripts-root reminder packet stays reviewable through the validator-first support bundle and returned shared wrappers without promoting driver-local rollback, NVMe foothold, or parked libbpf evidence into the shared smoke-and-test route)",
    "(- `scripts/zigux/check_build_only_phase12_surface.zig`, `scripts/zigux/check_phase12_release_readiness_packet.zig`, `scripts/zigux/check_phase12_complex_driver_lane_packet.zig`, `scripts/zigux/check_phase12_cross_compile_smoke.zig`, `scripts/zigux/check_phase12_libbpf_snapshot.zig`, `scripts/zigux/check_phase12_libbpf_lane_marker.zig`, `scripts/zigux/check_phase12_libbpf_heavy_consumer_packet.zig`, and `scripts\zigux/validate_phase12.zig` keep the current Phase 12 validator-side support bundle explicit from the scripts root)",
    "(- `make -C zigux phase12-validate`, `make -C zigux phase12-smoke`, `make -C zigux phase12-test`, and `make -C zigux phase12` are shipped current-`master` wrapper evidence again, while `zigux/tests/phase12_build.zig` keeps the shared smoke and test route bounded to the six-file `virtio_net` sextet)",
    "(- keep the shared route split explicit here too: the six-file `virtio_net` packet is the only current shared smoke-and-test route, the rollback-lab `virtio_scsi` survey-build packet and bounded `nvme_pci` foothold stay driver-local evidence outside that route, and the parked libbpf packet stays limited to survey, snapshot, lane-marker, and heavy-consumer reminder guards)",
};

const EXPECTED_SUPPORT_TOOLS = [_][]const u8{
    "scripts/zigux/check_build_only_phase12_surface.zig",
    "scripts/zigux/check_phase12_release_readiness_packet.zig",
    "scripts/zigux/check_phase12_complex_driver_lane_packet.zig",
    "scripts/zigux/check_phase12_cross_compile_smoke.zig",
    "scripts/zigux/check_phase12_libbpf_snapshot.zig",
    "scripts/zigux/check_phase12_libbpf_lane_marker.zig",
    "scripts/zigux/check_phase12_libbpf_heavy_consumer_packet.zig",
    "scripts\zigux/validate_phase12.zig",
};

pub fn checkText(text: []const u8) guard.GuardError!void {
    for (EXPECTED_PHASE12_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (EXPECTED_SUPPORT_TOOLS) |marker| try guard.requireMarker(text, marker);
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
