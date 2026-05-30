const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const module = b.createModule(.{
        .root_source_file = b.path("lane02_docs_root_freeze_checklist_contract.zig"),
        .target = target,
        .optimize = optimize,
    });

    const unit_tests = b.addTest(.{
        .name = "lane02-docs-root-freeze-checklist-contract",
        .root_module = module,
    });
    const run_unit_tests = b.addRunArtifact(unit_tests);

    const contract = b.step(
        "lane02-docs-root-freeze-checklist-contract",
        "Run the Lane 02 docs-root freeze/checklist contract",
    );
    contract.dependOn(&run_unit_tests.step);

    const test_step = b.step("test", "Run the Lane 02 docs-root freeze/checklist contract");
    test_step.dependOn(&run_unit_tests.step);
}
