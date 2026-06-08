const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const contract_tests = b.addTest(.{
        .name = "lane05-setup-cleanup-handoff-contract-tests",
        .root_module = b.createModule(.{
            .root_source_file = b.path("lane05_setup_cleanup_handoff_contract.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });

    const run_tests = b.addRunArtifact(contract_tests);

    const contract_step = b.step(
        "lane05-setup-cleanup-handoff-contract",
        "Run the Lane 05 setup cleanup handoff workflow contract.",
    );
    contract_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the Lane 05 setup cleanup handoff workflow contract.");
    test_step.dependOn(&run_tests.step);

    b.default_step.dependOn(&run_tests.step);
}
