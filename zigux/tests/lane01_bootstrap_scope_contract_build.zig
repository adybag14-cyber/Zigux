const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const unit_tests = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("lane01_bootstrap_scope_contract.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });

    const run_unit_tests = b.addRunArtifact(unit_tests);
    run_unit_tests.setCwd(b.path("../.."));

    const contract_step = b.step("lane01-bootstrap-scope-contract", "Run Lane 01 bootstrap scope contract");
    contract_step.dependOn(&run_unit_tests.step);

    const test_step = b.step("test", "Run Lane 01 bootstrap scope contract");
    test_step.dependOn(&run_unit_tests.step);
}
