const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE10_TESTS_ROOT_COMPANION_CHECKER_SELF_TEST=pass";

const COMPANION_REQUIRED_MARKERS = [_][]const u8{
    "Keep the current bounded virtio closure packet explicit through the shared reminder surfaces",
    "`scripts/zigux/check_phase10_bootstrap_route.zig`",
    "`scripts/zigux/check_phase10_core_packet.zig`",
    "`scripts/zigux/check_phase10_tests_readme_core_surfaces.zig`",
    "`scripts/zigux/check_phase10_closure_manifest_counts.zig`",
    "`Documentation/zigux/phase10-virtio-ring-survey.md`",
    "`drivers/virtio/virtio_ring_publish_readiness.zig`",
    "`zigux/tests/phase10_virtio_ring_survey.zig`",
    "`Documentation/zigux/phase10-virtio-input-module-slice.md`",
    "`drivers/virtio/virtio_input_queue_callback_preflight.zig`",
    "`drivers/virtio/virtio_input_teardown_preflight.zig`",
    "`zigux/tests/phase10_virtio_input_queue_callback_preflight.zig`",
    "`zigux/tests/phase10_virtio_input_teardown_preflight.zig`",
    "`Documentation/zigux/phase10-virtio-mmio-config-write-disposition-companion.md`",
    "`zigux/tests/phase10_virtio_mmio_apply_observation_replay.zig`",
    "`zigux/tests/build.phase10_virtio_mmio_apply_observation_replay.zig`",
    "`scripts\zigux/validate_phase10.zig`",
    "`scripts\zigux/validate_phase10_closure.zig`",
    "`zigux/tests/phase10_closure_manifest.json`",
    "The returned shared build gate now runs through `zigux/Makefile`, `make -C zigux phase10-validate`, `make -C zigux phase10-test`, `make -C zigux phase10`, and `zigux/tests/phase10_build.zig`.",
    "current direct lane readback now rematerializes `drivers/virtio/virtio_driver_id.zig` and `zigux/tests/phase10_virtio_driver_id.zig`",
    "Keep the queue-local `P10-L10` ring freeze-boundary packet distinct from the bounded `P10-L11` MMIO helper packet",
    "`drivers/virtio/virtio.zig` owns shared device-status bookkeeping",
    "`drivers/virtio/virtio_ring.zig` owns virtqueue wrapper shape and notification planning",
    "`drivers/virtio/virtio_mmio.zig` owns MMIO wrapper planning",
};

const COMPANION_FORBIDDEN_MARKERS = [_][]const u8{
    "current `master` still does not materialize `scripts\zigux/validate_phase10.zig`",
    "current direct lane readback still does not materialize `drivers/virtio/virtio_driver_id.zig`",
    "last-known packet member",
};

const TESTS_ROOT_REQUIRED_MARKERS = [_][]const u8{
    "`Documentation/zigux/phase10-closure-evidence.md`",
    "`Documentation/zigux/phase10-virtio-driver-lane-sequencing.md`",
    "`Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md`",
    "`scripts/zigux/check_phase10_tests_readme_core_surfaces.zig`",
    "`scripts/zigux/check_phase10_bootstrap_route.zig`",
    "`scripts/zigux/check_phase10_harness_coverage.zig`",
    "`scripts\zigux/validate_phase10_closure.zig`",
    "`zigux/tests/phase10_closure_manifest.json`",
    "The returned shared build gate now runs through `zigux/Makefile`, `make -C zigux phase10-validate`, `make -C zigux phase10-test`, `make -C zigux phase10`.",
    "`Documentation/zigux/phase10-virtio-input-module-slice.md`",
    "`drivers/virtio/virtio_input_queue_callback_preflight.zig`",
    "`drivers/virtio/virtio_ring_publish_readiness.zig`",
    "`zigux/tests/phase10_virtio_input_teardown_observation.zig`",
    "queue-callback-preflight, registration-preflight, status-drain, and teardown-observation replays explicit here",
    "`zigux/tests/phase10_virtio_mmio_apply_observation_replay.zig`",
    "`zigux/tests/build.phase10_virtio_mmio_apply_observation_replay.zig`",
    "without widening into lifecycle, IRQ-delivery, or DMA claims",
};

const SCRIPTS_ROOT_REQUIRED_MARKERS = [_][]const u8{
    "`scripts/zigux/check_phase10_ring_packet.zig`",
    "`scripts/zigux/check_phase10_input_packet.zig`",
    "`scripts/zigux/check_phase10_mmio_packet.zig`",
    "`scripts/zigux/check_phase10_harness_coverage.zig`",
    "`scripts/zigux/check_phase10_tests_readme_core_surfaces.zig`",
    "`scripts\zigux/validate_phase10.zig`",
    "`scripts\zigux/validate_phase10_closure.zig`",
    "`drivers/virtio/virtio_ring_publish_readiness.zig`",
    "`Documentation/zigux/phase10-virtio-core-survey.md`, `zigux/tests/phase10_virtio_core.zig`, `Documentation/zigux/phase10-virtio-core-slice.md`, `drivers/virtio/virtio_verify.zig`, `zigux/tests/phase10_virtio_core_reset_queue.zig`, `zigux/tests/phase10_virtio_core_interrupt_compound_ack.zig`, `zigux/tests/phase10_virtio_core_manifest.json`, and `zigux/tests/phase10_virtio_core_survey.zig` keep the bounded core packet explicit",
    "`drivers/virtio/virtio_driver_id.zig` plus `zigux/tests/phase10_virtio_driver_id.zig` pair stays explicit",
    "`zigux/Makefile`, `make -C zigux phase10-validate`, `make -C zigux phase10-test`, and `make -C zigux phase10` keep the returned shared build gate explicit",
    "do not widen this scripts-root packet into queue execution parity, IRQ delivery, DMA behavior, input registration lifecycle closure, or risky transport follow-through",
};

const SCRIPTS_ROOT_FORBIDDEN_MARKERS = [_][]const u8{
    "remain the narrower core-side repo-reality gaps on current `master`",
};

const PHASE10_START = [_][]const u8{
    "## Phase 10 tests-root packet",
};

const PHASE10_END = [_][]const u8{
    "## Phase 11 tests-root packet",
};

pub fn checkText(text: []const u8) guard.GuardError!void {
    for (COMPANION_REQUIRED_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (COMPANION_FORBIDDEN_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (TESTS_ROOT_REQUIRED_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (SCRIPTS_ROOT_REQUIRED_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (SCRIPTS_ROOT_FORBIDDEN_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (PHASE10_START) |marker| try guard.requireMarker(text, marker);
    for (PHASE10_END) |marker| try guard.requireMarker(text, marker);
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
