const std = @import("std");

const PhaseExpectation = struct {
    heading: []const u8,
    required_goal: []const u8,
    required_marker: []const u8,
};

const phase_expectations = [_]PhaseExpectation{
    .{
        .heading = "## Phase 1: Alpha Host-Side Helpers",
        .required_goal = "prove that Zig can live in-tree on low-risk host-side helper code",
        .required_marker = "tools/lib/bitmap.zig",
    },
    .{
        .heading = "## Phase 2: Toolchain and Kbuild Enablement",
        .required_goal = "make Zigux buildable, reproducible, and acceptable inside Linux-style workflows",
        .required_marker = "scripts/zigux/fixdep.zig",
    },
    .{
        .heading = "## Phase 3: ABI and Interop Substrate",
        .required_goal = "define the permanent C/Zigux boundary",
        .required_marker = "zigux/bindings/",
    },
    .{
        .heading = "## Phase 4: Differential Validation and Rollback",
        .required_goal = "make every future Zigux port measurable and reversible",
        .required_marker = "zigux/tests/atomic64_diff.zig",
    },
    .{
        .heading = "## Phase 5: Samples and Reference Patterns",
        .required_goal = "make approved Zigux idioms reviewable and repeatable",
        .required_marker = "samples/zigux/",
    },
    .{
        .heading = "## Phase 6: Greenfield Leaf Helpers",
        .required_goal = "allow low-risk new helper code in Zigux without taking runtime-core risk",
        .required_marker = "lib/bsearch.zig",
    },
    .{
        .heading = "## Phase 7: In-Kernel Leaf Libraries",
        .required_goal = "bring the first reusable runtime helper families into the product path",
        .required_marker = "lib/rbtree.zig",
    },
    .{
        .heading = "## Phase 8: Userspace-Adjacent Tooling Expansion",
        .required_goal = "prove Zigux inside serious repo-hosted tooling, not just tiny helpers",
        .required_marker = "tools/lib/bpf/zigux_segments/",
    },
    .{
        .heading = "## Phase 9: Runtime Pilot Modules",
        .required_goal = "enter runtime kernels through tests and samples, not production pressure",
        .required_marker = "zigux/tests/runtime_*",
    },
    .{
        .heading = "## Phase 10: Virtio and Lab Drivers",
        .required_goal = "prove the driver model on VM-friendly transports before touching harder hardware",
        .required_marker = "drivers/virtio/*.zig",
    },
    .{
        .heading = "## Phase 11: Simple Production Drivers",
        .required_goal = "move from lab drivers to bounded real hardware drivers with straightforward lifecycles",
        .required_marker = "drivers/watchdog/*.zig",
    },
    .{
        .heading = "## Phase 12: Complex Production Drivers and Heavy Helper Consumers",
        .required_goal = "take on high-value, high-risk drivers only after earlier proof",
        .required_marker = "drivers/net/virtio_net.zig",
    },
    .{
        .heading = "## Phase 13: Shared Subsystem Helpers",
        .required_goal = "port bounded helper layers shared across multiple runtime consumers",
        .required_marker = "fs/libfs.zig",
    },
    .{
        .heading = "## Phase 14: Core-Adjacent Bounded Internals",
        .required_goal = "study or wrap critical shared infrastructure without claiming premature parity",
        .required_marker = "kernel/workqueue_bridge.zig",
    },
    .{
        .heading = "## Phase 15: Full-Parity Blockers and Long-Term Governance",
        .required_goal = "govern the final mixed-language steady state honestly",
        .required_marker = "parity scorecard",
    },
};

fn readRoadmap() ![]u8 {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    return std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "../../zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md",
        std.testing.allocator,
        .limited(96 * 1024),
    );
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn markerIndex(haystack: []const u8, marker: []const u8) !usize {
    return std.mem.indexOf(u8, haystack, marker) orelse error.MissingRoadmapMarker;
}

test "lane 01 roadmap keeps the phase sequence bounded and ordered" {
    const roadmap = try readRoadmap();
    defer std.testing.allocator.free(roadmap);

    try expectContains(roadmap, "## Product Features by Phase");

    var previous_index: usize = try markerIndex(roadmap, "## Product Features by Phase");
    for (phase_expectations) |phase| {
        const current_index = try markerIndex(roadmap, phase.heading);
        try std.testing.expect(current_index > previous_index);
        try expectContains(roadmap, phase.required_goal);
        try expectContains(roadmap, phase.required_marker);
        previous_index = current_index;
    }

    const freeze_index = try markerIndex(roadmap, "## Freeze Map for Near- and Mid-Term Planning");
    try std.testing.expect(freeze_index > previous_index);
}

test "lane 01 roadmap keeps early helper work ahead of runtime and driver expansion" {
    const roadmap = try readRoadmap();
    defer std.testing.allocator.free(roadmap);

    const phase1_index = try markerIndex(roadmap, "## Phase 1: Alpha Host-Side Helpers");
    const phase3_index = try markerIndex(roadmap, "## Phase 3: ABI and Interop Substrate");
    const phase9_index = try markerIndex(roadmap, "## Phase 9: Runtime Pilot Modules");
    const phase10_index = try markerIndex(roadmap, "## Phase 10: Virtio and Lab Drivers");
    const phase14_index = try markerIndex(roadmap, "## Phase 14: Core-Adjacent Bounded Internals");
    const phase15_index = try markerIndex(roadmap, "## Phase 15: Full-Parity Blockers and Long-Term Governance");

    try std.testing.expect(phase1_index < phase3_index);
    try std.testing.expect(phase3_index < phase9_index);
    try std.testing.expect(phase9_index < phase10_index);
    try std.testing.expect(phase10_index < phase14_index);
    try std.testing.expect(phase14_index < phase15_index);

    try expectContains(roadmap, "Port leaf helpers before shared runtime helpers.");
    try expectContains(roadmap, "Port shared runtime helpers before drivers.");
    try expectContains(roadmap, "Port simple drivers before high-throughput queueing and DMA-heavy drivers.");
    try expectContains(roadmap, "Deep-core freeze is real.");
}

test "lane 01 roadmap keeps phase sequence anchored to live-state confirmation" {
    const roadmap = try readRoadmap();
    defer std.testing.allocator.free(roadmap);

    try expectContains(roadmap, "This roadmap remains the planning baseline for Zigux bootstrap sequencing and phase intent.");
    try expectContains(roadmap, "confirm the live repo tree, `Documentation/zigux/README.md`, and active lane notes before treating every later phase packet below as already materialized on `master`.");
    try expectContains(roadmap, "if a proposed Zigux task does not come with bounded scope, validation, rollback, and ownership, it is not ready for the product repo");
}
