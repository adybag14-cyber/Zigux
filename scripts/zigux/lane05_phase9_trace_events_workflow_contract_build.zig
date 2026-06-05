const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const contract = b.addExecutable(.{
        .name = "lane05-phase9-trace-events-workflow-contract",
        .root_module = b.createModule(.{
            .root_source_file = b.path("lane05_phase9_trace_events_workflow_contract.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });

    const run_contract = b.addRunArtifact(contract);
    const contract_step = b.step(
        "lane05-phase9-trace-events-workflow-contract",
        "Validate the Lane 05 Phase 9 trace-events workflow block",
    );
    contract_step.dependOn(&run_contract.step);

    const tests = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("lane05_phase9_trace_events_workflow_contract.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });
    const run_tests = b.addRunArtifact(tests);
    const test_step = b.step("test", "Run the Lane 05 Phase 9 trace-events workflow contract tests");
    test_step.dependOn(&run_tests.step);
}
