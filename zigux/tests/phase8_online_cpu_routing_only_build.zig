const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const online_cpu_routing_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/bpf/zigux_segments/online_cpu_routing.zig"),
        .target = target,
        .optimize = optimize,
    });

    const online_cpu_routing_tests = b.addTest(.{
        .name = "phase8-online-cpu-routing-tests",
        .root_module = online_cpu_routing_module,
    });

    const run_online_cpu_routing_tests = b.addRunArtifact(online_cpu_routing_tests);

    const test_step = b.step("test", "Run focused Phase 8 online CPU routing tests");
    test_step.dependOn(&run_online_cpu_routing_tests.step);
}
