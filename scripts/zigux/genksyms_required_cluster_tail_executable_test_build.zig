const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const cluster_tail_tests = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("genksyms_required_cluster_tail_executable_test.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });
    const run_cluster_tail_tests = b.addRunArtifact(cluster_tail_tests);

    const cluster_tail_step = b.step(
        "lane23-genksyms-required-cluster-tail-executable",
        "Run Lane 23 genksyms required cluster-tail executable proof",
    );
    cluster_tail_step.dependOn(&run_cluster_tail_tests.step);

    const test_step = b.step("test", "Run Lane 23 genksyms required cluster-tail executable proof");
    test_step.dependOn(&run_cluster_tail_tests.step);
    b.default_step.dependOn(&run_cluster_tail_tests.step);
}
