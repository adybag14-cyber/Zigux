const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const libbpf_segment_verify_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/bpf/zigux_segments/verify.zig"),
        .target = target,
        .optimize = optimize,
    });

    const libbpf_segment_verify_tests = b.addTest(.{
        .name = "phase8-libbpf-segment-verify-tests",
        .root_module = libbpf_segment_verify_module,
    });

    const run_libbpf_segment_verify_tests = b.addRunArtifact(libbpf_segment_verify_tests);
    const test_step = b.step("test", "Run focused Phase 8 libbpf segment verify build");
    test_step.dependOn(&run_libbpf_segment_verify_tests.step);
}
