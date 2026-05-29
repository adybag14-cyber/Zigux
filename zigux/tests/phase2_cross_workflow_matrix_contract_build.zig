const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});
    const workflow_text = readWorkflow(b);

    const options = b.addOptions();
    options.addOption([]const u8, "workflow", workflow_text);

    const workflow_matrix_module = b.createModule(.{
        .root_source_file = b.path("phase2_cross_workflow_matrix_contract.zig"),
        .target = target,
        .optimize = optimize,
    });
    workflow_matrix_module.addOptions("phase2_cross_workflow_matrix_options", options);

    const workflow_matrix_tests = b.addTest(.{
        .name = "phase2-cross-workflow-matrix-contract-tests",
        .root_module = workflow_matrix_module,
    });
    const run_workflow_matrix_tests = b.addRunArtifact(workflow_matrix_tests);

    const contract_step = b.step("phase2-cross-workflow-matrix-contract", "Run the Phase 2 cross workflow matrix contract tests");
    contract_step.dependOn(&run_workflow_matrix_tests.step);

    const test_step = b.step("test", "Run the Phase 2 cross workflow matrix contract tests");
    test_step.dependOn(&run_workflow_matrix_tests.step);

    b.default_step.dependOn(test_step);
}

fn readWorkflow(b: *std.Build) []const u8 {
    const candidates = [_][]const u8{
        "../../.github/workflows/zigux-bootstrap.yml",
        ".github/workflows/zigux-bootstrap.yml",
    };

    for (candidates) |path| {
        return std.Io.Dir.cwd().readFileAlloc(b.graph.io, path, b.allocator, .limited(1024 * 1024)) catch |err| switch (err) {
            error.FileNotFound => continue,
            else => @panic("failed to read zigux-bootstrap workflow"),
        };
    }

    @panic("missing .github/workflows/zigux-bootstrap.yml");
}
