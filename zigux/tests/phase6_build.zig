const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const base64_module = b.createModule(.{
        .root_source_file = b.path("../../lib/base64.zig"),
        .target = target,
        .optimize = optimize,
    });
    const base64_root_module = b.createModule(.{
        .root_source_file = b.path("phase6_base64.zig"),
        .target = target,
        .optimize = optimize,
    });
    base64_root_module.addImport("base64", base64_module);

    const bsearch_module = b.createModule(.{
        .root_source_file = b.path("../../lib/bsearch.zig"),
        .target = target,
        .optimize = optimize,
    });
    const bsearch_root_module = b.createModule(.{
        .root_source_file = b.path("phase6_bsearch.zig"),
        .target = target,
        .optimize = optimize,
    });
    bsearch_root_module.addImport("bsearch", bsearch_module);

    const bsearch_lower_bound_c_abi_root_module = b.createModule(.{
        .root_source_file = b.path("phase6_bsearch_lower_bound_c_abi.zig"),
        .target = target,
        .optimize = optimize,
    });
    bsearch_lower_bound_c_abi_root_module.addImport("bsearch", bsearch_module);

    const bsearch_c_abi_budget_root_module = b.createModule(.{
        .root_source_file = b.path("phase6_bsearch_c_abi_budget.zig"),
        .target = target,
        .optimize = optimize,
    });
    bsearch_c_abi_budget_root_module.addImport("bsearch", bsearch_module);

    const base64_tests = b.addTest(.{
        .name = "phase6-base64-tests",
        .root_module = base64_root_module,
    });
    const run_base64_tests = b.addRunArtifact(base64_tests);
    run_base64_tests.skip_foreign_checks = true;

    const bsearch_tests = b.addTest(.{
        .name = "phase6-bsearch-tests",
        .root_module = bsearch_root_module,
    });
    const run_bsearch_tests = b.addRunArtifact(bsearch_tests);
    run_bsearch_tests.skip_foreign_checks = true;

    const bsearch_lower_bound_c_abi_tests = b.addTest(.{
        .name = "phase6-bsearch-lower-bound-c-abi-tests",
        .root_module = bsearch_lower_bound_c_abi_root_module,
    });
    const run_bsearch_lower_bound_c_abi_tests = b.addRunArtifact(bsearch_lower_bound_c_abi_tests);
    run_bsearch_lower_bound_c_abi_tests.skip_foreign_checks = true;

    const bsearch_c_abi_budget_tests = b.addTest(.{
        .name = "phase6-bsearch-c-abi-budget-tests",
        .root_module = bsearch_c_abi_budget_root_module,
    });
    const run_bsearch_c_abi_budget_tests = b.addRunArtifact(bsearch_c_abi_budget_tests);
    run_bsearch_c_abi_budget_tests.skip_foreign_checks = true;

    const bsearch_test_step = b.step("phase6-bsearch-test", "Run Phase 6 bsearch helper tests");
    bsearch_test_step.dependOn(&run_bsearch_tests.step);
    bsearch_test_step.dependOn(&run_bsearch_lower_bound_c_abi_tests.step);
    bsearch_test_step.dependOn(&run_bsearch_c_abi_budget_tests.step);

    const test_step = b.step("test", "Run Phase 6 helper tests");
    test_step.dependOn(&run_base64_tests.step);
    test_step.dependOn(&run_bsearch_tests.step);
    test_step.dependOn(&run_bsearch_lower_bound_c_abi_tests.step);
    test_step.dependOn(&run_bsearch_c_abi_budget_tests.step);
}
