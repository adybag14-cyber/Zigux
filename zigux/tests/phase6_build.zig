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

    const base64_perf_root_module = b.createModule(.{
        .root_source_file = b.path("phase6_base64_perf.zig"),
        .target = target,
        .optimize = optimize,
    });
    base64_perf_root_module.addImport("base64", base64_module);

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
    const bsearch_index_range_accessors_root_module = b.createModule(.{
        .root_source_file = b.path("phase6_bsearch_index_range_accessors.zig"),
        .target = target,
        .optimize = optimize,
    });
    bsearch_index_range_accessors_root_module.addImport("bsearch", bsearch_module);

    const bsearch_perf_root_module = b.createModule(.{
        .root_source_file = b.path("phase6_bsearch_perf.zig"),
        .target = target,
        .optimize = optimize,
    });
    bsearch_perf_root_module.addImport("bsearch", bsearch_module);

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

    const checksum_module = b.createModule(.{
        .root_source_file = b.path("../../lib/checksum.zig"),
        .target = target,
        .optimize = optimize,
    });
    const checksum_root_module = b.createModule(.{
        .root_source_file = b.path("phase6_checksum.zig"),
        .target = target,
        .optimize = optimize,
    });
    checksum_root_module.addImport("checksum", checksum_module);

    const checksum_perf_root_module = b.createModule(.{
        .root_source_file = b.path("phase6_checksum_perf.zig"),
        .target = target,
        .optimize = optimize,
    });
    checksum_perf_root_module.addImport("checksum", checksum_module);

    const hexdump_module = b.createModule(.{
        .root_source_file = b.path("../../lib/hexdump.zig"),
        .target = target,
        .optimize = optimize,
    });
    const hexdump_vectors_module = b.createModule(.{
        .root_source_file = b.path("fixtures/phase6_hexdump_vectors.zig"),
        .target = target,
        .optimize = optimize,
    });
    const hexdump_root_module = b.createModule(.{
        .root_source_file = b.path("phase6_hexdump.zig"),
        .target = target,
        .optimize = optimize,
    });
    hexdump_root_module.addImport("hexdump", hexdump_module);
    hexdump_root_module.addImport("phase6_hexdump_vectors", hexdump_vectors_module);

    const hexdump_perf_root_module = b.createModule(.{
        .root_source_file = b.path("phase6_hexdump_perf.zig"),
        .target = target,
        .optimize = optimize,
    });
    hexdump_perf_root_module.addImport("hexdump", hexdump_module);
    hexdump_perf_root_module.addImport("phase6_hexdump_vectors", hexdump_vectors_module);
    const hexdump_perf_matrix_root_module = b.createModule(.{
        .root_source_file = b.path("phase6_hexdump_perf_matrix.zig"),
        .target = target,
        .optimize = optimize,
    });
    hexdump_perf_matrix_root_module.addImport("hexdump", hexdump_module);
    hexdump_perf_matrix_root_module.addImport("phase6_hexdump_vectors", hexdump_vectors_module);

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

    const bsearch_index_range_accessors_tests = b.addTest(.{
        .name = "phase6-bsearch-index-range-accessors-tests",
        .root_module = bsearch_index_range_accessors_root_module,
    });
    const run_bsearch_index_range_accessors_tests = b.addRunArtifact(bsearch_index_range_accessors_tests);
    run_bsearch_index_range_accessors_tests.skip_foreign_checks = true;

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

    const checksum_tests = b.addTest(.{
        .name = "phase6-checksum-tests",
        .root_module = checksum_root_module,
    });
    const run_checksum_tests = b.addRunArtifact(checksum_tests);
    run_checksum_tests.skip_foreign_checks = true;
    const checksum_perf_matrix_tests = b.addTest(.{
        .name = "phase6-checksum-perf-matrix-tests",
        .root_module = checksum_perf_root_module,
    });
    const run_checksum_perf_matrix_tests = b.addRunArtifact(checksum_perf_matrix_tests);
    run_checksum_perf_matrix_tests.skip_foreign_checks = true;

    const hexdump_tests = b.addTest(.{
        .name = "phase6-hexdump-tests",
        .root_module = hexdump_root_module,
    });
    const run_hexdump_tests = b.addRunArtifact(hexdump_tests);
    run_hexdump_tests.skip_foreign_checks = true;
    const hexdump_perf_matrix_tests = b.addTest(.{
        .name = "phase6-hexdump-perf-matrix-tests",
        .root_module = hexdump_perf_matrix_root_module,
    });
    const run_hexdump_perf_matrix_tests = b.addRunArtifact(hexdump_perf_matrix_tests);
    run_hexdump_perf_matrix_tests.skip_foreign_checks = true;

    const base64_perf = b.addExecutable(.{
        .name = "phase6-base64-perf",
        .root_module = base64_perf_root_module,
    });
    const run_base64_perf = b.addRunArtifact(base64_perf);
    run_base64_perf.skip_foreign_checks = true;

    const bsearch_perf = b.addExecutable(.{
        .name = "phase6-bsearch-perf",
        .root_module = bsearch_perf_root_module,
    });
    const run_bsearch_perf = b.addRunArtifact(bsearch_perf);
    run_bsearch_perf.skip_foreign_checks = true;

    const checksum_perf = b.addExecutable(.{
        .name = "phase6-checksum-perf",
        .root_module = checksum_perf_root_module,
    });
    const run_checksum_perf = b.addRunArtifact(checksum_perf);
    run_checksum_perf.skip_foreign_checks = true;

    const hexdump_perf = b.addExecutable(.{
        .name = "phase6-hexdump-perf",
        .root_module = hexdump_perf_root_module,
    });
    const run_hexdump_perf = b.addRunArtifact(hexdump_perf);
    run_hexdump_perf.skip_foreign_checks = true;

    const base64_test_step = b.step("phase6-base64-test", "Run Phase 6 base64 helper tests");
    base64_test_step.dependOn(&run_base64_tests.step);
    const base64_review_step = b.step("phase6-base64-review", "Run Phase 6 base64 helper review preflight");
    base64_review_step.dependOn(&run_base64_tests.step);
    base64_review_step.dependOn(&run_base64_perf.step);

    const bsearch_test_step = b.step("phase6-bsearch-test", "Run Phase 6 bsearch helper tests");
    bsearch_test_step.dependOn(&run_bsearch_tests.step);
    bsearch_test_step.dependOn(&run_bsearch_index_range_accessors_tests.step);
    bsearch_test_step.dependOn(&run_bsearch_lower_bound_c_abi_tests.step);
    bsearch_test_step.dependOn(&run_bsearch_c_abi_budget_tests.step);

    const checksum_test_step = b.step("phase6-checksum-test", "Run Phase 6 checksum helper tests");
    checksum_test_step.dependOn(&run_checksum_tests.step);
    checksum_test_step.dependOn(&run_checksum_perf_matrix_tests.step);
    const checksum_perf_matrix_test_step = b.step(
        "phase6-checksum-perf-matrix-test",
        "Run Phase 6 checksum perf matrix preflight",
    );
    checksum_perf_matrix_test_step.dependOn(&run_checksum_perf_matrix_tests.step);

    const hexdump_test_step = b.step("phase6-hexdump-test", "Run Phase 6 hexdump helper tests");
    hexdump_test_step.dependOn(&run_hexdump_tests.step);
    hexdump_test_step.dependOn(&run_hexdump_perf_matrix_tests.step);
    const hexdump_review_step = b.step("phase6-hexdump-review", "Run Phase 6 hexdump perf-matrix review preflight");
    hexdump_review_step.dependOn(&run_hexdump_perf_matrix_tests.step);
    const hexdump_perf_matrix_test_step = b.step(
        "phase6-hexdump-perf-matrix-test",
        "Run Phase 6 hexdump perf matrix preflight",
    );
    hexdump_perf_matrix_test_step.dependOn(&run_hexdump_perf_matrix_tests.step);

    const base64_perf_step = b.step("phase6-base64-perf", "Run Phase 6 base64 helper perf gate");
    base64_perf_step.dependOn(&run_base64_perf.step);

    const bsearch_perf_step = b.step("phase6-bsearch-perf", "Run Phase 6 bsearch helper perf gate");
    bsearch_perf_step.dependOn(&run_bsearch_perf.step);

    const checksum_perf_step = b.step("phase6-checksum-perf", "Run Phase 6 checksum helper perf gate");
    checksum_perf_step.dependOn(&run_checksum_perf.step);

    const hexdump_perf_step = b.step("phase6-hexdump-perf", "Run Phase 6 hexdump helper perf gate");
    hexdump_perf_step.dependOn(&run_hexdump_perf.step);

    const test_step = b.step("test", "Run Phase 6 helper tests");
    test_step.dependOn(&run_base64_tests.step);
    test_step.dependOn(&run_bsearch_tests.step);
    test_step.dependOn(&run_bsearch_index_range_accessors_tests.step);
    test_step.dependOn(&run_bsearch_lower_bound_c_abi_tests.step);
    test_step.dependOn(&run_bsearch_c_abi_budget_tests.step);
    test_step.dependOn(&run_checksum_tests.step);
    test_step.dependOn(&run_checksum_perf_matrix_tests.step);
    test_step.dependOn(&run_hexdump_tests.step);
    test_step.dependOn(&run_hexdump_perf_matrix_tests.step);
}
