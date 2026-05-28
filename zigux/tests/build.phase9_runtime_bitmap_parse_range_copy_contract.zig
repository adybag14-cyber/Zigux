const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const bitmap_view_module = b.createModule(.{
        .root_source_file = b.path("../helpers/bitmap_view.zig"),
        .target = target,
        .optimize = optimize,
    });

    const runtime_bitmap_sample_module = b.createModule(.{
        .root_source_file = b.path("../../samples/zigux/runtime_bitmap.zig"),
        .target = target,
        .optimize = optimize,
    });
    runtime_bitmap_sample_module.addImport("bitmap_view", bitmap_view_module);

    const runtime_bitmap_parse_range_copy_contract_module = b.createModule(.{
        .root_source_file = b.path("../../samples/zigux/runtime_bitmap_parse_range_copy_contract.zig"),
        .target = target,
        .optimize = optimize,
    });
    runtime_bitmap_parse_range_copy_contract_module.addImport(
        "runtime_bitmap_sample",
        runtime_bitmap_sample_module,
    );

    const runtime_bitmap_parse_range_copy_contract_tests = b.addTest(.{
        .name = "phase9-runtime-bitmap-parse-range-copy-contract-tests",
        .root_module = runtime_bitmap_parse_range_copy_contract_module,
    });

    const run_runtime_bitmap_parse_range_copy_contract_tests = b.addRunArtifact(
        runtime_bitmap_parse_range_copy_contract_tests,
    );

    const phase9_runtime_bitmap_parse_range_copy_contract = b.step(
        "phase9-runtime-bitmap-parse-range-copy-contract-tests",
        "Run the Phase 9 runtime bitmap parse, range-mutation, and copy contract tests.",
    );
    phase9_runtime_bitmap_parse_range_copy_contract.dependOn(
        &run_runtime_bitmap_parse_range_copy_contract_tests.step,
    );
}
