const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const tests = b.addTest(.{
        .name = "phase1-vsprintf-fixture-contract-test",
        .root_module = b.createModule(.{
            .root_source_file = b.path("phase1_vsprintf_fixture_contract.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });

    const run_tests = b.addRunArtifact(tests);
    const contract_step = b.step(
        "phase1-vsprintf-fixture-contract",
        "Run the focused Phase 1 vsprintf fixture contract",
    );
    contract_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the focused Phase 1 vsprintf fixture contract");
    test_step.dependOn(&run_tests.step);
}
