const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const tests = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("lane01_bootstrap_phase3_abi_contract.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });

    const run_tests = b.addRunArtifact(tests);
    run_tests.setCwd(b.path("../.."));

    const named_step = b.step(
        "lane01-bootstrap-phase3-abi-contract",
        "Run the Lane 01 Phase 3 ABI roadmap contract",
    );
    named_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the Lane 01 Phase 3 ABI roadmap contract");
    test_step.dependOn(&run_tests.step);
}
