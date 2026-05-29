const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const string_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/string.zig"),
        .target = target,
        .optimize = optimize,
    });

    const contract_module = b.createModule(.{
        .root_source_file = b.path("phase1_string_sysfs_review_contract.zig"),
        .target = target,
        .optimize = optimize,
    });
    contract_module.addImport("string", string_module);

    const contract_tests = b.addTest(.{
        .name = "phase1-string-sysfs-review-contract-tests",
        .root_module = contract_module,
    });
    const run_contract_tests = b.addRunArtifact(contract_tests);

    const contract_step = b.step(
        "phase1-string-sysfs-review-contract",
        "Run the Phase 1 string sysfs review contract",
    );
    contract_step.dependOn(&run_contract_tests.step);

    const test_step = b.step("test", "Run the Phase 1 string sysfs review contract");
    test_step.dependOn(&run_contract_tests.step);
}
