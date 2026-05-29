const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});
    const contract_module = b.createModule(.{
        .root_source_file = b.path("lane05_archive_parts_variable_chunk_contract.zig"),
        .target = target,
        .optimize = optimize,
    });

    const contract_tests = b.addTest(.{
        .name = "lane05-archive-parts-variable-chunk-contract-tests",
        .root_module = contract_module,
    });

    const run_contract_tests = b.addRunArtifact(contract_tests);

    const test_step = b.step("test", "Run the Lane 05 archive-parts variable-chunk contract tests.");
    test_step.dependOn(&run_contract_tests.step);

    b.default_step.dependOn(test_step);
}
