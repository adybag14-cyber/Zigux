const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const abi_bindings_path = b.option(
        []const u8,
        "abi-bindings-path",
        "Path to the ABI bindings source",
    ) orelse "../bindings/abi.zig";
    const layout_assert_path = b.option(
        []const u8,
        "layout-assert-path",
        "Path to the layout assertion helper source",
    ) orelse "../helpers/layout_assert.zig";

    const abi_bindings = b.createModule(.{
        .root_source_file = b.path(abi_bindings_path),
        .target = target,
        .optimize = optimize,
    });
    const layout_assert = b.createModule(.{
        .root_source_file = b.path(layout_assert_path),
        .target = target,
        .optimize = optimize,
    });
    layout_assert.addImport("abi_bindings", abi_bindings);

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase3_abi_layout_assert_core_contract.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addImport("abi_bindings", abi_bindings);
    root_module.addImport("layout_assert", layout_assert);

    const tests = b.addTest(.{
        .name = "phase3-abi-layout-assert-core-contract",
        .root_module = root_module,
    });
    const run_tests = b.addRunArtifact(tests);

    const contract_step = b.step(
        "phase3-abi-layout-assert-core-contract",
        "Run the Phase 3 core ABI layout assertion contract",
    );
    contract_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the Phase 3 core ABI layout assertion contract");
    test_step.dependOn(&run_tests.step);
    b.default_step.dependOn(&run_tests.step);
}
