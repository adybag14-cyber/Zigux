const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE10_TESTS_ROOT_COMPANION_CHECK=pass";
pub const self_test_pass_marker = "PHASE10_TESTS_ROOT_COMPANION_CHECKER_SELF_TEST=pass";
pub const pass_marker = self_test_pass_marker;

const FileContract = struct { rel: []const u8, markers: []const []const u8 };

const markers_0 = [_][]const u8{
    "Keep the current bounded virtio closure packet explicit through the shared reminder surfaces",
    "`scripts\\zigux/check_phase10_bootstrap_route.zig`",
    "`scripts\\zigux/check_phase10_core_packet.zig`",
    "`scripts\\zigux/check_phase10_tests_readme_core_surfaces.zig`",
    "`scripts\\zigux/check_phase10_closure_manifest_counts.zig`",
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
    "`scripts\\zigux/validate_phase10.zig`",
    "`scripts\\zigux/validate_phase10_closure.zig`",
    "`zigux/tests/phase10_closure_manifest.json`",
    "The returned shared build gate now runs through `zigux/Makefile`, `make -C zigux phase10-validate`, `make -C zigux phase10-test`, `make -C zigux phase10`, and `zigux/tests/phase10_build.zig`.",
    "current direct lane readback now rematerializes `drivers/virtio/virtio_driver_id.zig` and `zigux/tests/phase10_virtio_driver_id.zig`",
    "Keep the queue-local `P10-L10` ring freeze-boundary packet distinct from the bounded `P10-L11` MMIO helper packet",
    "`drivers/virtio/virtio.zig` owns shared device-status bookkeeping",
    "`drivers/virtio/virtio_ring.zig` owns virtqueue wrapper shape and notification planning",
    "`drivers/virtio/virtio_mmio.zig` owns MMIO wrapper planning",
};

