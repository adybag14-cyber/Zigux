const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const unit_tests = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("fixdep_target_dot_public_entry_test.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });

    const run_unit_tests = b.addRunArtifact(unit_tests);

    const named_step = b.step(
        "fixdep-target-dot-public-entry",
        "Run the fixdep target-dot public-entry proof",
    );
    named_step.dependOn(&run_unit_tests.step);

    const test_step = b.step("test", "Run fixdep target-dot public-entry tests");
    test_step.dependOn(&run_unit_tests.step);

    b.default_step.dependOn(&run_unit_tests.step);
}
