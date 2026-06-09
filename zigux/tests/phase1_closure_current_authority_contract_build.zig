const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase1_closure_current_authority_contract.zig"),
        .target = target,
        .optimize = optimize,
    });

    const unit_tests = b.addTest(.{
        .root_module = root_module,
    });
    const run_unit_tests = b.addRunArtifact(unit_tests);

    const named_step = b.step(
        "phase1-closure-current-authority-contract",
        "Run the Phase 1 closure current-authority contract",
    );
    named_step.dependOn(&run_unit_tests.step);

    const test_step = b.step("test", "Run the Phase 1 closure current-authority contract");
    test_step.dependOn(&run_unit_tests.step);

    b.default_step.dependOn(&run_unit_tests.step);
}
