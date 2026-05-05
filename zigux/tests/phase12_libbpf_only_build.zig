const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const phase12_libbpf_segments_module = b.createModule(.{
        .root_source_file = b.path("phase12_libbpf_segments.zig"),
        .target = target,
        .optimize = optimize,
    });

    const libbpf_cpu_mask_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/bpf/zigux_segments/cpu_mask.zig"),
        .target = target,
        .optimize = optimize,
    });
    const libbpf_type_names_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/bpf/zigux_segments/type_names.zig"),
        .target = target,
        .optimize = optimize,
    });
    const libbpf_logging_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/bpf/zigux_segments/logging.zig"),
        .target = target,
        .optimize = optimize,
    });
    const libbpf_pin_path_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/bpf/zigux_segments/pin_path.zig"),
        .target = target,
        .optimize = optimize,
    });
    const libbpf_perf_buffer_poll_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/bpf/zigux_segments/perf_buffer_poll.zig"),
        .target = target,
        .optimize = optimize,
    });

    const phase12_libbpf_reviewability_module = b.createModule(.{
        .root_source_file = b.path("phase12_libbpf_reviewability.zig"),
        .target = target,
        .optimize = optimize,
    });
    phase12_libbpf_reviewability_module.addImport("cpu_mask", libbpf_cpu_mask_module);
    phase12_libbpf_reviewability_module.addImport("bpf_type_names", libbpf_type_names_module);
    phase12_libbpf_reviewability_module.addImport("logging", libbpf_logging_module);
    phase12_libbpf_reviewability_module.addImport("pin_path", libbpf_pin_path_module);
    phase12_libbpf_reviewability_module.addImport("perf_buffer_poll", libbpf_perf_buffer_poll_module);

    const phase12_libbpf_segments_tests = b.addTest(.{
        .name = "phase12-libbpf-segment-survey-tests",
        .root_module = phase12_libbpf_segments_module,
    });
    const run_phase12_libbpf_segments_tests = b.addRunArtifact(phase12_libbpf_segments_tests);

    const phase12_libbpf_reviewability_tests = b.addTest(.{
        .name = "phase12-libbpf-reviewability-tests",
        .root_module = phase12_libbpf_reviewability_module,
    });
    const run_phase12_libbpf_reviewability_tests = b.addRunArtifact(phase12_libbpf_reviewability_tests);

    const test_step = b.step("test", "Run focused Phase 12 libbpf survey and reviewability tests");
    test_step.dependOn(&run_phase12_libbpf_segments_tests.step);
    test_step.dependOn(&run_phase12_libbpf_reviewability_tests.step);
}
