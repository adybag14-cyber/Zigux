const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const contract_tests = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("phase9_freeze_map_study_boundaries_contract.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });
    const run_contract_tests = b.addRunArtifact(contract_tests);
    run_contract_tests.cwd = b.path("../..");

    const named_step = b.step(
        "phase9-freeze-map-study-boundaries-contract",
        "Run the Lane 02 Phase 9 freeze-map study-boundaries contract.",
    );
    named_step.dependOn(&run_contract_tests.step);

    const test_step = b.step("test", "Run the Lane 02 Phase 9 freeze-map study-boundaries contract.");
    test_step.dependOn(&run_contract_tests.step);

    b.default_step.dependOn(&run_contract_tests.step);
}
