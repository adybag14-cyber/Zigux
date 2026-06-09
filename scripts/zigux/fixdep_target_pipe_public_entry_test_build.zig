const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const unit_tests = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("fixdep_target_pipe_public_entry_test.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });
    const run_unit_tests = b.addRunArtifact(unit_tests);

    const proof_step = b.step(
        "fixdep-target-pipe-public-entry",
        "Run the fixdep target-pipe public-entry proof",
    );
    proof_step.dependOn(&run_unit_tests.step);

    const test_step = b.step("test", "Run the fixdep target-pipe public-entry tests");
    test_step.dependOn(&run_unit_tests.step);

    b.default_step.dependOn(&run_unit_tests.step);
}
