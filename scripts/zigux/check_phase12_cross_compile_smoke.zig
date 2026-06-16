const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "{CHECK_NAME}_SELF_TEST=pass";

const REQUIRED_FILES = [_][]const u8{
    "NOTE_PATH",
    "MAKEFILE_PATH",
    "VALIDATOR_PATH",
    "WORKFLOW_PATH",
};

const NOTE_MARKERS = [_][]const u8{
    "- support checker: `scripts/zigux/check_phase12_cross_compile_smoke.zig`",
    "the active shared `virtio_net` compile-smoke packet is the six-file bundle in `zigux/tests/phase12_build.zig`",
    "current `zigux/Makefile` directly exposes `make -C zigux phase12-validate`, `make -C zigux phase12-smoke`, `make -C zigux phase12-test`, `make -C zigux phase12`, `make -C zigux phase12-virtio-net-syntax-lab-test`, and `make -C zigux phase12-virtio-net-throughput-parity-test`",
    "the isolated syntax-lab rerun handles are `zig build test --build-file zigux/tests/phase12_virtio_net_syntax_lab_build.zig --summary all` and `make -C zigux phase12-virtio-net-syntax-lab-test`, so the companion stays reviewable without joining the shared packet",
    "the dedicated throughput-parity rerun handles are `zig build phase12-virtio-net-throughput-parity --build-file zigux/tests/phase12_build.zig --summary all` and `make -C zigux phase12-virtio-net-throughput-parity-test`, so the perf-focused replay stays reviewable without widening the shared packet",
    "the shipped cross-compile checker now keeps that returned wrapper wording plus the isolated syntax-lab rerun hook and the dedicated throughput-parity rerun hook fail-closed across this note and `zigux/Makefile`",
    "If only the isolated syntax-lab rerun hook or the dedicated throughput-parity rerun hook drifts, repair just that narrower rerun handle around `zigux/tests/phase12_virtio_net_syntax_lab_build.zig`, `zigux/tests/phase12_build.zig`, `zigux/Makefile`, and this note instead of widening the shared packet.",
};

const MAKEFILE_MARKERS = [_][]const u8{
    "phase12-virtio-net-syntax-lab-test:",
    "$(ZIG_REPO_ROOT) build test --build-file zigux/tests/phase12_virtio_net_syntax_lab_build.zig --summary all",
    "phase12-virtio-net-throughput-parity-test:",
    "$(ZIG_REPO_ROOT) build phase12-virtio-net-throughput-parity --build-file zigux/tests/phase12_build.zig --summary all",
    "phase12: phase12-validate phase12-smoke phase12-test",
};

const VALIDATOR_MARKERS = [_][]const u8{
    "CROSS_COMPILE_CHECKER_PATH = \"scripts/zigux/check_phase12_cross_compile_smoke.zig\"",
    "CROSS_COMPILE_CHECKER_PATH,",
};

const WORKFLOW_MARKERS = [_][]const u8{
    "- name: Self-test current Phase 12 cross-compile smoke checker",
    "run: zig run scripts/zigux/check_phase12_cross_compile_smoke.zig -- --self-test",
    "- name: Check current Phase 12 cross-compile smoke packet",
    "run: zig run scripts/zigux/check_phase12_cross_compile_smoke.zig --",
};

const FORBIDDEN_NOTE_MARKERS = [_][]const u8{
    "the remaining same-family note drift is shared wording",
};

const CHECK_NAME = [_][]const u8{
    "PHASE12_CROSS_COMPILE_SMOKE",
};

pub fn checkText(text: []const u8) guard.GuardError!void {
    for (REQUIRED_FILES) |marker| try guard.requireMarker(text, marker);
    for (NOTE_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (MAKEFILE_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (VALIDATOR_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (WORKFLOW_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (FORBIDDEN_NOTE_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (CHECK_NAME) |marker| try guard.requireMarker(text, marker);
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
