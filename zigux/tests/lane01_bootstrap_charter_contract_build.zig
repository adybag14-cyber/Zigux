const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const module = b.createModule(.{
        .root_source_file = b.path("lane01_bootstrap_charter_contract.zig"),
        .target = target,
        .optimize = optimize,
    });

    const unit_tests = b.addTest(.{
        .name = "lane01-bootstrap-charter-contract",
        .root_module = module,
    });

    const run_unit_tests = b.addRunArtifact(unit_tests);
    run_unit_tests.setCwd(b.path("../.."));

    const contract = b.step(
        "lane01-bootstrap-charter-contract",
        "Run the focused Lane 01 bootstrap charter contract",
    );
    contract.dependOn(&run_unit_tests.step);

    const test_step = b.step("test", "Run the focused Lane 01 bootstrap charter contract");
    test_step.dependOn(&run_unit_tests.step);
}