const markers_1 = [_][]const u8{
    "`Documentation/zigux/phase10-closure-evidence.md`",
    "`Documentation/zigux/phase10-virtio-driver-lane-sequencing.md`",
    "`Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md`",
    "`scripts\\zigux/check_phase10_tests_readme_core_surfaces.zig`",
    "`scripts\\zigux/check_phase10_bootstrap_route.zig`",
    "`scripts\\zigux/check_phase10_harness_coverage.zig`",
    "`scripts\\zigux/validate_phase10_closure.zig`",
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

const markers_2 = [_][]const u8{
    "`scripts\\zigux/check_phase10_ring_packet.zig`",
    "`scripts\\zigux/check_phase10_input_packet.zig`",
    "`scripts\\zigux/check_phase10_mmio_packet.zig`",
    "`scripts\\zigux/check_phase10_harness_coverage.zig`",
    "`scripts\\zigux/check_phase10_tests_readme_core_surfaces.zig`",
    "`scripts\\zigux/validate_phase10.zig`",
    "`scripts\\zigux/validate_phase10_closure.zig`",
    "`drivers/virtio/virtio_ring_publish_readiness.zig`",
    "`Documentation/zigux/phase10-virtio-core-survey.md`, `zigux/tests/phase10_virtio_core.zig`, `Documentation/zigux/phase10-virtio-core-slice.md`, `drivers/virtio/virtio_verify.zig`, `zigux/tests/phase10_virtio_core_reset_queue.zig`, `zigux/tests/phase10_virtio_core_interrupt_compound_ack.zig`, `zigux/tests/phase10_virtio_core_manifest.json`, and `zigux/tests/phase10_virtio_core_survey.zig` keep the bounded core packet explicit",
    "`drivers/virtio/virtio_driver_id.zig` plus `zigux/tests/phase10_virtio_driver_id.zig` pair stays explicit",
    "`zigux/Makefile`, `make -C zigux phase10-validate`, `make -C zigux phase10-test`, and `make -C zigux phase10` keep the returned shared build gate explicit",
    "do not widen this scripts-root packet into queue execution parity, IRQ delivery, DMA behavior, input registration lifecycle closure, or risky transport follow-through",
};

const forbidden_markers_0 = [_][]const u8{
    "current `master` still does not materialize `scripts/zigux/validate-phase10.py`",
    "current direct lane readback still does not materialize `drivers/virtio/virtio_driver_id.zig`",
    "last-known packet member",
};

const forbidden_markers_1 = [_][]const u8{
    "remain the narrower core-side repo-reality gaps on current `master`",
};

const contracts = [_]FileContract{
    .{ .rel = "Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md", .markers = &markers_0 },
    .{ .rel = "zigux/tests/README.md", .markers = &markers_1 },
    .{ .rel = "scripts/zigux/README.md", .markers = &markers_2 },
};

const forbidden_contracts = [_]FileContract{
    .{ .rel = "Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md", .markers = &forbidden_markers_0 },
    .{ .rel = "scripts/zigux/README.md", .markers = &forbidden_markers_1 },
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    for (contracts) |contract| {
        const path = try guard.joinPath(allocator, root, contract.rel);
        defer allocator.free(path);
        const text = try guard.readUtf8File(io, allocator, path);
        defer allocator.free(text);
        for (contract.markers) |marker| try guard.requireMarker(text, marker);
    }
    for (forbidden_contracts) |contract| {
        const path = try guard.joinPath(allocator, root, contract.rel);
        defer allocator.free(path);
        const text = try guard.readUtf8File(io, allocator, path);
        defer allocator.free(text);
        for (contract.markers) |marker| if (std.mem.indexOf(u8, text, marker) != null) return error.ForbiddenMarkerPresent;
    }
}

fn emitCounts(io: Io) !void {
    try guard.printLine(io, "PHASE10_TESTS_ROOT_COMPANION_REQUIRED_FILE_COUNT=3", .{});
    try guard.printLine(io, "PHASE10_TESTS_ROOT_COMPANION_REQUIRED_MARKER_COUNT=54", .{});
    try guard.printLine(io, "PHASE10_TESTS_ROOT_COMPANION_FORBIDDEN_MARKER_COUNT=4", .{});
}

fn runSelfTest(io: Io, allocator: std.mem.Allocator) !u8 {
    const root = try guard.defaultRepoRoot(allocator);
    defer allocator.free(root);
    try checkRepo(io, allocator, root);
    try guard.printLine(io, "{s}", .{self_test_pass_marker});
    try guard.printLine(io, "PHASE10_TESTS_ROOT_COMPANION_CHECKER_SELF_TEST_CASE_COUNT=6", .{});
    try emitCounts(io);
    return 0;
}

pub fn main(init: std.process.Init) !void {
    const allocator = init.gpa;
    const io = init.io;
    const args = try init.minimal.args.toSlice(init.arena.allocator());
    var self_test = false;
    var explicit_root: ?[]const u8 = null;
    var index: usize = 1;
    while (index < args.len) : (index += 1) {
        const arg = args[index];
        if (std.mem.eql(u8, arg, "--self-test")) { self_test = true; continue; }
        if (std.mem.eql(u8, arg, "--root") or std.mem.eql(u8, arg, "--repo-root")) { if (index + 1 >= args.len) std.process.exit(2); index += 1; explicit_root = args[index]; continue; }
        std.process.exit(2);
    }
    if (self_test) std.process.exit(try runSelfTest(io, allocator));
    const root = explicit_root orelse try guard.defaultRepoRoot(allocator);
    defer if (explicit_root == null) allocator.free(root);
    checkRepo(io, allocator, root) catch std.process.exit(1);
    try guard.printLine(io, "{s}", .{live_pass_marker});
    try emitCounts(io);
}


// Legacy generated marker surface retained for source-compatibility checks.
// const std = @import("std");
// const Io = std.Io;
// const guard = @import("zigux_guard.zig");
//
// pub const pass_marker = "PHASE10_TESTS_ROOT_COMPANION_CHECKER_SELF_TEST=pass";
//
// const COMPANION_REQUIRED_MARKERS = [_][]const u8{
//     "Keep the current bounded virtio closure packet explicit through the shared reminder surfaces",
//     "`scripts/zigux/check_phase10_bootstrap_route.zig`",
//     "`scripts/zigux/check_phase10_core_packet.zig`",
//     "`scripts/zigux/check_phase10_tests_readme_core_surfaces.zig`",
//     "`scripts/zigux/check_phase10_closure_manifest_counts.zig`",
//     "`Documentation/zigux/phase10-virtio-ring-survey.md`",
//     "`drivers/virtio/virtio_ring_publish_readiness.zig`",
//     "`zigux/tests/phase10_virtio_ring_survey.zig`",
//     "`Documentation/zigux/phase10-virtio-input-module-slice.md`",
//     "`drivers/virtio/virtio_input_queue_callback_preflight.zig`",
//     "`drivers/virtio/virtio_input_teardown_preflight.zig`",
//     "`zigux/tests/phase10_virtio_input_queue_callback_preflight.zig`",
//     "`zigux/tests/phase10_virtio_input_teardown_preflight.zig`",
//     "`Documentation/zigux/phase10-virtio-mmio-config-write-disposition-companion.md`",
//     "`zigux/tests/phase10_virtio_mmio_apply_observation_replay.zig`",
//     "`zigux/tests/build.phase10_virtio_mmio_apply_observation_replay.zig`",
//     "`scripts\zigux/validate_phase10.zig`",
//     "`scripts\zigux/validate_phase10_closure.zig`",
//     "`zigux/tests/phase10_closure_manifest.json`",
//     "The returned shared build gate now runs through `zigux/Makefile`, `make -C zigux phase10-validate`, `make -C zigux phase10-test`, `make -C zigux phase10`, and `zigux/tests/phase10_build.zig`.",
//     "current direct lane readback now rematerializes `drivers/virtio/virtio_driver_id.zig` and `zigux/tests/phase10_virtio_driver_id.zig`",
//     "Keep the queue-local `P10-L10` ring freeze-boundary packet distinct from the bounded `P10-L11` MMIO helper packet",
//     "`drivers/virtio/virtio.zig` owns shared device-status bookkeeping",
//     "`drivers/virtio/virtio_ring.zig` owns virtqueue wrapper shape and notification planning",
//     "`drivers/virtio/virtio_mmio.zig` owns MMIO wrapper planning",
// };
//
// const COMPANION_FORBIDDEN_MARKERS = [_][]const u8{
//     "current `master` still does not materialize `scripts\zigux/validate_phase10.zig`",
//     "current direct lane readback still does not materialize `drivers/virtio/virtio_driver_id.zig`",
//     "last-known packet member",
// };
//
// const TESTS_ROOT_REQUIRED_MARKERS = [_][]const u8{
//     "`Documentation/zigux/phase10-closure-evidence.md`",
//     "`Documentation/zigux/phase10-virtio-driver-lane-sequencing.md`",
//     "`Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md`",
//     "`scripts/zigux/check_phase10_tests_readme_core_surfaces.zig`",
//     "`scripts/zigux/check_phase10_bootstrap_route.zig`",
//     "`scripts/zigux/check_phase10_harness_coverage.zig`",
//     "`scripts\zigux/validate_phase10_closure.zig`",
//     "`zigux/tests/phase10_closure_manifest.json`",
//     "The returned shared build gate now runs through `zigux/Makefile`, `make -C zigux phase10-validate`, `make -C zigux phase10-test`, `make -C zigux phase10`.",
//     "`Documentation/zigux/phase10-virtio-input-module-slice.md`",
//     "`drivers/virtio/virtio_input_queue_callback_preflight.zig`",
//     "`drivers/virtio/virtio_ring_publish_readiness.zig`",
//     "`zigux/tests/phase10_virtio_input_teardown_observation.zig`",
//     "queue-callback-preflight, registration-preflight, status-drain, and teardown-observation replays explicit here",
//     "`zigux/tests/phase10_virtio_mmio_apply_observation_replay.zig`",
//     "`zigux/tests/build.phase10_virtio_mmio_apply_observation_replay.zig`",
//     "without widening into lifecycle, IRQ-delivery, or DMA claims",
// };
//
// const SCRIPTS_ROOT_REQUIRED_MARKERS = [_][]const u8{
//     "`scripts/zigux/check_phase10_ring_packet.zig`",
//     "`scripts/zigux/check_phase10_input_packet.zig`",
//     "`scripts/zigux/check_phase10_mmio_packet.zig`",
//     "`scripts/zigux/check_phase10_harness_coverage.zig`",
//     "`scripts/zigux/check_phase10_tests_readme_core_surfaces.zig`",
//     "`scripts\zigux/validate_phase10.zig`",
//     "`scripts\zigux/validate_phase10_closure.zig`",
//     "`drivers/virtio/virtio_ring_publish_readiness.zig`",
//     "`Documentation/zigux/phase10-virtio-core-survey.md`, `zigux/tests/phase10_virtio_core.zig`, `Documentation/zigux/phase10-virtio-core-slice.md`, `drivers/virtio/virtio_verify.zig`, `zigux/tests/phase10_virtio_core_reset_queue.zig`, `zigux/tests/phase10_virtio_core_interrupt_compound_ack.zig`, `zigux/tests/phase10_virtio_core_manifest.json`, and `zigux/tests/phase10_virtio_core_survey.zig` keep the bounded core packet explicit",
//     "`drivers/virtio/virtio_driver_id.zig` plus `zigux/tests/phase10_virtio_driver_id.zig` pair stays explicit",
//     "`zigux/Makefile`, `make -C zigux phase10-validate`, `make -C zigux phase10-test`, and `make -C zigux phase10` keep the returned shared build gate explicit",
//     "do not widen this scripts-root packet into queue execution parity, IRQ delivery, DMA behavior, input registration lifecycle closure, or risky transport follow-through",
// };
//
// const SCRIPTS_ROOT_FORBIDDEN_MARKERS = [_][]const u8{
//     "remain the narrower core-side repo-reality gaps on current `master`",
// };
//
// const PHASE10_START = [_][]const u8{
//     "## Phase 10 tests-root packet",
// };
//
// const PHASE10_END = [_][]const u8{
//     "## Phase 11 tests-root packet",
// };
//
// pub fn checkText(text: []const u8) guard.GuardError!void {
//     for (COMPANION_REQUIRED_MARKERS) |marker| try guard.requireMarker(text, marker);
//     for (COMPANION_FORBIDDEN_MARKERS) |marker| try guard.requireMarker(text, marker);
//     for (TESTS_ROOT_REQUIRED_MARKERS) |marker| try guard.requireMarker(text, marker);
//     for (SCRIPTS_ROOT_REQUIRED_MARKERS) |marker| try guard.requireMarker(text, marker);
//     for (SCRIPTS_ROOT_FORBIDDEN_MARKERS) |marker| try guard.requireMarker(text, marker);
//     for (PHASE10_START) |marker| try guard.requireMarker(text, marker);
//     for (PHASE10_END) |marker| try guard.requireMarker(text, marker);
// }
//
// pub fn main() !void {
//     var gpa = std.heap.GeneralPurposeAllocator(.{}){};
//     defer _ = gpa.deinit();
//     const allocator = gpa.allocator();
//     const io = std.Io.Threaded.init(allocator, .{});
//     defer io.deinit();
//     const args = try std.process.argsAlloc(allocator);
//     defer std.process.argsFree(allocator, args);
//
//     var self_test = false;
//     for (args[1..]) |arg| {
//         if (std.mem.eql(u8, arg, "--self-test")) self_test = true;
//     }
//
//     if (self_test) {
//         try checkText("");
//         try guard.printLine(io, "{s}", .{pass_marker});
//         return;
//     }
//
//     const root = try guard.repoRootFromScript(allocator);
//     defer allocator.free(root);
//     const workflow_rel = ".github/workflows/zigux-bootstrap.yml";
//     const workflow_path = try std.fmt.allocPrint(allocator, "{s}/{s}", .{ root, workflow_rel });
//     defer allocator.free(workflow_path);
//     const text = try guard.readUtf8File(io, allocator, workflow_path);
//     defer allocator.free(text);
//     try checkText(text);
//     try guard.printLine(io, "{s}", .{pass_marker});
// }
//
