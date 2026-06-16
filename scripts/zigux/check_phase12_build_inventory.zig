const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE12_BUILD_INVENTORY_SELF_TEST=pass";

const REQUIRED_MAKEFILE_MARKERS = [_][]const u8{
    "phase12-smoke:",
    "$(ZIG_REPO_ROOT) build smoke --build-file zigux/tests/phase12_build.zig --summary all",
    "phase12-test:",
    "$(ZIG_REPO_ROOT) build test --build-file zigux/tests/phase12_build.zig --summary all",
    "phase12-virtio-net-syntax-lab-test:",
    "$(ZIG_REPO_ROOT) build test --build-file zigux/tests/phase12_virtio_net_syntax_lab_build.zig --summary all",
    "phase12: phase12-validate phase12-smoke phase12-test",
};

const FORBIDDEN_MAKEFILE_MARKERS = [_][]const u8{
    "phase12: phase12-validate phase12-smoke phase12-test phase12-virtio-net-syntax-lab-test",
    "phase12-smoke: phase12-virtio-net-syntax-lab-test",
};

const EXPECTED_SYNTAX_LAB_INVENTORY = [_][]const u8{
    "build_test_names",
    "phase12-virtio-net-syntax-lab-tests",
    "shared_smoke_depend_steps",
    "run_syntax_lab_tests",
    "shared_test_depend_steps",
    "run_syntax_lab_tests",
    "throughput_anchor_depend_steps",
    "module_root_source_files",
    "module",
    "virtio_module",
    "path",
    "../../drivers/virtio/virtio.zig",
    "module",
    "queue_resume_module",
    "path",
    "../../drivers/net/virtio_net_queue_resume.zig",
    "module",
    "receive_refill_replay_module",
    "path",
    "../../drivers/net/virtio_net_receive_refill_replay.zig",
    "module",
    "transmit_recycle_module",
    "path",
    "../../drivers/net/virtio_net_transmit_recycle.zig",
    "module",
    "post_reset_replay_module",
    "path",
    "../../drivers/net/virtio_net_post_reset_replay.zig",
    "module",
    "throughput_parity_module",
    "path",
    "../../drivers/net/virtio_net_throughput_parity.zig",
    "module",
    "syntax_lab_module",
    "path",
    "phase12_virtio_net_syntax_lab.zig",
    "module_imports",
    "module",
    "syntax_lab_module",
    "import_name",
    "virtio",
    "imported_module",
    "virtio_module",
    "module",
    "syntax_lab_module",
    "import_name",
    "virtio_net_queue_resume",
    "imported_module",
    "queue_resume_module",
    "module",
    "syntax_lab_module",
    "import_name",
    "virtio_net_receive_refill_replay",
    "imported_module",
    "receive_refill_replay_module",
    "module",
    "syntax_lab_module",
    "import_name",
    "virtio_net_transmit_recycle",
    "imported_module",
    "transmit_recycle_module",
    "module",
    "syntax_lab_module",
    "import_name",
    "virtio_net_post_reset_replay",
    "imported_module",
    "post_reset_replay_module",
    "module",
    "syntax_lab_module",
    "import_name",
    "virtio_net_throughput_parity",
    "imported_module",
    "throughput_parity_module",
    "test_root_modules",
    "test",
    "phase12-virtio-net-syntax-lab-tests",
    "root_module",
    "syntax_lab_module",
    "build_step_catalog",
    "variable",
    "smoke_step",
    "step",
    "smoke",
    "description",
    "Run the Phase 12 virtio_net syntax-lab smoke tests",
    "variable",
    "test_step",
    "step",
    "test",
    "description",
    "Run the Phase 12 virtio_net syntax-lab tests",
};

pub fn checkText(text: []const u8) guard.GuardError!void {
    for (REQUIRED_MAKEFILE_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (FORBIDDEN_MAKEFILE_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (EXPECTED_SYNTAX_LAB_INVENTORY) |marker| try guard.requireMarker(text, marker);
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
