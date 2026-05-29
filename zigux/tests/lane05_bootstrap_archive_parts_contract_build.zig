const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const contract_tests = b.addTest(.{
        .name = "lane05-bootstrap-archive-parts-contract-tests",
        .root_module = b.createModule(.{
            .root_source_file = b.path("lane05_bootstrap_archive_parts_contract.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });
    const run_contract_tests = b.addRunArtifact(contract_tests);
    run_contract_tests.setCwd(b.path("../.."));

    const contract_step = b.step(
        "lane05-bootstrap-archive-parts-contract",
        "Run the Lane 05 bootstrap archive-parts contract tests",
    );
    contract_step.dependOn(&run_contract_tests.step);

    const test_step = b.step("test", "Run Lane 05 bootstrap archive-parts contract tests");
    test_step.dependOn(&run_contract_tests.step);
}
