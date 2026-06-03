const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const root_module = b.createModule(.{
        .root_source_file = b.path("../../Documentation/zigux/lane02_docs_root_freeze_map_contract.zig"),
        .target = target,
        .optimize = optimize,
    });

    const tests = b.addTest(.{
        .name = "lane02-docs-root-freeze-map-contract",
        .root_module = root_module,
    });
    const run_tests = b.addRunArtifact(tests);

    const test_step = b.step(
        "test",
        "Run the Lane 02 docs-root, review-checklist, and freeze-map contract",
    );
    test_step.dependOn(&run_tests.step);

    const contract_step = b.step(
        "lane02-docs-root-freeze-map-contract",
        "Run the Lane 02 docs-root, review-checklist, and freeze-map contract",
    );
    contract_step.dependOn(&run_tests.step);
}
