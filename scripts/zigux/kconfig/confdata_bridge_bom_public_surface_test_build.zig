const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const root_module = b.createModule(.{
        .root_source_file = b.path("confdata_bridge_bom_public_surface_test.zig"),
        .target = target,
        .optimize = optimize,
    });

    const tests = b.addTest(.{
        .name = "confdata-bridge-bom-public-surface-tests",
        .root_module = root_module,
    });
    const run_tests = b.addRunArtifact(tests);

    const first_line_module = b.createModule(.{
        .root_source_file = b.path("confdata_bridge_first_line_bom_public_surface_test.zig"),
        .target = target,
        .optimize = optimize,
    });

    const first_line_tests = b.addTest(.{
        .name = "confdata-bridge-first-line-bom-public-surface-tests",
        .root_module = first_line_module,
    });
    const run_first_line_tests = b.addRunArtifact(first_line_tests);

    const first_line_export_module = b.createModule(.{
        .root_source_file = b.path("confdata_bridge_first_line_bom_export_surface_test.zig"),
        .target = target,
        .optimize = optimize,
    });

    const first_line_export_tests = b.addTest(.{
        .name = "confdata-bridge-first-line-bom-export-surface-tests",
        .root_module = first_line_export_module,
    });
    const run_first_line_export_tests = b.addRunArtifact(first_line_export_tests);

    const contract_step = b.step(
        "confdata-bridge-bom-public-surface",
        "Run confdata bridge BOM public-surface tests",
    );
    contract_step.dependOn(&run_tests.step);
    contract_step.dependOn(&run_first_line_tests.step);
    contract_step.dependOn(&run_first_line_export_tests.step);

    const test_step = b.step("test", "Run confdata bridge BOM public-surface tests");
    test_step.dependOn(&run_tests.step);
    test_step.dependOn(&run_first_line_tests.step);
    test_step.dependOn(&run_first_line_export_tests.step);
}
