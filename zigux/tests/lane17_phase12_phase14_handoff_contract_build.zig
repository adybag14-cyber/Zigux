const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const contract_tests = b.addTest(.{
        .name = "lane17-phase12-phase14-handoff-contract-tests",
        .root_module = b.createModule(.{
            .root_source_file = b.path("lane17_phase12_phase14_handoff_contract.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });

    const run_contract_tests = b.addRunArtifact(contract_tests);
    run_contract_tests.setCwd(b.path("../.."));

    const contract_step = b.step(
        "lane17-phase12-phase14-handoff-contract",
        "Run the Lane 17 Phase 12 to Phase 14 workflow handoff contract",
    );
    contract_step.dependOn(&run_contract_tests.step);

    const test_step = b.step("test", "Run the Lane 17 Phase 12 to Phase 14 workflow handoff contract");
    test_step.dependOn(&run_contract_tests.step);
}
