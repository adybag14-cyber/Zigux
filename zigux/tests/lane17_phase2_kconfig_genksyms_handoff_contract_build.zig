const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});
    const workflow_path = b.option(
        []const u8,
        "workflow-path",
        "Path to the zigux-bootstrap workflow file",
    ) orelse ".github/workflows/zigux-bootstrap.yml";

    const options = b.addOptions();
    options.addOption([]const u8, "workflow_path", workflow_path);

    const contract_module = b.createModule(.{
        .root_source_file = b.path("lane17_phase2_kconfig_genksyms_handoff_contract.zig"),
        .target = target,
        .optimize = optimize,
    });
    contract_module.addOptions("lane17_options", options);

    const tests = b.addTest(.{
        .name = "lane17-phase2-kconfig-genksyms-handoff-contract",
        .root_module = contract_module,
    });

    const run = b.addRunArtifact(tests);

    const contract_step = b.step(
        "lane17-phase2-kconfig-genksyms-handoff-contract",
        "Validate the Lane 17 Phase 2 kconfig/genksyms handoff workflow contract",
    );
    contract_step.dependOn(&run.step);

    const test_step = b.step("test", "Run the Lane 17 Phase 2 workflow handoff contract");
    test_step.dependOn(&run.step);
}
