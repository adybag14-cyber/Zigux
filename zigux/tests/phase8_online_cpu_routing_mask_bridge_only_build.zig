const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});
    const root_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/bpf/zigux_segments/online_cpu_routing_mask_bridge_verify.zig"),
        .target = target,
        .optimize = optimize,
    });

    const unit_tests = b.addTest(.{
        .name = "phase8-online-cpu-routing-mask-bridge-tests",
        .root_module = root_module,
    });

    const run_unit_tests = b.addRunArtifact(unit_tests);
    const test_step = b.step("test", "Run focused Phase 8 online-cpu routing mask-bridge tests.");
    test_step.dependOn(&run_unit_tests.step);
}
