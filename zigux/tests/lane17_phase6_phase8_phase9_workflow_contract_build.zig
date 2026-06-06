const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});
    const workflow_path = b.option(
        []const u8,
        "workflow-path",
        "Path to .github/workflows/zigux-bootstrap.yml or a compact current-marker fixture",
    ) orelse ".github/workflows/zigux-bootstrap.yml";
    const workflow_text = std.Io.Dir.cwd().readFileAlloc(
        b.graph.io,
        workflow_path,
        b.allocator,
        .limited(256 * 1024),
    ) catch |err| {
        std.debug.panic("failed to read workflow path '{s}': {}", .{ workflow_path, err });
    };

    const options = b.addOptions();
    options.addOption([]const u8, "workflow_text", workflow_text);

    const contract_module = b.createModule(.{
        .root_source_file = b.path("lane17_phase6_phase8_phase9_workflow_contract.zig"),
        .target = target,
        .optimize = optimize,
    });
    contract_module.addOptions("build_options", options);

    const tests = b.addTest(.{
        .name = "lane17-phase6-phase8-phase9-workflow-contract",
        .root_module = contract_module,
    });

    const run_tests = b.addRunArtifact(tests);

    const contract_step = b.step(
        "lane17-phase6-phase8-phase9-workflow-contract",
        "Validate Lane 17 Phase 6, Phase 8, and Phase 9 workflow bridge markers",
    );
    contract_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run Lane 17 Phase 6, Phase 8, and Phase 9 workflow bridge contract");
    test_step.dependOn(&run_tests.step);
}
