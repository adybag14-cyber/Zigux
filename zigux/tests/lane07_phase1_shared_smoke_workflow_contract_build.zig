const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});
    const workflow_path = b.option(
        []const u8,
        "workflow-path",
        "Path to the zigux-bootstrap workflow to inspect",
    ) orelse "../../.github/workflows/zigux-bootstrap.yml";
    const workflow_text = b.build_root.handle.readFileAlloc(
        b.graph.io,
        workflow_path,
        b.allocator,
        .limited(1024 * 1024),
    ) catch |err| @panic(@errorName(err));

    const root_module = b.createModule(.{
        .root_source_file = b.path("lane07_phase1_shared_smoke_workflow_contract.zig"),
        .target = target,
        .optimize = optimize,
    });
    const options = b.addOptions();
    options.addOption([]const u8, "workflow_text", workflow_text);
    root_module.addOptions("contract_options", options);
    const contract_tests = b.addTest(.{
        .name = "lane07-phase1-shared-smoke-workflow-contract",
        .root_module = root_module,
    });
    const run_contract = b.addRunArtifact(contract_tests);

    const contract_step = b.step(
        "lane07-phase1-shared-smoke-workflow-contract",
        "Run the Lane 07 Phase 1 shared smoke workflow contract",
    );
    contract_step.dependOn(&run_contract.step);

    const test_step = b.step("test", "Run the Lane 07 Phase 1 shared smoke workflow contract");
    test_step.dependOn(&run_contract.step);
}
