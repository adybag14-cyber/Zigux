const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const cpu_mask_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/bpf/zigux_segments/cpu_mask.zig"),
        .target = target,
        .optimize = optimize,
    });
    const type_names_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/bpf/zigux_segments/type_names.zig"),
        .target = target,
        .optimize = optimize,
    });
    const logging_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/bpf/zigux_segments/logging.zig"),
        .target = target,
        .optimize = optimize,
    });
    const pin_path_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/bpf/zigux_segments/pin_path.zig"),
        .target = target,
        .optimize = optimize,
    });
    const perf_buffer_poll_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/bpf/zigux_segments/perf_buffer_poll.zig"),
        .target = target,
        .optimize = optimize,
    });
    const online_cpu_routing_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/bpf/zigux_segments/online_cpu_routing.zig"),
        .target = target,
        .optimize = optimize,
    });

    const reviewability_root_module = b.createModule(.{
        .root_source_file = b.path("phase12_libbpf_reviewability.zig"),
        .target = target,
        .optimize = optimize,
    });
    reviewability_root_module.addImport("cpu_mask", cpu_mask_module);
    reviewability_root_module.addImport("bpf_type_names", type_names_module);
    reviewability_root_module.addImport("logging", logging_module);
    reviewability_root_module.addImport("pin_path", pin_path_module);
    reviewability_root_module.addImport("perf_buffer_poll", perf_buffer_poll_module);
    reviewability_root_module.addImport("online_cpu_routing", online_cpu_routing_module);

    const reviewability_tests = b.addTest(.{
        .name = "phase12-libbpf-reviewability-tests",
        .root_module = reviewability_root_module,
    });
    const run_reviewability_tests = b.addRunArtifact(reviewability_tests);

    const test_step = b.step(
        "test",
        "Run the Phase 12 libbpf reviewability tests",
    );
    test_step.dependOn(&run_reviewability_tests.step);
}
