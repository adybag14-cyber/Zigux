const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const contract_module = b.createModule(.{
        .root_source_file = b.path("lane17_phase6_phase8_handoff_contract.zig"),
        .target = target,
        .optimize = optimize,
    });
    const contract_tests = b.addTest(.{
        .root_module = contract_module,
    });
    const run_contract_tests = b.addRunArtifact(contract_tests);
    run_contract_tests.setCwd(b.path("../.."));

    const contract_step = b.step(
        "lane17-phase6-phase8-handoff-contract",
        "Validate the Lane 17 Phase 6 workflow handoff into Phase 8 tooling routes",
    );
    contract_step.dependOn(&run_contract_tests.step);

    const test_step = b.step("test", "Run the Lane 17 Phase 6 to Phase 8 handoff contract");
    test_step.dependOn(&run_contract_tests.step);
}
