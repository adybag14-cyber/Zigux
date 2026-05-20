const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const libbpf_segments_root_module = b.createModule(.{
        .root_source_file = b.path("phase8_libbpf_segments.zig"),
        .target = target,
        .optimize = optimize,
    });

    const libbpf_segments_tests = b.addTest(.{
        .name = "phase8-libbpf-segment-tests",
        .root_module = libbpf_segments_root_module,
    });

    const run_libbpf_segments_tests = b.addRunArtifact(libbpf_segments_tests);

    const test_step = b.step("test", "Run focused Phase 8 libbpf segment survey tests");
    test_step.dependOn(&run_libbpf_segments_tests.step);
}
