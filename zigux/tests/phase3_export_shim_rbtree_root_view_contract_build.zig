const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});
    const export_shim_path = b.option(
        []const u8,
        "export-shim-path",
        "Path to the Phase 3 export shim module",
    ) orelse "../kernel/export_shim.zig";

    const export_shim_module = b.createModule(.{
        .root_source_file = b.path(export_shim_path),
        .target = target,
        .optimize = optimize,
    });

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase3_export_shim_rbtree_root_view_contract.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addImport("export_shim_binding", export_shim_module);

    const tests = b.addTest(.{
        .name = "phase3-export-shim-rbtree-root-view-contract",
        .root_module = root_module,
    });

    const run_tests = b.addRunArtifact(tests);
    const contract_step = b.step(
        "phase3-export-shim-rbtree-root-view-contract",
        "Run the Phase 3 export-shim rbtree root-view contract",
    );
    contract_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the Phase 3 export-shim rbtree root-view contract");
    test_step.dependOn(&run_tests.step);
    b.default_step.dependOn(&run_tests.step);
}
