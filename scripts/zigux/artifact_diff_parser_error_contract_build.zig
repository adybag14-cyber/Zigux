const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const contract = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("artifact_diff_parser_error_contract.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });

    const run_contract = b.addRunArtifact(contract);
    const contract_step = b.step(
        "artifact-diff-parser-error-contract",
        "Run the artifact diff parser and error surface contract",
    );
    contract_step.dependOn(&run_contract.step);

    const test_step = b.step("test", "Run artifact diff parser/error contract tests");
    test_step.dependOn(&run_contract.step);
}
