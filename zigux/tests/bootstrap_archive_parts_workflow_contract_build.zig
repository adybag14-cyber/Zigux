const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});
    const contract_inputs = b.addOptions();
    contract_inputs.addOption(
        []const u8,
        "workflow_path",
        b.pathFromRoot("../../.github/workflows/zigux-bootstrap-archive-parts-packet.yml"),
    );

    const root_module = b.createModule(.{
        .root_source_file = b.path("bootstrap_archive_parts_workflow_contract.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addOptions("archive_parts_contract_inputs", contract_inputs);

    const tests = b.addTest(.{
        .name = "bootstrap-archive-parts-workflow-contract-test",
        .root_module = root_module,
    });
    const run_tests = b.addRunArtifact(tests);

    const test_step = b.step(
        "bootstrap-archive-parts-workflow-contract-test",
        "Run the focused Lane 05 archive-parts workflow contract",
    );
    test_step.dependOn(&run_tests.step);

    const default_step = b.step("test", "Run focused Lane 05 archive-parts workflow contract tests");
    default_step.dependOn(&run_tests.step);
}
