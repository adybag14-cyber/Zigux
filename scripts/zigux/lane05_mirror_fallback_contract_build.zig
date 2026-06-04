const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const contract_module = b.createModule(.{
        .root_source_file = b.path("lane05_mirror_fallback_contract.zig"),
        .target = target,
        .optimize = optimize,
    });

    const unit_tests = b.addTest(.{
        .root_module = contract_module,
    });

    const run_tests = b.addRunArtifact(unit_tests);

    const contract_step = b.step(
        "lane05-mirror-fallback-contract",
        "Run the Lane 05 bootstrap mirror fallback contract",
    );
    contract_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run Lane 05 bootstrap mirror fallback contract tests");
    test_step.dependOn(&run_tests.step);
}
