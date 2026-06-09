const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const root_module = b.createModule(.{
        .root_source_file = b.path("lane02_phase8_docs_root_addendum_contract.zig"),
        .target = target,
        .optimize = optimize,
    });

    const unit_tests = b.addTest(.{
        .name = "lane02-phase8-docs-root-addendum-contract-tests",
        .root_module = root_module,
    });
    const run_unit_tests = b.addRunArtifact(unit_tests);

    const contract_step = b.step(
        "lane02-phase8-docs-root-addendum-contract",
        "Run the Lane 02 Phase 8 docs-root addendum contract",
    );
    contract_step.dependOn(&run_unit_tests.step);

    const test_step = b.step("test", "Run the Lane 02 Phase 8 docs-root addendum contract");
    test_step.dependOn(&run_unit_tests.step);
    b.default_step.dependOn(test_step);
}
