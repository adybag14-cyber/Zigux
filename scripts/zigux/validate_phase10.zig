const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE10_VALIDATION_CORE_PACKET=pass";
pub const self_test_pass_marker = "PHASE10_VALIDATE_SELF_TEST=pass";

const CHECKS = [_][]const u8{
    "CheckSpecphase10-bootstrap-routescripts\\zigux/check_phase10_bootstrap_route.zig",
    "CheckSpecphase10-core-packetscripts\\zigux/check_phase10_core_packet.zig",
    "CheckSpecphase10-shared-freeze-boundaryscripts\\zigux/check_phase10_shared_freeze_boundary.zig",
    "CheckSpecphase10-ring-packetscripts\\zigux/check_phase10_ring_packet.zig",
    "CheckSpecphase10-ring-manifest-destinationsscripts\\zigux/check_phase10_ring_manifest_destinations.zig",
    "CheckSpecphase10-input-packetscripts\\zigux/check_phase10_input_packet.zig",
    "CheckSpecphase10-mmio-packetscripts\\zigux/check_phase10_mmio_packet.zig",
    "CheckSpecphase10-harness-coveragescripts\\zigux/check_phase10_harness_coverage.zig",
    "CheckSpecphase10-tests-readme-core-surfacesscripts\\zigux/check_phase10_tests_readme_core_surfaces.zig",
    "CheckSpecphase10-closure-manifest-countsscripts\\zigux/check_phase10_closure_manifest_counts.zig",
    "CheckSpecphase10-closurescripts\\zigux/validate_phase10_closure.zig",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_checks_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_checks_path);
    const text_checks = try guard.readUtf8File(io, allocator, text_checks_path);
    defer allocator.free(text_checks);
    for (CHECKS) |marker| try guard.requireMarker(text_checks, marker);
}

fn runSelfTest(io: Io, allocator: std.mem.Allocator) !u8 {
    try checkRepo(io, allocator, try guard.defaultRepoRoot(allocator));
    try guard.printLine(io, "{s}", .{self_test_pass_marker});
    return 0;
}

pub fn main(init: std.process.Init) !void {
    const allocator = init.gpa;
    const io = init.io;
    const args = try init.minimal.args.toSlice(allocator);

    var self_test = false;
    var explicit_root: ?[]const u8 = null;
    var index: usize = 1;
    while (index < args.len) : (index += 1) {
        const arg = args[index];
        if (std.mem.eql(u8, arg, "--self-test")) {
            self_test = true;
            continue;
        }
        if (std.mem.eql(u8, arg, "--root")) {
            if (index + 1 >= args.len) std.process.exit(2);
            index += 1;
            explicit_root = args[index];
            continue;
        }
    }

    const root = explicit_root orelse try guard.repoRootFromScript(allocator);
    defer if (explicit_root == null) allocator.free(root);

    if (self_test) {
        std.process.exit(try runSelfTest(io, allocator));
    }

    checkRepo(io, allocator, root) catch {
        std.process.exit(1);
    };
    try guard.printLine(io, "{s}", .{live_pass_marker});
}
