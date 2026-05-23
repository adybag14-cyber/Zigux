const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});
    const matrix_module = b.createModule(.{
        .root_source_file = b.path("phase14_skbuff_compile_shard_matrix.zig"),
        .target = target,
        .optimize = optimize,
    });

    const matrix_tests = b.addTest(.{
        .name = "phase14-skbuff-compile-shard-matrix-tests",
        .root_module = matrix_module,
    });
    const run_matrix_tests = b.addRunArtifact(matrix_tests);

    const matrix_step = b.step(
        "phase14-skbuff-compile-shard-matrix",
        "Run the standalone Phase 14 skbuff compile shard matrix guard",
    );
    matrix_step.dependOn(&run_matrix_tests.step);
}
