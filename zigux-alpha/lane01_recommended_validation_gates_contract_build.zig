const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const contract_tests = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("lane01_recommended_validation_gates_contract.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });
    const run_contract = b.addRunArtifact(contract_tests);

    const contract_step = b.step(
        "lane01-recommended-validation-gates-contract",
        "Run the Lane 01 recommended validation gates roadmap contract",
    );
    contract_step.dependOn(&run_contract.step);

    const test_step = b.step("test", "Run Lane 01 recommended validation gates contract tests");
    test_step.dependOn(&run_contract.step);
}
